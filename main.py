from pipelines.data_loader import load_data
from pipelines.transcripts import transcribe_audio,load_model
from db.database import insert_row,get_rows_without_speaker,update_speaker
from db.init_db import initialise_db
import datetime
import librosa
from typing import Literal
from transformers import pipeline
import torch

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
             

def run_pipeline(data_source):
    initialise_db()
    model=load_model()
    audio_file_paths=load_data(data_source)
    run_transcription_pipeline(model,audio_file_paths)
    del(model)
    torch.mps.empty_cache()
    classifier=pipeline("zero-shot-classification",model="typeform/mobilebert-uncased-mnli",truncation=True,max_length=256)
    run_classifier_pipeline(classifier)
    



        
        

