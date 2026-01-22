"""Main Streamlit application for Data Insights Chatbot."""

import streamlit as st
import pandas as pd
import asyncio
from io import BytesIO
import matplotlib.pyplot as plt
import os

# Add current directory to path for imports
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.agent import data_insights_agent
from agent.dependencies import AgentDependencies
from agent.settings import load_settings
from utils.data_loader import load_csv_or_excel, validate_dataframe


# Page configuration
st.set_page_config(
    page_title="Data Insights Chatbot",
    page_icon="📊",
    layout="wide"
)

# Load settings (with error handling)
try:
    settings = load_settings()
except ValueError as e:
    st.error(f"⚠️ Configuration Error:\n\n{str(e)}")
    st.stop()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent_deps" not in st.session_state:
    st.session_state.agent_deps = AgentDependencies()

# Sidebar: File upload and dataset management
with st.sidebar:
    st.header("📁 Data Upload")

    uploaded_file = st.file_uploader(
        "Upload CSV or Excel file",
        type=["csv", "xlsx", "xls"],
        help="Upload your dataset to start analyzing"
    )

    if uploaded_file is not None:
        try:
            # Read file data
            bytes_data = uploaded_file.read()

            # Load dataframe
            df, info = load_csv_or_excel(bytes_data, uploaded_file.name)

            # Validate
            warnings = validate_dataframe(df)
            if warnings:
                for warning in warnings:
                    st.warning(warning)

            # Store in session state
            file_name = uploaded_file.name
            st.session_state.agent_deps.set_dataframe(file_name, df)

            # Display info
            st.success(f"✅ Loaded: {file_name}")
            st.metric("Rows", f"{info.rows:,}")
            st.metric("Columns", info.columns)
            st.write(f"**Memory:** {info.memory_usage}")

            if info.has_nulls:
                st.info("ℹ️ Dataset contains missing values")

            # Preview
            with st.expander("📋 Data Preview"):
                st.dataframe(df.head(10), width="stretch")

            # Column info
            with st.expander("📝 Column Information"):
                col_types = pd.DataFrame({
                    'Column': df.columns,
                    'Type': [str(dtype) for dtype in df.dtypes],
                    'Non-Null': [df[col].count() for col in df.columns],
                    'Unique': [df[col].nunique() for col in df.columns]
                })
                st.dataframe(col_types, width="stretch")

        except Exception as e:
            st.error(f"Error loading file: {str(e)}")

    # Settings
    st.divider()
    st.header("⚙️ Settings")

    chart_style = st.selectbox(
        "Chart Style",
        ["darkgrid", "whitegrid", "dark", "white", "ticks"],
        index=0
    )
    st.session_state.agent_deps.chart_style = chart_style

    # About
    st.divider()
    st.caption("**Data Insights Chatbot**")
    st.caption("Powered by DeepSeek, PandasAI & Seaborn")
    st.caption("v1.0.0")


# Main area: Chat interface
st.title("📊 Data Insights Chatbot")
st.caption("Ask questions about your data in natural language")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

        # Display charts if present in temp directory
        if "chart_path" in message:
            if os.path.exists(message["chart_path"]):
                st.image(message["chart_path"])

# Chat input
if prompt := st.chat_input("Ask a question about your data..."):
    # Check if data is loaded
    if st.session_state.agent_deps.get_current_dataframe() is None:
        st.error("⚠️ Please upload a dataset first!")
    else:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.write(prompt)

        # Get agent response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                try:
                    # Run agent (async)
                    result = asyncio.run(
                        data_insights_agent.run(
                            prompt,
                            deps=st.session_state.agent_deps
                        )
                    )

                    response = result.output

                    # Display response
                    st.write(response)

                    # Check if visualization was created (look for file path in response)
                    chart_path = None
                    import re
                    import glob
                    from datetime import datetime, timedelta

                    # Strategy 1: Extract file path from response
                    if "Saved to:" in response or "temp/charts/" in response:
                        # Match file path patterns
                        # Pattern 1: Relative path "temp/charts/filename.png"
                        match = re.search(r'(temp/charts/[\w\-_]+\.png)', response)
                        if match:
                            rel_path = match.group(1)
                            chart_path = os.path.abspath(rel_path)
                        else:
                            # Pattern 2: Absolute path "/path/to/temp/charts/filename.png"
                            match = re.search(r'(/[^\s]+temp/charts/[\w\-_]+\.png|[A-Za-z]:[^\s]+temp/charts/[\w\-_]+\.png)', response)
                            if match:
                                chart_path = match.group(0)

                    # Strategy 2: Fallback - if response mentions visualization but no path found,
                    # check for recently created files (within last 10 seconds)
                    if not chart_path and any(keyword in response.lower() for keyword in ["visualization", "heatmap", "chart", "plot", "created", "generated"]):
                        charts_dir = "temp/charts"
                        if os.path.exists(charts_dir):
                            # Get all png files sorted by modification time (newest first)
                            chart_files = glob.glob(os.path.join(charts_dir, "*.png"))
                            if chart_files:
                                newest_file = max(chart_files, key=os.path.getmtime)
                                # Check if file was created in the last 10 seconds
                                file_time = datetime.fromtimestamp(os.path.getmtime(newest_file))
                                if datetime.now() - file_time < timedelta(seconds=10):
                                    chart_path = newest_file

                    # Display the chart if file exists
                    if chart_path and os.path.exists(chart_path):
                        st.image(chart_path, width="stretch", caption="Generated visualization")
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": response,
                            "chart_path": chart_path
                        })
                    elif chart_path:
                        st.warning(f"⚠️ Chart file created but not found at: {chart_path}")
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": response
                        })
                    else:
                        # Store in history (no chart)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": response
                        })

                except Exception as e:
                    error_msg = f"❌ Error: {str(e)}"
                    st.error(error_msg)

                    # Provide helpful suggestions
                    if "api" in str(e).lower() or "key" in str(e).lower():
                        st.info("💡 Make sure your DEEPSEEK_API_KEY is set in the .env file")
                    elif "column" in str(e).lower():
                        st.info("💡 Check that column names match exactly (case-sensitive)")

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })

# Help section
with st.expander("💡 How to use"):
    st.markdown("""
    **Getting Started:**
    1. Upload a CSV or Excel file using the sidebar
    2. Ask questions about your data in natural language
    3. View statistics, visualizations, and insights

    **Example Questions:**
    - "What are the descriptive statistics for all numeric columns?"
    - "Show me a correlation heatmap"
    - "Create a scatter plot of age vs salary"
    - "Perform a t-test comparing salary between group A and B"
    - "What is the average salary by department?" (uses PandasAI)
    - "Show me the distribution of age"
    - "Analyze the time series data with frequency 12"
    - "Generate a comprehensive profile report"

    **Available Analysis:**
    - Descriptive statistics
    - Correlation analysis
    - Statistical tests (t-test, ANOVA)
    - Data visualizations (scatter, box, violin, heatmap, distribution)
    - Natural language queries
    - Time series analysis
    - Automated EDA reports
    """)

# Footer
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    if st.session_state.agent_deps.get_current_dataframe() is not None:
        df = st.session_state.agent_deps.get_current_dataframe()
        st.metric("Dataset Rows", f"{len(df):,}")
with col2:
    st.metric("Chat Messages", len(st.session_state.messages))
with col3:
    st.metric("Analyses Run", len(st.session_state.agent_deps.analysis_history))
