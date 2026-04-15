from __future__ import annotations

from pathlib import Path


def _format_number(value: float) -> str:
    if value.is_integer():
        return str(int(value))
    text = f"{value:.15g}"
    return text


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
            if not digit_seen or lexeme == ".":
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


def _tree_to_string(node) -> str:
    kind = node[0]
    if kind == "num":
        return _format_number(node[1])
    if kind == "neg":
        return f"(neg {_tree_to_string(node[1])})"
    _, op, left, right = node
    return f"({op} {_tree_to_string(left)} {_tree_to_string(right)})"


def _evaluate(node) -> float:
    kind = node[0]
    if kind == "num":
        return node[1]
    if kind == "neg":
        return -_evaluate(node[1])
    _, op, left, right = node
    lv = _evaluate(left)
    rv = _evaluate(right)
    if op == "+":
        return lv + rv
    if op == "-":
        return lv - rv
    if op == "*":
        return lv * rv
    if op == "/":
        return lv / rv
    raise ValueError("Unknown operator")


def _tokens_to_string(tokens: list[tuple[str, str]]) -> str:
    out: list[str] = []
    for token_type, token_value in tokens:
        if token_type == "END":
            out.append("[END]")
        else:
            out.append(f"[{token_type}:{token_value}]")
    return " ".join(out)


def evaluate_file(input_path: str) -> list[dict]:
    input_file = Path(input_path)
    output_file = input_file.parent / "output.txt"
    results: list[dict] = []
    output_blocks: list[str] = []

    with input_file.open("r", encoding="utf-8") as fh:
        lines = [line.rstrip("\n") for line in fh]

    for expression in lines:
        tree_text = "ERROR"
        tokens_text = "ERROR"
        result_value: float | str = "ERROR"
        result_text = "ERROR"

        try:
            tokens = _tokenize(expression)
            ast = _parse(tokens)
            tree_text = _tree_to_string(ast)
            tokens_text = _tokens_to_string(tokens)
            value = _evaluate(ast)
            result_value = value
            result_text = _format_result(value)
        except Exception:
            pass

        results.append(
            {
                "input": expression,
                "tree": tree_text,
                "tokens": tokens_text,
                "result": result_value,
            }
        )
        output_blocks.append(
            f"Input: {expression}\n"
            f"Tree: {tree_text}\n"
            f"Tokens: {tokens_text}\n"
            f"Result: {result_text}"
        )

    with output_file.open("w", encoding="utf-8") as fh:
        fh.write("\n\n".join(output_blocks))
        if output_blocks:
            fh.write("\n")

    return results
