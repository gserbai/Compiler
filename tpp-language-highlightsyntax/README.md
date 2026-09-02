# TPP Language Support for VS Code

Extension for **Syntax Highlighting** of the **TPP** language, used in the Compilers course.

## Features

- Keyword highlighting (`se`, `então`, `senão`, `fim`, `repita`, `até`)
- Type highlighting (`inteiro`, `flutuante`)
- I/O highlighting (`leia`, `escreva`, `retorna`)
- Operator highlighting (`+`, `-`, `*`, `/`, `:=`, `<>`, `<=`, `>=`, `&&`, `||`, `!`)
- Number highlighting (integers, floats, scientific notation)
- Function call highlighting
- Comment support (`{ ... }`)
- Snippets for common structures
- Auto-closing of parentheses, brackets and comment braces

The highlighting rules follow the compiler implementation: accented keywords such as `então`, `senão` and `até` are required, and TPP does not currently provide string literals.

See the repository's [TPP grammar and language guide](../GRAMATICA_TPP.md) for the accepted syntax and complete examples.

## Installation (Development Mode)

### Prerequisites

- [VS Code](https://code.visualstudio.com/) installed
- [Node.js](https://nodejs.org/) installed (v14+) only if doing VSIX installation

### Step by step

1. **Clone or extract** this package into a folder:
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
2. **Copy the folder** to the VS Code extensions directory:
- **Linux/macOS:**
     ```bash
     cp -r tpp-language ~/.vscode/extensions/
     ```
- **Windows:**
     ```
     Copy the folder to: %USERPROFILE%\.vscode\extensions\
     ```
3. **Restart VS Code**
4. **Open any `.tpp` file** and highlighting will be applied automatically.

---

### Installation via VSIX (Packaged)

If you want to generate an installable `.vsix` file:

1. Install `vsce`:
   ```bash
   npm install -g @vscode/vsce
   ```
2. Inside the project folder, run:
   ```bash
   vsce package
   ```
   This generates a `tpp-language-1.0.0.vsix` file.
3. In VS Code, press `Ctrl+Shift+P` and run:
   ```
   Extensions: Install from VSIX...
   ```
   Select the generated `.vsix` file.

---

## Available Snippets

| Prefix        | Description                      |
|---------------|----------------------------------|
| `se`          | if-then structure                |
| `se-senao`    | if-then-else structure           |
| `repita`      | repeat-until structure           |
| `inteiro`     | integer variable declaration     |
| `flutuante`   | float variable declaration       |
| `vetor-int`   | integer array declaration        |
| `funcao`      | function without return          |
| `funcao-int`  | function with integer return     |
| `funcao-float`| function with float return       |
| `leia`        | leia command                     |
| `escreva`     | escreva command                  |
| `retorna`     | retorna command                  |
| `:=`          | assignment                       |

## How it works

Highlighting is implemented via **TextMate Grammar** (`.tmLanguage.json`), the same standard used by all VS Code language extensions. The rules use **regular expressions** to identify tokens and assign semantic **scopes** (e.g. `keyword.control.tpp`, `storage.type.tpp`), which the VS Code color theme then colorizes.

---
Compilers - UTFPR — Guilherme Saides Serbai
