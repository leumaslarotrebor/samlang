"""
SamLang — Tree-Walking Interpreter
=====================================
The interpreter walks the AST produced by the Parser and
executes each node directly — no bytecode, no compilation.

Execution model:
    - Environment: a stack of scopes (dicts) for variable storage
    - Each function call pushes a new scope onto the stack
    - Variable lookup walks up the scope stack (lexical scoping)
    - Functions are first-class values stored in the environment

Supported features:
    - Variables (let, assign)
    - Arithmetic (+, -, *, /, %)
    - Comparisons (==, !=, <, >, <=, >=)
    - Print (numbers and strings)
    - If / else
    - While loops
    - User-defined functions with parameters
    - Return statements
    - Recursion
"""

from ast_nodes import (
    Number, String, Identifier, BinaryOp, UnaryOp,
    LetStatement, AssignStatement, PrintStatement,
    IfStatement, WhileStatement, FunctionDef, FunctionCall,
    ReturnStatement, Block, Program
)


# ── Runtime exceptions ───────────────────────────────────────────────────────

class RuntimeError_(Exception):
    """SamLang runtime error (renamed to avoid shadowing Python's RuntimeError)."""
    pass


class ReturnValue(Exception):
    """
    Used to unwind the call stack when a return statement is hit.
    Caught by the function call handler.
    """
    def __init__(self, value):
        self.value = value


# ── Environment (scope chain) ─────────────────────────────────────────────────

class Environment:
    """
    A linked scope chain for variable storage.

    Each function call creates a new Environment with the
    caller's environment as its parent. Variable lookup
    walks up the chain — inner scopes shadow outer ones.
    """

    def __init__(self, parent=None):
        self.vars = {}
        self.parent = parent

    def get(self, name):
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name)
        raise RuntimeError_(f"Undefined variable: '{name}'")

    def set(self, name, value):
        """Create or update a variable in the current scope."""
        self.vars[name] = value

    def assign(self, name, value):
        """
        Update an existing variable — walks up scope chain.
        Raises error if variable was never declared.
        """
        if name in self.vars:
            self.vars[name] = value
            return
        if self.parent:
            self.parent.assign(name, value)
            return
        raise RuntimeError_(f"Assignment to undeclared variable: '{name}'")

    def __repr__(self):
        return f"Env({list(self.vars.keys())})"


# ── SamLang Function (callable) ───────────────────────────────────────────────

class SamFunction:
    """
    Represents a user-defined SamLang function.
    Stores the parameter list, body block, and the closure
    environment at the time of definition.
    """

    def __init__(self, name, params, body, closure):
        self.name = name
        self.params = params
        self.body = body
        self.closure = closure  # environment where function was defined

    def __repr__(self):
        return f"<function {self.name}({', '.join(self.params)})>"


# ── Interpreter ───────────────────────────────────────────────────────────────

