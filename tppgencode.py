import sys
import os
import logging
from dataclasses import dataclass

logging.basicConfig(
    level=logging.DEBUG,
    filename="gencode.log",
    filemode="w",
    format="%(filename)10s:%(lineno)4d:%(message)s"
)
log = logging.getLogger()

from myerror import MyError

error_handler = MyError('GenCodeErrors')

check_tpp = False
check_key = False


# ═════════════════════════════════════════════════════════════
# GERAÇÃO DE CÓDIGO LLVM
# ═════════════════════════════════════════════════════════════

try:
    from llvmlite import ir
except Exception as exc:  # pragma: no cover
    ir = None
    _LLVMLITE_IMPORT_ERROR = exc


@dataclass
class VarInfo:
    ptr: object
    tpp_type: str
    dimensions: list
    is_global: bool = False
    is_array_param: bool = False


class LLVMCodeGenerator:
    """
    Gera LLVM IR a partir da AST podada produzida por tppsema._prune().

    A linguagem TPP possui basicamente:
    - tipos inteiro/flutuante;
    - variáveis escalares e vetores;
    - funções;
    - leia/escreva;
    - se/senão;
    - repita/até;
    - expressões aritméticas, relacionais e lógicas.
    """

    def __init__(self, module_name="tpp_module"):
        if ir is None:
            raise RuntimeError(f"llvmlite não está instalado: {_LLVMLITE_IMPORT_ERROR}")

        self.module = ir.Module(name=module_name)

        self.i32 = ir.IntType(32)
        self.i1 = ir.IntType(1)
        self.double = ir.DoubleType()
        self.void = ir.VoidType()
        self.i8 = ir.IntType(8)
        self.i8ptr = self.i8.as_pointer()

        self.builder = None
        self.current_function = None
        self.current_ret_type = None
        self.current_tpp_function = None
        self.current_exit_block = None
        self.current_ret_ptr = None

        self.globals = {}
        self.locals = {}
        self.functions = {}
        self.function_ret_types = {}
        self.function_params = {}
        self.function_name_map = {}

        self.printf = None
        self.scanf = None
        self.string_id = 0

    # ──────────────────────────────────────────────────────
    # Utilitários de AST
    # ──────────────────────────────────────────────────────

    @staticmethod
    def walk(node):
        if node is None:
            return
        yield node
        for child in getattr(node, "children", ()):
            yield from LLVMCodeGenerator.walk(child)

    @staticmethod
    def children(node, *types):
        return [c for c in getattr(node, "children", ()) if c.type in types]

    @staticmethod
    def child(node, *types):
        for c in getattr(node, "children", ()):
            if c.type in types:
                return c
        return None

    @staticmethod
    def has_ancestor(node, *types):
        p = getattr(node, "parent", None)
        while p is not None:
            if p.type in types:
                return True
            p = getattr(p, "parent", None)
        return False

    @staticmethod
    def id_name(id_node):
        """
        Extrai o identificador real de um nó ID.

        O parser monta algo como:
        ID
        └── x

        Dependendo da poda, o valor pode estar no próprio nó ou em um filho.
        """
        if id_node is None:
            return "?"
        for c in getattr(id_node, "children", ()):
            if c.type == "ID" and c.name not in ("ID", "id"):
                return c.name
        if id_node.name not in ("ID", "id"):
            return id_node.name
        return "?"

    @staticmethod
    def tipo_str(tipo_node):
        if tipo_node is None:
            return "vazio"
        for c in getattr(tipo_node, "children", ()):
            if c.type == "INTEIRO":
                return "inteiro"
            if c.type == "FLUTUANTE":
                return "flutuante"
        if tipo_node.type == "INTEIRO":
            return "inteiro"
        if tipo_node.type == "FLUTUANTE":
            return "flutuante"
        return "vazio"

    def llvm_type(self, tpp_type):
        if tpp_type == "inteiro":
            return self.i32
        if tpp_type == "flutuante":
            return self.double
        return self.void

    def llvm_function_name(self, tpp_name):
        # Para gerar um executável via lli/clang, a função principal vira main.
        return "main" if tpp_name == "principal" else tpp_name

    def is_top_level_var_decl(self, node):
        return node.type == "DECLARACAO_VARIAVEIS" and not self.has_ancestor(node, "DECLARACAO_FUNCAO", "CABECALHO", "CORPO")

    def is_function_decl(self, node):
        return node.type == "DECLARACAO_FUNCAO"

    # ──────────────────────────────────────────────────────
    # Entrada principal
    # ──────────────────────────────────────────────────────

    def generate(self, root):
        self._declare_runtime()
        self._declare_globals(root)
        self._declare_function_signatures(root)
        self._emit_functions(root)
        return str(self.module)

    # ──────────────────────────────────────────────────────
    # Declarações
    # ──────────────────────────────────────────────────────

    def _declare_runtime(self):
        printf_ty = ir.FunctionType(self.i32, [self.i8ptr], var_arg=True)
        scanf_ty = ir.FunctionType(self.i32, [self.i8ptr], var_arg=True)

        self.printf = ir.Function(self.module, printf_ty, name="printf")
        self.scanf = ir.Function(self.module, scanf_ty, name="scanf")

    def _declare_globals(self, root):
        for node in self.walk(root):
            if self.is_top_level_var_decl(node):
                self._declare_var_list(node, global_scope=True)

    def _declare_function_signatures(self, root):
        for node in self.walk(root):
            if not self.is_function_decl(node):
                continue

            tipo_node = self.child(node, "TIPO")
            ret_type = self.tipo_str(tipo_node)

            cab = self.child(node, "CABECALHO")
            if cab is None:
                continue

            id_node = self.child(cab, "ID")
            tpp_name = self.id_name(id_node)
            llvm_name = self.llvm_function_name(tpp_name)

            params = self._collect_params(self.child(cab, "LISTA_PARAMETROS"))

            # Se principal for vazia, ainda emitimos i32 @main() para o runtime.
            if tpp_name == "principal" and ret_type == "vazio":
                llvm_ret = self.i32
            else:
                llvm_ret = self.llvm_type(ret_type)

            llvm_param_types = []
            for p_type, _p_name, is_array in params:
                base_ty = self.llvm_type(p_type)
                llvm_param_types.append(base_ty.as_pointer() if is_array else base_ty)

            fn_ty = ir.FunctionType(llvm_ret, llvm_param_types)
            fn = ir.Function(self.module, fn_ty, name=llvm_name)

            for arg, (_p_type, p_name, _is_array) in zip(fn.args, params):
                arg.name = p_name

            self.functions[tpp_name] = fn
            self.function_name_map[tpp_name] = llvm_name
            self.function_ret_types[tpp_name] = ret_type
            self.function_params[tpp_name] = params

    def _emit_functions(self, root):
        for node in self.walk(root):
            if self.is_function_decl(node):
                self._emit_function(node)

    def _emit_function(self, node):
        cab = self.child(node, "CABECALHO")
        if cab is None:
            return

        tpp_name = self.id_name(self.child(cab, "ID"))
        fn = self.functions[tpp_name]

        block = fn.append_basic_block("entry")
        self.builder = ir.IRBuilder(block)
        self.current_function = fn
        self.current_tpp_function = tpp_name
        self.current_ret_type = self.function_ret_types[tpp_name]
        self.locals = {}

        # Bloco de saída único da função.
        # Ele é criado para facilitar a visualização do CFG como:
        # entry -> ... -> exit.
        # As instruções RETORNA armazenam o valor em retval e desviam para exit.
        self.current_exit_block = fn.append_basic_block("exit")
        self.current_ret_ptr = None
        if fn.function_type.return_type != self.void:
            self.current_ret_ptr = self.builder.alloca(fn.function_type.return_type, name="retval")

        # IMPORTANTE PARA LLVM VÁLIDO:
        # todos os allocas locais ficam no começo do bloco entry, antes de
        # store/load/br/ret. Isso facilita compilar o .ll com clang/llc.

        # 1) Aloca e inicializa parâmetros locais.
        for arg, (p_type, p_name, is_array) in zip(fn.args, self.function_params[tpp_name]):
            if is_array:
                self.locals[p_name] = VarInfo(arg, p_type, [], is_array_param=True)
            else:
                ptr = self.builder.alloca(self.llvm_type(p_type), name=p_name)
                self.locals[p_name] = VarInfo(ptr, p_type, [])
                self.builder.store(arg, ptr)

        corpo = self.child(cab, "CORPO")

        # 2) Pré-declara variáveis locais do corpo antes de gerar comandos.
        # A árvore da gramática pode deixar DECLARACAO_VARIAVEIS em ordem
        # aninhada/recursiva; pré-alocar evita alloca depois de ret/br.
        if corpo is not None:
            self._predeclare_locals(corpo)
            self._emit_corpo(corpo)

        # Retorno padrão quando a função termina sem retorna explícito.
        # Em vez de emitir ret direto, desviamos para o bloco exit.
        if not self.builder.block.is_terminated:
            if fn.function_type.return_type != self.void and self.current_ret_ptr is not None:
                self.builder.store(ir.Constant(fn.function_type.return_type, 0), self.current_ret_ptr)
            self.builder.branch(self.current_exit_block)

        # Bloco único de saída da função.
        # Todos os caminhos que terminariam com ret agora convergem aqui.
        exit_builder = ir.IRBuilder(self.current_exit_block)
        exit_builder.position_at_end(self.current_exit_block)
        if fn.function_type.return_type == self.void:
            exit_builder.ret_void()
        else:
            ret_val = exit_builder.load(self.current_ret_ptr, name="ret.final")
            exit_builder.ret(ret_val)

        # Mantém a impressão textual do LLVM mais didática:
        # entry primeiro, blocos intermediários no meio e exit no fim.
        if self.current_exit_block in fn.blocks:
            fn.blocks.remove(self.current_exit_block)
            fn.blocks.append(self.current_exit_block)

    def _predeclare_locals(self, node):
        """Aloca antecipadamente todas as variáveis locais declaradas no corpo.

        Isso não gera código executável de declaração; só reserva espaço local
        no bloco entry. Depois, quando a declaração aparecer no fluxo normal,
        _declare_var_list verá que a variável já está em self.locals e não
        realocará.
        """
        for n in self.walk(node):
            if n.type == "DECLARACAO_VARIAVEIS":
                self._declare_var_list(n, global_scope=False)

    def _declare_var_list(self, decl_node, global_scope=False):
        tipo = self.tipo_str(self.child(decl_node, "TIPO"))
        lista = self.child(decl_node, "LISTA_VARIAVEIS")

        if lista is None:
            # Em algumas árvores podadas a lista pode ter sumido e os VAR
            # ficam diretamente sob DECLARACAO_VARIAVEIS.
            vars_ = self.children(decl_node, "VAR")
        else:
            vars_ = [n for n in self.walk(lista) if n.type == "VAR"]

        seen = set()
        for var_node in vars_:
            name = self.id_name(self.child(var_node, "ID"))
            if name in seen or name == "?":
                continue
            seen.add(name)

            dims = self._var_dimensions(var_node)
            base_ty = self.llvm_type(tipo)

            if dims:
                llvm_ty = base_ty
                for size in reversed(dims):
                    llvm_ty = ir.ArrayType(llvm_ty, size)
            else:
                llvm_ty = base_ty

            if global_scope:
                if name in self.globals:
                    continue
                glob = ir.GlobalVariable(self.module, llvm_ty, name=name)
                glob.initializer = ir.Constant(llvm_ty, None)
                glob.linkage = "common"
                glob.align = 4
                self.globals[name] = VarInfo(glob, tipo, dims, is_global=True)
            else:
                if name in self.locals:
                    continue
                # Durante a pré-declaração estamos no bloco entry; usar o builder
                # atual mantém alloca antes dos comandos reais.
                if self.builder is not None and self.builder.block is self.current_function.entry_basic_block:
                    ptr = self.builder.alloca(llvm_ty, name=name)
                else:
                    ptr = self._alloca_entry(name, llvm_ty)
                self.locals[name] = VarInfo(ptr, tipo, dims)

    def _collect_params(self, lista_node):
        params = []
        if lista_node is None:
            return params

        for p in self.walk(lista_node):
            if p.type != "PARAMETRO":
                continue
            # Evita contar PARAMETRO pai e filho aninhado como dois parâmetros.
            if self.has_ancestor(p, "PARAMETRO"):
                continue

            tipo = self.tipo_str(self.child(p, "TIPO"))
            id_node = self.child(p, "ID")
            name = self.id_name(id_node)

            # parâmetro vetor costuma aparecer como PARAMETRO contendo outro PARAMETRO
            is_array = any(c.type == "PARAMETRO" for c in getattr(p, "children", ()))
            if name != "?":
                params.append((tipo, name, is_array))

        return params

    def _alloca_entry(self, name, llvm_ty):
        entry = self.current_function.entry_basic_block
        builder = ir.IRBuilder(entry)

        # Insere depois dos allocas já existentes e antes da primeira instrução real.
        insert_before = None
        for inst in entry.instructions:
            if getattr(inst, "opname", None) != "alloca":
                insert_before = inst
                break

        if insert_before is not None:
            builder.position_before(insert_before)
        else:
            builder.position_at_end(entry)

        return builder.alloca(llvm_ty, name=name)

    # ──────────────────────────────────────────────────────
    # Comandos
    # ──────────────────────────────────────────────────────

    def _emit_corpo(self, corpo_node):
        for acao in self._flatten_actions(corpo_node):
            self._emit_statement(acao)
            if self.builder.block.is_terminated:
                break

    def _flatten_actions(self, node):
        result = []
        if node is None:
            return result
        if node.type == "ACAO":
            result.append(node)
            return result
        for c in getattr(node, "children", ()):
            result.extend(self._flatten_actions(c))
        return result

    def _emit_statement(self, node):
        if node is None:
            return

        if node.type == "ACAO":
            for c in getattr(node, "children", ()):
                self._emit_statement(c)
            return

        if node.type == "DECLARACAO_VARIAVEIS":
            self._declare_var_list(node, global_scope=False)
            return

        if node.type == "ATRIBUICAO":
            self._emit_atribuicao(node)
            return

        if node.type == "SE":
            # ignora o nó token SE, que não tem EXPRESSAO/CORPO
            if self.child(node, "CORPO") is not None:
                self._emit_se(node)
            return

        if node.type == "REPITA":
            if self.child(node, "CORPO") is not None:
                self._emit_repita(node)
            return

        if node.type == "LEIA":
            if self.child(node, "VAR") is not None:
                self._emit_leia(node)
            return

        if node.type == "ESCREVA":
            self._emit_escreva(node)
            return

        if node.type == "RETORNA":
            self._emit_retorna(node)
            return

        if node.type in ("CHAMADA_FUNCAO", "EXPRESSAO", "EXPRESSAO_LOGICA",
                         "EXPRESSAO_SIMPLES", "EXPRESSAO_ADITIVA",
                         "EXPRESSAO_MULTIPLICATIVA", "EXPRESSAO_UNARIA",
                         "FATOR", "VAR", "NUM_INTEIRO", "NUM_PONTO_FLUTUANTE",
                         "NUM_NOTACAO_CIENTIFICA"):
            self._emit_expr(node)
            return

        for c in getattr(node, "children", ()):
            self._emit_statement(c)

    def _emit_atribuicao(self, node):
        
        meaningful = [
            c for c in getattr(node, "children", ())
            if c.type not in ("SIMBOLO",)
        ]

        var_node = None
        expr_node = None

        # Caso mais comum: existe o token ATRIBUICAO separando esquerda e direita.
        assign_pos = None
        for idx, c in enumerate(meaningful):
            if c.type == "ATRIBUICAO":
                assign_pos = idx
                break

        if assign_pos is not None:
            # Lado esquerdo: primeiro VAR antes do :=
            for c in meaningful[:assign_pos]:
                if c.type == "VAR":
                    var_node = c
                    break

            # Lado direito: primeiro nó semanticamente útil após o :=.
            # Pode ser EXPRESSAO, EXPRESSAO_ADITIVA, VAR, chamada, número etc.
            for c in meaningful[assign_pos + 1:]:
                if c.type != "ATRIBUICAO":
                    expr_node = c
                    break
        else:
            # Fallback para árvores podadas sem o token ATRIBUICAO.
            if meaningful and meaningful[0].type == "VAR":
                var_node = meaningful[0]
                for c in meaningful[1:]:
                    expr_node = c
                    break

        if var_node is None or expr_node is None:
            return None

        ptr, var_type = self._var_pointer(var_node)
        value, value_type = self._emit_expr(expr_node)
        value = self._cast(value, value_type, var_type)
        self.builder.store(value, ptr)
        return value, var_type

    def _emit_se(self, node):
        expr_node = self._first_expr_child(node)
        corpos = self.children(node, "CORPO")
        if expr_node is None or not corpos:
            return

        cond_val, cond_type = self._emit_expr(expr_node)
        cond = self._to_bool(cond_val, cond_type)

        then_bb = self.current_function.append_basic_block("if.then")
        else_bb = self.current_function.append_basic_block("if.else") if len(corpos) > 1 else None
        end_bb = self.current_function.append_basic_block("if.end")

        if else_bb is not None:
            self.builder.cbranch(cond, then_bb, else_bb)
        else:
            self.builder.cbranch(cond, then_bb, end_bb)

        self.builder.position_at_end(then_bb)
        self._emit_corpo(corpos[0])
        if not self.builder.block.is_terminated:
            self.builder.branch(end_bb)

        if else_bb is not None:
            self.builder.position_at_end(else_bb)
            self._emit_corpo(corpos[1])
            if not self.builder.block.is_terminated:
                self.builder.branch(end_bb)

        self.builder.position_at_end(end_bb)

    def _emit_repita(self, node):
        corpos = self.children(node, "CORPO")
        expr_node = self._last_expr_child(node)
        if not corpos or expr_node is None:
            return

        loop_bb = self.current_function.append_basic_block("repeat.body")
        end_bb = self.current_function.append_basic_block("repeat.end")

        self.builder.branch(loop_bb)
        self.builder.position_at_end(loop_bb)

        self._emit_corpo(corpos[0])
        if self.builder.block.is_terminated:
            return

        cond_val, cond_type = self._emit_expr(expr_node)
        cond = self._to_bool(cond_val, cond_type)

        # TPP: repita ... até expr  → sai quando expr é verdadeiro.
        self.builder.cbranch(cond, end_bb, loop_bb)
        self.builder.position_at_end(end_bb)

    def _emit_leia(self, node):
        var_node = self.child(node, "VAR")
        if var_node is None:
            return

        ptr, tpp_type = self._var_pointer(var_node)
        if tpp_type == "flutuante":
            fmt = self._global_string("%lf\0", "fmt_scan_float")
        else:
            fmt = self._global_string("%d\0", "fmt_scan_int")

        self.builder.call(self.scanf, [fmt, ptr])

    def _emit_escreva(self, node):
        expr_node = self._first_expr_child(node)
        if expr_node is None:
            return

        value, tpp_type = self._emit_expr(expr_node)
        if tpp_type == "flutuante":
            fmt = self._global_string("%f\n\0", "fmt_print_float")
            value = self._cast(value, tpp_type, "flutuante")
        else:
            fmt = self._global_string("%d\n\0", "fmt_print_int")
            value = self._cast(value, tpp_type, "inteiro")

        self.builder.call(self.printf, [fmt, value])

    def _emit_retorna(self, node):
        expr_node = self._first_expr_child(node)

        fn_ret_ty = self.current_function.function_type.return_type

        # Com bloco exit único, RETORNA não emite ret diretamente.
        # Ele grava o valor de retorno em retval e desvia para exit.
        if fn_ret_ty == self.void:
            if not self.builder.block.is_terminated:
                self.builder.branch(self.current_exit_block)
            return

        if expr_node is None:
            ret_val = ir.Constant(fn_ret_ty, 0)
        else:
            value, value_type = self._emit_expr(expr_node)
            tpp_target = "flutuante" if fn_ret_ty == self.double else "inteiro"
            ret_val = self._cast(value, value_type, tpp_target)

        if not self.builder.block.is_terminated:
            self.builder.store(ret_val, self.current_ret_ptr)
            self.builder.branch(self.current_exit_block)

    # ──────────────────────────────────────────────────────
    # Expressões
    # ──────────────────────────────────────────────────────

    def _emit_expr(self, node):
        if node is None:
            return ir.Constant(self.i32, 0), "inteiro"

        t = node.type

        if t == "NUM_INTEIRO":
            return ir.Constant(self.i32, self._numeric_value(node, int, 0)), "inteiro"

        if t in ("NUM_PONTO_FLUTUANTE", "NUM_NOTACAO_CIENTIFICA"):
            return ir.Constant(self.double, self._numeric_value(node, float, 0.0)), "flutuante"

        if t == "VAR":
            ptr, tpp_type = self._var_pointer(node)
            return self.builder.load(ptr), tpp_type

        if t == "CHAMADA_FUNCAO":
            return self._emit_call(node)

        if t == "ATRIBUICAO":
            return self._emit_atribuicao(node)

        if t == "EXPRESSAO_UNARIA":
            ch = self._meaningful_children(node)
            if len(ch) == 1:
                return self._emit_expr(ch[0])

            op = self.child(node, "OPERADOR_SOMA", "OPERADOR_NEGACAO")
            fator = None
            for c in ch:
                if c is not op:
                    fator = c
            value, value_type = self._emit_expr(fator)

            if op and self._operator_kind(op) == "MENOS":
                if value_type == "flutuante":
                    return self.builder.fneg(value), value_type
                return self.builder.neg(value), value_type

            if op and self._operator_kind(op) == "NAO":
                b = self._to_bool(value, value_type)
                return self.builder.not_(b), "inteiro"

            return value, value_type

        if t in ("EXPRESSAO_LOGICA", "EXPRESSAO_SIMPLES",
                 "EXPRESSAO_ADITIVA", "EXPRESSAO_MULTIPLICATIVA"):
            return self._emit_binary_or_passthrough(node)

        if t in ("EXPRESSAO", "FATOR", "NUMERO"):
            ch = self._meaningful_children(node)
            if len(ch) == 1:
                return self._emit_expr(ch[0])
            if len(ch) >= 3:
                return self._emit_expr(ch[1])

        # fallback: tenta emitir o primeiro filho semanticamente útil
        ch = self._meaningful_children(node)
        if ch:
            return self._emit_expr(ch[0])

        return ir.Constant(self.i32, 0), "inteiro"

    def _emit_binary_or_passthrough(self, node):
        ch = self._meaningful_children(node)
        if len(ch) == 1:
            return self._emit_expr(ch[0])

        op = None
        for c in ch:
            if c.type in ("OPERADOR_LOGICO", "OPERADOR_RELACIONAL",
                          "OPERADOR_SOMA", "OPERADOR_MULTIPLICACAO"):
                op = c
                break

        if op is None:
            return self._emit_expr(ch[0])

        idx = ch.index(op)
        left_node = ch[idx - 1]
        right_node = ch[idx + 1]

        left, left_type = self._emit_expr(left_node)
        right, right_type = self._emit_expr(right_node)
        op_kind = self._operator_kind(op)

        if op.type == "OPERADOR_LOGICO":
            l = self._to_bool(left, left_type)
            r = self._to_bool(right, right_type)
            if op_kind == "E":
                return self.builder.and_(l, r), "inteiro"
            return self.builder.or_(l, r), "inteiro"

        if op.type == "OPERADOR_RELACIONAL":
            common = "flutuante" if "flutuante" in (left_type, right_type) else "inteiro"
            left = self._cast(left, left_type, common)
            right = self._cast(right, right_type, common)

            if common == "flutuante":
                pred = {
                    "MENOR": "<", "MAIOR": ">", "IGUAL": "==", "DIFERENTE": "!=",
                    "MENOR_IGUAL": "<=", "MAIOR_IGUAL": ">="
                }[op_kind]
                return self.builder.fcmp_ordered(pred, left, right), "inteiro"

            pred = {
                "MENOR": "<", "MAIOR": ">", "IGUAL": "==", "DIFERENTE": "!=",
                "MENOR_IGUAL": "<=", "MAIOR_IGUAL": ">="
            }[op_kind]
            return self.builder.icmp_signed(pred, left, right), "inteiro"

        if op.type == "OPERADOR_SOMA":
            common = "flutuante" if "flutuante" in (left_type, right_type) else "inteiro"
            left = self._cast(left, left_type, common)
            right = self._cast(right, right_type, common)

            if common == "flutuante":
                if op_kind == "MAIS":
                    return self.builder.fadd(left, right), common
                return self.builder.fsub(left, right), common

            if op_kind == "MAIS":
                return self.builder.add(left, right), common
            return self.builder.sub(left, right), common

        if op.type == "OPERADOR_MULTIPLICACAO":
            common = "flutuante" if "flutuante" in (left_type, right_type) else "inteiro"
            left = self._cast(left, left_type, common)
            right = self._cast(right, right_type, common)

            if common == "flutuante":
                if op_kind == "VEZES":
                    return self.builder.fmul(left, right), common
                return self.builder.fdiv(left, right), common

            if op_kind == "VEZES":
                return self.builder.mul(left, right), common
            return self.builder.sdiv(left, right), common

        return left, left_type

    def _emit_call(self, node):
        func_name = self.id_name(self.child(node, "ID"))
        fn = self.functions.get(func_name)
        if fn is None:
            return ir.Constant(self.i32, 0), "inteiro"

        args = []
        arg_nodes = self._argument_nodes(self.child(node, "LISTA_ARGUMENTOS"))
        params = self.function_params.get(func_name, [])

        for i, arg_node in enumerate(arg_nodes):
            val, val_type = self._emit_expr(arg_node)
            if i < len(params):
                target_type = params[i][0]
                val = self._cast(val, val_type, target_type)
            args.append(val)

        call = self.builder.call(fn, args)

        ret_type = self.function_ret_types.get(func_name, "vazio")
        if ret_type == "vazio":
            return ir.Constant(self.i32, 0), "inteiro"
        return call, ret_type

    # ──────────────────────────────────────────────────────
    # Variáveis, vetores e literais
    # ──────────────────────────────────────────────────────

    def _lookup_var(self, name):
        if name in self.locals:
            return self.locals[name]
        return self.globals.get(name)

    def _var_pointer(self, var_node):
        name = self.id_name(self.child(var_node, "ID"))
        info = self._lookup_var(name)
        if info is None:
            # A semântica já deveria ter capturado isso; fallback seguro.
            tmp = self._alloca_entry(name, self.i32)
            self.locals[name] = VarInfo(tmp, "inteiro", [])
            info = self.locals[name]

        if info.dimensions:
            indices = self.children(var_node, "INDICE")
            gep_indices = [ir.Constant(self.i32, 0)]
            for idx_node in indices:
                idx_expr = self._index_expr(idx_node)
                idx_val, idx_type = self._emit_expr(idx_expr)
                idx_val = self._cast(idx_val, idx_type, "inteiro")
                gep_indices.append(idx_val)

            # Se A foi usado sem índice, usa ponteiro para o primeiro elemento.
            while len(gep_indices) < len(info.dimensions) + 1:
                gep_indices.append(ir.Constant(self.i32, 0))

            return self.builder.gep(info.ptr, gep_indices), info.tpp_type

        return info.ptr, info.tpp_type

    def _var_dimensions(self, var_node):
        dims = []
        for idx in self.children(var_node, "INDICE"):
            value = self._extract_int_literal(idx)
            dims.append(value if value is not None and value > 0 else 1)
        return dims

    def _index_expr(self, idx_node):
        for c in getattr(idx_node, "children", ()):
            if c.type not in ("ABRE_COLCHETE", "FECHA_COLCHETE", "SIMBOLO"):
                return c
        return None

    def _extract_int_literal(self, node):
        for n in self.walk(node):
            if n.type == "VALOR":
                try:
                    return int(str(n.name))
                except ValueError:
                    return None
        return None

    def _numeric_value(self, node, conv, default):
        for n in self.walk(node):
            if n.type == "VALOR":
                try:
                    return conv(str(n.name))
                except ValueError:
                    return default
        try:
            return conv(str(node.name))
        except ValueError:
            return default

    # ──────────────────────────────────────────────────────
    # Auxiliares de expressão
    # ──────────────────────────────────────────────────────

    def _meaningful_children(self, node):
        ignored = {
            "SIMBOLO", "ABRE_PARENTESE", "FECHA_PARENTESE",
            "ABRE_COLCHETE", "FECHA_COLCHETE", "VIRGULA",
            "DOIS_PONTOS", "FIM", "ENTAO", "SENAO", "ATE",
        }
        return [c for c in getattr(node, "children", ()) if c.type not in ignored]

    def _operator_kind(self, op_node):
        for n in self.walk(op_node):
            if n is op_node:
                continue
            if n.type in {
                "MAIS", "MENOS", "VEZES", "DIVIDE",
                "MENOR", "MAIOR", "IGUAL", "DIFERENTE",
                "MENOR_IGUAL", "MAIOR_IGUAL",
                "E", "OU", "NAO"
            }:
                return n.type
        return op_node.type

    def _first_expr_child(self, node):
        expr_types = {
            "EXPRESSAO", "EXPRESSAO_LOGICA", "EXPRESSAO_SIMPLES",
            "EXPRESSAO_ADITIVA", "EXPRESSAO_MULTIPLICATIVA",
            "EXPRESSAO_UNARIA", "FATOR", "VAR", "NUM_INTEIRO",
            "NUM_PONTO_FLUTUANTE", "NUM_NOTACAO_CIENTIFICA",
            "CHAMADA_FUNCAO", "ATRIBUICAO"
        }
        for c in getattr(node, "children", ()):
            if c.type in expr_types:
                return c
        return None

    def _last_expr_child(self, node):
        expr_types = {
            "EXPRESSAO", "EXPRESSAO_LOGICA", "EXPRESSAO_SIMPLES",
            "EXPRESSAO_ADITIVA", "EXPRESSAO_MULTIPLICATIVA",
            "EXPRESSAO_UNARIA", "FATOR", "VAR", "NUM_INTEIRO",
            "NUM_PONTO_FLUTUANTE", "NUM_NOTACAO_CIENTIFICA",
            "CHAMADA_FUNCAO", "ATRIBUICAO"
        }
        found = None
        for c in getattr(node, "children", ()):
            if c.type in expr_types:
                found = c
        return found

    def _argument_nodes(self, lista):
        if lista is None:
            return []
        expr_types = {
            "EXPRESSAO", "EXPRESSAO_LOGICA", "EXPRESSAO_SIMPLES",
            "EXPRESSAO_ADITIVA", "EXPRESSAO_MULTIPLICATIVA",
            "EXPRESSAO_UNARIA", "FATOR", "VAR", "NUM_INTEIRO",
            "NUM_PONTO_FLUTUANTE", "NUM_NOTACAO_CIENTIFICA",
            "CHAMADA_FUNCAO", "ATRIBUICAO"
        }
        args = []
        for c in getattr(lista, "children", ()):
            if c.type in expr_types:
                args.append(c)
            elif c.type == "LISTA_ARGUMENTOS":
                args.extend(self._argument_nodes(c))
        return args

    # ──────────────────────────────────────────────────────
    # Casts e runtime I/O
    # ──────────────────────────────────────────────────────

    def _cast(self, value, from_type, to_type):
        if from_type == to_type:
            return value

        if to_type == "inteiro":
            if value.type == self.i1:
                return self.builder.zext(value, self.i32)
            if from_type == "flutuante":
                return self.builder.fptosi(value, self.i32)
            return value

        if to_type == "flutuante":
            if value.type == self.i1:
                return self.builder.uitofp(value, self.double)
            if from_type == "inteiro":
                return self.builder.sitofp(value, self.double)
            return value

        return value

    def _to_bool(self, value, tpp_type):
        if value.type == self.i1:
            return value
        if tpp_type == "flutuante":
            return self.builder.fcmp_ordered("!=", value, ir.Constant(self.double, 0.0))
        return self.builder.icmp_signed("!=", value, ir.Constant(self.i32, 0))

    def _global_string(self, text, prefix):
        data = bytearray(text.encode("utf-8"))
        ty = ir.ArrayType(self.i8, len(data))
        name = f"{prefix}_{self.string_id}"
        self.string_id += 1

        glob = ir.GlobalVariable(self.module, ty, name=name)
        glob.global_constant = True
        glob.linkage = "internal"
        glob.initializer = ir.Constant(ty, data)

        zero = ir.Constant(self.i32, 0)
        return self.builder.gep(glob, [zero, zero], inbounds=True)


