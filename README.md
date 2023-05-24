# CopilotBot

CopilotBot is an exploratory Telegram bot for Promptmaster Copilot. It's designed to interact with users on Telegram and provide responses using the OpenAI GPT-3 model.

## Getting Started

These instructions will guide you on how to deploy and run the bot on Heroku.

### Prerequisites

- Python 3.6 or higher
- A Telegram account
- A Heroku account

### Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/szabodav/copilotbot.git
    cd copilotbot
    ```

2. Install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

### Configuration

1. Create a new bot on Telegram:

    - Open the Telegram app and search for the "BotFather" bot.
    - Start a chat with BotFather and follow the instructions to create a new bot.
    - After creating the bot, BotFather will give you a token. This is your `TELEGRAM_BOT_TOKEN`.

2. Get your OpenAI API key:

    - Sign up for an account on the [OpenAI website](https://www.openai.com/).
    - Navigate to the API section to find your API key. This is your `OPENAI_API_KEY`.

3. Set up your Heroku app:

    - Create a new app on the [Heroku dashboard](https://dashboard.heroku.com/).
    - In the "Settings" tab, add the following config vars:
        - `TELEGRAM_BOT_TOKEN`: Your Telegram bot token.
        - `OPENAI_API_KEY`: Your OpenAI API key.
        - `WEBAPP_URL`: The URL of your Heroku app, followed by `/telegram-webhook`. For example, if your app is named `my-copilotbot`, the `WEBAPP_URL` would be `https://my-copilotbot.herokuapp.com/telegram-webhook`.

### Deployment

1. Deploy your app to Heroku:

    ```bash
    git push heroku main
    ```

2. Scale up your web dynos:

    - In the "Resources" tab of your Heroku dashboard, scale up your `web` dynos to 1.

Your bot should now be running on Heroku and responding to messages on Telegram.

## Usage

To use the bot, start a chat with it on Telegram or add it to a group. The bot will monitor the group chat and if someone sends a voice message it will automatically send back a transcript of the voice message using OpenAI's Whisper API.
It's pretty simple. :)

## Contributing

Contributions are welcome! Please feel free to submit a pull request.

## License

This project is open source and available under the [MIT License](https://opensource.org/licenses/MIT).
