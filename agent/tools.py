"""Analysis tools for the Data Insights Agent."""

from pydantic_ai import RunContext
from typing import Optional, List, Dict, Any
import asyncio
import pandas as pd
from .dependencies import AgentDependencies
from .settings import load_settings
from utils import statistics, visualization
from utils.html_utils import fix_html_cjk_encoding
from pandasai import Agent as PandasAIAgent
from pandasai.llm import OpenAI as PandasAI_OpenAI
from ydata_profiling import ProfileReport
import os




async def describe_dataset(
    ctx: RunContext[AgentDependencies],
    columns: Optional[List[str]] = None
) -> str:
    """
    Provide descriptive statistics for the dataset.

    Args:
        ctx: Runtime context with dependencies
        columns: Specific columns to analyze (None = all numeric)

    Returns:
        Formatted statistics as string
    """
    df = ctx.deps.get_current_dataframe()
    if df is None:
        return "Error: No dataset uploaded. Please upload a CSV or Excel file first."

    try:
        # Call async statistics function
        stats_results = await statistics.descriptive_statistics(df, columns)

        # Format as readable string
        output = "📊 Descriptive Statistics:\n\n"
        for col, stats_dict in stats_results.items():
            output += f"**{col}:**\n"
            output += f"  • Mean: {stats_dict['mean']:.2f}\n"
            output += f"  • Median: {stats_dict['median']:.2f}\n"
            output += f"  • Std Dev: {stats_dict['std']:.2f}\n"
            output += f"  • Min: {stats_dict['min']:.2f}\n"
            output += f"  • Max: {stats_dict['max']:.2f}\n"
            output += f"  • Q25: {stats_dict['q25']:.2f}, Q75: {stats_dict['q75']:.2f}\n"
            output += f"  • Count: {stats_dict['count']}, Missing: {stats_dict['missing']}\n"
            output += "\n"

        # Track in history
        ctx.deps.add_to_history(
            query=f"describe_dataset({columns})",
            result="success",
            tool_used="describe_dataset"
        )

        return output

    except Exception as e:
        return f"Error calculating statistics: {str(e)}"


async def correlation_analysis_tool(
    ctx: RunContext[AgentDependencies],
    method: str = "pearson",
    columns: Optional[List[str]] = None
) -> str:
    """
    Perform correlation analysis on dataset.

    Args:
        ctx: Runtime context with dependencies
        method: Correlation method ('pearson', 'spearman', 'kendall')
        columns: Specific columns to analyze

    Returns:
        Formatted correlation results
    """
    df = ctx.deps.get_current_dataframe()
    if df is None:
        return "Error: No dataset uploaded."

    try:
        # Calculate correlations
        corr_result = await statistics.correlation_analysis(df, method, columns)

        # Format results
        output = f"📈 Correlation Analysis ({method.capitalize()}):\n\n"

        corr_matrix = corr_result['correlation_matrix']
        cols = corr_result['columns']

        # Find strong correlations (|r| > 0.7)
        strong_corrs = []
        for i, col1 in enumerate(cols):
            for j, col2 in enumerate(cols):
                if i < j:  # Avoid duplicates
                    corr_val = corr_matrix[col1][col2]
                    if abs(corr_val) > 0.7:
                        strong_corrs.append((col1, col2, corr_val))

        if strong_corrs:
            output += "**Strong Correlations (|r| > 0.7):**\n"
            for col1, col2, val in sorted(strong_corrs, key=lambda x: abs(x[2]), reverse=True):
                output += f"  • {col1} ↔ {col2}: {val:.3f}\n"
        else:
            output += "No strong correlations found (|r| > 0.7)\n"

        output += "\n💡 Tip: Use create_visualization with plot_type='heatmap' to see the full correlation matrix."

        ctx.deps.add_to_history(
            query=f"correlation_analysis({method})",
            result="success",
            tool_used="correlation_analysis_tool"
        )

        return output

    except Exception as e:
        return f"Error in correlation analysis: {str(e)}"


