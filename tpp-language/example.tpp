// Example to program in TPP — Factorial and Fibonacci
// Demonstrated all the builds from language

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

flutuante media (flutuante: A[], inteiro: tam)
    flutuante: soma
    inteiro: i
    soma := 0.0
    i := 0
    repita
        soma := soma + A[i]
        i := i + 1
    até i = tam
    retorna(soma / tam)
fim

inteiro principal ()
    inteiro: num
    inteiro: i
    flutuante: notas[5]
    flutuante: resultado

    // Lê e calcula fatorial
    leia(num)
    escreva(fatorial(num))

    // Lê vetor de notas
    i := 0
    repita
        leia(notas[i])
        i := i + 1
    até i = 5

    resultado := media(notas, 5)
    escreva(resultado)

    // Teste de operadores lógicos
    se (num > 0) && (num < 100) então
        escreva(fibonacci(num))
    senão
        escreva(0)
    fim
fim
