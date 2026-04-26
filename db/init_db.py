import sqlalchemy
from sqlalchemy import create_engine, text
from pathlib import Path

def initialise_db():
    BASE_DIR = Path(__file__).parent.parent
    db_path = BASE_DIR / "callcentre.db"

    engine = create_engine(f'sqlite:///{db_path}')

    # Create table
    with engine.connect() as conn:
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER,
                timestamp DATETIME,
                transcript TEXT,
                speaker TEXT,        
                call_duration REAL           
            )
        '''))
        conn.commit()
    