"""Anomaly detection engine for manufacturing test data."""

import pandas as pd
from typing import Dict, Tuple


class AnomalyDetector:
    """Detect anomalies in test data based on user-defined boundaries."""

    @staticmethod
    def detect_anomalies(df: pd.DataFrame, item_number: str, criteria: Dict[str, Tuple[float, float]]) -> pd.DataFrame:
        """
        Detect anomalies in test data based on user-defined boundaries.

        Parameters:
        -----------
        df : pd.DataFrame
            The input test data (from uploaded Excel file)
        item_number : str
            The specific ITEM_NUMBER to analyze (e.g., 'WNPZ001100PF')
        criteria : dict
            Dictionary mapping RESULT_NAME to (lower_bound, upper_bound)
            Example: {'Dim Stab Warp': (-4.75, -2.75)}

        Returns:
        --------
        pd.DataFrame with additional columns:
            - Lower_Bound: Expected lower limit (only for rows with criteria)
            - Upper_Bound: Expected upper limit (only for rows with criteria)
            - IS_OUTLIER: 'ABNORMAL' or 'NORMAL' (defaults to 'NORMAL')

        Logic:
        ------
        1. Filter df to only rows where ITEM_NUMBER == item_number
        2. Initialize all rows as 'NORMAL'
        3. For each row with criteria defined:
           - If RESPONSE < lower_bound OR RESPONSE > upper_bound:
               IS_OUTLIER = 'ABNORMAL'
           - Else: remains 'NORMAL'
        4. Return augmented DataFrame
        """
        # Filter to specific item
        filtered_df = df[df['ITEM_NUMBER'] == item_number].copy()

        # Initialize new columns - everything defaults to NORMAL
        filtered_df['Lower_Bound'] = None
        filtered_df['Upper_Bound'] = None
        filtered_df['IS_OUTLIER'] = 'NORMAL'

        # Process each row
        for idx, row in filtered_df.iterrows():
            result_name = row['RESULT_NAME']

            # Check if this result_name has criteria defined
            if result_name in criteria:
                lower_bound, upper_bound = criteria[result_name]
                filtered_df.at[idx, 'Lower_Bound'] = lower_bound
                filtered_df.at[idx, 'Upper_Bound'] = upper_bound

                # Get response value and check bounds
                try:
                    response = float(row['RESPONSE'])

                    if response < lower_bound or response > upper_bound:
                        filtered_df.at[idx, 'IS_OUTLIER'] = 'ABNORMAL'
                    # else remains NORMAL (already set as default)
                except (ValueError, TypeError):
                    # If RESPONSE is not numeric, keep as NORMAL
                    pass

        return filtered_df

    @staticmethod
    def get_summary_stats(result_df: pd.DataFrame) -> Dict[str, int]:
        """
        Get summary statistics from detection results.

        Parameters:
        -----------
        result_df : pd.DataFrame
            DataFrame returned by detect_anomalies()

        Returns:
        --------
        dict with keys:
            - total_analyzed: Total count of all rows
            - normal_count: Count of NORMAL
            - abnormal_count: Count of ABNORMAL
            - percent_abnormal: Percentage of abnormal out of total
        """
        normal_count = (result_df['IS_OUTLIER'] == 'NORMAL').sum()
        abnormal_count = (result_df['IS_OUTLIER'] == 'ABNORMAL').sum()
        total_analyzed = len(result_df)

        percent_abnormal = (abnormal_count / total_analyzed * 100) if total_analyzed > 0 else 0

        return {
            'total_analyzed': total_analyzed,
            'normal_count': normal_count,
            'abnormal_count': abnormal_count,
            'percent_abnormal': percent_abnormal
        }

    @staticmethod
    def get_affected_test_sessions(result_df: pd.DataFrame) -> pd.DataFrame:
        """
        Get list of TEST_NUMBERs that have at least one anomaly.

        Parameters:
        -----------
        result_df : pd.DataFrame
            DataFrame returned by detect_anomalies()

        Returns:
        --------
        pd.DataFrame with columns:
            - TEST_NUMBER
            - anomaly_count: Count of abnormal measurements
            - affected_result_names: List of RESULT_NAMEs with anomalies
        """
        # Filter to only abnormal rows
        abnormal_df = result_df[result_df['IS_OUTLIER'] == 'ABNORMAL']

        if abnormal_df.empty:
            return pd.DataFrame(columns=['TEST_NUMBER', 'anomaly_count', 'affected_result_names'])

        # Group by TEST_NUMBER
        affected = abnormal_df.groupby('TEST_NUMBER').agg({
            'IS_OUTLIER': 'count',
            'RESULT_NAME': lambda x: ', '.join(x.unique())
        }).reset_index()

        affected.columns = ['TEST_NUMBER', 'anomaly_count', 'affected_result_names']

        return affected.sort_values('anomaly_count', ascending=False)

    @staticmethod
    def get_anomaly_breakdown(result_df: pd.DataFrame) -> pd.DataFrame:
        """
        Get count of anomalies by RESULT_NAME.

        Parameters:
        -----------
        result_df : pd.DataFrame
            DataFrame returned by detect_anomalies()

        Returns:
        --------
        pd.DataFrame with columns:
            - RESULT_NAME
            - anomaly_count
        """
        abnormal_df = result_df[result_df['IS_OUTLIER'] == 'ABNORMAL']

        if abnormal_df.empty:
            return pd.DataFrame(columns=['RESULT_NAME', 'anomaly_count'])

        breakdown = abnormal_df.groupby('RESULT_NAME').size().reset_index(name='anomaly_count')
        return breakdown.sort_values('anomaly_count', ascending=False)
