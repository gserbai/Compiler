#!/usr/bin/env bash
set -euo pipefail

# Script para gerar LLVM IR (.ll) e compilar executáveis x86 dos testes TPP.
# Uso:
#   ./gerar_executaveis_tpp.sh
# Deve ser executado na raiz do projeto geracao-de-codigo-gserbai.

if [[ ! -f "tppgencode.py" ]]; then
    echo "Erro: execute este script na raiz do projeto, onde está o arquivo tppgencode.py."
    exit 1
fi

if [[ ! -d "tests" ]]; then
    echo "Erro: pasta tests/ não encontrada."
    exit 1
fi

if ! command -v clang >/dev/null 2>&1; then
    echo "Erro: clang não encontrado. Instale com: sudo apt install clang llvm lld"
    exit 1
fi

# Ativa o venv automaticamente se existir e ainda não estiver ativo.
if [[ -d "venv" && -z "${VIRTUAL_ENV:-}" ]]; then
    source venv/bin/activate
fi

mkdir -p build/executaveis

# Remove LLVM IR antigo para evitar confusão.
rm -f tests/*.ll

echo "==> Gerando arquivos LLVM IR (.ll)..."
for src in tests/*.tpp; do
    echo "Gerando IR: $src"
    # Alguns testes podem ser casos inválidos de sintaxe/semântica e não gerar .ll.
    # Por isso o script continua mesmo se algum caso não produzir IR.
    python tppgencode.py "$src" >/dev/null || true
done

shopt -s nullglob
ll_files=(tests/*.ll)

if (( ${#ll_files[@]} == 0 )); then
    echo "Nenhum arquivo .ll foi gerado. Verifique o tppgencode.py."
    exit 1
fi

echo

echo "==> Compilando .ll para executáveis x86..."
for ll in "${ll_files[@]}"; do
    base=$(basename "$ll")
    exe_name="${base%.tpp.ll}"
    exe_path="build/executaveis/$exe_name"

    echo "Compilando: $ll -> $exe_path"
    clang -Wno-override-module "$ll" -o "$exe_path"
done

echo

echo "==> Executáveis gerados em build/executaveis/:"
ls -lh build/executaveis/

echo

echo "Exemplo de execução:"
echo "  ./build/executaveis/gencode-test-002"
echo "  echo $?"
