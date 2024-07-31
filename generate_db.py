"""
Script to generate and execute an `.sql` file to be used for pre-populating the database:
"""

import argparse
import json
import os
import sqlite3

from natsort import natsorted

from local_settings import APP_DIR
from settings import EXCHANGE_RATE_OUT

if __name__ == "__main__":
    ASSET_PATH = os.path.join(APP_DIR, "app/src/main/assets")
    DATABASE_NAME = "com.example.budgetapp.data.database.AppDatabase"
    EXCHANGE_RATE_TABLE = "exchange_rates"

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--schema_dir",
        "-sd",
        type=str,
        default=os.path.join(ASSET_PATH, "schemas", DATABASE_NAME),
        help="Directory containing the schema files. The script will use the `.json` file in the directory with the highest version number.",
    )
    parser.add_argument(
        "--sql_path",
        type=str,
        default=os.path.join(ASSET_PATH, "create_db.sql"),
        # default="output/create_db.sql",
        help="Path to save the `.sql` file to.",
    )
    parser.add_argument(
        "--db_dir",
        type=str,
        default=os.path.join(ASSET_PATH, "database"),
        help="Name of the database file to be created.",
    )
    parser.add_argument(
        "--exchange_json",
        "-ej",
        type=str,
        default=EXCHANGE_RATE_OUT,
        help="Path to the exchange rates json file.",
    )

    args = parser.parse_args()

    # --------------------------------------------------- #

    # Find schema file with highest version number
    schema_files = os.listdir(args.schema_dir)
    latest_schema_file = natsorted(schema_files)[-1]
    schema_version = latest_schema_file.split(".")[0]
    latest_schema_file = os.path.join(args.schema_dir, latest_schema_file)

    with open(latest_schema_file, "r") as f:
        schema_dict = json.load(f)

    sql_script = ""

    entities = schema_dict["database"]["entities"]
    for entity in entities:
        table_name = entity["tableName"]
        create_sql = entity["createSql"].replace("`${TABLE_NAME}`", table_name)
        sql_script += f"{create_sql};\n\n"

    # Insert exchange rates
    with open(args.exchange_json, "r") as f:
        exchange_rates = json.load(f)

    sql_script += f"INSERT INTO {EXCHANGE_RATE_TABLE} (source, other, rate) VALUES"
    for entry in exchange_rates:
        source, other, rate = entry["source"], entry["other"], entry["rate"]
        sql_script += f"\n('{source}', '{other}', {rate}),"
    sql_script = sql_script[:-1] + ";\n"

    with open(args.sql_path, "w") as f:
        f.write(sql_script)
        print(f"SQL script created at {args.sql_path}")

    # Execute script and save resulting database
    db_path = os.path.join(
        args.db_dir, f"{DATABASE_NAME.split('.')[-1]}_{schema_version}.db"
    )

    # Connect to the SQLite database
    with sqlite3.connect(db_path) as conn:
        conn.cursor().executescript(sql_script)
        conn.commit()
        print(f"Database created at {db_path}")
