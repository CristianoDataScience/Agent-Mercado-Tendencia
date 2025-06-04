import os
import streamlit as st
import markdown
import pdfkit
from dotenv import load_dotenv, find_dotenv
from crewai import Agent, Task, Crew

# Carregar variáveis de ambiente
load_dotenv(find_dotenv())

# Interface
st.set_page_config(page_title="Relatório de Mercado", layout="wide")
st.title("📊 Gerador de Relatório de Mercado com IA")

# Input do usuário
sector = st.text_input("Digite o setor ou tema que deseja pesquisar:", "Melhor Projeto para se criar ou melhorar em tecnologia em 2025")

if st.button("🔍 Gerar Relatório"):
    with st.spinner("Gerando relatório com IA..."):

        # Criando os agentes
        pesquisador = Agent(
            role="Pesquisador de Mercado",
            goal="Coletar e organizar informações relevantes sobre {sector}",
            backstory="""Você é um pesquisador experiente que analisa tendências de mercado e coleta
            dados relevantes sobre {sector}. Seu trabalho é garantir que todas as informações estejam atualizadas e bem documentadas.""",
            allow_delegation=False,
            verbose=True,
        )

        analista = Agent(
            role="Analista de Tendências",
            goal="Analisar os dados do setor {sector}",
            backstory="""Você é um analista de mercado que examina os dados coletados para identificar
            tendências emergentes, oportunidades e ameaças no setor {sector}.""",
            allow_delegation=False,
            verbose=True,
        )

        redator = Agent(
            role="Redator de Relatórios",
            goal="Elaborar um relatório consolidado sobre a análise de mercado do setor {sector}.",
            backstory="""Você é um redator profissional que transforma análises de mercado em um relatório
            estruturado e compreensível para tomadores de decisão.""",
            allow_delegation=False,
            verbose=True,
        )

        # Tarefas
        coleta_dados = Task(
            description=(
                "1. Pesquisar e coletar informações atualizadas sobre {sector};"
                "2. Identificar os principais players, tendência e estatísticas do setor;"
                "3. Organizar os dados de forma clara para análise."
            ),
            expected_output="Um documento estruturado contendo dados de mercado sobre {sector}.",
            agent=pesquisador
        )

        analise_tendencias = Task(
            description=(
                "1. Examinar os dados coletados pelo Pesquisador de Mercado."
                "2. Identificar padrões, tendências emergentes e oportunidades no setor {sector}."
                "3. Elaborar uma análise detalhada destacando os principais pontos."
            ),
            expected_output="Um relatório com insights e tendências baseados nos dados do setor {sector}.",
            agent=analista
        )

        redacao_relatorio = Task(
            description=(
                "1. Usar a análise de tendência para criar um relatório detalhado sobre {sector}."
                "2. Garantir que o relatório seja bem estruturado e compreensível."
                "3. Apresentar um resumo executivo e recomendações finais."
            ),
            expected_output="Um relátório de análise de mercado em formato Markdown, pronto para leitura e apresentação.",
            agent=redator
        )

        # Crew
        crew = Crew(
            agents=[pesquisador, analista, redator],
            tasks=[coleta_dados, analise_tendencias, redacao_relatorio],
            verbose=True,
        )

        resultado = crew.kickoff(inputs={"sector": sector})

        # Exibir o relatório no Streamlit (como Markdown)
        st.subheader("📄 Relatório Gerado")
        st.markdown(str(resultado), unsafe_allow_html=True)

        # Gerar HTML e PDF
        html_content = markdown.markdown(str(resultado))
        html_path = "/tmp/relatorio.html"
        pdf_path = f"/tmp/relatorio_{sector.lower().replace(' ', '_')}.pdf"

        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        # Detectar caminho do wkhtmltopdf
        wkhtmltopdf_path = "/opt/homebrew/bin/wkhtmltopdf"  # Altere conforme necessário
        if not os.path.exists(wkhtmltopdf_path):
            st.error(f"❌ wkhtmltopdf não encontrado em {wkhtmltopdf_path}.")
        else:
            config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
            try:
                pdfkit.from_file(html_path, pdf_path, configuration=config)

                # Exibir botão de download
                with open(pdf_path, "rb") as pdf_file:
                    st.download_button(
                        label="📥 Baixar Relatório em PDF",
                        data=pdf_file,
                        file_name=f"relatorio_{sector.lower().replace(' ', '_')}.pdf",
                        mime="application/pdf"
                    )
            except Exception as e:
                st.error(f"Erro ao gerar PDF: {str(e)}")