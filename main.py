from dotenv import load_dotenv
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent,
    TextMessage,
    TextSendMessage,
    AudioMessage,
    AudioSendMessage,
)
from src.audio import audio
from src.models import OpenAIModel
from src.speech import Speech
from src.storage import Storage, FileStorage
from src.profile import ProfileManager

import datetime
import math
import os
import uuid

load_dotenv()

app           = Flask(__name__, static_url_path="/audio", static_folder="files/")
model         = OpenAIModel(os.getenv("OPENAI_API_KEY"))
line_bot_api  = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler       = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))
speech        = Speech()

# TinyDB
log_storage    = Storage(FileStorage("tinydb/file.db"))
memory_storage = Storage(FileStorage("tinydb/reflect.db"))
profile_mgr    = ProfileManager("tinydb/profile.db")

# Config
CHAT_MODEL  = os.getenv("CHAT_COMPLETION_MODEL", "gpt-4o")
AUDIO_MODEL = os.getenv("AUDIO_MODEL_ENGINE",  "whisper-1")
SERVER_URL  = os.getenv("SERVER_URL")
MAX_TOKENS  = int(os.getenv("MAX_RESPONSE_TOKENS", 300))


def build_chat_messages(profile: dict, student_text: str, memories: list[str]) -> list[dict]:
    mem_prompt = f"This is a record of what you have done for the student in the past: {memories}" if memories else ""
    return [
        {
            "role": "system",
            "content": (
                "You are an American English teacher currently living in Taiwan, "
                "proficient in both English and Chinese. You know how to correct "
                "students' grammatical mistakes and guide them to improve their English proficiency.\n"
                f"Student profile -> Occupation: {profile.get('occupation','?')}, "
                f"Age: {profile.get('age','?')}, Need: {profile.get('need','?')}."
            ),
        },
        {
            "role": "user",
            f"content": f"{mem_prompt}\nStudent says: \"{student_text}\"\n\nAnswer in <={MAX_TOKENS} words.",
        },
    ]

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body      = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_text(event):
    text    = event.message.text.strip()
    user_id = event.source.user_id

    # 收集個人資料（未完成會自動回覆問題並 return）
    if not profile_mgr.ensure_profile(line_bot_api, event, text):
        return

    # 取最新 profile / memories
    profile  = profile_mgr.get(user_id) or {}
    memories = memory_storage.get(user_id)[-5:] if memory_storage.get(user_id) else []

    messages = build_chat_messages(profile, text, memories)
    _, reply = model.chat_completion(messages, CHAT_MODEL)

    log_storage.save(
        {
            "user_id": user_id,
            "log": f"student: {text} | teacher: {reply}",
            "created_at": datetime.datetime.now().isoformat(),
        }
    )
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))

@handler.add(MessageEvent, message=AudioMessage)
def handle_audio(event):
    user_id = event.source.user_id

    # 收集個人資料（未完成會提示用文字回答）
    if not profile_mgr.ensure_profile(line_bot_api, event):
        return

    # 1. 下載 & Whisper 轉錄
    in_path = f"{uuid.uuid4()}.m4a"
    content = line_bot_api.get_message_content(event.message.id)
    with open(in_path, "wb") as f:
        for chunk in content.iter_content():
            f.write(chunk)
    text = model.audio_transcriptions(in_path, AUDIO_MODEL)

    # 2. 每 10 則做教師反思
    history = log_storage.get(user_id)
    if history and len(history) % 10 == 0:
        hist10 = history[-10:]
        msgs = [
            {
                "role": "system",
                "content": "You are now an experienced English teacher who knows how to guide students, summarize and verify their learning situations, and set goals for them.",
            },
            {
                "role": "user",
                "content": (
                    f"Regarding the previous 10 conversations with the student: {hist10}\n"
                    "Please reflect on the following:\n"
                    "1. At which stage and level are the students' questions regarding learning English?\n"
                    "2. Are the answers given by the teacher really helpful to the student?\n"
                    "3. If you were the teacher, how would you modify your responses to better assist the student?"
                ),
            },
        ]
        _, reflection = model.chat_completion(msgs, CHAT_MODEL)
        memory_storage.save(
            {"user_id": user_id, "reflect": reflection, "created_at": datetime.datetime.now().isoformat()}
        )

    # 3. 產生教師回覆
    profile  = profile_mgr.get(user_id) or {}
    memories = memory_storage.get(user_id)[-5:] if memory_storage.get(user_id) else []
    messages = build_chat_messages(profile, text, memories)
    _, reply = model.chat_completion(messages, CHAT_MODEL)

    log_storage.save(
        {
            "user_id": user_id,
            "log": f"student: {text} | teacher: {reply}",
            "created_at": datetime.datetime.now().isoformat(),
        }
    )

    # 4. TTS & 傳送
    tmp_mp3 = f"{uuid.uuid4()}.mp3"
    speech.text_to_speech(reply, "en-US-Studio-O", "en-US", tmp_mp3)

    out_name = f"{uuid.uuid4()}.m4a"
    out_path = f"files/{out_name}"
    audio.convert_to_aac(tmp_mp3, out_path)
    duration = audio.get_audio_duration(tmp_mp3)
    audio_url = f"{SERVER_URL}/audio/{out_name}"

    for p in (in_path, tmp_mp3):
        if os.path.exists(p):
            os.remove(p)

    line_bot_api.reply_message(
        event.reply_token,
        [
            AudioSendMessage(original_content_url=audio_url, duration=math.ceil(duration * 1000)),
            TextSendMessage(text=reply),
        ],
    )

@app.route("/", methods=["GET"])
def home():
    return "Hello World!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
