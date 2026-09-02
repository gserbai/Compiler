# Gramática e guia da linguagem TPP

Este documento descreve a linguagem aceita pela implementação atual deste compilador. Ele foi reconstruído a partir das regras léxicas de `tpplex.py`, das produções de `tppparser.py`, da análise de `tppsema.py`, do gerador LLVM em `tppgencode.py` e dos programas presentes em `tests/`.

A gramática usada no projeto foi fornecida pelo Prof. Dr. Rogério Aparecido Gonçalves na disciplina de Compiladores da UTFPR – Campus Campo Mourão. Este arquivo é um guia prático da implementação do repositório, não uma substituição do material oficial da disciplina.

## Primeiro programa

Todo programa executável deve possuir uma função chamada `principal`. Um programa mínimo é:

```tpp
inteiro principal()
    retorna(0)
fim
```

Salve o conteúdo em um arquivo com extensão `.tpp`, por exemplo `programa.tpp`.

Características importantes da escrita TPP:

- as palavras reservadas são minúsculas;
- os acentos de `então`, `senão` e `até` são obrigatórios;
- uma atribuição usa `:=`, enquanto uma comparação de igualdade usa `=`;
- não existem chaves de bloco nem ponto e vírgula;
- a indentação e as quebras de linha facilitam a leitura, mas não delimitam comandos;
- comentários são escritos entre `{` e `}`.

## Elementos léxicos

### Palavras reservadas

| Grupo | Palavras |
| --- | --- |
| Tipos | `inteiro`, `flutuante` |
| Condicional | `se`, `então`, `senão`, `fim` |
| Repetição | `repita`, `até` |
| Funções | `retorna` |
| Entrada e saída | `leia`, `escreva` |

As palavras reservadas diferenciam maiúsculas de minúsculas. Por exemplo, `inteiro` é um tipo, mas `Inteiro` é tratado como identificador.

### Identificadores

Um identificador começa com uma letra. Depois dela, pode conter letras, algarismos e `_`:

```text
letra (letra | algarismo | "_")*
```

Exemplos válidos:

```text
x
total
nota_final
fibonacci2
```

O conjunto exato reconhecido pelo lexer é:

```text
[A-Za-záÁãÃàÀéÉíÍóÓõÕ][A-Za-z0-9_áÁãÃàÀéÉíÍóÓõÕ]*
```

Letras como `ç`, `ú` e as que possuem acento circunflexo não são aceitas em identificadores. Para nomes de variáveis e funções portáveis, prefira letras ASCII sem acentos.

### Números

São reconhecidos:

| Categoria | Exemplos |
| --- | --- |
| Inteiro | `0`, `10`, `2048` |
| Ponto flutuante | `0.0`, `3.14`, `.5`, `2.` |
| Notação científica | `1e3`, `2.5E-4`, `-3.14e+2` |

Use os algarismos ASCII de `0` a `9`. A eventual aceitação de outros caracteres numéricos pelo mecanismo de expressões regulares do Python não faz parte da linguagem documentada.

Valores negativos normalmente são formados pelo operador unário `-`. Existe uma particularidade no lexer atual: diante da forma científica decimal, o sinal pode ser incorporado ao próprio número mesmo quando existe espaço. Em uma subtração desse tipo, use parênteses:

```tpp
resultado := a - (3.14e2)
```

Sem os parênteses, tanto `a-3.14e2` quanto `a - 3.14e2` podem perder o token de subtração e causar erro sintático.

### Comentários

Comentários podem ocupar uma ou várias linhas:

```tpp
{ comentário de uma linha }

{
  comentário com
  várias linhas
}
```

Comentários não podem ser aninhados. Os formatos `// comentário` e `/* comentário */` não fazem parte da linguagem aceita pelo compilador.

## Tipos e declarações

A implementação possui dois tipos numéricos:

- `inteiro`: inteiro de 32 bits no LLVM IR;
- `flutuante`: número de dupla precisão no LLVM IR.

Declarações usam o tipo seguido de `:`:

```tpp
inteiro: idade
inteiro: a, b, resultado
flutuante: media
```

A declaração e a atribuição são comandos separados:

```tpp
inteiro: quantidade
quantidade := 10
```

Não escreva `inteiro: quantidade := 10`, pois essa forma não pertence à gramática.

Variáveis podem ser globais ou locais a uma função:

```tpp
inteiro: contador_global

inteiro principal()
    inteiro: contador_local
    contador_global := 1
    contador_local := 2
    retorna(0)
fim
```

Inicialize variáveis globais dentro de `principal` ou de outra função. Embora o parser reconheça uma atribuição no nível global, o gerador LLVM atual não emite esse comando como inicialização global.

## Vetores

Os índices são escritos entre colchetes:

```tpp
inteiro: valores[10]

valores[0] := 25
escreva(valores[0])
```

Para a geração LLVM atual, declare cada dimensão com um literal inteiro positivo. O índice usado no acesso deve ser do tipo `inteiro`. Não há verificação de limites em tempo de execução.

