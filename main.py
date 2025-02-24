import os as O, re as R
from pyrogram import Client as C, filters as F
from pyrogram.types import Message as M
import time
import asyncio
from config import API_ID as A, API_HASH as H, BOT_TOKEN as T, SESSION as S, OWNER_ID  # add your owner id here

# Set your private channel backup chat id here:
PRIVATE_CHANNEL = "YOUR_PRIVATE_CHANNEL_CHAT_ID"  # e.g., "-1001234567890"
# Set your forced subscription channel id or username
FORCE_SUBS_CHANNEL = "YOUR_FORCE_SUBS_CHANNEL"  # e.g., "@yourchannel"

# Authorized users dictionary: {user_id: "free" or "premium"}
AUTHORIZED_USERS = {}  # owner can add or remove users dynamically

# Free video extraction counter for free users: {user_id: count}
FREE_VIDEO_COUNT = {}

# Initialize bot client (X) and user client (Y)
X = C("X", api_id=A, api_hash=H, bot_token=T)
Y = C("Y", api_id=A, api_hash=H, session_string=S)
Z, W = {}, {}

try:
    Y.start()
    print("userbot started")
except Exception:
    print("check your session")
    pass

progress_cache = {}

def E(L):
    # Extract channel/chat ID and message ID from link
    Q = R.match(r"https://t\.me/c/(\d+)/(\d+)", L)
    P = R.match(r"https://t\.me/([^/]+)/(\d+)", L)
    if Q:
        return f"-100{Q.group(1)}", int(Q.group(2)), "private"
    elif P:
        return P.group(1), int(P.group(2)), "public"
    else:
        return None, None, None

async def J(C_obj, U_obj, I, D, link_type):
    # Fetch message from public or private chat based on link_type
    try:
        print(f"Fetching message from {I}, Message ID: {D}, Type: {link_type}")
        return await (C_obj if link_type == "public" else U_obj).get_messages(I, D)
    except Exception as e:
        print(f"Error fetching message: {e}")
        return None

