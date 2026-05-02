import pandas as pd
import re
import glob
import os
import fitz  # PyMuPDF
import xlsxwriter
from tqdm import tqdm

# --- CONFIGURAÇÃO DE CAMINHOS ---
# --- olá testando para git 
PASTA_DADOS = "dados"
PASTA_MIDIAS = os.path.join(PASTA_DADOS, "midias")
PASTA_RESULTADOS = os.path.join(PASTA_DADOS, "resultados")

# Criar pastas caso não existam
for p in [PASTA_MIDIAS, PASTA_RESULTADOS]:
    os.makedirs(p, exist_ok=True)

ARQUIVO_WHATS_FINAL = os.path.join(PASTA_RESULTADOS, "Relatorio_WhatsApp_Consolidado.xlsx")
ARQUIVO_EXTRATO_FINAL = os.path.join(PASTA_RESULTADOS, "Extrato_Nubank.xlsx")
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
# MÓDULO 1: WHATSAPP
# ==========================================
def processar_whatsapp():
    global reader
    print("\n[!] Carregando motores de IA e GPU...")
    import torch
    import easyocr
    
    gpu_on = torch.cuda.is_available()
    print(f" -> ACELERAÇÃO POR GPU: {'ATIVADA' if gpu_on else 'DESATIVADA'}")

    # Busca o TXT da conversa (ignora os arquivos de cache "_lido")
    conversa_txt_lista = glob.glob(os.path.join(PASTA_DADOS, "*.txt"))
    conversa_txt = [f for f in conversa_txt_lista if "_lido" not in f]
    
    if not conversa_txt:
        print(f"ERRO: Nenhum arquivo .txt de conversa encontrado em {PASTA_DADOS}"); return

    # Busca imagens
    imagens = []
    for ext in ["*.jpg", "*.png", "*.jpeg"]:
        imagens.extend(glob.glob(os.path.join(PASTA_MIDIAS, ext)))
    
    pdfs_midia = [f for f in glob.glob(os.path.join(PASTA_MIDIAS, "*.pdf"))]
    dados_arquivos = {}

    if imagens:
        print(f" -> Verificando {len(imagens)} imagens em {PASTA_MIDIAS}...")
        if reader is None: reader = easyocr.Reader(['pt'], gpu=gpu_on)
        
        for img in tqdm(imagens, desc="Processando OCR", unit="img"):
            nome_arq = os.path.basename(img) # Ex: IMG-123.jpg
            # Pega o nome sem a extensão (Ex: IMG-123) e adiciona "_lido"
            nome_base = os.path.splitext(nome_arq)[0]
            cache = os.path.join(PASTA_MIDIAS, f"{nome_base}_lido")
            
            if os.path.exists(cache):
                with open(cache, 'r', encoding='utf-8') as f: 
                    texto = f.read()
            else:
                texto = " ".join(reader.readtext(img, detail=0))
                with open(cache, 'w', encoding='utf-8') as f: 
                    f.write(texto)
            
            v, _ = extrair_dados_texto(texto)
            dados_arquivos[nome_arq] = {'Valor_OCR': v, 'Texto_OCR': texto}
    
    # ... (restante do código segue igual)