Use, por enquanto, vetores unidimensionais. O parser reconhece matrizes e parâmetros vetoriais como `inteiro: valores[]`, mas essas duas formas ainda não funcionam de ponta a ponta na análise semântica e no back-end LLVM. Prefira vetores globais ou vetores locais unidimensionais acessados diretamente.

## Funções

Não existe uma palavra reservada `função`. Uma função começa diretamente pelo tipo de retorno, pelo nome e pelos parâmetros:

```tpp
inteiro soma(inteiro: a, inteiro: b)
    retorna(a + b)
fim
```

Uma função sem valor de retorno omite o tipo:

```tpp
mostraDobro(inteiro: valor)
    escreva(valor * 2)
fim
```

Chamadas usam a forma habitual:

```tpp
resultado := soma(10, 20)
mostraDobro(resultado)
```

Regras práticas:

- parâmetros usam `tipo: nome`;
- os parâmetros são separados por vírgula;
- `retorna(expressao)` exige parênteses;
- uma função tipada deve possuir um retorno compatível;
- funções podem chamar funções declaradas mais adiante;
- recursão é permitida;
- `principal` não deve receber parâmetros nem ser chamada por outra função.

Use preferencialmente esta assinatura de entrada:

```tpp
inteiro principal()
    retorna(0)
fim
```

## Entrada e saída

`leia` recebe uma variável ou posição de vetor:

```tpp
leia(idade)
leia(valores[i])
```

`escreva` recebe uma expressão numérica:

```tpp
escreva(idade)
escreva(a + b)
escreva(soma(a, b))
```

A implementação atual não possui literais de texto. Portanto, construções como `escreva("resultado")` não são válidas.

## Condicional

Um condicional simples termina com `fim`:

```tpp
se idade >= 18 então
    escreva(1)
fim
```

O ramo alternativo usa `senão`:

```tpp
se valor >= 0 então
    escreva(valor)
senão
    escreva(-valor)
fim
```

Condicionais podem ser aninhados. Parênteses ao redor da condição são opcionais, mas ajudam a deixar expressões lógicas mais claras.

## Repetição

TPP possui o laço `repita ... até`. O corpo executa pelo menos uma vez e o laço termina quando a condição se torna verdadeira:

```tpp
inteiro: i
i := 0

repita
    escreva(i)
    i := i + 1
até i = 10
```

Não existem os comandos `para` e `enquanto` na implementação atual.

## Operadores

| Categoria | Operadores | Observação |
| --- | --- | --- |
| Atribuição | `:=` | armazena o valor na variável à esquerda |
| Aritméticos | `+`, `-`, `*`, `/` | funcionam com inteiros e flutuantes |
| Relacionais | `<`, `>`, `=`, `<>`, `<=`, `>=` | produzem uma condição |
| Lógicos | `&&`, `\|\|`, `!` | e, ou e negação |

O operador `%` não é reconhecido. Para evitar ambiguidades, use parênteses ao combinar operadores lógicos e relacionais.

TPP usa `=` em comparações e `<>` para diferença. Os operadores `==` e `!=` de outras linguagens não são válidos.

Da maior para a menor precedência, a gramática organiza as expressões assim:

1. parênteses, chamadas, variáveis, índices e números;
2. operadores unários `+`, `-` e `!`;
3. multiplicação e divisão `*`, `/`;
4. soma e subtração `+`, `-`;
5. relacionais `<`, `>`, `=`, `<>`, `<=`, `>=`;
6. lógicos `&&` e `||`;
7. atribuição `:=`.

`&&` e `||` possuem o mesmo nível de precedência nesta implementação e não realizam curto-circuito no LLVM IR gerado. Use parênteses quando a ordem for importante.

Em uma condição, zero é falso e qualquer valor numérico diferente de zero é verdadeiro.

## Gramática em EBNF

Na notação abaixo, texto entre aspas representa um terminal da linguagem, `[ item ]` representa um item opcional e `{ item }` representa repetição. Esses colchetes e chaves pertencem à notação EBNF; não devem ser copiados literalmente para um programa TPP.

