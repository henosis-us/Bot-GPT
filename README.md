# Bot-GPT 

Bot-GPT is a Discord bot designed to interact with users through various commands, leveraging the OpenAI API and other services.

## Features

- **Text and File Responses**: The bot can send messages as text or as a file if the content is too long.
- **Command Handling**: Supports various commands for cool features
- **Image Generation**: Uses DALL-E 3 model to generate images based on prompts.
- **Transcript Fetching**: Can retrieve transcripts of YouTube videos.
- **Token Counting**: Provides an estimate of the number of tokens in a given text.
- **Internet Query**: Can fetch internet data if the user query requires a search & can parse html
- **Thread Continuation**: Maintains conversation threads using OpenAI's thread IDs through replies.

## How to Setup

1. **Clone the Repository**: Obtain the code by cloning the repository to your local machine.
git clone https://github.com/henosis-us/Bot-GPT.git

2. **Install Dependencies**: Install the required Python packages listed in `requirements.txt` using the command:
bash
pip install -r requirements.txt
if running locally I recommend venv
3. **Environment Variables**: Set up the necessary environment variables for `DISCORD_TOKEN`, `OPENAI_API_KEY`, and `PPLX_API_KEY`. These can be placed in a `.env` file or set in your environment.

4. **Docker (Optional)**: If using Docker, build the Docker image using the provided `Dockerfile` and run the container with `docker-compose up`.

5. **Run the Bot**: Start the bot by running `main.py`:
bash
python main.py

6. **Invite the Bot**: Create an invite link for your bot and add it to your Discord server.

Make sure to follow the Discord developer documentation to set up a bot account and retrieve your `DISCORD_TOKEN`.
7. **Configure Permissions**: Ensure that the bot has the necessary permissions on your Discord server to read messages, send messages, manage messages, and any other permissions required for its features.

8. **Start Interacting**: Once the bot is running and invited to your server, you can start interacting with it using the supported commands.

For detailed command usage and additional configuration options, !help
