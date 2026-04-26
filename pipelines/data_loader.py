from pathlib import Path
from typing import Iterator, Literal,Any
from datasets import load_dataset,Dataset
import zipfile,os
import soundfile as sf
import shutil




def _is_hf_dataset(source: str)-> bool:
    """ Returns True if the source is a HF Datatset. Logic is if it ends with .zip, then zip file
    else a HF dataset

    Args:
        source (str): Path of the Zip File or HF Dataset

    Returns:
        bool: True if HF Dataset else False
    """
    p=Path(source)
    return not(p.suffix==".zip")

def load_hf_dataset(dataset_id:str,temp_dir:Path,split="train") -> list:
    """Given a path to a HF dataset, loads it and returns list of file paths

    Args:
        dataset_id (str): Path to HF dataset
        temp_dir: path to where the audio files will be stored

    Returns:
        List: list having file paths of audios
    """
    ds=load_dataset(dataset_id,split=split,trust_remote_code=True)
    filepaths=[]
    for index,row in enumerate(ds):
        samples=row['audio'].get_all_samples()
        array = samples.data[0].numpy()
        sr = samples.sample_rate
        filename=temp_dir/f"HF_Audio_{index}.wav"
        sf.write(filename,array,sr)
        filepaths.append(Path(filename))
    return filepaths
    

def load_zip_file(zip_file_path:str,temp_dir:Path)-> list:
    """Given a file path to a zip file, extract audio and return a list
    having file paths

    Args:
        zip_file_path (str): Path to the zip file
        temp_dir: path to where the audio files will be stored

    Returns:
        Dataset: list of file paths
    """
    with zipfile.ZipFile(zip_file_path,'r') as z:
        z.extractall(temp_dir)
    audio_paths=[
        os.path.join(temp_dir,f)
        for f in os.listdir(temp_dir) if f.endswith(('.mp3','.wav','.m4a','.flac'))
    ]
    return sorted(audio_paths)




def load_data(source:str| Path)->list:
    '''
    Given a string, decides whether its a HF dataset or a file path to a zip file
    and then prepares a list containing file paths to audio for further processingl
    '''
    TEMP_DIR=Path(__file__).parent.parent/"Temp_Files"
    try:
        shutil.rmtree(TEMP_DIR)
    except FileNotFoundError:
        pass
    TEMP_DIR.mkdir(exist_ok=True)   
    if(_is_hf_dataset(source=source)): 
        return load_hf_dataset(source,temp_dir=TEMP_DIR)
    return load_zip_file(source,temp_dir=TEMP_DIR)

