import sqlite3 
from datetime import datetime

DB_NAME = "adega.db"

def conectar_db():
    try: 
        conn = sqlite3.connect(DB_NAME)
        return conn
    except sqlite3.Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None
    
def criar_tabela():
    conn = conectar_db()
    if conn is None:
        return
    
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo_barras TEXT UNIQUE,
        nome TEXT NOT NULL,
        preco_venda REAL N  OT NULL,
        preco_custo REAL,
        quantidade_estoque INTEGER NOT NULL,
        estoque_minimo INTEGER DEFAULT 5
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vendas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data_hora TEXT NOT NULL,
        total_venda REAL NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS itens_venda (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        venda_id INTEGER NOT NULL,
        produto_id INTEGER NOT NULL,
        quantidade INTEGER NOT NULL,
        preco_unitario_momento REAL NOT NULL,
        FOREIGN KEY (venda_id) REFERENCES vendas (id),
        FOREIGN KEY (produto_id) REFERENCES produtos (id)
    );
    """)

    conn.commit()
    conn.close()


def adicionar_produto(codigo, nome, preco_venda, preco_custo, estoque, estoque_minimo):
    conn = conectar_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO produtos (codigo_barras, nome, preco_venda, preco_custo, quantidade_estoque, estoque_minimo) VALUES (?, ?, ?, ?, ?, ?)",
            (codigo, nome, preco_venda, preco_custo, estoque, estoque_minimo)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"Erro: Código de barras '{codigo}' já existe.")
        return False
    finally:
        conn.close()
    return True

def listar_produtos():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, codigo_barras, nome, preco_venda, quantidade_estoque, estoque_minimo FROM produtos ORDER BY nome")
    produtos = cursor.fetchall()
    conn.close()
    return produtos

def atualizar_produto(id_produto, codigo, nome, preco_venda, preco_custo, estoque, estoque_minimo):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE produtos 
        SET codigo_barras = ?, nome = ?, preco_venda = ?, preco_custo = ?, quantidade_estoque = ?, estoque_minimo = ?
        WHERE id = ?
        """,
        (codigo, nome, preco_venda, preco_custo, estoque, estoque_minimo, id_produto)
    )
    conn.commit()
    conn.close()

def remover_produto(id_produto):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM produtos WHERE id = ?", (id_produto,))
    conn.commit()
    conn.close()

def buscar_produto_por_codigo(codigo):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, preco_venda, quantidade_estoque FROM produtos WHERE codigo_barras = ?", (codigo,))
    produto = cursor.fetchone()
    conn.close()
    return produto


def registrar_venda(carrinho):

    conn = conectar_db()
    cursor = conn.cursor()
    
    try:
        total_venda = sum(item['preco'] * item['qtd'] for item in carrinho)
        
        data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO vendas (data_hora, total_venda) VALUES (?, ?)", (data_atual, total_venda))
        
        venda_id = cursor.lastrowid
        
        for item in carrinho:
            cursor.execute(
                "INSERT INTO itens_venda (venda_id, produto_id, quantidade, preco_unitario_momento) VALUES (?, ?, ?, ?)",
                (venda_id, item['id'], item['qtd'], item['preco'])
            )
            
            cursor.execute(
                "UPDATE produtos SET quantidade_estoque = quantidade_estoque - ? WHERE id = ?",
                (item['qtd'], item['id'])
            )

        conn.commit()

    except Exception as e:
        print(f"Erro ao registrar venda, revertendo transação: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == '__main__':

    print("Inicializando banco de dados...")
    criar_tabela()
    print("Tabelas criadas com sucesso (se não existiam).")


def gerar_relatorio_vendas(data_inicio, data_fim):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, data_hora, total_venda FROM vendas WHERE data_hora BETWEEN ? AND ?",
        (f"{data_inicio} 00:00:00", f"{data_fim} 23:59:59")
    )
    vendas = cursor.fetchall()
    conn.close()
    return vendas

def gerar_relatorio_estoque_baixo():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT nome, quantidade_estoque, estoque_minimo 
        FROM produtos 
        WHERE quantidade_estoque <= estoque_minimo
        ORDER BY quantidade_estoque ASC
    """)
    produtos = cursor.fetchall()
    conn.close()
    return produtos