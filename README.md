# 🚀 Sistema de Conciliação Financeira Turbo (WhatsApp + Nubank)

Este projeto automatiza a conferência de comprovantes enviados pelo WhatsApp com o extrato bancário do Nubank. Ele utiliza Inteligência Artificial (OCR) e aceleração por GPU para processar milhares de comprovantes em minutos.

## 🛠️ Funcionalidades
- **Leitura de WhatsApp**: Captura mensagens multilinhas, legendas de anexos e mídias.
- **OCR com GPU**: Extrai texto de imagens (JPG/PNG) e PDFs usando a placa de vídeo (NVIDIA).
- **Processador de Extrato**: Lê o PDF do Nubank e gera fórmulas de saldo dinâmicas no Excel.
- **Conciliação Inteligente**: Cruza valores e pinta de **VERDE** (OK) ou **VERMELHO** (Não encontrado), trazendo o contexto da conversa.

---

## 📱 1. Como Exportar a Conversa do WhatsApp
Para o script funcionar, você precisa do histórico de mensagens:
1. No celular, abra a conversa desejada.
2. Toque no nome do contato/grupo no topo.
3. Role até o fim e toque em **Exportar conversa**.
4. Selecione **ANEXAR MÍDIA** (obrigatório para ler os comprovantes).
5. Envie para você mesmo (e-mail ou drive) e baixe na pasta `dados/`.

---

## 📂 2. Estrutura de Pastas
Organize seus arquivos assim para o script rodar corretamente:
```text
projeto-financeiro/
├── Sistema_Financeiro_Turbo_GPU.py
├── pyproject.toml
├── dados/
│   ├── Conversa.txt (O histórico exportado)
│   ├── Extrato_Nubank.pdf (O PDF do banco)
│   └── midias/ (Coloque as fotos e PDFs aqui)
```

---

## 💻 3. Configuração do Ambiente (Usando UV)
Recomendamos o uso do **[uv](https://github.com)** para gerenciamento rápido de pacotes.

```bash
# 1. Criar ambiente isolado (Python 3.12)
uv venv --python 3.12

# 2. Ativar o ambiente
.venv\Scripts\activate

# 3. Instalar dependências com foco em GPU (NVIDIA CUDA 12.4)
uv pip install torch torchvision --index-url https://pytorch.org
uv pip install easyocr pymupdf pandas xlsxwriter tqdm openpyxl
```

---

## 🚀 4. Como Usar
No terminal, execute o script principal:
```bash
python Sistema_Financeiro_Turbo_GPU.py
```
Utilize o menu interativo:
- **Opção 1**: Processa as imagens e PDFs do WhatsApp.
- **Opção 2**: Processa o extrato do banco.
- **Opção 3**: Realiza o cruzamento final (Gera o arquivo `CONCILIACAO_FINAL_ESTRUTURADA.xlsx` na pasta `dados/resultados/`).

---

## 🛡️ Segurança e Privacidade
O arquivo `.gitignore` deste projeto está configurado para **NÃO** enviar sua pasta `dados/` para o GitHub. Seus comprovantes e extratos financeiros permanecem apenas no seu computador local.
