from typing import Annotated, Literal
from pydantic import BaseModel, Field
from Secrets.keys import discord_id
from Secrets.keys import bot_token
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
class DiscordInput(BaseModel):
    recipient: Annotated[int, Field(description="The recipient.")]
    message: Annotated[int, Field(description="The content of the message.")]
def discord_messenger(input: Annotated[DiscordInput, "Input to the discord messenger."]) -> int:
    print(f'recipient: {input.recipient}')
    recipient={}
    recipient['discord_id'] = discord_id
    print(input.message)
    try:

        #recipient = {"discord_id": discord_id}
        print(f"recipient_id: {recipient['discord_id']}\n{input.message}")

        channel_id = get_dm_channel(recipient["discord_id"])  # (input("\nenter user id: "))

        response = send_message(channel_id, input.message)

        if response.status_code == 200 or response.status_code == 201:
            return f"Message:{input.message}\nMessage sent successfully"
        else:
            return f"Failed to send message, status code: {response.status_code}"
    except Exception as e:
        print(e)
        return "failed to send message"
