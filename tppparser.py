import sys
import os

from sys import argv, exit

import logging

logging.basicConfig(
     level = logging.DEBUG,
     filename = "parser.log",
     filemode = "w",
     format = "%(filename)10s:%(lineno)4d:%(message)s"
)
log = logging.getLogger()

# source_file global para p_error conseguir calcular coluna corretamente
source_file = ""

import ply.yacc as yacc
 
# Get the token map from the lexer.  This is required.
from tpplex import tokens, define_column
import tpplex

from mytree import MyNode
from anytree.exporter import DotExporter, UniqueDotExporter
from anytree import RenderTree, AsciiStyle

from myerror import MyError

error_handler = MyError('ParserErrors')

check_tpp = False
check_key = False
check_gentree = False

root = None

# ══════════════════════════════════════════════
# REGRAS GRAMATICAIS
# ══════════════════════════════════════════════

def p_programa(p):
    """programa : lista_declaracoes"""

    global root

    programa = MyNode(name='programa', type='PROGRAMA')
    root = programa
    p[0] = programa
    p[1].parent = programa


def p_lista_declaracoes(p):
    """lista_declaracoes : lista_declaracoes declaracao
                        | declaracao
    """
    pai = MyNode(name='lista_declaracoes', type='LISTA_DECLARACOES')
    p[0] = pai
    p[1].parent = pai

    if len(p) > 2:
        p[2].parent = pai


def p_declaracao(p):
    """declaracao : declaracao_variaveis
                | inicializacao_variaveis
                | declaracao_funcao
    """
    pai = MyNode(name='declaracao', type='DECLARACAO')
    p[0] = pai
    p[1].parent = pai


def p_declaracao_variaveis(p):
    """declaracao_variaveis : tipo DOIS_PONTOS lista_variaveis"""

    pai = MyNode(name='declaracao_variaveis', type='DECLARACAO_VARIAVEIS')
    p[0] = pai

    p[1].parent = pai

    filho = MyNode(name='DOIS_PONTOS', type='DOIS_PONTOS', parent=pai)
    filho_sym = MyNode(name=p[2], type='SIMBOLO', parent=filho)
    p[2] = filho

    p[3].parent = pai


def p_inicializacao_variaveis(p):
    """inicializacao_variaveis : atribuicao"""

    pai = MyNode(name='inicializacao_variaveis', type='INICIALIZACAO_VARIAVEIS')
    p[0] = pai
    p[1].parent = pai


def p_lista_variaveis(p):
    """lista_variaveis : lista_variaveis VIRGULA var
                        | var
    """
    pai = MyNode(name='lista_variaveis', type='LISTA_VARIAVEIS')
    p[0] = pai
    if len(p) > 2:
        p[1].parent = pai
        filho = MyNode(name='virgula', type='VIRGULA', parent=pai)
        filho_sym = MyNode(name=',', type='SIMBOLO', parent=filho)
        p[3].parent = pai
    else:
       p[1].parent = pai


def p_var(p):
    """var : ID
            | ID indice
    """
    pai = MyNode(name='var', type='VAR')
    p[0] = pai
    filho = MyNode(name='ID', type='ID', parent=pai)
    filho_id = MyNode(name=p[1], type='ID', parent=filho)
    p[1] = filho
    if len(p) > 2:
        p[2].parent = pai


def p_indice(p):
    """indice : indice ABRE_COLCHETE expressao FECHA_COLCHETE
                | ABRE_COLCHETE expressao FECHA_COLCHETE
    """
    pai = MyNode(name='indice', type='INDICE')
    p[0] = pai
    if len(p) == 5:
        p[1].parent = pai

        filho2 = MyNode(name='abre_colchete', type='ABRE_COLCHETE', parent=pai)
        filho_sym2 = MyNode(name=p[2], type='SIMBOLO', parent=filho2)
        p[2] = filho2

        p[3].parent = pai

        filho4 = MyNode(name='fecha_colchete', type='FECHA_COLCHETE', parent=pai)
        filho_sym4 = MyNode(name=p[4], type='SIMBOLO', parent=filho4)
        p[4] = filho4
    else:
        filho1 = MyNode(name='abre_colchete', type='ABRE_COLCHETE', parent=pai)
        filho_sym1 = MyNode(name=p[1], type='SIMBOLO', parent=filho1)
        p[1] = filho1

        p[2].parent = pai

        filho3 = MyNode(name='fecha_colchete', type='FECHA_COLCHETE', parent=pai)
        filho_sym3 = MyNode(name=p[3], type='SIMBOLO', parent=filho3)
        p[3] = filho3


