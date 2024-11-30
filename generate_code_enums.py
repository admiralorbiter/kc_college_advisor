def generate_classification_dict(input_file, output_file):
    # Read the input file and generate dictionary entries
    entries = []
    with open(input_file, 'r') as f:
        next(f)  # Skip header line
        for line in f:
            # Split on first comma only
            parts = line.strip().split(',', 1)
            if len(parts) == 2:
                code, description = parts
                # Clean the code and description
                code = code.strip()
                description = description.strip()
                # Remove any extra quotes
                description = description.strip('"')
                entries.append(f'    "{code}": "{description}"')

    # Generate the Python code
    dict_code = "CLASSIFICATION_CODES = {\n"
    dict_code += ",\n".join(entries)
    dict_code += "\n}\n"

    # Write to output file
    with open(output_file, 'w') as f:
        f.write(dict_code)

if __name__ == "__main__":
    generate_classification_dict(
        "data/codes.csv",
        "models/classification_codes.py"
    )