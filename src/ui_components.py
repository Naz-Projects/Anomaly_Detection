"""Reusable UI components for the Streamlit app."""

import streamlit as st
import pandas as pd
from src.detector import AnomalyDetector
from src.export import create_formatted_excel


def display_results(result_df: pd.DataFrame):
    """
    Display analysis results with metrics and tables.

    Parameters:
    -----------
    result_df : pd.DataFrame
        DataFrame containing analysis results with IS_OUTLIER column
    """
    st.divider()
    st.subheader("Analysis Results")

    # Get summary statistics
    stats = AnomalyDetector.get_summary_stats(result_df)

    # Display summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Analyzed", stats['total_analyzed'])
    with col2:
        st.metric("Normal", stats['normal_count'])
    with col3:
        st.metric("Abnormal", stats['abnormal_count'])

    # Check if there are anomalies
    abnormal_df = result_df[result_df['IS_OUTLIER'] == 'ABNORMAL'].copy()

    if not abnormal_df.empty:
        # Detailed results table - only show rows with anomalies
        st.markdown("### Detailed Anomaly Records")

        # Select relevant columns for display
        display_cols = ['ITEM_NUMBER', 'TEST_NUMBER', 'RESULT_NAME', 'RESPONSE', 'Lower_Bound', 'Upper_Bound', 'IS_OUTLIER']
        display_df = abnormal_df[display_cols]

        st.dataframe(display_df, width='stretch', hide_index=True)

        # Download button for full results
        st.markdown("### Export Results")

        # Create formatted Excel file
        excel_file = create_formatted_excel(result_df)

        st.download_button(
            label="Download Results (Excel with highlighting)",
            data=excel_file,
            file_name="anomaly_detection_results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width='content'
        )
    else:
        st.success("No anomalies detected! All measurements are within acceptable ranges.")

    # Clear results button
    if st.button("Clear Results"):
        st.session_state.analysis_results = None
        st.rerun()


def display_file_stats(stats: dict, filename: str):
    """
    Display basic statistics about uploaded file.

    Parameters:
    -----------
    stats : dict
        Dictionary with total_rows, total_items, total_tests
    filename : str
        Name of the uploaded file
    """
    st.success(f"File loaded: {filename}")
    metric_col1, metric_col2, metric_col3 = st.columns(3)
    with metric_col1:
        st.metric("Total Rows", f"{stats['total_rows']:,}")
    with metric_col2:
        st.metric("Products", stats['total_items'])
    with metric_col3:
        st.metric("Tests", stats['total_tests'])


def display_filter_row(i: int, filter_item: dict, result_names: list, df: pd.DataFrame, selected_items: list, remove_callback):
    """
    Display a single filter row with test type selector and bounds.

    Parameters:
    -----------
    i : int
        Filter index
    filter_item : dict
        Filter configuration with result_name, lower_bound, upper_bound
    result_names : list
        Available result names to choose from
    df : pd.DataFrame
        The data dataframe
    selected_items : list
        Selected product items
    remove_callback : function
        Function to call when remove button is clicked
    """
    from src.data_loader import DataLoader

    col1, col2, col3, col4 = st.columns([3, 1.5, 1.5, 0.5])

    with col1:
        # Store previous selection to detect changes
        prev_result_name = filter_item.get('result_name')

        selected_result = st.selectbox(
            "Test Type",
            options=result_names,
            key=f"result_name_{i}",
            index=result_names.index(filter_item['result_name']) if filter_item['result_name'] in result_names else 0
        )

        # If result name changed, recalculate IQR bounds and force rerun
        if selected_result != prev_result_name:
            st.session_state.filters[i]['result_name'] = selected_result

            # Calculate IQR bounds for the new result name
            iqr_lower, iqr_upper = DataLoader.calculate_iqr_bounds(df, selected_items, selected_result)
            if iqr_lower is not None and iqr_upper is not None:
                st.session_state.filters[i]['lower_bound'] = iqr_lower
                st.session_state.filters[i]['upper_bound'] = iqr_upper

            # Force rerun to update input boxes
            st.rerun()

        # Update result name in session state
        st.session_state.filters[i]['result_name'] = selected_result

        # If bounds are still default (0.0), calculate IQR bounds
        if filter_item['lower_bound'] == 0.0 and filter_item['upper_bound'] == 0.0:
            iqr_lower, iqr_upper = DataLoader.calculate_iqr_bounds(df, selected_items, selected_result)
            if iqr_lower is not None and iqr_upper is not None:
                st.session_state.filters[i]['lower_bound'] = iqr_lower
                st.session_state.filters[i]['upper_bound'] = iqr_upper

        # Show actual data range and IQR bounds
        all_min_vals = []
        all_max_vals = []
        for item in selected_items:
            min_val, max_val = DataLoader.get_value_range(df, item, selected_result)
            if min_val is not None:
                all_min_vals.append(min_val)
            if max_val is not None:
                all_max_vals.append(max_val)

        if all_min_vals and all_max_vals:
            overall_min = min(all_min_vals)
            overall_max = max(all_max_vals)

            # Get quartile bounds for display
            q1, q3 = DataLoader.calculate_iqr_bounds(df, selected_items, selected_result)
            if q1 is not None and q3 is not None:
                st.caption(f"Data range: {overall_min:.3f} to {overall_max:.3f} | Quartile bounds (Q1-Q3): {q1:.3f} to {q3:.3f}")
            else:
                st.caption(f"Data range: {overall_min:.3f} to {overall_max:.3f}")

    with col2:
        # Use session state value directly to ensure it updates
        lower = st.number_input(
            "Lower",
            value=st.session_state.filters[i]['lower_bound'],
            format="%.3f",
            key=f"lower_{i}_{selected_result}"  # Include result_name in key to force refresh
        )
        st.session_state.filters[i]['lower_bound'] = lower

    with col3:
        # Use session state value directly to ensure it updates
        upper = st.number_input(
            "Upper",
            value=st.session_state.filters[i]['upper_bound'],
            format="%.3f",
            key=f"upper_{i}_{selected_result}"  # Include result_name in key to force refresh
        )
        st.session_state.filters[i]['upper_bound'] = upper

    with col4:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("✕", key=f"remove_{i}", help="Remove"):
            remove_callback(i)
            st.rerun()