def p_indice_error(p):
    """indice : ABRE_COLCHETE error FECHA_COLCHETE
                | indice ABRE_COLCHETE error FECHA_COLCHETE
    """
    print(error_handler.newError(check_key, 'ERR-SYN-INDICE'))
    error_line = p.lineno(2)
    father = MyNode(name='ERR-SYN-INDICE::{}'.format(error_line), type='ERROR')
    logging.error("Syntax error parsing index rule at line {}".format(error_line))
    parser.errok()
    p[0] = father


def p_tipo(p):
    """tipo : INTEIRO
        | FLUTUANTE
    """
    pai = MyNode(name='tipo', type='TIPO')
    p[0] = pai

    if p[1] == "inteiro":
        filho1 = MyNode(name='INTEIRO', type='INTEIRO', parent=pai)
        filho_sym = MyNode(name=p[1], type=p[1].upper(), parent=filho1)
        p[1] = filho1
    else:
        # FIX: branch FLUTUANTE agora faz p[1] = filho1, filho não fica solto na árvore
        filho1 = MyNode(name='FLUTUANTE', type='FLUTUANTE', parent=pai)
        filho_sym = MyNode(name=p[1], type=p[1].upper(), parent=filho1)
        p[1] = filho1


def p_declaracao_funcao(p):
    """declaracao_funcao : tipo cabecalho 
                        | cabecalho 
    """
    pai = MyNode(name='declaracao_funcao', type='DECLARACAO_FUNCAO')
    p[0] = pai
    p[1].parent = pai

    if len(p) == 3:
        p[2].parent = pai


def p_cabecalho(p):
    """cabecalho : ID ABRE_PARENTESE lista_parametros FECHA_PARENTESE corpo FIM"""

    pai = MyNode(name='cabecalho', type='CABECALHO')
    p[0] = pai

    filho1 = MyNode(name='ID', type='ID', parent=pai)
    filho_id = MyNode(name=p[1], type='ID', parent=filho1)
    p[1] = filho1

    filho2 = MyNode(name='ABRE_PARENTESE', type='ABRE_PARENTESE', parent=pai)
    filho_sym2 = MyNode(name='(', type='SIMBOLO', parent=filho2)
    p[2] = filho2

    p[3].parent = pai  # lista_parametros

    filho4 = MyNode(name='FECHA_PARENTESE', type='FECHA_PARENTESE', parent=pai)
    filho_sym4 = MyNode(name=')', type='SIMBOLO', parent=filho4)
    p[4] = filho4

    p[5].parent = pai  # corpo

    filho6 = MyNode(name='FIM', type='FIM', parent=pai)
    filho_id = MyNode(name='fim', type='FIM', parent=filho6)
    p[6] = filho6


def p_cabecalho_error(p):
    """cabecalho : ID ABRE_PARENTESE error FECHA_PARENTESE corpo FIM
                | ID ABRE_PARENTESE lista_parametros FECHA_PARENTESE error FIM
    """
    print(error_handler.newError(check_key, 'ERR-SYN-CABECALHO'))
    error_line = p.lineno(1)
    p[0] = MyNode(name='ERR-SYN-CABECALHO::{}'.format(error_line), type='ERROR')
    parser.errok()


