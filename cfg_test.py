from pathlib import Path

import pytest

import gerar_cfg


SAMPLE_IR = """
declare i32 @external(i32)

define i32 @helper(i32 %n) {
entry:
  %is_zero = icmp eq i32 %n, 0
  br i1 %is_zero, label %yes, label %no

yes:
  ret i32 1

no:
  ret i32 2
}

define i32 @main() {
entry:
  %value = call i32 @helper(i32 0)
  ret i32 %value
}
"""


def test_export_cfgs_creates_dot_only_for_defined_functions(tmp_path):
    ir_path = tmp_path / "programa.ll"
    ir_path.write_text(SAMPLE_IR, encoding="utf-8")

    artifacts = gerar_cfg.export_cfgs(
        ir_path,
        output_dir=tmp_path / "cfg",
        image_format="dot",
    )

    assert set(artifacts) == {"helper", "main"}
    assert not (tmp_path / "cfg" / "external.dot").exists()
    helper_dot = artifacts["helper"][0].read_text(encoding="utf-8")
    assert "CFG for 'helper' function" in helper_dot
    assert "->" in helper_dot
    assert "yes" in helper_dot
    assert "no" in helper_dot
    assert "entry" in artifacts["main"][0].read_text(encoding="utf-8")


def test_cfg_can_hide_llvm_instructions(tmp_path):
    ir_path = tmp_path / "programa.ll"
    ir_path.write_text(SAMPLE_IR, encoding="utf-8")

    artifacts = gerar_cfg.export_cfgs(
        ir_path,
        output_dir=tmp_path / "cfg",
        image_format="dot",
        show_instructions=False,
    )

    dot_source = artifacts["helper"][0].read_text(encoding="utf-8")
    assert "entry" in dot_source
    assert "icmp" not in dot_source


def test_png_requires_graphviz_but_preserves_dot_files(tmp_path, monkeypatch):
    ir_path = tmp_path / "programa.ll"
    ir_path.write_text(SAMPLE_IR, encoding="utf-8")
    monkeypatch.setattr(gerar_cfg.shutil, "which", lambda _name: None)

    with pytest.raises(gerar_cfg.CFGError, match="Graphviz não foi encontrado"):
        gerar_cfg.export_cfgs(
            ir_path,
            output_dir=tmp_path / "cfg",
            image_format="png",
        )

    assert (tmp_path / "cfg" / "helper.dot").is_file()
    assert (tmp_path / "cfg" / "main.dot").is_file()


def test_png_rendering_uses_graphviz_and_records_images(tmp_path, monkeypatch):
    ir_path = tmp_path / "programa.ll"
    ir_path.write_text(SAMPLE_IR, encoding="utf-8")
    commands = []

    monkeypatch.setattr(gerar_cfg.shutil, "which", lambda _name: "/usr/bin/dot")

    def fake_run(command, **_kwargs):
        commands.append(command)
        Path(command[-1]).write_bytes(b"imagem")
        return gerar_cfg.subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(gerar_cfg.subprocess, "run", fake_run)

    artifacts = gerar_cfg.export_cfgs(
        ir_path,
        output_dir=tmp_path / "cfg",
        image_format="png",
    )

    assert len(commands) == 2
    assert all("-Tpng" in command for command in commands)
    assert all(paths[1].suffix == ".png" for paths in artifacts.values())
    assert all(paths[1].is_file() for paths in artifacts.values())


def test_function_filenames_do_not_collide_by_case(tmp_path):
    ir_path = tmp_path / "programa.ll"
    ir_path.write_text(
        "define i32 @Foo() { ret i32 1 }\n"
        "define i32 @foo() { ret i32 2 }\n",
        encoding="utf-8",
    )

    artifacts = gerar_cfg.export_cfgs(
        ir_path,
        output_dir=tmp_path / "cfg",
        image_format="dot",
    )

    assert artifacts["Foo"][0].name == "Foo.dot"
    assert artifacts["foo"][0].name == "foo-2.dot"


def test_cli_uses_and_cleans_the_default_output_dir(tmp_path, monkeypatch, capsys):
    ir_path = tmp_path / "programa.tpp.ll"
    ir_path.write_text(SAMPLE_IR, encoding="utf-8")
    monkeypatch.setattr(gerar_cfg, "PROJECT_ROOT", tmp_path)

    output_dir = tmp_path / "build" / "cfg" / "programa"
    output_dir.mkdir(parents=True)
    (output_dir / "funcao-removida.dot").write_text("antigo", encoding="utf-8")
    (output_dir / "funcao-removida.png").write_bytes(b"antigo")

    assert gerar_cfg.main([str(ir_path), "--format", "dot"]) == 0

    assert not (output_dir / "funcao-removida.dot").exists()
    assert not (output_dir / "funcao-removida.png").exists()
    assert (output_dir / "helper.dot").is_file()
    assert (output_dir / "main.dot").is_file()
    assert "CFGs:" in capsys.readouterr().out


def test_compile_tpp_and_export_cfg(tmp_path):
    source_path = tmp_path / "programa.tpp"
    source_path.write_text(
        "inteiro principal()\n    retorna(0)\nfim\n",
        encoding="utf-8",
    )

    ir_path = gerar_cfg.compile_tpp(source_path)
    artifacts = gerar_cfg.export_cfgs(
        ir_path,
        output_dir=tmp_path / "cfg",
        image_format="dot",
    )

    assert ir_path.is_file()
    assert set(artifacts) == {"main"}
    assert artifacts["main"][0].is_file()
