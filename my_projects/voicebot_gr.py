import gradio as gr
from openai import OpenAI
import os
from dotenv import load_dotenv

MODEL = 'gpt-4o-mini'
AUDIO_LOCATION = "audio_file.wav"
SPEECH_FILE_PATH = 'audio_response.mp3'

def transcribe_text_to_voice(client, audio_location):
    audio_file = open(audio_location, "rb")
    transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
    return transcript.text

def chat_completion(client, user_prompt):
    system_prompt = """
    You are a friendly and sometimes humorous assistant named Guido.
    When you respond, you speak in a somewhat stereotypical New Jersey
    Italian accent like this: Whaddaya mean I gotta go to the meeting at 7?
    Can't I just stay home and watch da game? Eh, I got better things ta do, Paisano
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
    response = client.audio.speech.create(model="tts-1", voice="onyx", input=response)
    response.stream_to_file(speech_file_path)

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    print("No API key was found")
client = OpenAI(api_key=api_key)

def main():
    with gr.Blocks() as demo:
        gr.Markdown("# Guido, the Voice 💬 Chatbot")
        gr.Markdown("Hi. Click the microphone icon to record yourself and let me know how I can help you today.")
        with gr.Row():
            with gr.Column():
                audio = gr.Audio(sources=["microphone"], type="filepath")
                submit = gr.Button("Submit")
            with gr.Column():
                transcript = gr.Textbox(label="Transcript")
                output = gr.Textbox(label="Guido's Response")
                response_audio = gr.Audio(label="Guido's Response Audio", interactive=False)

        submit.click(
            fn=lambda audio_file: process_audio(client, audio_file),
            inputs=audio,
            outputs=[transcript, output, response_audio]
        )

    demo.launch()

def process_audio(client, audio_file):
    try:
        text = transcribe_text_to_voice(client, audio_file)
        response = chat_completion(client, text)
        text_to_speech_ai(client, SPEECH_FILE_PATH, response)
        return text, response, SPEECH_FILE_PATH
    except:
        return "An error occurred while processing the audio.", "An error occurred while processing the audio.", None

if __name__ == "__main__":
    main()

