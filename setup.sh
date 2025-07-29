#!/bin/bash

# Script para configurar o ambiente e instalar dependências.
# Usa 'set -e' para sair imediatamente se um comando falhar.
set -e

# Função para verificar e instalar dependências
setup_environment() {
    required_version=$(cat .python-version)
    current_version=$(python3 --version 2>&1 | awk '{split($2, a, "."); print a[1]"."a[2]}')
    IFS='.' read -r -a current <<< "$current_version"
    IFS='.' read -r -a required <<< "$required_version"
    if (( current[0] < required[0] )) || (( current[0] == required[0] && current[1] < required[1] )); then
        echo "Erro: Python \$required_version ou superior é necessário. Versão atual: \$current_version"
        exit 1
    fi

    echo "Verificando ambiente virtual..."
    if [ ! -d ".venv" ]; then
        echo "Ambiente virtual não encontrado. Criando..."
        python3 -m venv .venv
    fi

    # Detecta o sistema operacional e define o caminho para o Python no venv
    case "\$OSTYPE" in
      msys*|cygwin*)
        VENV_PYTHON=".venv/Scripts/python.exe"
        ;;
      *)
        VENV_PYTHON=".venv/bin/python"
        ;;
    esac

    echo "Garantindo que o pip esteja instalado e atualizado no ambiente virtual..."
    $VENV_PYTHON -m ensurepip --upgrade

    echo "Instalando/verificando dependências de requirements.txt..."
    $VENV_PYTHON -m pip install -r requirements.txt
    $VENV_PYTHON -m pip install pyyaml
}

# Executa a configuração
setup_environment

# Mensagem de sucesso e instruções
echo ""
echo "----------------------------------------------------"
echo "✅ Setup concluído com sucesso!"
echo "O ambiente está pronto para uso."
echo "----------------------------------------------------"

echo ""
echo "Para usar a ferramenta, primeiro ATIVE o ambiente virtual:"
echo ""
echo "  source .venv/bin/activate"
echo ""
echo "Depois, execute um dos comandos disponíveis. Por exemplo:"
echo ""
echo "  python3 main.py list"
echo ""
