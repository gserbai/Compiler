import re  # Importa o módulo de Expressões Regulares (Regular Expressions) do Python

# 1. MAPEAMENTO DE REGRAS (TOKEN_SPECS)
# Esta lista define as "etiquetas" (nomes) e os "padrões" (regex) que o compilador busca.
# O Python tentará casar o texto seguindo a ordem desta lista.
TOKEN_SPECS = [
    ('NUMBER',   r'\d+'),           # Busca um ou mais dígitos (0-9)
    ('ID',       r'[a-zA-Z_]\w*'),  # Busca nomes de variáveis (começa com letra/_ e segue com letra/num)
    ('OP',       r'[+\-*/=]'),      # Busca os operadores matemáticos básicos e o de atribuição
    ('NEWLINE',  r'\n'),            # Identifica quebras de linha (útil para contar erros por linha)
    ('SKIP',     r'[ \t]+'),        # Identifica espaços e tabs (serão ignorados depois)
]

def tokenize(codigo):
    tokens = []  # Lista onde vamos guardar os tokens encontrados (nosso "output")
    
    # 2. CONSTRUÇÃO DA SUPER REGEX
    # Esta linha cria uma string gigante que junta todas as regras usando o operador '|' (OU).
    # O trecho (?P<NOME>padrao) cria um "grupo nomeado", permitindo saber qual regra venceu.
    regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_SPECS)
    
    # O laço for pede ao re.finditer: "Vá no 'codigo' e me traga o próximo pedaço que faz sentido"
    for match in re.finditer(regex, codigo):
    
    # Imagine que o scanner parou em cima do 'x'
    
    # 1. PERGUNTA: "Qual luz do painel acendeu?" 
    # O match.lastgroup olha para o (?P<NOME>) que deu certo.
    # No caso do 'x', ele retorna a string 'ID'.
             kind = match.lastgroup  
    
    # 2. PERGUNTA: "O que está escrito fisicamente nesse pedaço do papel?"
    # O match.group() retorna o texto bruto capturado.
    # No caso do 'x', ele retorna 'x'.
             value = match.group()   
    
    # Agora temos: kind = 'ID' e value = 'x'
    
    # 3. FILTRAGEM: "Eu devo ignorar isso?"
    # Se o kind for 'SKIP' (espaço/tab), a gente ignora.
    # Se for importante (como 'ID', 'OP' ou 'NUMBER'), a gente guarda.
             if kind != 'SKIP':
        
        # 4. ARMAZENAMENTO: "Anote no caderninho"
        # Criamos uma tupla (uma dupla fixa) e jogamos na nossa lista de tokens.
                  tokens.append((kind, value)) 
        
    # O laço termina aqui, o ponteiro do re.finditer pula o 'x' 
    # e vai procurar o próximo (que seria o espaço, depois o '=', etc.)