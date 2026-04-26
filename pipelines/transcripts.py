import whisper
import torch
import librosa
from typing import Union

def load_model(model_size="base")->whisper.Whisper:
    '''
    Returns a Whisper model as per the model_size
    '''
    device="mps" if torch.backends.mps.is_available() else "cpu"
    model=whisper.load_model(model_size,device)
    return model

def transcribe_audio(model:whisper.Whisper,audio_sample:Union[str,object])->dict:
    '''
    Transcribes audio to text using Whisper Model
    Args:
    model(whisper.Whisper)-Any whisper Model
    audio_sample(str-Path of the Audio File or HF Audio decoder Object)

    Returns:
    dict : whisper output containing transcription and other data
    '''

    result=model.transcribe(audio=str(audio_sample),fp16=False)
    
    return result