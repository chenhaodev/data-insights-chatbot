"""Data visualization utilities using Seaborn and Matplotlib."""

import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib.figure import Figure
from typing import Optional, Tuple
import os
import matplotlib.font_manager as fm
import sys

# Global variable to store the selected CJK font
_CJK_FONT = None

def get_cjk_font():
    """Get or detect CJK-compatible font."""
    global _CJK_FONT

    if _CJK_FONT is not None:
        return _CJK_FONT

    # Get list of available fonts
    available_fonts = {f.name for f in fm.fontManager.ttflist}

    # List of CJK-compatible fonts to try (in order of preference)
    # Use partial matching for flexibility
    cjk_font_patterns = [
        ('PingFang', ['PingFang SC', 'PingFang TC', 'PingFang HK']),  # macOS
        ('STHeiti', ['STHeiti', 'Heiti SC', 'Heiti TC']),  # macOS System font
        ('Songti', ['Songti SC', 'Songti TC']),  # macOS
        ('Hiragino Sans GB', ['Hiragino Sans GB']),  # macOS
        ('Microsoft YaHei', ['Microsoft YaHei']),  # Windows
        ('SimHei', ['SimHei']),  # Windows
        ('SimSun', ['SimSun']),  # Windows
        ('Noto Sans CJK', ['Noto Sans CJK SC', 'Noto Sans CJK TC']),  # Linux
        ('WenQuanYi', ['WenQuanYi Zen Hei', 'WenQuanYi Micro Hei']),  # Linux
        ('Arial Unicode MS', ['Arial Unicode MS']),  # Cross-platform fallback
    ]

    # Find first available CJK font
    font_found = False
    selected_font = None

    for pattern, font_names in cjk_font_patterns:
        # Check for exact matches first
        for font_name in font_names:
            if font_name in available_fonts:
                selected_font = font_name
                font_found = True
                break

        # If no exact match, try partial match
        if not font_found:
            for available_font in available_fonts:
                if pattern in available_font:
                    selected_font = available_font
                    font_found = True
                    break

        if font_found:
            break

    # If no CJK font found, use platform-specific fallback
    if not font_found or selected_font is None:
        if sys.platform == 'darwin':
            # macOS: Try AppleGothic or any available system font
            fallback_fonts = ['AppleGothic', 'Apple SD Gothic Neo', 'Arial Unicode MS']
        elif sys.platform == 'win32':
            # Windows
            fallback_fonts = ['Microsoft YaHei', 'SimHei', 'SimSun']
        else:
            # Linux
            fallback_fonts = ['Noto Sans CJK SC', 'WenQuanYi Zen Hei']

        # Find first available fallback
        for font in fallback_fonts:
            if font in available_fonts:
                selected_font = font
                break

    # Cache the result
    _CJK_FONT = selected_font if selected_font else 'DejaVu Sans'
    return _CJK_FONT

def apply_cjk_font():
    """Apply CJK font configuration to current matplotlib settings."""
    cjk_font = get_cjk_font()
    plt.rcParams['font.sans-serif'] = [cjk_font, 'DejaVu Sans', 'Arial']
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['font.family'] = 'sans-serif'

# Configure fonts on module load
apply_cjk_font()

# Set default Seaborn theme
sns.set_theme(style="darkgrid")


def create_distribution_plot(
    df: pd.DataFrame,
    column: str,
    figsize: Tuple[int, int] = (8, 6)
) -> Figure:
    """
    Create distribution plot with histogram and KDE.

    Args:
        df: DataFrame containing the data
        column: Column name to plot
        figsize: Figure size (width, height)

    Returns:
        matplotlib Figure object
    """
    # Apply CJK font configuration
    apply_cjk_font()

    # Filter out NaN values for cleaner distribution
    plot_df = df.dropna(subset=[column])

    # Raise error if insufficient data
    if len(plot_df) < 2:
        raise ValueError(f"Column '{column}' has insufficient valid data (need at least 2 values)")

    fig, ax = plt.subplots(figsize=figsize)

    # Create histogram with KDE overlay
    sns.histplot(
        data=plot_df,
        x=column,
        kde=True,
        ax=ax
    )

    ax.set_title(f"Distribution of {column}")
    ax.set_xlabel(column)
    ax.set_ylabel("Frequency")

    plt.tight_layout()
    return fig


def create_correlation_heatmap(
    corr_matrix: pd.DataFrame,
    figsize: Tuple[int, int] = (10, 8)
) -> Figure:
    """
    Create correlation heatmap.

    Args:
        corr_matrix: Correlation matrix DataFrame
        figsize: Figure size (width, height)

    Returns:
        matplotlib Figure object
    """
    # Apply CJK font configuration
    apply_cjk_font()

    # Filter out columns/rows where all OFF-DIAGONAL correlations are NaN
    # This removes non-numeric columns that couldn't be correlated
    # Create a copy and set diagonal to NaN to check off-diagonal values
    corr_no_diag = corr_matrix.copy()
    np.fill_diagonal(corr_no_diag.values, np.nan)

    # Keep only rows/columns that have at least one valid off-diagonal correlation
    valid_mask = ~corr_no_diag.isna().all(axis=1)
    filtered_corr = corr_matrix.loc[valid_mask, valid_mask]

    # If all correlations are invalid, use original (edge case)
    if filtered_corr.empty:
        filtered_corr = corr_matrix

    fig, ax = plt.subplots(figsize=figsize)

    # Create heatmap with annotations
    sns.heatmap(
        filtered_corr,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        center=0,
        square=True,
        linewidths=1,
        cbar_kws={"shrink": 0.8},
        ax=ax
    )

    ax.set_title("Correlation Heatmap")

    plt.tight_layout()
    return fig


