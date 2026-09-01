import sys
import os
import logging
from sys import argv
import ply.lex as lex
from ply.lex import TOKEN
from myerror import MyError

# -----------------------------------------------------------------------------
# 1. CONFIGURAÇÃO DE LOG E TRATAMENTO DE ERROS
# -----------------------------------------------------------------------------
logging.basicConfig(
    level=logging.DEBUG,
    filename="lex.log",
    filemode="w",
    format="%(filename)10s:%(lineno)4d:%(message)s"
)
log = logging.getLogger()

le = MyError('LexerErrors')

check_tpp = False
check_key = False

# -----------------------------------------------------------------------------
# 2. LISTA DE TOKENS E PALAVRAS RESERVADAS
# -----------------------------------------------------------------------------
tokens = [
    "ID",
    "NUM_NOTACAO_CIENTIFICA",
    "NUM_PONTO_FLUTUANTE",
    "NUM_INTEIRO",
    "MAIS",
    "MENOS",
    "VEZES",
    "DIVIDE",
    "E",
    "OU",
    "DIFERENTE",
    "MENOR_IGUAL",
    "MAIOR_IGUAL",
    "MENOR",
    "MAIOR",
    "IGUAL",
    "NAO",
    "ABRE_PARENTESE",
    "FECHA_PARENTESE",
    "ABRE_COLCHETE",
    "FECHA_COLCHETE",
    "VIRGULA",
    "DOIS_PONTOS",
    "ATRIBUICAO",
]

reserved_words = {
    "se": "SE",
    "então": "ENTAO",
    "senão": "SENAO",
    "fim": "FIM",
    "repita": "REPITA",
    "flutuante": "FLUTUANTE",
    "retorna": "RETORNA",
    "até": "ATE",
    "leia": "LEIA",
    "escreva": "ESCREVA",
    "inteiro": "INTEIRO",
}

tokens = tokens + list(reserved_words.values())

# -----------------------------------------------------------------------------
# 3. EXPRESSÕES REGULARES COMPLEXAS
# -----------------------------------------------------------------------------
digito = r"([0-9])"
letra  = r"([a-zA-ZáÁãÃàÀéÉíÍóÓõÕ])"
sinal  = r"([\-\+]?)"

# Identificador: deve começar com uma letra
id = r"(" + letra + r"(" + digito + r"+|_|" + letra + r")*)"

# Inteiro: um ou mais dígitos
inteiro = r"\d+"

# Ponto Flutuante: com expoente OU com ponto decimal
flutuante = r'\d+[eE][-+]?\d+|(\.\d+|\d+\.\d*)([eE][-+]?\d+)?'

# Notação Científica: formato normalizado (ex: -3.14e+2)
notacao_cientifica = (
    r"(" + sinal + r"([1-9])\." + digito + r"+[eE]" + sinal + digito + r"+)"
)

# -----------------------------------------------------------------------------
# 4. EXPRESSÕES REGULARES SIMPLES (Símbolos e Operadores)
# -----------------------------------------------------------------------------
t_MAIS            = r'\+'
t_MENOS           = r'-'
t_VEZES           = r'\*'
t_DIVIDE          = r'/'
t_ABRE_PARENTESE  = r'\('
t_FECHA_PARENTESE = r'\)'
t_ABRE_COLCHETE   = r'\['
t_FECHA_COLCHETE  = r'\]'
t_VIRGULA         = r','
t_ATRIBUICAO      = r':='
t_DOIS_PONTOS     = r':'

t_E   = r'&&'
t_OU  = r'\|\|'
t_NAO = r'!'

t_DIFERENTE   = r'<>'
t_MENOR_IGUAL = r'<='
t_MAIOR_IGUAL = r'>='
t_MENOR       = r'<'
t_MAIOR       = r'>'
t_IGUAL       = r'='

# -----------------------------------------------------------------------------
# 5. REGRAS DE AÇÃO PARA TOKENS (Funções do PLY)
# -----------------------------------------------------------------------------

