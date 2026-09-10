produtos = []
receita = 0


def cadastrar_produto(nome, preco, quantidade):
    produto = {
        'nome': nome,
        'preço': float(preco),
        'quantidade': int(quantidade)
    }

    produtos.append(produto)

    print('\nProduto cadastrado com sucesso!')


def registro_producao():
    print('\n===== REGISTRANDO PRODUÇÃO =====')

    if len(produtos) == 0:
        print('Não existem produtos cadastrados.')

    else:
        for indice, produto in enumerate(produtos):
            print(f"{indice} --> {produto['nome']}")

        escolha = int(input('\nEscolha o produto: '))
        quantidade_produzida = int(input('Informe a quantidade produzida: '))

        if escolha < 0 or escolha >= len(produtos):
            print('\nProduto inválido.')

        elif quantidade_produzida <= 0:
            print('\nA quantidade deve ser maior que zero.')

        else:
            produtos[escolha]['quantidade'] += quantidade_produzida

            print('\nProdução registrada com sucesso!')
            print(
                f"Estoque atual: {produtos[escolha]['quantidade']} unidades"
            )


def registro_venda():
    global receita

    print('\n===== REGISTRANDO VENDA =====')

    if len(produtos) == 0:
        print('Não existem produtos cadastrados.')

    else:
        for indice, produto in enumerate(produtos):
            print(
                f"{indice} --> {produto['nome']} "
                f"| Estoque: {produto['quantidade']}"
            )

        escolha = int(input('\nEscolha um produto: '))
        quantidade_vendida = int(input('Informe a quantidade vendida: '))

        if escolha < 0 or escolha >= len(produtos):
            print('\nProduto inválido.')

        elif quantidade_vendida <= 0:
            print('\nA quantidade vendida deve ser maior que zero.')

        elif quantidade_vendida > produtos[escolha]['quantidade']:
            print('\nEstoque insuficiente.')

        else:
            produtos[escolha]['quantidade'] -= quantidade_vendida

            valor_vendido = (
                quantidade_vendida * produtos[escolha]['preço']
            )

            receita += valor_vendido

            print('\nVenda realizada com sucesso!')
            print(f'Valor da venda: R$ {valor_vendido:.2f}')
            print(f'Receita acumulada: R$ {receita:.2f}')
            print(
                f"Estoque restante: "
                f"{produtos[escolha]['quantidade']} unidades"
            )


def consulta_estoque():
    print('\n===== ESTOQUE =====')

    if len(produtos) == 0:
        print('Sem produtos cadastrados.')

    else:
        for indice, produto in enumerate(produtos):
            print(f'''
Código: {indice}
Produto: {produto['nome']}
Preço: R$ {produto['preço']:.2f}
Quantidade: {produto['quantidade']}
''')


def relatorios():
    print('\n===== RELATÓRIOS =====')

    if len(produtos) == 0:
        print('Não existem produtos cadastrados.')

    else:
        total_itens = 0
        valor_estoque = 0

        for produto in produtos:
            total_itens += produto['quantidade']

            valor_estoque += (
                produto['quantidade'] * produto['preço']
            )

        print(f'Produtos cadastrados: {len(produtos)}')
        print(f'Quantidade total em estoque: {total_itens}')
        print(f'Valor estimado do estoque: R$ {valor_estoque:.2f}')
        print(f'Receita acumulada: R$ {receita:.2f}')


def funcionarios():
    print('\n===== FUNCIONÁRIOS =====')
    print('Funcionalidade ainda não implementada.')


def menu_principal():
    opcao = -1

    while opcao != 0:

        print('''
===== SISTEMA DE GESTÃO DE PRODUÇÃO =====

1 - Cadastrar produto
2 - Registrar produção
3 - Registrar venda
4 - Consultar estoque
5 - Relatórios
6 - Funcionários
0 - Sair
''')

        opcao = int(input('Informe a opção: '))

        if opcao == 1:

            nome = input('Informe o nome do produto: ')
            preco = float(input('Informe o preço do produto: R$ '))
            quantidade = int(input('Informe a quantidade inicial: '))

            if preco <= 0:
                print('\nO preço deve ser maior que zero.')

            elif quantidade < 0:
                print('\nA quantidade não pode ser negativa.')

            else:
                cadastrar_produto(nome, preco, quantidade)

        elif opcao == 2:
            registro_producao()

        elif opcao == 3:
            registro_venda()

        elif opcao == 4:
            consulta_estoque()

        elif opcao == 5:
            relatorios()

        elif opcao == 6:
            funcionarios()

        elif opcao == 0:
            print('\nPrograma finalizado.')

        else:
            print('\nCÓDIGO INVÁLIDO! TENTE NOVAMENTE.')


if __name__ == "__main__":
    menu_principal()
