{ quicksort ajustado }

inteiro: v[10]
inteiro: tam

inteiro partition(inteiro: e, inteiro: d)
  inteiro: pivo, i, j, aux

  pivo := v[d]
  i := e - 1
  j := e

  repita
    se v[j] <= pivo então
      i := i + 1

      aux := v[i]
      v[i] := v[j]
      v[j] := aux
    fim

    j := j + 1
  até j = d

  aux := v[i + 1]
  v[i + 1] := v[d]
  v[d] := aux

  retorna(i + 1)
fim

quick(inteiro: e, inteiro: d)
  inteiro: p

  se e < d então
    p := partition(e, d)
    quick(e, p - 1)
    quick(p + 1, d)
  fim
fim

printArray()
  inteiro: i

  i := 0

  repita
    escreva(v[i])
    i := i + 1
  até i = tam
fim

inteiro principal()
  tam := 10

  v[0] := 5
  v[1] := 3
  v[2] := 2
  v[3] := 4
  v[4] := 7
  v[5] := 1
  v[6] := 0
  v[7] := 6
  v[8] := 9
  v[9] := 8

  quick(0, 9)

  printArray()

  retorna(0)
fim
