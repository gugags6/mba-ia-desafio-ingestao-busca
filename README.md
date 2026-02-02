# Desafio MBA Engenharia de Software com IA - Full Cycle

# Busca Semântica com PDF + LangChain + pgvector

Passo 1: Subir o ambiente docker do PG Vector:

docker compose up -d

Passo 2: Realizar a ingestao do documento:
python src/ingest.py

Passo 3: Executar o script de chat:
python src/chat.py
