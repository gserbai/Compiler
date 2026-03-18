class CodeGenerator:
    def __init__(self):
        self.instrucoes = []

    def gerar(self, no):
        if isinstance(no, Numero):
            # Carrega imediato no registrador temporário t0
            self.instrucoes.append(f"li t0, {no.valor}")
        
        elif isinstance(no, BinOp):
            # Lógica recursiva: gera código para os dois lados e depois soma
            self.gerar(no.esquerda)
            self.instrucoes.append("mv t1, t0") # Salva resultado da esquerda
            self.gerar(no.direita)
            # t0 tem a direita, t1 tem a esquerda
            self.instrucoes.append(f"add t2, t1, t0")
            
        return "\n".join(self.instrucoes)