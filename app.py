import builtins
import streamlit as str
import os
import pandas as pd
import io
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime

# Configuracoes de Conexao
load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

str.set_page_config(page_title="Sistema de Cadastro IoT", layout="wide")
str.title("Painel de Controle de Servicos IoT")

# ==========================================
# FUNCOES DE BANCO DE DADOS
# ==========================================

def buscar_servicos():
    try:
        res = supabase.table("servicos").select("id, nome, periodicidade, descricao").execute()
        return res.data if res.data else []
    except Exception as e:
        str.error(f"Erro ao buscar catalogo de servicos: {e}")
        return []

def buscar_historico_atividades():
    try:
        res = supabase.table("registros_atividades").select(
            "id, nome_obra, responsavel_tecnico, funcionarios, clima, data_inicio, data_termino, observacoes, servico_id, servicos(nome)"
        ).order("data_inicio", desc=True).execute()
        return res.data if res.data else []
    except Exception as e:
        str.error(f"Erro ao buscar historico de atividades: {e}")
        return []

def buscar_fotos_registro(registro_id):
    try:
        res = supabase.table("evidencias_fotos").select("url_storage").eq("registro_id", registro_id).execute()
        return [foto['url_storage'] for foto in res.data] if res.data else []
    except Exception as e:
        return []

def excluir_registro_completo(registro_id):
    try:
        supabase.table("evidencias_fotos").delete().eq("registro_id", registro_id).execute()
        resposta = supabase.table("registros_atividades").delete().eq("id", registro_id).execute()
        
        if resposta.data and len(resposta.data) > 0:
            return True
        else:
            str.error("Falha na exclusao: O registro nao foi localizado no banco de dados ou a operacao foi rejeitada.")
            return False
    except Exception as e:
        str.error(f"Erro critico durante a exclusao no banco de dados: {e}")
        return False

def gerar_excel(dados_dict_list):
    df = pd.DataFrame(dados_dict_list)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Historico')
        worksheet = writer.sheets['Historico']
        for i, col in enumerate(df.columns):
            # Utilizacao de builtins.str para evitar o sombreamento pelo alias 'str' do Streamlit
            max_len = max(df[col].astype(builtins.str).map(len).max(), len(col)) + 2
            worksheet.set_column(i, i, max_len)
    return output.getvalue()

# Inicializacao de dados relacionais
servicos_disponiveis = buscar_servicos()
opcoes_servicos = {s['nome']: s['id'] for s in servicos_disponiveis}
opcoes_clima = ["Ensolarado", "Parcialmente Nublado", "Nublado", "Chuvoso", "Tempestade Severa", "Neblina"]
historico_geral = buscar_historico_atividades()

tab_registro, tab_lista = str.tabs(["Registrar Atividade da Obra", "Historico e Gerenciamento"])

