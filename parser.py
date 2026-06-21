"""
SamLang — Recursive Descent Parser
=====================================
The parser consumes the token list from the Lexer and builds
an Abstract Syntax Tree (AST) using recursive descent parsing.

Grammar (informal):
    program     → statement* EOF
    statement   → let_stmt | assign_stmt | print_stmt
                | if_stmt | while_stmt | fun_def | return_stmt
                | expr_stmt
    let_stmt    → "let" IDENT "=" expression
    assign_stmt → IDENT "=" expression
    print_stmt  → "print" expression
    if_stmt     → "if" expression block ("else" block)?
    while_stmt  → "while" expression block
    fun_def     → "fun" IDENT "(" params ")" block
    return_stmt → "return" expression
    block       → "{" statement* "}"
    expression  → comparison
    comparison  → addition (("==" | "!=" | "<" | ">" | "<=" | ">=") addition)*
    addition    → multiplication (("+" | "-") multiplication)*
    multiplication → unary (("*" | "/" | "%") unary)*
    unary       → "-" unary | primary
    primary     → NUMBER | STRING | "true" | "false"
                | IDENT "(" args ")" | IDENT | "(" expression ")"
"""

from lexer import (
    Token, NUMBER, STRING, IDENT, OP, ASSIGN,
    LPAREN, RPAREN, LBRACE, RBRACE, COMMA, NEWLINE, EOF
)
from ast_nodes import (
    Number, String, Identifier, BinaryOp, UnaryOp,
    LetStatement, AssignStatement, PrintStatement,
    IfStatement, WhileStatement, FunctionDef, FunctionCall,
    ReturnStatement, Block, Program
)


# ── Parser Error ─────────────────────────────────────────────────────────────

class ParseError(Exception):
    pass


# ── Parser ───────────────────────────────────────────────────────────────────

