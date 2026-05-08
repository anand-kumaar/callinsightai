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
    
def update_speaker(id: int, speaker: str):
   try:
    with engine.connect() as conn:
            conn.execute(text('''
                UPDATE conversations 
                SET speaker = :speaker 
                WHERE id = :id
            '''), {'speaker': speaker, 'id': id})
            conn.commit()
            return True
   except Exception as e:
       print(f"Error Updating Speaker:{e}")
       return False


def get_rows_without_speaker():
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text('SELECT id, transcript FROM conversations WHERE speaker = ""'))
            return result.fetchall()
    except Exception as e:
        print(f"error fetching rows : {e}")
        return False

def get_all_conversations():
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text('SELECT * FROM conversations '))
            return result.fetchall()
    except Exception as e:
        print(f"error fetching rows : {e}")
        return False

def insert_row_analysis(transcript_id:int,speaker:str,mood:str,mood_score:float,keywords:str):
    '''
    Inserts a row in the database table analysis
    Args:
    id: Primary Key for identifying rows in the table
    transcript_id(int): Column ID from the transcript table
    speaker: Column Speaker from the transcript table
    mood: Mood of the speaker based upon analysis by a NLP Model
    mood_score: Score assigned to the analysed mood
    keywords: keywords associated with the transcript
    '''
    try:
        with engine.connect() as conn:
            conn.execute(text('''
                INSERT INTO analysis (transcript_id,speaker,mood,mood_score,keywords)
                VALUES (:transcript_id,:speaker,:mood,:mood_score,:keywords)
            '''), {
                'transcript_id': transcript_id,
                'speaker': speaker,
                'mood': mood,
                'mood_score':mood_score,
                'keywords':keywords
            })
            conn.commit()
            return True
    except Exception as e:
        print(f"Error Inserting Row :{e}")
        return False

def get_unanalysed_rows():
    try:
        with engine.connect() as conn:
            result = conn.execute(text('''
                SELECT c.id, c.transcript, c.speaker 
                FROM conversations c
                LEFT JOIN analysis a ON a.transcript_id = c.id
                WHERE a.transcript_id IS NULL
            '''))
            return result.fetchall()
    except Exception as e:
        print(f"Error fetching unanalysed rows: {e}")
        return False
    
def get_conversation_stats():
    with engine.connect() as conn:
        result=conn.execute(text('''
            SELECT COUNT(*) as total_calls,AVG(call_duration) as avg_duration
                                 FROM conversations'''))
        return result.fetchone()


def get_analysis_stats():
    with engine.connect() as conn:
        mood_result=conn.execute(text('''
                SELECT mood,COUNT(*) as mood_count,AVG(mood_score) as avg_score
                                 FROM analysis
                                 GROUP BY mood
                                 ORDER BY mood_count DESC'''))
        keyword_result=conn.execute(text('''
                SELECT keywords from ANALYSIS'''))
        return {'mood':mood_result.fetchall(),'keywords':keyword_result.fetchall()}
    

def update_conversation_id(id: int, conv_id: int):
    try:
        with engine.connect() as conn:
            conn.execute(text('''
                UPDATE conversations 
                SET conversation_id = :conv_id 
                WHERE id = :id
            '''), {'conv_id': conv_id, 'id': id})
            conn.commit()
            return True
    except Exception as e:
       print(f"Error Updating conversation_id:{e}")
       return False

def get_conversation_by_id(conv_id: int):
    try:
        with engine.connect() as conn:
            result = conn.execute(text('''
                SELECT c.transcript, c.speaker, c.conversation_id, a.mood, a.mood_score, a.keywords 
                FROM conversations c
                INNER JOIN analysis a ON a.transcript_id = c.id
                WHERE c.conversation_id = :conv_id
            '''), {'conv_id': conv_id})
            return result.fetchall()
    except Exception as e:
        print(f"Error fetching conversation_id:{conv_id}. {e}")
        return False

def get_distinct_conv_id():
    try:
        with engine.connect() as conn:
            result = conn.execute(text('''
                SELECT DISTINCT conversation_id from conversations'''))
            return result.fetchall()
    except Exception as e:
        print(f"Error fetching distinct conversation ids {e}")
        return False 
