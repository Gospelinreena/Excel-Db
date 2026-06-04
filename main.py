import pandas as pd
import numpy as np
from config import Config
from validator import DataValidator
from db_handler import MongoDBHandler

def load_data():
    config = Config()
    
    if config.INPUT_FILE.suffix == '.csv':
        df = pd.read_csv(config.INPUT_FILE)
    else:
        df = pd.read_excel(config.INPUT_FILE)
    
    print(f"Loaded: {df.shape[0]} rows, {df.shape[1]} columns")
    return df

def identify_types(df):
    type_map = {
        'int64': 'int',
        'float64': 'double',
        'bool': 'bool',
        'datetime64': 'date',
        'object': 'string'
    }
    
    print("\nData type mapping:")
    for col in df.columns:
        pandas_type = str(df[col].dtype)
        mongo_type = type_map.get(pandas_type, 'string')
        print(f"  {col}: {pandas_type} -> MongoDB {mongo_type}")

def clean_data(df):
    print("\nCleaning data...")
    
    # Convert date
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        print(" Converted date column")
    
    # Remove duplicates
    before = len(df)
    df = df.drop_duplicates()
    print(f" Removed {before - len(df)} duplicates")
    
    # Fill missing values
    for col in df.columns:
        if df[col].dtype in ['int64', 'float64']:
            df[col] = df[col].fillna(0)
        else:
            df[col] = df[col].fillna("unknown")
    
    print(f" Filled missing values")
    return df

def prepare_for_mongodb(df):
    """Convert DataFrame to list of dictionaries"""
    df_clean = df.copy()
    
    # Convert datetime to string
    for col in df_clean.select_dtypes(include=['datetime64']).columns:
        df_clean[col] = df_clean[col].dt.strftime('%Y-%m-%d')
    
    # Replace NaN with None
    df_clean = df_clean.replace({np.nan: None, pd.NaT: None})
    
    return df_clean.to_dict(orient='records')

def main():
    config = Config()
    
    print("\n[1/6] Loading data...")
    df = load_data()
    
    print("\n[2/6] Identifying data types...")
    identify_types(df)

    print("\n[3/6] Validating data...")
    validator = DataValidator(df, config)
    validation_result = validator.validate()
    
    if validation_result['errors']:
        print("  Validation errors:")
        for error in validation_result['errors']:
            print(f"     - {error}")
    
    if validation_result['warnings']:
        print("  Warnings:")
        for warning in validation_result['warnings']:
            print(f"     - {warning}")
    
    print("\n[4/6] Cleaning data...")
    df = clean_data(df)
    
    print("\n[5/6] Preparing for MongoDB...")
    records = prepare_for_mongodb(df)
    print(f"  Prepared {len(records)} records")
    
    print("\n[6/6] Inserting into MongoDB...")
    db = MongoDBHandler(config)
    
    if db.connect():
        db.create_schema()
        inserted = db.insert_many(records)
        db.create_indexes()
        total = db.get_count()
        db.close()
        
        print(f"\n   Success! Inserted {inserted} records")
        print(f"   Total in MongoDB: {total}")
    else:
        print("\n   MongoDB not available")
        print("  Saving to CSV instead...")
        df.to_csv('data/output_backup.csv', index=False)
        print("   Saved to data/output_backup.csv")
    
    print("PIPELINE COMPLETE")
    print(f"Input: {config.INPUT_FILE}")
    print(f"Rows processed: {len(df)}")
    print(f"Database: {config.DATABASE_NAME}")
    print(f"Collection: {config.COLLECTION_NAME}")

if __name__ == "__main__":
    main()