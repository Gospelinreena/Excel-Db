import pandas as pd
import numpy as np
from config import Config
from validator import DataValidator
from db_handler import MongoDBHandler


def load_data():
    config = Config()

    if config.INPUT_FILE.suffix == ".csv":
        df = pd.read_csv(config.INPUT_FILE)
    else:
        df = pd.read_excel(config.INPUT_FILE)
    return df


def identify_types(df):

    type_map = {
        "int64": "int",
        "float64": "double",
        "bool": "bool",
        "datetime64[ns]": "date",
        "object": "string"
    }
    detected = {}

    for col in df.columns:
        pandas_type = str(df[col].dtype)
        detected[col] = type_map.get(
            pandas_type,
            "string"
        )
    return detected


def clean_data(df):

    if "date" in df.columns:

        df["date"] = pd.to_datetime(
            df["date"],
            errors="coerce"
        )
    df = df.drop_duplicates()

    df = df.where(
        pd.notnull(df),
        None
    )
    return df


def prepare_for_mongodb(df):

    df_clean = df.copy()

    df_clean = df_clean.replace(
        {
            np.nan: None,
            pd.NaT: None
        }
    )

    return df_clean.to_dict(
        orient="records"
    )


def main():
    print("Loading Data...")
    config = Config()

    df = load_data()

    print(
        f"Loaded {len(df)} rows"
    )

    mongo_types = identify_types(df)

    print("\nDetected Types:")

    for col, dtype in mongo_types.items():
        print(f"{col} -> {dtype}")

    validator = DataValidator(
        df,
        config
    )

    validation = validator.validate()

    if validation["errors"]:
        print("\nValidation Errors:")
        for error in validation["errors"]:
            print(error)
        return

    if validation["warnings"]:
        print("\nWarnings:")
        for warning in validation["warnings"]:
            print(warning)

    df = clean_data(df)

    records = prepare_for_mongodb(df)

    db = MongoDBHandler(config)

    if db.connect():

        db.create_schema(mongo_types)
        inserted = db.insert_many(records)
        print(
            f"\nInserted {inserted} records"
        )

        db.create_indexes()
        print("Indexes Created")
        db.close()
        print("Connection Closed")


if __name__ == "__main__":
    main()