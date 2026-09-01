#!/usr/bin/env bash
set -euo pipefail

# Script para gerar LLVM IR (.ll) e compilar executáveis nativos dos testes TPP.
# Uso:
#   ./gerar_executaveis_tpp.sh
# Deve ser executado na raiz do projeto.

if [[ ! -f "tppgencode.py" ]]; then
    echo "Erro: execute este script na raiz do projeto, onde está o arquivo tppgencode.py."
    exit 1
fi

if [[ ! -d "tests" ]]; then
    echo "Erro: pasta tests/ não encontrada."
    exit 1
fi

if ! command -v clang >/dev/null 2>&1; then
    echo "Erro: clang não encontrado. Instale com: sudo apt install clang llvm"
    exit 1
fi

# Usa o ambiente virtual recomendado, mesmo que ele não esteja ativado.
if [[ -n "${VIRTUAL_ENV:-}" ]]; then
    python_cmd="python"
elif [[ -x ".venv/bin/python" ]]; then
    python_cmd=".venv/bin/python"
elif [[ -x "venv/bin/python" ]]; then
    python_cmd="venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
    python_cmd="python3"
else
    echo "Erro: Python 3 não encontrado."
    exit 1
fi

if ! "$python_cmd" -c "import anytree, llvmlite, ply" >/dev/null 2>&1; then
    echo "Erro: dependências Python ausentes. Execute:"
    echo "  python3 -m venv .venv"
    echo "  .venv/bin/python -m pip install -r requirements.txt"
    exit 1
fi

mkdir -p build/executaveis

# Remove LLVM IR antigo para evitar confusão.
rm -f tests/*.tpp.ll

echo "==> Gerando arquivos LLVM IR (.ll)..."
for src in tests/*.tpp; do
    echo "Gerando IR: $src"
    # Alguns testes podem ser casos inválidos de sintaxe/semântica e não gerar .ll.
    # Por isso o script continua mesmo se algum caso não produzir IR.
    "$python_cmd" tppgencode.py "$src" >/dev/null || true
done

shopt -s nullglob
ll_files=(tests/*.tpp.ll)

if (( ${#ll_files[@]} == 0 )); then
    echo "Nenhum arquivo .ll foi gerado. Verifique o tppgencode.py."
    exit 1
fi

echo

echo "==> Compilando .ll para executáveis nativos..."
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
echo "  echo \$?"
