from tinydb import TinyDB, where
from BetterJSONStorage import BetterJSONStorage # Enhance storage ability
from pathlib import Path

# Handle reading, writing, and deleting data from a file-based database using TinyDB
class FileStorage:
    def __init__(self, file_name):
        """
        Initialize the file storage with the provided file path
        """
        self.path = Path(file_name)

    def get(self, id):
        """
        Fetch data from the database by user_id
        """
        with TinyDB(self.path, access_mode="r+", storage=BetterJSONStorage) as db:
            data = db.search(where('user_id') == id) # Search for records where 'user_id' matches the provided id
        return data

    def save(self, data):
        """
        Save new data into the database
        """
        with TinyDB(self.path, access_mode="r+", storage=BetterJSONStorage) as db:
            db.insert(data)

    def remove(self, id):
        """
        Remove data from the database by user_id
        """
        with TinyDB(self.path, access_mode="r+", storage=BetterJSONStorage) as db:
            db.remove(where('user_id') == id) # Remove all records where 'user_id' matches the provided id

# A wrapper around a specific storage implementation (in this case, FileStorage)
class Storage:
    def __init__(self, storage):
        self.storage = storage

    def get(self, id):
        return self.storage.get(id)

    def save(self, data):
        self.storage.save(data)

    def remove(self, id):
        self.storage.remove(id)