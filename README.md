# 🎭 Roleplay Data Pipeline 🤖

A powerful, flexible conversation generator that creates realistic roleplay datasets by combining Character AI with Google's Gemini models! ✨

## 📋 Overview

This tool helps you automatically generate high-quality conversational datasets between:
- A character from Character.AI (acting as your roleplay partner)
- A user persona controlled by Gemini (simulating realistic human responses)

Perfect for building custom datasets for fine-tuning chatbots, training conversational AI, or creating pre-made roleplay scenarios! 🚀

## ✨ Features

- 🤝 Seamless integration with Character.AI's unofficial API
- 🧠 Smart persona generation with Google's Gemini models
- ⏱️ Customizable conversation pacing with natural delays
- 💾 Automatic backup system to prevent data loss
- ⚙️ Highly configurable through a simple JSON file
- 🔄 API key rotation to prevent rate limiting
- 📊 Progress tracking and error handling
- 📂 Organized output in clean JSON format

## 🛠️ Installation

1. Clone this repository:
```bash
git clone https://github.com/Chungus1310/Roleplay_Data_Pipeline.git
cd Roleplay_Data_Pipeline
```

2. Install Python requirements:
```bash
pip install PyCharacterAI
```

3. Clone the better_genai module:
```bash
git clone https://github.com/Chungus1310/better_genai.git
```

4. Create a `.env` file with your Gemini API keys:
```
GEMINI_API_KEY1=your_gemini_api_key_here
GEMINI_API_KEY2=your_second_key_here
# Add more keys as needed
```

5. Configure your `config.json` file (check the Configuration section below)

## 🚀 Usage

1. Run the main script:
```bash
python main.py
```

2. Optionally specify a custom config file:
```bash
python main.py custom_config.json
```

3. Watch as the conversations are automatically generated! The script will:
   - Initialize both AI systems
   - Generate the conversation based on your settings
   - Save progress regularly with automatic backups
   - Output a clean JSON dataset in the `datasets` folder

Press `Ctrl+C` at any time to gracefully stop the process and save progress.

## ⚙️ Configuration

All settings are managed through the `config.json` file:

```json
{
  "character_ai": {
    "token": "YOUR_CHARACTER_AI_TOKEN_HERE", 
    "character_id": "CHARACTER_ID_HERE"
  },
  "gemini": {
    "model": "gemini-2.0-flash",
    "key_rotation_interval": 0.5,
    "history_size": 2
  },
  "pipeline": {
    "target_message_count": 100,
    "delay_min": 0.5,
    "delay_max": 3.0,
    "save_frequency": 1,
    "create_backups": true,
    "max_backups": 5
  },
  "user_persona": {
    "name": "Your character name here",
    "personality": "Friendly and curious individual with a passion for meaningful conversations",
    "background": "A well-read person who enjoys learning about others' experiences and perspectives",
    "interests": "Philosophy, culture, storytelling, and understanding different viewpoints",
    "speaking_style": "Warm and engaging, asks thoughtful questions"
  },
  "scenario": "A casual conversation between two individuals meeting for the first time in a comfortable setting"
}
```

### Important Settings:

- **character_ai.token**: Your Character.AI token (see FAQ for how to obtain)
- **character_ai.character_id**: ID of the character you want to use
- **gemini.model**: Which Gemini model to use (e.g. "gemini-2.0-flash", "gemini-1.5-pro")
- **pipeline.target_message_count**: How many conversation exchanges to generate
- **user_persona**: Details about the character Gemini will roleplay as
- **scenario**: Description of the roleplay setting and context

## 📁 Output Format

The tool generates JSON files in the `datasets` folder with this structure:

```json
{
  "metadata": {
    "date": "2025-02-26 10:45:22",
    "characters": {
      "user": "Your character name",
      "character": "AI Character"
    },
    "scenario": "Your scenario description",
    "pair_count": 100,
    "total_target": 100
  },
  "scenario": "Your scenario description",
  "conversation_pairs": [
    {
      "user": "User message text here",
      "character": "Character response text here",
      "timestamp": "2025-02-26 10:45:30"
    },
    // More conversation pairs...
  ]
}
```

## ❓ FAQ

### How do I get my Character.AI token?
> ⚠️ WARNING, DO NOT SHARE THESE TOKENS WITH ANYONE! Anyone with your tokens has full access to your account!
1. Open the Character.AI website in your browser
2. Open the `developer tools` (`F12`, `Ctrl+Shift+I`, or `Cmd+J`)
3. Go to the `Nerwork` tab
4. Interact with website in some way, for example, go to your profile and look for `Authorization` in the request header
5. Copy the value after `Token`

> For example, token in `https://plus.character.ai/chat/user/public/following/` request headers:
> ![img](https://github.com/Xtr4F/PyCharacterAI/blob/main/assets/token.png)

### How do I find a character's ID?
The character ID is in the URL when you visit that character's chat page:
`https://character.ai/chat?char=CHARACTER_ID_HERE`

### Why am I getting rate limited?
- Add more Gemini API keys to your `.env` file
- Increase the `key_rotation_interval` in your config
- Add delays between requests with `delay_min` and `delay_max`

### What if my Character.AI session expires?
The tool automatically handles session reconnection! If your session expires during generation, it will try to reconnect and continue.

## 🔄 Advanced Usage

### Custom User Personas

You can create different user personas by modifying the `user_persona` section:

```json
"user_persona": {
  "name": "Alex",
  "personality": "Introverted, analytical, and quietly curious",
  "background": "Computer programmer with a secret passion for medieval history",
  "interests": "Programming languages, medieval weaponry, chess, hiking alone",
  "speaking_style": "Concise and thoughtful, occasionally uses technical jargon"
}
```


## 👨‍💻 Author

**Chun** - [GitHub Profile](https://github.com/Chungus1310)

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- [PyCharacterAI by Xtr4F](https://github.com/Xtr4F/PyCharacterAI) for the Character.AI integration
- [better_genai by Chungus1310](https://github.com/Chungus1310/better_genai) for enhanced Gemini API handling

---

⭐ Star this repository if you find it useful! ⭐

💬 Report issues or suggest improvements in the Issues section 💬
