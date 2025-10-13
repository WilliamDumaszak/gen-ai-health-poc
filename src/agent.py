#imports
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.prompts import ChatPromptTemplate

# Carrega o arquivo de variáveis de ambiente
load_dotenv()

class AGENT():
    def __init__(self):
        self.llm = ChatGroq(
        model="openai/gpt-oss-20b",
        temperature=0.2
        )

        self.search_tool = DuckDuckGoSearchRun()

        self.agent = create_react_agent(
            self.llm,
            [self.search_tool]
        )


    def run(self, user_input: str):

        contexto = (
            "Você é um assistente de IA especialista em Síndrome Respiratória Aguda Grave (SRAG). "
            "Gere relatórios com notícias recentes sobre SRAG e explique o cenário relatado. "
            f"Pergunta: {user_input}"
        )

        return self.agent.invoke({"messages": [{"role": "user", "content": contexto}]})
    
