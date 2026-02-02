import os
from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector




PROMPT_TEMPLATE = """
CONTEXTO:
{contexto}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual é a capital da França?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Você acha isso bom ou ruim?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

PERGUNTA DO USUÁRIO:
{pergunta}

RESPONDA A "PERGUNTA DO USUÁRIO"
"""




def search_prompt(question: str, k: int = 10) -> str:
    """
    Recebe uma pergunta do usuário e devolve o prompt final
    contendo os chunks mais relevantes como CONTEXTO.
    """

    load_dotenv()


    for var in ("PGVECTOR_URL", "PGVECTOR_COLLECTION", "OPENAI_API_KEY"):
        if not os.getenv(var):
            raise RuntimeError(f"Environment variable {var} is not set")

    if not question:
        raise ValueError("A pergunta não pode ser vazia.")


    embeddings = OpenAIEmbeddings(
        model=os.getenv("OPENAI_MODEL", "text-embedding-3-small")
    )

 
    store = PGVector(
        embeddings=embeddings,
        collection_name=os.getenv("PG_VECTOR_COLLECTION_NAME"),
        connection=os.getenv("DATABASE_URL"),
        use_jsonb=True,
    )

   
    results = store.similarity_search_with_score(question, k=k)

    if not results:
        contexto = ""
    else:
        # concatenar só os textos
        contexto = "\n\n".join(
            [doc.page_content for doc, score in results]
        )


        prompt = PROMPT_TEMPLATE.format(
        contexto=contexto,
        pergunta=question
    )

    return prompt
