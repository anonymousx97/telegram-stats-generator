# Modded to work Standalone by Ryuk
# Based on Stats.py from the bot userge-x

import asyncio
import os
import sys

if __name__ != "__main__":
    sys.exit()
print("Starting Stats Genrator.\n")

from dotenv import load_dotenv
from pyrogram import Client
from pyrogram.enums import ChatMemberStatus, ChatType
from pyrogram.errors import FloodWait, UserNotParticipant


async def gs():
    owner = await app.get_me()
    u_mention = owner.first_name
    unread_mentions = 0
    unread_msg = 0
    private_chats = 0
    bots = 0
    users_ = 0
    groups = 0
    groups_admin = 0
    groups_creator = 0
    channels = 0
    channels_admin = 0
    channels_creator = 0
    async for dialog in app.get_dialogs():
        try:
            unread_mentions += dialog.unread_mentions_count
            unread_msg += dialog.unread_messages_count
            chat_type = dialog.chat.type
            if chat_type in [ChatType.BOT, ChatType.PRIVATE]:
                private_chats += 1
                if chat_type == ChatType.BOT:
                    bots += 1
                else:
                    users_ += 1
            else:
                try:
                    checks_ = (
                        await app.get_chat_member(dialog.chat.id, owner.id)
                    ).status
                except:
                    pass
                if chat_type in [ChatType.GROUP, ChatType.SUPERGROUP]:
                    groups += 1
                    if checks_ == ChatMemberStatus.OWNER:
                        groups_creator += 1
                    if checks_ == ChatMemberStatus.ADMINISTRATOR:
                        groups_admin += 1
                else:  # Channel
                    channels += 1
                    if checks_ == ChatMemberStatus.OWNER:
                        channels_creator += 1
                    if checks_ == ChatMemberStatus.ADMINISTRATOR:
                        channels_admin += 1
        except FloodWait as e:
            await asyncio.sleep(e.value + 5)

    results = f"""
<b><u>Telegram Stats</u></b>
User:  <b>{u_mention}</b>

<b>Private Chats:</b> <code>{private_chats}</code><code>
    • Users: {users_}
    • Bots: {bots}</code>
<b>Groups:</b> <code>{groups}</code>
<b>Channels:</b> <code>{channels}</code>
<b>Admin in Groups:</b> <code>{groups_admin}</code><code>
    ★ Creator: {groups_creator}
    • Admin Rights: {groups_admin - groups_creator}</code>
<b>Admin in Channels:</b> <code>{channels_admin}</code><code>
    ★ Creator: {channels_creator}
    • Admin Rights: {channels_admin - channels_creator}</code>
<b>Unread Messages:</b> <code>{unread_msg}</code>
<b>Unread Mentions:</b> <code>{unread_mentions}</code>
"""
    await app.send_message("me", results)


try:
    ask = int(
        input(
            "1.I have Config.env saved\n2.I don't have config.env, Will enter vars\nChoose 1 or 2\n> "
        )
    )
    if ask == 1:
        path = input(
            "\nEnter path to your config or just enter file name if it's in the same directory.\n> "
        )
        if not load_dotenv(path):
            print("\nCouldn't load config.\nEnter Vars manually.")
        else:
            print("\nConfig Loaded.")

    API_ID = int(os.environ.get("API_ID", 0)) or int(input("Your API ID: "))
    API_HASH = os.environ.get("API_HASH") or input("Your API HASH: ")
    STRING = os.environ.get("STRING_SESSION")

    app = Client(
        name="bot",
        session_string=STRING,
        api_id=API_ID,
        api_hash=API_HASH,
        in_memory=True,
    )

    app.start()
    print("Started.")
    app.run(gs())
    print("Done, Stats sent to saved messages")
except KeyboardInterrupt:
    print("Exited")
