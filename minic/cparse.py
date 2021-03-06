# cparse.py
# coding: utf-8
r"""
Proyecto 2: Escribir un analizador
==================================
En este proyecto, escribes el shell básico de un analizador para MiniC.
A continuación se incluye la forma BNF del lenguaje. Su tarea es escribir
las reglas de análisis y construir el AST para esta gramática usando SLY.
La siguiente gramática es parcial. Se agregan más características en
proyectos posteriores.

	program : decl_list

	decl_list : decl_list decl
			| decl

	decl : var_decl
			| fun_decl

	var_decl : type_spec IDENT ;
			| type_spec IDENT [ ] ;

	type_spec : VOID
			| BOOL
			| INT
			| FLOAT

	fun_decl : type_spec IDENT ( params ) compound_stmt

	params : param_list
			| VOID

	param_list : param_list , param
			| param

	param : type_spec IDENT
			| type_spec IDENT [ ]

	compound_stmt : { local_decls stmt_list }

	local_decls : local_decls local_decl
			| empty

	local_decl : type_spec IDENT ;
			| type_spec IDENT [ ] ;

	stmt_list : stmt_list stmt
			| empty

	stmt : expr_stmt
			| compound_stmt
			| if_stmt
			| while_stmt
			| return_stmt
			| break_stmt

	expr_stmt : expr ;
			| ;

	while_stmt : WHILE ( expr ) stmt

	if_stmt : IF ( expr ) stmt
			| IF ( expr ) stmt ELSE stmt

	return_stmt : RETURN ;
			| RETURN expr ;

	break_stmt : BREAK ;

	expr : IDENT = expr | IDENT[ expr ] = expr
			| expr OR expr
			| expr AND expr
			| expr EQ expr | expr NE expr
			| expr LE expr | expr < expr | expr GE expr | expr > expr
			| expr + expr | expr - expr
			| expr * expr | expr / expr | expr % expr
			| ! expr | - expr | + expr
			| ( expr )
			| IDENT | IDENT[ expr ] | IDENT( args ) | IDENT . size
			| BOOL_LIT | INT_LIT | FLOAT_LIT | NEW type_spec [ expr ]

	arg_list : arg_list , expr
			| expr

	args : arg_list
			| empty


Para hacer el proyecto, siga las instrucciones que siguen a continuación.
"""
# ----------------------------------------------------------------------
# Analizadores son definidos usando SLY.  Se hereda de la clase Parser
#
# vea http://sly.readthedocs.io/en/latest/
# ----------------------------------------------------------------------
import sly

# ----------------------------------------------------------------------
# El siguiente import carga la función error(lineno, msg) que se debe
# usar para informar todos los mensajes de error emitidos por su analizador.
# Las pruebas unitarias y otras características del compilador se basarán
# en esta función. Consulte el archivo errors.py para obtener más
# documentación sobre el mecanismo de manejo de errores.
from errors import error

# ------------------------------------------------- ---------------------
# Importar la clase lexer. Su lista de tokens es necesaria para validar y
# construir el objeto analizador.
from clex import Lexer

# ----------------------------------------------------------------------
# Obtener los nodos AST.
# Lea las instrucciones en ast.py
from cast import *


