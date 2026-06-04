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
    
    return df

def identify_types(df):
    type_map = {
        'int64': 'int',
        'float64': 'double',
        'bool': 'bool',
        'datetime64': 'date',
        'object': 'string'
    }
    
    for col in df.columns:
        pandas_type = str(df[col].dtype)
        mongo_type = type_map.get(pandas_type, 'string')

def clean_data(df):
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
    
    df = df.drop_duplicates()
    
    for col in df.columns:
        if df[col].dtype in ['int64', 'float64']:
            df[col] = df[col].fillna(0)
        else:
            df[col] = df[col].fillna("unknown")
    
    return df

def prepare_for_mongodb(df):
    df_clean = df.copy()
    
    for col in df_clean.select_dtypes(include=['datetime64']).columns:
        df_clean[col] = df_clean[col].dt.strftime('%Y-%m-%d')
    
    df_clean = df_clean.replace({np.nan: None, pd.NaT: None})
    
    return df_clean.to_dict(orient='records')

def main():
    config = Config()
    
    df = load_data()
    identify_types(df)
    
    validator = DataValidator(df, config)
    validation_result = validator.validate()
    
    df = clean_data(df)
    records = prepare_for_mongodb(df)
    
    db = MongoDBHandler(config)
    
    if db.connect():
        db.create_schema()
        inserted = db.insert_many(records)
        db.create_indexes()
        db.close()

if __name__ == "__main__":
    main()