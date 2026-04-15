from encryption import encrypt_file, decrypt_file, verify
from parser import tokenize, Parser, evaluate, print_tree


def run_encryption():
    """
    Controls encryption workflow.
    WHY: Keeps main() clean and modular.
    """

    print("=== Encryption Part ===")

    shift1 = int(input("Enter shift1: "))
    shift2 = int(input("Enter shift2: "))

    encrypt_file(shift1, shift2)
    decrypt_file(shift1, shift2)

    if verify():
        print("Decryption successful!")
    else:
        print("Decryption failed!")


def run_parser():
    """
    Controls expression parsing.
    """

    print("\n=== Expression Parser ===")

    expr = input("Input: ")

    tokens = tokenize(expr)

    if tokens == "ERROR":
        print("Tokens: ERROR")
        print("Tree: ERROR")
        print("Result: ERROR")
        return

    print("Tokens:", tokens)

    parser = Parser(tokens)
    tree = parser.expr()

    print("Tree:", print_tree(tree))

    result = evaluate(tree)
    print("Result:", result)


def main():
    """
    Entry point of program.
    """

    run_encryption()
    run_parser()


if __name__ == "__main__":
    main()