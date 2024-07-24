import argparse
import os

from bs4 import BeautifulSoup


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--input",
        "-i",
        type=str,
        help="Input file path", 
        default="data/currency_decimals.html"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Output file path",
        default="output/currency_decimals.kt"
    )

    args = parser.parse_args()

    # Parse the HTML file
    with open(args.input, "r") as f:
        soup = BeautifulSoup(f, "html.parser")

    parsed = {}
    columns = []
    rows = soup.find_all("tr")
    for heading in rows[0].find_all("th"):
        columns.append(heading.text)
        parsed[heading.text] = []

    for row in rows[1:]:
        for col, data in zip(columns, row.find_all("td")):
            parsed[col].append(data.text)

    code_col, decimals_col = columns[0], columns[2]

    # Get decimal groups
    decimal_groups = {}
    for code, decimals in zip(parsed[code_col], parsed[decimals_col]):
        num_dec = int(decimals.strip().split(" ", 1)[0])
        if num_dec not in decimal_groups:
            decimal_groups[num_dec] = []
        decimal_groups[num_dec].append(code)

    # Generate Kotlin lists
    output_parent = os.path.dirname(args.output)    
    if not os.path.exists(output_parent):
        os.makedirs(output_parent)

    with open(args.output, "w") as f:
        f.write("val currenciesByDecimals = mapOf(\n")
        for num_dec in sorted(decimal_groups.keys()):
            codes = decimal_groups[num_dec]
            f.write(f"\t{num_dec} to listOf(")
            f.write(", ".join([f"\"{code}\"" for code in codes]))
            f.write("),\n")
        f.write(")\n")