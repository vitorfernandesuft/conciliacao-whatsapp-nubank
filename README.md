Elaborado por: Vitor Fernandes de Oliveira Neto - CEO VF - Veiculos 
------------------------------
## 🚀 Sistema de Conciliação Financeira Turbo (WhatsApp + Nubank)
Este projeto automatiza a conferência de comprovantes enviados pelo WhatsApp com o extrato bancário do Nubank. Ele utiliza Inteligência Artificial (OCR) e aceleração por GPU para processar milhares de comprovantes em minutos, garantindo integridade total nos dados financeiros.
------------------------------
## 🧠 Regras de Negócio e Lógica de Conciliação
O sistema não realiza apenas um cruzamento simples de valores; ele segue regras rígidas para garantir a precisão:
## 1. Processamento de Mídias (Módulo WhatsApp)

* Triagem Inteligente: Processa apenas arquivos de imagem (.jpg, .png, .jpeg) e documentos .pdf. Vídeos e outros formatos são ignorados.
* Cache de OCR: Gera um arquivo .txt de "cache" para cada imagem. Se a imagem já foi processada, o script lê o cache em vez de realizar o OCR novamente, poupando GPU.
* Leitura Seletiva de PDFs: PDFs curtos (até 2 páginas) são lidos integralmente. PDFs longos têm apenas o cabeçalho extraído para evitar dados irrelevantes.
* Limpeza de Memória: Após o OCR, o script libera a VRAM da GPU e força o gc.collect() para manter a performance do sistema.

## 2. Processamento Bancário (Módulo Extrato)

* Independência de Nomes: Qualquer PDF na pasta Extrato_nubank/ é processado, independente do nome do arquivo.
* Fusão e Deduplicação: Consolida múltiplos arquivos de extrato. Transações idênticas presentes em mais de um arquivo são mantidas como uma única ocorrência.
* Busca Resiliente: Utiliza uma janela de busca de até 12 linhas abaixo do gatilho da transação para localizar valores em descrições muito longas.
* Ordenação Cronológica: Converte datas textuais (ex: "10 MAI 2026") em objetos de data reais para ordenação correta.

## 3. Inteligência de Conciliação (O Coração do Script)

* Prioridade do Extrato: O banco é a "âncora". O script percorre o extrato e busca evidências no WhatsApp. Comprovantes no WhatsApp sem correspondente no banco são ignorados.
* Causalidade Cronológica: Um gasto só é conciliado com comprovantes enviados na mesma data ou em data posterior à transação.
* Consumo Único (Fila): Evita que um único comprovante concilie múltiplas despesas de mesmo valor. O script "consome" as evidências na ordem em que aparecem no chat.
* Captura de Contexto: Extrai a conversa do chat (1 linha antes e 2 depois do arquivo) para identificar o autor e o assunto.

------------------------------
## 📂 Estrutura de Pastas

projeto-financeiro/
├── Sistema_Financeiro_Turbo_GPU.py
├── pyproject.toml
├── dados/
│   ├── Conversa.txt          # Histórico exportado do WhatsApp
│   ├── Extrato_nubank/       # Coloque seus PDFs de extrato aqui
│   ├── midias/               # Fotos e comprovantes em PDF do WhatsApp
│   └── resultados/           # Relatórios gerados automaticamente

------------------------------
## 📦 Bibliotecas Necessárias
Para instalar todas as dependências manualmente via `pip`, utilize o comando abaixo (mas prefira usar o UV, logo abaixo explico, ele ja instala tudo automaticamente):
```bash
pip install pandas pymupdf tqdm torch easyocr xlsxwriter openpyxl
```
*   **pandas**: Essencial para a manipulação de dados e tabelas.
*   **pymupdf (fitz)**: Utilizado para extrair texto de comprovantes em PDF.
*   **tqdm**: Adiciona as barras de progresso durante o processamento.
*   **torch & easyocr**: O "cérebro" do sistema para reconhecimento de texto em imagens (OCR).
*   **xlsxwriter & openpyxl**: Motores para leitura e gravação de arquivos Excel com formatação avançada.

------------------------------
## � Configuração do Ambiente (Usando UV)
Recomendamos o uso do uv para gerenciamento ultrarrápido.
### Roteiro de Instalação do Zero:

**1. Instale o UV (caso não tenha):**
No Windows (PowerShell):
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```
No Linux/Mac:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**2. Prepare o Projeto:**
Abra o terminal na pasta do projeto e execute:
```bash
# Inicializa o projeto e cria o ambiente virtual isolado
uv init

# Adiciona todas as dependências de uma vez
uv add pandas pymupdf tqdm torch easyocr xlsxwriter openpyxl
```

**3. Execute o Sistema:**
O UV garantirá que o Python correto e as versões exatas das bibliotecas sejam usadas:
```bash
uv run Sistema_Financeiro_Turbo_GPU.py
```

*Dica: O UV criará uma pasta `.venv`. Você não precisa se preocupar com ela, o comando `uv run` gerencia tudo automaticamente.*

------------------------------
## 📊 Output (Relatório Final)
A planilha CONCILIACAO_FINAL_ESTRUTURADA.xlsx apresenta:

* Sinalização Visual: Linhas em Verde (Conciliado) ou Vermelho (Não encontrado).
* Rastreabilidade: Dados do Banco, Hora da mensagem, Texto extraído do comprovante (OCR), nome do arquivo original e o contexto da conversa.

------------------------------
## 🛡️ Segurança e Privacidade
O arquivo .gitignore está configurado para NÃO enviar a pasta dados/ para o GitHub. Seus dados financeiros permanecem estritamente locais e privados.
------------------------------
Dica técnica: Se você possui uma NVIDIA, o script usará automaticamente o motor CUDA para acelerar o processamento de imagens.

## 🛡️ dados técnicos da versão de 10/05/2026 V1
1 - Gestão de Recursos: O uso de gc.collect() e torch.cuda.empty_cache() é vital para processos de longa duração. conforme vai crescendo a varredura ao longo do ano por exemplo. 
2 - Lógica de Causalidade: A restrição TS_Whats.dt.date >= data_limite na conciliação é perfeita; ela impede "viagens no tempo" onde um comprovante antigo pagaria uma conta nova.Sempre qeu você inserir no whats um comprovante é porque a despesa com 100% de certeja ja existe em data e hr anterior no comprovante do nubank. então o script so pega a data e hr do extrado nubanck e varre a conversa do whats sempre pra frente, nunca pra trás, isso ja evita pegar despesas iguais pra tras. 
Resiliência no OCR: O sistema de cache para o EasyOCR economiza horas de processamento em execuções repetidas. A gente manda limpar o cache da placa de vídeo após rodar as leituras das imagens. 