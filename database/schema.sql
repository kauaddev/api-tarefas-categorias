-- Estrutura do banco (SQLite) da API de Tarefas e Categorias.
-- Gerado a partir dos modelos SQLAlchemy (app/models.py).
-- A API já cria estas tabelas sozinha na primeira execução;
-- este arquivo serve de documentação e para recriar o banco manualmente:
--   sqlite3 tarefas.db < database/schema.sql

CREATE TABLE categorias (
	id INTEGER NOT NULL, 
	nome VARCHAR(80) NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (nome)
);

CREATE INDEX ix_categorias_id ON categorias (id);

CREATE TABLE usuarios (
	id INTEGER NOT NULL, 
	username VARCHAR(50) NOT NULL, 
	senha_hash VARCHAR(100) NOT NULL, 
	criado_em DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (username)
);

CREATE INDEX ix_usuarios_id ON usuarios (id);

CREATE TABLE tarefas (
	id INTEGER NOT NULL, 
	titulo VARCHAR(120) NOT NULL, 
	descricao TEXT, 
	concluida BOOLEAN NOT NULL, 
	criada_em DATETIME NOT NULL, 
	categoria_id INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(categoria_id) REFERENCES categorias (id)
);

CREATE INDEX ix_tarefas_id ON tarefas (id);
