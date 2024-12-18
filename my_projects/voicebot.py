import streamlit as st
from audio_recorder_streamlit import audio_recorder
from openai import OpenAI
import os
from dotenv import load_dotenv

MODEL = 'gpt-4o-mini'
AUDIO_LOCATION="audio_file.wav"
# a couple of test functions 
def streamlit_test():
    st.title("My Interactive App")

    # Add some widgets
    with st.form("my_form"):
        text_input = st.text_input("What's your name?")
        submit_button = st.form_submit_button("Submit")

def audio_record_test():
    audio_bytes = audio_recorder()
    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")
# end test functions  - this block can be deleted


def transcribe_text_to_voice(client, audio_location):
    audio_file=open(audio_location, "rb")
    transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
    return transcript.text

def chat_completion(client, user_prompt):
    system_prompt =  """
    You are a friendly and sometimes humorous assistant named Guido. 
    Whe you respond, you speak in a somewhat streotypical New Jersey 
    Italian accent like this: Whaddaya mean I gotta go to the meeting at 7? 
    Can’t I just stay home and watch da game? Eh, I got better things ta do, Paisano”
    """
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
      ])
    if response:
        return response.choices[0].message.content
    else:
        return "No response returned from OpenAI"

def text_to_speech_ai(client, speech_file_path, response):
    response = client.audio.speech.create(model="tts-1",voice="onyx",input=response)
    response.stream_to_file(speech_file_path)


load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    print("No API key was found")
client = OpenAI(api_key=api_key)

st.title("Guido, the Voice 💬 Chatbot")
"""
Hi. Just click on the microphone icon to allow me to use the microphone.
Then click microphone to record yourself to let me know how I can help you today.
"""

#audio recorder is the streamlit recorder component
audio_bytes = audio_recorder()
#if you get some audio
if audio_bytes:
    
    audio_location = AUDIO_LOCATION
    with open(audio_location, "wb") as f:
        f.write(audio_bytes)
    try:
        #transcribe audio file to text
        text=transcribe_text_to_voice(client, audio_location)
        #display teh input text
        st.write(f'You said: {text}')

         #Use API to get an AI response and display it
        response = chat_completion(client, text)
        st.write(f'Guido said: {response}')
        
        # Read out the text response using tts
        speech_file_path = 'audio_response.mp3'
        text_to_speech_ai(client, speech_file_path, response)
        #play the response
        st.audio(speech_file_path, autoplay=True)
    except:
        pass

   

    