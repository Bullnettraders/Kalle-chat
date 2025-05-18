import discord
import os
import requests
from openai import OpenAI

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = discord.Client(intents=intents)

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
WEB_SERVICE_URL = os.getenv("WEB_SERVICE_URL")

client_openai = OpenAI(api_key=OPENAI_API_KEY)
user_greeted = set()

@client.event
async def on_ready():
    print(f"✅ Bot ist online als {client.user}")
    channel = client.get_channel(CHANNEL_ID)
    if channel:
        await channel.send("👋 Hey! Ich bin **Kalle**, dein KI-Trading-Coach. Frag mich alles rund ums Trading!")

@client.event
async def on_message(message):
    if message.channel.id != CHANNEL_ID or message.author.bot:
        return

    user_input = message.content.strip()

    if message.author.id not in user_greeted:
        user_greeted.add(message.author.id)
        await message.channel.send(f"👋 Hey {message.author.mention}! Ich bin Kalle. Stell mir deine Trading-Frage!")

    if user_input.startswith("!") or user_input.startswith("/"):
        return

    try:
        response = client_openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Du bist Kalle, ein professioneller Trading-Coach. Antworte ehrlich. Wenn du etwas nicht weißt, gib es zu."
                },
                {"role": "user", "content": user_input}
            ]
        )
        reply = response.choices[0].message.content.strip()

        if "ich bin mir nicht sicher" in reply.lower() or len(reply) < 20:
            web_res = requests.post(f"{WEB_SERVICE_URL}/learn", json={"question": user_input})
            if web_res.status_code == 200:
                reply = web_res.json().get("answer", "Ich konnte dazu nichts finden.")

        await message.channel.send(f"📊 **Kalles Antwort**\n\n{reply}\n\n---\n💬 *Frag mich mehr, wenn du willst!*")

    except Exception as e:
        print("❌ Fehler:", e)
        await message.channel.send("⚠️ Upps. Etwas ist schiefgelaufen.")

client.run(DISCORD_TOKEN)
