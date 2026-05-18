import os
import re
import hashlib
import tempfile

import fitz
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI(title="VF OCR Service")

CACHE_DIR = "/app/cache"
os.makedirs(CACHE_DIR, exist_ok=True)

_reader = None


def get_reader():
    global _reader
    if _reader is None:
        import easyocr
        _reader = easyocr.Reader(['pt'], gpu=False)
    return _reader


def extrair_valor(texto: str) -> float:
    match = re.search(r'(?:R\$|Valor.*?)\s?([\d\.]+,\d{2})', texto, re.IGNORECASE)
    if match:
        return float(match.group(1).replace('.', '').replace(',', '.'))
    return 0.0


def hash_bytes(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ocr")
async def processar_ocr(file: UploadFile = File(...)):
    conteudo = await file.read()
    nome = (file.filename or "").lower()
    texto = ""

    cache_path = os.path.join(CACHE_DIR, f"{hash_bytes(conteudo)}.txt")

    if os.path.exists(cache_path):
        with open(cache_path, 'r', encoding='utf-8') as f:
            texto = f.read()

    elif nome.endswith('.pdf'):
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp.write(conteudo)
            tmp_path = tmp.name
        try:
            doc = fitz.open(tmp_path)
            texto = "".join(p.get_text() for p in doc) if len(doc) <= 2 else doc[0].get_text()
            doc.close()
        finally:
            os.unlink(tmp_path)

    elif nome.endswith(('.jpg', '.jpeg', '.png')):
        ext = os.path.splitext(nome)[1] or '.jpg'
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
            tmp.write(conteudo)
            tmp_path = tmp.name
        try:
            resultado = get_reader().readtext(tmp_path, detail=0)
            texto = " ".join(resultado)
        finally:
            os.unlink(tmp_path)

    else:
        raise HTTPException(status_code=400, detail=f"Formato não suportado: {nome}")

    if texto:
        with open(cache_path, 'w', encoding='utf-8') as f:
            f.write(texto)

    return JSONResponse({
        "arquivo": file.filename,
        "valor": extrair_valor(texto),
        "texto": texto,
    })