async def K(c, t, C_obj, h, m, start_time):
    # Progress updater function
    global progress_cache
    p = (c / t) * 100
    step = int(p // 10) * 10

    if m not in progress_cache or progress_cache[m] != step or p >= 100:
        progress_cache[m] = step
        bar = "🟢" * (int(p / 10)) + "🔴" * (10 - int(p / 10))
        speed = (c / (time.time() - start_time)) / (1024 * 1024) if time.time() > start_time else 0
        eta = time.strftime("%M:%S", time.gmtime((t - c) / (speed * 1024 * 1024))) if speed > 0 else "00:00"
        await C_obj.edit_message_text(h, m, f"__**Pyro Handler...**__\n\n{bar}\n\n📊 **__Completed__**: {p:.2f}%\n🚀 **__Speed__**: {speed:.2f} MB/s\n⏳ **__ETA__**: {eta}\n\n**__ PRINCE __**")
        if p >= 100:
            progress_cache.pop(m, None)

async def V(C_obj, U_obj, m_obj, d, link_type, u):
    """
    Modified function V returns a tuple: (status_string, sent_message_object)
    Also enforces a limit of 5 video extractions for free users.
    """
    try:
        if m_obj.media:
            # Check if this is a video and if the user is free
            if m_obj.video and AUTHORIZED_USERS.get(u, "free") == "free":
                if FREE_VIDEO_COUNT.get(u, 0) >= 5:
                    return "Video extraction limit reached for free users. Upgrade to premium for unlimited access.", None
                else:
                    FREE_VIDEO_COUNT[u] = FREE_VIDEO_COUNT.get(u, 0) + 1

            st = time.time()
            if link_type == "private":
                P = await C_obj.send_message(d, "Downloading...")
                W[u] = {"cancel": False, "progress": P.id}
                F_path = await U_obj.download_media(m_obj, progress=K, progress_args=(C_obj, d, P.id, st))
                if W.get(u, {}).get("cancel"):
                    await C_obj.edit_message_text(d, P.id, "Canceled.")
                    if O.path.exists(F_path):
                        O.remove(F_path)
                    del W[u]
                    return "Canceled.", None
                if not F_path:
                    await C_obj.edit_message_text(d, P.id, "Failed.")
                    del W[u]
                    return "Failed.", None
                await C_obj.edit_message_text(d, P.id, "Uploading...")
                th = "v3.jpg"
                if m_obj.video:
                    width, height, duration = m_obj.video.width, m_obj.video.height, m_obj.video.duration
                    sent_msg = await C_obj.send_video(d, video=F_path, caption=m_obj.caption.markdown, thumb=th,
                                                      width=width, height=height, duration=duration,
                                                      progress=K, progress_args=(C_obj, d, P.id, st))
                elif m_obj.video_note:
                    sent_msg = await C_obj.send_video_note(d, video_note=F_path, progress=K, progress_args=(C_obj, d, P.id, st))
                elif m_obj.voice:
                    sent_msg = await C_obj.send_voice(d, F_path, progress=K, progress_args=(C_obj, d, P.id, st))
                elif m_obj.sticker:
                    sent_msg = await C_obj.send_sticker(d, m_obj.sticker.file_id)
                elif m_obj.audio:
                    try:
                        thumb = await U_obj.download_media(m_obj.audio.thumbs[0].file_id)
                    except:
                        thumb = None
                    sent_msg = await C_obj.send_audio(d, audio=F_path, caption=m_obj.caption.markdown, thumb=th,
                                                      progress=K, progress_args=(C_obj, d, P.id, st))
                    if thumb is not None:
                        O.remove(thumb)
                elif m_obj.photo:
                    sent_msg = await C_obj.send_photo(d, photo=F_path, caption=m_obj.caption.markdown,
                                                      progress=K, progress_args=(C_obj, d, P.id, st))
                elif m_obj.document:
                    sent_msg = await C_obj.send_document(d, document=F_path, caption=m_obj.caption.markdown,
                                                         progress=K, progress_args=(C_obj, d, P.id, st))
                O.remove(F_path)
                await C_obj.delete_messages(d, P.id)
                del W[u]
                return "Done.", sent_msg
            else:
                sent_msg = await m_obj.copy(chat_id=d)
                return "Copied.", sent_msg
        elif m_obj.text:
            if link_type == "private":
                sent_msg = await C_obj.send_message(d, text=m_obj.text.markdown)
            else:
                sent_msg = await m_obj.copy(chat_id=d)
            return "Sent.", sent_msg
    except Exception as e:
        return f"Error: {e}", None

# ----------------------- Authentication & Force-Sub Check -----------------------

async def is_subscribed(user_id):
    try:
        member = await X.get_chat_member(FORCE_SUBS_CHANNEL, user_id)
        if member.status in ["member", "administrator", "creator"]:
            return True
        else:
            return False
    except Exception as e:
        return False

def auth_required(func):
    async def wrapper(C_obj, m: M, *args, **kwargs):
        user_id = m.from_user.id
        # Check if user is authorized
        if user_id not in AUTHORIZED_USERS:
            await m.reply_text("❌ You are not authorized to use this bot. Contact the owner for access.")
            return
        # Check forced subscription
        if not await is_subscribed(user_id):
            await m.reply_text(f"❌ You must join {FORCE_SUBS_CHANNEL} to use this bot.")
            return
        return await func(C_obj, m, *args, **kwargs)
    return wrapper

# ----------------------- Command Handlers -----------------------

@X.on_message(F.command("start"))
async def start_handler(C_obj, m: M):
    await m.reply_text(
        "🚀✨ ʜᴇʟʟᴏ! ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴛʜᴇ Sᴀᴠᴇ Rᴇsᴛʀɪᴄᴛᴇᴅ ʙᴏᴛ! ✨🚀\n"
        "🔐 ʏᴏᴜʀ ғɪʟᴇs ᴀʀᴇ sᴀғᴇ & sᴇᴄᴜʀᴇ ᴡɪᴛʜ ᴜs! 🔥\n"
        "⚡ ᴅʀᴏᴘ ʏᴏᴜʀ ʟɪɴᴋ ᴀɴᴅ ʟᴇᴛ'ꜱ ɢᴇᴛ ꜱᴛᴀʀᴛᴇᴅ! 🎯\n\n"
        "Note: You must be authorized and subscribed to use all features."
    )

# Owner-only command to add authorized users
@X.on_message(F.command("adduser"))
async def add_user_handler(C_obj, m: M):
    user_id = m.from_user.id
    if user_id != OWNER_ID:
        await m.reply_text("❌ Only the owner can add users.")
        return
    args = m.text.split()
    if len(args) < 3:
        await m.reply_text("Usage: /adduser <user_id> <free/premium>")
        return
    try:
        target_id = int(args[1])
    except ValueError:
        await m.reply_text("Invalid user_id.")
        return
    user_type = args[2].lower()
    if user_type not in ["free", "premium"]:
        await m.reply_text("User type must be either 'free' or 'premium'.")
        return
    AUTHORIZED_USERS[target_id] = user_type
    await m.reply_text(f"✅ User {target_id} added as {user_type}.")

# Owner-only command to remove authorized users
@X.on_message(F.command("removeuser"))
async def remove_user_handler(C_obj, m: M):
    user_id = m.from_user.id
    if user_id != OWNER_ID:
        await m.reply_text("❌ Only the owner can remove users.")
        return
    args = m.text.split()
    if len(args) < 2:
        await m.reply_text("Usage: /removeuser <user_id>")
        return
    try:
        target_id = int(args[1])
    except ValueError:
        await m.reply_text("Invalid user_id.")
        return
    if target_id in AUTHORIZED_USERS:
        del AUTHORIZED_USERS[target_id]
        await m.reply_text(f"✅ User {target_id} removed.")
    else:
        await m.reply_text("User not found in authorized list.")

# Owner-only command to view bot stats
@X.on_message(F.command("stats"))
async def stats_handler(C_obj, m: M):
    user_id = m.from_user.id
    if user_id != OWNER_ID:
        await m.reply_text("❌ Only the owner can view stats.")
        return
    total_users = len(AUTHORIZED_USERS)
    free_users = sum(1 for ut in AUTHORIZED_USERS.values() if ut == "free")
    premium_users = sum(1 for ut in AUTHORIZED_USERS.values() if ut == "premium")
    await m.reply_text(f"📊 Bot Stats:\nTotal Users: {total_users}\nFree Users: {free_users}\nPremium Users: {premium_users}")

# New join command to join a channel using join link
@X.on_message(F.command("join"))
@auth_required
async def join_handler(C_obj, m: M):
    args = m.text.split(maxsplit=1)
    if len(args) < 2:
        await m.reply_text("Please provide a join link after the command.")
        return
    join_link = args[1]
    try:
        # Using user client (Y) to join the chat
        await Y.join_chat(join_link)
        await m.reply_text("✅ Successfully joined the channel!")
    except Exception as e:
        await m.reply_text(f"❌ Error joining channel: {e}")

@X.on_message(F.command("batch"))
@auth_required
async def B(C_obj, m: M):
    U = m.from_user.id
    Z[U] = {"step": "start"}
    await m.reply_text("Send start link.")

@X.on_message(F.command("cancel"))
@auth_required
async def N(C_obj, m: M):
    U = m.from_user.id
    if U in W:
        W[U]["cancel"] = True
        await m.reply_text("Cancelling...")
    else:
        await m.reply_text("No active task.")

@X.on_message(F.text & ~F.command(["start", "batch", "cancel", "join", "adduser", "removeuser", "stats"]))
@auth_required
async def H(C_obj, m: M):
    U = m.from_user.id
    if U not in Z:
        return
    current_step = Z[U].get("step")
    if current_step == "start":
        L = m.text
        I, D, link_type = E(L)
        if not I or not D:
            await m.reply_text("Invalid link. Please check the format.")
            del Z[U]
            return
        Z[U].update({"step": "count", "cid": I, "sid": D, "lt": link_type})
        await m.reply_text("How many messages?")
    elif current_step == "count":
        if not m.text.isdigit():
            await m.reply_text("Enter a valid number.")
            return
        Z[U].update({"step": "dest", "num": int(m.text)})
        await m.reply_text("Send destination chat ID for backup (primary destination will be your user-provided ID and backup will also be forwarded to your private channel).")
    elif current_step == "dest":
        # Here, user provides the primary destination chat id.
        d_chat = m.text.strip()
        Z[U].update({"step": "process", "did": d_chat})
        I, start_msg_id, N_val, link_type = Z[U]["cid"], Z[U]["sid"], Z[U]["num"], Z[U]["lt"]
        R_count = 0
        primary_sent_msgs = []  # To store sent messages in primary destination
        backup_sent_msgs = []   # To store sent messages in backup (private channel)
        pt = await m.reply_text(
            """⏳✨ Pʀᴏᴄessɪɴɢ ʏᴏᴜʀ ʀᴇǫᴜᴇsᴛ... 🔄🚀
🛠️ Pʟᴇᴀsᴇ ʜᴏʟᴅ ᴏɴ ᴘᴀᴛɪᴇɴᴛʟʏ, ʏᴏᴜʀ ғɪʟᴇs ɪs ʙᴇɪɴɢ ᴘʀᴏᴄessᴇᴅ! 🎯💫"""
        )
        max_retries = 5
        for i in range(N_val):
            msg_id = start_msg_id + i
            retries = 0
            while retries < max_retries:
                msg_obj = await J(C_obj, Y, I, msg_id, link_type)
                if msg_obj:
                    # Try processing and forwarding to both primary and backup channels
                    res1, sent_msg1 = await V(C_obj, Y, msg_obj, d_chat, link_type, U)
                    res2, sent_msg2 = await V(C_obj, Y, msg_obj, PRIVATE_CHANNEL, link_type, U)
                    if "limit reached" in res1.lower() or "limit reached" in res2.lower():
                        await m.reply_text("Free video extraction limit reached. Upgrade to premium for unlimited access.")
                        del Z[U]
                        return
                    if (res1 in ["Done.", "Copied.", "Sent."]) and (res2 in ["Done.", "Copied.", "Sent."]):
                        await pt.edit(f"{i+1}/{N_val}: {res1} & {res2}")
                        R_count += 1
                        if sent_msg1:
                            primary_sent_msgs.append(sent_msg1)
                        if sent_msg2:
                            backup_sent_msgs.append(sent_msg2)
                        break
                    else:
                        await pt.edit(f"{i+1}/{N_val}: Attempt {retries+1} failed: {res1} & {res2}")
                else:
                    await m.reply_text(f"{msg_id} not found. Retrying...")
                retries += 1
                await asyncio.sleep(3)
            if retries == max_retries:
                await m.reply_text(f"Failed to process message {msg_id} after {max_retries} retries.")
        await m.reply_text(f"Batch Completed ✅")
        # Pin first and last messages in primary destination
        if primary_sent_msgs:
            try:
                await X.pin_chat_message(d_chat, primary_sent_msgs[0].message_id)
                await X.pin_chat_message(d_chat, primary_sent_msgs[-1].message_id)
                await m.reply_text("Primary destination: Start and end messages pinned.")
            except Exception as e:
                await m.reply_text(f"Error pinning in primary destination: {e}")
        # Pin first and last messages in backup (private channel)
        if backup_sent_msgs:
            try:
                await X.pin_chat_message(PRIVATE_CHANNEL, backup_sent_msgs[0].message_id)
                await X.pin_chat_message(PRIVATE_CHANNEL, backup_sent_msgs[-1].message_id)
                await m.reply_text("Backup destination: Start and end messages pinned.")
            except Exception as e:
                await m.reply_text(f"Error pinning in backup destination: {e}")
        del Z[U]

print("Bot started successfully!!")
X.run()
