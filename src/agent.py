#imports
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from langchain_community.tools.tavily_search import TavilySearchResults

import json
import os
from datetime import datetime
from src.tools import TOOLS

# Carrega o arquivo de variáveis de ambiente
load_dotenv()

class AGENT():
    def __init__(self):
        self.llm = ChatGroq(
        model="openai/gpt-oss-20b",
        temperature=0.2
        )

        self.search_tool = TavilySearchResults(max_results=5)

        self.tools=TOOLS()

        self.agent = create_react_agent(
            self.llm,
            [self.search_tool]
        )

    def log_agent_interaction(self, input_msg, output_msg):
        os.makedirs("logs", exist_ok=True)
        output_text = output_msg.get("output", str(output_msg))
        with open("logs/agent_log.jsonl", "a") as f:
            f.write(json.dumps({
                "timestamp": datetime.now().isoformat(),
                "input": input_msg,
                "output": output_text
            }) + "\n")


    def run(self, user_input: str):

        metrics=self.tools.tool_metrics()

        contexto = (
            "Você é um assistente de IA especialista em relatórios sobre Síndrome Respiratória Aguda Grave (SRAG). "
            f"Aqui estão métricas extraídas da base OpenDataSUS: {metrics}\n\n"
            "Busque noticias recentes sobre SRAG, usando o TavilySeatch, que ajudem a compor a sua analise.\n"
            "Sempre cite as fontes.\n"
            f"Pergunta: {user_input}"
        )

        return self.agent.invoke({"messages": [{"role": "user", "content": contexto}]})
    
