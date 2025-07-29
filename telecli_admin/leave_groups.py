# leave_groups.py
from telethon.tl.functions.channels import LeaveChannelRequest
from telethon.tl.functions.messages import DeleteChatUserRequest, DeleteHistoryRequest
from prompt_toolkit import prompt
from tqdm import tqdm
from . import config

async def leave_groups(client, selections):
    ids = [int(x.strip()) for x in selections.split(',')]  # Supondo IDs ou números sequenciais mapeados para IDs
    confirm = prompt(f"Confirma saída de {len(ids)} grupos? (s/n): ").lower()
    if confirm != 's':
        return
    
    for group_id in tqdm(ids, desc="Saindo de grupos"):
        try:
            entity = await client.get_entity(group_id)
            if hasattr(entity, 'broadcast') and entity.broadcast:  # Canal
                await client(LeaveChannelRequest(entity))
            else:  # Grupo
                await client(DeleteChatUserRequest(chat_id=group_id, user_id='me'))
            # Bloquear (se aplicável): await client(BlockRequest(entity.id))
            await client(DeleteHistoryRequest(peer=entity, max_id=0, just_clear=True))
        except Exception as e:
            print(f"Erro ao sair de {group_id}: {e}")