async def create_visualization(
    ctx: RunContext[AgentDependencies],
    plot_type: str,
    column: Optional[str] = None,
    x_col: Optional[str] = None,
    y_col: Optional[str] = None,
    group_by: Optional[str] = None
) -> str:
    """
    Create data visualization.

    Args:
        ctx: Runtime context
        plot_type: Type of plot ('distribution', 'scatter', 'box', 'violin', 'heatmap')
        column: Column for single-variable plots
        x_col: X-axis column for scatter plots
        y_col: Y-axis column for scatter plots
        group_by: Grouping column

    Returns:
        Success message with file path
    """
    df = ctx.deps.get_current_dataframe()
    if df is None:
        return "Error: No dataset uploaded."

    try:
        import uuid
        plot_id = str(uuid.uuid4())[:8]

        if plot_type == "distribution":
            if not column:
                return "Error: 'column' parameter required for distribution plot"
            fig = visualization.create_distribution_plot(df, column)
            filename = f"dist_{column}_{plot_id}"

        elif plot_type == "scatter":
            if not x_col or not y_col:
                return "Error: 'x_col' and 'y_col' required for scatter plot"
            fig = visualization.create_scatter_plot(df, x_col, y_col)
            filename = f"scatter_{x_col}_{y_col}_{plot_id}"

        elif plot_type == "box":
            if not column:
                return "Error: 'column' parameter required for box plot"
            fig = visualization.create_box_plot(df, column, group_by)
            filename = f"box_{column}_{plot_id}"

        elif plot_type == "violin":
            if not column:
                return "Error: 'column' parameter required for violin plot"
            fig = visualization.create_violin_plot(df, column, group_by)
            filename = f"violin_{column}_{plot_id}"

        elif plot_type == "heatmap":
            # Get correlation matrix first
            corr_result = await statistics.correlation_analysis(df, "pearson")
            corr_df = corr_result['dataframe']
            fig = visualization.create_correlation_heatmap(corr_df)
            filename = f"heatmap_{plot_id}"

        else:
            return f"Error: Unknown plot type '{plot_type}'. Use: distribution, scatter, box, violin, or heatmap"

        # Save figure
        filepath = visualization.save_figure(fig, filename)

        # Convert to relative path if absolute
        if os.path.isabs(filepath):
            try:
                filepath_rel = os.path.relpath(filepath)
            except ValueError:
                filepath_rel = filepath
        else:
            filepath_rel = filepath

        ctx.deps.add_to_history(
            query=f"create_visualization({plot_type})",
            result="success",
            tool_used="create_visualization"
        )

        return f"✅ Visualization created successfully!\nSaved to: {filepath_rel}\n\n💡 Chart file: {filepath_rel}"

    except Exception as e:
        return f"Error creating visualization: {str(e)}"


async def perform_statistical_test(
    ctx: RunContext[AgentDependencies],
    test_type: str,
    column1: str,
    column2: Optional[str] = None,
    group_column: Optional[str] = None
) -> str:
    """
    Perform statistical hypothesis test.

    Args:
        ctx: Runtime context
        test_type: Test type ('ttest', 'anova')
        column1: First column or dependent variable
        column2: Second column (for t-test)
        group_column: Grouping column (for grouped tests)

    Returns:
        Formatted test results
    """
    df = ctx.deps.get_current_dataframe()
    if df is None:
        return "Error: No dataset uploaded."

    try:
        if test_type == "ttest":
            if group_column:
                # Independent t-test by group
                groups = df[group_column].unique()
                if len(groups) != 2:
                    return f"Error: T-test requires exactly 2 groups. Found {len(groups)} groups in '{group_column}'"

                group1_data = df[df[group_column] == groups[0]][column1]
                group2_data = df[df[group_column] == groups[1]][column1]

                result = await statistics.t_test_analysis(group1_data, group2_data)

                output = f"📊 Independent T-Test Results:\n\n"
                output += f"**Comparing:** {column1} between {groups[0]} and {groups[1]}\n\n"
                output += f"  • Group 1 ({groups[0]}): mean = {result['group1_mean']:.2f}, std = {result['group1_std']:.2f}\n"
                output += f"  • Group 2 ({groups[1]}): mean = {result['group2_mean']:.2f}, std = {result['group2_std']:.2f}\n"
                output += f"  • T-statistic: {result['t_statistic']:.4f}\n"
                output += f"  • P-value: {result['p_value']:.4f}\n"
                output += f"  • Degrees of freedom: {result['degrees_of_freedom']}\n\n"
                output += f"**Interpretation:** {result['interpretation']}\n"

                return output

            elif column2:
                # Paired or independent t-test between two columns
                result = await statistics.t_test_analysis(df[column1], df[column2])

                output = f"📊 T-Test Results:\n\n"
                output += f"**Comparing:** {column1} vs {column2}\n\n"
                output += f"  • Column 1 mean: {result['group1_mean']:.2f}\n"
                output += f"  • Column 2 mean: {result['group2_mean']:.2f}\n"
                output += f"  • T-statistic: {result['t_statistic']:.4f}\n"
                output += f"  • P-value: {result['p_value']:.4f}\n\n"
                output += f"**Interpretation:** {result['interpretation']}\n"

                return output
            else:
                return "Error: T-test requires either 'column2' or 'group_column'"

        elif test_type == "anova":
            if not group_column:
                return "Error: ANOVA requires 'group_column' parameter"

            groups = df[group_column].unique()
            group_data = [df[df[group_column] == g][column1] for g in groups]

            result = await statistics.anova_test(group_data)

            output = f"📊 One-Way ANOVA Results:\n\n"
            output += f"**Analyzing:** {column1} across {len(groups)} groups in {group_column}\n\n"
            output += f"  • F-statistic: {result['f_statistic']:.4f}\n"
            output += f"  • P-value: {result['p_value']:.4f}\n"
            output += f"  • Number of groups: {result['num_groups']}\n\n"

            output += "**Group Means:**\n"
            for i, (group, mean) in enumerate(zip(groups, result['group_means'])):
                output += f"  • {group}: {mean:.2f}\n"

            output += f"\n**Interpretation:** {result['interpretation']}\n"

            return output

        else:
            return f"Error: Unknown test type '{test_type}'. Use: 'ttest' or 'anova'"

        ctx.deps.add_to_history(
            query=f"perform_statistical_test({test_type})",
            result="success",
            tool_used="perform_statistical_test"
        )

    except Exception as e:
        return f"Error performing statistical test: {str(e)}"


