from db.database import get_conn


def save_broadcast(media_type, file_id, caption=""):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO broadcasts (media_type, file_id, caption) VALUES (?, ?, ?)",
        (media_type, file_id, caption),
    )
    conn.commit()
    conn.close()


def get_broadcasts(limit=20):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, media_type, file_id, caption, sent_at FROM broadcasts ORDER BY sent_at DESC LIMIT ?",
        (limit,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows
