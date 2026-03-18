from ast_nodes import Numero, BinOp, Atribuicao

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self): # Olha o token atual sem consumir
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consume(self): # Pega o token e avança
        token = self.peek()
        self.pos += 1
        return token

    def parse_expression(self):
        # Exemplo simplificado para: numero + numero
        esquerda = Numero(self.consume()[1])
        operador = self.consume()[1]
        direita = Numero(self.consume()[1])
        return BinOp(esquerda, operador, direita)