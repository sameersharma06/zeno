"""
Singleton database connection pool
"""
import sqlite3
import threading
from core.paths import get_data_dir

class DatabasePool:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._init_db()
        return cls._instance
    
    def _init_db(self):
        data_dir = get_data_dir()
        self.db_path = f"{data_dir}/zeno.db"
        
        # Create tables if not exist
        conn = self._get_connection()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                type TEXT NOT NULL,
                content TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL,
                deadline TEXT NOT NULL,
                done BOOLEAN DEFAULT 0
            )
        """)
        conn.commit()
        conn.close()
    
    def _get_connection(self):
        """Get a new connection (thread-safe)"""
        return sqlite3.connect(self.db_path, check_same_thread=False)
    
    def execute_query(self, query, params=()):
        """Safe execute with automatic connection management"""
        conn = self._get_connection()
        try:
            cursor = conn.execute(query, params)
            result = cursor.fetchall()
            conn.commit()
            return result
        finally:
            conn.close()

# Global instance
db_pool = DatabasePool()
