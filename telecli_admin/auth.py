# auth.py
from telethon import TelegramClient
from telethon.sessions import StringSession
import os
from prompt_toolkit import prompt
from . import config

async def authenticate():
    if os.path.exists(config.SESSION_FILE):
        consent = prompt("Usar sessão existente? (s/n): ").lower()
        if consent == 's':
            return TelegramClient(StringSession(open(config.SESSION_FILE).read()), config.API_ID, config.API_HASH)
    
    client = TelegramClient(StringSession(), config.API_ID, config.API_HASH)
    await client.start(phone=lambda: prompt("Digite seu número de telefone: "))
    print("Login realizado com sucesso.")
    with open(config.SESSION_FILE, 'w') as f:
        f.write(client.session.save())
    return client