def p_lista_parametros(p):
    """lista_parametros : lista_parametros VIRGULA parametro
                    | parametro
                    | vazio
    """
    pai = MyNode(name='lista_parametros', type='LISTA_PARAMETROS')
    p[0] = pai
    p[1].parent = pai

    if len(p) > 2:
        filho2 = MyNode(name='virgula', type='VIRGULA', parent=pai)
        filho_sym2 = MyNode(name=',', type='SIMBOLO', parent=filho2)
        p[2] = filho2
        p[3].parent = pai


def p_parametro(p):
    """parametro : tipo DOIS_PONTOS ID
                | parametro ABRE_COLCHETE FECHA_COLCHETE
    """
    # FIX: ordem corrigida para tipo DOIS_PONTOS ID (alinhado com a gramática e o parser do professor)
    pai = MyNode(name='parametro', type='PARAMETRO')
    p[0] = pai
    p[1].parent = pai

    if p[2] == ':':
        # tipo DOIS_PONTOS ID
        filho2 = MyNode(name='DOIS_PONTOS', type='DOIS_PONTOS', parent=pai)
        filho_sym2 = MyNode(name=':', type='SIMBOLO', parent=filho2)
        p[2] = filho2

        filho3 = MyNode(name='id', type='ID', parent=pai)
        filho_id = MyNode(name=p[3], type='ID', parent=filho3)
        p[3] = filho3
    else:
        # parametro ABRE_COLCHETE FECHA_COLCHETE
        filho2 = MyNode(name='abre_colchete', type='ABRE_COLCHETE', parent=pai)
        filho_sym2 = MyNode(name='[', type='SIMBOLO', parent=filho2)
        p[2] = filho2

        filho3 = MyNode(name='fecha_colchete', type='FECHA_COLCHETE', parent=pai)
        filho_sym3 = MyNode(name=']', type='SIMBOLO', parent=filho3)
        p[3] = filho3


def p_parametro_error(p):
    """parametro : tipo error ID
                | parametro error FECHA_COLCHETE
                | parametro ABRE_COLCHETE error
    """
    print(error_handler.newError(check_key, 'ERR-SYN-PARAMETRO'))
    error_line = p.lineno(1)
    p[0] = MyNode(name='ERR-SYN-PARAMETRO::{}'.format(error_line), type='ERROR')
    parser.errok()


def p_corpo(p):
    """corpo : corpo acao
            | vazio
    """
    pai = MyNode(name='corpo', type='CORPO')
    p[0] = pai
    p[1].parent = pai

    if len(p) > 2:
        p[2].parent = pai


def p_acao(p):
    """acao : expressao
        | declaracao_variaveis
        | se
        | repita
        | leia
        | escreva
        | retorna
    """
    pai = MyNode(name='acao', type='ACAO')
    p[0] = pai
    p[1].parent = pai


def p_se(p):
    """se : SE expressao ENTAO corpo FIM
          | SE expressao ENTAO corpo SENAO corpo FIM
    """
    pai = MyNode(name='se', type='SE')
    p[0] = pai

    filho1 = MyNode(name='SE', type='SE', parent=pai)
    filho_se = MyNode(name=p[1], type='SE', parent=filho1)
    p[1] = filho1

    p[2].parent = pai

    filho3 = MyNode(name='ENTAO', type='ENTAO', parent=pai)
    filho_entao = MyNode(name=p[3], type='ENTAO', parent=filho3)
    p[3] = filho3

    p[4].parent = pai

    if len(p) == 8:
        filho5 = MyNode(name='SENAO', type='SENAO', parent=pai)
        filho_senao = MyNode(name=p[5], type='SENAO', parent=filho5)
        p[5] = filho5

        p[6].parent = pai

        filho7 = MyNode(name='FIM', type='FIM', parent=pai)
        filho_fim = MyNode(name=p[7], type='FIM', parent=filho7)
        p[7] = filho7
    else:
        filho5 = MyNode(name='fim', type='FIM', parent=pai)
        filho_fim = MyNode(name=p[5], type='FIM', parent=filho5)
        p[5] = filho5


