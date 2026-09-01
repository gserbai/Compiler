import sys
import os
import logging

# Configura o log de depuração em arquivo (não aparece no terminal)
logging.basicConfig(
    level=logging.DEBUG,
    filename="sema.log",
    filemode="w",
    format="%(filename)10s:%(lineno)4d:%(message)s"
)
log = logging.getLogger()

# MyError é o gerenciador de mensagens de erro/aviso do compilador.
# Ele lê as mensagens do arquivo ErrorMessages.properties e formata
# a saída dependendo do modo: chave (-k) ou mensagem legível.
from myerror import MyError
se = MyError('SemaErrors')

# Flags globais controladas pelos argumentos de linha de comando
check_tpp = False   # indica se um arquivo .tpp foi fornecido
check_key = False   # se True, imprime só a chave do erro (ex: ERR-SEM-VAR-NOT-DECL)
pruned_root = None  # raiz da ASTO podada, usada por módulos futuros (ex: gerador de IR)


# ─────────────────────────────────────────────────────────
# CLASSE Symbol
# Representa uma entrada na Tabela de Símbolos.
# Cada variável, função ou parâmetro declarado no programa
# tem um Symbol associado.
# ─────────────────────────────────────────────────────────
class Symbol:
    def __init__(self, name, kind, sym_type, scope, lineno=0, dimensions=None, params=None):
        self.name        = name         # nome do identificador (ex: 'x', 'principal')
        self.kind        = kind         # categoria: 'var' | 'func' | 'param'
        self.sym_type    = sym_type     # tipo TPP: 'inteiro' | 'flutuante' | 'vazio'
        self.scope       = scope        # escopo onde foi declarado: 'global' ou nome da função
        self.lineno      = lineno       # linha da declaração no código-fonte
        self.dimensions  = dimensions or []  # lista de nós INDICE (só para arrays)
        self.params      = params or []      # lista de (tipo, nome) dos parâmetros (só para funções)
        self.initialized = False        # True se a variável já recebeu algum valor
        self.used        = False        # True se a variável foi lida em alguma expressão