def create_scatter_plot(
    df: pd.DataFrame,
    x: str,
    y: str,
    hue: Optional[str] = None,
    figsize: Tuple[int, int] = (8, 6)
) -> Figure:
    """
    Create scatter plot with optional regression line.

    Args:
        df: DataFrame containing the data
        x: Column name for x-axis
        y: Column name for y-axis
        hue: Optional column for color coding
        figsize: Figure size (width, height)

    Returns:
        matplotlib Figure object
    """
    # Apply CJK font configuration
    apply_cjk_font()

    # Filter out rows where x or y is NaN
    plot_df = df.dropna(subset=[x, y])

    # Raise error if insufficient data
    if len(plot_df) < 2:
        raise ValueError(f"Insufficient valid data for scatter plot of '{x}' vs '{y}' (need at least 2 points)")

    fig, ax = plt.subplots(figsize=figsize)

    # Create scatter plot with regression line
    sns.regplot(
        data=plot_df,
        x=x,
        y=y,
        ax=ax,
        scatter_kws={'alpha': 0.6}
    )

    # Add hue if specified
    if hue:
        sns.scatterplot(
            data=plot_df,
            x=x,
            y=y,
            hue=hue,
            ax=ax,
            alpha=0.6,
            legend='full'
        )

    ax.set_title(f"{y} vs {x}")
    ax.set_xlabel(x)
    ax.set_ylabel(y)

    plt.tight_layout()
    return fig


def create_box_plot(
    df: pd.DataFrame,
    column: str,
    group_by: Optional[str] = None,
    figsize: Tuple[int, int] = (8, 6)
) -> Figure:
    """
    Create box plot for distribution analysis.

    Args:
        df: DataFrame containing the data
        column: Column name to plot
        group_by: Optional column for grouping
        figsize: Figure size (width, height)

    Returns:
        matplotlib Figure object
    """
    # Apply CJK font configuration
    apply_cjk_font()

    # Filter out rows where the target column is NaN
    plot_df = df.dropna(subset=[column])

    # If grouped, also filter out groups with <2 valid values (can't create meaningful box plot)
    if group_by:
        group_counts = plot_df.groupby(group_by)[column].count()
        valid_groups = group_counts[group_counts >= 2].index
        plot_df = plot_df[plot_df[group_by].isin(valid_groups)]

    fig, ax = plt.subplots(figsize=figsize)

    if group_by:
        sns.boxplot(
            data=plot_df,
            x=group_by,
            y=column,
            ax=ax
        )
        ax.set_title(f"{column} by {group_by}")
    else:
        sns.boxplot(
            data=plot_df,
            y=column,
            ax=ax
        )
        ax.set_title(f"Distribution of {column}")

    ax.set_xlabel(group_by if group_by else "")
    ax.set_ylabel(column)

    plt.tight_layout()
    return fig


def create_violin_plot(
    df: pd.DataFrame,
    column: str,
    group_by: Optional[str] = None,
    figsize: Tuple[int, int] = (8, 6)
) -> Figure:
    """
    Create violin plot for distribution analysis.

    Args:
        df: DataFrame containing the data
        column: Column name to plot
        group_by: Optional column for grouping
        figsize: Figure size (width, height)

    Returns:
        matplotlib Figure object
    """
    # Apply CJK font configuration
    apply_cjk_font()

    # Filter out rows where the target column is NaN
    plot_df = df.dropna(subset=[column])

    # If grouped, also filter out groups with <2 valid values
    if group_by:
        group_counts = plot_df.groupby(group_by)[column].count()
        valid_groups = group_counts[group_counts >= 2].index
        plot_df = plot_df[plot_df[group_by].isin(valid_groups)]

    fig, ax = plt.subplots(figsize=figsize)

    if group_by:
        sns.violinplot(
            data=plot_df,
            x=group_by,
            y=column,
            ax=ax
        )
        ax.set_title(f"{column} by {group_by}")
    else:
        sns.violinplot(
            data=plot_df,
            y=column,
            ax=ax
        )
        ax.set_title(f"Distribution of {column}")

    plt.tight_layout()
    return fig


def create_pairplot(
    df: pd.DataFrame,
    columns: Optional[list] = None,
    hue: Optional[str] = None
) -> Figure:
    """
    Create pairwise relationship plots.

    Args:
        df: DataFrame containing the data
        columns: List of columns to include (None = all numeric)
        hue: Optional column for color coding

    Returns:
        matplotlib Figure object from PairGrid
    """
    # Apply CJK font configuration
    apply_cjk_font()

    if columns:
        plot_df = df[columns]
    else:
        plot_df = df.select_dtypes(include=[np.number])

    pairplot = sns.pairplot(plot_df, hue=hue, diag_kind="kde")
    return pairplot.fig


def save_figure(fig: Figure, filename: str, output_dir: str = "temp/charts") -> str:
    """
    Save figure to file.

    Args:
        fig: matplotlib Figure object
        filename: Name for the file (without extension)
        output_dir: Directory to save the file

    Returns:
        str: Full path to the saved file
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Full file path
    filepath = os.path.join(output_dir, f"{filename}.png")

    # Save figure
    fig.savefig(filepath, dpi=300, bbox_inches='tight')

    # Close figure to free memory
    plt.close(fig)

    return filepath