# ==========================================
# ABA 1: FORMULARIO LIVRE COM STATUS VISUAL
# ==========================================
with tab_registro:
    str.header("Acompanhamento e Registro de Obras")
    
    obras_existentes = list(set([h.get("nome_obra") for h in historico_geral if h.get("nome_obra") and h.get("nome_obra") != "Obra Nao Identificada"]))
    
    str.markdown("### Identificacao da Obra / Trecho")
    opcao_obra = str.selectbox("Selecione uma obra em andamento ou inicie uma nova:", ["-- Iniciar Nova Obra --"] + obras_existentes)
    
    if opcao_obra == "-- Iniciar Nova Obra --":
        obra_alvo = str.text_input("Digite o nome ou identificador da Obra (Ex: Rua A - Lote 5):")
    else:
        obra_alvo = opcao_obra

    str.divider()

    if obra_alvo:
        historico_desta_obra = [h for h in historico_geral if h.get("nome_obra") == obra_alvo]
        etapas_concluidas = [h["servicos"]["nome"] for h in historico_desta_obra if h.get("servicos")]
        
        str.markdown(f"### Status Atual da Obra: **{obra_alvo}**")
        str.caption("Verifique o cronograma executado neste trecho.")
        
        col_s1, col_s2, col_s3 = str.columns(3)
        with col_s1:
            if "Escavacao para rede de drenagem" in etapas_concluidas:
                str.info("Fase 1: Escavacao (Concluida)")
            else:
                str.warning("Fase 1: Escavacao (Pendente)")
        with col_s2:
            if "Servico de terraplanagem" in etapas_concluidas:
                str.info("Fase 2: Terraplanagem (Concluida)")
            else:
                str.warning("Fase 2: Terraplanagem (Pendente)")
        with col_s3:
            if "Servico de pavimentacao asfaltica" in etapas_concluidas:
                str.info("Fase 3: Pavimentacao (Concluida)")
            else:
                str.warning("Fase 3: Pavimentacao (Pendente)")

        str.markdown("<br>", unsafe_allow_html=True)

        with str.form("registro_servico"):
            str.markdown("### Registro de Execucao")
            servico_selecionado = str.selectbox("Selecione qual Servico/Etapa deseja registrar agora:", options=list(opcoes_servicos.keys()))
            
            col1, col2 = str.columns(2)
            with col1:
                responsavel = str.text_input("Nome do Responsavel Tecnico pela Etapa")
            with col2:
                funcionarios = str.text_input("Equipe (separados por virgula)")

            col3, col4, col5 = str.columns(3)
            with col3:
                data_inicio = str.date_input("Data de Inicio da Etapa")
            with col4:
                data_termino = str.date_input("Data de Termino da Etapa")
            with col5:
                clima = str.selectbox("Condicao Climatica predominante", options=opcoes_clima)
                
            observacao = str.text_area("Observacoes da Execucao desta Etapa")
            fotos_anexadas = str.file_uploader("Anexar Fotos desta Etapa", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)
            
            submeter = str.form_submit_button("Finalizar Etapa e Salvar", use_container_width=True)

        if submeter:
            if not responsavel:
                str.warning("O nome do responsavel tecnico e obrigatorio.")
            elif not fotos_anexadas:
                str.warning("Por favor, anexe ao menos uma foto desta etapa.")
            else:
                with str.spinner("Salvando dados..."):
                    try:
                        dados_registro = {
                            "nome_obra": obra_alvo,
                            "servico_id": opcoes_servicos[servico_selecionado],
                            "responsavel_tecnico": responsavel,
                            "funcionarios": funcionarios,
                            "clima": clima,
                            # Utilizacao de strftime para evitar a chamada do modulo 'str' como funcao
                            "data_inicio": data_inicio.strftime("%Y-%m-%d"),
                            "data_termino": data_termino.strftime("%Y-%m-%d"),
                            "observacoes": observacao
                        }
                        
                        res_registro = supabase.table("registros_atividades").insert(dados_registro).execute()
                        registro_id = res_registro.data[0]['id']
                        
                        for idx, foto in enumerate(fotos_anexadas):
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            extensao = foto.name.split('.')[-1]
                            nome_arquivo = f"{registro_id}_foto_{idx}_{timestamp}.{extensao}"
                            caminho_arquivo = f"evidencias/{nome_arquivo}"
                            
                            supabase.storage.from_("fotos_servicos").upload(
                                path=caminho_arquivo,
                                file=foto.getvalue(),
                                file_options={"content-type": f"image/{extensao}"}
                            )
                            
                            url_foto = supabase.storage.from_("fotos_servicos").get_public_url(caminho_arquivo)
                            supabase.table("evidencias_fotos").insert({
                                "registro_id": registro_id,
                                "url_storage": url_foto
                            }).execute()
                        
                        str.success(f"Servico '{servico_selecionado}' registrado com sucesso.")
                        str.rerun() 
                        
                    except Exception as e:
                        str.error(f"Erro critico ao salvar os dados: {e}")

