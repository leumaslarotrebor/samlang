"""
SamLang — Main Entry Point
===========================
Usage:
    python samlang.py program.sam          # run a .sam file
    python samlang.py program.sam --ast    # print AST then run
    python samlang.py program.sam --tokens # print tokens then run

Pipeline:
    Source (.sam) → Lexer → Token list → Parser → AST → Interpreter → Output
"""

import sys
from lexer import Lexer, LexerError
from parser import Parser, ParseError
from interpreter import Interpreter, RuntimeError_


def print_tokens(tokens):
    print("\n── TOKENS ──────────────────────────────")
    for tok in tokens:
        print(f"  {tok}")
    print()


def print_ast(ast):
    print("\n── AST ─────────────────────────────────")
    for node in ast.statements:
        print(f"  {node}")
    print()


def run_file(path, show_tokens=False, show_ast=False):
    try:
        with open(path, "r") as f:
            source = f.read()
    except FileNotFoundError:
        print(f"Error: file not found: {path}")
        sys.exit(1)

    # ── Stage 1: Lex ────────────────────────────────────────────────────────
    try:
        lexer = Lexer(source)
        tokens = lexer.tokenize()
    except LexerError as e:
        print(f"Lexer error: {e}")
        sys.exit(1)

    if show_tokens:
        print_tokens(tokens)

    # ── Stage 2: Parse ──────────────────────────────────────────────────────
    try:
        parser = Parser(tokens)
        ast = parser.parse()
    except ParseError as e:
        print(f"Parse error: {e}")
        sys.exit(1)

    if show_ast:
        print_ast(ast)

    # ── Stage 3: Interpret ──────────────────────────────────────────────────
    try:
        interpreter = Interpreter()
        interpreter.run(ast)
    except RuntimeError_ as e:
        print(f"Runtime error: {e}")
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print("SamLang Interpreter")
        print("Usage: python samlang.py <file.sam> [--tokens] [--ast]")
        print()
        print("Flags:")
        print("  --tokens    Print token list before running")
        print("  --ast       Print AST before running")
        sys.exit(0)

    path        = sys.argv[1]
    show_tokens = "--tokens" in sys.argv
    show_ast    = "--ast"    in sys.argv

    run_file(path, show_tokens=show_tokens, show_ast=show_ast)


if __name__ == "__main__":
    main()
