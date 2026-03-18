### 1. Análise Léxica (O Scanner - `scanner.l`)

É a fase de "alfabetização". O compilador lê o seu arquivo de texto e identifica o que é palavra, o que é número e o que é símbolo.

* **O que faz:** Agrupa caracteres em **Tokens**.
* **Exemplo:** Transforma `x = 10;` em `ID(x)`, `OP_ATRIB`, `CONST(10)`, `FIM_SENTENÇA`.
* **Ferramenta:** **Flex**.

### 2. Análise Sintática (O Parser - `parser.y`)

É a fase da "gramática". Ele verifica se a ordem dos tokens faz sentido segundo as regras da sua linguagem.

* **O que faz:** Organiza os tokens em uma estrutura hierárquica chamada **Árvore de Sintaxe Abstrata (AST)**.
* **Exemplo:** Verifica se você não escreveu `= x 10;` (que estaria gramaticalmente errado).
* **Ferramenta:** **Bison**.

### 3. Análise Semântica (A Lógica)

É a fase do "sentido". O compilador checa se o que você escreveu é lógico, mesmo que a gramática esteja certa.

* **O que faz:** Checa tipos (não pode somar `int` com `string`), verifica se as variáveis foram declaradas e gerencia a **Tabela de Símbolos**.
* **Exemplo:** Se você usar `x = y + 1`, ele confere se `y` existe e se é um número.

### 4. Geração de Código Intermediário (O IR - `codegen.cpp`)

Aqui é onde o **LLVM** brilha. Em vez de traduzir direto para o chip (RISC-V), você traduz para uma linguagem "meio-termo".

* **O que faz:** Transforma a sua AST em **LLVM IR** (uma linguagem que parece um assembly universal).
* **Vantagem:** O LLVM IR é fácil de otimizar e funciona em qualquer processador depois.

### 5. Otimização (O "Pulo do Gato")

O LLVM pega aquele código intermediário e tenta deixá-lo mais rápido e eficiente.

* **O que faz:** Remove código que nunca é usado, simplifica contas matemáticas e organiza os loops.
* **No seu caso:** É aqui que você poderia injetar as técnicas de **Approximate Computing** para economizar energia!

### 6. Geração de Código de Máquina (O Backend)

A fase final, onde o compilador "fala" a língua do hardware.

* **O que faz:** Traduz o LLVM IR para o **Assembly específico** (no seu caso, **RISC-V**).
* **Resultado:** Um arquivo `.s` ou um binário executável que roda no seu simulador ou placa.

---

### O resumo do resumo:

1. **Léxico:** Identifica as palavras.
2. **Sintático:** Monta a estrutura da frase (Árvore).
3. **Semântico:** Vê se a frase faz sentido lógico.
4. **IR (LLVM):** Traduz para uma língua "universal" (para otimizar).
5. **Backend:** Cospe o Assembly do **RISC-V**.


### Como compilar esse "monstro"?

Como você está no Linux, você vai precisar dos headers do LLVM. No Arch ou Ubuntu, você instala o pacote `llvm-dev`.

O comando de compilação é chatinho porque o LLVM tem muitas dependências, então você usa o `llvm-config`:

```bash
# 1. Gera o parser
bison -d parser.y -o parser.cpp

# 2. Gera o scanner
flex -o scanner.cpp scanner.l

# 3. Compila tudo junto
g++ main.cpp scanner.cpp parser.cpp codegen.cpp `llvm-config --cxxflags --ldflags --libs` -lpthread -lncurses -ldl -o meu_compilador

```

### O que isso faz?

Se você passar um arquivo `teste.c` com:

```c
int main() {
    return 42;
}

```

O seu compilador vai cuspir o **LLVM IR**. Para transformar isso em **x86**, basta rodar o comando do próprio LLVM:
`./meu_compilador teste.c | llc -march=x86-64 -o saida.s`