# ═════════════════════════════════════════════════════════════
# PROGRAMA PRINCIPAL
# ═════════════════════════════════════════════════════════════

def main():
    global check_tpp
    global check_key

    check_tpp = False
    check_key = False
    idx_tpp = -1

    for idx, arg in enumerate(sys.argv):
        aux = arg.split('.')
        if aux[-1] == 'tpp':
            check_tpp = True
            idx_tpp = idx

        if arg == "-k":
            check_key = True

    if (not check_key and len(sys.argv) < 2) or (check_key and len(sys.argv) < 3):
        raise TypeError(error_handler.newError(check_key, 'ERR-GENCODE-USE'))

    if not check_tpp:
        raise IOError(error_handler.newError(check_key, 'ERR-GENCODE-NOT-TPP'))

    if not os.path.exists(sys.argv[idx_tpp]):
        raise IOError(error_handler.newError(check_key, 'ERR-GENCODE-FILE-NOT-EXISTS'))

    with open(sys.argv[idx_tpp], "r", encoding="utf-8") as data:
        source_file = data.read()

    import contextlib
    import io

    silent_stdout = io.StringIO()

    # 1. Parser
    with contextlib.redirect_stdout(silent_stdout):
        import tppparser
        tppparser.check_key = check_key
        tppparser.source_file = source_file
        tppparser.root = None
        tppparser.parser.parse(source_file)

    if tppparser.root is None:
        return

    # 2. Semântica
    with contextlib.redirect_stdout(silent_stdout):
        import tppsema
        tppsema.check_key = check_key
        analyser = tppsema.SemanticAnalyzer()
        analyser.run(tppparser.root)

    # Se houver erro semântico, não gera IR e não imprime nada em stdout.
    if analyser.errors:
        return

    # 3. Poda da árvore e geração de LLVM IR
    pruned_root = tppsema._prune(tppparser.root)

    generator = LLVMCodeGenerator(module_name=os.path.basename(sys.argv[idx_tpp]))
    llvm_ir = generator.generate(pruned_root)

    # Salva um .ll para facilitar execução manual com lli/clang.
    # Não imprime no terminal, porque o pytest espera stdout vazio para os .tpp válidos.
    with open(sys.argv[idx_tpp] + ".ll", "w", encoding="utf-8") as f:
        f.write(llvm_ir)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
