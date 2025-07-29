# telecli_admin/service.py
import os
import asyncio
import json
import yaml
import csv
from telethon import TelegramClient

from telethon.tl.functions.messages import GetDialogsRequest, GetHistoryRequest, ForwardMessagesRequest
from telethon.tl.functions.channels import LeaveChannelRequest
from telethon.tl.functions.messages import DeleteChatUserRequest, DeleteHistoryRequest
from telethon.tl.types import InputPeerEmpty
from tqdm import tqdm
from . import config
from .exceptions import *

class TelegramService:
    def __init__(self, session_file=config.SESSION_FILE):
        # Passar o nome do arquivo de sessão diretamente para o cliente
        # O Telethon gerenciará o carregamento e salvamento automaticamente.
        self.client = TelegramClient(session_file, config.API_ID, config.API_HASH)
        print("Serviço inicializado. Tentando conectar...")

    async def connect(self):
        try:
            await self.client.connect()
            if not await self.client.is_user_authorized():
                print("Sessão não encontrada ou inválida. Iniciando login com QR code...")
                await self.client.qr_login()
                print("Login via QR code bem-sucedido! Sessão salva.")
            else:
                print("Conectado com sucesso usando a sessão existente.")
        except Exception as e:
            # Captura erros de credenciais inválidas (API_ID/HASH)
            if 'API_ID' in str(e) or 'API_HASH' in str(e):
                raise AuthenticationError("API_ID ou API_HASH inválido. Verifique o arquivo config.py")
            raise AuthenticationError(f"Falha na conexão/autenticação: {e}")

    async def get_dialogs(self, limit=100):
        dialogs = await self.client(GetDialogsRequest(offset_date=None, offset_id=0, offset_peer=InputPeerEmpty(), limit=limit, hash=0))
        groups = []
        for i, dialog in enumerate(dialogs.chats, 1):
            if hasattr(dialog, 'title'):
                groups.append({'num': i, 'name': dialog.title, 'id': dialog.id})
        return groups

    async def get_group_details(self, group_id):
        try:
            entity = await self.client.get_entity(group_id)
            return {
                'name': entity.title,
                'id': entity.id,
                'type': 'group' if entity.megagroup else 'channel' if entity.broadcast else 'private',
                'members': entity.participants_count if hasattr(entity, 'participants_count') else 0,
                'created_at': entity.date.isoformat() if hasattr(entity, 'date') else 'N/A'
            }
        except ValueError:
            raise GroupNotFoundError(f"Grupo com ID '{group_id}' não encontrado.")

    async def leave_group(self, group_id):
        try:
            entity = await self.client.get_entity(group_id)
            if hasattr(entity, 'broadcast') and entity.broadcast:
                await self.client(LeaveChannelRequest(entity))
            else:
                await self.client(DeleteChatUserRequest(chat_id=group_id, user_id='me'))
            await self.client(DeleteHistoryRequest(peer=entity, max_id=0, just_clear=True))
            return f"Saída do grupo '{entity.title}' concluída."
        except ValueError:
            raise GroupNotFoundError(f"Grupo com ID '{group_id}' não encontrado.")
        except Exception as e:
            raise TelegramAdminError(f"Erro ao sair do grupo {group_id}: {e}")

    async def export_media(self, group_id, folder='downloads'):
        try:
            entity = await self.client.get_entity(group_id)
            download_folder = os.path.join(folder, str(entity.id))
            os.makedirs(download_folder, exist_ok=True)
            messages = await self.client(GetHistoryRequest(peer=entity, limit=100, offset_id=0, offset_date=None, add_offset=0, max_id=0, min_id=0, hash=0))

            for msg in tqdm(messages.messages, desc=f"Baixando mídias de {entity.title}"):
                if msg.media:
                    await asyncio.sleep(1 / config.RATE_LIMIT)
                    path = await self.client.download_media(msg.media, file=os.path.join(download_folder, str(msg.id)))
                    if not path:
                        continue
                    if msg.message:
                        try:
                            with open(f"{path}.txt", 'w') as f:
                                f.write(msg.message)
                        except IOError as e:
                            print(f"Erro ao escrever arquivo {path}.txt: {e}")
                            continue
            return f"Mídias de '{entity.title}' salvas em '{download_folder}'."
        except ValueError:
            raise GroupNotFoundError(f"Grupo com ID '{group_id}' não encontrado.")
        except Exception as e:
            raise MediaExportError(f"Erro ao exportar mídia: {e}")

    async def disconnect(self):
        await self.client.disconnect()
