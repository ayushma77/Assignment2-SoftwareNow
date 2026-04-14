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


