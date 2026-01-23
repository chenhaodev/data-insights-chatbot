"""Statistical analysis utilities using scipy and statsmodels."""

import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.api import OLS, add_constant
from typing import Dict, Optional, List, Union, Any
import asyncio


async def descriptive_statistics(
    df: pd.DataFrame,
    columns: Optional[List[str]] = None
) -> Dict[str, Dict[str, float]]:
    """
    Calculate comprehensive descriptive statistics.

    Args:
        df: DataFrame to analyze
        columns: Specific columns to analyze (None = all numeric columns)

    Returns:
        Dict mapping column names to their statistics

    Example:
        >>> stats = await descriptive_statistics(df, ['age', 'salary'])
        >>> print(stats['age']['mean'])
    """
    def _compute():
        if columns is None:
            numeric_df = df.select_dtypes(include=[np.number])
        else:
            numeric_df = df[columns].select_dtypes(include=[np.number])

        # Filter out columns where >95% of values are NaN (mostly empty columns)
        valid_cols = []
        for col in numeric_df.columns:
            null_percentage = numeric_df[col].isna().sum() / len(numeric_df[col])
            if null_percentage < 0.95:  # Keep columns with <95% NaN
                valid_cols.append(col)

        numeric_df = numeric_df[valid_cols]

        results = {}
        for col in numeric_df.columns:
            results[col] = {
                "mean": float(numeric_df[col].mean()),
                "median": float(numeric_df[col].median()),
                "std": float(numeric_df[col].std()),
                "min": float(numeric_df[col].min()),
                "max": float(numeric_df[col].max()),
                "q25": float(numeric_df[col].quantile(0.25)),
                "q75": float(numeric_df[col].quantile(0.75)),
                "count": int(numeric_df[col].count()),
                "missing": int(numeric_df[col].isna().sum())
            }
        return results

    # Run blocking pandas operations in thread pool
    return await asyncio.to_thread(_compute)


async def correlation_analysis(
    df: pd.DataFrame,
    method: str = "pearson",
    columns: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Calculate correlation matrix.

    Args:
        df: DataFrame to analyze
        method: Correlation method ('pearson', 'spearman', 'kendall')
        columns: Specific columns to analyze (None = all numeric)

    Returns:
        Dict with correlation matrix and metadata

    Raises:
        ValueError: If method is not valid
    """
    def _compute():
        numeric_df = df[columns] if columns else df.select_dtypes(include=[np.number])

        # Filter out columns where >95% of values are NaN (mostly empty columns)
        valid_cols = []
        for col in numeric_df.columns:
            null_percentage = numeric_df[col].isna().sum() / len(numeric_df[col])
            if null_percentage < 0.95:  # Keep columns with <95% NaN
                valid_cols.append(col)

        numeric_df = numeric_df[valid_cols]

        if method not in ["pearson", "spearman", "kendall"]:
            raise ValueError(f"Invalid method: {method}. Use 'pearson', 'spearman', or 'kendall'")

        corr_matrix = numeric_df.corr(method=method)

        return {
            "correlation_matrix": corr_matrix.to_dict(),
            "method": method,
            "columns": corr_matrix.columns.tolist(),
            "dataframe": corr_matrix  # Keep for visualization
        }

    return await asyncio.to_thread(_compute)


async def t_test_analysis(
    group1: pd.Series,
    group2: pd.Series,
    alternative: str = "two-sided"
) -> Dict[str, Union[float, str, bool]]:
    """
    Perform independent samples t-test.

    Args:
        group1: First group data
        group2: Second group data
        alternative: 'two-sided', 'less', or 'greater'

    Returns:
        Dict with test statistics and interpretation
    """
    def _compute():
        # Remove NaN values
        g1 = group1.dropna()
        g2 = group2.dropna()

        # Perform t-test
        statistic, p_value = stats.ttest_ind(g1, g2, alternative=alternative)

        # Interpretation
        significant = p_value < 0.05
        interpretation = (
            f"The difference is {'statistically significant' if significant else 'not significant'} "
            f"at α=0.05 (p={p_value:.4f})"
        )

        return {
            "t_statistic": float(statistic),
            "p_value": float(p_value),
            "degrees_of_freedom": len(g1) + len(g2) - 2,
            "group1_mean": float(g1.mean()),
            "group2_mean": float(g2.mean()),
            "group1_std": float(g1.std()),
            "group2_std": float(g2.std()),
            "significant": significant,
            "interpretation": interpretation,
            "alternative": alternative
        }

    return await asyncio.to_thread(_compute)


async def regression_analysis(
    X: pd.DataFrame,
    y: pd.Series
) -> Dict[str, Any]:
    """
    Perform OLS regression analysis.

    Args:
        X: Independent variables (predictors)
        y: Dependent variable (target)

    Returns:
        Dict with regression results
    """
    def _compute():
        # Add constant for intercept
        X_with_const = add_constant(X)

        # Fit model
        model = OLS(y, X_with_const).fit()

        return {
            "r_squared": float(model.rsquared),
            "adj_r_squared": float(model.rsquared_adj),
            "f_statistic": float(model.fvalue),
            "f_pvalue": float(model.f_pvalue),
            "coefficients": {name: float(coef) for name, coef in model.params.items()},
            "pvalues": {name: float(pval) for name, pval in model.pvalues.items()},
            "residuals_mean": float(model.resid.mean()),
            "residuals_std": float(model.resid.std()),
            "summary": str(model.summary())
        }

    return await asyncio.to_thread(_compute)


async def time_series_decomposition(
    series: pd.Series,
    freq: int,
    model: str = "additive"
) -> Dict[str, Any]:
    """
    Decompose time series into trend, seasonal, and residual components.

    Args:
        series: Time series data
        freq: Seasonal frequency (e.g., 12 for monthly data with yearly seasonality)
        model: 'additive' or 'multiplicative'

    Returns:
        Dict with decomposition results
    """
    def _compute():
        # Perform decomposition
        result = seasonal_decompose(series, model=model, period=freq)

        return {
            "trend": result.trend.to_dict(),
            "seasonal": result.seasonal.to_dict(),
            "residual": result.resid.to_dict(),
            "model": model,
            "frequency": freq
        }

    return await asyncio.to_thread(_compute)


async def anova_test(
    groups: List[pd.Series]
) -> Dict[str, Any]:
    """
    Perform one-way ANOVA test.

    Args:
        groups: List of groups to compare

    Returns:
        Dict with ANOVA results
    """
    def _compute():
        # Remove NaN values from each group
        clean_groups = [g.dropna() for g in groups]

        # Perform ANOVA
        f_statistic, p_value = stats.f_oneway(*clean_groups)

        significant = p_value < 0.05
        interpretation = (
            f"The group means are {'significantly different' if significant else 'not significantly different'} "
            f"at α=0.05 (p={p_value:.4f})"
        )

        return {
            "f_statistic": float(f_statistic),
            "p_value": float(p_value),
            "num_groups": len(groups),
            "significant": significant,
            "interpretation": interpretation,
            "group_means": [float(g.mean()) for g in clean_groups],
            "group_sizes": [len(g) for g in clean_groups]
        }

    return await asyncio.to_thread(_compute)
