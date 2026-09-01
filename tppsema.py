import sys
import os
import logging

logging.basicConfig(
    level=logging.DEBUG,
    filename="sema.log",
    filemode="w",
    format="%(filename)10s:%(lineno)4d:%(message)s"
)
log = logging.getLogger()

from myerror import MyError
se = MyError('SemaErrors')

check_tpp = False
check_key = False
pruned_root = None  # árvore podada, acessível por outros módulos (ex: gerador de IR)


class Symbol:
    def __init__(self, name, kind, sym_type, scope, lineno=0, dimensions=None, params=None):
        self.name        = name
        self.kind        = kind          # 'var' | 'func' | 'param'
        self.sym_type    = sym_type      # 'inteiro' | 'flutuante' | 'vazio'
        self.scope       = scope
        self.lineno      = lineno
        self.dimensions  = dimensions or []
        self.params      = params or []  # list of (type_str, param_name)
        self.initialized = False
        self.used        = False


class SemanticAnalyzer:

    def __init__(self):
        self.table         = {}   # (name, scope) -> Symbol
        self.scope         = 'global'
        self.func          = None
        self.func_ret_type = None  # tipo de retorno declarado da função atual
        self.func_has_return = False
        self.errors        = []
        self.warnings      = []
        # Catálogo de símbolos globais coletados antes da análise dos corpos.
        # Ele permite chamadas/uso de globais declarados mais adiante no arquivo
        # sem alterar a ordem final de impressão dos avisos.
        self.global_catalog = {}

    # ── messaging ──────────────────────────────────────
    def _err(self, key, **kw):
        msg = se.newError(check_key, key, **kw)
        if msg:
            self.errors.append(msg)

    def _warn(self, key, **kw):
        msg = se.newError(check_key, key, **kw)
        if msg:
            self.warnings.append(msg)

    # ── symbol table ───────────────────────────────────
    def _declare(self, sym):
        k = (sym.name, sym.scope)
        if k in self.table:
            prev = self.table[k]
            self._warn('WAR-SEM-VAR-DECL-PREV', valor=sym.name, tipo=prev.sym_type)
            self.table[k] = sym
            return

        # Se o símbolo global já foi pré-coletado, insere o mesmo objeto
        # na tabela principal para preservar flags de uso/inicialização
        # eventualmente marcadas antes da declaração aparecer na ordem do arquivo.
        if sym.scope == 'global' and k in self.global_catalog:
            pre = self.global_catalog[k]
            pre.kind = sym.kind
            pre.sym_type = sym.sym_type
            pre.lineno = sym.lineno
            pre.dimensions = sym.dimensions
            pre.params = sym.params
            self.table[k] = pre
        else:
            self.table[k] = sym

    def _lookup(self, name):
        if (name, self.scope) in self.table:
            return self.table[(name, self.scope)]
        if (name, 'global') in self.table:
            return self.table[(name, 'global')]
        # Suporte a declarações globais que aparecem depois do ponto de uso.
        return self.global_catalog.get((name, 'global'))

    # ── tree helpers ───────────────────────────────────
    @staticmethod
    def _child(node, *types):
        for c in node.children:
            if c.type in types:
                return c
        return None

    @staticmethod
    def _children(node, *types):
        return [c for c in node.children if c.type in types]

    @staticmethod
    def _find_all(node, *types):
        result = []
        if node.type in types:
            result.append(node)
        for c in node.children:
            result.extend(SemanticAnalyzer._find_all(c, *types))
        return result

    @staticmethod
    def _id_name(id_node):
        """Extract string from an ID-type node (the leaf holds the actual name)."""
        for c in id_node.children:
            if c.type == 'ID':
                return c.name
        return id_node.name

    @staticmethod
    def _tipo_str(tipo_node):
        if tipo_node is None:
            return None
        for c in tipo_node.children:
            if c.type in ('INTEIRO', 'FLUTUANTE'):
                return c.type.lower()
        return None


    # ── pre-pass: global declarations ─────────────────────
    def _collect_global_catalog(self, node):
        """Coleta declarações globais antes de analisar corpos de funções.

        Isso evita falso positivo em casos como uma função usar uma variável
        global ou chamar outra função declarada mais abaixo no arquivo.
        A coleta não emite mensagens e não insere na tabela principal ainda,
        preservando a ordem dos avisos de pós-análise.
        """
        if node is None:
            return

        if node.type == 'DECLARACAO_FUNCAO':
            self._catalog_func(node)
            return  # não entra no corpo da função nesta etapa

        if node.type == 'DECLARACAO_VARIAVEIS':
            self._catalog_vars(node)
            return

        for c in node.children:
            self._collect_global_catalog(c)

    def _catalog_vars(self, node):
        tipo_node = self._child(node, 'TIPO')
        var_type = self._tipo_str(tipo_node)
        lista = self._child(node, 'LISTA_VARIAVEIS')
        self._catalog_lista_vars(lista, var_type)

    def _catalog_lista_vars(self, lista, var_type):
        if lista is None:
            return
        for c in lista.children:
            if c.type == 'VAR':
                id_node = self._child(c, 'ID')
                if id_node:
                    name = self._id_name(id_node)
                    dims = self._children(c, 'INDICE')
                    self.global_catalog.setdefault(
                        (name, 'global'),
                        Symbol(name, 'var', var_type, 'global',
                               lineno=getattr(c, 'lineno', 0), dimensions=dims)
                    )
            elif c.type == 'LISTA_VARIAVEIS':
                self._catalog_lista_vars(c, var_type)

    def _catalog_func(self, node):
        tipo_node = self._child(node, 'TIPO')
        ret_type = self._tipo_str(tipo_node) if tipo_node else 'vazio'
        cab = self._child(node, 'CABECALHO')
        if cab is None:
            return

        id_node = self._child(cab, 'ID')
        func_name = self._id_name(id_node) if id_node else '?'

        params = []
        l_params = self._child(cab, 'LISTA_PARAMETROS')
        if l_params:
            self._collect_params(l_params, params)

        self.global_catalog.setdefault(
            (func_name, 'global'),
            Symbol(func_name, 'func', ret_type, 'global',
                   lineno=getattr(cab, 'lineno', 0), params=params)
        )

    # ══════════════════════════════════════════════════
    # Main entry
    # ══════════════════════════════════════════════════
    def run(self, root):
        # 1ª etapa: coleta assinaturas e variáveis globais sem analisar corpos.
        # 2ª etapa: percorre a árvore normalmente e emite erros/avisos.
        self._collect_global_catalog(root)
        self._visit(root)
        self._post_checks()

    # ══════════════════════════════════════════════════
    # Visitor dispatch
    # ══════════════════════════════════════════════════
    def _visit(self, node):
        if node is None:
            return None

        t = node.type

        if t == 'DECLARACAO_VARIAVEIS':
            self._decl_var(node)
            return None

        if t == 'DECLARACAO_FUNCAO':
            self._decl_func(node)
            return None

        if t == 'ATRIBUICAO':
            return self._do_atrib(node)

        if t == 'SE':
            self._do_se(node); return None

        if t == 'REPITA':
            self._do_repita(node); return None

        if t == 'LEIA':
            self._do_leia(node); return None

        if t == 'ESCREVA':
            self._do_escreva(node); return None

        if t == 'RETORNA':
            return self._do_retorna(node)

        if t == 'CHAMADA_FUNCAO':
            return self._do_call(node)

        if t == 'VAR':
            return self._do_var(node)

        if t == 'NUMERO':
            return self._do_numero(node)

        # Generic: visit children, collect types
        types = []
        for c in node.children:
            r = self._visit(c)
            if r in ('inteiro', 'flutuante'):
                types.append(r)

        if types:
            return 'flutuante' if 'flutuante' in types else types[0]
        return None

    # ── declarations ───────────────────────────────────
    def _decl_var(self, node):
        tipo_node = self._child(node, 'TIPO')
        var_type  = self._tipo_str(tipo_node)
        lista     = self._child(node, 'LISTA_VARIAVEIS')
        self._decl_lista_vars(lista, var_type)

    def _decl_lista_vars(self, lista, var_type):
        if lista is None:
            return
        for c in lista.children:
            if c.type == 'VAR':
                self._decl_one_var(c, var_type)
            elif c.type == 'LISTA_VARIAVEIS':
                self._decl_lista_vars(c, var_type)

    def _decl_one_var(self, var_node, var_type):
        id_node = self._child(var_node, 'ID')
        if id_node is None:
            return
        name = self._id_name(id_node)
        dims = self._children(var_node, 'INDICE')

        # verifica tipo do índice já na declaração (ex: c[1.2] é erro)
        for idx in dims:
            for ic in idx.children:
                if ic.type not in ('ABRE_COLCHETE', 'FECHA_COLCHETE', 'SIMBOLO'):
                    t = self._visit(ic)
                    if t and t != 'inteiro':
                        self._err('ERR-SEM-ARRAY-INDEX-NOT-INT', valor=name)

        sym  = Symbol(name, 'var', var_type, self.scope,
                      lineno=getattr(var_node, 'lineno', 0),
                      dimensions=dims)
        self._declare(sym)

    def _decl_func(self, node):
        tipo_node = self._child(node, 'TIPO')
        ret_type  = self._tipo_str(tipo_node) if tipo_node else 'vazio'

        cab = self._child(node, 'CABECALHO')
        if cab is None:
            return

        id_node   = self._child(cab, 'ID')
        func_name = self._id_name(id_node) if id_node else '?'

        # collect params
        params   = []
        l_params = self._child(cab, 'LISTA_PARAMETROS')
        if l_params:
            self._collect_params(l_params, params)

        sym = Symbol(func_name, 'func', ret_type, 'global',
                     lineno=getattr(cab, 'lineno', 0), params=params)
        self._declare(sym)

        # enter function scope
        saved_scope, saved_func, saved_ret = self.scope, self.func, self.func_ret_type
        self.scope        = func_name
        self.func         = func_name
        self.func_ret_type = ret_type

        # declare params in local scope
        if l_params:
            self._decl_params(l_params)

        # visit body — collect return types found
        saved_has_return   = self.func_has_return
        self.func_has_return = False
        corpo = self._child(cab, 'CORPO')
        if corpo:
            self._visit(corpo)

        # if function declared non-void but no return found → type error
        if ret_type and ret_type != 'vazio' and not self.func_has_return:
            self._err('ERR-SEM-FUNC-RET-TYPE-ERROR',
                      valor=func_name, de='vazio', para=ret_type)

        self.func_has_return = saved_has_return
        self.scope           = saved_scope
        self.func            = saved_func
        self.func_ret_type   = saved_ret

    def _collect_params(self, lista, params):
        for c in lista.children:
            if c.type == 'PARAMETRO':
                tipo_node = self._child(c, 'TIPO')
                p_type    = self._tipo_str(tipo_node)
                id_node   = self._child(c, 'ID')
                if id_node:
                    params.append((p_type, self._id_name(id_node)))
            elif c.type == 'LISTA_PARAMETROS':
                self._collect_params(c, params)

    def _decl_params(self, lista):
        for c in lista.children:
            if c.type == 'PARAMETRO':
                tipo_node = self._child(c, 'TIPO')
                p_type    = self._tipo_str(tipo_node)
                id_node   = self._child(c, 'ID')
                if id_node:
                    name = self._id_name(id_node)
                    sym  = Symbol(name, 'param', p_type, self.scope,
                                  lineno=getattr(c, 'lineno', 0))
                    sym.initialized = True
                    self._declare(sym)
            elif c.type == 'LISTA_PARAMETROS':
                self._decl_params(c)

    # ── statements ─────────────────────────────────────
    def _do_atrib(self, node):
        var_node = self._child(node, 'VAR')
        # expression is everything that isn't VAR or ATRIBUICAO symbol nodes
        expr_types = []
        for c in node.children:
            if c.type not in ('VAR', 'ATRIBUICAO', 'SIMBOLO'):
                t = self._visit(c)
                if t:
                    expr_types.append(t)

        var_type = self._do_var(var_node, mark_used=False) if var_node else None

        # mark initialized
        if var_node:
            id_node = self._child(var_node, 'ID')
            if id_node:
                sym = self._lookup(self._id_name(id_node))
                if sym:
                    sym.initialized = True

        expr_type = ('flutuante' if 'flutuante' in expr_types else expr_types[0]) if expr_types else None

        if var_type and expr_type and var_type != expr_type:
            id_node = self._child(var_node, 'ID')
            vname   = self._id_name(id_node) if id_node else '?'
            self._warn('WAR-SEM-IMP-COERC-OF-VAR', valor=vname, de=expr_type, para=var_type)

        return var_type

    def _do_se(self, node):
        for c in node.children:
            if c.type not in ('SE', 'ENTAO', 'SENAO', 'FIM'):
                self._visit(c)

    def _do_repita(self, node):
        for c in node.children:
            if c.type not in ('REPITA', 'ATE'):
                self._visit(c)

    def _do_leia(self, node):
        var_node = self._child(node, 'VAR')
        if var_node:
            id_node = self._child(var_node, 'ID')
            if id_node:
                name = self._id_name(id_node)
                sym  = self._lookup(name)
                if sym is None:
                    self._err('ERR-SEM-VAR-NOT-DECL', valor=name)
                else:
                    sym.initialized = True
                    sym.used        = True

    def _do_escreva(self, node):
        for c in node.children:
            if c.type not in ('ESCREVA', 'ABRE_PARENTESE', 'FECHA_PARENTESE'):
                self._visit(c)

    def _do_retorna(self, node):
        ret_val_type = None
        for c in node.children:
            if c.type not in ('RETORNA', 'ABRE_PARENTESE', 'FECHA_PARENTESE', 'SIMBOLO'):
                ret_val_type = self._visit(c)
                break

        self.func_has_return = True

        if self.func and self.func_ret_type:
            expected = self.func_ret_type
            actual   = ret_val_type or 'vazio'
            if expected != 'vazio' and actual != 'vazio' and expected != actual:
                self._err('ERR-SEM-FUNC-RET-TYPE-ERROR',
                          valor=self.func, de=actual, para=expected)

        return ret_val_type

    def _do_call(self, node):
        id_node   = self._child(node, 'ID')
        func_name = self._id_name(id_node) if id_node else '?'

        sym = self.table.get((func_name, 'global')) or self.global_catalog.get((func_name, 'global'))
        if sym is None or sym.kind != 'func':
            self._err('ERR-SEM-CALL-FUNC-NOT-DECL', valor=func_name)
            return None

        sym.used = True

        if func_name == 'principal':
            if self.func == 'principal':
                self._warn('WAR-SEM-CALL-REC-FUNC-MAIN')
            else:
                self._err('ERR-SEM-CALL-FUNC-NOT-DECL', valor=func_name)
            return None

        lista_arg = self._child(node, 'LISTA_ARGUMENTOS')
        n_args    = self._count_args(lista_arg)
        n_params  = len(sym.params)

        if n_args < n_params:
            self._err('ERR-SEM-CALL-FUNC-WITH-FEW-ARGS', valor=func_name)
        elif n_args > n_params:
            self._err('ERR-SEM-CALL-FUNC-WITH-MANY-ARGS', valor=func_name)

        if lista_arg:
            arg_types = self._collect_arg_types(lista_arg)
            for i, arg_type in enumerate(arg_types):
                if i < len(sym.params):
                    param_type, _ = sym.params[i]
                    if arg_type and param_type and arg_type != param_type:
                        self._warn('WAR-SEM-ATR-DIFF-TYPES-IMP-COERC-OF-FUNC-ARG',
                                   valor=func_name, de=arg_type, para=param_type)

        return sym.sym_type

    def _count_args(self, lista):
        if lista is None:
            return 0
        n = 0
        for c in lista.children:
            if c.type in ('EXPRESSAO', 'EXPRESSAO_LOGICA', 'EXPRESSAO_SIMPLES',
                          'EXPRESSAO_ADITIVA', 'EXPRESSAO_MULTIPLICATIVA',
                          'EXPRESSAO_UNARIA', 'FATOR', 'VAR', 'NUMERO',
                          'CHAMADA_FUNCAO', 'ATRIBUICAO'):
                n += 1
            elif c.type == 'LISTA_ARGUMENTOS':
                n += self._count_args(c)
        return n

    def _collect_arg_types(self, lista):
        """Visita cada argumento e retorna lista de tipos inferidos."""
        if lista is None:
            return []
        types = []
        for c in lista.children:
            if c.type in ('EXPRESSAO', 'EXPRESSAO_LOGICA', 'EXPRESSAO_SIMPLES',
                          'EXPRESSAO_ADITIVA', 'EXPRESSAO_MULTIPLICATIVA',
                          'EXPRESSAO_UNARIA', 'FATOR', 'VAR', 'NUMERO',
                          'CHAMADA_FUNCAO', 'ATRIBUICAO'):
                types.append(self._visit(c))
            elif c.type == 'LISTA_ARGUMENTOS':
                types.extend(self._collect_arg_types(c))
        return types

    def _do_var(self, node, mark_used=True):
        if node is None:
            return None
        id_node = self._child(node, 'ID')
        if id_node is None:
            return None
        name = self._id_name(id_node)
        sym  = self._lookup(name)
        if sym is None:
            self._err('ERR-SEM-VAR-NOT-DECL', valor=name)
            return None
        if mark_used:
            sym.used = True

        indices = self._children(node, 'INDICE')
        for dim_i, idx in enumerate(indices):
            # visita a expressão do índice para checar tipo
            idx_type = None
            for ic in idx.children:
                if ic.type not in ('ABRE_COLCHETE', 'FECHA_COLCHETE', 'SIMBOLO'):
                    t = self._visit(ic)
                    if t:
                        idx_type = t
            if idx_type and idx_type != 'inteiro':
                self._err('ERR-SEM-ARRAY-INDEX-NOT-INT', valor=name)

            # verifica out-of-range se índice é literal inteiro
            idx_val = self._extract_int_literal(idx)
            if idx_val is not None and sym.dimensions and dim_i < len(sym.dimensions):
                dim_size = self._extract_int_literal(sym.dimensions[dim_i])
                if dim_size is not None and idx_val >= dim_size:
                    self._err('ERR-SEM-ARRAY-INDEX-OUT-OF-RANGE', valor=name)

        return sym.sym_type

    @staticmethod
    def _extract_int_literal(node):
        """Extrai valor inteiro de um nó literal, percorrendo a cadeia de expressão."""
        if node is None:
            return None
        # procura recursivamente um nó VALOR sob NUM_INTEIRO
        val_nodes = SemanticAnalyzer._find_all(node, 'VALOR')
        # verifica se o pai direto do VALOR é NUM_INTEIRO (não flutuante)
        for vn in val_nodes:
            if vn.parent and vn.parent.type == 'NUM_INTEIRO':
                try:
                    return int(vn.name)
                except ValueError:
                    pass
        return None

    def _do_numero(self, node):
        for c in node.children:
            if c.type == 'NUM_INTEIRO':
                return 'inteiro'
            if c.type in ('NUM_PONTO_FLUTUANTE', 'NUM_NOTACAO_CIENTIFICA'):
                return 'flutuante'
        return 'inteiro'

    # ── post-analysis ──────────────────────────────────
    def _post_checks(self):
        if ('principal', 'global') not in self.table:
            self._err('ERR-SEM-MAIN-NOT-DECL')

        for sym in self.table.values():
            if sym.kind == 'func' and not sym.used and sym.name != 'principal':
                self._warn('WAR-SEM-FUNC-DECL-NOT-USED', valor=sym.name)
            elif sym.kind == 'var':
                if not sym.used:
                    self._warn('WAR-SEM-VAR-DECL-NOT-USED', valor=sym.name)
                elif not sym.initialized:
                    self._warn('WAR-SEM-VAR-DECL-NOT-INIT', valor=sym.name)

    def print_results(self):
        for msg in self.errors:
            print(msg)
        for msg in self.warnings:
            print(msg)


