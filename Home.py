import time
import streamlit as st
from utils import cria_chain_conversa, PASTA_ARQUIVOS
from pathlib import Path
import fitz  # PyMuPDF

# Pasta temporária para armazenar arquivos PDF
PASTA_ARQUIVOS = Path('arquivos')
PASTA_ARQUIVOS.mkdir(exist_ok=True)


def sidebar():
    uploaded_pdfs = st.file_uploader(
        'Adicione seus arquivos PDF', 
        type=['pdf'],
        accept_multiple_files=True
    )

    if uploaded_pdfs:
        # Remove arquivos antigos apenas se novos forem carregados
        for arquivo in PASTA_ARQUIVOS.glob('*.pdf'):
            arquivo.unlink()

        # Salva os novos PDFs
        for pdf in uploaded_pdfs:
            pdf_path = PASTA_ARQUIVOS / pdf.name
            with open(pdf_path, 'wb') as f:
                f.write(pdf.getbuffer())

    label_botao = 'Inicializar ChatBot' if 'chain' not in st.session_state else 'Atualizar ChatBot'

    if st.button(label_botao, use_container_width=True):
        if not any(PASTA_ARQUIVOS.glob('*.pdf')):  # Verifica se há PDFs na pasta
            st.error('Adicione arquivos PDF para inicializar o chatbot')
        else:
            st.success('Inicializando o ChatBot...')
            cria_chain_conversa()
            st.rerun()


def obter_resposta_com_pagina(question):
    chain = st.session_state.get('chain')
    resposta = chain.invoke({'question': question})
    
    # Suponha que a IA esteja retornando também a página em que encontrou a informação
    paginas_relevantes = obter_paginas_da_resposta(resposta)  # Método fictício para pegar as páginas
    return resposta, paginas_relevantes


def obter_paginas_da_resposta(resposta):
    if 'source_documents' in resposta:
        paginas_relevantes = []
        for doc in resposta['source_documents']:
            # O campo 'source' pode conter o número da página ou o nome do arquivo
            if 'source' in doc.metadata:
                paginas_relevantes.append(doc.metadata['doc_id'])  # Pode ser o número da página ou o nome do arquivo
        return paginas_relevantes    


def obter_paginas_texto():
    """
    Retorna um dicionário contendo o conteúdo de cada página do PDF.
    A chave é o número da página e o valor é o texto extraído dessa página.
    """
    pdf_path = r'C:\Users\nanda\OneDrive\Área de Trabalho\Meus Projetos Python\catalogoProdutos2.pdf'  # Caminho do seu PDF
    doc = fitz.open(pdf_path)
    paginas_texto = {i + 1: page.get_text("text") for i, page in enumerate(doc)}
    return paginas_texto


def exibir_resposta_com_paginas(resposta, paginas_relevantes):
    """
    Exibe a resposta junto com as páginas relevantes usadas para obtê-la.
    """
    st.markdown(resposta['answer'])

    print('2222222=='+str(paginas_relevantes))
    if paginas_relevantes:
        st.markdown(f"Informação obtida nas páginas: {', '.join(map(str, paginas_relevantes))}")


def chat_window():
    st.header('🤖 Bem-vindo ao Chat PDF', divider=True)

    if 'chain' not in st.session_state:
        st.error('Faça o upload de PDFs para começar!')
        st.stop()

    chain = st.session_state['chain']
    memory = chain.memory

    mensagens = memory.load_memory_variables({})['chat_history']
    
    container = st.container()
    for mensagem in mensagens:
        chat = container.chat_message(mensagem.type)
        chat.markdown(mensagem.content)

    nova_mensagem = st.chat_input('Converse com seus documentos...')
    if nova_mensagem:
        chat = container.chat_message('human')
        chat.markdown(nova_mensagem)

        chat = container.chat_message('ai')
        chat.markdown('Gerando resposta...')
        resposta, paginas_relevantes = obter_resposta_com_pagina(nova_mensagem)
        exibir_resposta_com_paginas(resposta, paginas_relevantes)


def main():
    with st.sidebar:
        sidebar()
    chat_window()


if __name__ == '__main__':
    main()
