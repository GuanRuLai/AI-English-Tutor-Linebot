from __future__ import annotations

import datetime
from linebot.models import TextSendMessage

from src.storage import Storage, FileStorage


class ProfileManager:
    """收集並存取 occupation / age / need 三欄位"""

    def __init__(self, db_path: str = "tinydb/profile.db") -> None:
        self.storage = Storage(FileStorage(db_path))

    def _save(self, record: dict) -> None:
        """內部儲存：若 user_id 已存在則覆蓋"""
        self.storage.save(record)

    def get(self, user_id: str) -> dict | None:
        """取得最新 profile"""
        data = self.storage.get(user_id)
        return data[-1] if data else None

    def _update_step(
        self, user_id: str, field: str, value: str, next_state: str | None
    ) -> None:
        profile = self.get(user_id) or {"state": "ask_occupation"}

        # 取出文件後先複製成一般 dict，並移除 doc_id 以免重複
        raw = self.get(user_id) or {}
        profile = dict(raw)             # 解除 TinyDB Document
        profile.pop("doc_id", None)     # 移除內建欄位
        if not profile:
            profile["state"] = "ask_occupation"

        profile[field] = value
        profile["state"] = next_state
        if next_state is None:  # 完成最後一步
            profile["completed"] = True
            profile["updated_at"] = datetime.datetime.now().isoformat()
        profile["user_id"] = user_id
        self._save(profile)

    def ensure_profile(
        self, api, event, incoming_text: str | None = ""
    ) -> bool:
        """
        若尚未收集完三題，依序提問並回傳 False 
        都完成則回傳 True 讓主程式繼續。
        """
        user_id = event.source.user_id
        profile = self.get(user_id)

        # 首度互動
        if not profile:
            self._save({"user_id": user_id, "state": "ask_occupation"})
            api.reply_message(
                event.reply_token,
                TextSendMessage(
                    text="Hi! I'm your AI English tutor.\nFirst, may I know your **occupation**?"
                ),
            )
            return False

        # 尚未完成
        if not profile.get("completed"):
            st = profile["state"]
            if st == "ask_occupation":
                self._update_step(user_id, "occupation", incoming_text, "ask_age")
                api.reply_message(
                    event.reply_token, TextSendMessage(text="Great, thanks! How old are you?")
                )
                return False

            if st == "ask_age":
                self._update_step(user_id, "age", incoming_text, "ask_need")
                api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="Got it. Finally, what's your main reason or goal for learning English?"),
                )
                return False

            if st == "ask_need":
                self._update_step(user_id, "need", incoming_text, None)
                api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="All set! Feel free to send me a voice or text question any time ✨"),
                )
                return False

        # 已完成
        return True