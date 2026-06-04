import pandas as pd

class DataValidator:
    def __init__(self, df, config):
        self.df = df
        self.config = config
        self.errors = []
        self.warnings = []
    
    def validate(self):
        self.check_required_columns()
        self.check_missing_values()
        self.check_sentiment_range()
        self.check_date_format()
        self.check_duplicates()
        
        return {
            'is_valid': len(self.errors) == 0,
            'errors': self.errors,
            'warnings': self.warnings
        }
    
    def check_required_columns(self):
        """Check if required columns exist"""
        for col in self.config.REQUIRED_COLUMNS:
            if col not in self.df.columns:
                self.errors.append(f"Missing required column: {col}")
    
    def check_missing_values(self):
        """Check for missing values"""
        missing = self.df.isnull().sum()
        for col, count in missing.items():
            if count > 0:
                percentage = (count / len(self.df)) * 100
                self.warnings.append(f"{col}: {count} missing values ({percentage:.1f}%)")
    
    def check_sentiment_range(self):
        """Check if sentiment values are in valid range"""
        if 'final_sentiment' in self.df.columns:
            min_val = self.df['final_sentiment'].min()
            max_val = self.df['final_sentiment'].max()
            
            if min_val < self.config.SENTIMENT_MIN:
                self.warnings.append(f"Sentiment below {self.config.SENTIMENT_MIN}: {min_val}")
            if max_val > self.config.SENTIMENT_MAX:
                self.warnings.append(f"Sentiment above {self.config.SENTIMENT_MAX}: {max_val}")
    
    def check_date_format(self):
        """Check if date column has valid format"""
        if 'date' in self.df.columns:
            try:
                pd.to_datetime(self.df['date'])
            except:
                self.errors.append("Date column has invalid format")
    
    def check_duplicates(self):
        """Check for duplicate rows"""
        duplicates = self.df.duplicated().sum()
        if duplicates > 0:
            self.warnings.append(f"Found {duplicates} duplicate rows")