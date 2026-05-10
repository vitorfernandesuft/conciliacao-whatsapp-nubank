import pandas as pd
import re
import glob
import os
import fitz  # PyMuPDF
from tqdm import tqdm
import gc

# --- CONFIGURAÇÃO DE CAMINHOS ---
PASTA_DADOS = "dados"
PASTA_MIDIAS = os.path.join(PASTA_DADOS, "midias")
PASTA_EXTRATOS = os.path.join(PASTA_DADOS, "Extrato_nubank")
PASTA_RESULTADOS = os.path.join(PASTA_DADOS, "resultados")

for p in [PASTA_MIDIAS, PASTA_RESULTADOS, PASTA_EXTRATOS]:
    os.makedirs(p, exist_ok=True)

ARQUIVO_WHATS_FINAL = os.path.join(PASTA_RESULTADOS, "Relatorio_WhatsApp_Consolidado.xlsx")
ARQUIVO_EXTRATO_FINAL = os.path.join(PASTA_RESULTADOS, "Extrato_Nubank_Unificado.xlsx")
ARQUIVO_CONCILIACAO = os.path.join(PASTA_RESULTADOS, "CONCILIACAO_FINAL_ESTRUTURADA.xlsx")

reader = None

def limpar_valor(valor):
    if pd.isna(valor) or valor == "": return 0.0
    if isinstance(valor, (int, float)): return abs(float(valor))
    s = str(valor).replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
    try: return abs(float(s))
    except: return 0.0

def extrair_dados_texto(texto):
    valor_match = re.search(r'(?:R\$|Valor.*?)\s?([\d\.]+,\d{2})', texto, re.IGNORECASE)
    valor_str = valor_match.group(1) if valor_match else "0,00"
    valor_num = float(valor_str.replace('.', '').replace(',', '.'))
    data_match = re.search(r'(\d{2}/\d{2}/\d{4})', texto)
    data = data_match.group(1) if data_match else ""
    return valor_num, data

# ==========================================
# MÓDULO 1: WHATSAPP (OCR + CONTEXTO)
# ==========================================
def processar_whatsapp():
    global reader
    print("\n[!] Lendo Conversas e Mídias (Cache OCR + Contexto)...")
    import torch
    import easyocr
    
    gpu_on = torch.cuda.is_available()
    conversa_txt_lista = glob.glob(os.path.join(PASTA_DADOS, "*.txt"))
    conversa_txt = [f for f in conversa_txt_lista if "_lido" not in f]
    if not conversa_txt: print("ERRO: TXT não encontrado."); return

    arquivos_midia = {}
    for ext in ["*.jpg", "*.png", "*.jpeg", "*.pdf"]:
        for f in glob.glob(os.path.join(PASTA_MIDIAS, ext)):
            arquivos_midia[os.path.basename(f)] = f
    
    dados_arquivos = {}
    for nome_arq, caminho_arq in tqdm(arquivos_midia.items(), desc="Processando Anexos"):
        texto = ""
        if caminho_arq.lower().endswith(('.png', '.jpg', '.jpeg')):
            nome_base = os.path.splitext(nome_arq)[0]
            cache = os.path.join(PASTA_MIDIAS, f"{nome_base}_lido.txt")
            if os.path.exists(cache):
                with open(cache, 'r', encoding='utf-8') as f: texto = f.read()
            else:
                if reader is None: reader = easyocr.Reader(['pt'], gpu=gpu_on)
                texto = " ".join(reader.readtext(caminho_arq, detail=0))
                with open(cache, 'w', encoding='utf-8') as f: f.write(texto)
        elif caminho_arq.lower().endswith('.pdf'):
            try:
                doc = fitz.open(caminho_arq)
                texto = "".join([p.get_text() for p in doc]) if len(doc) <= 2 else doc[0].get_text()
                doc.close()
            except: continue
        if texto:
            v, _ = extrair_dados_texto(texto)
            dados_arquivos[nome_arq] = {'Valor_Anexo': v, 'Texto_Anexo': texto}

    if reader is not None:
        del reader
        reader = None
    if gpu_on: torch.cuda.empty_cache()
    gc.collect()

    with open(conversa_txt[0], 'r', encoding='utf-8', errors='ignore') as f:
        linhas_conversa = f.readlines()

    # Otimização: Criar um padrão regex que busca qualquer um dos nomes de arquivo de uma vez
    if not dados_arquivos: print("AVISO: Nenhuma mídia processada."); return
    padrao_arquivos = re.compile('|'.join(map(re.escape, dados_arquivos.keys())))

    mensagens_vinculo = []
    for i, linha in enumerate(linhas_conversa):
        match_arq = padrao_arquivos.search(linha)
        if match_arq:
                nome_arq = match_arq.group()
                info = dados_arquivos[nome_arq]
                m = re.search(r'(\d{2}/\d{2}/\d{4}\s\d{2}:\d{2})', linha)
                data_hora = m.group(1) if m else ""
                
                # Contexto: 1 linha antes, 2 linhas depois
                inicio = max(0, i - 1)
                fim = min(len(linhas_conversa), i + 3)
                contexto = "".join(linhas_conversa[inicio:fim]).strip()
                
                mensagens_vinculo.append({
                    'TS_Whats': pd.to_datetime(data_hora, dayfirst=True) if data_hora else pd.Timestamp.min,
                    'Data_Hora': data_hora,
                    'Arquivo': nome_arq,
                    'Valor_Anexo': info['Valor_Anexo'],
                    'Texto_Arquivo': info['Texto_Anexo'], # Coluna recuperada
                    'Contexto_Chat': contexto
                })
    
    df = pd.DataFrame(mensagens_vinculo).sort_values('TS_Whats').reset_index(drop=True)
    df.to_excel(ARQUIVO_WHATS_FINAL, index=False)

