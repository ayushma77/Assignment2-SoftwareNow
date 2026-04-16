from evaluator import evaluate_file


def main() -> None:
    # Run the Question 2 evaluator using the provided sample input file.
    # The evaluator returns parsed/evaluated results in memory and does not
    # write any output file, so sample_output.txt remains the expected reference.
    evaluate_file("sample_input.txt")

    # Simple confirmation for command-line runs.
    print("Evaluation complete. No output file written.")


if __name__ == "__main__":
    # Standard Python script entry point.
    main()