class Interpreter:
    """
    Tree-walking interpreter for SamLang.

    Usage:
        from lexer import Lexer
        from parser import Parser
        from interpreter import Interpreter

        source = open("program.sam").read()
        tokens = Lexer(source).tokenize()
        ast    = Parser(tokens).parse()
        Interpreter().run(ast)
    """

    def __init__(self):
        self.global_env = Environment()

    def run(self, program):
        """Execute a Program node."""
        for stmt in program.statements:
            self.execute(stmt, self.global_env)

    # ── Statement execution ───────────────────────────────────────────────────

    def execute(self, node, env):
        """Dispatch execution to the correct handler."""

        if isinstance(node, LetStatement):
            value = self.evaluate(node.value, env)
            env.set(node.name, value)

        elif isinstance(node, AssignStatement):
            value = self.evaluate(node.value, env)
            env.assign(node.name, value)

        elif isinstance(node, PrintStatement):
            value = self.evaluate(node.value, env)
            if isinstance(value, str):
                # Handle escape sequences
                print(value.replace("\\n", "\n").replace("\\t", "\t"), end="")
            else:
                print(value)

        elif isinstance(node, IfStatement):
            condition = self.evaluate(node.condition, env)
            if self.is_truthy(condition):
                self.execute_block(node.then_block, Environment(env))
            elif node.else_block:
                self.execute_block(node.else_block, Environment(env))

        elif isinstance(node, WhileStatement):
            while self.is_truthy(self.evaluate(node.condition, env)):
                try:
                    self.execute_block(node.body, Environment(env))
                except ReturnValue:
                    break

        elif isinstance(node, FunctionDef):
            func = SamFunction(node.name, node.params, node.body, env)
            env.set(node.name, func)

        elif isinstance(node, ReturnStatement):
            value = self.evaluate(node.value, env)
            raise ReturnValue(value)

        elif isinstance(node, FunctionCall):
            self.call_function(node, env)

        elif isinstance(node, Block):
            self.execute_block(node, env)

        else:
            # Expression used as statement — evaluate and discard result
            self.evaluate(node, env)

    def execute_block(self, block, env):
        """Execute all statements in a Block node."""
        for stmt in block.statements:
            self.execute(stmt, env)

    # ── Expression evaluation ─────────────────────────────────────────────────

    def evaluate(self, node, env):
        """Evaluate an expression node and return its value."""

        if isinstance(node, Number):
            return node.value

        if isinstance(node, String):
            return node.value

        if isinstance(node, Identifier):
            return env.get(node.name)

        if isinstance(node, UnaryOp):
            operand = self.evaluate(node.operand, env)
            if node.op == "-":
                return -operand
            raise RuntimeError_(f"Unknown unary operator: {node.op}")

        if isinstance(node, BinaryOp):
            return self.evaluate_binary(node, env)

        if isinstance(node, FunctionCall):
            return self.call_function(node, env)

        raise RuntimeError_(f"Cannot evaluate node: {type(node).__name__}")

    def evaluate_binary(self, node, env):
        """Evaluate a binary operation."""
        left  = self.evaluate(node.left,  env)
        right = self.evaluate(node.right, env)
        op    = node.op

        if op == "+":
            # Support string concatenation
            if isinstance(left, str) or isinstance(right, str):
                return str(left) + str(right)
            return left + right
        if op == "-":  return left - right
        if op == "*":  return left * right
        if op == "%":  return left % right
        if op == "/":
            if right == 0:
                raise RuntimeError_("Division by zero")
            return left // right  # integer division

        # Comparisons return 1 (true) or 0 (false)
        if op == "==": return 1 if left == right else 0
        if op == "!=": return 1 if left != right else 0
        if op == "<":  return 1 if left <  right else 0
        if op == ">":  return 1 if left >  right else 0
        if op == "<=": return 1 if left <= right else 0
        if op == ">=": return 1 if left >= right else 0

        raise RuntimeError_(f"Unknown operator: {op}")

    def call_function(self, node, env):
        """
        Execute a function call:
        1. Look up the function in the environment
        2. Create a new scope with the closure as parent
        3. Bind arguments to parameters
        4. Execute the function body
        5. Catch ReturnValue and return its value
        """
        func = env.get(node.name)

        if not isinstance(func, SamFunction):
            raise RuntimeError_(f"'{node.name}' is not a function")

        if len(node.args) != len(func.params):
            raise RuntimeError_(
                f"'{node.name}' expects {len(func.params)} argument(s), "
                f"got {len(node.args)}"
            )

        # Evaluate arguments in the CALLER's environment
        arg_values = [self.evaluate(arg, env) for arg in node.args]

        # Create a new scope rooted in the function's closure
        call_env = Environment(parent=func.closure)

        # Bind parameters to argument values
        for param, value in zip(func.params, arg_values):
            call_env.set(param, value)

        # Execute and catch return
        try:
            self.execute_block(func.body, call_env)
            return 0  # implicit return 0 if no return statement
        except ReturnValue as r:
            return r.value

    def is_truthy(self, value):
        """0 and empty string are falsy; everything else is truthy."""
        if isinstance(value, int):
            return value != 0
        if isinstance(value, str):
            return value != ""
        return True


# ── Quick test ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from lexer import Lexer
    from parser import Parser

    sample = """
let x = 10
let y = 3
let result = x + y
print "Sum: "
print result
print "\n"

if result > 10 {
    print "Greater than 10\n"
} else {
    print "10 or less\n"
}

fun factorial(n) {
    if n <= 1 {
        return 1
    }
    return n * factorial(n - 1)
}

print "Factorial of 5: "
print factorial(5)
print "\n"

let i = 1
while i <= 5 {
    print i
    print "\n"
    i = i + 1
}
"""
    tokens = Lexer(sample).tokenize()
    ast    = Parser(tokens).parse()
    Interpreter().run(ast)
