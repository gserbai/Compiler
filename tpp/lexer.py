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
# O Lexer gera um arquivo "lex.log" com detalhes da execução para debug.
logging.basicConfig(
    level=logging.DEBUG,
    filename="lex.log",
    filemode="w",
    format="%(filename)10s:%(lineno)4d:%(message)s"
)
log = logging.getLogger()

# Instancia o gerenciador de erros usando o arquivo .properties
le = MyError('LexerErrors')

# -----------------------------------------------------------------------------
# 2. LISTA DE TOKENS E PALAVRAS RESERVADAS
# -----------------------------------------------------------------------------
tokens = [
    "ID",  # identificador
    # numerais
    "NUM_NOTACAO_CIENTIFICA",  # ponto flutuante em notaçao científica
    "NUM_PONTO_FLUTUANTE",     # ponto flutuante
    "NUM_INTEIRO",             # inteiro
    # operadores binarios
    "MAIS",         # +
    "MENOS",        # -
    "VEZES",        # *
    "DIVIDE",       # /
    "E",            # &&
    "OU",           # ||
    "DIFERENTE",    # <>
    "MENOR_IGUAL",  # <=
    "MAIOR_IGUAL",  # >=
    "MENOR",        # <
    "MAIOR",        # >
    "IGUAL",        # =
    # operadores unarios
    "NAO",          # !
    # simbolos
    "ABRE_PARENTESE",   # (
    "FECHA_PARENTESE",  # )
    "ABRE_COLCHETE",    # [
    "FECHA_COLCHETE",   # ]
    "VIRGULA",          # ,
    "DOIS_PONTOS",      # :
    "ATRIBUICAO",       # :=
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

# Adiciona as palavras reservadas à lista de tokens principal
tokens = tokens + list(reserved_words.values())

# -----------------------------------------------------------------------------
# 3. EXPRESSÕES REGULARES COMPLEXAS (Regras Básicas)
# -----------------------------------------------------------------------------
digito = r"([0-9])"
letra = r"([a-zA-ZáÁãÃàÀéÉíÍóÓõÕ])"
sinal = r"([\-\+]?)"

# Identificador: deve começar com uma letra
id = r"(" + letra + r"(" + digito + r"+|_|" + letra + r")*)"

# Inteiro: um ou mais dígitos
inteiro = r"\d+"

# Ponto Flutuante: Caminho 1 (com expoente) ou Caminho 2 (com ponto decimal)
flutuante = r'\d+[eE][-+]?\d+|(\.\d+|\d+\.\d*)([eE][-+]?\d+)?'

# Notação Científica: formato normalizado (ex: -3.14e+2)
notacao_cientifica = (r"(" + sinal + r"([1-9])\." + digito + r"+[eE]" + sinal + digito + r"+)")  # o mesmo que '(([-\+]?)([1-9])\.([0-9])+[eE]([-\+]?)([0-9]+))'


# -----------------------------------------------------------------------------
# 4. EXPRESSÕES REGULARES SIMPLES (Símbolos e Operadores)
# -----------------------------------------------------------------------------
t_MAIS = r'\+'
t_MENOS = r'-'
t_VEZES = r'\*'
t_DIVIDE = r'/'
t_ABRE_PARENTESE = r'\('
t_FECHA_PARENTESE = r'\)'
t_ABRE_COLCHETE = r'\['
t_FECHA_COLCHETE = r'\]'
t_VIRGULA = r','
t_ATRIBUICAO = r':='
t_DOIS_PONTOS = r':'

t_E = r'&&'
t_OU = r'\|\|'
t_NAO = r'!'

t_DIFERENTE = r'<>'
t_MENOR_IGUAL = r'<='
t_MAIOR_IGUAL = r'>='
t_MENOR = r'<'
t_MAIOR = r'>'
t_IGUAL = r'='

# -----------------------------------------------------------------------------
# 5. REGRAS DE AÇÃO PARA TOKENS (Funções do PLY)
# -----------------------------------------------------------------------------

@TOKEN(id)
def t_ID(token):
    # Verifica se o ID é uma palavra reservada; se for, atualiza o tipo do token
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

# Caracteres ignorados (espaços e tabs)
t_ignore = " \t"


#Old
##def t_COMENTARIO(token):
    #r"(\{((.|\n)*?)\})"
    #token.lexer.lineno += token.value.count("\n")
    #pass # Comentários são descartados silenciosamente
def t_COMENTARIO(token):
    r"\{"
    # Procura a próxima fecha-chave no restante do texto
    end_pos = token.lexer.lexdata.find('}', token.lexpos)

    if end_pos == -1:
        # Se não achou '}', chegou ao fim do arquivo sem fechar
        line = token.lineno
        column = define_column(token.lexer.lexdata, token.lexpos)
        message = le.newError(check_key, 'ERR-LEX-UNCLOSED-COMMENT', line, column)
        print(message)
        # Avança o lexer até o fim para parar a análise
        token.lexer.lexpos = len(token.lexer.lexdata)
    else:
        # Se achou, conta as quebras de linha dentro do comentário
        comment_text = token.lexer.lexdata[token.lexpos:end_pos+1]
        token.lexer.lineno += comment_text.count("\n")
        # Pula o conteúdo do comentário
        token.lexer.lexpos = end_pos + 1


# Quebras de linha: Mantém o controle correto das linhas do arquivo
def t_newline(token):
    r"\n+"
    token.lexer.lineno += len(token.value)

# Função auxiliar: Calcula a coluna do token para mensagens de erro precisas
def define_column(input, lexpos):
    begin_line = input.rfind("\n", 0, lexpos) + 1
    return (lexpos - begin_line) + 1

# Tratamento de Erros Léxicos: Captura caracteres não reconhecidos
def t_error(token):
    line = token.lineno
    column = define_column(token.lexer.lexdata, token.lexpos)
    # Chama a classe de erro passando a linha, coluna e o caractere inválido
    message = le.newError(check_key, 'ERR-LEX-INV-CHAR', line, column, valor=token.value[0])
    print(message)
    # Pula 1 caractere inválido e continua a análise
    token.lexer.skip(1)

# -----------------------------------------------------------------------------
# 6. CONSTRUÇÃO DO LEXER E FUNÇÕES DE EXECUÇÃO
# -----------------------------------------------------------------------------
# Constrói o analisador léxico sob a casca do PLY
lexer = lex.lex(optimize=True, debug=True, debuglog=log)

def main():
    global check_tpp
    global check_key

    check_tpp = False # Corrigido typo (era check_ttp)
    check_key = False
    idx_tpp = -1

    # Processa os argumentos de linha de comando
    for idx, arg in enumerate(sys.argv):
        aux = arg.split('.')
        if aux[-1] == 'tpp':
            check_tpp = True
            idx_tpp = idx
        if arg == "-k":
            check_key = True

    # Validações de uso e existência de arquivo
    # Se passou só o nome do script (len < 2) OU se passou só o script e a flag -k (len == 2)
    if len(sys.argv) < 2 or (len(sys.argv) == 2 and "-k" in sys.argv):
        raise TypeError(le.newError(check_key, 'ERR-LEX-USE'))

    if not check_tpp:
        raise IOError(le.newError(check_key, 'ERR-LEX-NOT-TPP'))
    elif not os.path.exists(sys.argv[idx_tpp]):
        raise IOError(le.newError(check_key, 'ERR-LEX-FILE-NOT-EXISTS'))
    else:
        # Abre e lê o arquivo .tpp com codificação segura
        with open(sys.argv[idx_tpp], 'r', encoding='utf-8') as data:
            source_file = data.read()
            lexer.input(source_file)

        # Laço principal de tokenização
        while True:
            tok = lexer.token()
            if not tok:
                break      # Fim do arquivo (EOF)
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
    try:
        main()
    except Exception as e:
        print(e)
