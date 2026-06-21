"""
SamLang — AST Node Definitions
================================
Every construct in SamLang is represented as an AST node.
The interpreter walks this tree to execute the program.
"""


class Number:
    """A numeric literal. Example: 42"""
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Number({self.value})"


class String:
    """A string literal. Example: "hello" """
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"String({self.value!r})"


class Identifier:
    """A variable name. Example: x"""
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"Identifier({self.name})"


class BinaryOp:
    """A binary operation. Example: x + 5"""
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def __repr__(self):
        return f"BinaryOp({self.left} {self.op} {self.right})"


class UnaryOp:
    """A unary operation. Example: -x"""
    def __init__(self, op, operand):
        self.op = op
        self.operand = operand

    def __repr__(self):
        return f"UnaryOp({self.op}{self.operand})"


class LetStatement:
    """Variable declaration. Example: let x = 5"""
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return f"Let({self.name} = {self.value})"


class AssignStatement:
    """Variable reassignment. Example: x = 10"""
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return f"Assign({self.name} = {self.value})"


class PrintStatement:
    """Print statement. Example: print x"""
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Print({self.value})"


class IfStatement:
    """If/else statement.
    Example:
        if x > 5 {
            print "big"
        } else {
            print "small"
        }
    """
    def __init__(self, condition, then_block, else_block=None):
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block

    def __repr__(self):
        return f"If({self.condition})"


class WhileStatement:
    """While loop.
    Example:
        while x > 0 {
            print x
            x = x - 1
        }
    """
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def __repr__(self):
        return f"While({self.condition})"


class FunctionDef:
    """Function definition.
    Example:
        fun greet(name) {
            print name
        }
    """
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body

    def __repr__(self):
        return f"FunctionDef({self.name}({', '.join(self.params)}))"


class FunctionCall:
    """Function call. Example: greet("world")"""
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def __repr__(self):
        return f"FunctionCall({self.name}({self.args}))"


class ReturnStatement:
    """Return statement. Example: return x + 1"""
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Return({self.value})"


class Block:
    """A sequence of statements."""
    def __init__(self, statements):
        self.statements = statements

    def __repr__(self):
        return f"Block({len(self.statements)} statements)"


class Program:
    """The root node — the entire program."""
    def __init__(self, statements):
        self.statements = statements

    def __repr__(self):
        return f"Program({len(self.statements)} statements)"
