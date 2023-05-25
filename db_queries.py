import aiosqlite
import sqlite3

DB_NAME = "user.db"
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

async def get_photo_and_caption():
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT file_path, caption FROM photos ORDER BY RANDOM() LIMIT 1")
        row = await cursor.fetchone()
        await cursor.close()
        if row:
            file_path, caption = row
            return file_path, caption
        else:
            return None, None


def insert_photo(user_id, file_path, caption):
    cursor.execute('INSERT INTO photos (user_id, file_path, caption) VALUES (?, ?, ?)', (user_id, file_path, caption))
    conn.commit()

def fetch_photos_by_user_id(user_id):
    cursor.execute('SELECT file_path, caption FROM photos WHERE user_id = ?', (user_id,))
    results = cursor.fetchall()
    return results