# ─────────────────────────────────────────────────────────
# CLASSE SemanticAnalyzer
# Percorre a ASA produzida pelo parser e realiza todas as
# verificações semânticas da linguagem TPP.
# ─────────────────────────────────────────────────────────
class SemanticAnalyzer:

    def __init__(self):
        # Tabela de Símbolos: dicionário com chave (nome, escopo) → Symbol
        # Usar tupla como chave permite que 'x' em 'global' e 'x' em 'func'
        # coexistam sem conflito.
        self.table         = {}

        # Escopo atual durante a varredura (começa global, muda ao entrar em função)
        self.scope         = 'global'

        # Nome da função sendo analisada no momento (None se estiver no global)
        self.func          = None

        # Tipo de retorno declarado da função atual (ex: 'inteiro')
        self.func_ret_type = None

        # Flag: indica se encontramos pelo menos um nó RETORNA no corpo da função atual
        self.func_has_return = False

        # Listas de mensagens acumuladas durante a análise
        self.errors        = []
        self.warnings      = []

    # ──────────────────────────────────────────────────────
    # EMISSÃO DE ERROS E AVISOS
    # _err  → erro semântico (ERR-SEM-*)
    # _warn → aviso semântico (WAR-SEM-*)
    # Ambos delegam ao MyError que formata a mensagem e
    # armazenam na lista correspondente para impressão final.
    # ──────────────────────────────────────────────────────
    def _err(self, key, **kw):
        msg = se.newError(check_key, key, **kw)
        if msg:
            self.errors.append(msg)

    def _warn(self, key, **kw):
        msg = se.newError(check_key, key, **kw)
        if msg:
            self.warnings.append(msg)

    # ──────────────────────────────────────────────────────
    # OPERAÇÕES NA TABELA DE SÍMBOLOS
    # ──────────────────────────────────────────────────────

    def _declare(self, sym):
        """Insere um Symbol na tabela. Se já existir (mesma chave),
        emite aviso de redeclaração antes de sobrescrever."""
        k = (sym.name, sym.scope)
        if k in self.table:
            prev = self.table[k]
            self._warn('WAR-SEM-VAR-DECL-PREV', valor=sym.name, tipo=prev.sym_type)
        self.table[k] = sym

    def _lookup(self, name):
        """Busca um símbolo pelo nome.
        Verifica primeiro o escopo local (função atual),
        depois o escopo global. Retorna None se não encontrar."""
        if (name, self.scope) in self.table:
            return self.table[(name, self.scope)]
        if (name, 'global') in self.table:
            return self.table[(name, 'global')]
        return None

    # ──────────────────────────────────────────────────────
    # UTILITÁRIOS PARA NAVEGAR NA ASA
    # ──────────────────────────────────────────────────────

    @staticmethod
    def _child(node, *types):
        """Retorna o primeiro filho do nó cujo tipo esteja em `types`.
        Útil para achar um filho específico sem varrer manualmente."""
        for c in node.children:
            if c.type in types:
                return c
        return None

    @staticmethod
    def _children(node, *types):
        """Retorna todos os filhos do nó cujo tipo esteja em `types`."""
        return [c for c in node.children if c.type in types]

    @staticmethod
    def _find_all(node, *types):
        """Busca recursiva em toda a subárvore: retorna todos os nós
        cujo tipo esteja em `types`, em pré-ordem."""
        result = []
        if node.type in types:
            result.append(node)
        for c in node.children:
            result.extend(SemanticAnalyzer._find_all(c, *types))
        return result

    @staticmethod
    def _id_name(id_node):
        """Extrai o nome (string) de um nó ID.
        O nó ID pode ter um filho com o valor real, ou o valor
        está no próprio atributo name do nó."""
        for c in id_node.children:
            if c.type == 'ID':
                return c.name
        return id_node.name

    @staticmethod
    def _tipo_str(tipo_node):
        """Extrai o tipo como string ('inteiro' ou 'flutuante')
        a partir de um nó TIPO da ASA."""
        if tipo_node is None:
            return None
        for c in tipo_node.children:
            if c.type in ('INTEIRO', 'FLUTUANTE'):
                return c.type.lower()   # 'INTEIRO' → 'inteiro'
        return None

    # ══════════════════════════════════════════════════════
    # PONTO DE ENTRADA DA ANÁLISE
    # ══════════════════════════════════════════════════════
    def run(self, root):
        """Executa a análise semântica completa:
        1. Varredura única da ASA (_visit)
        2. Verificações globais pós-varredura (_post_checks)"""
        self._visit(root)
        self._post_checks()

    # ══════════════════════════════════════════════════════
    # VISITOR — despacha cada nó para o método correto
    # ══════════════════════════════════════════════════════
    def _visit(self, node):
        """Examina o tipo do nó e chama o método especializado.
        Retorna o tipo inferido da expressão ('inteiro', 'flutuante' ou None)."""
        if node is None:
            return None

        t = node.type

        # Declaração de variável: popula a tabela de símbolos
        if t == 'DECLARACAO_VARIAVEIS':
            self._decl_var(node)
            return None

        # Declaração de função: registra a função e analisa o corpo
        if t == 'DECLARACAO_FUNCAO':
            self._decl_func(node)
            return None

        # Atribuição: verifica tipos e marca variável como inicializada
        if t == 'ATRIBUICAO':
            return self._do_atrib(node)

        # Estrutura condicional: visita condição e corpo(s)
        if t == 'SE':
            self._do_se(node); return None

        # Estrutura de repetição: visita corpo e condição de parada
        if t == 'REPITA':
            self._do_repita(node); return None

        # Leitura de variável: marca como inicializada e usada
        if t == 'LEIA':
            self._do_leia(node); return None

        # Escrita de expressão: visita a expressão interna
        if t == 'ESCREVA':
            self._do_escreva(node); return None

        # Retorno de função: verifica compatibilidade de tipo com a declaração
        if t == 'RETORNA':
            return self._do_retorna(node)

        # Chamada de função: verifica existência, aridade e tipos dos argumentos
        if t == 'CHAMADA_FUNCAO':
            return self._do_call(node)

        # Referência a variável: lookup na tabela, verifica índices de array
        if t == 'VAR':
            return self._do_var(node)

        # Literal numérico: retorna o tipo ('inteiro' ou 'flutuante')
        if t == 'NUMERO':
            return self._do_numero(node)

        # Caso genérico: nó não reconhecido explicitamente.
        # Visita todos os filhos e propaga o tipo mais "contaminante":
        # se qualquer filho for flutuante, o resultado é flutuante.
        types = []
        for c in node.children:
            r = self._visit(c)
            if r in ('inteiro', 'flutuante'):
                types.append(r)

        if types:
            return 'flutuante' if 'flutuante' in types else types[0]
        return None

    # ──────────────────────────────────────────────────────
    # DECLARAÇÕES
    # ──────────────────────────────────────────────────────

    def _decl_var(self, node):
        """Processa um nó DECLARACAO_VARIAVEIS.
        Extrai o tipo e delega a declaração de cada variável da lista."""
        tipo_node = self._child(node, 'TIPO')
        var_type  = self._tipo_str(tipo_node)          # 'inteiro' ou 'flutuante'
        lista     = self._child(node, 'LISTA_VARIAVEIS')
        self._decl_lista_vars(lista, var_type)

    def _decl_lista_vars(self, lista, var_type):
        """Percorre recursivamente a LISTA_VARIAVEIS e declara cada VAR."""
        if lista is None:
            return
        for c in lista.children:
            if c.type == 'VAR':
                self._decl_one_var(c, var_type)
            elif c.type == 'LISTA_VARIAVEIS':
                # lista pode ser aninhada pela gramática recursiva à esquerda
                self._decl_lista_vars(c, var_type)

    def _decl_one_var(self, var_node, var_type):
        """Declara uma única variável na tabela de símbolos.
        Se for array, verifica se o índice de declaração é inteiro."""
        id_node = self._child(var_node, 'ID')
        if id_node is None:
            return
        name = self._id_name(id_node)
        dims = self._children(var_node, 'INDICE')  # lista de dimensões (vazia se não for array)

        # Verifica o tipo do índice já na declaração
        # Ex: inteiro: c[1.2] → índice 1.2 é flutuante → erro
        for idx in dims:
            for ic in idx.children:
                if ic.type not in ('ABRE_COLCHETE', 'FECHA_COLCHETE', 'SIMBOLO'):
                    t = self._visit(ic)
                    if t and t != 'inteiro':
                        self._err('ERR-SEM-ARRAY-INDEX-NOT-INT', valor=name)

        # Cria e registra o símbolo na tabela
        sym = Symbol(name, 'var', var_type, self.scope,
                     lineno=getattr(var_node, 'lineno', 0),
                     dimensions=dims)
        self._declare(sym)

    def _decl_func(self, node):
        """Processa um nó DECLARACAO_FUNCAO:
        1. Registra a função na tabela (escopo global)
        2. Muda para o escopo local da função
        3. Declara os parâmetros no escopo local
        4. Visita o corpo
        5. Restaura o escopo anterior"""
        tipo_node = self._child(node, 'TIPO')
        # Se não tiver tipo declarado, a função é 'vazio' (procedimento)
        ret_type  = self._tipo_str(tipo_node) if tipo_node else 'vazio'

        cab = self._child(node, 'CABECALHO')
        if cab is None:
            return

        id_node   = self._child(cab, 'ID')
        func_name = self._id_name(id_node) if id_node else '?'

        # Coleta os parâmetros como lista de (tipo, nome) para guardar no Symbol
        params   = []
        l_params = self._child(cab, 'LISTA_PARAMETROS')
        if l_params:
            self._collect_params(l_params, params)

        # Registra a função na tabela de símbolos (sempre escopo global)
        sym = Symbol(func_name, 'func', ret_type, 'global',
                     lineno=getattr(cab, 'lineno', 0), params=params)
        self._declare(sym)

        # Salva o estado do escopo atual antes de entrar na função
        saved_scope, saved_func, saved_ret = self.scope, self.func, self.func_ret_type
        self.scope         = func_name   # escopo local = nome da função
        self.func          = func_name
        self.func_ret_type = ret_type

        # Declara os parâmetros formais no escopo local da função
        if l_params:
            self._decl_params(l_params)

        # Salva e reseta o flag de retorno para essa função
        saved_has_return     = self.func_has_return
        self.func_has_return = False

        # Visita o corpo da função para checar todas as instruções
        corpo = self._child(cab, 'CORPO')
        if corpo:
            self._visit(corpo)

        # Se a função tem tipo não-vazio mas nenhum RETORNA foi encontrado → erro
        if ret_type and ret_type != 'vazio' and not self.func_has_return:
            self._err('ERR-SEM-FUNC-RET-TYPE-ERROR',
                      valor=func_name, de='vazio', para=ret_type)

        # Restaura o estado do escopo anterior (sai da função)
        self.func_has_return = saved_has_return
        self.scope           = saved_scope
        self.func            = saved_func
        self.func_ret_type   = saved_ret

    def _collect_params(self, lista, params):
        """Coleta os parâmetros da lista e preenche a lista `params`
        com tuplas (tipo, nome). Usada para armazenar no Symbol da função."""
        for c in lista.children:
            if c.type == 'PARAMETRO':
                tipo_node = self._child(c, 'TIPO')
                p_type    = self._tipo_str(tipo_node)
                id_node   = self._child(c, 'ID')
                if id_node:
                    params.append((p_type, self._id_name(id_node)))
            elif c.type == 'LISTA_PARAMETROS':
                self._collect_params(c, params)  # recursão pela gramática

    def _decl_params(self, lista):
        """Declara cada parâmetro formal como Symbol no escopo local da função.
        Parâmetros já nascem com initialized=True pois recebem valor na chamada."""
        for c in lista.children:
            if c.type == 'PARAMETRO':
                tipo_node = self._child(c, 'TIPO')
                p_type    = self._tipo_str(tipo_node)
                id_node   = self._child(c, 'ID')
                if id_node:
                    name = self._id_name(id_node)
                    sym  = Symbol(name, 'param', p_type, self.scope,
                                  lineno=getattr(c, 'lineno', 0))
                    sym.initialized = True   # parâmetro sempre começa inicializado
                    self._declare(sym)
            elif c.type == 'LISTA_PARAMETROS':
                self._decl_params(c)

    # ──────────────────────────────────────────────────────
    # INSTRUÇÕES
    # ──────────────────────────────────────────────────────

    def _do_atrib(self, node):
        """Processa uma atribuição (var := expressao):
        1. Visita a expressão do lado direito para inferir seu tipo
        2. Resolve a variável destino (lado esquerdo)
        3. Marca a variável como inicializada
        4. Verifica coerção implícita de tipo se os tipos divergirem"""
        var_node = self._child(node, 'VAR')

        # Visita todos os filhos que não são a variável destino nem o símbolo ':='
        expr_types = []
        for c in node.children:
            if c.type not in ('VAR', 'ATRIBUICAO', 'SIMBOLO'):
                t = self._visit(c)
                if t:
                    expr_types.append(t)

        # Resolve o tipo da variável destino (mark_used=False pois atribuição não é "uso")
        var_type = self._do_var(var_node, mark_used=False) if var_node else None

        # Marca a variável destino como inicializada
        if var_node:
            id_node = self._child(var_node, 'ID')
            if id_node:
                sym = self._lookup(self._id_name(id_node))
                if sym:
                    sym.initialized = True

        # Tipo da expressão: flutuante "contamina" (se algum operando for flutuante, tudo é)
        expr_type = ('flutuante' if 'flutuante' in expr_types else expr_types[0]) if expr_types else None

        # Se tipos são incompatíveis, emite aviso de coerção implícita
        if var_type and expr_type and var_type != expr_type:
            id_node = self._child(var_node, 'ID')
            vname   = self._id_name(id_node) if id_node else '?'
            self._warn('WAR-SEM-IMP-COERC-OF-VAR', valor=vname, de=expr_type, para=var_type)

        return var_type

    def _do_se(self, node):
        """Visita os filhos do SE ignorando os tokens de decoração
        (SE, ENTAO, SENAO, FIM são palavras-chave, não têm semântica própria)."""
        for c in node.children:
            if c.type not in ('SE', 'ENTAO', 'SENAO', 'FIM'):
                self._visit(c)

    def _do_repita(self, node):
        """Visita o corpo e a condição do REPITA,
        ignorando os tokens REPITA e ATE."""
        for c in node.children:
            if c.type not in ('REPITA', 'ATE'):
                self._visit(c)

    def _do_leia(self, node):
        """Processa leia(var): busca a variável na tabela e
        marca como inicializada e usada (leia é uma forma de inicialização)."""
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
        """Processa escreva(expressao): visita a expressão interna
        ignorando os tokens de estrutura."""
        for c in node.children:
            if c.type not in ('ESCREVA', 'ABRE_PARENTESE', 'FECHA_PARENTESE'):
                self._visit(c)

    def _do_retorna(self, node):
        """Processa retorna(expressao):
        1. Infere o tipo do valor retornado
        2. Marca que a função possui retorno (func_has_return = True)
        3. Verifica se o tipo retornado bate com o declarado na função"""
        ret_val_type = None
        for c in node.children:
            if c.type not in ('RETORNA', 'ABRE_PARENTESE', 'FECHA_PARENTESE', 'SIMBOLO'):
                ret_val_type = self._visit(c)
                break  # só o primeiro filho relevante é o valor retornado

        # Sinaliza que encontramos pelo menos um retorno nesta função
        self.func_has_return = True

        # Verifica compatibilidade: tipo retornado vs tipo declarado
        if self.func and self.func_ret_type:
            expected = self.func_ret_type
            actual   = ret_val_type or 'vazio'
            # Só emite erro se ambos são concretos e divergem
            if expected != 'vazio' and actual != 'vazio' and expected != actual:
                self._err('ERR-SEM-FUNC-RET-TYPE-ERROR',
                          valor=self.func, de=actual, para=expected)

        return ret_val_type

    def _do_call(self, node):
        """Processa uma chamada de função:
        1. Verifica se a função foi declarada
        2. Marca a função como usada
        3. Bloqueia chamadas a principal de outros escopos
        4. Verifica aridade (nº de argumentos vs nº de parâmetros)
        5. Verifica tipos dos argumentos vs parâmetros formais"""
        id_node   = self._child(node, 'ID')
        func_name = self._id_name(id_node) if id_node else '?'

        # Funções são sempre declaradas no escopo global
        sym = self.table.get((func_name, 'global'))
        if sym is None:
            self._err('ERR-SEM-CALL-FUNC-NOT-DECL', valor=func_name)
            return None

        # Marca a função como utilizada
        sym.used = True

        # Chamadas à principal são proibidas (exceto recursão dentro dela mesma)
        if func_name == 'principal':
            if self.func == 'principal':
                self._warn('WAR-SEM-CALL-REC-FUNC-MAIN')  # recursão: aviso
            else:
                self._err('ERR-SEM-CALL-FUNC-MAIN-NOT-ALLOWED')  # outro escopo: erro

        # Conta quantos argumentos foram passados na chamada
        lista_arg = self._child(node, 'LISTA_ARGUMENTOS')
        n_args    = self._count_args(lista_arg)
        n_params  = len(sym.params)

        # Verifica aridade
        if n_args < n_params:
            self._err('ERR-SEM-CALL-FUNC-WITH-FEW-ARGS', valor=func_name)
        elif n_args > n_params:
            self._err('ERR-SEM-CALL-FUNC-WITH-MANY-ARGS', valor=func_name)

        # Verifica tipos dos argumentos posicionalmente
        if lista_arg:
            arg_types = self._collect_arg_types(lista_arg)
            for i, arg_type in enumerate(arg_types):
                if i < len(sym.params):
                    param_type, _ = sym.params[i]
                    if arg_type and param_type and arg_type != param_type:
                        self._warn('WAR-SEM-ATR-DIFF-TYPES-IMP-COERC-OF-FUNC-ARG',
                                   valor=func_name, de=arg_type, para=param_type)

        # Retorna o tipo de retorno da função chamada (para uso em expressões)
        return sym.sym_type

    def _count_args(self, lista):
        """Conta recursivamente quantos argumentos existem na LISTA_ARGUMENTOS.
        A lista pode ser aninhada pela gramática recursiva à esquerda."""
        if lista is None:
            return 0
        n = 0
        for c in lista.children:
            # Cada nó de expressão no nível atual é um argumento
            if c.type in ('EXPRESSAO', 'EXPRESSAO_LOGICA', 'EXPRESSAO_SIMPLES',
                          'EXPRESSAO_ADITIVA', 'EXPRESSAO_MULTIPLICATIVA',
                          'EXPRESSAO_UNARIA', 'FATOR', 'VAR', 'NUMERO',
                          'CHAMADA_FUNCAO', 'ATRIBUICAO'):
                n += 1
            elif c.type == 'LISTA_ARGUMENTOS':
                n += self._count_args(c)  # recursão pela gramática
        return n

    def _collect_arg_types(self, lista):
        """Visita cada argumento na LISTA_ARGUMENTOS e retorna lista de tipos inferidos.
        Usado para checar compatibilidade com os parâmetros formais."""
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
        """Processa uma referência a variável (nó VAR):
        1. Busca na tabela de símbolos
        2. Marca como usada (se mark_used=True)
        3. Verifica tipo e valor dos índices (para arrays)
        Retorna o tipo da variável ou None se não encontrada."""
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

        # Verifica cada índice de acesso ao array
        indices = self._children(node, 'INDICE')
        for dim_i, idx in enumerate(indices):
            # Infere o tipo da expressão de índice
            idx_type = None
            for ic in idx.children:
                if ic.type not in ('ABRE_COLCHETE', 'FECHA_COLCHETE', 'SIMBOLO'):
                    t = self._visit(ic)
                    if t:
                        idx_type = t
            # Índice deve ser inteiro
            if idx_type and idx_type != 'inteiro':
                self._err('ERR-SEM-ARRAY-INDEX-NOT-INT', valor=name)

            # Se o índice for um literal inteiro, verifica se está dentro do tamanho declarado
            idx_val = self._extract_int_literal(idx)
            if idx_val is not None and sym.dimensions and dim_i < len(sym.dimensions):
                dim_size = self._extract_int_literal(sym.dimensions[dim_i])
                if dim_size is not None and idx_val >= dim_size:
                    self._err('ERR-SEM-ARRAY-INDEX-OUT-OF-RANGE', valor=name)

        return sym.sym_type

    @staticmethod
    def _extract_int_literal(node):
        """Tenta extrair o valor numérico inteiro de um nó de índice.
        Percorre a subárvore procurando nó VALOR filho de NUM_INTEIRO.
        Retorna o inteiro se encontrar, ou None caso contrário."""
        if node is None:
            return None
        val_nodes = SemanticAnalyzer._find_all(node, 'VALOR')
        for vn in val_nodes:
            # Só considera se o pai for NUM_INTEIRO (descarta flutuantes)
            if vn.parent and vn.parent.type == 'NUM_INTEIRO':
                try:
                    return int(vn.name)
                except ValueError:
                    pass
        return None

    def _do_numero(self, node):
        """Determina o tipo de um literal numérico:
        NUM_INTEIRO → 'inteiro'
        NUM_PONTO_FLUTUANTE ou NUM_NOTACAO_CIENTIFICA → 'flutuante'"""
        for c in node.children:
            if c.type == 'NUM_INTEIRO':
                return 'inteiro'
            if c.type in ('NUM_PONTO_FLUTUANTE', 'NUM_NOTACAO_CIENTIFICA'):
                return 'flutuante'
        return 'inteiro'  # fallback seguro

    # ──────────────────────────────────────────────────────
    # VERIFICAÇÕES PÓS-ANÁLISE
    # Executadas depois que toda a ASA foi percorrida.
    # Dependem do estado completo da tabela de símbolos.
    # ──────────────────────────────────────────────────────
    def _post_checks(self):
        """Verifica regras que só podem ser checadas após varrer o programa inteiro:
        - Existência da função principal
        - Funções declaradas e não usadas
        - Variáveis declaradas e não usadas
        - Variáveis usadas mas nunca inicializadas"""

        # Função principal é obrigatória em todo programa TPP
        if ('principal', 'global') not in self.table:
            self._err('ERR-SEM-MAIN-NOT-DECL')

        for sym in self.table.values():
            if sym.kind == 'func' and not sym.used and sym.name != 'principal':
                # Função declarada mas nunca chamada (principal é exceção: não precisa ser chamada)
                self._warn('WAR-SEM-FUNC-DECL-NOT-USED', valor=sym.name)
            elif sym.kind == 'var':
                if not sym.used:
                    # Variável declarada mas nunca lida em nenhuma expressão
                    self._warn('WAR-SEM-VAR-DECL-NOT-USED', valor=sym.name)
                elif not sym.initialized:
                    # Variável foi lida mas nunca recebeu valor (potencial lixo de memória)
                    self._warn('WAR-SEM-VAR-DECL-NOT-INIT', valor=sym.name)

    def print_results(self):
        """Imprime todos os erros primeiro, depois todos os avisos."""
        for msg in self.errors:
            print(msg)
        for msg in self.warnings:
            print(msg)


