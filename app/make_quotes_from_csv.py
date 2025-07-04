import csv

# This function takes a filename, opens the CSV file, and prints each row as a list.
def make_str_from_csv_file(filename):
    """
    This function takes a filename, opens the CSV file, and returns a string with each row as a list.
    The CSV file should have at least three columns:
    - Column 1: The source
    - Column 2: The author
    - Column 3: The quote
    The function returns a text of quotes with separator ---.
    """
    result = []
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            result.append(row[2])
    result = '\n\n---\n\n'.join(result)
    return result

# This function takes a string and writes it to a markdown (.md) file.
def to_md(data: str):
    with open('output.md', 'w', encoding='utf-8') as mdfile:
        mdfile.write(data)
