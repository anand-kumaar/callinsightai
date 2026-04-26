from pipelines.data_loader import load_data
from pipelines.transcripts import transcribe_audio,load_model
from db.database import insert_row
from db.init_db import initialise_db
import datetime

'''
Here we are going to update the entire database given the source dataset.
Do we need a function here as well??
Maybe. we will decide that later. Lets be done with the code first
'''
def run_pipeline(data_source):
    #print(data_source)
    initialise_db()
    model=load_model()
    audio_file_paths=load_data(data_source)
    for i,file in enumerate(audio_file_paths):
            model_output=transcribe_audio(model,file)
            duration=model_output['segments'][-1]['end']/60
            insert_row(
                    conversation_id=i,
                    timestamp=datetime.datetime.now(),
                    transcript=model_output['text'],
                    speaker="",
                    call_duration=duration
            )
        
        

