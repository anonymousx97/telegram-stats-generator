# Modded to work Standalone by Ryuk
# Based on Stats.py from the bot userge-x

import asyncio
import os
import sys

if __name__ != "__main__":
    sys.exit()

print("Starting Stats Genrator.\n")


import pyrogram
from dotenv import load_dotenv
from pyrogram import Client, raw, types, utils
from pyrogram.enums import ChatMemberStatus, ChatType
from pyrogram.errors import FloodWait, UserNotParticipant


async def get_dialogs():

    current = 0
    total = (1 << 31) - 1
    limit = min(100, total)

    offset_date = 0
    offset_id = 0
    offset_peer = raw.types.InputPeerEmpty()

    while True:
        r = await app.invoke(
            raw.functions.messages.GetDialogs(
                offset_date=offset_date,
                offset_id=offset_id,
                offset_peer=offset_peer,
                limit=limit,
                hash=0,
                exclude_pinned=False,
                folder_id=0,
            ),
            sleep_threshold=60,
        )

        users = {i.id: i for i in r.users}
        chats = {i.id: i for i in r.chats}

        messages = {}

        dialogs = []

        for message in r.messages:
            if isinstance(message, raw.types.MessageEmpty):
                continue

            chat_id = utils.get_peer_id(message.peer_id)

            messages[chat_id] = message

        for dialog in r.dialogs:
            if not isinstance(dialog, raw.types.Dialog):
                continue

            dialogs.append(types.Dialog._parse(app, dialog, messages, users, chats))

        if not dialogs:
            return

        last = dialogs[-1]

        offset_id = last.top_message.id
        offset_date = last.top_message.date
        offset_peer = last._raw.peer

        for dialog in dialogs:
            await asyncio.sleep(0)
            yield dialog

            current += 1

            if current >= total:
                return

        await asyncio.sleep(5)


async def gs():
    owner = app.me
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
    total = 0
    async for dialog in get_dialogs():
        total += 1

        print(dialog.chat.id, dialog.chat.title or dialog.chat.first_name)

        unread_mentions += dialog.unread_mentions_count
        unread_msg += dialog.unread_messages_count

        try:
            chat_type = dialog.chat.type
        except:
            print(dialog, dialog.chat)
            continue

        if chat_type in [ChatType.BOT, ChatType.PRIVATE]:
            private_chats += 1
            if chat_type == ChatType.BOT:
                bots += 1
            else:
                users_ += 1
            continue

        try:
            rdc = dialog.chat._raw
            creator = rdc.creator
            admin = rdc.admin_rights
        except:
            print(dialog, dialog.chat)
            continue

        if chat_type in [ChatType.GROUP, ChatType.SUPERGROUP]:
            groups += 1
            if creator:
                groups_creator += 1
            elif admin:
                groups_admin += 1
        else:  # Channel
            channels += 1
            if creator:
                channels_creator += 1
            elif admin:
                channels_admin += 1

    results = f"""
<b><u>Telegram Stats</u></b>
User:  <b>{u_mention}</b>
Total: <b>{total}</b>

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
    STRING = os.environ.get("SESSION_STRING")

    app = Client(
        name="bot",
        session_string=STRING,
        api_id=API_ID,
        api_hash=API_HASH,
        no_updates=True,
        takeout=True,
    )

    app.start()
    print("Started.")
    app.run(gs())
    print("Done, Stats sent to saved messages")
except KeyboardInterrupt:
    print("Exited")
