#!/bin/bash
# ================================================================
# VF Veículos — Setup inicial do Droplet (Ubuntu 22.04)
# Execute como root: bash setup-servidor.sh
# ================================================================

set -e

echo ">>> Atualizando sistema..."
apt-get update && apt-get upgrade -y

echo ">>> Instalando Docker..."
curl -fsSL https://get.docker.com | sh
systemctl enable docker
systemctl start docker

echo ">>> Instalando Docker Compose plugin..."
apt-get install -y docker-compose-plugin

echo ">>> Configurando firewall..."
ufw allow 22/tcp    # SSH
ufw allow 8080/tcp  # Evolution API
ufw allow 5678/tcp  # N8N
ufw allow 8000/tcp  # OCR Service
ufw --force enable

echo ">>> Criando pasta do projeto..."
mkdir -p /opt/vf-automacao
cd /opt/vf-automacao

echo ""
echo "========================================"
echo "  Setup completo!"
echo "  Próximos passos:"
echo "  1. Copie os arquivos do projeto para /opt/vf-automacao/"
echo "  2. cp .env.example .env && nano .env"
echo "  3. docker compose up -d"
echo "========================================"
