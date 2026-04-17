# HIT137 Group Assignment 2

## Group Name: DAN20

### Group Members:

    * Ayushma Pandey – S394814
    * Bibek Prasai – S396542
    * Tharaka Maduwantha Senevirathne Edirisinghe Arachchige – S396116
    * Kritik Dahal – S395912



# Description

    This project contains two main components:

    1. **File Encryption & Decryption (Question 1)**
    2. **Expression Parser and Evaluator (Question 2)**



# Part 1: Encryption & Decryption (question1.py)

    ## Overview
        This program:
        * Reads text from `raw_text.txt`
        * Encrypts it using custom rules
        * Saves encrypted output to `encrypted_text.txt`
        * Stores rule mapping in `encrypted_text.rulemap`
        * Decrypts the file using stored rules
        * Verifies correctness of decryption



    ## Encryption Rules

    ### Lowercase Letters:
        * `a–m` → shift forward by `(shift1 × shift2)`
        * `n–z` → shift backward by `(shift1 + shift2)`

    ### Uppercase Letters:
        * `A–M` → shift backward by `shift1`
        * `N–Z` → shift forward by `(shift2²)`

    ### Other Characters:
        * Remain unchanged



    ## Key Improvement
        To ensure **correct decryption**, the program:
        * Stores which rule was used for each character
        * Saves this in a binary file: `encrypted_text.rulemap`
        This guarantees **100% accurate decryption**



    ## Files Used
    * `raw_text.txt` → input file
    * `encrypted_text.txt` → encrypted output
    * `decrypted_text.txt` → decrypted result
    * `encrypted_text.rulemap` → rule tracking file



    ## Features
    * Character-by-character encryption
    * Rule tracking for accurate reversal
    * Binary rule storage
    * Exact verification with error reporting



# Part 2: Expression Evaluator (question2.py + evaluator.py)

    ## Overview
        This part:
        * Reads expressions from `sample_input.txt`
        * Tokenizes input
        * Builds a parse tree
        * Evaluates expressions
        * Returns structured results (no output file)



    ## Features

        * Supports:

        * Addition `+`
        * Subtraction `-`
        * Multiplication `*`
        * Division `/`
        * Handles:

        * Parentheses `( )`
        * Unary minus (e.g., `-5`)
        * Implicit multiplication (e.g., `2(3+4)`)
        * Error handling:

        * Invalid characters
        * Invalid numbers
        * Syntax errors



    ## Files Used
        * `question2.py` → runs evaluator
        * `evaluator.py` → core logic (tokenizer, parser, evaluator)
        * `sample_input.txt` → input expressions
        * `sample_output.txt` → expected reference output



# How to Run
    ## Run Question 1 (Encryption):
    ```bash
    python question1.py
    ```

    Then enter:
    ```
    shift1: <number>
    shift2: <number>
    ```



    ## Run Question 2 (Evaluator):
    ```bash
    python question2.py
    ```



    ## Run Main (Test Only)
    ```bash
    python main.py
    ```


Repository Contents
    * `question1.py`
    * `question2.py`
    * `evaluator.py`
    * `main.py`
    * `raw_text.txt`
    * `encrypted_text.txt`
    * `decrypted_text.txt`
    * `encrypted_text.rulemap`
    * `sample_input.txt`
    * `sample_output.txt`
    * `README.md`
    * `.gitignore`



GitHub Repository:
https://github.com/ayushma77/Assignment2-SoftwareNow


Summary:
    Encryption is fully reversible using rule mapping
    Decryption is guaranteed accurate
    Expression evaluator supports complex math parsing
    Modular, clean, and testable design


