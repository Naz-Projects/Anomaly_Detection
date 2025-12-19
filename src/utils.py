"""Utility functions for session state management."""

import streamlit as st


def add_filter():
    """Add a new empty filter to the session state."""
    st.session_state.filters.append({
        'result_name': None,
        'lower_bound': 0.0,
        'upper_bound': 0.0
    })


def remove_filter(index: int):
    """
    Remove a filter at the specified index.

    Parameters:
    -----------
    index : int
        Index of the filter to remove
    """
    st.session_state.filters.pop(index)


def initialize_session_state():
    """Initialize all session state variables."""
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'selected_item' not in st.session_state:
        st.session_state.selected_item = None
    if 'filters' not in st.session_state:
        st.session_state.filters = []
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
