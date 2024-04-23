import discord
import anthropic

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

client = discord.Client(intents=intents)
anthropic_client = anthropic.Anthropic(api_key="#####")

def format_response(response):
    formatted_text = "**Claude:**\n\n"

    if isinstance(response, list) and len(response) > 0:
        text = response[0].text

        # Replace newline characters with actual newlines
        text = text.replace('\\n', '\n')

        formatted_text += text

    return formatted_text.strip()

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    print(f'Message from {message.author}: {message.content}')

    try:
        # Send the user's message to Claude and get the response
        claude_response = anthropic_client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=400,
            temperature=0.0,
            messages=[
                {"role": "user", "content": message.content}
            ]
        )

        # Format Claude's response
        formatted_response = format_response(claude_response.content)

        # Split the formatted response into chunks of 2000 characters or less
        response_chunks = [formatted_response[i:i+2000] for i in range(0, len(formatted_response), 2000)]

        # Send each chunk as a separate message
        for chunk in response_chunks:
            await message.channel.send(chunk)

    except Exception as e:
        print(f"Error processing message: {e}")
        await message.channel.send("Sorry, I encountered an error while processing your message. Please try again later.")

client.run('#####')