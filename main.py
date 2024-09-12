import sqlite3
import os
import sys
import platform
from time import sleep
from datetime import datetime, timedelta
import locale

conn = sqlite3.connect('database_gastos.db')
cursor = conn.cursor()

locale.setlocale(locale.LC_ALL, 'pt_BR.utf-8')

data_atual = datetime.now()

nome_tabela = f'gastos_mensais'

tabela = True

def criar_tabela():
    limpar_tela()
    
    cursor.execute(f'''create table if not exists "{nome_tabela}"(
                        id integer,
                        valor_inicial float,
                        valor_restante float,
                        valor_cache float,
                        valor_reserva float,
                        data_inicio integer,
                        dias integer,
                        semana integer,
                        ultima_atualizacao text,
                        dinheiro_semana1 text,
                        dinheiro_semana2 text,
                        dinheiro_semana3 text,
                        dinheiro_semana4 text
                        ) ''')
    cursor.execute(f'insert into "{nome_tabela}" (id) values (1)')
    cursor.execute(f'update "{nome_tabela}" set valor_cache = 0 where id = 1')
    cursor.execute(f'update "{nome_tabela}" set semana = 1 where id = 1')
    cursor.execute(f'update "{nome_tabela}" set valor_restante = 0 where id = 1')
    cursor.execute(f'update "{nome_tabela}" set valor_reserva = 0 where id = 1')
    cursor.execute(f'update "{nome_tabela}" set dinheiro_semana1 = "nao_feito" where id = 1')
    cursor.execute(f'update "{nome_tabela}" set dinheiro_semana2 = "nao_feito" where id = 1')
    cursor.execute(f'update "{nome_tabela}" set dinheiro_semana3 = "nao_feito" where id = 1')
    cursor.execute(f'update "{nome_tabela}" set dinheiro_semana4 = "nao_feito" where id = 1')
    conn.commit()

    print('Tabela Criada!')
    sleep(2)

    main()   
     
def verificar_tabela():
    while True:
        limpar_tela()
        
        try:
            cursor.execute(f'select * from "{nome_tabela}" ')

            print('Já existe uma tabela desse mês!\n')
            print('(1) Nova tabela')
            print('(2) Cancelar')

            opcao = int(input('\nOpção: '))

            if opcao == 1:
                limpar_tela()
                print('Atenção! esta ação substituirá todos os seus dados')
                
                print('\n(1) Prosseguir')
                print('(2) Cancelar')
                
                opcao2 = int(input('\nOpção: '))

                if opcao2 == 1:
                    cursor.execute(f'drop table if exists "{nome_tabela}" ')
                    conn.commit()
                    
                    criar_tabela()

                elif opcao2 == 2:
                    main()
                
                else:
                    print('Opção Inválida!')

            elif opcao == 2:
                main()

        except sqlite3.OperationalError:
            criar_tabela()

def regis_valor():
    while True:    
        limpar_tela()
        try:
            cursor.execute(f'select * from "{nome_tabela}" ')
        
        except sqlite3.OperationalError:
            print('Tabela não encontrada')
            print('Crie uma tabela antes de começar!')
            sleep(2)

            main()


        verficar_data = cursor.execute(f'''select data_inicio from "{nome_tabela}" ''').fetchone()[0]

        if verficar_data is None:

            print('Digite o dia de início\n')

            try:
                dia = int(input('Dia: '))

                if dia <= data_atual.day:

                    data_escolhida = dia
                    
                    cursor.execute(f'update "{nome_tabela}" set data_inicio = "{data_escolhida}" where id = 1')

                    conn.commit()

                    print('Data escolhida!')
                    sleep(2)
                    

                elif dia > data_atual.day:
                    print('Digite uma data válida!')
                    sleep(2)
                    regis_valor()

            except ValueError:
                limpar_tela()

                print('Digite apenas números!')
                sleep(2)


        try:
            limpar_tela()
            valor = cursor.execute(f'''select valor_inicial from "{nome_tabela}" ''').fetchone()[0]

            print('Valor do mês ja registrado!')
            
            print(f'Valor: R${valor:.2f}'.replace('.' , ','))

            
            print('\n(1) alterar o valor atual')
            print('(2) Cancelar ')

            opcao = input('\nOpção: ')

            if opcao == '1':
                limpar_tela()

                alteracao = float(input('Digite o valor: ').replace(',' , '.'))
                
                cursor.execute(f'update "{nome_tabela}" set valor_inicial = {alteracao}')
                conn.commit()

                print(f'Valor alterado com sucesso para {alteracao:.2f}!'.replace('.', ','))
                sleep(2)
                
                main()

            elif opcao == '2':
                main()
            
            else:
                limpar_tela()
                
                print('Opção Inválida!')
                sleep(2)

        except Exception as error:               
            try:
                limpar_tela()
                valor = float(input('Digite o valor que será usado neste mês: ').replace(',' , '.'))

                cursor.execute(f'''update "{nome_tabela}" set valor_inicial = {valor} where id = 1''')

                conn.commit()
                print('Valor Registrado!')
                sleep(2)

                main()

            except ValueError:
                limpar_tela()

                print('Digite apenas números!')
                sleep(2)
    
