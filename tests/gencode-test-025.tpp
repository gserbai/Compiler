{Maior do Vetor}

inteiro maiorvetor(inteiro:v[], inteiro:tam)
	inteiro: maior
	inteiro i:= 0
	maior := v[0]

	repita
		se v[i] > maior
			maior := v[i]
		i := i +1
	ate i = 5
	retorna maior

inteiro main()
	inteiro v[5] := {1,2,3,4,5}
	inteiro maior := maiorvetor(v,5)
	escreva(maior)
