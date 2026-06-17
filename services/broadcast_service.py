from db.database import get_cursor


def save_broadcast(media_type, file_id, caption=""):
    with get_cursor() as cur:
        cur.execute(
            "INSERT INTO broadcasts"
            " (media_type, file_id, caption)"
            " VALUES (?, ?, ?)",
            (media_type, file_id, caption),
        )


def get_broadcasts(limit=10):
    with get_cursor() as cur:
        cur.execute(
            "SELECT id, media_type, file_id, caption, sent_at"
            " FROM broadcasts ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        return cur.fetchall()