class Parser:
    """
    Recursive descent parser for SamLang.

    Usage:
        from lexer import Lexer
        from parser import Parser

        tokens = Lexer(source).tokenize()
        ast = Parser(tokens).parse()
    """

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    # ── Token navigation ─────────────────────────────────────────────────────

    def current(self):
        return self.tokens[self.pos]

    def peek(self, offset=1):
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return self.tokens[-1]  # EOF

    def advance(self):
        tok = self.tokens[self.pos]
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return tok

    def skip_newlines(self):
        while self.current().type == NEWLINE:
            self.advance()

    def expect(self, type_, value=None):
        """Consume a token of the expected type (and optionally value)."""
        tok = self.current()
        if tok.type != type_:
            raise ParseError(
                f"Line {tok.line}: expected {type_!r} but got "
                f"{tok.type!r} ({tok.value!r})"
            )
        if value is not None and tok.value != value:
            raise ParseError(
                f"Line {tok.line}: expected {value!r} but got {tok.value!r}"
            )
        return self.advance()

    def match(self, type_, value=None):
        """Return True and advance if current token matches."""
        tok = self.current()
        if tok.type == type_:
            if value is None or tok.value == value:
                self.advance()
                return True
        return False

    # ── Entry point ──────────────────────────────────────────────────────────

    def parse(self):
        """Parse the full program and return a Program AST node."""
        statements = []
        self.skip_newlines()
        while self.current().type != EOF:
            stmt = self.parse_statement()
            if stmt is not None:
                statements.append(stmt)
            self.skip_newlines()
        return Program(statements)

    # ── Statements ───────────────────────────────────────────────────────────

    def parse_statement(self):
        tok = self.current()

        if tok.type == NEWLINE:
            self.advance()
            return None

        if tok.type == IDENT:
            if tok.value == "let":
                return self.parse_let()
            if tok.value == "print":
                return self.parse_print()
            if tok.value == "if":
                return self.parse_if()
            if tok.value == "while":
                return self.parse_while()
            if tok.value == "fun":
                return self.parse_function_def()
            if tok.value == "return":
                return self.parse_return()
            # Could be assignment or expression
            if (self.peek().type == ASSIGN):
                return self.parse_assign()

        return self.parse_expr_statement()

    def parse_let(self):
        """let x = expression"""
        self.advance()  # consume 'let'
        name_tok = self.expect(IDENT)
        self.expect(ASSIGN)
        value = self.parse_expression()
        return LetStatement(name_tok.value, value)

    def parse_assign(self):
        """x = expression"""
        name_tok = self.advance()  # consume identifier
        self.expect(ASSIGN)
        value = self.parse_expression()
        return AssignStatement(name_tok.value, value)

    def parse_print(self):
        """print expression"""
        self.advance()  # consume 'print'
        value = self.parse_expression()
        return PrintStatement(value)

    def parse_if(self):
        """if condition { block } else { block }"""
        self.advance()  # consume 'if'
        condition = self.parse_expression()
        then_block = self.parse_block()
        else_block = None
        self.skip_newlines()
        if self.current().type == IDENT and self.current().value == "else":
            self.advance()  # consume 'else'
            else_block = self.parse_block()
        return IfStatement(condition, then_block, else_block)

    def parse_while(self):
        """while condition { block }"""
        self.advance()  # consume 'while'
        condition = self.parse_expression()
        body = self.parse_block()
        return WhileStatement(condition, body)

    def parse_function_def(self):
        """fun name(params) { block }"""
        self.advance()  # consume 'fun'
        name_tok = self.expect(IDENT)
        self.expect(LPAREN)
        params = []
        if self.current().type != RPAREN:
            params.append(self.expect(IDENT).value)
            while self.current().type == COMMA:
                self.advance()
                params.append(self.expect(IDENT).value)
        self.expect(RPAREN)
        body = self.parse_block()
        return FunctionDef(name_tok.value, params, body)

    def parse_return(self):
        """return expression"""
        self.advance()  # consume 'return'
        value = self.parse_expression()
        return ReturnStatement(value)

    def parse_expr_statement(self):
        """An expression used as a statement (e.g. a function call)."""
        return self.parse_expression()

    def parse_block(self):
        """{ statement* }"""
        self.skip_newlines()
        self.expect(LBRACE)
        self.skip_newlines()
        statements = []
        while self.current().type not in (RBRACE, EOF):
            stmt = self.parse_statement()
            if stmt is not None:
                statements.append(stmt)
            self.skip_newlines()
        self.expect(RBRACE)
        return Block(statements)

    # ── Expressions (precedence climbing) ────────────────────────────────────

    def parse_expression(self):
        return self.parse_comparison()

    def parse_comparison(self):
        """comparison → addition (CMP_OP addition)*"""
        left = self.parse_addition()
        while (self.current().type == OP and
               self.current().value in ("==", "!=", "<", ">", "<=", ">=")):
            op = self.advance().value
            right = self.parse_addition()
            left = BinaryOp(left, op, right)
        return left

    def parse_addition(self):
        """addition → multiplication (('+' | '-') multiplication)*"""
        left = self.parse_multiplication()
        while (self.current().type == OP and
               self.current().value in ("+", "-")):
            op = self.advance().value
            right = self.parse_multiplication()
            left = BinaryOp(left, op, right)
        return left

    def parse_multiplication(self):
        """multiplication → unary (('*' | '/' | '%') unary)*"""
        left = self.parse_unary()
        while (self.current().type == OP and
               self.current().value in ("*", "/", "%")):
            op = self.advance().value
            right = self.parse_unary()
            left = BinaryOp(left, op, right)
        return left

    def parse_unary(self):
        """unary → '-' unary | primary"""
        if self.current().type == OP and self.current().value == "-":
            op = self.advance().value
            operand = self.parse_unary()
            return UnaryOp(op, operand)
        return self.parse_primary()

    def parse_primary(self):
        """primary → NUMBER | STRING | IDENT | IDENT(...) | (expr) | true | false"""
        tok = self.current()

        if tok.type == NUMBER:
            self.advance()
            return Number(tok.value)

        if tok.type == STRING:
            self.advance()
            return String(tok.value)

        if tok.type == IDENT and tok.value == "true":
            self.advance()
            return Number(1)

        if tok.type == IDENT and tok.value == "false":
            self.advance()
            return Number(0)

        if tok.type == IDENT:
            # Could be function call or plain identifier
            if self.peek().type == LPAREN:
                return self.parse_function_call()
            self.advance()
            return Identifier(tok.value)

        if tok.type == LPAREN:
            self.advance()  # consume '('
            expr = self.parse_expression()
            self.expect(RPAREN)
            return expr

        raise ParseError(
            f"Line {tok.line}: unexpected token {tok.type!r} ({tok.value!r})"
        )

    def parse_function_call(self):
        """IDENT '(' args ')'"""
        name_tok = self.advance()  # consume function name
        self.expect(LPAREN)
        args = []
        if self.current().type != RPAREN:
            args.append(self.parse_expression())
            while self.current().type == COMMA:
                self.advance()
                args.append(self.parse_expression())
        self.expect(RPAREN)
        return FunctionCall(name_tok.value, args)


# ── Quick test ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from lexer import Lexer

    sample = """
let x = 10
let y = x + 5
if x > 3 {
    print "x is big"
} else {
    print "x is small"
}
while x > 0 {
    x = x - 1
}
fun add(a, b) {
    return a + b
}
"""
    tokens = Lexer(sample).tokenize()
    ast = Parser(tokens).parse()
    for node in ast.statements:
        print(node)
