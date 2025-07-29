# export_media.py
from telethon.tl.functions.messages import GetHistoryRequest
import os
import asyncio
from tqdm import tqdm
from . import config

async def export_media(client, group_id, folder='downloads'):
    entity = await client.get_entity(group_id)
    os.makedirs(f"{folder}/{entity.title}", exist_ok=True)
    messages = await client(GetHistoryRequest(peer=entity, limit=100, offset_id=0, offset_date=None, add_offset=0, max_id=0, min_id=0, hash=0))
    
    for msg in tqdm(messages.messages, desc="Baixando mídias"):
        if msg.media:
            # Download com rate limit
            await asyncio.sleep(1 / config.RATE_LIMIT)
            path = await client.download_media(msg.media, file=f"{folder}/{entity.title}/{msg.id}")
            # Preservar legenda e hashtags
            if msg.message:
                with open(f"{path}.txt", 'w') as f:
                    f.write(msg.message)  # Inclui hashtags na legenda
        # Suporte a álbuns: msg.grouped_id para agrupar