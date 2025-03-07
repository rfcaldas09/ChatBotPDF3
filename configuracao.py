# -*- coding: UTF-8 -*-

import streamlit as st

MODEL_NAME = 'gpt-3.5-turbo-0125'
RETRIEVAL_SEARCH_TYPE = 'mmr'
RETRIEVAL_KWARGS = {"k": 10, "fetch_k": 30}

PROMPT = '''Voce e um Chatbot que auxilia na interpretacao 
de documentos que lhe sao fornecidos. 
O documento fornece um catalogo de produtos com cores e tamanhos.
Utilize o contexto para responder as perguntas do usuario.
Se voce nao sabe a resposta, apenas diga que nao sabe e nao tente 
inventar a resposta.

Contexto:
{context}

Conversa atual:
{chat_history}
Human: {question}
AI: '''

def get_config(config_name):
    if config_name.lower() in st.session_state:
        return st.session_state[config_name.lower()]
    elif config_name.lower() == 'model_name':
        return MODEL_NAME
    elif config_name.lower() == 'retrieval_search_type':
        return RETRIEVAL_SEARCH_TYPE
    elif config_name.lower() == 'retrieval_kwargs':
        return RETRIEVAL_KWARGS
    elif config_name.lower() == 'prompt':
        return PROMPT