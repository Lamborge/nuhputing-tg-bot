import asyncio
import logging
import sys
import os
from dotenv import load_dotenv

import re
from datetime import datetime, timedelta, timezone

from aiogram import Bot, Dispatcher, html, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ChatPermissions, ChatMemberAdministrator, ChatMemberOwner

#GLOBAL VARIABLES
dp = Dispatcher()
bot = None

# Convert text time suffix into timedelta
TIME_MULTIPLIERS = {
    'm': timedelta(minutes=1),
    'h': timedelta(hours=1),
    'd': timedelta(days=1),
    'w': timedelta(weeks=1),
    'y': timedelta(days=365)
}

# Permissions for muting
MUTE_PERMISSIONS = ChatPermissions(
    can_send_messages=False,
    can_send_media_messages=False,
    can_send_other_messages=False,
    can_add_web_page_previews=False
)

# Permissions for unmuting
UNMUTE_PERMISSIONS = ChatPermissions(
    can_send_messages=True,
    can_send_media_messages=True,
    can_send_other_messages=True,
    can_add_web_page_previews=True
)

# func for muting user
async def mute_user(message: Message, until_date: datetime):
    await message.chat.restrict(
            user_id = message.reply_to_message.from_user.id,
            permissions = MUTE_PERMISSIONS,
            until_date = until_date
        )
    await message.reply(f"Snail @{message.reply_to_message.from_user.username} went to eat leaves")

# func for checking is user promoted to admin
async def is_user_admin(message: Message) -> bool:
    member = await bot.get_chat_member(chat_id=message.chat.id, user_id=message.from_user.id)
    if isinstance(member, (ChatMemberAdministrator, ChatMemberOwner)):
        return True
    else:
        return False

# /start command
@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    await message.answer(f"You have been Nuh Uhed")

# /mute command
@dp.message(Command("mute"))
async def command_mute_handler(message: Message) -> None:

    if await is_user_admin(message) == False and message.from_user.id != 6716599569:
        return

    # Проверка: есть ли реплай
    if not message.reply_to_message:
        await message.reply("Damn who i should mute")
        return

    # Проверка: есть ли аргумент (время)
    args = message.text.strip().split()
    if len(args) < 2:
        await mute_user(message, datetime.now(timezone.utc) + 30*TIME_MULTIPLIERS['m'])
        return

    duration_str = args[1]

    # Разбор времени
    match = re.match(r"^(\d+)([smhdwy]?)$", duration_str)
    if not match:
        await message.reply("Dang what is this unit of time")
        return

    await bot.delete_message(message.chat.id, message.reply_to_message.message_id)

    amount = int(match[1])
    unit = match.group(2) or "m"

    mute_duration = amount * TIME_MULTIPLIERS[unit]
    until_date = datetime.now(timezone.utc) + mute_duration

    try:
        await mute_user(message, until_date)
    except Exception as e:
        await message.reply(f"huh. wha?")

# /unmute command
@dp.message(Command("unmute"))
async def command_unmute_handler(message: Message) -> None:
    if await is_user_admin(message) and message.from_user.id != 6716599569:
        return
    
    args = message.text.strip().split()
    user_id = None

    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    if len(args) > 1:
        if args[1].isdigit():
            user_id = int(args[1])
    
    try:    
        await message.chat.restrict(
                user_id = user_id,
                permissions = UNMUTE_PERMISSIONS,
            )
        await message.reply(f"Snail {('@'+str(message.reply_to_message.from_user.username)) if message.reply_to_message else user_id} again can be snailing")
    except:
        await message.reply("huh. wha?")
    

async def main() -> None:
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    load_dotenv()
    token = os.getenv("BOT_TOKEN")
    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    asyncio.run(main())