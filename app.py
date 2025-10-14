#imports
import streamlit as st
from PIL import Image
import sys
import os
from pathlib import Path


# Ajusta o path para importar módulos de níveis superiores
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.tools import TOOLS
from src.agent import AGENT

tools=TOOLS()
agent=AGENT()

# --- Execução direta ---
if __name__ == "__main__":

    ########## App Web ##########

    # Configuração da página do Streamlit
    st.set_page_config(page_title="Agente de saúde", page_icon="⚕️", layout="wide")

    # Título principal
    st.title("Agente de Saúde com foco em SRAG ⚕️")

    # Interface principal
    st.header("Atualização Epidemiológica em Tempo Real sobre Síndrome Respiratória Aguda Grave (SRAG)")

    # Executa o Agente de IA

    user_input = st.text_input("Solicite seu relatório sobre SRAG:")

    if st.button("Solicitar Relatório"):

        if "SRAG" not in user_input.upper():
            st.warning("Pergunte apenas sobre SRAG ou indicadores relacionados.")
            raise ValueError("Pergunte apenas sobre SRAG ou indicadores relacionados.")
               
        resposta = agent.run(user_input)

        log=agent.log_agent_interaction(user_input, resposta)

        #st.write(resposta[message])
        ultima_mensagem = resposta["messages"][-1]
        st.markdown(ultima_mensagem.content)

        # Renderiza os gráficos
        st.subheader("Visualização dos Dados, histórico dos Últimos 30 Dias e 12 Meses")
        daily_path, monthly_path = tools.tool_charts()
        image1 = Image.open(daily_path)
        image2 = Image.open(monthly_path)
        st.image(image1, caption="Gráfico diário dos últimos 30 dias", use_column_width=True)
        st.image(image2, caption="Gráfico mensal dos últimos 12 meses", use_column_width=True)
