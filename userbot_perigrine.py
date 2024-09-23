import time
import asyncio
from datetime import datetime
import random
from telethon import TelegramClient, errors
from termcolor import colored
import socket
import logging

logging.basicConfig(level=logging.WARNING)

# Your Telegram API credentials
API_ID = 29256324  # Replace with your API ID
API_HASH = 'c0b8670a63f1451e28cd06569915ea70'   # Replace with your API Hash
PHONE_NUMBER = '254799228645'  # Replace with your phone number
SOURCE_CHAT = "@fromose"
MESSAGE_IDS = [44]
PROBLEMATIC_LIST = []

bot_name, bot_username = '', ''
GROUP_LIST = []
INVALID_GROUPS = set()

client = TelegramClient('userbot_session_perigrine', API_ID, API_HASH)
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
    try:
        print('Trying to gather groups...')
        async for dialog in client.iter_dialogs():
            if dialog.is_group:
                group_item = {"name": dialog.title, "id": dialog.id}
                if group_item not in GROUP_LIST:
                    GROUP_LIST.append(group_item)
        print(colored("DETECTED GROUPS: " + str(len(GROUP_LIST)), 'green'))
    except Exception as e:
        print(bot_name + '<' + bot_username + '>' + 'Encountered a get_group Error\n\n' + str(e))

async def forward_messages():
    """Forward messages to groups."""
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

                    await asyncio.sleep(1.0)

                except errors.FloodWaitError as e:
                    print(colored(bot_name + " will retry in " + group['name'] + " due to FloodWait\n", 'yellow'))
                    current_problems.append(group)
                except errors.ChatWriteForbiddenError:
                    print(colored(bot_name + " cannot write in " + group['name'] + ", skipping\n", 'red'))
                    GROUP_LIST.remove(group)
                except errors.PeerIdInvalidError:
                    print(colored(bot_name + " encountered invalid peer ID for " + group['name'] + ", skipping\n", 'red'))
                    GROUP_LIST.remove(group)
                except Exception as e:
                    print(colored(bot_name + " will retry in " + group['name'] + " in the next round\n", 'yellow'))
                    current_problems.append(group)
                    print(bot_name + '<' + bot_username + '>' + " ERROR at group: " + group['name'] + '\n\n' + str(e))

        # Update the problematic list
        PROBLEMATIC_LIST.clear()
        PROBLEMATIC_LIST.extend(current_problems)

        end = time.time()
        time_taken = int(end - start)
        print("Time taken: " + str(time_taken) + ' seconds')

        break_duration = random.randint(1, 10)  # Random break between 1 to 10 minutes
        print(colored(f'😉 {break_duration} minutes break, sent to ' + str(len(success_groups)) + ' groups out of ' + str(len(GROUP_LIST)), 'green'))

        await asyncio.sleep(break_duration * 60)

async def main():
    while not is_connected():
        print("No internet connection. Retrying in 5 seconds...")
        await asyncio.sleep(5)
    
    await get_bot_info()
    await forward_messages()

client.loop.run_until_complete(main())