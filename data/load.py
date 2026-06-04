import pandas as pd

df = pd.read_csv('data/news_features.csv')

print("Num of rows and columns:", df.shape)
print("\nColumn names:", df.columns.tolist())
print("\nFirst 5 rows:")
print(df.head())
print("\nData types:")
print(df.dtypes)
