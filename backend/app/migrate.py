from sqlalchemy import text

from app.db import engine


def run_migrations():
    with engine.connect() as conn:
        feedings_cols = {row[1] for row in conn.execute(text("PRAGMA table_info(feedings)")).fetchall()}
        if "height_mm" not in feedings_cols:
            conn.execute(text("ALTER TABLE feedings ADD COLUMN height_mm INTEGER"))
        if "ambient_temp_f" not in feedings_cols:
            conn.execute(text("ALTER TABLE feedings ADD COLUMN ambient_temp_f INTEGER"))
        if "flour_type" not in feedings_cols:
            conn.execute(text("ALTER TABLE feedings ADD COLUMN flour_type TEXT"))
        if "flour_brand" not in feedings_cols:
            conn.execute(text("ALTER TABLE feedings ADD COLUMN flour_brand TEXT"))

        starters_cols = {row[1] for row in conn.execute(text("PRAGMA table_info(starters)")).fetchall()}
        if "feed_interval_hours" not in starters_cols:
            conn.execute(text("ALTER TABLE starters ADD COLUMN feed_interval_hours INTEGER"))
        if "archived" not in starters_cols:
            conn.execute(text("ALTER TABLE starters ADD COLUMN archived INTEGER NOT NULL DEFAULT 0"))

        bakes_cols = {row[1] for row in conn.execute(text("PRAGMA table_info(bakes)")).fetchall()}
        if "tags" not in bakes_cols:
            conn.execute(text("ALTER TABLE bakes ADD COLUMN tags TEXT"))

        conn.commit()
