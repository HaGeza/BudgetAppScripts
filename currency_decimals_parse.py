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
        default="data/currencies_wikipedia.html",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Output file path",
        default="output/currency_info.kt",
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

    # Generate Kotlin lists
    output_parent = os.path.dirname(args.output)
    if not os.path.exists(output_parent):
        os.makedirs(output_parent)

    with open(args.output, "w") as f:
        codes = []

        f.write("val CURRENCIES_BY_DECIMALS = mapOf(\n")
        for code, decimals in zip(parsed[code_col], parsed[decimals_col]):
            try:
                num_dec = int(decimals.strip().split(" ", 1)[0])
            except ValueError:
                continue
            f.write(f'\t"{code}" to {num_dec},\n')
            codes.append(code)
        f.write(")\n\n")

        f.write(f"val CURRENCY_CODES = listOf(\n")
        for code in codes:
            f.write(f'\t"{code}",\n')
        f.write(")\n")