def p_se_error(p):
    """se : error expressao ENTAO corpo FIM
        | SE expressao error corpo FIM
        | error expressao ENTAO corpo SENAO corpo FIM
        | SE expressao error corpo SENAO corpo FIM
        | SE expressao ENTAO corpo error corpo FIM
        | SE expressao ENTAO corpo SENAO corpo
        | SE expressao corpo FIM
        | SE expressao corpo SENAO corpo FIM
        | SE error FIM
    """
    print(error_handler.newError(check_key, 'ERR-SYN-SE'))
    error_line = p.lineno(1)
    p[0] = MyNode(name='ERR-SYN-SE::{}'.format(error_line), type='ERROR')
    parser.errok()


def p_repita(p):
    """repita : REPITA corpo ATE expressao"""

    pai = MyNode(name='repita', type='REPITA')
    p[0] = pai

    filho1 = MyNode(name='REPITA', type='REPITA', parent=pai)
    filho_repita = MyNode(name=p[1], type='REPITA', parent=filho1)
    p[1] = filho1

    p[2].parent = pai  # corpo.

    filho3 = MyNode(name='ATE', type='ATE', parent=pai)
    filho_ate = MyNode(name=p[3], type='ATE', parent=filho3)
    p[3] = filho3

    p[4].parent = pai   # expressao.


def p_repita_error(p):
    """repita : error corpo ATE expressao
            | REPITA corpo error expressao
    """
    print(error_handler.newError(check_key, 'ERR-SYN-REPITA'))
    error_line = p.lineno(1)
    p[0] = MyNode(name='ERR-SYN-REPITA::{}'.format(error_line), type='ERROR')
    parser.errok()


def p_atribuicao(p):
    """atribuicao : var ATRIBUICAO expressao"""

    pai = MyNode(name='atribuicao', type='ATRIBUICAO')
    p[0] = pai

    p[1].parent = pai

    filho2 = MyNode(name='ATRIBUICAO', type='ATRIBUICAO', parent=pai)
    filho_sym2 = MyNode(name=':=', type='SIMBOLO', parent=filho2)
    p[2] = filho2

    p[3].parent = pai


def p_leia(p):
    """leia : LEIA ABRE_PARENTESE var FECHA_PARENTESE"""

    pai = MyNode(name='leia', type='LEIA')
    p[0] = pai

    filho1 = MyNode(name='LEIA', type='LEIA', parent=pai)
    filho_sym1 = MyNode(name=p[1], type='LEIA', parent=filho1)
    p[1] = filho1

    filho2 = MyNode(name='ABRE_PARENTESE', type='ABRE_PARENTESE', parent=pai)
    filho_sym2 = MyNode(name='(', type='SIMBOLO', parent=filho2)
    p[2] = filho2

    p[3].parent = pai  # var

    filho4 = MyNode(name='FECHA_PARENTESE', type='FECHA_PARENTESE', parent=pai)
    filho_sym4 = MyNode(name=')', type='SIMBOLO', parent=filho4)
    p[4] = filho4


def p_leia_error(p):
    """leia : LEIA ABRE_PARENTESE error FECHA_PARENTESE
    """
    print(error_handler.newError(check_key, 'ERR-SYN-LEIA'))
    error_line = p.lineno(1)
    p[0] = MyNode(name='ERR-SYN-LEIA::{}'.format(error_line), type='ERROR')
    parser.errok()


def p_escreva(p):
    """escreva : ESCREVA ABRE_PARENTESE expressao FECHA_PARENTESE"""

    pai = MyNode(name='escreva', type='ESCREVA')
    p[0] = pai

    filho1 = MyNode(name='ESCREVA', type='ESCREVA', parent=pai)
    filho_sym1 = MyNode(name=p[1], type='ESCREVA', parent=filho1)
    p[1] = filho1

    filho2 = MyNode(name='ABRE_PARENTESE', type='ABRE_PARENTESE', parent=pai)
    filho_sym2 = MyNode(name='(', type='SIMBOLO', parent=filho2)
    p[2] = filho2

    p[3].parent = pai  # expressao.

    filho4 = MyNode(name='FECHA_PARENTESE', type='FECHA_PARENTESE', parent=pai)
    filho_sym4 = MyNode(name=')', type='SIMBOLO', parent=filho4)
    p[4] = filho4


