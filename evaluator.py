from __future__ import annotations

from pathlib import Path


def _format_number(value: float) -> str:
    if value.is_integer():
        return str(int(value))
    return f"{value:.15g}"


def _format_result(value: float) -> str:
    if value.is_integer():
        return str(int(value))
    return f"{value:.4f}".rstrip("0").rstrip(".")


def _tokenize(expression: str) -> list[tuple[str, str]]:
    tokens: list[tuple[str, str]] = []
    i = 0
    n = len(expression)

    while i < n:
        ch = expression[i]

        if ch.isspace():
            i += 1
            continue

        if ch in "+-*/":
            tokens.append(("OP", ch))
            i += 1
            continue

        if ch == "(":
            tokens.append(("LPAREN", ch))
            i += 1
            continue

        if ch == ")":
            tokens.append(("RPAREN", ch))
            i += 1
            continue

        if ch.isdigit() or ch == ".":
            start = i
            dot_seen = ch == "."
            digit_seen = ch.isdigit()
            i += 1

            while i < n:
                nxt = expression[i]
                if nxt.isdigit():
                    digit_seen = True
                    i += 1
                elif nxt == "." and not dot_seen:
                    dot_seen = True
                    i += 1
                else:
                    break

            lexeme = expression[start:i]

            # CHANGE MADE:
            # Reject invalid decimal forms like ".", ".4", "3."
            # This also makes "3..4" fail instead of becoming 3 * 0.4
            if (
                not digit_seen
                or lexeme == "."
                or lexeme.startswith(".")
                or lexeme.endswith(".")
            ):
                raise ValueError("Invalid number literal")

            tokens.append(("NUM", lexeme))
            continue

        raise ValueError("Invalid character")

    tokens.append(("END", ""))
    return tokens


def _parse(tokens: list[tuple[str, str]]):
    pos = 0

    def peek() -> tuple[str, str]:
        return tokens[pos]

    def consume(expected_type: str | None = None, expected_value: str | None = None):
        nonlocal pos
        token = tokens[pos]

        if expected_type is not None and token[0] != expected_type:
            raise ValueError("Unexpected token")

        if expected_value is not None and token[1] != expected_value:
            raise ValueError("Unexpected token")

        pos += 1
        return token

    def parse_expression():
        node = parse_term()

        while True:
            tk_type, tk_val = peek()
            if tk_type == "OP" and tk_val in "+-":
                consume("OP", tk_val)
                right = parse_term()
                node = ("bin", tk_val, node, right)
            else:
                return node

    def parse_term():
        node = parse_factor()

        while True:
            tk_type, tk_val = peek()

            if tk_type == "OP" and tk_val in "*/":
                consume("OP", tk_val)
                right = parse_factor()
                node = ("bin", tk_val, node, right)

            elif tk_type in {"NUM", "LPAREN"}:
                # implicit multiplication: 2(3+4), (2)(3)
                right = parse_factor()
                node = ("bin", "*", node, right)

            else:
                return node

    def parse_factor():
        tk_type, tk_val = peek()

        if tk_type == "OP" and tk_val == "-":
            consume("OP", "-")
            return ("neg", parse_factor())

        if tk_type == "OP" and tk_val == "+":
            raise ValueError("Unary plus is not supported")

        if tk_type == "NUM":
            _, lexeme = consume("NUM")
            return ("num", float(lexeme))

        if tk_type == "LPAREN":
            consume("LPAREN", "(")
            node = parse_expression()
            consume("RPAREN", ")")
            return node

        raise ValueError("Unexpected token")

    root = parse_expression()

    if peek()[0] != "END":
        raise ValueError("Trailing tokens")

    return root


def _evaluate(node) -> float:
    kind = node[0]

    # CHANGE MADE:
    # Added full evaluation logic so the tree is actually calculated
    if kind == "num":
        return node[1]

    if kind == "neg":
        return -_evaluate(node[1])

    if kind == "bin":
        op = node[1]
        left = _evaluate(node[2])
        right = _evaluate(node[3])

        if op == "+":
            return left + right
        if op == "-":
            return left - right
        if op == "*":
            return left * right
        if op == "/":
            if right == 0:
                raise ZeroDivisionError("Division by zero")
            return left / right

    raise ValueError("Invalid parse tree")


def _tree_to_string(node) -> str:
    kind = node[0]

    # CHANGE MADE:
    # Added conversion from internal tree tuples to required output format
    if kind == "num":
        return _format_number(node[1])

    if kind == "neg":
        return f"(neg {_tree_to_string(node[1])})"

    if kind == "bin":
        op = node[1]
        left = _tree_to_string(node[2])
        right = _tree_to_string(node[3])
        return f"({op} {left} {right})"

    raise ValueError("Invalid parse tree")


def _tokens_to_string(tokens: list[tuple[str, str]]) -> str:
    # CHANGE MADE:
    # Added conversion from token tuples to required token text format
    parts: list[str] = []

    for token_type, token_value in tokens:
        if token_type == "END":
            parts.append("[END]")
        else:
            parts.append(f"[{token_type}:{token_value}]")

    return " ".join(parts)


def evaluate_file(input_path: str) -> list[dict]:
    # CHANGE MADE:
    # Added the required main function for Q2
    # - reads expressions from file
    # - processes each line
    # - writes output.txt
    # - returns list of dictionaries

    input_file = Path(input_path)
    output_file = input_file.with_name("output.txt")

    results: list[dict] = []
    blocks: list[str] = []

    with input_file.open("r", encoding="utf-8") as fh:
        for raw_line in fh:
            expression = raw_line.rstrip("\n")

            if expression.strip() == "":
                continue

            try:
                tokens = _tokenize(expression)
                tree = _parse(tokens)
                value = _evaluate(tree)

                tree_str = _tree_to_string(tree)
                tokens_str = _tokens_to_string(tokens)
                result_value: float | str = value
                result_str = _format_result(value)

            # CHANGE MADE:
            # Clean per-line error handling so bad lines become ERROR
            except (ValueError, ZeroDivisionError):
                tree_str = "ERROR"
                tokens_str = "ERROR"
                result_value = "ERROR"
                result_str = "ERROR"

            results.append(
                {
                    "input": expression,
                    "tree": tree_str,
                    "tokens": tokens_str,
                    "result": result_value,
                }
            )

            block = "\n".join(
                [
                    f"Input: {expression}",
                    f"Tree: {tree_str}",
                    f"Tokens: {tokens_str}",
                    f"Result: {result_str}",
                ]
            )
            blocks.append(block)

    with output_file.open("w", encoding="utf-8") as fh:
        fh.write("\n\n".join(blocks))

    return results