# ─────────────────────────────────────────────────────────
# PODA DA AST
# ─────────────────────────────────────────────────────────

# Nós intermediários de expressão que são colapsáveis:
# se têm exatamente 1 filho que também é um nó de expressão,
# são apenas passagem e não adicionam semântica.
_PASSTHROUGH_TYPES = {
    'EXPRESSAO',
    'EXPRESSAO_LOGICA',
    'EXPRESSAO_SIMPLES',
    'EXPRESSAO_ADITIVA',
    'EXPRESSAO_MULTIPLICATIVA',
    'EXPRESSAO_UNARIA',
    'FATOR',
    'NUMERO',
    'DECLARACAO',
    'LISTA_DECLARACOES',
    'INICIALIZACAO_VARIAVEIS',
    'LISTA_VARIAVEIS',
    'VAZIO',
}

# Nós cujos filhos são apenas decoração sintática (parênteses, fim, etc.)
# e que devem ser completamente removidos da árvore podada.
_REMOVE_TYPES = {
    'ABRE_PARENTESE',
    'FECHA_PARENTESE',
    'ABRE_COLCHETE',
    'FECHA_COLCHETE',
    'VIRGULA',
    'DOIS_PONTOS',
    'FIM',
    'SIMBOLO',
    'ENTAO',
    'SENAO',
    'ATE',
}


