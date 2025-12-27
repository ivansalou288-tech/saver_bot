import sqlite3
from pathlib import Path

curent_path = Path(__file__).parent
messages_path = curent_path / 'databases' / 'messages.db'

connection = sqlite3.connect(messages_path)
cursor = connection.cursor()

# Создаем новую таблицу для истории балансов
cursor.execute('''
CREATE TABLE IF NOT EXISTS balance_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user INTEGER NOT NULL,
    balance INTEGER NOT NULL,
    games INTEGER NOT NULL,
    streak INTEGER,
    points INTEGER,
    message_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# Создаем индекс для быстрого поиска
cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_created ON balance_history(user, created_at DESC)')

# Переносим данные из старой таблицы (если есть)
try:
    cursor.execute('SELECT user, balance, games, streak, points, message_id FROM balanses')
    old_data = cursor.fetchall()
    for row in old_data:
        cursor.execute('''
            INSERT INTO balance_history (user, balance, games, streak, points, message_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', row)
except sqlite3.OperationalError:
    pass

connection.commit()
connection.close()

print("Миграция завершена успешно!")
