{ Exemplo TPP com fatorial, Fibonacci, vetores e números flutuantes }

inteiro fatorial (inteiro: n)
    inteiro: resultado
    resultado := 1
    repita
        resultado := resultado * n
        n := n - 1
    até n = 0
    retorna(resultado)
fim

inteiro fibonacci (inteiro: n)
    se n <= 1 então
        retorna(n)
    senão
        retorna(fibonacci(n - 1) + fibonacci(n - 2))
    fim
fim

flutuante media(flutuante: soma, inteiro: quantidade)
    retorna(soma / quantidade)
fim

inteiro principal ()
    inteiro: num
    inteiro: i
    flutuante: notas[5]
    flutuante: somaNotas
    flutuante: resultado

    { Lê e calcula o fatorial }
    leia(num)
    escreva(fatorial(num))

    { Lê o vetor de notas e acumula a soma }
    i := 0
    somaNotas := 0.0
    repita
        leia(notas[i])
        somaNotas := somaNotas + notas[i]
        i := i + 1
    até i = 5

    resultado := media(somaNotas, 5)
    escreva(resultado)

    { Testa operadores lógicos }
    se (num > 0) && (num < 100) então
        escreva(fibonacci(num))
    senão
        escreva(0)
    fim
    retorna(0)
fim