# ==========================================
# MÓDULO 2: EXTRATO NUBANK
# ==========================================
def processar_extrato():
    print("\n--- [PASSO 2] Unificando Extratos ---")
    arquivos = glob.glob(os.path.join(PASTA_EXTRATOS, "*.pdf"))
    if not arquivos: return
    todas_transacoes = []
    meses_map = {'JAN': '01', 'FEV': '02', 'MAR': '03', 'ABR': '04', 'MAI': '05', 'JUN': '06',
                 'JUL': '07', 'AGO': '08', 'SET': '09', 'OUT': '10', 'NOV': '11', 'DEZ': '12'}

    for caminho_pdf in arquivos:
        doc = fitz.open(caminho_pdf)
        data_at = ""
        for pagina in doc:
            linhas = pagina.get_text("text").split('\n')
            for i, lin in enumerate(linhas):
                lin = lin.strip()
                m_data = re.match(r'^(\d{2}\s[A-Z]{3}\s\d{4})', lin)
                if m_data: data_at = m_data.group(1); continue
                # Captura transações comuns ignorando 'Recebida' para focar em saídas/pagamentos se necessário
                if any(lin.startswith(x) for x in ["Transferência", "Pagamento", "Débito", "Compra", "Pix", "Crédito"]):
                    for j in range(1, 12):
                        if i+j < len(linhas):
                            candidata = linhas[i+j].strip()
                            m_val = re.search(r'([\d\.]+,\d{2})$', candidata)
                            if m_val and not re.match(r'^\d{2}\s[A-Z]{3}', candidata) and "Total" not in candidata:
                                v = float(m_val.group(1).replace('.','').replace(',','.'))
                                if "recebida" not in lin.lower() and "recebido" not in lin.lower(): v = -abs(v)
                                todas_transacoes.append({'Data_Banco': data_at, 'Descrição_Banco': lin, 'Valor_Banco': v})
                                break
        doc.close()

    df = pd.DataFrame(todas_transacoes)
    if not df.empty:
        def formatar_data(x):
            partes = x.split()
            mes = meses_map.get(partes[1], '01')
            return pd.to_datetime(f"{partes[2]}-{mes}-{partes[0]}")
        df['TS_Banco'] = df['Data_Banco'].apply(formatar_data)
        df = df.drop_duplicates().sort_values('TS_Banco').reset_index(drop=True)
        df.to_excel(ARQUIVO_EXTRATO_FINAL, index=False)

