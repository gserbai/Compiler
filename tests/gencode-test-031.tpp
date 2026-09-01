{ insertion sort ajustado com sentinela }

inteiro: i, j, x, tam
inteiro: vet[11]

insert_sort()
  i := 2

  repita
    x := vet[i]
    j := i - 1
    vet[0] := x

    se x < vet[j] então
      repita
        vet[j + 1] := vet[j]
        j := j - 1
      até x >= vet[j]
    fim

    vet[j + 1] := x

    i := i + 1
  até i > tam
fim

printArray()
  inteiro: p

  p := 1

  repita
    escreva(vet[p])
    p := p + 1
  até p > tam
fim

inteiro principal()
  tam := 10

  vet[1] := 5
  vet[2] := 3
  vet[3] := 2
  vet[4] := 4
  vet[5] := 7
  vet[6] := 1
  vet[7] := 0
  vet[8] := 6
  vet[9] := 9
  vet[10] := 8

  insert_sort()

  printArray()

  retorna(0)
fim
