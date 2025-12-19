"""
Anomaly Detector - Manufacturing Test Results Analysis
A Streamlit application for detecting anomalies in test data.
"""

import streamlit as st
import pandas as pd

from src.data_loader import DataLoader
from src.detector import AnomalyDetector
from src.utils import add_filter, remove_filter, initialize_session_state
from src.ui_components import display_results, display_file_stats, display_filter_row

# Page configuration
st.set_page_config(
    page_title="Anomaly Detector",
    page_icon=":mag:",
    layout="wide"
)

# Initialize session state
initialize_session_state()


def main():
    """Main application entry point."""

    st.title("Anomaly Detector")
    st.caption("Automated detection of abnormal test results")
    st.divider()

    # File upload section
    st.subheader("Upload Test Results")

    col_upload, col_stats = st.columns([1, 2])

    with col_upload:
        uploaded_file = st.file_uploader(
            "Choose an Excel file",
            type=['xlsx', 'xls'],
            help="Upload your manufacturing test results in Excel format"
        )

    if uploaded_file is not None:
        # Load the file
        with st.spinner("Loading file..."):
            df, error = DataLoader.load_excel(uploaded_file)

        if error:
            st.error(f":x: {error}")
            return

        # Store in session state
        st.session_state.df = df

        # Display basic statistics
        with col_stats:
            stats = DataLoader.get_basic_stats(df)
            display_file_stats(stats, uploaded_file.name)

        # Data preview
        with st.expander("Preview Data", expanded=False):
            st.dataframe(df.head(10), width='stretch')

        st.divider()

        # Product selection
        st.markdown("**Select Products**")
        col1, col2 = st.columns([2, 3])
        with col1:
            item_numbers = DataLoader.get_item_numbers(df)
            selected_items = st.multiselect(
                "Choose ITEM_NUMBER(s)",
                options=item_numbers,
                default=item_numbers,
                help="Select one or more products to analyze",
                label_visibility="collapsed"
            )

        if selected_items:
            st.session_state.selected_item = selected_items

            # Show test count
            total_tests = sum([DataLoader.get_test_count(df, item) for item in selected_items])
            with col2:
                st.markdown(f"<br>**{len(selected_items)}** product(s), **{total_tests}** test sessions", unsafe_allow_html=True)

            st.divider()

            # Configure detection criteria
            configure_filters_section(df, selected_items)

            # Display results if available
            if st.session_state.analysis_results is not None:
                display_results(st.session_state.analysis_results)

    else:
        st.info(":point_up: Please upload an Excel file to get started")


def configure_filters_section(df: pd.DataFrame, selected_items: list):
    """
    Display the filters configuration section.

    Parameters:
    -----------
    df : pd.DataFrame
        The input dataframe
    selected_items : list
        List of selected ITEM_NUMBERs
    """
    st.subheader("Detection Criteria")
    st.caption("Add filters to detect anomalies. Bounds are auto-calculated using quartiles (Q1-Q3) and can be adjusted manually.")

    # Get analyzable result names across all selected products
    result_names = []
    for item in selected_items:
        item_results = DataLoader.get_analyzable_result_names(df, item)
        result_names.extend(item_results)
    result_names = sorted(list(set(result_names)))

    if not result_names:
        st.warning(":warning: No analyzable test types found for selected products")
        return

    st.caption(f"{len(result_names)} test types available for analysis")

    # Display existing filters
    if st.session_state.filters:
        for i, filter_item in enumerate(st.session_state.filters):
            display_filter_row(i, filter_item, result_names, df, selected_items, remove_filter)

    # Buttons
    st.markdown("")
    btn_col1, btn_col2 = st.columns([1, 3])

    with btn_col1:
        if st.button("➕ Add Filter", width='stretch'):
            add_filter()
            st.rerun()

    with btn_col2:
        if st.button("▶ Run Analysis", type="primary", width='stretch'):
            run_analysis(df, selected_items)


def run_analysis(df: pd.DataFrame, selected_items: list):
    """
    Execute the anomaly detection analysis.

    Parameters:
    -----------
    df : pd.DataFrame
        The input dataframe
    selected_items : list
        List of selected ITEM_NUMBERs to analyze
    """
    if not st.session_state.filters:
        st.warning("Please add at least one filter to run the analysis")
        return

    # Build criteria dictionary from filters
    criteria = {
        f['result_name']: (f['lower_bound'], f['upper_bound'])
        for f in st.session_state.filters
        if f['result_name'] is not None
    }

    # Run anomaly detection for all selected products
    with st.spinner("Analyzing data..."):
        all_results = []
        for item in selected_items:
            result_df = AnomalyDetector.detect_anomalies(df, item, criteria)
            all_results.append(result_df)

        # Combine all results
        combined_results = pd.concat(all_results, ignore_index=True)
        st.session_state.analysis_results = combined_results

    st.success(f"Analysis complete! Processed {len(selected_items)} product(s) with {len(st.session_state.filters)} filter(s)")
    st.rerun()


if __name__ == "__main__":
    main()