# ==========================================
# ABA 2: LISTAS, HISTORICO E GERENCIAMENTO
# ==========================================
with tab_lista:
    str.header("Visualizacao e Historico de Cadastros")
    
    if historico_geral:
        dados_formatados = []
        mapa_registros = {} 
        opcoes_selecao = {}
        
        for h in historico_geral:
            id_reg = h["id"]
            obra = h.get("nome_obra", "Nao Identificada")
            nome_serv = h["servicos"]["nome"] if h.get("servicos") else "Nao identificado"
            data_ini = h["data_inicio"]
            resp = h["responsavel_tecnico"]
            
            mapa_registros[id_reg] = h
            rotulo_amigavel = f"Obra: {obra} | {nome_serv} ({data_ini}) [ID: {id_reg[:8]}]"
            opcoes_selecao[rotulo_amigavel] = id_reg
            
            dados_formatados.append({
                "Nome da Obra": obra,
                "Servico Executado": nome_serv,
                "Resp. Tecnico": resp,
                "Equipe": h.get("funcionarios", "-"),
                "Clima": h.get("clima", "-"),
                "Inicio": data_ini,
                "Termino": h["data_termino"],
                "Observacoes": h["observacoes"],
                "ID Sistema": id_reg
            })
            
        str.subheader("Historico Completo de Obras e Servicos")
        str.dataframe(dados_formatados, use_container_width=True, hide_index=True)
        
        excel_file = gerar_excel(dados_formatados)
        str.download_button(
            label="Exportar Relatorio para Excel (.xlsx)",
            data=excel_file,
            file_name=f"Relatorio_Obras_{datetime.now().strftime('%d_%m_%Y')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary"
        )
        
        str.markdown("---")
        
        str.subheader("Edicao e Gerenciamento de Servicos Salvos")
        
        if "registro_selecionado" not in str.session_state:
            str.session_state.registro_selecionado = "-- Escolha um registro do historico --"
            
        lista_opcoes = ["-- Escolha um registro do historico --"] + list(opcoes_selecao.keys())
        
        if str.session_state.registro_selecionado not in lista_opcoes:
            str.session_state.registro_selecionado = "-- Escolha um registro do historico --"

        selecionado = str.selectbox(
            "Escolha o registro para Editar, Ver Fotos ou Remover:", 
            options=lista_opcoes,
            key="registro_selecionado"
        )
        
        if selecionado != "-- Escolha um registro do historico --":
            id_real = opcoes_selecao[selecionado]
            registro_atual = mapa_registros[id_real]
            fotos_existentes = buscar_fotos_registro(id_real)
            
            col_edicao, col_exclusao = str.columns([2, 1])
            
            with col_edicao:
                str.markdown("### Editar Dados do Servico")
                
                if fotos_existentes:
                    str.caption("Fotos vinculadas a este servico:")
                    colunas_fotos = str.columns(3)
                    for i, url_img in enumerate(fotos_existentes):
                        with colunas_fotos[i % 3]:
                            str.image(url_img, use_container_width=True)
                else:
                    str.info("Nenhuma foto encontrada.")

                with str.form("form_efetivo_edicao"):
                    edit_obra = str.text_input("Identificacao da Obra", value=registro_atual.get("nome_obra", ""))
                    
                    nome_servico_atual = registro_atual["servicos"]["nome"] if registro_atual.get("servicos") else list(opcoes_servicos.keys())[0]
                    idx_servico = list(opcoes_servicos.keys()).index(nome_servico_atual) if nome_servico_atual in opcoes_servicos else 0
                    
                    edit_servico = str.selectbox("Modificar Servico Executado", options=list(opcoes_servicos.keys()), index=idx_servico)
                    edit_responsavel = str.text_input("Responsavel Tecnico", value=registro_atual["responsavel_tecnico"])
                    edit_funcionarios = str.text_input("Equipe", value=registro_atual.get("funcionarios", ""))
                    
                    col_dt1, col_dt2, col_dt3 = str.columns(3)
                    with col_dt1:
                        edit_inicio = str.date_input("Inicio", value=datetime.strptime(registro_atual["data_inicio"], "%Y-%m-%d").date())
                    with col_dt2:
                        edit_termino = str.date_input("Termino", value=datetime.strptime(registro_atual["data_termino"], "%Y-%m-%d").date())
                    with col_dt3:
                        idx_clima = opcoes_clima.index(registro_atual["clima"]) if registro_atual["clima"] in opcoes_clima else 0
                        edit_clima = str.selectbox("Clima", options=opcoes_clima, index=idx_clima)
                    
                    edit_observacao = str.text_area("Observacoes", value=registro_atual["observacoes"])
                    novas_fotos = str.file_uploader("Selecione mais imagens para anexar", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)
                    
                    btn_salvar = str.form_submit_button("Salvar Alteracoes e Fotos")
                    
                    if btn_salvar:
                        with str.spinner("Atualizando dados..."):
                            dados_atualizados = {
                                "nome_obra": edit_obra,
                                "servico_id": opcoes_servicos[edit_servico],
                                "responsavel_tecnico": edit_responsavel,
                                "funcionarios": edit_funcionarios,
                                "clima": edit_clima,
                                "data_inicio": edit_inicio.strftime("%Y-%m-%d"),
                                "data_termino": edit_termino.strftime("%Y-%m-%d"),
                                "observacoes": edit_observacao
                            }
                            supabase.table("registros_atividades").update(dados_atualizados).eq("id", id_real).execute()
                            
                            if novas_fotos:
                                for idx, foto in enumerate(novas_fotos):
                                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                    extensao = foto.name.split('.')[-1]
                                    nome_arquivo = f"{id_real}_foto_nova_{idx}_{timestamp}.{extensao}"
                                    caminho_arquivo = f"evidencias/{nome_arquivo}"
                                    
                                    supabase.storage.from_("fotos_servicos").upload(
                                        path=caminho_arquivo, file=foto.getvalue(), file_options={"content-type": f"image/{extensao}"}
                                    )
                                    url_nova_foto = supabase.storage.from_("fotos_servicos").get_public_url(caminho_arquivo)
                                    supabase.table("evidencias_fotos").insert({"registro_id": id_real, "url_storage": url_nova_foto}).execute()

                            str.success("Registro modificado com sucesso.")
                            str.rerun()
            
            with col_exclusao:
                str.markdown("### Zona de Exclusao")
                str.warning("A exclusao removera as fotos e o registro permanentemente do historico da obra.")
                confirmar_delecao = str.checkbox("Eu desejo apagar permanentemente este registro.")
                btn_deletar = str.button("EXCLUIR REGISTRO", disabled=not confirmar_delecao, use_container_width=True)
                
                if btn_deletar:
                    with str.spinner("Removendo dados..."):
                        if excluir_registro_completo(id_real):
                            str.session_state.registro_selecionado = "-- Escolha um registro do historico --"
                            str.rerun()
    else:
        str.info("Nenhuma atividade executada ou registrada no historico ainda.")