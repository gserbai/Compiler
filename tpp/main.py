from lexer import tokenize
from parser import Parser
from codegen import CodeGenerator

def main():
    codigo_fonte = "10 + 20"
    
    # 1. Lexer
    tokens = tokenize(codigo_fonte)
    
    # 2. Parser
    parser = Parser(tokens)
    ast = parser.parse_expression()
    
    # 3. CodeGen
    cg = CodeGenerator()
    resultado_asm = cg.gerar(ast)
    
    print("--- Assembly Gerado ---")
    print(resultado_asm)

if __name__ == "__main__":
    main()