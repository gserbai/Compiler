{ Programa para testar erros léxicos no Lexer }
inteiro principal()
inteiro valor := 10
flutuante taxa := 2.5
    { 1. Teste de Caractere Inválido (Cifrão) }
valor := valor + $50
    { 2. Teste de Caractere Inválido (Arroba) }
taxa := taxa @ 2.0
    { 3. Caractere Inválido (Cerquilha) }
# escreva(valor)
    { 4. Caractere Inválido (Aspas) }
escreva(valor)
    { 5. Operadores invalidos }
valor := valor % 2
valor := valor & 2
valor := valor | 2
    { 6. Comentário não fechado - SEMPRE POR ÚLTIMO }
    {Este comentário nunca fecha...