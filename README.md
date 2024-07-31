# BudgetApp Scripts

Various scripts to generate files to be used in [BudgetApp](https://github.com/HaGeza/BudgetApp).

## Parsing HTML tables

- `process_html_tables`: parses two tables and creates two files:
    - `--currency_in` --> `--currency_out`: generates two **Kotlin** variables: one is a list of supported currency codes, one is a dictionary mapping from currency code to decimals
    - `--exchange_in` --> `--exchange_out`: generates a single **JSON** file to be used for pre-populating the `exchange_rates` table of the application with rates for supported currencies to USD
