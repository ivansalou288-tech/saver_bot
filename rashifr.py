import sqlite3
from pathlib import Path


curent_path = (Path(__file__)).parent
messages_path = curent_path / 'databases' / 'messages.db'
def rashifr():
        connection = sqlite3.connect(messages_path)
        cursor = connection.cursor()


        cursor.execute("""
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT,
                photo TEXT,
                video TEXT,
                voice TEXT,
                audio TEXT,
                document TEXT,
                video_note TEXT
            )
        """)
        
        result = cursor.execute(
            "SELECT text, photo, video, voice, audio, document, video_note FROM messages WHERE conn = ? AND chat = ?", 
            ('-9BEiuFjWEqYEwAAZ3Qu8vKWCho', 5400863080)
        ).fetchall()
        
        
        if result:
            for i in result:
                cursor.execute(
                    "INSERT INTO results (text, photo, video, voice, audio, document, video_note) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    i
                )
                connection.commit()
        
        connection.close()
        print('ok')

rashifr()