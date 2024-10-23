# Discord Bot with AI Integration

This project is a Discord bot that integrates with AI models through the OpenRouter API. The bot responds to messages in your Discord server using advanced language models, providing natural and context-aware responses. It supports text interactions and image analysis, making it a versatile tool for various Discord communities.

## Features

- AI-powered responses using models from OpenRouter
- Image analysis capabilities
- Conversation context management
- Queue system for handling multiple requests
- Rate limiting and error handling
- Support for multiple AI models

## Prerequisites

- Python 3.7 or higher
- A Discord account and a server where you have permissions to add bots
- An OpenRouter account and API key

## Installation

1. Clone this repository or download the source code.

2. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root and add the following:
   ```
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   DISCORD_BOT_TOKEN=your_discord_bot_token_here
   ```

4. Replace `your_openrouter_api_key_here` with your OpenRouter API key and `your_discord_bot_token_here` with your Discord bot token.

## Setting up the Discord Bot

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications/).
2. Click "New Application" and give your bot a name.
3. Go to the "Bot" section and click "Add Bot".
4. Under "Token", click "Copy" to copy your bot token (use this in your `.env` file).
5. Enable the "Message Content Intent" under "Privileged Gateway Intents".
6. Go to "OAuth2" > "URL Generator", select "bot" under scopes, and choose necessary permissions.
7. Use the generated URL to invite the bot to your server.

## Usage

1. Run the bot:
   ```
   python DC.py
   ```

2. In your Discord server, use the command prefix `!ai` followed by your message to interact with the bot. For example:
   ```
   !ai What's the weather like today?
   ```

3. To analyze an image, attach an image to your message along with the `!ai` command.

## Customization

- You can change the AI model by modifying the `OPENROUTER_MODEL` variable in `DC.py`.
- Adjust the `MAX_CONTEXT_MESSAGES` and `CONTEXT_EXPIRATION` variables to change how conversation context is managed.
- Modify the `MAX_QUEUE_SIZE` to change the number of requests the bot can handle simultaneously.

## Contributing

Contributions to improve the bot are welcome. Please feel free to submit pull requests or open issues to suggest improvements or report bugs.

## License

This project is open-source and available under the MIT License.

## Disclaimer

This bot uses AI models that may produce content that doesn't reflect real-world facts or opinions. Always verify important information from reliable sources.
