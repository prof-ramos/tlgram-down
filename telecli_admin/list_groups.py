# list_groups.py
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
from rich.console import Console
from rich.table import Table
import json
import yaml
import csv
from . import config

async def list_dialogs(client, export_format=None):
    dialogs = await client(GetDialogsRequest(offset_date=None, offset_id=0, offset_peer=InputPeerEmpty(), limit=100, hash=0))
    groups = []
    console = Console()
    table = Table(title="Lista de Grupos/Conversas")
    table.add_column("Nº", style="cyan")
    table.add_column("Nome", style="magenta")
    table.add_column("ID", style="green")
    
    for i, dialog in enumerate(dialogs.chats, 1):
        if hasattr(dialog, 'title'):  # Grupos/canais
            groups.append({'num': i, 'name': dialog.title, 'id': dialog.id})
            table.add_row(str(i), dialog.title, str(dialog.id))
    
    console.print(table)
    
    if export_format in config.EXPORT_FORMATS:
        filename = f"groups.{export_format}"
        if export_format == 'json':
            with open(filename, 'w') as f:
                json.dump(groups, f, indent=4)
        elif export_format == 'yaml':
            with open(filename, 'w') as f:
                yaml.dump(groups, f)
        elif export_format == 'csv':
            with open(filename, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['num', 'name', 'id'])
                writer.writeheader()
                writer.writerows(groups)
        print(f"Exportado para {filename}")

async def export_groups_details(client, filename='groups_details.json'):
    # Similar à list_dialogs, mas inclui tipo, membros, data de criação
    dialogs = await client(GetDialogsRequest(offset_date=None, offset_id=0, offset_peer=InputPeerEmpty(), limit=100, hash=0))  # Mesma chamada
    details = []
    for dialog in dialogs.chats:
        if hasattr(dialog, 'title'):
            entity = await client.get_entity(dialog.id)
            details.append({
                'name': dialog.title,
                'id': dialog.id,
                'type': 'group' if entity.megagroup else 'channel' if entity.broadcast else 'private',
                'members': entity.participants_count if hasattr(entity, 'participants_count') else 0,
                'created_at': dialog.date.isoformat() if hasattr(dialog, 'date') else 'N/A'
            })
    with open(filename, 'w') as f:
        json.dump(details, f, indent=4)