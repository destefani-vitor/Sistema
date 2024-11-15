import pandas as pd
import mysql.connector

class dados():
    def __init__(self) -> None:
        """
        Inicializa a conexão com o banco de dados MySQL usando as credenciais fornecidas.
        """
        self.conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='sistema_salgados'
            )
    
    def df_trasformation(self,query):
        """
        Executa uma consulta SQL fornecida e retorna o resultado como um DataFrame do Pandas.
        
        Parâmetros:
        query (str): A consulta SQL a ser executada.
        
        Retorna:
        DataFrame: O resultado da consulta em formato de DataFrame.
        """
        cursor = self.conn.cursor()
        cursor.execute(query)
        colun = [desc[0] for desc in cursor.description]
        result = cursor.fetchall()
        df = pd.DataFrame(result, columns=colun)
        cursor.close()
        return df
              
    def produtos(self):
        """
        Retorna uma lista dos produtos únicos da tabela 'produtos'.
        
        Retorna:
        numpy.ndarray: Lista de produtos únicos.
        """
        produtos = self.df_trasformation('SELECT produto FROM produtos')
        list_produtos = produtos['produto'].unique()
        return list_produtos

    def verfi_client(self,telefone):
        """
        Verifica se um número de telefone já está cadastrado na tabela 'clientes'.
        
        Parâmetros:
        telefone (str): O número de telefone a ser verificado.
        
        Retorna:
        bool: True se o telefone não estiver cadastrado, False caso contrário.
        """
        query = f"SELECT count(nome) as contagem FROM clientes WHERE numero_cel = '{telefone}'"
        df = self.df_trasformation(query)
        return df['contagem'].iloc[0] == 0
    
    def name_client(self,telefone):
        """
        Retorna o nome do cliente com base no número de telefone fornecido.
        
        Parâmetros:
        telefone (str): O número de telefone do cliente.
        
        Retorna:
        str: O nome do cliente, ou None se o cliente não for encontrado.
        """
        query = f"SELECT nome FROM clientes WHERE numero_cel = '{telefone}'"
        try:
            df = self.df_trasformation(query)
            nome = df['nome'].item()
        except:
            nome = None
        return nome  
            
    def cadast_client(self,tel,nom):
        """
        Cadastra um novo cliente na tabela 'clientes'.
        
        Parâmetros:
        tel (str): O número de telefone do cliente.
        nom (str): O nome do cliente.
        
        Retorna:
        bool: False se o cadastro for bem-sucedido, True se ocorrer um erro.
        """
        cursor = self.conn.cursor()
        dado = (tel,nom)
        try:
            cursor.execute(f"INSERT INTO Clientes (numero_cel, nome) VALUES {dado};")
            cursor.close()
            return False
        except:
            return True

    def cadast_pedido(self,dados,produtos,telefone,dt_hr,tp_entrega):
        """
        Cadastra um novo pedido na tabela 'produto'.
        
        Parâmetros:
        dados (dict): Dados adicionais do pedido.
        produtos (list): Lista de produtos no pedido.
        telefone (str): Número de telefone do cliente.
        dt_hr (str): Data e hora do pedido.
        tp_entrega (str): Tipo de entrega (ex: delivery ou retirada).
        
        Retorna:
        bool: True se o cadastro for bem-sucedido, False se ocorrer um erro.
        """
        cursor = self.conn.cursor()
        produtos = pd.DataFrame(produtos)
        df_dados = pd.DataFrame({
                                'numero_cel': [telefone],
                                'data_hora' : [dt_hr],
                                'tp_entrega': [tp_entrega]
                                }) 
        df_dados = pd.concat([dados] * len(produtos), ignore_index=True)
        pedido = pd.concat([produtos, dados], axis=1)
        dados_insert = [tuple(row) for row in pedido.to_numpy()]
        sql = """insert into produto (numero_cel,data_hora,produto,sabor,quantidade,finalizado) values (%s, %s, %s, %s, %s, %s)"""
        try:
            cursor.executemany(sql,dados_insert)
            self.conn.commit()
            cursor.close()
            return True
        except: 
            return False
        
    def resumo(self,st):
        """
        Gera um resumo do pedido, calculando os valores totais e quantidades.
        
        Parâmetros:
        st (list): Lista de dicionários contendo os itens do pedido.
        
        Retorna:
        tuple: Um DataFrame com o resumo do pedido, o valor total e a quantidade total.
        """
        df_vlr = self.df_trasformation("select * from produtos")
        df = pd.DataFrame(st)
        df = df.merge(df_vlr,how='left',on='produto')
        df['preco'] = df.apply(lambda df: df['preco']/100 if df['produto'] != "Mini Sanduíche" else df['preco'],axis=1)
        df['Valor'] = df['preco'] * df['quantidade']
        df['Valor'] = df['Valor'].astype(float)
        df = df[['produto','quantidade','Valor']]
        df.rename(columns={'quantidade': 'Quantidade','produto' : 'Produto'}, inplace=True)
        df = df.groupby(by='Produto').sum()
        vlr = df['Valor'].sum()
        qnt = df['Quantidade'].sum()
        return df, vlr, qnt
