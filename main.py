import requests
import telebot
from pydub import AudioSegment
import openai
import os
from flask import Flask, request

bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
openai_key = os.getenv("OPENAI_API_KEY")

# Initialize the bot
bot = telebot.TeleBot(bot_token)

# Create the Flask app
app = Flask(__name__)

# Define the route for the webhook
@app.route('/telegram-webhook', methods=['POST'])
def handle_webhook():
    print(request.get_json(force=True))
    update = telebot.types.Update.de_json(request.get_json(force=True))
    bot.process_new_updates([update])
    return 'OK'

# Split audio file into chunks
def split_audio(audio, max_duration_seconds):
    audio_length_ms = len(audio)
    max_duration_ms = max_duration_seconds * 1000  # convert to ms

    chunks = []

    for i in range(0, audio_length_ms, max_duration_ms):
        chunk = audio[i:i + max_duration_ms]
        chunks.append(chunk)

    return chunks

# Transcribe a chunk
def transcribe_chunk(chunk):
    chunk.export("temp_chunk.wav", format="wav")
    with open("temp_chunk.wav", "rb") as audio_file:
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
        return transcript["text"]

@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    # Get the voice message file
    file_info = bot.get_file(message.voice.file_id)
    file_url = f"https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}"

    # Download the file
    response = requests.get(file_url, stream=True)
    if response.status_code == 200:
        with open('voice_message.ogg', 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
    else:
        bot.send_message(message.chat.id, "Hm, I'll stay out of this one.")

    # Load the audio data with pydub
    audio = AudioSegment.from_ogg('voice_message.ogg')

    # Convert the audio to WAV format
    audio = audio.set_frame_rate(16000)  # Set the frame rate to 16kHz
    audio = audio.set_channels(1)  # Set the number of channels to 1 (mono)
    audio = audio.set_sample_width(2)  # Set the sample width to 2 bytes (16 bits)
    audio.export("output.wav", format="wav")

    # Send the audio file to Whisper API
    openai.api_key = openai_key
    audio_file = open("output.wav", 'rb')
    try:
        whisper_response = openai.Audio.transcribe("whisper-1", audio_file)
        print(whisper_response)
        # Extract the transcription from the response
        transcription = whisper_response["text"]
        # Send the transcription to the group
        bot.send_message(message.chat.id, transcription)
    except Exception as e:
        # If transcription fails, split the audio into chunks and transcribe each chunk
        chunks = split_audio(audio, 23)
        for chunk in chunks:
            try:
                text = transcribe_chunk(chunk)
                bot.send_message(message.chat.id, text)
            except Exception as e:
                bot.send_message(message.chat.id, f'Sorry, I was unable to transcribe a part of the voice message. Error: {str(e)}')

# Set the webhook URL
webhook_url = os.getenv('WEBAPP_URL') + '/telegram-webhook'
bot.remove_webhook()
bot.set_webhook(url=webhook_url)

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
