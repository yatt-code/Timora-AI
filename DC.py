import discord
import requests
import time
import re
import logging
from collections import deque, defaultdict
import json
import ssl
import aiohttp
import os
from dotenv import load_dotenv
import certifi
import base64
from io import BytesIO
import random
import asyncio
from asyncio import Queue

# Load environment variables
load_dotenv()

# Constants
INITIAL_RETRY_DELAY = 1  # Start with a 1 second delay
MAX_RETRY_DELAY = 32  # Maximum delay of 32 seconds
MAX_RETRIES = 5  # Maximum number of retries
CACHE_EXPIRATION = 3600  # Cache expiration time in seconds (1 hour)
MAX_REQUESTS = 5
TIME_WINDOW = 60  # 1 minute
TRIGGER_PREFIX = "!ai"

# Set SSL certificate file path
os.environ['SSL_CERT_FILE'] = os.getenv('SSL_CERT_FILE')

# Set up SSL context
ssl_context = ssl.create_default_context(cafile=certifi.where())

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

# Add this near the top of your file, after the constants and before the function definitions
MAX_QUEUE_SIZE = 10  # Maximum number of requests in the queue
request_queue = asyncio.Queue(maxsize=MAX_QUEUE_SIZE)

# Create a custom aiohttp ClientSession with the SSL context
async def get_aiohttp_session():
    return aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context))

# Create the Discord client
client = discord.Client(intents=intents)

# Load API keys and tokens from environment variables
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Specify the model you want to use
OPENROUTER_MODEL = "meta-llama/llama-3.2-11b-vision-instruct"
# Other model options include:
# "openai/gpt-3.5-turbo"
# "google/palm-2-chat-bison"
# "anthropic/claude-2"
# "meta-llama/llama-2-70b-chat"
# Check OpenRouter's documentation for the most up-to-date list of available models

# Cache to store previous prompts and responses
cache = {}
request_times = deque()

def sanitize_input(input_text):
    # Remove any non-alphanumeric characters except common punctuation
    return re.sub(r'[^a-zA-Z0-9\s.,!?-]', '', input_text)

def format_response(response):
    if 'choices' in response and len(response['choices']) > 0:
        text = response['choices'][0]['message']['content']

        # Replace newline characters with actual newlines
        text = text.replace('\\n', '\n')

        return text.strip()
    
    return "Sorry, I couldn't generate a response."

def check_rate_limit():
    current_time = time.time()
    while request_times and current_time - request_times[0] > TIME_WINDOW:
        request_times.popleft()
    return len(request_times) < MAX_REQUESTS

# Add a trigger prefix
TRIGGER_PREFIX = "!ai"

async def encode_image(attachment):
    """Encode the image attachment as a base64 string."""
    buffer = BytesIO()
    await attachment.save(buffer)
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

@client.event
async def on_ready():
    logging.info(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if not message.content.startswith(TRIGGER_PREFIX):
        return

    user_message = message.content[len(TRIGGER_PREFIX):].strip()
    logging.info(f'Triggered message from {message.author}: {user_message}')

    image_data = None
    if message.attachments:
        for attachment in message.attachments:
            if attachment.content_type.startswith('image/'):
                image_data = await encode_image(attachment)
                break

    try:
        await request_queue.put((message, user_message, image_data))
        queue_size = request_queue.qsize()
        if queue_size > 1:
            await message.channel.send(f"Your request has been queued. Current queue size: {queue_size}")
    except asyncio.QueueFull:
        await message.channel.send("I'm sorry, but I'm currently at maximum capacity. Please try again later.")

async def process_queue():
    while True:
        message, user_message, image_data = await request_queue.get()
        try:
            await process_message(message, user_message, image_data)
        except Exception as e:
            logging.error(f"Error processing queued message: {e}")
            await message.channel.send("Sorry, an error occurred while processing your request.")
        finally:
            request_queue.task_done()

async def process_message(message, user_message, image_data):
    user_id = str(message.author.id)
    current_time = time.time()
    
    # Clear expired context
    if current_time - conversation_history[user_id]["last_update"] > CONTEXT_EXPIRATION:
        conversation_history[user_id]["messages"].clear()
    
    conversation_history[user_id]["last_update"] = current_time
    
    sanitized_content = sanitize_input(user_message)
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Include conversation history in the messages
    messages = list(conversation_history[user_id]["messages"])
    messages.append({"role": "user", "content": sanitized_content})
    
    if image_data:
        messages[-1]["content"] = [
            {"type": "text", "text": sanitized_content},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
        ]

    data = {
        "model": OPENROUTER_MODEL,
        "messages": messages,
        "max_tokens": 400,
        "temperature": 0.0
    }

    retry_delay = INITIAL_RETRY_DELAY
    retries = 0

    while retries < MAX_RETRIES:
        logging.info(f"Sending request to OpenRouter API with content: {sanitized_content}")
        try:
            response = requests.post(OPENROUTER_API_URL, headers=headers, json=data)
            logging.info(f"OpenRouter API response status code: {response.status_code}")
            logging.info(f"OpenRouter API response content: {response.text}")
            
            if response.status_code == 429:
                retries += 1
                if retries >= MAX_RETRIES:
                    await message.channel.send("I'm sorry, but I've reached my rate limit. Please try again later.")
                    return
                
                wait_time = retry_delay * (1 + random.random())
                logging.info(f"Rate limited. Retrying in {wait_time:.2f} seconds...")
                await message.channel.send(f"Rate limit reached. Retrying in {wait_time:.2f} seconds...")
                await asyncio.sleep(wait_time)
                retry_delay = min(retry_delay * 2, MAX_RETRY_DELAY)
                continue
            
            response.raise_for_status()
            ai_response = response.json()
            
            formatted_response = format_response(ai_response)
            
            # Update conversation history
            conversation_history[user_id]["messages"].append({"role": "user", "content": sanitized_content})
            conversation_history[user_id]["messages"].append({"role": "assistant", "content": formatted_response})
            
            # Split the formatted response into chunks of 2000 characters or less
            response_chunks = [formatted_response[i:i+2000] for i in range(0, len(formatted_response), 2000)]

            # Send each chunk as a separate message
            for chunk in response_chunks:
                await message.channel.send(chunk)
            
            break  # Exit the loop if successful
        except Exception as e:
            logging.error(f"Error in API request: {str(e)}")
            await message.channel.send(f"Sorry, an error occurred: {str(e)}")
            return

# Modify the main() function at the end of the file:
async def main():
    async with await get_aiohttp_session() as session:
        async with client:
            client.http.session = session
            asyncio.create_task(process_queue())  # Start the queue processing task
            await client.start(DISCORD_BOT_TOKEN)

# Run the bot
asyncio.run(main())

# After loading environment variables
if not OPENROUTER_API_KEY:
    logging.error("OpenRouter API key is not set. Please check your .env file.")
    raise ValueError("OpenRouter API key is missing")

logging.info("OpenRouter API key loaded successfully")

# Add these imports at the top of your file
from collections import defaultdict, deque

# Add these constants
MAX_CONTEXT_MESSAGES = 5  # Maximum number of previous messages to keep as context
CONTEXT_EXPIRATION = 600  # Context expiration time in seconds (10 minutes)

# Add this near your other global variables
conversation_history = defaultdict(lambda: {"messages": deque(maxlen=MAX_CONTEXT_MESSAGES), "last_update": time.time()})
