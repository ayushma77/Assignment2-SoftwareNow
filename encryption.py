# This file handles ALL encryption-related logic.
# We separate it so the program is modular and easier to test/debug.

def shift_char(c, shift):
    """
    Helper function to shift a character within A–Z or a–z.
    WHY: Centralising shifting avoids duplication and ensures consistency
    between encryption and decryption.
    """

    if c.islower():
        base = 97
    else:
        base = 65

    # WHY: % 26 ensures we wrap around alphabet correctly (A–Z or a–z)
    return chr((ord(c) - base + shift) % 26 + base)


def encrypt_char(c, shift1, shift2):
    """
    Encrypt a single character based on assignment rules.
    WHY: We process one character at a time so we can apply different rules
    depending on uppercase/lowercase and position in alphabet.
    """

    # Handle lowercase letters
    if c.islower():

        # First half of alphabet (a–m)
        if 'a' <= c <= 'm':
            # WHY: Multiply shifts to increase complexity of encryption
            shift = shift1 * shift2
            return shift_char(c, shift)

        # Second half (n–z)
        else:
            # WHY: Use negative shift to reverse direction for variation
            shift = shift1 + shift2
            return shift_char(c, -shift)

    # Handle uppercase letters
    elif c.isupper():

        # First half (A–M)
        if 'A' <= c <= 'M':
            # WHY: Simple negative shift creates a different encryption pattern
            return shift_char(c, -shift1)

        # Second half (N–Z)
        else:
            # WHY: Squaring shift2 creates a stronger encryption effect
            return shift_char(c, shift2 ** 2)

    # Non-alphabet characters remain unchanged
    # WHY: Assignment requirement (preserve formatting, spaces, punctuation)
    return c


def decrypt_char(c, shift1, shift2):
    """
    Reverse the encryption.
    WHY: Decryption must apply EXACT inverse operations of encryption.
    """

    # Handle lowercase letters
    if c.islower():

        # First half (a–m)
        if 'a' <= c <= 'm':
            # WHY: Reverse multiplication shift
            shift = shift1 * shift2
            return shift_char(c, -shift)

        # Second half (n–z)
        else:
            # WHY: Reverse addition shift
            shift = shift1 + shift2
            return shift_char(c, shift)

    # Handle uppercase letters
    elif c.isupper():

        # First half (A–M)
        if 'A' <= c <= 'M':
            # WHY: Reverse of -shift1 is +shift1
            return shift_char(c, shift1)

        # Second half (N–Z)
        else:
            # WHY: Reverse of +shift2^2 is subtraction
            return shift_char(c, -(shift2 ** 2))

    # Non-alphabet characters remain unchanged
    return c


def encrypt_file(shift1, shift2):
    """
    Read original file → encrypt → write to new file.
    WHY: Keeps original data intact (important for verification).
    """

    with open("raw_text.txt", "r") as f:
        text = f.read()

    # WHY: Efficient character-by-character transformation
    encrypted = "".join(encrypt_char(c, shift1, shift2) for c in text)

    with open("encrypted_text.txt", "w") as f:
        f.write(encrypted)


def decrypt_file(shift1, shift2):
    """
    Read encrypted file → decrypt → save result.
    WHY: Needed to verify correctness of encryption system.
    """

    with open("encrypted_text.txt", "r") as f:
        text = f.read()

    # WHY: Apply inverse transformation for each character
    decrypted = "".join(decrypt_char(c, shift1, shift2) for c in text)

    with open("decrypted_text.txt", "w") as f:
        f.write(decrypted)


def verify():
    """
    Compare original and decrypted files.
    WHY: Ensures encryption + decryption are perfectly reversible.
    """

    with open("raw_text.txt", "r") as f:
        original = f.read()

    with open("decrypted_text.txt", "r") as f:
        decrypted = f.read()

    # WHY: If true → encryption system is correct
    return original == decrypted