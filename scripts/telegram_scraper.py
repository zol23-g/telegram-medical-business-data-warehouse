import os
import csv
import logging
import logging.config
import yaml
import argparse
from telethon import TelegramClient
from dotenv import load_dotenv  # Import dotenv
import uuid  # Import UUID for generating unique identifiers

# Load environment variables from .env file
load_dotenv()

# Ensure necessary directories exist
os.makedirs('logs', exist_ok=True)
os.makedirs('raw_data/images', exist_ok=True)

# Load logging configuration
with open('config/logging_config.yaml', 'r') as file:
    config = yaml.safe_load(file.read())
    logging.config.dictConfig(config)

logger = logging.getLogger(__name__)

# Telegram API credentials (from environment variables)
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
phone = os.getenv('PHONE_NUMBER')

# Create the Telegram client
client = TelegramClient('session_name', api_id, api_hash)

# Argument parser setup
parser = argparse.ArgumentParser(description="Telegram Scraper")
parser.add_argument('--telegram-channel', type=str, help='Telegram channel to download data from')
parser.add_argument('--batch-file', type=str, help='File containing a list of Telegram channels')
parser.add_argument('--min-id', type=int, help='Offset ID for incremental updates')
args = parser.parse_args()

# Function to read channels from batch file
def read_channels_from_file(filepath):
    with open(filepath, 'r') as file:
        channels = [line.strip() for line in file if line.strip()]
    logger.info(f"Loaded {len(channels)} channels from {filepath}")
    return channels

# Determine channels to scrape
channel_usernames = []
if args.telegram_channel:
    channel_usernames = [args.telegram_channel]
    logger.info(f"Scraping data from single channel: {args.telegram_channel}")
elif args.batch_file:
    channel_usernames = read_channels_from_file(args.batch_file)
    logger.info(f"Scraping data from batch file: {args.batch_file}")
else:
    logger.error("No Telegram channel or batch file provided")
    exit(1)

# Channels to collect images from (specific channels)
image_channels = ['CheMed123', 'lobelia4cosmetics']

async def scrape_telegram_channels(min_id=None):
    all_messages = []
    for username in channel_usernames:
        logger.info(f"Starting to scrape messages from {username} with min_id={min_id}")
        try:
            async for message in client.iter_messages(username, min_id=min_id or 0):
                message_id = str(uuid.uuid4())  # Generate a unique identifier
                all_messages.append({
                    'message_id': message_id,  # Store the unique identifier
                    'sender_id': message.sender_id,
                    'message_text': message.text,
                    'channel': username,
                    'date': message.date
                })
                logger.info(f"Scraped message from {username}: {message.text[:30]}...")  # Log only part of the message
        except Exception as e:
            logger.error(f"Error scraping messages from {username}: {e}")
    return all_messages

async def scrape_images(min_id=None):
    for username in image_channels:
        if username in channel_usernames:
            logger.info(f"Starting to scrape images from {username} with min_id={min_id}")
            try:
                async for message in client.iter_messages(username, min_id=min_id or 0):
                    if message.photo:
                        message_id = str(uuid.uuid4())  # Generate a unique identifier for the image
                        path = await message.download_media(file=f'data/raw/images/{username}_{message_id}.jpg')
                        logger.info(f"Downloaded image from {username}: {path}")
            except Exception as e:
                logger.error(f"Error scraping images from {username}: {e}")

def store_data(messages, filepath='data/raw/messages.csv'):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    try:
        with open(filepath, mode='w', newline='', encoding='utf-8') as file:  # Specify encoding='utf-8'
            writer = csv.DictWriter(file, fieldnames=['message_id', 'sender_id', 'message_text', 'channel', 'date'])
            writer.writeheader()
            for message in messages:
                writer.writerow(message)
        logger.info(f"Stored {len(messages)} messages to {filepath}")
    except Exception as e:
        logger.error(f"Error storing messages to {filepath}: {e}")

async def main():
    logger.info("Starting Telegram client...")
    await client.start(phone)
    logger.info("Telegram client started.")
    
    logger.info("Scraping messages...")
    messages = await scrape_telegram_channels(min_id=args.min_id)
    
    logger.info("Storing scraped messages...")
    store_data(messages)
    
    logger.info("Scraping images...")
    await scrape_images(min_id=args.min_id)

    logger.info("Scraping process completed.")

if __name__ == '__main__':
    try:
        with client:
            logger.info("Running the main Telegram scraper function.")
            client.loop.run_until_complete(main())
    except Exception as e:
        logger.error(f"An error occurred during execution: {e}")
