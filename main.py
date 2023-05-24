import requests
import telebot
from pydub import AudioSegment
import io
import openai

bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
openai_key = os.getenv("OPENAI_API_KEY")

# Initialize the bot
bot = telebot.TeleBot('TELEGRAM_BOT_TOKEN')

# OpenAI API key
openai_key = 'OPENAI_API_KEY'

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


# Start the bot
bot.polling()
