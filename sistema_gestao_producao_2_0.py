import sqlite3 as sq

BANCO = 'banco_dados_v2.db'


def conectar():
    """Abre uma conexão com o banco de dados."""
    conexao = sq.connect(BANCO)
    conexao.execute('PRAGMA foreign_keys = ON')
    return conexao


def criar_banco():
    """Cria as tabelas sem apagar dados existentes."""
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id_produto INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            preco REAL NOT NULL CHECK(preco >= 0),
            estoque INTEGER NOT NULL DEFAULT 0 CHECK(estoque >= 0)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS funcionarios (
            id_funcionario INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cargo TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS producoes (
            id_producao INTEGER PRIMARY KEY AUTOINCREMENT,
            id_produto INTEGER NOT NULL,
            quantidade INTEGER NOT NULL CHECK(quantidade > 0),
            data_registro TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_produto) REFERENCES produtos(id_produto)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendas (
            id_venda INTEGER PRIMARY KEY AUTOINCREMENT,
            id_produto INTEGER NOT NULL,
            quantidade INTEGER NOT NULL CHECK(quantidade > 0),
            preco_unitario REAL NOT NULL,
            data_registro TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_produto) REFERENCES produtos(id_produto)
        )
    """)
    conexao.commit()
    conexao.close()


def ler_inteiro(mensagem):
    """Lê um número inteiro; retorna None em caso de erro."""
    try:
        return int(input(mensagem))
    except ValueError:
        print('Digite um número inteiro válido.')
        return None


def cadastrar_produto():
    """Cadastra um produto com preço e estoque inicial."""
    nome = input('Nome do produto: ').strip()
    if not nome:
        print('O nome é obrigatório.')
        return
    try:
        preco = float(input('Preço (use ponto para decimais): '))
    except ValueError:
        print('Preço inválido.')
        return
    estoque = ler_inteiro('Estoque inicial: ')
    if estoque is None:
        return
    if preco < 0 or estoque < 0:
        print('Preço e estoque não podem ser negativos.')
        return
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute('INSERT INTO produtos (nome, preco, estoque) VALUES (?, ?, ?)',
                   (nome, preco, estoque))
    conexao.commit()
    print(f'Produto cadastrado com ID {cursor.lastrowid}.')
    conexao.close()


def listar_produtos():
    """Lista todos os produtos e estoques."""
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute('SELECT id_produto, nome, preco, estoque FROM produtos ORDER BY id_produto')
    produtos = cursor.fetchall()
    conexao.close()
    if not produtos:
        print('Nenhum produto cadastrado.')
        return
    for produto in produtos:
        print(f'ID {produto[0]} | {produto[1]} | R$ {produto[2]:.2f} | Estoque: {produto[3]}')


def registrar_producao():
    """Registra produção e aumenta o estoque na mesma transação."""
    id_produto = ler_inteiro('ID do produto: ')
    quantidade = ler_inteiro('Quantidade produzida: ')
    if id_produto is None or quantidade is None:
        return
    if quantidade <= 0:
        print('A quantidade deve ser maior que zero.')
        return
    conexao = conectar()
    try:
        cursor = conexao.cursor()
        cursor.execute('UPDATE produtos SET estoque = estoque + ? WHERE id_produto = ?',
                       (quantidade, id_produto))
        if cursor.rowcount == 0:
            print('Produto não encontrado.')
            return
        cursor.execute('INSERT INTO producoes (id_produto, quantidade) VALUES (?, ?)',
                       (id_produto, quantidade))
        conexao.commit()
        print('Produção registrada e estoque atualizado.')
    except sq.Error as erro:
        conexao.rollback()
        print('Erro ao registrar produção:', erro)
    finally:
        conexao.close()


def registrar_venda():
    """Registra venda e reduz estoque quando houver unidades suficientes."""
    id_produto = ler_inteiro('ID do produto: ')
    quantidade = ler_inteiro('Quantidade vendida: ')
    if id_produto is None or quantidade is None:
        return
    if quantidade <= 0:
        print('A quantidade deve ser maior que zero.')
        return
    conexao = conectar()
    try:
        cursor = conexao.cursor()
        cursor.execute('SELECT preco FROM produtos WHERE id_produto = ?', (id_produto,))
        produto = cursor.fetchone()
        if produto is None:
            print('Produto não encontrado.')
            return
        cursor.execute("""
            UPDATE produtos SET estoque = estoque - ?
            WHERE id_produto = ? AND estoque >= ?
        """, (quantidade, id_produto, quantidade))
        if cursor.rowcount == 0:
            print('Estoque insuficiente para esta venda.')
            return
        cursor.execute("""
            INSERT INTO vendas (id_produto, quantidade, preco_unitario)
            VALUES (?, ?, ?)
        """, (id_produto, quantidade, produto[0]))
        conexao.commit()
        print(f'Venda registrada. Total: R$ {quantidade * produto[0]:.2f}')
    except sq.Error as erro:
        conexao.rollback()
        print('Erro ao registrar venda:', erro)
    finally:
        conexao.close()


def consultar_estoque():
    """Consulta o estoque de um produto por ID."""
    id_produto = ler_inteiro('ID do produto: ')
    if id_produto is None:
        return
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute('SELECT nome, estoque FROM produtos WHERE id_produto = ?', (id_produto,))
    produto = cursor.fetchone()
    conexao.close()
    if produto is None:
        print('Produto não encontrado.')
    else:
        print(f'{produto[0]}: {produto[1]} unidade(s) em estoque.')


def excluir_produto():
    """Exclui apenas produtos sem movimentações."""
    id_produto = ler_inteiro('ID do produto a excluir: ')
    if id_produto is None:
        return
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute('SELECT nome FROM produtos WHERE id_produto = ?', (id_produto,))
    produto = cursor.fetchone()
    if produto is None:
        print('Produto não encontrado.')
        conexao.close()
        return
    cursor.execute('SELECT COUNT(*) FROM producoes WHERE id_produto = ?', (id_produto,))
    producoes = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM vendas WHERE id_produto = ?', (id_produto,))
    vendas = cursor.fetchone()[0]
    if producoes > 0 or vendas > 0:
        print('Não é possível excluir: o produto possui histórico de produção ou venda.')
    else:
        confirmar = input(f'Excluir {produto[0]}? (s/n): ').strip().lower()
        if confirmar == 's':
            cursor.execute('DELETE FROM produtos WHERE id_produto = ?', (id_produto,))
            conexao.commit()
            print('Produto excluído.')
        else:
            print('Exclusão cancelada.')
    conexao.close()


def funcionarios():
    """Cadastra e lista funcionários."""
    print('\n1 - Cadastrar funcionário\n2 - Listar funcionários')
    opcao = ler_inteiro('Opção: ')
    if opcao == 1:
        nome = input('Nome: ').strip()
        cargo = input('Cargo: ').strip()
        if not nome or not cargo:
            print('Nome e cargo são obrigatórios.')
            return
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute('INSERT INTO funcionarios (nome, cargo) VALUES (?, ?)', (nome, cargo))
        conexao.commit()
        conexao.close()
        print('Funcionário cadastrado.')
    elif opcao == 2:
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute('SELECT id_funcionario, nome, cargo FROM funcionarios ORDER BY id_funcionario')
        registros = cursor.fetchall()
        conexao.close()
        if not registros:
            print('Nenhum funcionário cadastrado.')
        for registro in registros:
            print(f'ID {registro[0]} | {registro[1]} | {registro[2]}')
    else:
        print('Opção inválida.')


def relatorios():
    """Mostra resumo de estoque, produção e vendas."""
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute('SELECT COUNT(*), COALESCE(SUM(preco * estoque), 0) FROM produtos')
    quantidade_produtos, valor_estoque = cursor.fetchone()
    cursor.execute('SELECT COALESCE(SUM(quantidade), 0) FROM producoes')
    total_produzido = cursor.fetchone()[0]
    cursor.execute('SELECT COALESCE(SUM(quantidade), 0), COALESCE(SUM(quantidade * preco_unitario), 0) FROM vendas')
    total_vendido, faturamento = cursor.fetchone()
    print('\n===== RELATÓRIO GERAL =====')
    print(f'Produtos cadastrados: {quantidade_produtos}')
    print(f'Unidades produzidas (histórico): {total_produzido}')
    print(f'Unidades vendidas (histórico): {total_vendido}')
    print(f'Faturamento registrado: R$ {faturamento:.2f}')
    print(f'Valor de venda do estoque atual: R$ {valor_estoque:.2f}')
    print('\n===== ÚLTIMAS VENDAS =====')
    cursor.execute("""
        SELECT v.id_venda, p.nome, v.quantidade, v.preco_unitario, v.data_registro
        FROM vendas v JOIN produtos p ON p.id_produto = v.id_produto
        ORDER BY v.id_venda DESC LIMIT 5
    """)
    vendas = cursor.fetchall()
    if not vendas:
        print('Nenhuma venda registrada.')
    for venda in vendas:
        print(f'Venda {venda[0]} | {venda[1]} | {venda[2]} un. | R$ {venda[2] * venda[3]:.2f} | {venda[4]}')
    conexao.close()


def menu_principal():
    """Mostra o menu até a opção de saída."""
    opcao = -1
    while opcao != 0:
        print("""
===== SISTEMA DE GESTÃO DE PRODUÇÃO 2.0 =====
1 - Cadastrar produto
2 - Listar produtos
3 - Registrar produção
4 - Registrar venda
5 - Consultar estoque
6 - Relatórios
7 - Funcionários
8 - Excluir produto
0 - Sair
""")
        opcao = ler_inteiro('Informe a opção: ')
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
        elif opcao == 6:
            relatorios()
        elif opcao == 7:
            funcionarios()
        elif opcao == 8:
            excluir_produto()
        elif opcao == 0:
            print('Sistema encerrado.')
        else:
            print('Opção inválida.')


if __name__ == '__main__':
    criar_banco()
    menu_principal()