def p_retorna(p):
    """retorna : RETORNA ABRE_PARENTESE expressao FECHA_PARENTESE"""

    pai = MyNode(name='retorna', type='RETORNA')
    p[0] = pai

    filho1 = MyNode(name='RETORNA', type='RETORNA', parent=pai)
    filho_sym1 = MyNode(name=p[1], type='RETORNA', parent=filho1)
    p[1] = filho1

    filho2 = MyNode(name='ABRE_PARENTESE', type='ABRE_PARENTESE', parent=pai)
    filho_sym2 = MyNode(name='(', type='SIMBOLO', parent=filho2)
    p[2] = filho2

    p[3].parent = pai  # expressao.

    filho4 = MyNode(name='FECHA_PARENTESE', type='FECHA_PARENTESE', parent=pai)
    filho_sym4 = MyNode(name=')', type='SIMBOLO', parent=filho4)
    p[4] = filho4


def p_expressao(p):
    """expressao : expressao_logica
                    | atribuicao
    """
    pai = MyNode(name='expressao', type='EXPRESSAO')
    p[0] = pai
    p[1].parent = pai


def p_expressao_logica(p):
    """expressao_logica : expressao_simples
                    | expressao_logica operador_logico expressao_simples
    """
    pai = MyNode(name='expressao_logica', type='EXPRESSAO_LOGICA')
    p[0] = pai
    p[1].parent = pai

    if len(p) > 2:
        p[2].parent = pai
        p[3].parent = pai


def p_expressao_simples(p):
    """expressao_simples : expressao_aditiva
                        | expressao_simples operador_relacional expressao_aditiva
    """
    pai = MyNode(name='expressao_simples', type='EXPRESSAO_SIMPLES')
    p[0] = pai
    p[1].parent = pai

    if len(p) > 2:
        p[2].parent = pai
        p[3].parent = pai


def p_expressao_aditiva(p):
    """expressao_aditiva : expressao_multiplicativa
                        | expressao_aditiva operador_soma expressao_multiplicativa
    """
    pai = MyNode(name='expressao_aditiva', type='EXPRESSAO_ADITIVA')
    p[0] = pai
    p[1].parent = pai

    if len(p) > 2:
        p[2].parent = pai
        p[3].parent = pai


def p_expressao_multiplicativa(p):
    """expressao_multiplicativa : expressao_unaria
                               | expressao_multiplicativa operador_multiplicacao expressao_unaria
        """
    pai = MyNode(name='expressao_multiplicativa', type='EXPRESSAO_MULTIPLICATIVA')
    p[0] = pai
    p[1].parent = pai

    if len(p) > 2:
        p[2].parent = pai
        p[3].parent = pai


def p_expressao_unaria(p):
    """expressao_unaria : fator
                        | operador_soma fator
                        | operador_negacao fator
        """
    pai = MyNode(name='expressao_unaria', type='EXPRESSAO_UNARIA')
    p[0] = pai

    # FIX: p[1] já é MyNode vindo de operador_soma/operador_negacao,
    # comparar com string '!' nunca seria verdadeiro. Basta atribuir o pai.
    p[1].parent = pai

    if len(p) > 2:
        p[2].parent = pai