@TOKEN(id)
def t_ID(token):
    # Palavras reservadas têm precedência sobre identificadores
    token.type = reserved_words.get(token.value, "ID")
    return token

@TOKEN(notacao_cientifica)
def t_NUM_NOTACAO_CIENTIFICA(token):
    return token

@TOKEN(flutuante)
def t_NUM_PONTO_FLUTUANTE(token):
    return token

@TOKEN(inteiro)
def t_NUM_INTEIRO(token):
    return token

# Caracteres ignorados
t_ignore = " \t"


def t_COMENTARIO(token):
    r"\{"
    # Busca linear pela fecha-chave: mais rápido que regex (.|\n)*? em arquivos grandes
    end_pos = token.lexer.lexdata.find('}', token.lexpos)

    if end_pos == -1:
        # Comentário não fechado — erro léxico com posição exata
        line   = token.lineno
        column = define_column(token.lexer.lexdata, token.lexpos)
        message = le.newError(check_key, 'ERR-LEX-UNCLOSED-COMMENT', line, column)
        print(message)
        # Avança até o fim do arquivo para encerrar a análise
        token.lexer.lexpos = len(token.lexer.lexdata)
    else:
        # Conta quebras de linha dentro do comentário para manter lineno correto
        comment_text = token.lexer.lexdata[token.lexpos:end_pos + 1]
        token.lexer.lineno += comment_text.count("\n")
        token.lexer.lexpos = end_pos + 1


def t_newline(token):
    r"\n+"
    token.lexer.lineno += len(token.value)


def define_column(input, lexpos):
    begin_line = input.rfind("\n", 0, lexpos) + 1
    return (lexpos - begin_line) + 1


def t_error(token):
    line   = token.lineno
    column = define_column(token.lexer.lexdata, token.lexpos)
    message = le.newError(check_key, 'ERR-LEX-INV-CHAR', line, column, valor=token.value[0])
    print(message)
    token.lexer.skip(1)

# -----------------------------------------------------------------------------
# 6. CONSTRUÇÃO DO LEXER
# -----------------------------------------------------------------------------
lexer = lex.lex(optimize=True, debug=True, debuglog=log)

# -----------------------------------------------------------------------------
# 7. FUNÇÕES DE EXECUÇÃO
# -----------------------------------------------------------------------------

def main():
    global check_tpp
    global check_key

    # FIX: era 'check_ttp' (typo), nunca resetava o global corretamente
    check_tpp = False
    check_key = False
    idx_tpp   = -1

    for idx, arg in enumerate(sys.argv):
        aux = arg.split('.')
        if aux[-1] == 'tpp':
            check_tpp = True
            idx_tpp   = idx
        if arg == "-k":
            check_key = True

    # Valida uso: precisa de pelo menos o arquivo .tpp (e -k se vier junto)
    if len(sys.argv) < 2 or (len(sys.argv) == 2 and "-k" in sys.argv):
        raise TypeError(le.newError(check_key, 'ERR-LEX-USE'))

    if not check_tpp:
        raise IOError(le.newError(check_key, 'ERR-LEX-NOT-TPP'))
    elif not os.path.exists(sys.argv[idx_tpp]):
        raise IOError(le.newError(check_key, 'ERR-LEX-FILE-NOT-EXISTS'))
    else:
        with open(sys.argv[idx_tpp], 'r', encoding='utf-8') as data:
            source_file = data.read()
        lexer.input(source_file)

        while True:
            tok = lexer.token()
            if not tok:
                break
            print(tok.type)


def test(pdata):
    with open(pdata, 'r', encoding='utf-8') as data:
        source_file = data.read()
    lexer.input(source_file)

    s = ""
    while True:
        tok = lexer.token()
        if not tok:
            break
        s += str(tok.type) + '\n'
    return s


if __name__ == "__main__":
    # FIX: segundo except com 'e' fora de escopo removido — unificado em um bloco só
    try:
        main()
    except Exception as e:
        print(e)