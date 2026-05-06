from google import genai
from dotenv import load_dotenv
import os
import json
from db.database import get_unanalysed_rows
import time

load_dotenv()
client=genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
#genai.configure(api_key=os.getenv("GEMINI_KEY"))
#model=genai.GenerativeModel("gemini-2.5-flash")


def analyse_transcript(transcript:str,speaker:str)->dict:
    """Calls Gemini API with and returns the mood along with score and keywords

    Args:
        transcript (str): Transcription of the call recording
        speaker (str): Customer or Agent

    Returns:
        dict: Return a dictionary with keys mood, mood_score and keywords
    """

    prompt=f"""
            Analyse the following {speaker} transcript from a call centre conversation.
            Return a JSON object with exactly this fields:
            -"mood":one of [frustrated,anxious,confused,calm,angry,inquisitive]
            -"mood_score"- rate your confidence in predicting the mood from 0 to 1
            -"key_words"- list of 6 keywords categorising the conversation
            Return Only a Valid JSON. No explanations,no markdowns no formatting

            {transcript}
            """
    try:
        response = client.models.generate_content(model="gemma-4-31b-it", contents=prompt)
        result=json.loads(response.text)
        time.sleep(15)
        return result
    except Exception as e:
        print(f"Error analysing transcript :{e}")
        return None