def p_operador_relacional(p):
    """operador_relacional : MENOR
                            | MAIOR
                            | IGUAL
                            | DIFERENTE 
                            | MENOR_IGUAL
                            | MAIOR_IGUAL
    """
    pai = MyNode(name='operador_relacional', type='OPERADOR_RELACIONAL')
    p[0] = pai

    if p[1] == "<":
        filho = MyNode(name='MENOR', type='MENOR', parent=pai)
        filho_sym = MyNode(name=p[1], type='SIMBOLO', parent=filho)
    elif p[1] == ">":
        filho = MyNode(name='MAIOR', type='MAIOR', parent=pai)
        filho_sym = MyNode(name=p[1], type='SIMBOLO', parent=filho)
    elif p[1] == "=":
        filho = MyNode(name='IGUAL', type='IGUAL', parent=pai)
        filho_sym = MyNode(name=p[1], type='SIMBOLO', parent=filho)
    elif p[1] == "<>":
        filho = MyNode(name='DIFERENTE', type='DIFERENTE', parent=pai)
        filho_sym = MyNode(name=p[1], type='SIMBOLO', parent=filho)
    elif p[1] == "<=":
        filho = MyNode(name='MENOR_IGUAL', type='MENOR_IGUAL', parent=pai)
        filho_sym = MyNode(name=p[1], type='SIMBOLO', parent=filho)
    elif p[1] == ">=":
        filho = MyNode(name='MAIOR_IGUAL', type='MAIOR_IGUAL', parent=pai)
        filho_sym = MyNode(name=p[1], type='SIMBOLO', parent=filho)
    else:
        print('Erro operador relacional')

    p[1] = filho


def p_operador_soma(p):
    """operador_soma : MAIS
                    | MENOS
    """
    if p[1] == "+":
        mais = MyNode(name='MAIS', type='MAIS')
        mais_lexema = MyNode(name='+', type='SIMBOLO', parent=mais)
        p[0] = MyNode(name='operador_soma', type='OPERADOR_SOMA', children=[mais])
    else:
        menos = MyNode(name='MENOS', type='MENOS')
        menos_lexema = MyNode(name='-', type='SIMBOLO', parent=menos)
        p[0] = MyNode(name='operador_soma', type='OPERADOR_SOMA', children=[menos])


def p_operador_logico(p):
    """operador_logico : E
                    | OU
    """
    if p[1] == "&&":
        filho = MyNode(name='E', type='E')
        filho_lexema = MyNode(name=p[1], type='SIMBOLO', parent=filho)
        p[0] = MyNode(name='operador_logico', type='OPERADOR_LOGICO', children=[filho])
    else:
        filho = MyNode(name='OU', type='OU')
        filho_lexema = MyNode(name=p[1], type='SIMBOLO', parent=filho)
        # FIX: type estava errado como 'OPERADOR_SOMA' no branch do OU
        p[0] = MyNode(name='operador_logico', type='OPERADOR_LOGICO', children=[filho])


def p_operador_negacao(p):
    """operador_negacao : NAO"""

    if p[1] == "!":
        filho = MyNode(name='NAO', type='NAO')
        negacao_lexema = MyNode(name=p[1], type='SIMBOLO', parent=filho)
        p[0] = MyNode(name='operador_negacao', type='OPERADOR_NEGACAO', children=[filho])


def p_operador_multiplicacao(p):
    """operador_multiplicacao : VEZES
                            | DIVIDE
        """
    if p[1] == "*":
        filho = MyNode(name='VEZES', type='VEZES')
        vezes_lexema = MyNode(name=p[1], type='SIMBOLO', parent=filho)
        p[0] = MyNode(name='operador_multiplicacao', type='OPERADOR_MULTIPLICACAO', children=[filho])
    else:
        divide = MyNode(name='DIVIDE', type='DIVIDE')
        divide_lexema = MyNode(name=p[1], type='SIMBOLO', parent=divide)
        p[0] = MyNode(name='operador_multiplicacao', type='OPERADOR_MULTIPLICACAO', children=[divide])


