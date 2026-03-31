TPP Language Support for VS Code
=================================

Syntax highlighting para TPP. Sem frescura.

FUNCIONALIDADES
---------------

  - Palavras-chave: se, então, senão, fim, repita, até
  - Tipos: inteiro, flutuante
  - I/O: leia, escreva, retorna
  - Operadores: + - * / := <> <= >= && || !
  - Números: inteiros, flutuantes, notação científica
  - Chamadas de função
  - Comentários: // e /* */
  - Snippets para estruturas comuns
  - Auto-fechamento de parênteses e colchetes


INSTALAÇÃO
----------

Não precisa de Node. Não precisa compilar nada. Só copiar.

  Linux/macOS:

    cp -r tpp-language ~/.vscode/extensions/

  Windows:

    Copie a pasta para %USERPROFILE%\.vscode\extensions\

Reinicie o VS Code. Abra um .tpp. Funciona.


INSTALAÇÃO VIA VSIX (opcional)
-------------------------------

Se por algum motivo você precisar do .vsix:

  1. Instale o vsce:

       npm install -g @vscode/vsce

  2. Empacote:

       vsce package

  3. No VS Code: Ctrl+Shift+P -> "Extensions: Install from VSIX..."

Isso requer Node.js v14+. Se não sabe o que é isso, use o método acima.


SNIPPETS
--------

  se          ->  se-então
  se-senao    ->  se-então-senão
  repita      ->  repita-até
  inteiro     ->  declaração de variável inteira
  flutuante   ->  declaração de variável flutuante
  vetor-int   ->  vetor inteiro
  funcao      ->  função sem retorno
  funcao-int  ->  função com retorno inteiro
  funcao-float -> função com retorno flutuante
  leia        ->  leia(var)
  escreva     ->  escreva(expr)
  retorna     ->  retorna(expr)


ESTRUTURA
---------

  tpp-language/
  ├── package.json                  manifesto da extensão
  ├── language-configuration.json   brackets, indentação
  ├── syntaxes/tpp.tmLanguage.json  gramática TextMate (regras do highlight)
  ├── snippets/tpp.json             snippets
  └── README                        este arquivo


COMO FUNCIONA
-------------

TextMate Grammar (.tmLanguage.json). Regex identificam tokens e atribuem
scopes semânticos (keyword.control.tpp, storage.type.tpp, etc). O tema de
cores do VS Code faz o resto.


---
Compiladores - UTFPR
Guilherme Saides Serbai - 2551802
