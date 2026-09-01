# Guia de geração de código TPP

O fluxo completo, incluindo instalação, execução de cada fase, geração nativa x86-64 e cross-compilation para AArch64/RISC-V, está documentado no [README](README.md).

## Referência rápida

```bash
# 1. Ambiente Python
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt

# 2. TPP -> LLVM IR
python tppgencode.py tests/gencode-test-023.tpp

# 3. LLVM IR -> executável nativo
mkdir -p build/demo
clang -O2 -Wno-override-module \
  tests/gencode-test-023.tpp.ll \
  -o build/demo/fibonacci

# 4. Execução
printf '5\n' | ./build/demo/fibonacci
```

Para gerar todos os exemplos válidos:

```bash
bash gerar_executaveis_tpp.sh
```

Para validar a geração de código:

```bash
python -m pytest -q tppgencode_test.py
```

O Clang usa o target do próprio computador quando `--target` não é informado. Consulte no README os comandos que geram assembly (`-S`), objeto com código de máquina (`-c`) e saídas para outras arquiteturas.
