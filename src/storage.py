from __future__ import annotations

import json
from pathlib import Path
from tinydb import TinyDB, where
from tinydb.storages import JSONStorage

class UTF8JSONStorage(JSONStorage):
    """TinyDB JSONStorage 但 _dump() 強制 ensure_ascii=False"""

    def _dump(self, obj: dict) -> str:  # type: ignore[override]
        return json.dumps(
            obj,
            indent=4,
            sort_keys=False,
            ensure_ascii=False, 
        )
    
class FileStorage:

    def __init__(self, file_name: str | Path):
        self.path = Path(file_name)
        # 確保目錄存在，避免 FileNotFoundError
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def get(self, user_id: str):
        with TinyDB(self.path, access_mode="r+", storage=UTF8JSONStorage) as db:
            return db.search(where("user_id") == user_id)

    def save(self, data: dict):
        with TinyDB(self.path, access_mode="r+", storage=UTF8JSONStorage) as db:
            db.insert(data)

    def remove(self, user_id: str):
        with TinyDB(self.path, access_mode="r+", storage=UTF8JSONStorage) as db:
            db.remove(where("user_id") == user_id)

class Storage:
    def __init__(self, storage: FileStorage):
        self.storage = storage

    def get(self, user_id: str):
        return self.storage.get(user_id)

    def save(self, data: dict):
        self.storage.save(data)

    def remove(self, user_id: str):
        self.storage.remove(user_id)
