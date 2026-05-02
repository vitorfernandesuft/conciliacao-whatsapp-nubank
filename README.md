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
# 1. Ensinando do jeito tradicionalzão
1. Instalar as Ferramentas Base (O Motor)Nesse computador novo, você precisa das duas ferramentas que instalamos no início:Instale o UV (mesmo comando de antes):powershellpowershell -c "irm https://astral.sh | iex"
Use o código com cuidado.Instale o Git: Baixe e instale o Git for Windows.2. Clonar o Projeto (Baixar do GitHub)Crie uma pasta nova (ex: C:\TesteVitor) e, dentro dela, abra o CMD e rode:cmd# Baixa o seu projeto exatamente como ele está no GitHub
git clone git@github.com:vitorfernandesuft/conciliacao-whatsapp-nubank.git
Use o código com cuidado.Nota: Como é um PC novo, você precisaria gerar uma nova chave SSH para esse PC e adicionar no GitHub, como fizemos antes. Se não quiser fazer isso agora, use o link HTTPS: git clone https://github.com.3. Criar o Ambiente com UV (A Mágica)Agora entre na pasta que o Git criou:cmdcd conciliacao-whatsapp-nubank
Use o código com cuidado.Em vez de instalar biblioteca por biblioteca, você vai usar o arquivo pyproject.toml ou o requirements.txt que você salvou. O UV faz tudo sozinho:cmd# 1. Cria o ambiente virtual 3.12 (o UV baixa o Python se não tiver)
uv venv --python 3.12

# 2. Ativa o ambiente
.venv\Scripts\activate

# 3. Instala todas as dependências de uma vez só!
uv pip install -r requirements.txt
Use o código com cuidado.4. O Detalhe Importante: A Pasta dadosLembra que colocamos a pasta dados/ no .gitignore? Por causa disso, ela não veio do GitHub. O seu script vai dar erro se você tentar rodar agora.Você precisa:Criar a pasta dados manualmente (ou o script criará para você).Copiar o seu arquivo de conversa (.txt) e o extrato (.pdf) para dentro dela.Copiar as fotos para dados/midias.5. Rodar e Validar a GPUComo o computador é novo, você precisa testar se a placa de vídeo dele está conversando com o Python:cmdpython -c "import torch; print('GPU ESTÁ FUNCIONANDO?', torch.cuda.is_available())"
Use o código com cuidado.Se der False, você já sabe: é só baixar o driver da NVIDIA nesse novo PC.Resumo do que aconteceu:O Git trouxe o seu código (o "esqueleto").O UV reconstruiu os "músculos" (as bibliotecas) em segundos.Você só precisou colocar o "combustível" (os arquivos de dados privados).

# 4. Ensiando a usar o UV de modo mais profissional 
O Jeito "Mestre" (com uv sync)Dentro da pasta do projeto, você simplesmente digita

:cmd: uv sync
O que o uv faz automaticamente quando você dá esse comando:Lê o pyproject.toml: Ele vê que você precisa do Python 3.12.Lê o uv.lock: Ele vê as versões exatas de cada biblioteca (torch, pandas, etc).Instala o Python: Se o PC não tiver o 3.12, o uv baixa e instala ele em uma pasta isolada.Cria o .venv: Cria o ambiente virtual sozinho.Instala as Bibliotecas: Baixa tudo o que está no arquivo de trava (lock).Tudo isso acontece em um único processo. Não precisa criar o venv na mão, nem ativar, nem dar pip install.

Como rodar o script depois do sync? Você também não precisa ativar o ambiente toda vez se usar o uv run. Basta digitar:cmd: uv run 
Sistema_Financeiro_Turbo_GPU.py
O uv identifica o ambiente virtual, usa o Python correto e roda o script. Se algo estiver faltando, ele avisa ou instala na hora.

Resumo da Simulação no PC Novo:
git clone ... (Baixa o código)
uv sync (Prepara a máquina inteira)
uv run script.py (Executa)

Por que o uv.lock é importante aqui No GitHub, o seu arquivo uv.lock é o segredo. Ele garante que o uv sync no outro computador instale exatamente as mesmas versões que você está usando hoje. Sem o .lock, o outro PC poderia baixar uma versão nova de alguma biblioteca que mudou o nome de um comando e seu script "quebraria".

## 🚀 4. Como Usar de outro modo ainda
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