class Parser(sly.Parser):
    debugfile = 'data/parser.txt'

    tokens = Lexer.tokens

    precedence = (
        ("nonassoc", LOWER),
        ("nonassoc", ELSE),
        ("left", ','),
        ("right", '=', ADDASSIGN, SUBASSIGN, MULASSIGN, DIVASSIGN, MODASSIGN),
        ("left", OR),
        ("left", AND),
        ("left", EQ, NE),
        ("left", LE, '<', GE, '>'),
        ("left", PLUS, MINUS),
        ("left", TIMES, DIVIDE, MOD),
        ("right", '!', UNARY, PRE),
        ("left", '.', '(', ')', '[', ']', INC, DEC)
    )

    @_("decl_list")
    def program(self, p):
        return Program(p.decl_list)

    @_("decl_list decl")
    def decl_list(self, p):
        p.decl_list.append(p.decl)
        return p.decl_list

    @_("decl")
    def decl_list(self, p):
        return [p.decl]

    @_("var_decl")
    def decl(self, p):
        return p.var_decl

    @_("fun_decl")
    def decl(self, p):
        return p.fun_decl

    @_("type_spec IDENT ';'")
    def var_decl(self, p):
        return StaticVarDeclStmt(p.type_spec, p.IDENT, None, lineno=p.lineno)

    @_("type_spec IDENT '=' expr ';'")
    def var_decl(self, p):
        return StaticVarDeclStmt(p.type_spec, p.IDENT, p.expr, lineno=p.lineno)

    @_("type_spec IDENT '[' expr ']' ';'")
    def var_decl(self, p):
        return StaticArrayDeclStmt(p.type_spec, p.IDENT, p.expr, lineno=p.lineno)

    @_("VOID", "BOOL", "INT", "FLOAT", "CHAR")
    def type_spec(self, p):
        return SimpleType(p[0], lineno=p.lineno)

    @_("type_spec IDENT '(' params ')' compound_stmt")
    def fun_decl(self, p):
        return FuncDeclStmt(p.type_spec, p.IDENT, p.params, p.compound_stmt, lineno=p.lineno)

    @_("param_list")
    def params(self, p):
        return p.param_list

    @_("VOID", "empty")
    def params(self, p):
        return []

    @_("param_list ',' param")
    def param_list(self, p):
        p.param_list.append(p.param)
        return p.param_list

    @_("param")
    def param_list(self, p):
        return [p.param]

    @_("type_spec IDENT")
    def param(self, p):
        return FuncParameter(p.type_spec, p.IDENT, lineno=p.lineno)

    @_("type_spec IDENT '[' ']'")
    def param(self, p):
        return FuncParameter(p.type_spec, p.IDENT, lineno=p.lineno)

    @_("'{' local_decls stmt_list '}'")
    def compound_stmt(self, p):
        return CompoundStmt(p.local_decls, p.stmt_list, lineno=p.lineno)

    @_("local_decls local_decl")
    def local_decls(self, p):
        p.local_decls.append(p.local_decl)
        return p.local_decls

    @_("empty")
    def local_decls(self, p):
        return []

    @_("type_spec IDENT ';'")
    def local_decl(self, p):
        return LocalVarDeclStmt(p.type_spec, p.IDENT, None, lineno=p.lineno)

    @_("type_spec IDENT '=' expr ';'")
    def local_decl(self, p):
        return LocalVarDeclStmt(p.type_spec, p.IDENT, p.expr, lineno=p.lineno)

    @_("type_spec IDENT '[' expr ']' ';'")
    def local_decl(self, p):
        return LocalArrayDeclStmt(p.type_spec, p.IDENT, p.expr, lineno=p.lineno)

    @_("stmt_list stmt")
    def stmt_list(self, p):
        p.stmt_list.append(p.stmt)
        return p.stmt_list

    @_("empty")
    def stmt_list(self, p):
        return []

    @_("expr_stmt", "compound_stmt", "if_stmt", "while_stmt",
       "for_stmt", "return_stmt", "break_stmt", "print_stmt")
    def stmt(self, p):
        return p[0]

    @_("expr ';'")
    def expr_stmt(self, p):
        return ExprStmt(p.expr, lineno=p.lineno)

    @_("';'")
    def expr_stmt(self, p):
        return NullStmt(None, lineno=p.lineno)

    @_("WHILE '(' expr ')' stmt")
    def while_stmt(self, p):
        return WhileStmt(p.expr, p.stmt, lineno=p.lineno)

    @_("FOR '(' args ';' args ';' args ')' stmt")
    def for_stmt(self, p):
        return ForStmt(p.args0, p.args1, p.args2, p.stmt, lineno=p.lineno)

    @_("IF '(' expr ')' stmt %prec LOWER")
    def if_stmt(self, p):
        return IfStmt(p.expr, p.stmt, None, lineno=p.lineno)

    @_("IF '(' expr ')' stmt ELSE stmt")
    def if_stmt(self, p):
        return IfStmt(p.expr, p.stmt0, p.stmt1, lineno=p.lineno)

    @_("RETURN ';'")
    def return_stmt(self, p):
        return ReturnStmt(None, lineno=p.lineno)

    @_("RETURN expr ';'")
    def return_stmt(self, p):
        return ReturnStmt(p.expr, lineno=p.lineno)

    @_("BREAK ';'")
    def break_stmt(self, p):
        return BreakStmt(None, lineno=p.lineno)

    @_("PRINT '(' args ')' ';'")
    def print_stmt(self, p):
        return PrintStmt(p.args, lineno=p.lineno)

    @_("IDENT '=' expr", "IDENT ADDASSIGN expr", "IDENT SUBASSIGN expr",
       "IDENT MULASSIGN expr", "IDENT DIVASSIGN expr", "IDENT MODASSIGN expr")
    def expr(self, p):
        return VarAssignmentExpr(p[1], p.IDENT, p.expr, lineno=p.lineno)

    @_("IDENT '[' expr ']' '=' expr", "IDENT '[' expr ']' ADDASSIGN expr",
       "IDENT '[' expr ']' SUBASSIGN expr", "IDENT '[' expr ']' MULASSIGN expr",
       "IDENT '[' expr ']' DIVASSIGN expr", "IDENT '[' expr ']' MODASSIGN expr")
    def expr(self, p):
        return ArrayAssignmentExpr(p[4], p.IDENT, p.expr0, p.expr1, lineno=p.lineno)

    @_("expr OR expr", "expr AND expr", "expr EQ expr", "expr NE expr",
       "expr LE expr", "expr '<' expr", "expr GE expr", "expr '>' expr",
       "expr PLUS expr", "expr MINUS expr",
       "expr TIMES expr", "expr DIVIDE expr", "expr MOD expr")
    def expr(self, p):
        return BinaryOpExpr(p[1], p.expr0, p.expr1, lineno=p.lineno)

    @_("'!' expr", "MINUS expr %prec UNARY", "PLUS expr %prec UNARY")
    def expr(self, p):
        return UnaryOpExpr(p[0], p.expr, lineno=p.lineno)

    @_("INC expr %prec PRE", "DEC expr %prec PRE")
    def expr(self, p):
        return UnaryOpExpr(p[0], p.expr, lineno=p.lineno)

    @_("expr INC", "expr DEC")
    def expr(self, p):
        return UnaryOpExpr(p[1], p.expr, lineno=p.lineno)

    @_("'(' expr ')'")
    def expr(self, p):
        return p.expr

    @_("IDENT")
    def expr(self, p):
        return VarExpr(p.IDENT, lineno=p.lineno)

    @_("IDENT '[' expr ']'")
    def expr(self, p):
        return ArrayExpr(p.IDENT, p.expr, lineno=p.lineno)

    @_("IDENT '(' args ')'")
    def expr(self, p):
        return FuncCallExpr(p.IDENT, p.args, lineno=p.lineno)

    @_("IDENT '.' SIZE")
    def expr(self, p):
        return ArraySizeExpr(p.IDENT, p.size, lineno=p.lineno)

    @_("BOOL_LIT", "TRUE", "FALSE")
    def expr(self, p):
        return BoolLiteral(p[0], lineno=p.lineno)

    @_("INT_LIT")
    def expr(self, p):
        return IntegerLiteral(p.INT_LIT, lineno=p.lineno)

    @_("FLOAT_LIT")
    def expr(self, p):
        return FloatLiteral(p.FLOAT_LIT, lineno=p.lineno)

    @_("CHAR_LIT")
    def expr(self, p):
        return CharLiteral(p.CHAR_LIT, lineno=p.lineno)

    @_("STRING_LIT")
    def expr(self, p):
        return StringLiteral(p.STRING_LIT, lineno=p.lineno)

    @_("NEW type_spec '[' expr ']'")
    def expr(self, p):
        return NewArrayExpr(p.type_spec, p.expr, lineno=p.lineno)

    @_("arg_list ',' expr")
    def arg_list(self, p):
        p.arg_list.append(p.expr)
        return p.arg_list

    @_("expr")
    def arg_list(self, p):
        return [p.expr]

    @_("arg_list")
    def args(self, p):
        return p.arg_list

    @_("empty")
    def args(self, p):
        return []

    @_("")
    def empty(self, p):
        pass

    # ----------------------------------------------------------------------
    # NO MODIFIQUE
    #
    # manejo de errores catch-all. Se llama a la siguiente función en
    # cualquier entrada incorrecta. p es el token ofensivo o None si
    # el final de archivo (EOF).

    def error(self, p):
        if p:
            error(p.lineno, "Syntax error in input at token '%s'" % p.value)
        else:
            error("EOF", "Syntax error. No more input.")


# ----------------------------------------------------------------------
#                  NO MODIFIQUE NADA A CONTINUACIÓN
# ----------------------------------------------------------------------


def parse(source):
    """
    Parser el código fuente en un AST. Devuelve la parte superior del árbol AST.
    """
    lexer = Lexer()
    parser = Parser()
    ast = parser.parse(lexer.tokenize(source))
    return ast


def main():
    """
    Programa principal. Usado para probar.
    """
    import sys

    if len(sys.argv) < 2:
        sys.stderr.write('Usage: python -m cparse filename\n')
        raise SystemExit(1)

    # Parse y crea el AST
    ast = parse(open(sys.argv[1]).read())

    # Genera el árbol de análisis sintáctico resultante
    for depth, node in flatten(ast):
        print('%s: %s%s' % (getattr(node, 'lineno', None), ' ' * (4 * depth), node))

    if '--ast' in sys.argv:
        create_ast_file(ast, sys.argv[1])


if __name__ == '__main__':
    main()
