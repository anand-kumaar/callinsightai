from pipelines.data_loader import load_data
from pipelines.transcripts import transcribe_audio,load_model
from db.database import insert_row,get_rows_without_speaker,update_speaker,get_unanalysed_rows,insert_row_analysis,get_all_conversations,update_conversation_id
from db.init_db import initialise_db
from pipelines.analyser import analyse_transcript
import datetime
import librosa
from typing import Literal
from transformers import pipeline
import torch
import json

'''
Here we are going to update the entire database given the source dataset.
Do we need a function here as well??
Maybe. we will decide that later. Lets be done with the code first
'''

def identify_speaker(classifier:object,transcript:str)->Literal["Customer","Agent"]:
   result=classifier(transcript[:100],candidate_labels=[
    "call centre representative greeting and helping or selling",
    "customer calling with a problem or question"
])
   return result['labels'][0]   

def update_conversation_ids():
    rows = get_all_conversations()
    print(f"Found {len(rows)} rows in conversation table")
    conv_counter = 0
    i = 0
    while i < len(rows):
        if i + 1 < len(rows) and abs(rows[i].call_duration - rows[i+1].call_duration) < 0.3:
            update_conversation_id(rows[i].id, conv_counter)
            update_conversation_id(rows[i+1].id, conv_counter)
            conv_counter += 1
            i += 2
        else:
            update_conversation_id(rows[i].id, conv_counter)
            conv_counter += 1
            i += 1
               



def run_transcription_pipeline(model,audio_file_paths):
     for i,file in enumerate(audio_file_paths):
            model_output=transcribe_audio(model,file)
            duration=librosa.get_duration(path=file)
            insert_row(conversation_id=i,
                    timestamp=datetime.datetime.now(),
                    transcript=model_output['text'],
                    speaker="",
                    call_duration=duration)
                    
def run_classifier_pipeline(classifier):
     rows=get_rows_without_speaker()
     for row in rows:
          speaker_detail=identify_speaker(classifier,row.transcript)
          speaker ="agent" if speaker_detail=="call centre representative greeting and helping or selling" else "customer"
          update_speaker(id=row.id,speaker=speaker)
             
def run_analysis_pipeline():
     '''
     Fetches all rows from conversations that dont have an analysis yet and inserts them in 
     the analysis table
     '''
     rows=get_unanalysed_rows()
     print(f"Found {len(rows)} unanalysed rows ")
     for row in rows:
          print(f"Analysis Transcript id:{row.id}")
          result=analyse_transcript(row.transcript,row.speaker)
          
          print(result)
          if result:
               insert_row_analysis(
                    transcript_id=row.id,
                    speaker=row.speaker,
                    mood=result.get("mood"),
                    mood_score=result.get("mood_score"),
                    keywords=json.dumps(result.get("key_words"))
               )
               print(f"Done — mood: {result.get('mood')}, keywords: {result.get('key_words')}")
          else:
               print(f"Skipping row {row.id} due to API error.")

def run_pipeline(data_source):
    initialise_db()
    model=load_model()
    audio_file_paths=load_data(data_source)
    run_transcription_pipeline(model,audio_file_paths)
    del(model)
    torch.mps.empty_cache()
    classifier=pipeline("zero-shot-classification",model="typeform/mobilebert-uncased-mnli",truncation=True,max_length=256)
    run_classifier_pipeline(classifier)
    update_conversation_ids()
    run_analysis_pipeline()
    


if __name__ == "__main__":
    run_analysis_pipeline()
        
        

