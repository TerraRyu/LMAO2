import sqlite3
import json
from typing import Any, Optional
import time

class Cache:
    def __init__(self, db_name: str = 'cache.db', expiration: int = 3600):
        self.conn = sqlite3.connect(db_name)
        self.expiration = expiration
        self._create_table()

    def _create_table(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    timestamp INTEGER
                )
            ''')

    def get(self, key: str) -> Optional[Any]:
        with self.conn:
            cursor = self.conn.execute('SELECT value, timestamp FROM cache WHERE key = ?', (key,))
            row = cursor.fetchone()
            if row:
                value, timestamp = row
                if time.time() - timestamp <= self.expiration:
                    return json.loads(value)
        return None

    def set(self, key: str, value: Any):
        serialized_value = json.dumps(value)
        timestamp = int(time.time())
        with self.conn:
            self.conn.execute('INSERT OR REPLACE INTO cache (key, value, timestamp) VALUES (?, ?, ?)',
                              (key, serialized_value, timestamp))

    def clear(self):
        with self.conn:
            self.conn.execute('DELETE FROM cache')

    def __del__(self):
        self.conn.close()

# Usage example:
if __name__ == "__main__":
    cache = Cache()
    
    # Set a value
    cache.set("example_key", {"data": "example_value"})
    
    # Get the value
    result = cache.get("example_key")
    print(result)  # Output: {'data': 'example_value'}
    
    # Try to get a non-existent key
    result = cache.get("non_existent_key")
    print(result)  # Output: None