# ==========================================
# MÓDULO 3: CONCILIAÇÃO FINAL
# ==========================================
def realizar_conciliacao():
    print("\n--- [PASSO 3] Gerando Relatório de Conciliação ---")
    df_banco = pd.read_excel(ARQUIVO_EXTRATO_FINAL)
    df_whats = pd.read_excel(ARQUIVO_WHATS_FINAL)
    
    df_banco['TS_Banco'] = pd.to_datetime(df_banco['TS_Banco'])
    df_whats['TS_Whats'] = pd.to_datetime(df_whats['TS_Whats'])
    
    df_banco['Status'] = 'NÃO CONCILIADO'
    df_banco['Data_Hora_Whats'], df_banco['Texto_Arquivo'], df_banco['Contexto_Chat'], df_banco['Arquivo_Whats'] = '', '', '', ''
    
    indices_whats_usados = set()

    for idx_b, row_b in df_banco.iterrows():
        v_busca = limpar_valor(row_b['Valor_Banco'])
        data_limite = row_b['TS_Banco'].date()
        
        match = df_whats[
            (df_whats['Valor_Anexo'].apply(limpar_valor) == v_busca) & 
            (df_whats['TS_Whats'].dt.date >= data_limite) &
            (~df_whats.index.isin(indices_whats_usados))
        ].head(1)

        if not match.empty:
            idx_w = match.index[0]
            indices_whats_usados.add(idx_w)
            df_banco.at[idx_b, 'Status'] = 'CONCILIADO'
            df_banco.at[idx_b, 'Data_Hora_Whats'] = match.iloc[0]['Data_Hora']
            df_banco.at[idx_b, 'Texto_Arquivo'] = match.iloc[0]['Texto_Arquivo'] # Recuperado
            df_banco.at[idx_b, 'Contexto_Chat'] = match.iloc[0]['Contexto_Chat'] # Adicionado ao fim
            df_banco.at[idx_b, 'Arquivo_Whats'] = match.iloc[0]['Arquivo']

    # Exportação Final
    writer = pd.ExcelWriter(ARQUIVO_CONCILIACAO, engine='xlsxwriter')
    # Ordem: Banco -> Dados Whats -> OCR -> Contexto
    cols = ['Status', 'Data_Banco', 'Valor_Banco', 'Data_Hora_Whats', 'Descrição_Banco', 'Texto_Arquivo', 'Arquivo_Whats', 'Contexto_Chat']
    df_banco[cols].to_excel(writer, index=False, sheet_name='Conciliacao')
    
    wb, ws = writer.book, writer.sheets['Conciliacao']
    f_v = wb.add_format({'bg_color': '#D9EAD3', 'font_color': '#006100'})
    f_r = wb.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'})
    f_m = wb.add_format({'num_format': 'R$ #,##0.00'})
    f_w = wb.add_format({'text_wrap': True, 'valign': 'top', 'font_size': 8})
    f_header = wb.add_format({'bold': True, 'bg_color': '#F2F2F2', 'border': 1})

    ws.conditional_format('A2:A5000', {'type': 'cell', 'criteria': 'equal to', 'value': '"CONCILIADO"', 'format': f_v})
    ws.conditional_format('A2:A5000', {'type': 'cell', 'criteria': 'equal to', 'value': '"NÃO CONCILIADO"', 'format': f_r})
    ws.set_column('A:B', 15); ws.set_column('C:C', 14, f_m)
    ws.set_column('D:D', 18); ws.set_column('E:F', 45, f_w)
    ws.set_column('G:G', 20)
    ws.set_column('H:H', 65, f_w) # Contexto por último e bem largo
    writer.close()
    print(f"SUCESSO: {ARQUIVO_CONCILIACAO}")

if __name__ == "__main__":
    processar_whatsapp(); processar_extrato(); realizar_conciliacao()
