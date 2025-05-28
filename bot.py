import asyncio
import logging
import sys
import os
from dotenv import load_dotenv
import random

import re
from datetime import datetime, timedelta, timezone

from aiogram import Bot, Dispatcher, html, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ChatPermissions, ChatMemberAdministrator, ChatMemberOwner

#======GLOBAL VARIABLES======
dp = Dispatcher()
bot = None

# Array of stickers file_id for randomly sending
R_STICKERS = [
    "CAACAgIAAxkBAAEBPoNoNv6mNQkd8VIWtgd7jyukr4ilSgAC-XMAAtcKCEu1Hewfp7mnsDYE", # rigby falling
    "CAACAgIAAxkBAAEBPoVoN28Qm3AhHt7h04xu_xrJdsIiAQACZHwAAsFVaEnML10-rEKokjYE", # :3 bunny
    "CAACAgIAAxkBAAEBPoZoN28QzZBIuogvTyIAAc0BYU4dZgkAArtuAAJobMBLgM1iVsLVM0I2BA", # ec chan in bucket
    "CAACAgIAAxkBAAEBPodoN28QWgNo-qxNGmo7A0PelO6EcAACMG0AAvXZuUldUB8Kg-HzXjYE" # glorp orange girl
]

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
    can_add_web_page_previews=False,
)

# Permissions for unmuting
UNMUTE_PERMISSIONS = ChatPermissions(
    can_send_messages=True,
    can_send_media_messages=True,
    can_send_other_messages=True,
    can_add_web_page_previews=True
)

# Strings for error messages
ERROR_EXCEPTION_STRING= "huh. wha?"
ERROR_NO_REPLY_STRING = "no snail detected"
#======END GLOBAL VARIABLES======



# func for muting user
async def mute_user(message: Message, until_date: datetime):
    await message.chat.restrict(
            user_id = message.reply_to_message.from_user.id,
            permissions = MUTE_PERMISSIONS,
            until_date = until_date
        )
    await message.reply(f"Snail @{message.reply_to_message.from_user.username} went to eat leaves")

# func for checking is user admin
async def is_user_admin(message: Message) -> bool:
    member = await bot.get_chat_member(chat_id=message.chat.id, user_id=message.from_user.id)
    if isinstance(member, (ChatMemberAdministrator, ChatMemberOwner)):
        return True
    if message.from_user.username == "GroupAnonymousBot":
        return True
    
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

    if not message.reply_to_message:
        await message.reply(ERROR_NO_REPLY_STRING)
        return

    args = message.text.strip().split()
    # if time is not specified then mute for 30m
    if len(args) < 2:
        await mute_user(message, datetime.now(timezone.utc) + 30*TIME_MULTIPLIERS['m'])
        return

    duration_str = args[1]

    # Parse time argument
    match = re.match(r"^(\d+)([smhdwy]?)$", duration_str)
    if not match:
        await message.reply("Dang what is this unit of time")
        return

    amount = int(match.group(1))
    unit = match.group(2) or "m"

    mute_duration = amount * TIME_MULTIPLIERS[unit]
    until_date = datetime.now(timezone.utc) + mute_duration

    try:
        await mute_user(message, until_date)
        await bot.delete_message(message.chat.id, message.reply_to_message.message_id)
    except:
        await message.reply(ERROR_EXCEPTION_STRING)

# /unmute and /unban command
@dp.message(Command(commands=["unmute", "unban"]))
async def command_unmute_handler(message: Message) -> None:
    if await is_user_admin(message) == False:
        return
    
    args = message.text.strip().split()
    user_id = None

    # if reply - user id = user id from reply
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    if len(args) > 1:
        if args[1].isdigit():
            user_id = int(args[1])

    # user id is not none verification
    if user_id == None:
        await message.reply(ERROR_NO_REPLY_STRING)
        return
    
    try:
        await message.chat.restrict(
                user_id = user_id,
                permissions = UNMUTE_PERMISSIONS,
            )
        await message.reply(f"Snail {('@'+str(message.reply_to_message.from_user.username)) if message.reply_to_message else user_id} again can be snailing")
    except:
        await message.reply(ERROR_EXCEPTION_STRING)

# /ban command
@dp.message(Command("ban"))
async def command_ban_handler(message: Message) -> None:
    if await is_user_admin(message) == False:
        return
    
    if not message.reply_to_message:
        await message.reply(ERROR_NO_REPLY_STRING)
        return
    
    try:
        await message.chat.restrict(
            user_id=message.reply_to_message.from_user.id,
            permissions=MUTE_PERMISSIONS
            )
        await message.reply_to_message.delete()
        await message.reply(f"@{message.reply_to_message.from_user.username} has been touched by the snail")
    except:
        await message.reply(ERROR_EXCEPTION_STRING)

@dp.message()
async def message_handler(message: Message) -> None:

    if message.text:
        _msg = message.text.strip().lower()

        if "insane" in _msg:
            chance = 0

            if _msg == "insane": # if msg text is just "insane" then chance to reply is 15%
                chance = 0.23
            else:
                chance = 0.15
            
            if random.random() < chance:
                await message.reply("insane")
            return

        # reply for yo
        elif re.search(r"\byo\b", _msg):
            await message.reply("gurt")
            return

        # reply for fumo
        elif "fumo" in _msg:
            await message.reply("OMG FUMO!!11!!1!11!!!" if random.random() < 0.5 else "ᗜˬᗜ")
            return
        
        # reply for crazy
        elif re.search(r"\bcrazy\b", _msg):
            if random.random() < 0.2:
                await message.reply("Crazy? I was crazy once. They locked me in a room. A rubber room. A rubber room with rats. And rats make me crazy.")
                return

        # reply for snail
        elif re.search(r"\bsnail\b", _msg):
            await message.reply("🐌")
            return
        
        # reply for nah, nuh, uh
        elif re.search(r"\bnah\b", _msg) or re.search(r"\bnuh\b", _msg) or re.search(r"\suh\b", _msg):
            if random.random() < 0.5:
                await message.reply("Nuh uh")
                return

    # 2% to send a sticker in reply
    if random.random() < 0.02:
        await message.reply_sticker(sticker=random.choice(R_STICKERS))
        return
        

async def main() -> None:
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    load_dotenv()
    token = os.getenv("BOT_TOKEN")
    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    asyncio.run(main())