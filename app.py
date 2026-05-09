import streamlit as st
import os
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime

# 1. Configurações de Conexão (Reutilizando sua lógica validada)
load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

st.set_page_config(page_title="Sistema de Cadastro IoT", page_icon="🛠️")

st.title("🛠️ Registro de Serviços IoT")

# 2. Busca de Serviços Cadastrados (Para o dropdown)
def buscar_servicos():
    try:
        res = supabase.table("servicos").select("id, nome").execute()
        return res.data if res.data else []
    except Exception as e:
        st.error(f"Erro ao conectar com a tabela 'servicos': {e}")
        return []

servicos_disponiveis = buscar_servicos()
opcoes = {s['nome']: s['id'] for s in servicos_disponiveis}

# 3. Interface de Usuário
with st.form("registro_servico"):
    st.subheader("Novo Registro de Atividade")
    
    servico_nome = st.selectbox("Selecione o Serviço", options=list(opcoes.keys()))
    observacao = st.text_area("Descrição do serviço realizado")
    
    # Componente de Câmera
    foto_capturada = st.camera_input("Bater foto do serviço realizado")
    
    submeter = st.form_submit_button("Finalizar e Salvar")

# 4. Lógica de Envio
if submeter:
    if foto_capturada and servico_nome:
        with st.spinner("Enviando dados para a nuvem..."):
            try:
                # Gerar nome único para a foto
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                nome_arquivo = f"foto_{timestamp}.jpg"
                caminho_arquivo = f"evidencias/{nome_arquivo}"
                
                # Upload para o Storage
                foto_bytes = foto_capturada.getvalue()
                supabase.storage.from_("fotos_servicos").upload(
                    path=caminho_arquivo,
                    file=foto_bytes,
                    file_options={"content-type": "image/jpeg"}
                )
                
                # Pegar URL Pública
                url_foto = supabase.storage.from_("fotos_servicos").get_public_url(caminho_arquivo)
                
                # Salvar no Banco SQL
                supabase.table("registros_atividades").insert({
                    "servico_id": opcoes[servico_nome],
                    "url_storage": url_foto,
                    "observacoes": observacao
                }).execute()
                
                st.success(f"Serviço '{servico_nome}' registrado com sucesso!")
                st.balloons()
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")
    else:
        st.warning("Por favor, capture uma foto antes de salvar.")