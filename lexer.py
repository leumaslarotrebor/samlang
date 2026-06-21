"""
SamLang — Lexer (Tokenizer)
============================
The lexer reads raw source code character by character
and produces a flat list of tokens for the parser.

Token types:
    NUMBER      — integer literals: 42, 0, 100
    STRING      — string literals: "hello"
    IDENT       — identifiers and keywords: x, let, if, while, fun
    OP          — operators: + - * / % == != < > <= >=
    ASSIGN      — assignment: =
    LPAREN      — (
    RPAREN      — )
    LBRACE      — {
    RBRACE      — }
    COMMA       — ,
    NEWLINE     — end of statement
    EOF         — end of file
"""


# ── Token ────────────────────────────────────────────────────────────────────

class Token:
    def __init__(self, type_, value, line=0):
        self.type = type_
        self.value = value
        self.line = line

    def __repr__(self):
        return f"Token({self.type}, {self.value!r}, line={self.line})"


# ── Token type constants ──────────────────────────────────────────────────────

NUMBER  = "NUMBER"
STRING  = "STRING"
IDENT   = "IDENT"
OP      = "OP"
ASSIGN  = "ASSIGN"
LPAREN  = "LPAREN"
RPAREN  = "RPAREN"
LBRACE  = "LBRACE"
RBRACE  = "RBRACE"
COMMA   = "COMMA"
NEWLINE = "NEWLINE"
EOF     = "EOF"

# Keywords — these are IDENT tokens whose value is a reserved word
KEYWORDS = {"let", "if", "else", "while", "fun", "return", "print", "true", "false"}

# Two-character operators must be checked before single-character ones
TWO_CHAR_OPS = {"==", "!=", "<=", ">="}
ONE_CHAR_OPS = {"+", "-", "*", "/", "%", "<", ">"}


# ── Lexer ────────────────────────────────────────────────────────────────────

class LexerError(Exception):
    pass


class Lexer:
    """
    Converts source code string into a list of Token objects.

    Usage:
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
    """

    def __init__(self, source):
        self.source = source
        self.pos = 0
        self.line = 1
        self.tokens = []

    def current(self):
        """Return current character or empty string at EOF."""
        if self.pos < len(self.source):
            return self.source[self.pos]
        return ""

    def peek(self):
        """Return next character without advancing."""
        if self.pos + 1 < len(self.source):
            return self.source[self.pos + 1]
        return ""

    def advance(self):
        """Consume and return current character."""
        ch = self.source[self.pos]
        self.pos += 1
        if ch == "\n":
            self.line += 1
        return ch

    def skip_whitespace(self):
        """Skip spaces and tabs (but NOT newlines — they are tokens)."""
        while self.current() in (" ", "\t"):
            self.advance()

    def skip_comment(self):
        """Skip from # to end of line."""
        while self.current() and self.current() != "\n":
            self.advance()

    def read_number(self):
        """Read a sequence of digits and return a NUMBER token."""
        start = self.pos
        while self.current().isdigit():
            self.advance()
        value = int(self.source[start:self.pos])
        return Token(NUMBER, value, self.line)

    def read_string(self):
        """Read a quoted string and return a STRING token."""
        self.advance()  # consume opening "
        start = self.pos
        while self.current() and self.current() != '"':
            if self.current() == "\\":
                self.advance()  # skip escape character
            self.advance()
        if not self.current():
            raise LexerError(f"Unterminated string at line {self.line}")
        value = self.source[start:self.pos]
        self.advance()  # consume closing "
        return Token(STRING, value, self.line)

    def read_ident_or_keyword(self):
        """Read an identifier or keyword and return an IDENT token."""
        start = self.pos
        while self.current().isalnum() or self.current() == "_":
            self.advance()
        value = self.source[start:self.pos]
        return Token(IDENT, value, self.line)

    def tokenize(self):
        """
        Main tokenization loop.
        Returns a list of Token objects ending with EOF.
        """
        while self.pos < len(self.source):
            ch = self.current()

            # Skip whitespace (not newlines)
            if ch in (" ", "\t"):
                self.skip_whitespace()
                continue

            # Comments
            if ch == "#":
                self.skip_comment()
                continue

            # Newlines become NEWLINE tokens
            if ch == "\n":
                self.tokens.append(Token(NEWLINE, "\\n", self.line))
                self.advance()
                continue

            # Numbers
            if ch.isdigit():
                self.tokens.append(self.read_number())
                continue

            # Strings
            if ch == '"':
                self.tokens.append(self.read_string())
                continue

            # Identifiers and keywords
            if ch.isalpha() or ch == "_":
                self.tokens.append(self.read_ident_or_keyword())
                continue

            # Two-character operators (must check before single-char)
            two = ch + self.peek()
            if two in TWO_CHAR_OPS:
                self.tokens.append(Token(OP, two, self.line))
                self.advance()
                self.advance()
                continue

            # Single-character operators
            if ch in ONE_CHAR_OPS:
                self.tokens.append(Token(OP, ch, self.line))
                self.advance()
                continue

            # Assignment
            if ch == "=":
                self.tokens.append(Token(ASSIGN, "=", self.line))
                self.advance()
                continue

            # Structural characters
            if ch == "(":
                self.tokens.append(Token(LPAREN, "(", self.line))
                self.advance()
                continue
            if ch == ")":
                self.tokens.append(Token(RPAREN, ")", self.line))
                self.advance()
                continue
            if ch == "{":
                self.tokens.append(Token(LBRACE, "{", self.line))
                self.advance()
                continue
            if ch == "}":
                self.tokens.append(Token(RBRACE, "}", self.line))
                self.advance()
                continue
            if ch == ",":
                self.tokens.append(Token(COMMA, ",", self.line))
                self.advance()
                continue

            raise LexerError(
                f"Unexpected character {ch!r} at line {self.line}"
            )

        self.tokens.append(Token(EOF, None, self.line))
        return self.tokens


# ── Quick test ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    sample = """
let x = 10
let y = x + 5
if x > 3 {
    print "x is big"
}
"""
    lexer = Lexer(sample)
    for tok in lexer.tokenize():
        print(tok)