def _prune(node):
    """
    Percorre a AST em pós-ordem e retorna a versão podada do nó.

    Regras:
    1. Nós do tipo REMOVE_TYPES são descartados (retorna None).
    2. Nós do tipo PASSTHROUGH com exatamente 1 filho relevante são colapsados:
       o filho sobe no lugar do pai.
    3. Todos os outros nós têm seus filhos podados recursivamente.

    IMPORTANTE: esta função NÃO modifica a árvore original — constrói
    uma nova árvore com nós desconectados (parent=None) para não
    quebrar a AST usada durante a análise semântica.
    """
    from mytree import MyNode

    if node is None:
        return None

    # Regra 1: descartar nós de decoração sintática
    if node.type in _REMOVE_TYPES:
        return None

    # Poda recursiva dos filhos
    pruned_children = []
    for c in node.children:
        pc = _prune(c)
        if pc is not None:
            pruned_children.append(pc)

    # Regra 2: colapsar nós de passagem com filho único
    if node.type in _PASSTHROUGH_TYPES and len(pruned_children) == 1:
        return pruned_children[0]

    # Regra 3: reconstruir nó com filhos podados
    new_node = MyNode(name=node.name, type=node.type)
    for c in pruned_children:
        c.parent = new_node

    return new_node


def export_pruned_tree(root, filepath):
    """Poda a AST e exporta como PNG e DOT."""
    from anytree.exporter import DotExporter, UniqueDotExporter

    pruned = _prune(root)
    if pruned is None:
        return None

    UniqueDotExporter(pruned).to_picture(filepath + ".pruned.ast.png")
    UniqueDotExporter(pruned).to_dotfile(filepath + ".pruned.ast.dot")

    return pruned


