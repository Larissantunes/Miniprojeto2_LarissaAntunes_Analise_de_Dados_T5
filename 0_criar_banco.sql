-- ===== CAMADA RAW =====
-- Cópia fiel dos CSVs: todas as colunas em TEXT, sem constraints.

CREATE TABLE raw_viagem (
    id_viagem TEXT,
    num_proposta TEXT,
    situacao TEXT,
    viagem_urgente TEXT,
    justificativa_urgencia TEXT,
    cod_orgao_superior TEXT,
    nome_orgao_superior TEXT,
    cod_orgao_solicitante TEXT,
    nome_orgao_solicitante TEXT,
    cpf_viajante TEXT,
    nome_viajante TEXT,
    cargo TEXT,
    funcao TEXT,
    descricao_funcao TEXT,
    data_inicio TEXT,
    data_fim TEXT,
    destinos TEXT,
    motivo TEXT,
    valor_diarias TEXT,
    valor_passagens TEXT,
    valor_devolucao TEXT,
    valor_outros_gastos TEXT
);

CREATE TABLE raw_pagamento (
    id_viagem TEXT,
    num_proposta TEXT,
    cod_orgao_superior TEXT,
    nome_orgao_superior TEXT,
    cod_orgao_pagador TEXT,
    nome_orgao_pagador TEXT,
    cod_ug_pagadora TEXT,
    nome_ug_pagadora TEXT,
    tipo_pagamento TEXT,
    valor TEXT
);

CREATE TABLE raw_passagem (
    id_viagem TEXT,
    num_proposta TEXT,
    meio_transporte TEXT,
    pais_origem_ida TEXT,
    uf_origem_ida TEXT,
    cidade_origem_ida TEXT,
    pais_destino_ida TEXT,
    uf_destino_ida TEXT,
    cidade_destino_ida TEXT,
    pais_origem_volta TEXT,
    uf_origem_volta TEXT,
    cidade_origem_volta TEXT,
    pais_destino_volta TEXT,
    uf_destino_volta TEXT,
    cidade_destino_volta TEXT,
    valor_passagem TEXT,
    taxa_servico TEXT,
    data_emissao TEXT,
    hora_emissao TEXT
);

CREATE TABLE raw_trecho (
    id_viagem TEXT,
    num_proposta TEXT,
    sequencia_trecho TEXT,
    origem_data TEXT,
    origem_pais TEXT,
    origem_uf TEXT,
    origem_cidade TEXT,
    destino_data TEXT,
    destino_pais TEXT,
    destino_uf TEXT,
    destino_cidade TEXT,
    meio_transporte TEXT,
    numero_diarias TEXT,
    missao TEXT
);

-- ===== CAMADA SILVER =====
-- Dados limpos e tipados, com integridade referencial (PK/FK) e constraints.

CREATE TABLE silver_viagem (
    id_viagem VARCHAR(20) PRIMARY KEY,
    num_proposta VARCHAR(20),
    situacao VARCHAR(50),
    viagem_urgente VARCHAR(5),
    cod_orgao_superior VARCHAR(20),
    nome_orgao_superior VARCHAR(255) NOT NULL,
    nome_viajante VARCHAR(255),
    cargo VARCHAR(255),
    data_inicio DATE,
    data_fim DATE,
    destinos VARCHAR(4000),
    motivo VARCHAR(4000),
    valor_diarias DECIMAL(10,2) CHECK (valor_diarias >= 0),
    valor_passagens DECIMAL(10,2),
    valor_devolucao DECIMAL(10,2),
    valor_outros_gastos DECIMAL(10,2),
    valor_total DECIMAL(12,2),
    duracao_dias INT
);

CREATE TABLE silver_pagamento (
    id_pagamento INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_viagem VARCHAR(20) NOT NULL REFERENCES silver_viagem(id_viagem),
    num_proposta VARCHAR(20),
    nome_orgao_pagador VARCHAR(255),
    nome_ug_pagadora VARCHAR(255),
    tipo_pagamento VARCHAR(50) NOT NULL,
    valor DECIMAL(10,2) CHECK (valor >= 0)
);

CREATE TABLE silver_passagem (
    id_passagem INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_viagem VARCHAR(20) NOT NULL REFERENCES silver_viagem(id_viagem),
    meio_transporte VARCHAR(50),
    pais_origem_ida VARCHAR(60),
    uf_origem_ida VARCHAR(40),
    cidade_origem_ida VARCHAR(80),
    pais_destino_ida VARCHAR(60),
    uf_destino_ida VARCHAR(40),
    cidade_destino_ida VARCHAR(80),
    valor_passagem DECIMAL(10,2) CHECK (valor_passagem >= 0),
    taxa_servico DECIMAL(10,2) CHECK (taxa_servico >= 0),
    data_emissao DATE
);

CREATE TABLE silver_trecho (
    id_trecho INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_viagem VARCHAR(20) NOT NULL REFERENCES silver_viagem(id_viagem),
    sequencia_trecho INT,
    origem_data DATE,
    origem_uf VARCHAR(40),
    origem_cidade VARCHAR(80),
    destino_data DATE,
    destino_uf VARCHAR(40),
    destino_cidade VARCHAR(80),
    meio_transporte VARCHAR(50),
    numero_diarias DECIMAL(10,2) CHECK (numero_diarias >= 0),
    UNIQUE (id_viagem, sequencia_trecho)
);
   