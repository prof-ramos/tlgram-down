# main.py
import asyncio
import argparse
import json
import yaml
import csv
from rich.console import Console
from rich.table import Table
from prompt_toolkit import prompt
from telecli_admin.service import TelegramService
from telecli_admin.exceptions import *

console = Console()

# --- Funções de Apresentação ---

def display_groups_table(groups):
    table = Table(title="Lista de Grupos/Conversas")
    table.add_column("Nº", style="cyan")
    table.add_column("Nome", style="magenta")
    table.add_column("ID", style="green")
    for group in groups:
        table.add_row(str(group['num']), group['name'], str(group['id']))
    console.print(table)

def export_data(data, filename, format):
    try:
        if format == 'json':
            with open(filename, 'w') as f:
                json.dump(data, f, indent=4)
        elif format == 'yaml':
            with open(filename, 'w') as f:
                yaml.dump(data, f)
        elif format == 'csv':
            with open(filename, 'w', newline='') as f:
                if data:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
        console.print(f"[bold green]Dados exportados com sucesso para {filename}[/bold green]")
    except Exception as e:
        console.print(f"[bold red]Erro ao exportar dados: {e}[/bold red]")

# --- Lógica Principal ---

async def main():
    parser = argparse.ArgumentParser(description="Telegram CLI Admin Tool")
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Comandos...
    list_parser = subparsers.add_parser('list', help="Lista grupos e canais.")
    list_parser.add_argument('--export', choices=['json', 'yaml', 'csv'], help="Exporta a lista para um arquivo.")

    leave_parser = subparsers.add_parser('leave', help="Sai de grupos/canais em massa.")
    leave_parser.add_argument('--groups', required=True, help="IDs dos grupos para sair, separados por vírgula.")

    export_media_parser = subparsers.add_parser('export-media', help="Exporta mídias de um grupo.")
    export_media_parser.add_argument('--group', required=True, help="ID do grupo para exportar.")
    export_media_parser.add_argument('--folder', default='downloads', help="Pasta de destino.")

    args = parser.parse_args()

    service = TelegramService()
    try:
        await service.connect()

        if args.command == 'list':
            groups = await service.get_dialogs()
            display_groups_table(groups)
            if args.export:
                export_data(groups, f"groups.{args.export}", args.export)

        elif args.command == 'leave':
            group_ids = [g.strip() for g in args.groups.split(',')]
            try:
                # Validate group IDs
                invalid_ids = []
                for group_id in group_ids:
                    try:
                        int(group_id)
                    except ValueError:
                        invalid_ids.append(group_id)
                if invalid_ids:
                    console.print(f"[red]Erro: IDs de grupo inválidos: {', '.join(invalid_ids)}.[/red]")
                else:
                    if prompt(f"Confirma a saída de {len(group_ids)} grupos? (s/n): ").lower() == 's':
                        for group_id in group_ids:
                            try:
                                result = await service.leave_group(int(group_id))
                                console.print(f"[green]{result}[/green]")
                            except GroupNotFoundError as e:
                                console.print(f"[red]Erro: {e}[/red]")
                            except TelegramAdminError as e:
                                console.print(f"[red]Erro inesperado: {e}[/red]")
                    else:
                        console.print("[yellow]Operação cancelada.[/yellow]")
            except Exception as e:
                console.print(f"[bold red]Erro durante operação de saída: {e}[/bold red]")

        elif args.command == 'export-media':
            try:
                result = await service.export_media(int(args.group), args.folder)
                console.print(f"[green]{result}[/green]")
            except (GroupNotFoundError, MediaExportError) as e:
                console.print(f"[red]Erro: {e}[/red]")

    except AuthenticationError as e:
        console.print(f"[bold red]Erro de Autenticação: {e}[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Ocorreu um erro fatal: {e}[/bold red]")
    finally:
        if service.client.is_connected():
            await service.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
