class Node:
    pass

class Numero(Node):
    def __init__(self, valor):
        self.valor = valor

class BinOp(Node):
    def __init__(self, esquerda, operador, direita):
        self.esquerda = esquerda
        self.operador = operador
        self.direita = direita

class Atribuicao(Node):
    def __init__(self, id_var, expressao):
        self.id_var = id_var
        self.expressao = expressao