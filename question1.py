"""
Create a program that read the text file " raw_text.txt",
encrypts its contents using a simple encryption method, 
and writes the encrypted text into a new file "encrypted_text.txt". 
Then create a function to decrypt the content and a function to 
verify the decryption was successful.

"""
def encrypt_char(ch, shift1, shift2):
    """Encrypt a single character using the assignment rules."""
    if ch.islower():
        pos = ord(ch) - ord('a')  # 0-25
        if pos <= 12:  # a-m: shift forward by shift1 * shift2
            new_pos = (pos + shift1 * shift2) % 26
        else:          # n-z: shift backward by shift1 + shift2
            new_pos = (pos - (shift1 + shift2)) % 26
        return chr(new_pos + ord('a'))

    elif ch.isupper():
        pos = ord(ch) - ord('A')  # 0-25
        if pos <= 12:  # A-M: shift backward by shift1
            new_pos = (pos - shift1) % 26
        else:          # N-Z: shift forward by shift2^2
            new_pos = (pos + shift2 ** 2) % 26
        return chr(new_pos + ord('A'))

    else:
        # Spaces, tabs, newlines, special chars, numbers — unchanged
        return ch


def decrypt_char(ch, shift1, shift2):
    """Reverse the encryption for a single character."""
    if ch.islower():
        pos = ord(ch) - ord('a')
        # We need to reverse: but after encryption the letter has moved,
        # so we reverse by applying the inverse shift and checking original range.
        # Try reversing a-m rule: original pos = new_pos - shift1*shift2
        candidate1 = (pos - shift1 * shift2) % 26
        # Try reversing n-z rule: original pos = new_pos + shift1+shift2
        candidate2 = (pos + (shift1 + shift2)) % 26

        # Pick the candidate that matches its original rule's range
        if 0 <= candidate1 <= 12:
            return chr(candidate1 + ord('a'))
        else:
            return chr(candidate2 + ord('a'))

    elif ch.isupper():
        pos = ord(ch) - ord('A')
        # Reverse A-M rule: original pos = new_pos + shift1
        candidate1 = (pos + shift1) % 26
        # Reverse N-Z rule: original pos = new_pos - shift2^2
        candidate2 = (pos - shift2 ** 2) % 26

        if 0 <= candidate1 <= 12:
            return chr(candidate1 + ord('A'))
        else:
            return chr(candidate2 + ord('A'))

    else:
        return ch


def encrypt_file(shift1, shift2, input_path="raw_text.txt", output_path="encrypted_text.txt"):
    """Read raw_text.txt, encrypt it, and write to encrypted_text.txt."""
    with open(input_path, 'r', encoding='utf-8') as f:
        raw_text = f.read()

    encrypted = ''.join(encrypt_char(ch, shift1, shift2) for ch in raw_text)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(encrypted)

    print(f"[✓] Encrypted '{input_path}' → '{output_path}'")
    return encrypted


def decrypt_file(shift1, shift2, input_path="encrypted_text.txt", output_path="decrypted_text.txt"):
    """Read encrypted_text.txt, decrypt it, and write to decrypted_text.txt."""
    with open(input_path, 'r', encoding='utf-8') as f:
        encrypted_text = f.read()

    decrypted = ''.join(decrypt_char(ch, shift1, shift2) for ch in encrypted_text)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(decrypted)

    print(f"[✓] Decrypted '{input_path}' → '{output_path}'")
    return decrypted


def verify_decryption(original_path="raw_text.txt", decrypted_path="decrypted_text.txt"):
    """Compare raw_text.txt with decrypted_text.txt and report result."""
    with open(original_path, 'r', encoding='utf-8') as f:
        original = f.read()

    with open(decrypted_path, 'r', encoding='utf-8') as f:
        decrypted = f.read()

    if original == decrypted:
        print("[✓] Verification PASSED: Decrypted text matches the original.")
        return True
    else:
        # Show first difference to help debugging
        for i, (a, b) in enumerate(zip(original, decrypted)):
            if a != b:
                print(f"[✗] Verification FAILED: First difference at position {i} "
                      f"(original={repr(a)}, decrypted={repr(b)})")
                return False
        # One is longer than the other
        print(f"[✗] Verification FAILED: Lengths differ "
              f"(original={len(original)}, decrypted={len(decrypted)})")
        return False


def main():
    print("=== HIT137 Assignment 2 — Question 1: Encryption ===\n")

    # Step 1: Get shift values from user
    while True:
        try:
            shift1 = int(input("Enter shift1 (positive integer): "))
            shift2 = int(input("Enter shift2 (positive integer): "))
            if shift1 <= 0 or shift2 <= 0:
                print("Please enter positive integers.\n")
                continue
            break
        except ValueError:
            print("Invalid input. Please enter integers.\n")

    print()

    # Step 2: Encrypt
    encrypt_file(shift1, shift2)

    # Step 3: Decrypt
    decrypt_file(shift1, shift2)

    # Step 4: Verify
    verify_decryption()


if __name__ == "__main__":
    main()