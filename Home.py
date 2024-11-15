import pandas as pd
import streamlit as st
from functions import *

# Instancia a classe dados
f = dados()

# Configura a página do Streamlit
st.set_page_config(
    page_title='Carla | Salgados',
    page_icon='🥟',
    layout= 'wide'
)

# Define as colunas na interface
cols1, cols2 = st.columns([0.25, 0.7])

@st.cache_data
def carregando():
    """
    Carrega os dados dos pedidos, clientes e produtos do banco de dados.
    Essa função é armazenada em cache para melhorar o desempenho.
    
    Retorna:
    DataFrame: DataFrame com os dados dos pedidos.
    DataFrame: DataFrame com os dados dos clientes.
    numpy.ndarray: Lista de produtos.
    """
    df_pedidos = f.df_trasformation("SELECT * FROM pedidos")
    df_clientes = f.df_trasformation("SELECT * FROM clientes")
    produtos = f.produtos()
    return df_pedidos, df_clientes, produtos

def clear_cache():
    """
    Limpa o cache da função carregando.
    """
    carregando.clear()

# Carrega os dados e os armazena no estado da sessão do Streamlit
df_pedidos, df_clientes, produtos = carregando()
st.session_state['DFS'] = df_pedidos, df_clientes, produtos

# Container para informações do cliente
with cols1.container(border=True):
    # Este bloco `with` cria um container na coluna 1 para inserir informações do cliente.
    col1, col2 = st.columns(2)
    col2.subheader('Cliente')
    col1.image('mulher.png', width=80)
    telefone = st.text_input('Telefone:')
    busca_nome = f.name_client(telefone)
    nome = st.text_input('Nome:', busca_nome)

    @st.dialog('Cadastrar Cliente')
    def cad_client(tel=None):
        """
        Função para cadastrar um novo cliente se ele não estiver no sistema.
        
        Parâmetros:
        tel (str): Número de telefone do cliente.
        """
        st.subheader('Ops, parece que este cliente ainda não está cadastrado!')
        telefone_cad = st.text_input('Telefone:', value=tel)
        nome_cad = st.text_input('Nome:')
        salvar = st.button('Salvar', use_container_width=True)
        if salvar:
            f.cadast_client(tel=telefone_cad, nom=nome_cad)
            clear_cache()
            st.rerun()

# Verifica se o telefone do cliente já está cadastrado
if telefone:
    if f.verfi_client(telefone):
        cad_client(telefone)

with cols1.container(border=True):
    # Este bloco `with` cria um container na coluna 1 para inserir dados de entrega.
    st.subheader('Dados de entrega:')
    dt_entrega = st.date_input('Selecione a data:')
    hr_entrega = st.time_input('Insira a Hora:')
    tp_entrega = st.radio('Selecione a forma de entrega:', ['Retirar', 'Entregar'], horizontal=True)
    dt_hr = str(dt_entrega) + " " + str(hr_entrega)
    

with cols2.container(border=True, height=623):
    # Este bloco `with` cria um container na coluna 2 para descrever o pedido do cliente.
    st.subheader('Descreva abaixo o pedido do cliente:👇')
    st.markdown('Você pode adicionar mais produtos clicando em "Adicionar".')

    @st.dialog('Concluído')
    def pedido_salvo():
        """
        Função para exibir um diálogo de confirmação de pedido salvo.
        """
        st.subheader('Pedido salvo com sucesso!')

    # Inicializa o estado da sessão para armazenar os pedidos
    if 'pedidos' not in st.session_state:
        st.session_state['pedidos'] = [{}]

    def adicionar_pedido():
        """
        Adiciona um novo pedido ao estado da sessão.
        """
        st.session_state['pedidos'].append({
            'produto': '',
            'sabor': '',
            'quantidade': 100
        })

    def remover_pedido(index):
        """
        Remove o pedido do índice especificado da lista de pedidos.
        Não remove se existir apenas um elemento na lista.
        """
        if len(st.session_state['pedidos']) > 1 and 0 <= index < len(st.session_state['pedidos']):
            st.session_state['pedidos'].pop(index)

    def exibir_pedidos():
        """
        Exibe os pedidos na interface para o usuário, com a opção de remover pedidos.
        """
        for i, pedido in enumerate(st.session_state['pedidos']):
            cols = st.columns([0.3, 0.3, 0.3, 0.1])
            with cols[0]:
                # Cria um selectbox para selecionar o produto
                st.session_state['pedidos'][i]['produto'] = st.selectbox(
                    'Produto', produtos, key=f'produto_{i}')
            with cols[1]:
                # Cria um selectbox para selecionar o sabor
                st.session_state['pedidos'][i]['sabor'] = st.selectbox(
                    'Sabor', ['Sabor 1', 'Sabor 2', 'Sabor 3'], key=f'sabor_{i}')
            with cols[2]:
                # Cria um number_input para selecionar a quantidade
                st.session_state['pedidos'][i]['quantidade'] = st.number_input(
                    'Quantidade', value=100, min_value=1, key=f'quantidade_{i}')
            with cols[3]:
                # Cria um botão para remover o pedido
                if st.button('❌ Remover o produto acima', key=f'remove_{i}', on_click=remover_pedido, args=(i,),use_container_width=True):
                    pass
            st.divider()
        
    exibir_pedidos()
    add_button = st.button('➕ Adicionar', use_container_width=True)
    save_button = st.button('💾 Salvar Pedido', use_container_width=True)
    
    with st.expander('Resumo do Pedido', icon='🧾'):
        # Este bloco `with` cria um expansor que exibe o resumo do pedido.
        df_resumo, preco, qnt = f.resumo(st.session_state['pedidos'])
        st.image("Logo_v1.png")
        st.markdown("Este é um breve resumo do seu pedido 👇")
        st.dataframe(df_resumo,
                     column_config={
                    'Valor': st.column_config.NumberColumn(
                        "💵 Valor",
                        format="R$%.2f"
                        )
                     },
                     use_container_width=True)
        st.divider()
        st.markdown(
        f"""
        <div style="text-align: center; font-size: 18px;">
            Quantidade: <span style="color:orange; font-weight: bold;">{qnt}</span> &nbsp;&nbsp;|&nbsp;&nbsp; Valor total: <span style="color:green; font-weight: bold;">R$ {preco}</span>
        </div>
        """,
        unsafe_allow_html=True
        )   
        st.divider()
    #COndicoes da camada
    if add_button:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      
        adicionar_pedido()

    if save_button:
        pedido_salvo()
