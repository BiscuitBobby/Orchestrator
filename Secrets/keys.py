import dotenv
import os

dotenv.load_dotenv()

bot_token = os.environ['DISCORD_KEY']
google_api = os.environ['GOOGLE_API_KEY']
wolfram_app_id = os.environ['WOLFRAM_ID']
discord_id = os.environ['DISCORD_ID']
llama_path = os.environ['LLAMA_PATH']
