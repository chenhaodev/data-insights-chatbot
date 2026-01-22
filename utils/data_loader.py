"""Data loading and validation utilities."""

from typing import Tuple, List
import pandas as pd
from pydantic import BaseModel
from io import BytesIO


class DataFrameInfo(BaseModel):
    """Information about loaded dataframe."""
    name: str
    rows: int
    columns: int
    column_names: list
    dtypes: dict
    has_nulls: bool
    memory_usage: str


def load_csv_or_excel(
    file_data: bytes,
    filename: str
) -> Tuple[pd.DataFrame, DataFrameInfo]:
    """
    Load CSV or Excel file from bytes and return DataFrame with metadata.

    Args:
        file_data: File data as bytes
        filename: Original filename

    Returns:
        Tuple of (DataFrame, DataFrameInfo)

    Raises:
        ValueError: If file type is not supported
    """
    # Determine file type from extension
    if filename.endswith('.csv'):
        df = pd.read_csv(BytesIO(file_data))
    elif filename.endswith(('.xlsx', '.xls')):
        df = pd.read_excel(BytesIO(file_data))
    else:
        raise ValueError(f"Unsupported file type: {filename}. Use CSV or Excel files.")

    # Create metadata
    info = DataFrameInfo(
        name=filename,
        rows=len(df),
        columns=len(df.columns),
        column_names=df.columns.tolist(),
        dtypes={col: str(dtype) for col, dtype in df.dtypes.items()},
        has_nulls=df.isnull().any().any(),
        memory_usage=f"{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB"
    )

    return df, info


def validate_dataframe(df: pd.DataFrame) -> List[str]:
    """
    Validate dataframe and return list of warnings.

    Args:
        df: DataFrame to validate

    Returns:
        List of warning messages
    """
    warnings = []

    # Check if empty
    if len(df) == 0:
        warnings.append("⚠️ DataFrame is empty (0 rows)")
        return warnings

    # Check for missing values
    missing_counts = df.isnull().sum()
    high_missing = missing_counts[missing_counts > len(df) * 0.5]
    if len(high_missing) > 0:
        warnings.append(
            f"⚠️ High missing values (>50%) in columns: {', '.join(high_missing.index.tolist())}"
        )

    # Check for all-null columns
    null_cols = df.columns[df.isnull().all()].tolist()
    if null_cols:
        warnings.append(f"⚠️ Columns with all null values: {', '.join(null_cols)}")

    # Check for duplicate columns
    if df.columns.duplicated().any():
        dup_cols = df.columns[df.columns.duplicated()].tolist()
        warnings.append(f"⚠️ Duplicate column names: {', '.join(dup_cols)}")

    # Check for constant columns
    numeric_df = df.select_dtypes(include=['number'])
    constant_cols = []
    for col in numeric_df.columns:
        if numeric_df[col].nunique() == 1:
            constant_cols.append(col)
    if constant_cols:
        warnings.append(f"ℹ️ Constant value columns: {', '.join(constant_cols)}")

    # Check for very large dataset
    if len(df) > 100000:
        warnings.append(
            f"ℹ️ Large dataset ({len(df):,} rows). Some operations may be slow."
        )

    return warnings


def get_column_info(df: pd.DataFrame) -> pd.DataFrame:
    """
    Get detailed information about DataFrame columns.

    Args:
        df: DataFrame to analyze

    Returns:
        DataFrame with column information
    """
    info_data = []

    for col in df.columns:
        col_info = {
            'column': col,
            'dtype': str(df[col].dtype),
            'non_null': df[col].count(),
            'null_count': df[col].isnull().sum(),
            'null_pct': f"{(df[col].isnull().sum() / len(df)) * 100:.1f}%",
            'unique': df[col].nunique()
        }

        # Add statistics for numeric columns
        if pd.api.types.is_numeric_dtype(df[col]):
            col_info['mean'] = f"{df[col].mean():.2f}"
            col_info['std'] = f"{df[col].std():.2f}"
            col_info['min'] = f"{df[col].min():.2f}"
            col_info['max'] = f"{df[col].max():.2f}"
        else:
            col_info['mean'] = '-'
            col_info['std'] = '-'
            col_info['min'] = '-'
            col_info['max'] = '-'

        info_data.append(col_info)

    return pd.DataFrame(info_data)