async def query_data_nl(
    ctx: RunContext[AgentDependencies],
    query: str
) -> str:
    """
    Execute natural language query using PandasAI.

    Args:
        ctx: Runtime context
        query: Natural language query

    Returns:
        Query results
    """
    df = ctx.deps.get_current_dataframe()
    if df is None:
        return "Error: No dataset uploaded."

    try:
        settings = load_settings()

        # Configure PandasAI with DeepSeek
        # CRITICAL: Use PandasAI's OpenAI wrapper
        llm = PandasAI_OpenAI(
            api_token=settings.deepseek_api_key,
            model=settings.deepseek_model,
            api_base=settings.deepseek_base_url
        )

        # Sample large dataframes
        if len(df) > settings.max_dataframe_rows:
            df_sample = df.sample(settings.max_dataframe_rows)
            output_note = f"\n\n⚠️ Note: Using sample of {settings.max_dataframe_rows:,} rows (total: {len(df):,})\n\n"
        else:
            df_sample = df
            output_note = ""

        # Create PandasAI agent
        pandas_agent = PandasAIAgent([df_sample], config={"llm": llm, "verbose": False})

        # Execute query in thread pool (PandasAI is blocking)
        result = await asyncio.to_thread(pandas_agent.chat, query)

        # Format result
        if isinstance(result, pd.DataFrame):
            formatted_result = f"Query result:\n```\n{result.to_string()}\n```"
        else:
            formatted_result = f"Query result: {result}"

        ctx.deps.add_to_history(
            query=f"query_data_nl: {query}",
            result="success",
            tool_used="query_data_nl"
        )

        return output_note + formatted_result

    except Exception as e:
        return f"Error executing natural language query: {str(e)}"


async def time_series_analysis(
    ctx: RunContext[AgentDependencies],
    column: str,
    freq: int = 12
) -> str:
    """
    Perform time series decomposition.

    Args:
        ctx: Runtime context
        column: Time series column
        freq: Seasonal frequency (e.g., 12 for monthly with yearly seasonality)

    Returns:
        Analysis results
    """
    df = ctx.deps.get_current_dataframe()
    if df is None:
        return "Error: No dataset uploaded."

    try:
        if column not in df.columns:
            return f"Error: Column '{column}' not found in dataset"

        series = df[column]

        # Validate series is numeric
        if not pd.api.types.is_numeric_dtype(series):
            return f"Error: Column '{column}' must be numeric for time series analysis"

        # Perform decomposition
        result = await statistics.time_series_decomposition(series, freq)

        output = f"📈 Time Series Decomposition: {column}\n\n"
        output += f"**Model:** {result['model'].capitalize()}\n"
        output += f"**Frequency:** {result['frequency']}\n\n"

        output += "✅ Decomposition complete!\n"
        output += "Components extracted: Trend, Seasonal, Residual\n\n"

        output += "💡 Tip: The decomposition helps identify:\n"
        output += "  • Trend: Long-term direction\n"
        output += "  • Seasonal: Repeating patterns\n"
        output += "  • Residual: Random fluctuations\n"

        ctx.deps.add_to_history(
            query=f"time_series_analysis({column})",
            result="success",
            tool_used="time_series_analysis"
        )

        return output

    except Exception as e:
        return f"Error in time series analysis: {str(e)}"


async def generate_profile_report(
    ctx: RunContext[AgentDependencies]
) -> str:
    """
    Generate comprehensive EDA report using ydata-profiling.

    Args:
        ctx: Runtime context

    Returns:
        Success message with file path
    """
    df = ctx.deps.get_current_dataframe()
    if df is None:
        return "Error: No dataset uploaded."

    try:
        # Create output directory
        output_dir = "temp/reports"
        os.makedirs(output_dir, exist_ok=True)

        filename = f"{ctx.deps.current_df_name.replace('.', '_')}_profile.html"
        filepath = os.path.join(output_dir, filename)

        # Generate profile report in thread pool (blocking operation)
        def _generate():
            # Configure ydata-profiling with UTF-8 support
            profile = ProfileReport(
                df,
                title=f"Profile Report: {ctx.deps.current_df_name}",
                minimal=True,
                progress_bar=False
            )
            profile.to_file(filepath)

            # Fix font encoding for Chinese and other Unicode characters
            fix_html_cjk_encoding(filepath)

        await asyncio.to_thread(_generate)

        ctx.deps.add_to_history(
            query="generate_profile_report",
            result="success",
            tool_used="generate_profile_report"
        )

        return f"✅ Comprehensive EDA report generated!\n\nSaved to: {filepath}\n\nOpen this HTML file in your browser to explore detailed analysis including:\n  • Variable types and distributions\n  • Correlations\n  • Missing values\n  • Duplicate rows\n  • And much more!"

    except Exception as e:
        return f"Error generating profile report: {str(e)}"