def calc_valor():
    while True:
        limpar_tela()
        try:
            cursor.execute(f'select * from "{nome_tabela}" ')
        
        except sqlite3.OperationalError:
            print('Tabela não encontrada')
            print('Crie uma tabela antes de começar!')
            sleep(2)

            main()

        try:
            valor_semanal = cursor.execute(f'select valor_inicial from "{nome_tabela}" ').fetchone()[0]
            valor_disponivel = int(valor_semanal) / 4
            valor_restante = cursor.execute(f'select valor_restante from "{nome_tabela}" ').fetchone()[0]

            valor_restante = valor_disponivel - valor_restante

            # Obter o dia de início como número do banco de dados (ex: 5 para dia 5 do mês)
            dia_inicio = cursor.execute(f'SELECT data_inicio FROM "{nome_tabela}"').fetchone()[0]

            # Usar o valor de dia_inicio para criar uma data no mês/ano atual
            hoje = datetime.today()
            ano = hoje.year
            mes = hoje.month

            # Criar a data com base no dia do início e mês/ano atual
            data_inicio = datetime(ano, mes, dia_inicio)

            # Obter a semana atual do banco de dados
            semana = cursor.execute(f'SELECT semana FROM "{nome_tabela}"').fetchone()[0]

            # Obter a última data em que a semana foi atualizada (se houver)
            ultima_atualizacao = cursor.execute(f'SELECT ultima_atualizacao FROM "{nome_tabela}"').fetchone()[0]

            # Se a última atualização está vazia, define como data de início
            if ultima_atualizacao is None:
                ultima_atualizacao = data_inicio
                cursor.execute(f'UPDATE "{nome_tabela}" SET ultima_atualizacao = "{data_inicio.strftime("%Y-%m-%d")}" WHERE id = 1')
                conn.commit()
            else:
                # Converter a string de ultima_atualizacao para um objeto datetime usando o formato correto
                ultima_atualizacao = datetime.strptime(ultima_atualizacao, '%Y-%m-%d')

            # Diferença de dias desde a última atualização
            dias_passados = (hoje - ultima_atualizacao).days
            
            
            # Se passaram mais de 7 dias, atualize a semana
            if dias_passados >= 7:
                semanas_adicionais = dias_passados // 7
                dias = (dias_passados % 7) + 1  # Reseta os dias para 1 depois de 7
                semana = (semana + semanas_adicionais - 1) % 5 + 1  # Atualiza a semana e reseta após 5
                
            else:
                # Se não passaram 7 dias, mantenha os dias atualizados mas sem resetar a semana
                dias = (dias_passados % 7) + 1

            if semana > 4:
                fim_semana()

            if semana == 1 and not tentar_resetar_dinheiro(1):
                dinheiro_resetado(1)
                cursor.execute(f'update "{nome_tabela}" set valor_restante = 0 where id = 1')
                cursor.execute(f'update "{nome_tabela}" set valor_reserva = 0 where id = 1')
                conn.commit()
                calc_valor()

            if semana == 2 and not tentar_resetar_dinheiro(2):
                dinheiro_resetado(2)
                cursor.execute(f'update "{nome_tabela}" set valor_restante = 0 where id = 1')
                cursor.execute(f'update "{nome_tabela}" set valor_reserva = 0 where id = 1')
                conn.commit()
                calc_valor()

            if semana == 3 and not tentar_resetar_dinheiro(3):
                dinheiro_resetado(3)
                cursor.execute(f'update "{nome_tabela}" set valor_restante = 0 where id = 1')
                cursor.execute(f'update "{nome_tabela}" set valor_reserva = 0 where id = 1')
                conn.commit()
                calc_valor()

            if semana == 4 and not tentar_resetar_dinheiro(4):
                dinheiro_resetado(4)
                cursor.execute(f'update "{nome_tabela}" set valor_restante = 0 where id = 1')
                cursor.execute(f'update "{nome_tabela}" set valor_reserva = 0 where id = 1')
                conn.commit()
                calc_valor()
                

            print(f'Valor por semana: R${valor_disponivel:.2f}'.replace('.' , ','))

            print(f'\nDia {dias}/7 | Semana {semana}/4 | Valor Disp: R${valor_restante:.2f}'.replace('.' , ','))

            print('\n(1) Compras')
            print('(2) Cancelar\n')

            opcao = input('Opção: ')

            if opcao == '1':
                compras()
            
            elif opcao == '2':
                main()

            else:
                print('Opção Inválida!')
                sleep(1)

        except TypeError as error:
            print(f'Nenhum valor registrado!')
            sleep(2)
            
            main()