# ==========================================
# MÓDULO 2: EXTRATO NUBANK
# ==========================================
def processar_extrato():
    print("\n--- [PASSO 2] Processando Extrato Nubank ---")
    arquivos = glob.glob(os.path.join(PASTA_DADOS, "Extrato_*.pdf"))
    if not arquivos: print(f"ERRO: Extrato não encontrado em {PASTA_DADOS}"); return
    doc = fitz.open(arquivos[0])
    transacoes = []
    data_at = ""
    for pagina in doc:
        linhas = pagina.get_text("text").split('\n')
        i = 0
        while i < len(linhas):
            lin = linhas[i].strip()
            m_data = re.match(r'^(\d{2}\s[A-Z]{3}\s\d{4})', lin)
            if m_data: data_at = m_data.group(1); i+=1; continue
            if any(x in lin for x in ["Total de entradas", "Total de saídas", "Saldo do dia"]): i+=1; continue
            if any(lin.startswith(x) for x in ["Transferência", "Pagamento", "Débito"]):
                desc, tipo = lin, ("entrada" if "recebida" in lin.lower() else "saida")
                prox = i + 1
                while prox < len(linhas):
                    m_val = re.search(r'([\d\.]+,\d{2})$', linhas[prox].strip())
                    if m_val:
                        v = float(m_val.group(1).replace('.','').replace(',','.'))
                        if tipo == "saida": v = -abs(v)
                        transacoes.append({'Data': data_at, 'Descrição': desc, 'Valor': v})
                        i = prox; break
                    else:
                        if linhas[prox].strip() and not re.match(r'^\d{2}\s[A-Z]{3}', linhas[prox]): desc += " " + linhas[prox].strip()
                        prox += 1
            i += 1
    doc.close()
    df = pd.DataFrame(transacoes)
    writer = pd.ExcelWriter(ARQUIVO_EXTRATO_FINAL, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Transacoes')
    pd.DataFrame({'Descrição': ['Entradas', 'Saídas', 'SALDO'], 'Valor': [0.0, 0.0, 0.0]}).to_excel(writer, index=False, sheet_name='Resumo')
    ws1, ws2 = writer.sheets['Transacoes'], writer.sheets['Resumo']
    ws2.write_formula('B2', '=SUMIF(Transacoes!C:C, ">0")')
    ws2.write_formula('B3', '=SUMIF(Transacoes!C:C, "<0")')
    ws2.write_formula('B4', '=B2+B3')
    ws1.set_column('C:C', 18, writer.book.add_format({'num_format': 'R$ #,##0.00'}))
    writer.close()
    print(f"SUCESSO: Extrato salvo em {PASTA_RESULTADOS}")

# ==========================================
# MÓDULO 3: CONCILIAÇÃO FINAL
# ==========================================
def realizar_conciliacao():
    if not os.path.exists(ARQUIVO_WHATS_FINAL): processar_whatsapp()
    if not os.path.exists(ARQUIVO_EXTRATO_FINAL): processar_extrato()
    print("\n--- [PASSO 3] Conciliando Banco x WhatsApp ---")
    df_banco = pd.read_excel(ARQUIVO_EXTRATO_FINAL, sheet_name='Transacoes')
    df_whats = pd.read_excel(ARQUIVO_WHATS_FINAL)
    df_whats['v_limpo'] = df_whats['Valor_OCR'].apply(limpar_valor)
    df_banco['v_limpo'] = df_banco['Valor'].apply(limpar_valor)
    df_banco['Status'] = 'Não Encontrado'
    df_banco['Legenda_WhatsApp'], df_banco['Conteúdo_OCR'], df_banco['Contexto_Chat'] = '', '', ''

    for idx_b, row_b in df_banco.iterrows():
        v_busca = row_b['v_limpo']
        if v_busca == 0: continue
        matches = df_whats[df_whats['v_limpo'] == v_busca].copy()
        if not matches.empty:
            idx_w = matches.index[0]
            row_w = df_whats.loc[idx_w]
            inicio, fim = max(0, idx_w - 2), min(len(df_whats), idx_w + 3)
            chat = "".join([f"[{r['Autor']}]: {r['Mensagem']}\n" for _, r in df_whats.iloc[inicio:fim].iterrows()])
            df_banco.at[idx_b, 'Status'] = 'CONCILIADO'
            df_banco.at[idx_b, 'Legenda_WhatsApp'] = str(row_w.get('Legenda_Anexo', ''))
            df_banco.at[idx_b, 'Conteúdo_OCR'] = str(row_w.get('Texto_OCR', ''))
            df_banco.at[idx_b, 'Contexto_Chat'] = chat.strip()

    df_final = df_banco.drop(columns=['v_limpo'])
    writer = pd.ExcelWriter(ARQUIVO_CONCILIACAO, engine='xlsxwriter')
    df_final.to_excel(writer, index=False)
    wb, ws = writer.book, writer.sheets['Sheet1']
    fmt_verde = wb.add_format({'bg_color': '#D9EAD3', 'font_color': '#006100'})
    fmt_vermelho = wb.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'})
    ws.conditional_format('D2:D2000', {'type': 'cell', 'criteria': 'equal to', 'value': '"CONCILIADO"', 'format': fmt_verde})
    ws.conditional_format('D2:D2000', {'type': 'cell', 'criteria': 'equal to', 'value': '"Não Encontrado"', 'format': fmt_vermelho})
    fmt_moeda = wb.add_format({'num_format': 'R$ #,##0.00'})
    fmt_wrap = wb.add_format({'text_wrap': True, 'valign': 'top', 'font_size': 9})
    ws.set_column('C:C', 15, fmt_moeda); ws.set_column('E:G', 50, fmt_wrap)
    writer.close()
    print(f"SUCESSO: Relatório Final salvo em {PASTA_RESULTADOS}")

def menu():
    while True:
        print("\n" + "="*50 + "\nSISTEMA FINANCEIRO V6.0\n" + "="*50)
        print("1 - WhatsApp | 2 - Extrato | 3 - CONCILIAÇÃO | 0 - Sair")
        op = input("\nEscolha: ")
        if op == '1': processar_whatsapp()
        elif op == '2': processar_extrato()
        elif op == '3': realizar_conciliacao()
        elif op in ['0', 'sair']: break

if __name__ == "__main__":
    menu()
