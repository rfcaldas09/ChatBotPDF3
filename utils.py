from pathlib import Path
import streamlit as st
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores.faiss import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_openai.chat_models import ChatOpenAI
from langchain.docstore.document import Document
import openai
from dotenv import load_dotenv
from pdf2image import convert_from_path
from PyPDF2 import PdfReader
from multiprocessing import cpu_count
import fitz  # PyMuPDF
import os
from configuracao import *

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

PASTA_ARQUIVOS = Path('arquivos')
os.makedirs(PASTA_ARQUIVOS, exist_ok=True)  # Cria o diretório se não existir

def extract_text_from_pdf(pdf_path):
    document = fitz.open(pdf_path)
    text = ""
    for page in document:
        text += page.get_text("text")
    return text

def importacao_documentos():
    documentos = []
    for arquivo in PASTA_ARQUIVOS.glob('*.pdf'):
        texto = extract_text_from_pdf(str(arquivo))

        doc = Document(page_content=texto, metadata={'source': str(arquivo)})
        documentos.append(doc)
    return documentos

def split_de_documentos(documentos):
    recur_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=500,
        separators=[".", " ", ""]
    )
    documentos = recur_splitter.split_documents(documentos)

    
    for i, doc in enumerate(documentos):
        doc.metadata['source'] = doc.metadata['source'].split('/')[-1]
        doc.metadata['doc_id'] = i
    return documentos

def cria_vector_store(documentos):
    embedding_model = OpenAIEmbeddings()

    vector_store = FAISS.from_documents(
        documents=documentos,
        embedding=embedding_model
    )
    return vector_store

def obter_pagina_da_resposta(resposta):
    if 'source' in resposta:
        return resposta['source']
    else:
        texto_resposta = resposta['answer']
        paginas_relevantes = identificar_paginas_por_texto(texto_resposta)
        return paginas_relevantes

def identificar_paginas_por_texto(texto_resposta):
    paginas_texto = obter_paginas_texto()
    paginas_relevantes = []
    for numero_pagina, texto_pagina in paginas_texto.items():
        if texto_resposta in texto_pagina:
            paginas_relevantes.append(numero_pagina)
    return paginas_relevantes

def obter_paginas_texto():
    pdf_path = r'C:\Users\nanda\OneDrive\Área de Trabalho\Meus Projetos Python\catalogoProdutos2.pdf'  # Caminho do seu PDF
    doc = fitz.open(pdf_path)
    paginas_texto = {i + 1: page.get_text("text") for i, page in enumerate(doc)}
    return paginas_texto

def cria_chain_conversa():
    documentos = importacao_documentos()
    documentos = split_de_documentos(documentos)
    vector_store = cria_vector_store(documentos)

    chat = ChatOpenAI(model=get_config('model_name'),
                      temperature=0,
                      max_tokens=4095)
    memory = ConversationBufferMemory(k=5,
                                      return_messages=True,
                                      memory_key='chat_history',
                                      output_key='answer')

    retriever = vector_store.as_retriever(
        search_type=get_config('retrieval_search_type'),
        search_kwargs=get_config('retrieval_kwargs')
    )

    prompt = PromptTemplate.from_template(get_config('prompt'))
    chat_chain = ConversationalRetrievalChain.from_llm(
        llm=chat,
        memory=memory,
        retriever=retriever,
        return_source_documents=True,
        verbose=True,
        combine_docs_chain_kwargs={'prompt': prompt}
    )

    st.session_state['chain'] = chat_chain

def exibir_resposta_com_paginas(resposta, paginas_relevantes):
    st.markdown(resposta['answer'])
    if paginas_relevantes:
        st.markdown(f"Informação obtida nas páginas: {', '.join(map(str, paginas_relevantes))}")

