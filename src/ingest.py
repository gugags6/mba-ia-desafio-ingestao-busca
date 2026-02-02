import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_postgres import PGVector
from pathlib import Path

load_dotenv()

PDF_PATH = os.getenv("PDF_PATH")

def ingest_pdf():

    required_vars = ("OPENAI_API_KEY", "DATABASE_URL", "PG_VECTOR_COLLECTION_NAME")

    for k in required_vars:
        if not os.getenv(k):
            raise RuntimeError(f" Environment variable {k} is not set")

  
    BASE_DIR = Path(__file__).resolve().parents[1]
    pdf_path = BASE_DIR/PDF_PATH

    if not pdf_path.exists():
        raise FileNotFoundError(f" PDF não encontrado em: {pdf_path}")

    print(f"Lendo PDF: {pdf_path.name}")


    docs = PyPDFLoader(str(pdf_path)).load()

    if not docs:
        raise SystemExit("Nenhuma página encontrada no PDF.")

    print(f"Total de páginas carregadas: {len(docs)}")

 
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        add_start_index=False
    )

    splits = splitter.split_documents(docs)

    if not splits:
        raise SystemExit(" Nenhum chunk gerado. Encerrando ingestão.")

    print(f"Total de chunks gerados: {len(splits)}")

 
    enriched_docs = []

    for d in splits:
        cleaned_metadata = {
            k: v for k, v in d.metadata.items()
            if v not in ("", None)
        }

        enriched_docs.append(
            Document(
                page_content=d.page_content,
                metadata=cleaned_metadata
            )
        )


    ids = [f"doc-{i}" for i in range(len(enriched_docs))]


    embedding_model = os.getenv("OPENAI_MODEL", "text-embedding-3-small")

    print(f" Gerando embeddings com modelo: {embedding_model}")

    embeddings = OpenAIEmbeddings(model=embedding_model)


    print("Conectando ao banco vetorial...")

    store = PGVector(
        embeddings=embeddings,
        collection_name=os.getenv("PG_VECTOR_COLLECTION_NAME"),
        connection=os.getenv("DATABASE_URL"),
        use_jsonb=True,  # metadados ficam mais flexíveis
    )

    print("Inserindo documentos no pgvector...")

    store.add_documents(
        documents=enriched_docs,
        ids=ids
    )

    print("\n INGESTÃO FINALIZADA COM SUCESSO!")
    print(f" Collection: {os.getenv('PGVECTOR_COLLECTION')}")
    print(f"Total armazenado: {len(enriched_docs)} chunks")


if __name__ == "__main__":
    ingest_pdf()