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
    update = telebot.types.Update.de_json(request.get_json(force=True), bot)
    bot.process_new_updates([update])
    return 'OK'

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
        bot.send_message(message.chat.id, 'Another voice message? Ugh, alright, give me a second.')
    else:
        bot.send_message(message.chat.id, "I can't even deal with you now.")

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
        whisper_response = openai.Audio.translate("whisper-1", audio_file)
        print(whisper_response)
        # Extract the transcription from the response
        translation = whisper_response["text"]
        # Send the transcription to the group
        bot.send_message(message.chat.id, translation)
    except Exception as e:
        bot.send_message(message.chat.id, f'Sorry, I was unable to transcribe the voice message. Error: {str(e)}')
        bot.send_message(message.chat.id, f'Whisper API response: {whisper_response}')


# Set the webhook URL
webhook_url = os.getenv('WEBAPP_URL') + '/telegram-webhook'
bot.remove_webhook()
bot.set_webhook(url=webhook_url)

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
