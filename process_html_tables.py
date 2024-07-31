"""
Script for parsing HTML tables:
- `--currency_in` --> `--currency_out`: generates two **Kotlin** variables: one is a list of supported currency codes,
  one is a dictionary mapping from currency code to decimals
- `--exchange_in` --> `--exchange_out`: generates a single **JSON** file to be used for pre-populating
  the `exchange_rates` table of the application with rates for supported currencies to USD
"""

import argparse
import json
import os

from bs4 import BeautifulSoup
import numpy as np

from settings import EXCHANGE_RATE_OUT


def parse_html_table(in_path: str) -> tuple[dict, dict]:
    """
    Parse an HTML table into a dictionary of columns and rows

    Args: `in_path`: Path to the input HTML file
    Returns: Tuple of columns and parsed data dictionaries
    """

    with open(in_path, "r") as f:
        soup = BeautifulSoup(f, "html.parser")

    parsed = {}
    columns = []
    rows = soup.find_all("tr")
    for heading in rows[0].find_all("th"):
        columns.append(heading.text)
        parsed[heading.text] = []

    for row in rows[1:]:
        for col, data in zip(columns, row.find_all(["th", "td"])):
            parsed[col].append(data.text)

    return columns, parsed


def get_currency_codes(in_file: str, code_col_ind: int = 0) -> list[str]:
    """
    Get a list of currency codes from table in `in_file`

    Args:
        `in_file`: Path to the input HTML file
        `code_col_ind`: Index of the column with currency codes, default is 0
    Returns: List of currency codes
    """

    cols, data = parse_html_table(in_file)
    return data[cols[code_col_ind]]


def generate_currency_info_constants(
    in_file: str,
    out_file: str,
    codes: list[str] = [],
    code_col_ind: int = 0,
    decimals_col_ind: int = 2,
) -> list[str]:
    """
    Generate Kotlin code for currency codes and decimals from a html table

    Args:
        `in_file`: Path to the input HTML file
        `out_file`: Path to the output Kotlin file
        `codes`: List of currency codes to include, use all if empty
    """

    currency_cols, currency_data = parse_html_table(in_file)
    code_col, decimals_col = (
        currency_cols[code_col_ind],
        currency_cols[decimals_col_ind],
    )

    # Generate Kotlin lists for currency codes and decimals
    output_parent = os.path.dirname(out_file)
    if not os.path.exists(output_parent):
        os.makedirs(output_parent)

    with open(out_file, "w") as f:
        seen_codes = []

        f.write("val CURRENCIES_BY_DECIMALS = mapOf(\n")
        for code, decimals in zip(currency_data[code_col], currency_data[decimals_col]):
            if codes and code not in codes:
                continue

            try:
                num_dec = int(decimals.strip().split(" ", 1)[0])
            except ValueError:
                continue
            f.write(f'\t"{code}" to {num_dec},\n')
            seen_codes.append(code)
        f.write(")\n\n")

        f.write(f"val CURRENCY_CODES = listOf(\n")
        for code in seen_codes:
            f.write(f'\t"{code}",\n')
        f.write(")\n")


def generate_exchange_rates_json(
    in_file: str,
    out_file: str,
    codes: list[str] = [],
    code_col_ind: int = 0,
    rate_col_ind: int = 3,
):
    """
    Generate a JSON file with exchange rates from a HTML table

    Args:
        `in_file`: Path to the input HTML file
        `out_file`: Path to the output JSON file
        `codes`: List of currency codes to include, use all if empty
    """

    exchange_cols, exchange_data = parse_html_table(in_file)
    code_col, rate_col = exchange_cols[code_col_ind], exchange_cols[rate_col_ind]

    json_data = []
    for code, rate in zip(exchange_data[code_col], exchange_data[rate_col]):
        if codes and code not in codes:
            continue

        num_rate = float(rate.strip().replace(",", ""))
        json_data.append(
            {
                "source": code.strip(),
                "other": "USD",
                "rate": np.format_float_positional(num_rate, trim="-"),
            }
        )

    with open(out_file, "w") as f:
        json.dump(json_data, f, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--currency_in",
        "-ci",
        type=str,
        help="Currency input file path",
        default="data/currencies_wikipedia.html",
    )
    parser.add_argument(
        "--currency_out",
        "-co",
        type=str,
        help="Currency output file path",
        default="output/currency_info.kt",
    )
    parser.add_argument(
        "--exchange_in",
        "-ei",
        type=str,
        help="Exchange input file path",
        default="data/exchange_rates.html",
    )
    parser.add_argument(
        "--exchange_out",
        "-eo",
        type=str,
        help="Exchange output file path",
        default=EXCHANGE_RATE_OUT,
    )

    args = parser.parse_args()

    codes = []
    try:
        codes_currency = get_currency_codes(args.currency_in)
        codes_exchange = get_currency_codes(args.exchange_in)
        codes = list(set(codes_currency) & set(codes_exchange))
    except Exception as e:
        print(f"Error getting currency codes: {e}")

    try:
        generate_currency_info_constants(args.currency_in, args.currency_out, codes)
    except Exception as e:
        print(f"Error generating currency info constants: {e}")

    try:
        generate_exchange_rates_json(args.exchange_in, args.exchange_out, codes)
    except Exception as e:
        print(f"Error generating exchange rates JSON: {e}")
