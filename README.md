# Bot-GPT 

Bot-GPT is a Discord bot designed to interact with users through various commands, leveraging the OpenAI API and other services.

## Tools

- **Python**: The primary programming language used.
- **Discord.py**: A Python library for interacting with Discord.
- **OpenAI API**: Used for generating responses and images.
- **Docker**: For containerization and easy deployment.
- **Perplexity AI (PPLX API)**: An alternative language model API (online search).
- **YouTube Transcript API**: For fetching video transcripts.
- **BeautifulSoup4**: For parsing HTML content.
- **Aiohttp**: For making asynchronous HTTP requests.
- **TikToken**: For tokenizing strings according to model specifications.

## Features

- **Text and File Responses**: The bot can send messages as text or as a file if the content is too long.
- **Command Handling**: Supports various commands for cool features
- **Image Generation**: Uses DALL-E 3 model to generate images based on prompts.
- **Transcript Fetching**: Can retrieve transcripts of YouTube videos.
- **Token Counting**: Provides an estimate of the number of tokens in a given text.
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