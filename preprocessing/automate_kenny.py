import pandas as pd
import numpy as np
import os

def preprocess_survey_data(df):
    """
    Preprocesses raw survey data based on the Diabetes Health Indicators Dataset features.

    Args:
        df: pandas DataFrame containing the raw survey data.

    Returns:
        pandas DataFrame with processed data.
    """

    # Ensure column names are consistent (e.g., handle potential whitespace or case differences)
    df.columns = df.columns.str.strip().str.replace(' ', '_')

    # 1. Handle Missing Values
    # Impute numerical columns with median and categorical/coded columns with mode
    for col in df.columns:
        if col in ['BMI', 'MentHlth', 'PhysHlth']: # Numerical features not explicitly binned or scaled
            df[col].fillna(df[col].median(), inplace=True)
        elif col in ['Diabetes_binary', 'HighBP', 'HighChol', 'CholCheck', 'Smoker',
                     'Stroke', 'HeartDiseaseorAttack', 'PhysActivity', 'Fruits',
                     'Veggies', 'HvyAlcoholConsump', 'AnyHealthcare', 'NoDocbcCost',
                     'DiffWalk', 'Sex', 'GenHlth', 'Age', 'Education', 'Income']: # Coded/Categorical/Binned features
            df[col].fillna(df[col].mode()[0], inplace=True)


    # 2. Handle Duplicates
    df.drop_duplicates(inplace=True)

    # Reset index after dropping duplicates
    df.reset_index(drop=True, inplace=True)

    # 3. Handle Outliers (Identification only, no removal as per notebook's reasoning)
    # You can add outlier removal or transformation logic here if needed for your raw data.
    # For example, using IQR:
    # for col in df.columns:
    #     if col in ['BMI', 'MentHlth', 'PhysHlth']:
    #         Q1 = df[col].quantile(0.25)
    #         Q3 = df[col].quantile(0.75)
    #         IQR = Q3 - Q1
    #         lower_bound = Q1 - 1.5 * IQR
    #         upper_bound = Q3 + 1.5 * IQR
    #         # Optional: remove outliers
    #         # df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]


    # 4. Encoding Categorical Features and Binning Numerical Features
    # This assumes raw data might not be in the desired numerical scales or binned.

    # Ensure binary columns are 0 or 1
    binary_cols = ['Diabetes_binary', 'HighBP', 'HighChol', 'CholCheck', 'Smoker',
                   'Stroke', 'HeartDiseaseorAttack', 'PhysActivity', 'Fruits',
                   'Veggies', 'HvyAlcoholConsump', 'AnyHealthcare', 'NoDocbcCost',
                   'DiffWalk', 'Sex']
    for col in binary_cols:
        if col in df.columns:
            # Convert to numeric first, coercing errors, then to int (0 or 1)
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
            df[col] = df[col].apply(lambda x: 1 if x > 0 else 0) # Ensure only 0 or 1

    # Handle GenHlth (scale 1-5) - Encoding into scale
    # Explicit mapping based on descriptions
    genhlth_mapping = {
        1: 1, 'excellent': 1,
        2: 2, 'very good': 2,
        3: 3, 'good': 3,
        4: 4, 'fair': 4,
        5: 5, 'poor': 5
    }
    if 'GenHlth' in df.columns:
        # Check if already in expected numerical range and type
        if not (df['GenHlth'].dtype in ['int64', 'float64'] and df['GenHlth'].between(1, 5, inclusive='both').all()):
            df['GenHlth'] = df['GenHlth'].map(genhlth_mapping)
            df['GenHlth'] = pd.to_numeric(df['GenHlth'], errors='coerce').fillna(df['GenHlth'].mode()[0]).astype(int)
        df['GenHlth'] = df['GenHlth'].clip(1, 5) # Ensure values are within the 1-5 range


    # Handle Education (scale 1-6) - Encoding into scale
    # Explicit mapping based on descriptions
    education_mapping = {
        1: 1, 'never attended school or only kindergarten': 1,
        2: 2, 'elementary': 2,
        3: 3, 'middle school': 3,
        4: 4, 'high school': 4,
        5: 5, 'less than 4 years college': 5,
        6: 6, '4 years college or more': 6
    }
    if 'Education' in df.columns:
        # Check if already in expected numerical range and type
        if not (df['Education'].dtype in ['int64', 'float64'] and df['Education'].between(1, 6, inclusive='both').all()):
            df['Education'] = df['Education'].map(education_mapping)
            df['Education'] = pd.to_numeric(df['Education'], errors='coerce').fillna(df['Education'].mode()[0]).astype(int)
        df['Education'] = df['Education'].clip(1, 6) # Ensure values are within the 1-6 range


    # Handle Age (13-level category) - Binning
    # This is a placeholder for binning if raw Age is not in 1-13 scale.
    # Assuming raw Age is continuous and needs to be binned according to the descriptions.
    if 'Age' in df.columns:
        # Check if already in expected numerical range and type (1-13)
        if not (df['Age'].dtype in ['int64', 'float64'] and df['Age'].between(1, 13, inclusive='both').all()):
            # Example binning for continuous Age:
            age_bins = [18, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, float('inf')]
            age_labels = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
            # Convert to numeric first, coercing errors
            df['Age'] = pd.to_numeric(df['Age'], errors='coerce')
            # Handle potential NaNs after coercion before binning
            df['Age'].fillna(df['Age'].median() if not df['Age'].isnull().all() else age_labels[len(age_labels)//2 -1], inplace=True) # Impute with median or middle bin label
            df['Age'] = pd.cut(df['Age'], bins=age_bins, labels=age_labels, right=False, include_lowest=True)
        df['Age'] = pd.to_numeric(df['Age']) # Ensure it's numeric


    # Handle Income (scale 1-8) - Binning
    # Assuming raw Income is not in 1-8 scale and needs to be mapped or binned.
    if 'Income' in df.columns:
        # Check if already in expected numerical range and type (1-8)
        if not (df['Income'].dtype in ['int64', 'float64'] and df['Income'].between(1, 8, inclusive='both').all()):
            income_bins = [0, 10000, 15000, 20000, 25000, 35000, 50000, 75000, float('inf')] # Example income bins based on descriptions
            income_labels = [1, 2, 3, 4, 5, 6, 7, 8]
            df['Income'] = pd.to_numeric(df['Income'], errors='coerce')
            df['Income'].fillna(df['Income'].median() if not df['Income'].isnull().all() else income_labels[len(income_labels)//2 -1], inplace=True) # Impute with median or middle bin label
            df['Income'] = pd.cut(df['Income'], bins=income_bins, labels=income_labels, right=False, include_lowest=True)
        df['Income'] = pd.to_numeric(df['Income']) # Ensure it's numeric

    # MentHlth and PhysHlth are numerical (days in past 30 days) - no binning or specific encoding needed beyond ensuring numeric type
    if 'MentHlth' in df.columns:
        df['MentHlth'] = pd.to_numeric(df['MentHlth'], errors='coerce').fillna(df['MentHlth'].median())
        df['MentHlth'] = df['MentHlth'].clip(0, 30).astype(int) # Ensure values are within 0-30 range

    if 'PhysHlth' in df.columns:
        df['PhysHlth'] = pd.to_numeric(df['PhysHlth'], errors='coerce').fillna(df['PhysHlth'].median())
        df['PhysHlth'] = df['PhysHlth'].clip(0, 30).astype(int) # Ensure values are within 0-30 range


    # 5. Ensure Correct Data Types (Final check)
    # Convert all columns to numeric, coercing errors to NaN and then filling NaN.
    for col in df.columns:
         df[col] = pd.to_numeric(df[col], errors='coerce')
         # Re-impute any NaNs that might have been introduced by coercion after specific handling
         if df[col].isnull().any():
             if col in binary_cols or col in ['GenHlth', 'Age', 'Education', 'Income']: # Coded/Binned features
                  df[col].fillna(df[col].mode()[0], inplace=True) # Impute with mode
             else:
                  df[col].fillna(df[col].median(), inplace=True) # Impute with median


    return df

if __name__ == "__main__":
    # Define the path to your raw data file
    # You might need to adjust this path based on where you store your raw data in the repository
    raw_data_path = 'diabetes_raw.csv' # Replace with your actual raw data file name

    # Define the path where you want to save the processed data
    processed_data_path = 'preprocessing/diabetes_preprocessing.csv' # Replace with your desired output file name

    try:
        # Load the raw data
        raw_df = pd.read_csv(raw_data_path)
        print(f"Successfully loaded raw data from {raw_data_path}")
        print("Raw data info:")
        raw_df.info()

        # Preprocess the data
        processed_df = preprocess_survey_data(raw_df)
        print("\nData preprocessing complete.")
        print("Processed data info:")
        processed_df.info()
        print("Processed data head:")
        print(processed_df.head())

        # Ensure the preprocessing directory exists before saving
        os.makedirs(os.path.dirname(processed_data_path), exist_ok=True)

        # Save the processed data
        processed_df.to_csv(processed_data_path, index=False)
        print(f"\nProcessed data saved to {processed_data_path}")
        

    except FileNotFoundError:
        print(f"Error: Raw data file not found at {raw_data_path}")
    except Exception as e:
        print(f"An error occurred during preprocessing: {e}")
