import time
from datetime import datetime
import random
import asyncio
from telethon import TelegramClient, errors
from termcolor import colored
import logging
import socket
import socks

# Set logging level to WARNING to reduce log output
logging.basicConfig(level=logging.WARNING)

# Telegram API credentials
API_ID = 29633441  # Replace with your API ID
API_HASH = '952a83fb7d08d7cdf7a651ec23b2d2b7'  # Replace with your API Hash
PHONE_NUMBER = '254742331256'  # Replace with your phone number
SOURCE_CHAT = "@johnsfrwd"
MESSAGE_IDS = [6, 8, 9]  # Message IDs to forward
PROBLEMATIC_LIST = []

bot_name, bot_username = '', ''
GROUP_LIST = []
INVALID_GROUPS = set()

# List of SOCKS5 proxies (IP, Port, Username, Password)
PROXIES = [
    ('23.165.240.222', 10515, 'ngenohkevin19', 'WwKhazXu44'),
    ('23.165.240.222', 10516, 'ngenohkevin19', 'WwKhazXu44'),
    ('23.165.240.222', 10517, 'ngenohkevin19', 'WwKhazXu44'),
]

# Choose a random proxy
chosen_proxy = random.choice(PROXIES)

# Proxy configuration
proxy_settings = {
    'proxy_type': 'socks5',
    'addr': chosen_proxy[0],
    'port': chosen_proxy[1],
    'username': chosen_proxy[2],
    'password': chosen_proxy[3],
}

# Initialize the client with proxy settings
client = TelegramClient('userbot_session_john', API_ID, API_HASH, proxy=proxy_settings)

def is_connected():
    """Check if the internet connection is available."""
    try:
        socket.create_connection(("1.1.1.1", 53))
        return True
    except OSError:
        return False

async def get_bot_info():
    """Fetch and display bot info."""
    global bot_username, bot_name
    try:
        await client.start(PHONE_NUMBER)
        me = await client.get_me()
        bot_name = me.first_name
        bot_username = me.username
        print(bot_name + '<' + bot_username + '>' + " STARTED...")
    except Exception as e:
        print('Error getting bot info:', str(e))

async def get_group_ids():
    """Retrieve group IDs where the bot is a member."""
    global GROUP_LIST
    try:
        print('Trying to gather groups...')
        async for dialog in client.iter_dialogs():
            if dialog.is_group:
                group_item = {"name": dialog.title, "id": dialog.id}
                if group_item not in GROUP_LIST and group_item['id'] not in INVALID_GROUPS:
                    GROUP_LIST.append(group_item)
        print(colored("DETECTED GROUPS: " + str(len(GROUP_LIST)), 'green'))
    except Exception as e:
        print(bot_name + '<' + bot_username + '>' + 'Encountered a get_group Error\n\n' + str(e))

async def forward_messages():
    """Forward messages to groups with randomized delays to mimic human behavior."""
    global GROUP_LIST
    while True:
        success_groups = []
        current_problems = []
        start = time.time()

        await get_group_ids()

        for group in GROUP_LIST:
            if group not in PROBLEMATIC_LIST:
                try:
                    random_message_id = random.choice(MESSAGE_IDS)
                    source_entity = await client.get_entity(SOURCE_CHAT)
                    group_entity = await client.get_entity(group['id'])  # Get group entity to ensure it's valid
                    await client.forward_messages(group_entity, random_message_id, source_entity)

                    now = datetime.now()
                    current_time = now.strftime("%H:%M:%S")
                    print(bot_name + '<' + bot_username + '>' + ' sent to ' + group['name'] + ' at.. ', current_time)
                    success_groups.append(group)

                    # Random sleep between 3 and 10 seconds to mimic human interaction
                    await asyncio.sleep(random.uniform(10, 15.0))

                except errors.FloodWaitError as e:
                    print(colored(f"{bot_name} FloodWaitError in {group['name']}, retrying in {e.seconds} seconds", 'yellow'))
                    await asyncio.sleep(e.seconds)
                    current_problems.append(group)
                except errors.ChatWriteForbiddenError:
                    print(colored(f"{bot_name} cannot write in {group['name']}, skipping", 'red'))
                    GROUP_LIST.remove(group)
                except errors.PeerIdInvalidError:
                    print(colored(f"{bot_name} invalid peer ID for {group['name']}, skipping", 'red'))
                    INVALID_GROUPS.add(group['id'])
                except Exception as e:
                    print(colored(f"{bot_name} encountered an error in {group['name']}, retrying later", 'yellow'))
                    current_problems.append(group)
                    print(bot_name + '<' + bot_username + '>' + " ERROR in group: " + group['name'] + '\n\n' + str(e))

        # Update the problematic list
        PROBLEMATIC_LIST.clear()
        PROBLEMATIC_LIST.extend(current_problems)

        # Remove invalid groups from GROUP_LIST
        GROUP_LIST = [group for group in GROUP_LIST if group['id'] not in INVALID_GROUPS]

        end = time.time()
        time_taken = int(end - start)
        print(f"Time taken: {time_taken} seconds")

        # Random break duration between 10 and 30 minutes
        break_duration = random.randint(5, 15)
        print(colored(f'😉 Taking a {break_duration}-minute break. Sent to {len(success_groups)} groups out of {len(GROUP_LIST)}', 'green'))

        # Sleep before the next round
        await asyncio.sleep(break_duration * 60)

async def main():
    """Main bot loop."""
    while not is_connected():
        print("No internet connection. Retrying in 10 seconds...")
        await asyncio.sleep(10)

    await get_bot_info()
    await forward_messages()

client.loop.run_until_complete(main())