def p_fator(p):
    """fator : ABRE_PARENTESE expressao FECHA_PARENTESE
            | var
            | chamada_funcao
            | numero
        """
    pai = MyNode(name='fator', type='FATOR')
    p[0] = pai
    if len(p) > 2:
        filho1 = MyNode(name='ABRE_PARENTESE', type='ABRE_PARENTESE', parent=pai)
        filho_sym1 = MyNode(name=p[1], type='SIMBOLO', parent=filho1)
        p[1] = filho1

        p[2].parent = pai

        filho3 = MyNode(name='FECHA_PARENTESE', type='FECHA_PARENTESE', parent=pai)
        filho_sym3 = MyNode(name=p[3], type='SIMBOLO', parent=filho3)
        p[3] = filho3
    else:
        p[1].parent = pai


def p_fator_error(p):
    """fator : ABRE_PARENTESE error FECHA_PARENTESE
        """


def p_numero(p):
    """numero : NUM_INTEIRO
                | NUM_PONTO_FLUTUANTE
                | NUM_NOTACAO_CIENTIFICA
    """
    pai = MyNode(name='numero', type='NUMERO')
    p[0] = pai

    valor = str(p[1])
    # FIX: find('e') não detectava 'E' maiúsculo (ex: 1.5E10).
    # Usando lower() para comparação case-insensitive.
    if valor.find('.') == -1 and 'e' not in valor.lower():
        aux = MyNode(name='NUM_INTEIRO', type='NUM_INTEIRO', parent=pai)
        aux_val = MyNode(name=p[1], type='VALOR', parent=aux)
        p[1] = aux
    elif 'e' in valor.lower():
        aux = MyNode(name='NUM_NOTACAO_CIENTIFICA', type='NUM_NOTACAO_CIENTIFICA', parent=pai)
        aux_val = MyNode(name=p[1], type='VALOR', parent=aux)
        p[1] = aux
    else:
        aux = MyNode(name='NUM_PONTO_FLUTUANTE', type='NUM_PONTO_FLUTUANTE', parent=pai)
        aux_val = MyNode(name=p[1], type='VALOR', parent=aux)
        p[1] = aux


def p_chamada_funcao(p):
    """chamada_funcao : ID ABRE_PARENTESE lista_argumentos FECHA_PARENTESE"""

    pai = MyNode(name='chamada_funcao', type='CHAMADA_FUNCAO')
    p[0] = pai

    # FIX: len(p) é sempre 5 nessa regra, o else nunca executava. Condição removida.
    filho1 = MyNode(name='ID', type='ID', parent=pai)
    filho_id = MyNode(name=p[1], type='ID', parent=filho1)
    p[1] = filho1

    filho2 = MyNode(name='ABRE_PARENTESE', type='ABRE_PARENTESE', parent=pai)
    filho_sym = MyNode(name=p[2], type='SIMBOLO', parent=filho2)
    p[2] = filho2

    p[3].parent = pai

    filho4 = MyNode(name='FECHA_PARENTESE', type='FECHA_PARENTESE', parent=pai)
    filho_sym = MyNode(name=p[4], type='SIMBOLO', parent=filho4)
    p[4] = filho4


def p_lista_argumentos(p):
    """lista_argumentos : lista_argumentos VIRGULA expressao
                    | expressao
                    | vazio
        """
    pai = MyNode(name='lista_argumentos', type='LISTA_ARGUMENTOS')
    p[0] = pai

    if len(p) > 2:
        p[1].parent = pai

        filho2 = MyNode(name='VIRGULA', type='VIRGULA', parent=pai)
        filho_sym = MyNode(name=p[2], type='SIMBOLO', parent=filho2)
        p[2] = filho2

        p[3].parent = pai
    else:
        p[1].parent = pai


def p_lista_argumentos_error(p):
    """lista_argumentos : error VIRGULA expressao
        """
    print(error_handler.newError(check_key, 'ERR-SYN-LISTA-ARGUMENTOS'))
    error_line = p.lineno(2)
    father = MyNode(name='ERR-SYN-LISTA-ARGUMENTOS::{}'.format(error_line), type='ERROR')
    logging.error("Syntax error parsing lista_argumentos at line {}".format(error_line))
    parser.errok()
    p[0] = father


def p_vazio(p):
    """vazio : """

    pai = MyNode(name='vazio', type='VAZIO')
    p[0] = pai


