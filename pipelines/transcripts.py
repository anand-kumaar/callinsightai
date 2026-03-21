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

def transcribe_audio(model:whisper.Whisper,audio_sample:Union[str,object])->str:
    '''
    Transcribes audio to text using Whisper Model
    Args:
    model(whisper.Whisper)-Any whisper Model
    audio_sample(str-Path of the Audio File or HF Audio decoder Object)

    Returns:
    String : Transcription Only
    '''
    if isinstance(audio_sample,str):
        result=model.transcribe(audio=audio_sample,fp16=False)
    else:
        audio_file=audio_sample.get_all_samples()
        audio_array,original_sr = audio_file.data[0].numpy(),audio_file.sample_rate
        audio_resampled = librosa.resample(audio_array, orig_sr=original_sr, target_sr=16000)
        result = model.transcribe(audio_resampled, fp16=False)
    
    return result['text']