```ebnf
programa               = declaracao , { declaracao } ;

declaracao             = declaracao_variaveis
                       | atribuicao
                       | declaracao_funcao ;

declaracao_variaveis   = tipo , ":" , lista_variaveis ;
lista_variaveis        = variavel , { "," , variavel } ;
variavel               = identificador , { "[" , expressao , "]" } ;

tipo                   = "inteiro" | "flutuante" ;

declaracao_funcao      = [ tipo ] , cabecalho ;
cabecalho              = identificador , "(" , [ lista_parametros ] , ")" ,
                         corpo , "fim" ;
lista_parametros       = parametro , { "," , parametro } ;
parametro              = tipo , ":" , identificador , { "[" , "]" } ;

corpo                  = { acao } ;
acao                   = expressao
                       | declaracao_variaveis
                       | condicional
                       | repeticao
                       | leitura
                       | escrita
                       | retorno ;

condicional            = "se" , expressao , "então" , corpo ,
                         [ "senão" , corpo ] , "fim" ;
repeticao              = "repita" , corpo , "até" , expressao ;
leitura                = "leia" , "(" , variavel , ")" ;
escrita                = "escreva" , "(" , expressao , ")" ;
retorno                = "retorna" , "(" , expressao , ")" ;

expressao              = atribuicao | expressao_logica ;
atribuicao             = variavel , ":=" , expressao ;

expressao_logica       = expressao_simples ,
                         { operador_logico , expressao_simples } ;
expressao_simples      = expressao_aditiva ,
                         { operador_relacional , expressao_aditiva } ;
expressao_aditiva      = expressao_multiplicativa ,
                         { operador_soma , expressao_multiplicativa } ;
expressao_multiplicativa = expressao_unaria ,
                           { operador_multiplicacao , expressao_unaria } ;
expressao_unaria       = fator | operador_unario , fator ;

fator                  = "(" , expressao , ")"
                       | variavel
                       | chamada_funcao
                       | numero ;

chamada_funcao         = identificador , "(" , [ lista_argumentos ] , ")" ;
lista_argumentos       = expressao , { "," , expressao } ;

identificador          = ID ;
numero                 = NUM_INTEIRO
                       | NUM_PONTO_FLUTUANTE
                       | NUM_NOTACAO_CIENTIFICA ;

operador_logico        = "&&" | "||" ;
operador_relacional    = "<" | ">" | "=" | "<>" | "<=" | ">=" ;
operador_soma          = "+" | "-" ;
operador_multiplicacao = "*" | "/" ;
operador_unario        = "+" | "-" | "!" ;
```

Essa EBNF apresenta a forma canônica destinada ao usuário. O parser contém regras adicionais de recuperação de erro e algumas ambiguidades decorrentes da ausência de terminadores de comando; elas não definem novas construções recomendadas da linguagem.

## Exemplo completo

```tpp
{ Lê dois inteiros, soma e apresenta o valor absoluto do resultado }

inteiro soma(inteiro: a, inteiro: b)
    retorna(a + b)
fim

inteiro principal()
    inteiro: a, b, resultado

    leia(a)
    leia(b)
    resultado := soma(a, b)

    se resultado >= 0 então
        escreva(resultado)
    senão
        escreva(-resultado)
    fim

    retorna(0)
fim
```

Outros exemplos válidos podem ser encontrados em `tests/`, especialmente:

- `gencode-test-012.tpp`: entrada, saída e função;
- `gencode-test-016.tpp`: vetores e repetição;
- `gencode-test-018.tpp`: condicional, repetição e função;
- `gencode-test-023.tpp`: recursão e Fibonacci;
- `gencode-test-031.tpp` e `gencode-test-032.tpp`: algoritmos de ordenação.

Os 25 exemplos que geram LLVM IR válido são `gencode-test-002.tpp` até `gencode-test-024.tpp`, além de `gencode-test-031.tpp` e `gencode-test-032.tpp`. Os casos `001` e `025` até `030` são entradas inválidas mantidas para exercitar erros; um arquivo de teste não deve ser considerado parte da linguagem apenas por possuir a extensão `.tpp`.

## Verificar e compilar um programa

Execute cada etapa para localizar problemas com mais facilidade:

```bash
# Tokens
python tpplex.py programa.tpp

# Sintaxe
python tppparser.py programa.tpp

# Semântica
python tppsema.py programa.tpp

# LLVM IR: cria programa.tpp.ll quando não existem erros
python tppgencode.py programa.tpp
```

Se `tppgencode.py` não criar o arquivo `.ll`, execute primeiro o parser e o analisador semântico, pois o gerador de código trabalha silenciosamente quando essas etapas encontram erros.

Para as árvores e o CFG:

```bash
# AST completa
python tppparser.py -t programa.tpp

# AST podada pela análise semântica
python tppsema.py -t programa.tpp

# CFG por função
python gerar_cfg.py programa.tpp
```

Consulte o `README.md` para instalação das dependências, geração do executável nativo e formatos gráficos disponíveis.

## Limitações atuais

Esta é uma linguagem e uma implementação educacionais. Atualmente não fazem parte do subconjunto utilizável:

- textos, caracteres e interpolação;
- tipos booleanos explícitos;
- módulos, classes ou registros;
- `para`, `enquanto`, `caso` ou `escolha`;
- operador de resto `%`;
- inicializadores de vetores como `{1, 2, 3}`, pois `{...}` representa comentário;
- comentários `//` ou `/* ... */`;
- inicialização executável no escopo global;
- parâmetros vetoriais e vetores multidimensionais no fluxo completo até LLVM;
- verificação dinâmica dos limites de vetores.

Os blocos `se` e `repita` não criam um novo escopo: uma variável declarada dentro deles pertence à função inteira. A análise de inicialização e retorno não acompanha todos os caminhos de controle; inicialize cada variável antes do uso em todos os caminhos e faça funções tipadas retornarem em todas as alternativas.

Use espaços ao redor dos operadores, uma ação por linha, parênteses em expressões compostas e as formas apresentadas neste guia. Essas convenções evitam as ambiguidades conhecidas do parser e tornam o código TPP mais fácil de ler.
