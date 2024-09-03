from Secrets.keys import discord_id
from Secrets.keys import bot_token
from langchain.tools import BaseTool
import requests

def get_dm_channel(user_id):
    url = 'https://discord.com/api/v9/users/@me/channels'
    headers = {
        'Authorization': f'Bot {bot_token}',
        'Content-Type': 'application/json',
    }
    payload = {
        'recipient_id': user_id
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        # Successfully retrieved the DM channel
        return response.json()['id']
    else:
        # Handle errors
        print(f"Error getting DM channel: {response.status_code}")
        print(response.json())
        return None


def send_message(channel_id, message):
    url = f'https://discord.com/api/v9/channels/{channel_id}/messages'
    headers = {
        'Authorization': f'Bot {bot_token}',
        'Content-Type': 'application/json',
    }
    payload = {
        'content': message
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        # Message sent successfully
        print("Message sent successfully.")
    else:
        # Handle errors
        print(f"Error sending message: {response.status_code}")
        print(response.json())
    return response


# -------------------------------------------------------------------------------------------------------------------

class DiscordBot(BaseTool):
    name = "discord_message"
    description = "Useful to send me a message via Discord. Tool input should be message to be sent"

    def __init__(self, bot_token: str):
        bot_token = bot_token
        object.__setattr__(self, "bot_token", bot_token)
        super().__init__()

    def _run(self, tool_input: str, **kwargs) -> str:
        """Send a message to a Discord channel."""
        message = tool_input
        print(message)
        try:
            recipient = {"discord_id": discord_id}

            print(f"recipient_id: {recipient['discord_id']}\n{message}")

            channel_id = get_dm_channel(recipient["discord_id"])

            response = send_message(channel_id, message)

            if response.status_code == 200 or response.status_code == 201:
                return (f'\nObservation: The following text has been sent through discord successfully: "{message}"\n'
                        f"you can stop now")
            else:
                return f"Failed to send message, status code: {response.status_code}"
        except Exception as e:
            print(e)
            return "failed to send message"


discord_messaging = DiscordBot(bot_token)