# ─────────────────────────────────────────────────────────
def main():
    global check_tpp, check_key

    check_tpp     = False
    check_key     = False
    check_gentree = False
    idx_tpp       = -1

    for idx, arg in enumerate(sys.argv):
        aux = arg.split('.')
        if aux[-1] == 'tpp':
            check_tpp = True
            idx_tpp   = idx
        if arg == '-k':
            check_key = True
        if arg == '-t':
            check_gentree = True

    if len(sys.argv) < 2 or (len(sys.argv) == 2 and '-k' in sys.argv):
        raise TypeError(se.newError(check_key, 'ERR-SEM-USE'))

    if not check_tpp:
        raise IOError(se.newError(check_key, 'ERR-SEM-NOT-TPP'))
    elif not os.path.exists(sys.argv[idx_tpp]):
        raise IOError(se.newError(check_key, 'ERR-SEM-FILE-NOT-EXISTS'))

    import tppparser
    tppparser.check_key = check_key
    with open(sys.argv[idx_tpp], 'r', encoding='utf-8') as f:
        source = f.read()
    tppparser.source_file = source
    tppparser.parser.parse(source)

    root = tppparser.root
    if root is None:
        return

    analyser = SemanticAnalyzer()
    analyser.run(root)
    analyser.print_results()

    global pruned_root
    pruned_root = _prune(root)
    if check_gentree:
        export_pruned_tree(root, sys.argv[idx_tpp])


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)