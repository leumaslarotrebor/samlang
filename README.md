# SamLang

A custom programming language built from scratch in Python — with a handwritten lexer, recursive-descent parser, AST, and tree-walking interpreter.

```bash
python3 samlang.py program.sam
```

---

## Why I Built This

I wanted to understand how programming languages actually work internally — not just use them. The only way that felt satisfying was to implement one. SamLang started as a question: *what happens between source code and execution?* This is the answer.

---

## Pipeline
Source (.sam file)

│

▼

┌────────┐

│ Lexer  │  Tokenizes source into a flat list of typed tokens

└────────┘  lexer.py

│

▼

┌────────┐

│ Parser │  Recursive-descent parser builds an Abstract Syntax Tree

└────────┘  parser.py

│

▼

┌─────┐

│ AST │  Tree of typed nodes — Program, IfStatement, BinaryOp, etc.

└─────┘  ast_nodes.py

│

▼

┌─────────────┐

│ Interpreter │  Tree-walker executes AST nodes directly

└─────────────┘  interpreter.py

│

▼

Output

---

## Language Features

```samlang
# Variables
let x = 10
let name = "SamLang"

# Arithmetic
let result = x * 2 + 5

# Conditionals
if result > 20 {
    print "big\n"
} else {
    print "small\n"
}

# While loops
let i = 1
while i <= 5 {
    print i
    print "\n"
    i = i + 1
}

# Functions and recursion
fun factorial(n) {
    if n <= 1 {
        return 1
    }
    return n * factorial(n - 1)
}

print factorial(6)
```

**Output:**
big

1

2

3

4

5

720

---

## File Structure
samlang/

├── lexer.py         # Tokenizer — reads source char by char, emits Token list

├── parser.py        # Recursive-descent parser — builds AST from token list

├── ast_nodes.py     # AST node classes — Number, BinaryOp, IfStatement, etc.

├── interpreter.py   # Tree-walking interpreter — executes AST nodes directly

├── samlang.py       # Entry point — wires pipeline, handles CLI flags

├── test.sam         # Feature demo program

└── compiler.py      # Original string-based transpiler (kept for reference)

---

## Usage

```bash
# Run a program
python3 samlang.py test.sam

# Debug: print token list
python3 samlang.py test.sam --tokens

# Debug: print AST
python3 samlang.py test.sam --ast
```

---

## Supported Syntax

| Feature | Syntax |
|---|---|
| Variable declaration | `let x = 5` |
| Assignment | `x = x + 1` |
| Arithmetic | `+ - * / %` |
| Comparison | `== != < > <= >=` |
| Print | `print x` / `print "hello\n"` |
| If / else | `if condition { } else { }` |
| While loop | `while condition { }` |
| Function definition | `fun name(a, b) { return a + b }` |
| Function call | `name(1, 2)` |
| Recursion | Supported via lexical scope chain |
| Comments | `# this is a comment` |
| String concat | `"hello" + " world"` |
| Booleans | `true` (1) / `false` (0) |

---

## Implementation Notes

**Lexer:** Reads source character by character. Handles two-char operators (`==`, `<=`) before single-char ones. Newlines are explicit tokens — SamLang uses newline-delimited statements.

**Parser:** Recursive descent with operator precedence: comparison → addition → multiplication → unary → primary. No parser generator used.

**AST:** Each language construct maps to a typed Python class (`IfStatement`, `BinaryOp`, `FunctionDef`, etc.) in `ast_nodes.py`.

**Interpreter:** Tree-walker using an `Environment` scope chain. Each function call pushes a new scope rooted in the closure environment — enabling lexical scoping and recursion. `ReturnValue` is raised as a Python exception to unwind the call stack.

---

## Author

Samuel Oral Robert V
GitHub: https://github.com/leumaslarotrebor
Portfolio: https://leumaslarotrebor.github.io
LinkedIn: https://linkedin.com/in/samuel-oral-robert-v-4226813a4/