# ─────────────────────────────────────────────────────────
# PODA DA AST → gera a ASTO (Árvore Sintática Abstrata Podada)
# ─────────────────────────────────────────────────────────

# Nós intermediários de expressão que são apenas "passagem":
# quando têm exatamente 1 filho relevante após a poda,
# o filho sobe no lugar do pai (colapso). Isso elimina cadeias
# desnecessárias como EXPRESSAO → EXPRESSAO_LOGICA → EXPRESSAO_SIMPLES → VAR
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

# Nós de pura decoração sintática: existem na gramática concreta
# mas não carregam semântica. São descartados completamente na poda.
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
    Percorre a AST em pós-ordem e retorna a versão podada (ASTO).

    Regras:
    1. Nós em _REMOVE_TYPES → descarta (retorna None)
    2. Nós em _PASSTHROUGH_TYPES com exatamente 1 filho → colapsa (filho sobe)
    3. Demais nós → reconstrói com filhos já podados

    IMPORTANTE: não modifica a ASA original. Constrói uma árvore nova
    com novos objetos MyNode, preservando a ASA para outros módulos.
    """
    from mytree import MyNode

    if node is None:
        return None

    # Regra 1: descarta decoração sintática
    if node.type in _REMOVE_TYPES:
        return None

    # Poda recursiva em pós-ordem: poda filhos antes de decidir sobre o pai
    pruned_children = []
    for c in node.children:
        pc = _prune(c)
        if pc is not None:
            pruned_children.append(pc)

    # Regra 2: colapsa nó de passagem com filho único
    if node.type in _PASSTHROUGH_TYPES and len(pruned_children) == 1:
        return pruned_children[0]

    # Regra 3: reconstrói o nó com os filhos podados
    new_node = MyNode(name=node.name, type=node.type)
    for c in pruned_children:
        c.parent = new_node

    return new_node


def export_pruned_tree(root, filepath):
    """Poda a AST e exporta a ASTO como PNG e DOT (via Graphviz)."""
    from anytree.exporter import DotExporter, UniqueDotExporter

    pruned = _prune(root)
    if pruned is None:
        return None

    UniqueDotExporter(pruned).to_picture(filepath + ".pruned.ast.png")
    UniqueDotExporter(pruned).to_dotfile(filepath + ".pruned.ast.dot")

    return pruned


# ─────────────────────────────────────────────────────────
# MAIN — ponto de entrada quando executado diretamente
# ─────────────────────────────────────────────────────────
def main():
    global check_tpp, check_key

    check_tpp     = False  # True se arquivo .tpp foi passado
    check_key     = False  # True se flag -k foi passada (saída em chaves)
    check_gentree = False  # True se flag -t foi passada (gera imagem da árvore)
    idx_tpp       = -1     # índice do argumento .tpp no sys.argv

    # Processa os argumentos de linha de comando
    for idx, arg in enumerate(sys.argv):
        aux = arg.split('.')
        if aux[-1] == 'tpp':
            check_tpp = True
            idx_tpp   = idx
        if arg == '-k':
            check_key = True
        if arg == '-t':
            check_gentree = True

    # Validações de uso
    if len(sys.argv) < 2 or (len(sys.argv) == 2 and '-k' in sys.argv):
        raise TypeError(se.newError(check_key, 'ERR-SEM-USE'))

    if not check_tpp:
        raise IOError(se.newError(check_key, 'ERR-SEM-NOT-TPP'))
    elif not os.path.exists(sys.argv[idx_tpp]):
        raise IOError(se.newError(check_key, 'ERR-SEM-FILE-NOT-EXISTS'))

    # Importa e executa o parser para obter a ASA
    import tppparser
    tppparser.check_key = check_key
    with open(sys.argv[idx_tpp], 'r', encoding='utf-8') as f:
        source = f.read()
    tppparser.parser.parse(source)

    root = tppparser.root
    if root is None:
        return

    # Executa a análise semântica e imprime resultados
    analyser = SemanticAnalyzer()
    analyser.run(root)
    analyser.print_results()

    # Gera e opcionalmente exporta a ASTO podada
    global pruned_root
    pruned_root = _prune(root)
    if check_gentree:
        export_pruned_tree(root, sys.argv[idx_tpp])


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
