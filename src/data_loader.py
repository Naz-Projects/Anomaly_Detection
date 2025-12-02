"""Data loading and validation for anomaly detection."""

import pandas as pd
from typing import Tuple, List


class DataLoader:
    """Handle Excel file loading and validation."""

    # Fields to exclude from analysis (summary fields)
    EXCLUDED_RESULT_NAMES = [
        "Ave Dim Stab Warp",
        "Std Dim Stab Warp",
        "Ave Dim Stab Fill",
        "Std Dim Stab Fill",
        "Test Complete?"
    ]

    # Required columns in the Excel file
    REQUIRED_COLUMNS = [
        "ITEM_NUMBER",
        "TEST_NUMBER",
        "RESULT_NAME",
        "RESPONSE"
    ]

    @staticmethod
    def load_excel(file) -> Tuple[pd.DataFrame, str]:
        """
        Load and validate Excel file.

        Parameters:
        -----------
        file : UploadedFile
            Streamlit uploaded file object

        Returns:
        --------
        Tuple[pd.DataFrame, str]
            (dataframe, error_message)
            If successful, error_message is None
        """
        try:
            # Read Excel file
            df = pd.read_excel(file, engine='openpyxl')

            # Validate required columns
            missing_cols = [col for col in DataLoader.REQUIRED_COLUMNS
                          if col not in df.columns]
            if missing_cols:
                return None, f"Missing required columns: {', '.join(missing_cols)}"

            # Check if dataframe is empty
            if df.empty:
                return None, "The uploaded file contains no data"

            return df, None

        except Exception as e:
            return None, f"Error reading Excel file: {str(e)}"

    @staticmethod
    def get_item_numbers(df: pd.DataFrame) -> List[str]:
        """Get list of unique ITEM_NUMBERs from dataframe."""
        return sorted(df['ITEM_NUMBER'].dropna().unique().tolist())

    @staticmethod
    def get_analyzable_result_names(df: pd.DataFrame, item_number: str = None) -> List[str]:
        """
        Get list of RESULT_NAMEs that can be analyzed (excluding summary fields).

        Parameters:
        -----------
        df : pd.DataFrame
            The input dataframe
        item_number : str, optional
            If provided, filter to only this ITEM_NUMBER

        Returns:
        --------
        List[str]
            Sorted list of analyzable RESULT_NAMEs
        """
        if item_number:
            df = df[df['ITEM_NUMBER'] == item_number]

        result_names = df['RESULT_NAME'].dropna().unique()

        # Filter out excluded summary fields
        analyzable = [name for name in result_names
                     if name not in DataLoader.EXCLUDED_RESULT_NAMES]

        return sorted(analyzable)

    @staticmethod
    def get_test_count(df: pd.DataFrame, item_number: str) -> int:
        """Get count of unique TEST_NUMBERs for a given ITEM_NUMBER."""
        filtered_df = df[df['ITEM_NUMBER'] == item_number]
        return filtered_df['TEST_NUMBER'].nunique()

    @staticmethod
    def get_value_range(df: pd.DataFrame, item_number: str, result_name: str) -> Tuple[float, float]:
        """
        Get min and max RESPONSE values for a specific ITEM_NUMBER and RESULT_NAME.

        Parameters:
        -----------
        df : pd.DataFrame
            The input dataframe
        item_number : str
            The ITEM_NUMBER to filter
        result_name : str
            The RESULT_NAME to filter

        Returns:
        --------
        Tuple[float, float]
            (min_value, max_value) or (None, None) if no numeric data
        """
        filtered_df = df[
            (df['ITEM_NUMBER'] == item_number) &
            (df['RESULT_NAME'] == result_name)
        ]

        try:
            # Convert to numeric, coerce errors to NaN
            numeric_values = pd.to_numeric(filtered_df['RESPONSE'], errors='coerce')
            numeric_values = numeric_values.dropna()

            if len(numeric_values) == 0:
                return None, None

            return float(numeric_values.min()), float(numeric_values.max())
        except Exception:
            return None, None

    @staticmethod
    def get_basic_stats(df: pd.DataFrame) -> dict:
        """
        Get basic statistics about the uploaded data.

        Returns:
        --------
        dict with keys:
            - total_rows: int
            - total_items: int
            - total_tests: int
        """
        return {
            'total_rows': len(df),
            'total_items': df['ITEM_NUMBER'].nunique(),
            'total_tests': df['TEST_NUMBER'].nunique()
        }
