# forward_content.py
from telethon.tl.functions.messages import GetHistoryRequest, ForwardMessagesRequest
from tqdm import tqdm
from . import config

async def forward_content(client, source_id, dest_id):
    source = await client.get_entity(source_id)
    dest = await client.get_entity(dest_id)
    messages = await client(GetHistoryRequest(peer=source, limit=100, offset_date=None, offset_id=0, max_id=0, min_id=0, add_offset=0, hash=0))  # Pegar histórico
    
    # Ordenar por data (cronológica reversa para forwarding)
    messages.messages.sort(key=lambda m: m.date)
    
    for msg in tqdm(messages.messages, desc="Encaminhando"):
        await client(ForwardMessagesRequest(from_peer=source, id=[msg.id], to_peer=dest))
        # Preserva texto, mídias, legendas