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
from pydantic_ai.messages import ModelMessage, ModelRequest, ModelResponse, UserPromptPart, TextPart


def convert_to_model_messages(st_messages: list) -> list[ModelMessage]:
    """Convert Streamlit message history to PydanticAI ModelMessage format.

    Args:
        st_messages: List of dicts with 'role' and 'content' keys from Streamlit session state

    Returns:
        List of ModelMessage objects (ModelRequest/ModelResponse) for PydanticAI
    """
    model_messages = []
    for msg in st_messages:
        if msg["role"] == "user":
            model_messages.append(ModelRequest(parts=[UserPromptPart(content=msg["content"])]))
        elif msg["role"] == "assistant":
            model_messages.append(ModelResponse(parts=[TextPart(content=msg["content"])]))
    return model_messages


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

        # Display charts if present (handle both old single chart_path and new multiple chart_paths)
        if "chart_paths" in message:
            # New format: multiple charts
            chart_paths = message["chart_paths"]
            if chart_paths:
                st.markdown("---")
                st.markdown("### 📊 Generated Visualizations")
                if len(chart_paths) == 1:
                    if os.path.exists(chart_paths[0]):
                        st.image(chart_paths[0], use_container_width=True)
                elif len(chart_paths) == 2:
                    col1, col2 = st.columns(2)
                    for idx, col in enumerate([col1, col2]):
                        if os.path.exists(chart_paths[idx]):
                            with col:
                                st.image(chart_paths[idx], use_container_width=True)
                else:
                    for i in range(0, len(chart_paths), 2):
                        cols = st.columns(2)
                        for j, col in enumerate(cols):
                            idx = i + j
                            if idx < len(chart_paths) and os.path.exists(chart_paths[idx]):
                                with col:
                                    st.image(chart_paths[idx], use_container_width=True)
        elif "chart_path" in message:
            # Old format: single chart (for backward compatibility)
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
                    # Track existing charts before agent run
                    import glob
                    charts_dir = "temp/charts"
                    existing_charts = set()
                    if os.path.exists(charts_dir):
                        existing_charts = set(glob.glob(os.path.join(charts_dir, "*.png")))

                    # Convert conversation history to PydanticAI format
                    # Exclude the current message (last one) since it's passed as 'prompt'
                    message_history = convert_to_model_messages(st.session_state.messages[:-1])

                    # Run agent (async) with full conversation context
                    result = asyncio.run(
                        data_insights_agent.run(
                            prompt,
                            deps=st.session_state.agent_deps,
                            message_history=message_history
                        )
                    )

                    response = result.output

                    # Check if visualizations were created BEFORE displaying response
                    # This ensures we capture all charts created during the agent run
                    chart_paths = []
                    import re
                    from datetime import datetime, timedelta

                    # Strategy 1: Compare before/after to find NEW charts created during this run
                    if os.path.exists(charts_dir):
                        current_charts = set(glob.glob(os.path.join(charts_dir, "*.png")))
                        new_charts = current_charts - existing_charts

                        if new_charts:
                            # Sort by modification time (newest first)
                            new_charts_with_time = [
                                (f, os.path.getmtime(f)) for f in new_charts
                            ]
                            new_charts_with_time.sort(key=lambda x: x[1], reverse=True)
                            chart_paths = [f for f, _ in new_charts_with_time]

                    # Strategy 2: Extract file paths from response text (as backup)
                    if not chart_paths and "temp/charts/" in response:
                        # Pattern: Find all relative paths "temp/charts/filename.png"
                        matches = re.findall(r'temp/charts/[^\s]+\.png', response)
                        for match in matches:
                            try:
                                chart_path = os.path.abspath(match)
                                if os.path.exists(chart_path) and chart_path not in chart_paths:
                                    chart_paths.append(chart_path)
                            except:
                                pass

                    # Strategy 3: Fallback - check for very recent files if response mentions visualizations
                    if not chart_paths and any(keyword in response.lower() for keyword in ["visualization", "visualisation", "heatmap", "chart", "plot", "created", "generated", "distribution", "scatter", "box plot", "violin"]):
                        if os.path.exists(charts_dir):
                            chart_files = glob.glob(os.path.join(charts_dir, "*.png"))
                            if chart_files:
                                # Get files created in the last 30 seconds
                                current_time = datetime.now()
                                recent_files = []
                                for chart_file in chart_files:
                                    file_time = datetime.fromtimestamp(os.path.getmtime(chart_file))
                                    if current_time - file_time < timedelta(seconds=30):
                                        recent_files.append((chart_file, file_time))

                                # Sort by creation time (newest first)
                                recent_files.sort(key=lambda x: x[1], reverse=True)
                                chart_paths = [f for f, _ in recent_files]

                    # Display response
                    st.write(response)

                    # Debug info to help troubleshoot
                    if chart_paths:
                        st.info(f"🔍 Detected {len(chart_paths)} visualization(s)")
                    elif any(keyword in response.lower() for keyword in ["plot", "chart", "visualization"]):
                        st.warning("⚠️ Response mentions visualizations but none were detected. This might be a detection issue.")

                    # Display all charts if any exist
                    if chart_paths:
                        # Remove duplicates while preserving order
                        chart_paths = list(dict.fromkeys(chart_paths))

                        st.markdown("---")
                        st.markdown("### 📊 Generated Visualizations")

                        # Display images in columns if multiple, or single if one
                        if len(chart_paths) == 1:
                            st.image(chart_paths[0], use_container_width=True, caption="Generated visualization")
                        elif len(chart_paths) == 2:
                            col1, col2 = st.columns(2)
                            with col1:
                                st.image(chart_paths[0], use_container_width=True, caption=f"Visualization 1")
                            with col2:
                                st.image(chart_paths[1], use_container_width=True, caption=f"Visualization 2")
                        else:
                            # For 3+ images, display in rows of 2
                            for i in range(0, len(chart_paths), 2):
                                cols = st.columns(2)
                                for j, col in enumerate(cols):
                                    idx = i + j
                                    if idx < len(chart_paths):
                                        with col:
                                            st.image(chart_paths[idx], use_container_width=True, caption=f"Visualization {idx + 1}")

                        # Store message with all chart paths
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": response,
                            "chart_paths": chart_paths  # Store as list
                        })
                    else:
                        # Store in history (no charts)
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
