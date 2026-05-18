-- ================================================================
-- VF Veículos — Schema Financeiro
-- ================================================================

CREATE TABLE IF NOT EXISTS transacoes_banco (
    id          SERIAL PRIMARY KEY,
    data_banco  VARCHAR(20),
    ts_banco    TIMESTAMP,
    descricao   VARCHAR(500),
    valor       NUMERIC(10,2),
    criado_em   TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS comprovantes_whatsapp (
    id              SERIAL PRIMARY KEY,
    ts_whatsapp     TIMESTAMP,
    nome_arquivo    VARCHAR(255),
    valor_extraido  NUMERIC(10,2),
    texto_ocr       TEXT,
    contexto_chat   TEXT,
    grupo_id        VARCHAR(100),
    criado_em       TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS conciliacao (
    id              SERIAL PRIMARY KEY,
    status          VARCHAR(20) NOT NULL DEFAULT 'NAO_CONCILIADO',
    transacao_id    INTEGER REFERENCES transacoes_banco(id),
    comprovante_id  INTEGER REFERENCES comprovantes_whatsapp(id),
    ts_banco        TIMESTAMP,
    ts_whatsapp     TIMESTAMP,
    valor           NUMERIC(10,2),
    descricao_banco VARCHAR(500),
    arquivo_whatsapp VARCHAR(255),
    texto_ocr       TEXT,
    contexto_chat   TEXT,
    atualizado_em   TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_conciliacao_status    ON conciliacao(status);
CREATE INDEX IF NOT EXISTS idx_transacoes_ts         ON transacoes_banco(ts_banco);
CREATE INDEX IF NOT EXISTS idx_comprovantes_ts       ON comprovantes_whatsapp(ts_whatsapp);
CREATE INDEX IF NOT EXISTS idx_comprovantes_valor    ON comprovantes_whatsapp(valor_extraido);
