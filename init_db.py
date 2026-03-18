import sqlalchemy
from sqlalchemy import create_engine, text

# Create engine (creates callcentre.db if it doesn't exist)
engine = create_engine('sqlite:///callcentre.db')

# Create table
with engine.connect() as conn:
    conn.execute(text('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pair_index INTEGER,
            timestamp DATETIME,
            agent_transcript TEXT,
            customer_transcript TEXT
        )
    '''))
    conn.commit()