def dinheiro_resetado(semana):
    if semana == 1:
        cursor.execute(f'update "{nome_tabela}" set dinheiro_semana1 = "feito" where id = 1')

    if semana == 2:
        cursor.execute(f'update "{nome_tabela}" set dinheiro_semana2 = "feito" where id = 1')

    if semana == 3:
        cursor.execute(f'update "{nome_tabela}" set dinheiro_semana3 = "feito" where id = 1')
    
    if semana == 4:
        cursor.execute(f'update "{nome_tabela}" set dinheiro_semana4 = "feito" where id = 1')

    conn.commit()

def tentar_resetar_dinheiro(semana):
    if semana == 1:

        dinheiro1 = cursor.execute(f'select dinheiro_semana1 from "{nome_tabela}" ').fetchone()[0]
        if dinheiro1 == 'feito':
            return True
        
        return False
    
    if semana == 2:

        dinheiro2 = cursor.execute(f'select dinheiro_semana2 from "{nome_tabela}" ').fetchone()[0]
        if dinheiro2 == 'feito':
            return True
        
        return False
    
    if semana == 3:

        dinheiro3 = cursor.execute(f'select dinheiro_semana3 from "{nome_tabela}" ').fetchone()[0]
        if dinheiro3 == 'feito':
            return True
        
        return False
    
    if semana == 4:

        dinheiro4 = cursor.execute(f'select dinheiro_semana4 from "{nome_tabela}" ').fetchone()[0]
        if dinheiro4 == 'feito':
            return True
        
        return False

def compras():
    while True:
        limpar_tela()
        
        valor_semanal = cursor.execute(f'select valor_inicial from "{nome_tabela}" ').fetchone()[0]
        valor_cache = cursor.execute(f'select valor_cache from "{nome_tabela}" ').fetchone()[0]
        valor_restante = cursor.execute(f'select valor_restante from "{nome_tabela}" ').fetchone()[0]
        valor_reserva = cursor.execute(f'select valor_reserva from "{nome_tabela}" ').fetchone()[0]
        
        valor_disponivel = (valor_semanal / 4) - valor_reserva

        valor = ((valor_semanal / 4) - valor_restante) - valor_cache

        print('Coloque o valor individual de cada item abaixo\n')
        
        print(f'Valor Disponível: R${valor:.2f}'.replace('.' , ','))
        print(f'Valor Gasto: R${valor_cache:.2f}'.replace('.' , ','))
        
        try:
            
            print('\n(1) Finalizar Compra')
            print('(0) Cancelar Compra\n')

            itens = float(input('\nValor do item: ').replace(',' , '.'))

            if itens > valor_disponivel:
                limpar_tela()
                
                print('Valor maior que o disponível!')
                sleep(2)
            

            elif itens > 1:
                cursor.execute(f'update "{nome_tabela}" set valor_cache = valor_cache + {itens} where id = 1')
                conn.commit()
                

            elif itens == 0:
                limpar_tela()
                
                cursor.execute(f'update "{nome_tabela}" set valor_cache = 0 where id = 1')
                conn.commit()
                
                print('Compra Cancelada!')
                print('Nenhum valor foi adicionado')
                sleep(1)
                
                calc_valor()
            
            elif itens == 1:
                cursor.execute(f'update "{nome_tabela}" set valor_restante = valor_restante + valor_cache where id = 1')
                cursor.execute(f'update "{nome_tabela}" set valor_reserva = valor_cache where id = 1')
                cursor.execute(f'update "{nome_tabela}" set valor_cache = 0 where id = 1')
                conn.commit()
                
                
                
                print('Compra Finalizada!')
                sleep(2)
                
                calc_valor()

        except ValueError as error:
            limpar_tela()
            
            print('Digite apenas números!')
            sleep(2)

def fim_semana():
    limpar_tela()

    print('As 4 semanas se completaram.')
    print('Inicie um nova tabela para continuar!')
    sleep(4)
    main()

def limpar_tela():
    sistema = platform.system()
    
    if sistema == 'Linux':
        os.system('clear')
    
    elif sistema == 'Windows':
        os.system('cls')

def main():
    while True:    
        limpar_tela()

        print('''
(1) Registrar valor do mês
(2) Calcular valor
(3) Criar tabela *              
    ''')
        
        opcao = input('\nOpção: ')

        if opcao == '1':
            regis_valor()
        
        elif opcao == '2':
            calc_valor()
        
        elif opcao == '3':
            verificar_tabela()

        else:
            limpar_tela()
            
            print('Opção Inválida!')
            sleep(2)      

if __name__ == '__main__':
    main()