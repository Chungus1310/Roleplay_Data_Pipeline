import asyncio
import json
import random
import time
import os
import sys
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional

from better_genai.client import GeminiClient
from PyCharacterAI import get_client
from PyCharacterAI.exceptions import SessionClosedError

class BackupManager:
    """Helps keep your conversation data safe with automatic backups!"""
    
    def __init__(self, base_filename: str, max_backups: int = 5):
        """
        Sets up our friendly backup system 
        
        base_filename: Where to save your main conversation
        max_backups: How many backup copies to keep just in case
        """
        self.base_filename = base_filename
        self.max_backups = max_backups
        self.backup_dir = os.path.join(os.path.dirname(base_filename), "backups")
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def save_data(self, data: Dict[str, Any]) -> None:
        """
        Safely saves your data with a temporary file first - no data loss here!
        """
        temp_filename = f"{self.base_filename}.tmp"
        
        try:
            with open(temp_filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            if os.path.exists(self.base_filename):
                self._create_backup()
                
            if os.path.exists(self.base_filename):
                os.remove(self.base_filename)
                
            os.rename(temp_filename, self.base_filename)
        except Exception as e:
            print(f"Oops! Had trouble saving data: {e}")
            if os.path.exists(temp_filename):
                try:
                    os.remove(temp_filename)
                except:
                    pass
    
    def _create_backup(self) -> None:
        """Makes a timestamped copy of your conversation - just to be safe!"""
        if not os.path.exists(self.base_filename):
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = os.path.join(
            self.backup_dir, 
            f"{os.path.basename(self.base_filename)}.{timestamp}.bak"
        )
        
        try:
            import shutil
            shutil.copy2(self.base_filename, backup_filename)
            self._cleanup_old_backups()
        except Exception as e:
            print(f"Couldn't create backup right now: {e}")
    
    def _cleanup_old_backups(self) -> None:
        """Keeps your backup folder tidy by removing older copies"""
        try:
            backups = [
                os.path.join(self.backup_dir, f) 
                for f in os.listdir(self.backup_dir) 
                if f.endswith('.bak')
            ]
            
            backups.sort(key=lambda x: os.path.getmtime(x))
            
            while len(backups) > self.max_backups:
                os.remove(backups[0])
                backups.pop(0)
        except Exception as e:
            print(f"Had a small issue cleaning up old backups: {e}")

class StandaloneRoleplayGenerator:
    def __init__(self, config_path="config.json"):
        """
        Gets your roleplay generator ready to create conversations!
        
        config_path: Path to your settings file (we'll create one if it's missing)
        """
        self.config = {
            "character_ai": {
                "token": "",
                "character_id": ""
            },
            "gemini": {
                "key_rotation_interval": 60,
                "history_size": 10,
                "model": "gemini-1.5-pro"
            },
            "pipeline": {
                "target_message_count": 50,
                "delay_min": 2.0,
                "delay_max": 4.0,
                "max_backups": 5
            },
            "user_persona": {
                "name": "User",
                "personality": "Friendly and curious individual",
                "background": "Someone interested in meaningful conversations",
            },
            "scenario": "A casual conversation between two individuals"
        }
        
        try:
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    custom_config = json.load(f)
                    for category, values in custom_config.items():
                        if category in self.config and isinstance(values, dict):
                            self.config[category].update(values)
                        else:
                            self.config[category] = values
                print(f"Loaded your settings from {config_path}")
            else:
                print(f"No config file found! Creating a starter one at {config_path}...")
                with open(config_path, "w", encoding="utf-8") as f:
                    json.dump(self.config, f, indent=2, ensure_ascii=False)
                print(f"Default settings saved to {config_path}. Please add your info and restart.")
                sys.exit(0)
        except Exception as e:
            print(f"Had trouble with the config file: {e}")
            print("Going with default settings instead")
        
        os.makedirs("datasets", exist_ok=True)
        os.makedirs("cache", exist_ok=True)
        
        self.char_ai_client = None
        self.char_ai_chat = None
        self.initialize_char_ai()
        
        self.gemini_client = GeminiClient(
            key_rotation_interval=self.config["gemini"]["key_rotation_interval"],
            history_size=self.config["gemini"]["history_size"],
            model=self.config["gemini"]["model"],
            improve_prompts=False,
            cache_dir="./cache"
        )
        
        self.conversation_data = {
            "metadata": {
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "characters": {
                    "user": self.config["user_persona"]["name"],
                    "character": "AI Character"
                },
                "scenario": self.config["scenario"],
                "pair_count": 0,
                "total_target": self.config["pipeline"]["target_message_count"]
            },
            "scenario": self.config["scenario"],
            "conversation_pairs": []
        }
        
        self.current_pair = {"user": "", "character": ""}
        
        self.output_file = f"datasets/conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        self.backup_manager = BackupManager(
            self.output_file, 
            max_backups=self.config["pipeline"].get("max_backups", 5)
        )
        
        print(f"Ready to generate {self.config['pipeline']['target_message_count']} message pairs!")
        print(f"Character: {self.config['character']['name']}")
        print(f"Scenario: {self.config['scenario']}")
    
    async def initialize_char_ai(self):
        """Sets up the Character AI client with better error handling"""
        try:
            self.char_ai_client = await get_client(token=self.config["character_ai"]["token"])
            me = await self.char_ai_client.account.fetch_me()
            print(f"Character AI: Logged in as @{me.username}")
            
            self.char_ai_chat, greeting = await self.char_ai_client.chat.create_chat(
                self.config["character_ai"]["character_id"]
            )
            print(f"Character AI Greeting: {greeting.get_primary_candidate().text}")
            return True
            
        except Exception as e:
            print(f"Failed to initialize Character AI: {e}")
            return False

    def add_message_pair(self, user_text: str, character_text: str):
        """Adds a new conversation exchange to our dataset"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        complete_pair = {
            "user": user_text,
            "character": character_text,
            "timestamp": timestamp
        }
        
        self.conversation_data["conversation_pairs"].append(complete_pair)
        self.conversation_data["metadata"]["pair_count"] += 1
        
        self.save_conversation()
    
    def save_conversation(self):
        """Saves your conversation progress so nothing gets lost"""
        try:
            self.backup_manager.save_data(self.conversation_data)
            print(f"Saved progress: {self.conversation_data['metadata']['pair_count']} / {self.conversation_data['metadata']['total_target']}")
        except Exception as e:
            print(f"Had a hiccup saving the conversation: {e}")
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(self.conversation_data, f, ensure_ascii=False, indent=2)
            print(f"But don't worry, saved it another way!")
    
    def clean_response(self, response: str) -> str:
        """Tidies up the AI's responses to keep things consistent"""
        response = response.strip()
        
        user_prefixes = ["user:", "*user:", "*as user:", "<user>:", "[user]:", "(as user)"]
        for prefix in user_prefixes:
            if response.lower().startswith(prefix):
                response = response[len(prefix):].strip()
        
        character_name = self.config["character"]["name"].lower() + ":"
        character_prefixes = [character_name, f"*as {character_name}", f"<{character_name}>", f"[{character_name}]"]
        for prefix in character_prefixes:
            if response.lower().startswith(prefix):
                response = response[len(prefix):].strip()
                
        return response
    
    async def get_user_message(self, is_first_message=False, recent_pairs=None):
        """Creates a realistic message from the user's perspective"""
        user = self.config["user_persona"]
        
        conversation_history = ""
        if recent_pairs:
            for pair in recent_pairs:
                conversation_history += f"{user['name']}: {pair['user']}\n\n"
                conversation_history += f"{self.character_name}: {pair['character']}\n\n"
        
        if is_first_message:
            prompt = f"""
            You are roleplaying as a character with the following traits:
            
            ABOUT YOU (THIS IS WHO YOU ARE):
            - Name: {user['name']}
            - Personality: {user['personality']}
            - Background: {user['background']}
            - Interests: {user['interests']}
            - Speaking Style: {user['speaking_style']}
            
            SCENARIO: 
            {self.config['scenario']}
            
            IMPORTANT INSTRUCTIONS:
            - Stay in character as {user['name']}
            - Write naturally and conversationally
            - Show your personality and background in subtle ways
            - Be genuinely interested in the conversation
            - Keep responses concise but engaging
            
            Start the conversation in a way that fits the scenario.
            """
        else:
            prompt = f"""
            Continue roleplaying as {user['name']} with these traits:
            
            ABOUT YOU:
            - Personality: {user['personality']}
            - Background: {user['background']}
            - Speaking Style: {user['speaking_style']}
            
            SCENARIO:
            {self.config['scenario']}
            
            RECENT CONVERSATION:
            {conversation_history}
            
            Respond naturally to the last message while staying in character.
            """
        
        try:
            response = await self.gemini_client.generate_content_async(prompt)
            response = self.clean_response(response)
            return response
        except Exception as e:
            print(f"Oops! Couldn't get a user response: {e}")
            if is_first_message:
                return f"Hi there! I'm {user['name']}. It's great to meet you. I'm really interested in {user['interests']}. What about you?"
            else:
                return "Sorry, got distracted for a second! Anyway, what were you saying?"

    async def get_character_message(self, recent_pairs=None):
        """Gets response exclusively from Character AI"""
        if not self.char_ai_client or not self.char_ai_chat:
            if not await self.initialize_char_ai():
                raise Exception("Cannot continue without Character AI connection")
        
        try:
            last_user_message = recent_pairs[-1]["user"] if recent_pairs else "Hello!"
            response = await self.char_ai_client.chat.send_message(
                self.config["character_ai"]["character_id"],
                self.char_ai_chat.chat_id,
                last_user_message
            )
            return self.clean_response(response.get_primary_candidate().text)
            
        except SessionClosedError:
            print("Character AI session expired, attempting to reconnect...")
            if await self.initialize_char_ai():
                return await self.get_character_message(recent_pairs)
            raise Exception("Failed to reconnect to Character AI")
            
        except Exception as e:
            raise Exception(f"Character AI error: {e}")

    async def run_generation(self):
        """Creates the whole conversation from start to finish"""
        if not await self.initialize_char_ai():
            print("Cannot continue without Character AI connection")
            return

        try:
            print(f"\n[Thinking up {self.config['user_persona']['name']}'s first message...]")
            user_message = await self.get_user_message(is_first_message=True)
            print(f"[{self.config['user_persona']['name']}]: {user_message}")
            
            print(f"\n[Now {self.config['character']['name']} is responding...]")
            delay = random.uniform(self.config["pipeline"]["delay_min"], self.config["pipeline"]["delay_max"])
            await asyncio.sleep(delay)
            
            character_message = await self.get_character_message([{"user": user_message, "character": ""}])
            print(f"[{self.config['character']['name']}]: {character_message}")
            
            self.add_message_pair(user_message, character_message)
            
            while self.conversation_data["metadata"]["pair_count"] < self.config["pipeline"]["target_message_count"]:
                try:
                    delay = random.uniform(self.config["pipeline"]["delay_min"], self.config["pipeline"]["delay_max"])
                    print(f"\n[Taking a {delay:.2f}s break to think...]")
                    await asyncio.sleep(delay)
                    
                    recent_pairs = self.conversation_data["conversation_pairs"][-3:] if self.conversation_data["conversation_pairs"] else []
                    
                    print("\n[Creating the user's next message...]")
                    user_message = await self.get_user_message(is_first_message=False, recent_pairs=recent_pairs)
                    print(f"[{self.config['user_persona']['name']}]: {user_message}")
                    
                    delay = random.uniform(self.config["pipeline"]["delay_min"], self.config["pipeline"]["delay_max"])
                    print(f"\n[Waiting {delay:.2f}s for character to respond...]")
                    await asyncio.sleep(delay)
                    
                    print(f"[Getting {self.config['character']['name']}'s thoughts...]")
                    latest_context = recent_pairs + [{"user": user_message, "character": ""}]
                    character_message = await self.get_character_message(latest_context)
                    print(f"[{self.config['character']['name']}]: {character_message}")
                    
                    self.add_message_pair(user_message, character_message)
                
                except SessionClosedError:
                    print("Character AI session expired, reconnecting...")
                    if not await self.initialize_char_ai():
                        raise Exception("Failed to reconnect to Character AI")
                    continue
                    
                except Exception as e:
                    print(f"Error during conversation: {e}")
                    break
        
        except KeyboardInterrupt:
            print("\nNo problem, saving your progress before stopping!")
        except Exception as e:
            print(f"Ran into a snag: {e}")
        finally:
            if self.char_ai_client:
                await self.char_ai_client.close_session()
            self.save_conversation()
            print(f"All done! Created {self.conversation_data['metadata']['pair_count']} conversation exchanges")
            print(f"Your new dataset is saved at: {self.output_file}")

async def main():
    """Where the magic begins!"""
    print("Roleplay Dataset Generator")
    print("===========================================")
    
    config_file = "config.json"
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    
    generator = StandaloneRoleplayGenerator(config_file)
    
    print("\nStarting the conversation generator...")
    print("Press Ctrl+C anytime to save and stop")
    
    try:
        await generator.run_generation()
    except KeyboardInterrupt:
        print("\nSaving your progress and wrapping things up!")
    
if __name__ == "__main__":
    os.makedirs("datasets", exist_ok=True)
    os.makedirs("cache", exist_ok=True)
    
    asyncio.run(main())

