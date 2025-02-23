import os as O, re as R
from pyrogram import Client as C, filters as F
from pyrogram.types import Message as M
import time
import asyncio
from config import API_ID as A, API_HASH as H, BOT_TOKEN as T, SESSION as S

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
    try:
        if m_obj.media:
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
                    return "Canceled."
                if not F_path:
                    await C_obj.edit_message_text(d, P.id, "Failed.")
                    del W[u]
                    return "Failed."
                await C_obj.edit_message_text(d, P.id, "Uploading...")
                th = "v3.jpg"
                if m_obj.video:
                    width, height, duration = m_obj.video.width, m_obj.video.height, m_obj.video.duration
                    await C_obj.send_video(d, video=F_path, caption=m_obj.caption.markdown, thumb=th,
                                           width=width, height=height, duration=duration,
                                           progress=K, progress_args=(C_obj, d, P.id, st))
                elif m_obj.video_note:
                    await C_obj.send_video_note(d, video_note=F_path, progress=K, progress_args=(C_obj, d, P.id, st))
                elif m_obj.voice:
                    await C_obj.send_voice(d, F_path, progress=K, progress_args=(C_obj, d, P.id, st))
                elif m_obj.sticker:
                    await C_obj.send_sticker(d, m_obj.sticker.file_id)
                elif m_obj.audio:
                    try:
                        thumb = await U_obj.download_media(m_obj.audio.thumbs[0].file_id)
                    except:
                        thumb = None
                    await C_obj.send_audio(d, audio=F_path, caption=m_obj.caption.markdown, thumb=th,
                                           progress=K, progress_args=(C_obj, d, P.id, st))
                    if thumb is not None:
                        O.remove(thumb)
                elif m_obj.photo:
                    await C_obj.send_photo(d, photo=F_path, caption=m_obj.caption.markdown,
                                           progress=K, progress_args=(C_obj, d, P.id, st))
                elif m_obj.document:
                    await C_obj.send_document(d, document=F_path, caption=m_obj.caption.markdown,
                                              progress=K, progress_args=(C_obj, d, P.id, st))
                O.remove(F_path)
                await C_obj.delete_messages(d, P.id)
                del W[u]
                return "Done."
            else:
                await m_obj.copy(chat_id=d)
                return "Copied."
        elif m_obj.text:
            await (C_obj.send_message(d, text=m_obj.text.markdown)
                     if link_type == "private" else m_obj.copy(chat_id=d))
            return "Sent."
    except Exception as e:
        return f"Error: {e}"

@X.on_message(F.command("start"))
async def sex(C_obj, m: M):
    await m.reply_text(
    "🚀✨ ʜᴇʏ! ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴛʜᴇ Sᴀᴠᴇ Rᴇsᴛʀɪᴄᴛᴇᴅ ʙᴏᴛ! ✨🚀\n"
    "🔐 ʏᴏᴜʀ ғɪʟᴇs ᴀʀᴇ sᴀғᴇ & sᴇᴄᴜʀᴇ ᴡɪᴛʜ ᴜs! 🔥\n"
    "⚡ ᴅʀᴏᴘ ʏᴏᴜʀ ʟɪɴᴋ ᴀɴᴅ ʟᴇᴛ'ꜱ ɢᴇᴛ ꜱᴛᴀʀᴛᴇᴅ! 🎯"
)

@X.on_message(F.command("batch"))
async def B(C_obj, m: M):
    U = m.from_user.id
    Z[U] = {"step": "start"}
    await m.reply_text("Send start link.")

@X.on_message(F.command("cancel"))
async def N(C_obj, m: M):
    U = m.from_user.id
    if U in W:
        W[U]["cancel"] = True
        await m.reply_text("Cancelling...")
    else:
        await m.reply_text("No active task.")

@X.on_message(F.text & ~F.command(["start", "batch", "cancel"]))
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
        await m.reply_text("Send destination chat ID.")
    elif current_step == "dest":
        d_chat = m.text
        Z[U].update({"step": "process", "did": d_chat})
        I, start_msg_id, N_val, link_type = Z[U]["cid"], Z[U]["sid"], Z[U]["num"], Z[U]["lt"]
        R_count = 0
        pt = await m.reply_text("""⏳✨ Pʀᴏᴄᴇssɪɴɢ ʏᴏᴜʀ ʀᴇǫᴜᴇsᴛ... 🔄🚀
🛠️ Pʟᴇᴀsᴇ ʜᴏʟᴅ ᴏɴ ᴘᴀᴛɪᴇɴᴛʟʏ, ʏᴏᴜʀ ғɪʟᴇ ɪs ʙᴇɪɴɢ ᴘʀᴏᴄᴇssᴇᴅ! 🎯💫""")
        for i in range(N_val):
            msg_id = start_msg_id + i
            msg_obj = await J(C_obj, Y, I, msg_id, link_type)
            if msg_obj:
                res = await V(C_obj, Y, msg_obj, d_chat, link_type, U)
                await pt.edit(f"{i+1}/{N_val}: {res}")
                if "Done" in res:
                    R_count += 1
            else:
                await m.reply_text(f"{msg_id} not found.")
            # Added delay to prevent flood wait error
            await asyncio.sleep(3)
        await m.reply_text(f"Batch Completed ✅")
        del Z[U]

print("Bot started successfully!!")
X.run()
