# TPP Language Support for VS Code

Extensão de **Syntax Highlighting** para a linguagem **TPP**.

## Funcionalidades

- Destaque de palavras-chave (`se`, `então`, `senão`, `fim`, `repita`, `até`)
- Destaque de tipos (`inteiro`, `flutuante`)
- Destaque de I/O (`leia`, `escreva`, `retorna`)
- Destaque de operadores (`+`, `-`, `*`, `/`, `:=`, `<>`, `<=`, `>=`, `&&`, `||`, `!`)
- Destaque de números (inteiros, flutuantes, notação científica)
- Destaque de chamadas de função
- Suporte a comentários (`//` e `/* */`)
- Snippets para estruturas comuns
- Auto-fechamento de parênteses e colchetes

## Instalação (Modo Desenvolvimento)

### Pré-requisitos
- [VS Code](https://code.visualstudio.com/) instalado
- !!! [Node.js](https://nodejs.org/) instalado (v14+) se quiser via VSIX !!!

### Passo a passo

1. **Clone ou extraia** este pacote em uma pasta:
   ```
   tpp-language/
   ├── package.json
   ├── language-configuration.json
   ├── syntaxes/
   │   └── tpp.tmLanguage.json
   ├── snippets/
   │   └── tpp.json
   └── README.md
   ```

2. **Copie a pasta** para o diretório de extensões do VS Code:

   - **Linux/macOS:**
     ```bash
     cp -r tpp-language ~/.vscode/extensions/
     ```
   - **Windows:**
     ```
     Copie a pasta para: %USERPROFILE%\.vscode\extensions\
     ```

3. **Reinicie o VS Code**

4. **Pronto!** Abra qualquer arquivo `.tpp` e o highlight será aplicado automaticamente.

---

### Instalação via VSIX (Empacotado)

Se quiser gerar um arquivo `.vsix` instalável:

1. Instale o `vsce`:
   ```bash
   npm install -g @vscode/vsce
   ```

2. Dentro da pasta do projeto, execute:
   ```bash
   vsce package
   ```
   Isso gera um arquivo `tpp-language-1.0.0.vsix`.

3. No VS Code, pressione `Ctrl+Shift+P` e execute:
   ```
   Extensions: Install from VSIX...
   ```
   Selecione o arquivo `.vsix` gerado.

---

## Snippets disponíveis

| Prefixo       | Descrição                        |
|---------------|----------------------------------|
| `se`          | Estrutura se-então               |
| `se-senao`    | Estrutura se-então-senão         |
| `repita`      | Estrutura repita-até             |
| `inteiro`     | Declaração de variável inteira   |
| `flutuante`   | Declaração de variável flutuante |
| `vetor-int`   | Declaração de vetor inteiro      |
| `funcao`      | Função sem retorno               |
| `funcao-int`  | Função com retorno inteiro       |
| `funcao-float`| Função com retorno flutuante     |
| `leia`        | Comando leia                     |
| `escreva`     | Comando escreva                  |
| `retorna`     | Comando retorna                  |

## Exemplo de código TPP destacado

```tpp
// Programa fatorial em TPP
inteiro fatorial (inteiro: n)
    inteiro: resultado
    resultado := 1
    repita
        resultado := resultado * n
        n := n - 1
    até n = 0
    retorna(resultado)
fim

inteiro principal ()
    inteiro: num
    leia(num)
    escreva(fatorial(num))
fim
```

## Estrutura do projeto

```
tpp-language/
├── package.json               # Manifesto da extensão
├── language-configuration.json # Config de brackets, indentação
├── syntaxes/
│   └── tpp.tmLanguage.json    # Gramática TextMate (regras do highlight)
├── snippets/
│   └── tpp.json               # Snippets de código
└── README.md                  # Este arquivo
```

## Como funciona

O highlight é implementado via **TextMate Grammar** (`.tmLanguage.json`), o mesmo padrão usado por todas as extensões de linguagem do VS Code. As regras usam **expressões regulares** para identificar tokens e atribuir **scopes** semânticos (ex: `keyword.control.tpp`, `storage.type.tpp`), que o tema de cores do VS Code então colore.

---

Desenvolvido para a disciplina de **Compiladores** — UTFPR by Guilherme Saides Serbai - 2551802
