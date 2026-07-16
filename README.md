# projetoIoT
Projeto de extensão

## Sistema RDO — Relatório Diário de Obras
# Sistema web completo para gestão de obras civis, com cadastro, acompanhamento diário de progresso, anexos fotográficos e geração automática de planilhas.

📌 Visão Geral
O Sistema RDO foi desenvolvido como projeto de extensão universitária em parceria com equipe multidisciplinar. O objetivo era resolver um problema real: empresas de construção civil perdiam horas retrabalhando dados de obras em planilhas manuais e relatórios em papel, com risco de extravio de informações críticas.

A solução centraliza todo o fluxo de registros diários de obra em uma plataforma web acessível de qualquer dispositivo com internet.

🎯 Problema que Resolve

Antes do sistema, o fluxo de registro de obras era:

❌ Relatórios diários preenchidos em papel
❌ Fotos tiradas e armazenadas em dispositivos individuais
❌ Planilhas Excel desatualizadas e fragmentadas
❌ Falta de histórico centralizado
❌ Dificuldade para gerar relatórios gerenciais
❌ Perda de informações por extravio de papel


Depois do sistema:

✅ Registro diário digital, georreferenciado e com foto
✅ Histórico permanente na nuvem
✅ Geração automática de planilhas
✅ Acesso multi-usuário com diferentes permissões
✅ Visão consolidada de todas as obras em andamento



🛠 Stack Tecnológica


Camada
Tecnologia
Por que foi escolhida
Front-end	Streamlit	Framework Python que permite criar interfaces web completas sem conhecimento profundo de HTML/CSS/JS
Back-end	Python 3.11	Linguagem principal do time, com ecossistema rico para automação e dados
Banco de dados	Supabase (PostgreSQL)	Banco gerenciado em nuvem, com auth, storage e real-time integrados
Hospedagem	Streamlit Cloud	Deploy gratuito e nativo para apps Streamlit, com CI/CD via GitHub
Automação	Pandas + OpenPyXL	Geração de planilhas Excel a partir dos dados do banco

✨ Funcionalidades Principais

👥 Multi-usuário com Permissões
Admin: acesso total ao sistema, gestão de usuários e obras
Engenheiro/Operador: cadastra e edita relatórios diários de obras
Visualizador: apenas consulta e exporta dados

🏗 Gestão de Obras
Cadastro de novas obras (nome, localização, cliente, responsável, datas)
Edição e arquivamento de obras concluídas
Listagem com filtros por status, cliente e período
Dashboard com métricas consolidadas

📝 Relatório Diário de Obras (RDO)
Formulário estruturado com: data, condições climáticas, equipe, atividades realizadas, dificuldades, materiais usados
Anexo de múltiplas fotos por relatório (armazenadas no Supabase Storage)
Histórico cronológico por obra
Edição e versionamento

📊 Geração Automática de Planilhas
Exportação em Excel (.xlsx) com dados filtrados
Formatação automática (cabeçalhos, cores, largura de colunas)
Agregação por obra, período ou atividade
Download direto pelo navegador

📈 Dashboard Visual
Indicadores em tempo real (total de obras ativas, relatórios no mês, fotos cadastradas)
Gráficos interativos (Plotly) com evolução diária, distribuição por tipo de atividade
Filtros por período, obra e responsável
