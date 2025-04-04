#!/usr/bin/env python3

# By Ryuk


if __name__ != "__main__":
    import sys

    sys.exit()

print("Starting Stats Genrator.\n")

import asyncio
import datetime
import os

from dotenv import load_dotenv
from pyrogram import Client, raw, types, utils
from pyrogram.enums import ChatType


async def _get_dialogs(folder_id):
    current = 0
    total = (1 << 31) - 1
    limit = 100

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
                folder_id=folder_id,
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


async def get_dialogs():
    # 0 is Main folder 
    # 1 is Archived chats
    for i in 0, 1:
        async for d in _get_dialogs(i):
            yield d


def make_link(chat) -> str:
    if username := chat.username:
        return f"https://t.me/{username}"

    if chat.type == ChatType.PRIVATE:
        return f"tg://user?id={chat.id}"

    return f"https://t.me/c/{chat.id}/-1"


async def gs():
    owner = app.me
    u_mention = owner.first_name

    total = 0

    groups = 0
    group_list = []
    group_owner_list = []
    group_admin_list = []

    channels = 0
    channel_list = []
    channel_owner_list = []
    channel_admin_list = []

    private_chats = 0
    users_list = []
    bot_list = []
    deleted_accounts = []

    unread_mentions = 0
    unread_msg = 0
    unread_reactions = 0

    async for dialog in get_dialogs():
        total += 1

        unread_mentions += dialog.unread_mentions_count
        unread_msg += dialog.unread_messages_count
        unread_reactions += dialog.unread_reactions_count

        chat = dialog.chat
        raw_chat = chat._raw

        chat_type = chat.type
        if chat_type in [ChatType.BOT, ChatType.PRIVATE]:
            private_chats += 1

            if getattr(raw_chat, "deleted", False):
                list_to_append = deleted_accounts
            elif chat_type == ChatType.BOT:
                list_to_append = bot_list
            else:
                list_to_append = users_list

        else:
            creator = raw_chat.creator
            admin = raw_chat.admin_rights

            if chat_type in [ChatType.GROUP, ChatType.SUPERGROUP]:
                groups += 1

                if creator:
                    list_to_append = group_owner_list
                elif admin:
                    list_to_append = group_admin_list
                else:
                    list_to_append = group_list

            else:  # Channel
                channels += 1

                if creator:
                    list_to_append = channel_owner_list
                elif admin:
                    list_to_append = channel_admin_list
                else:
                    list_to_append = channel_list
        try:
            date = datetime.datetime.fromtimestamp(raw_chat.date)
        except:
            date = None

        to_join = [
            f"•> {chat.title or chat.full_name}",
            f"ID: {chat.id}",
            f"Link: {make_link(chat)}",
        ]

        if date:
            to_join.append(f"Date: {date}")

        if dialog.unread_mentions_count:
            to_join.append(f"Unread Mentions: {dialog.unread_mentions_count}")

        if dialog.unread_messages_count:
            to_join.append(f"Unread Messages: {dialog.unread_messages_count}")

        if dialog.unread_reactions_count:
            to_join.append(f"Unread Reactions: {dialog.unread_reactions_count}")

        list_to_append.append("\n  - ".join(to_join))

    results = f"""
<b><u>Telegram Stats</u></b>
User:  <b>{u_mention}</b>
Total: <b>{total}</b>

<b>Private Chats:</b> <code>{private_chats}</code><code>
    • Users: {len(users_list)}
    • Bots: {len(bot_list)}
    • Deleted accounts: {len(deleted_accounts)}</code>

<b>Groups:</b> <code>{groups}</code>
<b>Channels:</b> <code>{channels}</code>

<b>Admin in Groups:</b> <code>{len(group_admin_list+group_owner_list)}</code><code>
    ★ Creator: {len(group_owner_list)}
    • Admin Rights: {len(group_admin_list)}</code>

<b>Admin in Channels:</b> <code>{len(channel_owner_list + channel_admin_list)}</code><code>
    ★ Creator: {len(channel_owner_list)}
    • Admin Rights: {len(channel_admin_list)}</code>

<b>Unread Messages:</b> <code>{unread_msg}</code>
<b>Unread Mentions:</b> <code>{unread_mentions}</code>
<b>Unread Reactions:</b> <code>{unread_reactions}</code>
"""
    stats_message = await app.send_message("me", results)

    print("\n\n", stats_message.text)

    stats_args = (
        ("users", users_list),
        ("bots", bot_list),
        ("deleted_accounts", deleted_accounts),
        ("groups", group_list),
        ("group_owner", group_owner_list),
        ("group_admin", group_admin_list),
        ("channels", channel_list),
        ("channel_owner", channel_owner_list),
        ("channel_admin", channel_admin_list),
    )

    for name, data_list in stats_args:
        write_stats(name, data_list)

    print("\n\nIndividual stats saved to respective files in the directory: stats.")


os.makedirs("stats", exist_ok=True)


def write_stats(stat_name, stat_list):
    with open(f"stats/{stat_name}.txt", "w") as f:
        f.write(f"Total: {len(stat_list)}\n\n{"\n\n\n".join(stat_list)}")


try:
    ask = int(
        input(
            "1.I have Config.env saved"
            "\n2.I don't have config.env, Will enter vars"
            "\nChoose 1 or 2"
            "\n> "
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
except KeyboardInterrupt:
    print("Exited")
