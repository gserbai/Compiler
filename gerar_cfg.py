#!/usr/bin/env python3
"""Gera grafos de fluxo de controle (CFG) a partir de TPP ou LLVM IR."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

from llvmlite import binding


PROJECT_ROOT = Path(__file__).resolve().parent
IMAGE_FORMATS = ("dot", "png", "svg", "pdf")


class CFGError(RuntimeError):
    """Erro esperado durante a geração dos CFGs."""


def _program_name(path: Path) -> str:
    name = path.name
    lower_name = name.lower()
    if lower_name.endswith(".tpp.ll"):
        program_name = name[:-7]
    elif lower_name.endswith(".tpp"):
        program_name = name[:-4]
    elif lower_name.endswith(".ll"):
        program_name = name[:-3]
    else:
        program_name = path.stem
    return program_name or "programa"


def default_output_dir(path: Path) -> Path:
    """Retorna o diretório padrão de saída para um programa."""
    return PROJECT_ROOT / "build" / "cfg" / _program_name(path)


def compile_tpp(source_path: Path) -> Path:
    """Compila um arquivo TPP e retorna o caminho do LLVM IR gerado."""
    source_path = source_path.resolve()
    if source_path.suffix.lower() != ".tpp":
        raise CFGError(f"o arquivo de entrada não possui extensão .tpp: {source_path}")
    if not source_path.is_file():
        raise CFGError(f"arquivo TPP não encontrado: {source_path}")

    ir_path = Path(f"{source_path}.ll")
    try:
        if ir_path.exists():
            ir_path.unlink()
    except OSError as exc:
        raise CFGError(f"não foi possível substituir o LLVM IR {ir_path}: {exc}") from exc

    try:
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "tppgencode.py"), str(source_path)],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        raise CFGError(f"não foi possível executar o gerador de LLVM IR: {exc}") from exc

    if result.returncode != 0 or not ir_path.is_file():
        detail = result.stdout.strip() or result.stderr.strip()
        suffix = f" ({detail})" if detail else ""
        raise CFGError(f"não foi possível gerar LLVM IR para {source_path}{suffix}")

    return ir_path


def _safe_filename(function_name: str) -> str:
    safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", function_name).strip("._")
    return safe_name or "funcao"


def _load_module(ir_path: Path):
    if not ir_path.is_file():
        raise CFGError(f"arquivo LLVM IR não encontrado: {ir_path}")

    try:
        module = binding.parse_assembly(ir_path.read_text(encoding="utf-8"))
        module.verify()
    except (OSError, RuntimeError, UnicodeError) as exc:
        raise CFGError(f"LLVM IR inválido em {ir_path}: {exc}") from exc

    return module


def export_cfgs(
    ir_path: Path,
    output_dir: Path | None = None,
    image_format: str = "png",
    show_instructions: bool = True,
) -> dict[str, list[Path]]:
    """Exporta um arquivo DOT e, opcionalmente, uma imagem por função definida."""
    ir_path = ir_path.resolve()
    if image_format not in IMAGE_FORMATS:
        raise CFGError(f"formato não suportado: {image_format}")

    uses_default_output = output_dir is None
    raw_output_dir = output_dir or default_output_dir(ir_path)
    if raw_output_dir.is_symlink():
        raise CFGError(f"o diretório de saída não pode ser um link simbólico: {raw_output_dir}")
    output_dir = raw_output_dir.resolve()

    module = _load_module(ir_path)
    functions = [function for function in module.functions if not function.is_declaration]
    if not functions:
        raise CFGError(f"nenhuma função definida em {ir_path}")

    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise CFGError(f"não foi possível criar o diretório {output_dir}: {exc}") from exc

    if uses_default_output:
        try:
            for old_path in output_dir.iterdir():
                if old_path.suffix.lower() in {".dot", ".png", ".svg", ".pdf"}:
                    if old_path.is_file() or old_path.is_symlink():
                        old_path.unlink()
        except OSError as exc:
            raise CFGError(f"não foi possível limpar CFGs antigos em {output_dir}: {exc}") from exc

    artifacts: dict[str, list[Path]] = {}
    used_filenames: set[str] = set()

    for function in functions:
        base_name = _safe_filename(function.name)
        filename = base_name
        index = 2
        while filename.casefold() in used_filenames:
            filename = f"{base_name}-{index}"
            index += 1
        used_filenames.add(filename.casefold())

        dot_path = output_dir / f"{filename}.dot"
        try:
            dot_source = binding.get_function_cfg(function, show_inst=show_instructions)
        except RuntimeError as exc:
            raise CFGError(f"não foi possível extrair o CFG de {function.name}: {exc}") from exc
        if not dot_source.strip():
            raise CFGError(f"o LLVM não retornou um CFG para a função {function.name}")
        try:
            dot_path.write_text(dot_source, encoding="utf-8")
        except OSError as exc:
            raise CFGError(f"não foi possível gravar {dot_path}: {exc}") from exc
        artifacts[function.name] = [dot_path]

    if image_format == "dot":
        return artifacts

    dot_executable = shutil.which("dot")
    if dot_executable is None:
        raise CFGError(
            f"os arquivos DOT foram gerados em {output_dir}, mas o Graphviz não foi "
            "encontrado; instale-o ou use --format dot"
        )

    for paths in artifacts.values():
        dot_path = paths[0]
        image_path = dot_path.with_suffix(f".{image_format}")
        try:
            result = subprocess.run(
                [dot_executable, f"-T{image_format}", str(dot_path), "-o", str(image_path)],
                capture_output=True,
                text=True,
                check=False,
            )
        except OSError as exc:
            raise CFGError(f"não foi possível executar o Graphviz: {exc}") from exc
        if result.returncode != 0:
            detail = result.stderr.strip() or result.stdout.strip()
            raise CFGError(f"Graphviz falhou ao renderizar {dot_path}: {detail}")
        if not image_path.is_file():
            raise CFGError(f"Graphviz não criou o arquivo esperado: {image_path}")
        paths.append(image_path)

    return artifacts


def _create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Gera um CFG por função a partir de um arquivo .tpp ou .ll."
    )
    parser.add_argument("input", type=Path, help="arquivo fonte .tpp ou LLVM IR .ll")
    parser.add_argument(
        "--format",
        choices=IMAGE_FORMATS,
        default="png",
        help="formato visual adicional; DOT sempre é gerado (padrão: png)",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        help="diretório de saída (padrão: build/cfg/<programa>)",
    )
    parser.add_argument(
        "--hide-instructions",
        action="store_true",
        help="mostra apenas os blocos e arestas, sem instruções LLVM",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _create_parser()
    args = parser.parse_args(argv)
    input_path = args.input.resolve()

    try:
        if input_path.suffix.lower() == ".tpp":
            ir_path = compile_tpp(input_path)
        elif input_path.suffix.lower() == ".ll":
            ir_path = input_path
        else:
            raise CFGError("a entrada deve possuir extensão .tpp ou .ll")

        artifacts = export_cfgs(
            ir_path,
            output_dir=args.output_dir,
            image_format=args.format,
            show_instructions=not args.hide_instructions,
        )
    except CFGError as exc:
        parser.exit(1, f"Erro: {exc}\n")

    print(f"LLVM IR: {ir_path}")
    print(f"CFGs: {(args.output_dir or default_output_dir(ir_path)).resolve()}")
    for function_name, paths in artifacts.items():
        generated = ", ".join(str(path) for path in paths)
        print(f"  {function_name}: {generated}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
