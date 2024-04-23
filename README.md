# Discord Bot with Claude Integration

This project is a proof-of-concept Discord bot that integrates with the Claude AI by Anthropic. The bot responds to messages in your Discord server using Claude's natural language processing capabilities. While the code provided is a starting point, the possibilities are endless if you ask Claude to add features to this foundation. Keep in mind that Claude gives a free $5 of API usage, but you'll need to pay for usage beyond that, even if you have a paid Claude Opus subscription. Consider switching to the computationally cheaper versions of Claude in the code to reduce the cost per message.

Claude failed constantly and required hand-holding to get this far, but it should be good from here. This upload should be enough for you to avoid the lame technical difficulties phase of programming and get straight to creativity.

## Installation

1. Install Python

2. Open a command prompt running as administrator and navigate to the installation folder.

3. Install the required Python packages by running the following commands:
   ```
   python -m pip install discord.py --user
   python -m pip install anthropic --user
   ```

4. Create a Discord server (if you haven't already) within the Discord UI.

5. Create a bot account:
   - Go to the Discord Developer Portal: [Discord Applications](https://discord.com/developers/applications/)
   - Click on "New Application" and give your bot a name.
   - Navigate to the "Bot" section on the left sidebar and click "Add Bot".
   - Copy the bot token (keep it secure, as it acts as the bot's username and password).

6. Replace the placeholder `'######'` in the `DC.py` file with your bot token:
   ```python
   client.run('######')
   ```

7. Authorize the bot to join your server:
   - Go to the "OAuth2" section on the left sidebar in the Discord Developer Portal.
   - Under "Scopes", check the "bot" option.
   - Under "Bot Permissions", check all or nearly all of the permissions that appear.
   - Copy the generated URL and paste it into a new browser tab.
   - Select the server you created from the dropdown list and click "Authorize".

8. Obtain your Claude API key:
   - Go to the Anthropic Console: [Anthropic Settings](https://console.anthropic.com/settings/keys)
   - Generate a new API key and copy it.

9. Replace the placeholder `'#####'` in the `DC.py` file with your Claude API key:
   ```python
   anthropic_client = anthropic.Anthropic(api_key="#####")
   ```

## Usage

1. Open a non-admin command prompt and navigate to the location of the `DC.py` file.

2. Run the bot by typing the following command and hitting Enter:
   ```
   DC.py
   ```

3. As long as the Python script is running on a computer connected to the internet, the bot will be logged in to your Discord server.

4. Any message sent by anyone in any channel of your server will be responded to by Claude.

## Additional Notes

- Make sure to keep your bot token and Claude API key secure and do not share them with anyone.
- You can customize the bot's behavior by modifying the code in the `DC.py` file.