def p_error(p):
    if p is None:
        print(error_handler.newError(check_key, "ERR-SYN-EOF-INESPERADO"))
    else:
        if not check_key:
            token = p
            line = token.lineno
            column = define_column(source_file, token.lexpos)
            print("Problema na linha {line}, coluna {column}, próximo ao token \'{token}\'".format(
                line=line, column=column, token=token.value))


# ══════════════════════════════════════════════
# PROGRAMA PRINCIPAL
# ══════════════════════════════════════════════

def main():

    global check_tpp
    global check_key
    global check_gentree
    # FIX: source_file declarado como global para p_error calcular coluna corretamente
    global source_file

    # FIX: era 'check_ttp' (typo), nunca resetava o global correto
    check_tpp = False
    check_key = False
    check_gentree = False
    
    for idx, arg in enumerate(sys.argv):
        aux = arg.split('.')
        if aux[-1] == 'tpp':
            check_tpp = True
            idx_tpp = idx

        if arg == "-k":
            check_key = True

        if arg == "-t":
            check_gentree = True

    if not check_key and len(sys.argv) < 2:
        raise TypeError(error_handler.newError(check_key, 'ERR-SYN-USE'))
    elif check_key and len(sys.argv) < 3:
        raise TypeError(error_handler.newError(check_key, 'ERR-SYN-USE'))

    if not check_tpp:
        raise IOError(error_handler.newError(check_key, 'ERR-SYN-NOT-TPP'))
    elif not os.path.exists(argv[idx_tpp]):
        raise IOError(error_handler.newError(check_key, 'ERR-SYN-FILE-NOT-EXISTS'))
    else:
        # Propaga o modo -k para o lexer usado internamente pelo parser.
        # Sem isto, erros léxicos encontrados durante tppparser.py -k
        # aparecem em português em vez de ERR-LEX-*.
        tpplex.check_key = check_key
        tpplex.lexer.lineno = 1

        data = open(argv[idx_tpp], encoding='utf-8')
        source_file = data.read()
        parser.parse(source_file)

    if root and root.children != ():
        # Árvore construída com sucesso
        if check_gentree:
            print(error_handler.newError(check_key, 'WAR-SYN-GEN-SYNTAX-TREE'))
            UniqueDotExporter(root).to_picture(argv[idx_tpp] + ".unique.ast.png")
            DotExporter(root).to_dotfile(argv[idx_tpp] + ".ast.dot")
            UniqueDotExporter(root).to_dotfile(argv[idx_tpp] + ".unique.ast.dot")
            with open(argv[idx_tpp] + "ascii_tree.txt", "w") as f:
                f.write(RenderTree(root, style=AsciiStyle()).by_attr())
            print(error_handler.newError(check_key, 'WAR-SYN-OUTPUT-FILE', file=argv[idx_tpp] + ".ast.png"))
            print(error_handler.newError(check_key, 'WAR-SYN-ANA-SUCCESS'))
        else:
            # Sem -t: reporta sucesso sem gerar arquivos gráficos
            print(error_handler.newError(check_key, 'WAR-SYN-GEN-SYNTAX-TREE'))
            print(error_handler.newError(check_key, 'WAR-SYN-ANA-SUCCESS'))
            print(error_handler.newError(check_key, 'WAR-SYN-OUTPUT-FILE'))
    else:
        print(error_handler.newError(check_key, "ERR-SYN-IRRECUPERAVEL"))
        print(error_handler.newError(check_key, 'WAR-SYN-NOT-GEN-SYNTAX-TREE'))


# Build the parser.
parser = yacc.yacc(method="LALR", optimize=True, start='programa', debug=True,
                   debuglog=log, errorlog=log, write_tables=False, tabmodule='tpp_parser_tab')

if __name__ == "__main__":

    # FIX: segundo except usava 'e' fora de escopo e era subclasse de Exception (redundante).
    # Unificado em um único bloco.
    try:
        main()
    except Exception as e:
        print(e)