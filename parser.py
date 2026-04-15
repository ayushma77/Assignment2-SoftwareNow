import re

# =========================
# TOKENIZER
# =========================

def tokenize(expr):
    """
    Convert input string into tokens.
    WHY: Parsing raw text is hard — tokens simplify structure.
    """

    # Regex extracts numbers and operators
    tokens = re.findall(r'\d+|[()+\-*/]', expr)

    # WHY: If nothing valid found → invalid expression
    if not tokens:
        return "ERROR"

    result = []

    for t in tokens:
        if t.isdigit():
            result.append(("NUM", int(t)))  # WHY: store actual number value

        elif t in "+-*/":
            result.append(("OP", t))  # WHY: classify operator type

        elif t == "(":
            result.append(("LPAREN", t))  # WHY: needed for grouping

        elif t == ")":
            result.append(("RPAREN", t))

        else:
            return "ERROR"

    result.append(("END", None))  # WHY: signals end of input
    return result


# =========================
# PARSER (Build Tree)
# =========================

class Parser:
    """
    Converts tokens → parse tree.
    WHY: Tree represents order of operations correctly.
    """

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        return self.tokens[self.pos]

    def eat(self):
        self.pos += 1

    def factor(self):
        """
        Handles numbers, parentheses, and unary minus.
        """

        token = self.current()

        if token[0] == "OP" and token[1] == "-":
            self.eat()
            return ("neg", self.factor())

        elif token[0] == "NUM":
            self.eat()
            return token[1]

        elif token[0] == "LPAREN":
            self.eat()
            node = self.expr()

            if self.current()[0] == "RPAREN":
                self.eat()
                return node

            return "ERROR"

        return "ERROR"

    def term(self):
        node = self.factor()

        while self.current()[0] == "OP" and self.current()[1] in ("*", "/"):
            op = self.current()[1]
            self.eat()
            node = (op, node, self.factor())

        return node

    def expr(self):
        node = self.term()

        while self.current()[0] == "OP" and self.current()[1] in ("+", "-"):
            op = self.current()[1]
            self.eat()
            node = (op, node, self.term())

        return node


# =========================
# EVALUATOR
# =========================

def evaluate(node):
    """
    Evaluate parse tree.
    """

    if isinstance(node, int):
        return node

    if node == "ERROR":
        return "ERROR"

    if node[0] == "neg":
        return -evaluate(node[1])

    left = evaluate(node[1])
    right = evaluate(node[2])

    if left == "ERROR" or right == "ERROR":
        return "ERROR"

    if node[0] == "+":
        return left + right
    elif node[0] == "-":
        return left - right
    elif node[0] == "*":
        return left * right
    elif node[0] == "/":
        if right == 0:
            return "ERROR"
        return left / right


def print_tree(node):
    """
    Convert tree → readable format.
    """

    if isinstance(node, int):
        return str(node)

    if node == "ERROR":
        return "ERROR"

    if node[0] == "neg":
        return f"(neg {print_tree(node[1])})"

    return f"({node[0]} {print_tree(node[1])} {print_tree(node[2])})"