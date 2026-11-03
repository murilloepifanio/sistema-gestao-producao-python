"""Sistema simples de gestão de produção com SQLite.

Autor: Murillo Epifânio Rodrigues de Almeida.
"""

import sqlite3 as sq


def criar_banco():
    """Cria o arquivo SQLite e a tabela de produtos, se necessário."""
    conexao = sq.connect("banco_dados.db")
    cursor = conexao.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id_produto INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            preco REAL NOT NULL,
            estoque INTEGER NOT NULL
        )
    """)
    conexao.commit()
    conexao.close()


def cadastrar_produto():
    """Solicita os dados e cadastra um produto no banco."""
    nome = input("Nome do produto: ").strip()
    if not nome:
        print("O nome não pode ficar vazio.")
        return
    try:
        preco = float(input("Preço (use ponto decimal): "))
        estoque = int(input("Estoque inicial: "))
    except ValueError:
        print("Preço ou quantidade inválida.")
        return
    if preco < 0 or estoque < 0:
        print("Preço e estoque não podem ser negativos.")
        return

    conexao = sq.connect("banco_dados.db")
    cursor = conexao.cursor()
    cursor.execute(
        "INSERT INTO produtos (nome, preco, estoque) VALUES (?, ?, ?)",
        (nome, preco, estoque)
    )
    conexao.commit()
    conexao.close()
    print("Produto cadastrado!")


def listar_produtos():
    """Lista todos os produtos cadastrados."""
    conexao = sq.connect("banco_dados.db")
    cursor = conexao.cursor()
    cursor.execute(
        "SELECT id_produto, nome, preco, estoque FROM produtos ORDER BY id_produto"
    )
    produtos = cursor.fetchall()
    conexao.close()

    if not produtos:
        print("Nenhum produto cadastrado.")
        return

    for produto in produtos:
        print(
            f"ID: {produto[0]} | Nome: {produto[1]} | "
            f"Preço: R$ {produto[2]:.2f} | Estoque: {produto[3]}"
        )


def registrar_producao():
    """Acrescenta unidades produzidas ao estoque."""
    try:
        id_produto = int(input("ID do produto: "))
        quantidade = int(input("Quantidade produzida: "))
    except ValueError:
        print("Digite números inteiros.")
        return
    if quantidade <= 0:
        print("A quantidade deve ser positiva.")
        return

    conexao = sq.connect("banco_dados.db")
    cursor = conexao.cursor()
    cursor.execute(
        "UPDATE produtos SET estoque = estoque + ? WHERE id_produto = ?",
        (quantidade, id_produto)
    )
    if cursor.rowcount == 0:
        print("Produto não encontrado.")
    else:
        conexao.commit()
        print("Produção registrada!")
    conexao.close()


def registrar_venda():
    """Desconta unidades vendidas se houver estoque suficiente."""
    try:
        id_produto = int(input("ID do produto: "))
        quantidade = int(input("Quantidade vendida: "))
    except ValueError:
        print("Digite números inteiros.")
        return
    if quantidade <= 0:
        print("A quantidade deve ser positiva.")
        return

    conexao = sq.connect("banco_dados.db")
    cursor = conexao.cursor()
    cursor.execute("""
        UPDATE produtos
        SET estoque = estoque - ?
        WHERE id_produto = ? AND estoque >= ?
    """, (quantidade, id_produto, quantidade))
    if cursor.rowcount == 0:
        print("Produto não encontrado ou estoque insuficiente.")
    else:
        conexao.commit()
        print("Venda registrada!")
    conexao.close()


def consultar_estoque():
    """Consulta o estoque de um produto pelo ID."""
    try:
        id_produto = int(input("ID do produto: "))
    except ValueError:
        print("Digite um ID válido.")
        return

    conexao = sq.connect("banco_dados.db")
    cursor = conexao.cursor()
    cursor.execute(
        "SELECT nome, estoque FROM produtos WHERE id_produto = ?",
        (id_produto,)
    )
    produto = cursor.fetchone()
    conexao.close()

    if produto is None:
        print("Produto não encontrado.")
    else:
        print(f"Produto: {produto[0]} | Estoque: {produto[1]} unidades")


def menu_principal():
    """Exibe o menu e chama as funções selecionadas."""
    opcao = -1
    while opcao != 0:
        print("""
===== SISTEMA DE GESTÃO DE PRODUÇÃO =====

1 - Cadastrar produto
2 - Listar produtos
3 - Registrar produção
4 - Registrar venda
5 - Consultar estoque
0 - Sair
""")
        try:
            opcao = int(input("Informe a opção: "))
        except ValueError:
            print("Digite apenas números.")
            continue

        if opcao == 1:
            cadastrar_produto()
        elif opcao == 2:
            listar_produtos()
        elif opcao == 3:
            registrar_producao()
        elif opcao == 4:
            registrar_venda()
        elif opcao == 5:
            consultar_estoque()
        elif opcao == 0:
            print("Sistema encerrado!")
        else:
            print("Opção inválida!")


if __name__ == "__main__":
    criar_banco()
    menu_principal()
