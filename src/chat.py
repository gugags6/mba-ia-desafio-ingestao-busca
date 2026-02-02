import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from search import search_prompt


def main():
    load_dotenv()

    
    if not os.getenv("OPENAI_API_KEY"):
        print(" OPENAI_API_KEY não configurada no .env")
        return
   
    llm = ChatOpenAI(
        model=os.getenv("OPENAI_LLM_MODEL", "gpt-5-nano"),
        temperature=0
    )

    print("\n Chat Semântico com PDF")
    print("Digite 'sair' para encerrar.\n")


    while True:
        question = input("PERGUNTA: ").strip()

        if not question:
            print("Digite uma pergunta válida.\n")
            continue

        if question.lower() == "sair":
            print("\nEncerrando chat...")
            break

  
        prompt = search_prompt(question)

        if not prompt:
            print(" Não foi possível gerar o prompt.")
            continue


        response = llm.invoke(prompt)

     
        print("\nRESPOSTA:", response.content)
        print("\n" + "-" * 60)


if __name__ == "__main__":
    main()
