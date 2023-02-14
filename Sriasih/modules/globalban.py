import asyncio
import time

from pyrogram import filters
from pyrogram.errors import FloodWait
from pyrogram.types import Message

from config import BANNED_USERS
from Sriasih import app, SUDOERS
from Sriasih.utils import get_readable_time
from Sriasih.utils.dbfunctions import (add_banned_user,
                                       get_banned_count,
                                       get_banned_users,
                                       get_served_chats,
                                       is_banned_user,
                                       remove_banned_user)




@app.on_message(filters.command("gban") & SUDOERS)
async def gbanuser(client, message: Message):
    if not message.reply_to_message:
        if len(message.command) != 2:
            return await message.reply_text("Balas ke pesan pengguna atau berikan ID pengguna")
        user = message.text.split(None, 1)[1]
        user = await app.get_users(user)
        user_id = user.id
        mention = user.mention
    else:
        user_id = message.reply_to_message.from_user.id
        mention = message.reply_to_message.from_user.mention
    if user_id == message.from_user.id:
        return await message.reply_text("Mau Gban diri sendiri?")
    elif user_id == app.id:
        return await message.reply_text("Haruskah saya memblokir diri saya sendiri? Lol")
    elif user_id in SUDOERS:
        return await message.reply_text("Anda ingin memblokir pengguna sudo?")
    is_gbanned = await is_banned_user(user_id)
    if is_gbanned:
        return await message.reply_text(f"{mention} sudah di GBANNED")
    if user_id not in BANNED_USERS:
        BANNED_USERS.add(user_id)
    served_chats = []
    chats = await get_served_chats()
    for chat in chats:
        served_chats.append(int(chat["chat_id"]))
    time_expected = len(served_chats)
    time_expected = get_readable_time(time_expected)
    mystic = await message.reply_text(f"memulai proses GBAN {mention},\nEstimasi waktu {time_expected}")
    number_of_chats = 0
    for chat_id in served_chats:
        try:
            await app.ban_chat_member(chat_id, user_id)
            number_of_chats += 1
        except FloodWait as e:
            await asyncio.sleep(int(e.x))
        except Exception:
            pass
    await add_banned_user(user_id)
    await message.reply_text(f"{mention}Berhasil di GBAN\nDari {number_of_chats}"
    )
    await mystic.delete()


@app.on_message(filters.command("ungban") & SUDOERS)
async def gungabn(client, message: Message):
    if not message.reply_to_message:
        if len(message.command) != 2:
            return await message.reply_text("Balas ke pesan pengguna atau berikan ID pengguna")
        user = message.text.split(None, 1)[1]
        user = await app.get_users(user)
        user_id = user.id
        mention = user.mention
    else:
        user_id = message.reply_to_message.from_user.id
        mention = message.reply_to_message.from_user.mention
    is_gbanned = await is_banned_user(user_id)
    if not is_gbanned:
        return await message.reply_text(f"{mention} tidak ada di list Gban")
    if user_id in BANNED_USERS:
        BANNED_USERS.remove(user_id)
    served_chats = []
    chats = await get_served_chats()
    for chat in chats:
        served_chats.append(int(chat["chat_id"]))
    time_expected = len(served_chats)
    time_expected = get_readable_time(time_expected)
    mystic = await message.reply_text(
        f"memulai proses UNGBAN {mention},\nEstimasi waktu {time_expected}"
    )
    number_of_chats = 0
    for chat_id in served_chats:
        try:
            await app.unban_chat_member(chat_id, user_id)
            number_of_chats += 1
        except FloodWait as e:
            await asyncio.sleep(int(e.x))
        except Exception:
            pass
    await remove_banned_user(user_id)
    await message.reply_text(
        f"{mention}Berhasil di UNGBAN\nDari {number_of_chats}"
    )
    await mystic.delete()


@app.on_message(filters.command("gbanlist") & SUDOERS)
async def gbanned_list(client, message: Message, _):
    counts = await get_banned_count()
    if counts == 0:
        return await message.reply_text("Tidak ada list Gbanned User")
    mystic = await message.reply_text("mengambil list Gbanned User")
    msg = "Gbanned Users:\n\n"
    count = 0
    users = await get_banned_users()
    for user_id in users:
        count += 1
        try:
            user = await app.get_users(user_id)
            user = (
                user.first_name if not user.mention else user.mention
            )
            msg += f"{count}➤ {user}\n"
        except Exception:
            msg += f"{count}➤ [Unfetched User]{user_id}\n"
            continue
    if count == 0:
        return await mystic.edit_text("Tidak Ditemukan Pengguna yang Di-Gban.")
    else:
        return await mystic.edit_text(msg)
