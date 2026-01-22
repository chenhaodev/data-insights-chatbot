"""Data visualization utilities using Seaborn and Matplotlib."""

import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib.figure import Figure
from typing import Optional, Tuple
import os
import matplotlib.font_manager as fm

# Configure matplotlib to support CJK (Chinese, Japanese, Korean) fonts
# Try to find and use system CJK fonts
def configure_cjk_fonts():
    """Configure matplotlib to use CJK-compatible fonts."""
    # List of CJK-compatible fonts to try (in order of preference)
    cjk_fonts = [
        'PingFang SC',  # macOS Simplified Chinese
        'PingFang TC',  # macOS Traditional Chinese
        'Hiragino Sans GB',  # macOS Chinese
        'Microsoft YaHei',  # Windows Chinese
        'SimHei',  # Windows Chinese
        'SimSun',  # Windows Chinese
        'Noto Sans CJK SC',  # Linux Chinese Simplified
        'Noto Sans CJK TC',  # Linux Chinese Traditional
        'Arial Unicode MS',  # Cross-platform fallback
    ]

    # Get list of available fonts
    available_fonts = [f.name for f in fm.fontManager.ttflist]

    # Find first available CJK font
    for font in cjk_fonts:
        if font in available_fonts:
            plt.rcParams['font.sans-serif'] = [font, 'DejaVu Sans']
            plt.rcParams['axes.unicode_minus'] = False  # Fix minus sign display
            return

    # Fallback: use default sans-serif with unicode support
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial']
    plt.rcParams['axes.unicode_minus'] = False

# Configure fonts on module load
configure_cjk_fonts()

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
    fig, ax = plt.subplots(figsize=figsize)

    # Create histogram with KDE overlay
    sns.histplot(
        data=df,
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
    fig, ax = plt.subplots(figsize=figsize)

    # Create heatmap with annotations
    sns.heatmap(
        corr_matrix,
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
    fig, ax = plt.subplots(figsize=figsize)

    # Create scatter plot with regression line
    sns.regplot(
        data=df,
        x=x,
        y=y,
        ax=ax,
        scatter_kws={'alpha': 0.6}
    )

    # Add hue if specified
    if hue:
        sns.scatterplot(
            data=df,
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
    fig, ax = plt.subplots(figsize=figsize)

    if group_by:
        sns.boxplot(
            data=df,
            x=group_by,
            y=column,
            ax=ax
        )
        ax.set_title(f"{column} by {group_by}")
    else:
        sns.boxplot(
            data=df,
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
    fig, ax = plt.subplots(figsize=figsize)

    if group_by:
        sns.violinplot(
            data=df,
            x=group_by,
            y=column,
            ax=ax
        )
        ax.set_title(f"{column} by {group_by}")
    else:
        sns.violinplot(
            data=df,
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
