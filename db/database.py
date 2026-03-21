import sqlalchemy
from sqlalchemy import create_engine, text
import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
db_path = BASE_DIR / "callcentre.db"
print(db_path)
engine = create_engine(f'sqlite:///{db_path}')

def insert_row(conversation_id:int,timestamp:datetime.datetime,transcript:str,speaker:str,call_duration:float):
    '''
    Inserts a row in the database table conversations
    Args:
    conversation_id(int): A conversation ID of which we are updating transcript
    timestamp(datetime.datetime): Time at which the conversation took place
    transcript(str): Transcript of the conversation
    speaker(str): speaker of the conversation
    call_duration(float):call duration in seconds

    '''
    try:
        with engine.connect() as conn:
            conn.execute(text('''
                INSERT INTO conversations (conversation_id, timestamp, transcript, speaker,call_duration)
                VALUES (:conversation_id, :timestamp, :transcript, :speaker,:call_duration)
            '''), {
                'conversation_id': conversation_id,
                'timestamp': timestamp,
                'transcript': transcript,
                'speaker': speaker,
                'call_duration': call_duration,
            })
            conn.commit()
            return True
    except Exception as e:
        print(f"Error Inserting Row :{e}")
        return False

