import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

class DataPipeline:
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.complex_keywords = ['scale', 'million', 'expert', 'global', 'enterprise', 'launch', 'transform', 'intensive']

    def load_data(self) -> pd.DataFrame:
        """Loads data from the CSV file."""
        try:
            df = pd.read_csv(self.data_path)
            logger.info(f"Loaded {len(df)} records from {self.data_path}")
            return df
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise

    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Applies feature engineering using Pandas."""
        logger.info("Engineering features...")
        df = df.copy()

        # 1. Goal Length: Combine title and description length
        df['title_length'] = df['title'].astype(str).apply(len)
        df['desc_length'] = df['description'].astype(str).apply(len)
        df['goal_length'] = df['title_length'] + df['desc_length']

        # 2. Complexity Indicators: Count occurrences of complex keywords
        def count_complexity(text):
            text = str(text).lower()
            return sum(1 for word in self.complex_keywords if word in text)

        df['complexity_score'] = df['description'].apply(count_complexity) + df['title'].apply(count_complexity)

        # 3. Category Encoding (Pandas categorical mapping)
        # We store the mapping so it could be reused, but here we just convert to category codes
        df['category'] = df['category'].astype('category')
        df['category_code'] = df['category'].cat.codes

        # Store the category mapping for later reference
        self.category_mapping = dict(enumerate(df['category'].cat.categories))

        return df

    def preprocess_data(self) -> pd.DataFrame:
        """Runs the full Pandas pipeline."""
        df = self.load_data()
        
        # Handle missing values if any
        df.fillna('', inplace=True)
        
        # Feature Engineering
        df_processed = self.engineer_features(df)
        
        # We keep only features needed for ML (Step 4) and the target variable
        features = ['goal_length', 'complexity_score', 'category_code', 'difficulty']
        return df_processed[features]
