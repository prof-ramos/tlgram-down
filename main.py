# main.py
import asyncio
import argparse
from telecli_admin.auth import authenticate
from telecli_admin.list_groups import list_dialogs, export_groups_details
from telecli_admin.leave_groups import leave_groups
from telecli_admin.export_media import export_media
from telecli_admin.spam_detection import detect_spam
from telecli_admin.forward_content import forward_content

async def main():
    parser = argparse.ArgumentParser(description="Telegram CLI Admin Tool")
    subparsers = parser.add_subparsers(dest='command')
    
    # Comando: list
    list_parser = subparsers.add_parser('list')
    list_parser.add_argument('--export', choices=['json', 'yaml', 'csv'])
    
    # Comando: export-groups
    export_parser = subparsers.add_parser('export-groups')
    export_parser.add_argument('--file', default='groups_details.json')
    
    # Comando: leave
    leave_parser = subparsers.add_parser('leave')
    leave_parser.add_argument('--groups', required=True)  # ex: 1,2,3

    # Comando: export-media
    export_media_parser = subparsers.add_parser('export-media')
    export_media_parser.add_argument('--group', required=True)
    export_media_parser.add_argument('--folder', default='downloads')

    # Comando: detect-spam
    detect_spam_parser = subparsers.add_parser('detect-spam')
    detect_spam_parser.add_argument('--group', required=True)
    detect_spam_parser.add_argument('--use-api', action='store_true')

    # Comando: forward
    forward_parser = subparsers.add_parser('forward')
    forward_parser.add_argument('--source', required=True)
    forward_parser.add_argument('--dest', required=True)
    
    args = parser.parse_args()
    client = await authenticate()
    async with client:
        if args.command == 'list':
            await list_dialogs(client, args.export)
        elif args.command == 'export-groups':
            await export_groups_details(client, args.file)
        elif args.command == 'leave':
            await leave_groups(client, args.groups)
        elif args.command == 'export-media':
            await export_media(client, args.group, args.folder)
        elif args.command == 'detect-spam':
            await detect_spam(client, args.group, args.use_api)
        elif args.command == 'forward':
            await forward_content(client, args.source, args.dest)

if __name__ == '__main__':
    asyncio.run(main())