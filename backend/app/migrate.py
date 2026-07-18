from sqlalchemy import text

from app.db import engine


def run_migrations():
    with engine.connect() as conn:
        feedings_cols = {row[1] for row in conn.execute(text("PRAGMA table_info(feedings)")).fetchall()}
        if "height_mm" not in feedings_cols:
            conn.execute(text("ALTER TABLE feedings ADD COLUMN height_mm INTEGER"))

        starters_cols = {row[1] for row in conn.execute(text("PRAGMA table_info(starters)")).fetchall()}
        if "feed_interval_hours" not in starters_cols:
            conn.execute(text("ALTER TABLE starters ADD COLUMN feed_interval_hours INTEGER"))

        conn.commit()
