# spam_detection.py
import re
import aiohttp
from rich.table import Table
from rich.console import Console
from . import config

async def detect_spam(client, group_id, use_api=False):
    entity = await client.get_entity(group_id)
    messages = await client.get_messages(entity, limit=50)
    spam_msgs = []
    
    # Heurísticas locais
    patterns = [re.compile(r'(spam|phishing|link suspeito)', re.I)]  # Adicionar regex/palavras-chave
    for msg in messages:
        if msg.message and (any(p.search(msg.message) for p in patterns) or len(set(msg.message)) < 10):  # Repetição
            spam_msgs.append({'id': msg.id, 'text': msg.message})
    
    # API externa se ativado
    if use_api and len(spam_msgs) > 0:
        async with aiohttp.ClientSession() as session:
            for msg in spam_msgs:
                if config.JAMAI_TOKEN_LIMIT > 0:
                    response = await session.post('https://jamai.api/detect', json={'text': msg['text'], 'key': config.JAMAI_API_KEY})
                    if response.status == 200:
                        data = await response.json()
                        msg['spam_score'] = data.get('score', 0)
                    config.JAMAI_TOKEN_LIMIT -= 1
                else:
                    print("Limite de tokens atingido.")
    
    # Exibir resultados
    console = Console()
    table = Table(title="Mensagens Suspeitas")
    table.add_column("ID")
    table.add_column("Texto")
    table.add_column("Score (se API)")
    for msg in spam_msgs:
        table.add_row(str(msg['id']), msg['text'], str(msg.get('spam_score', 'N/A')))
    console.print(table)