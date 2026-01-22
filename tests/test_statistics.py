"""Tests for statistical analysis utilities."""

import pytest
import pandas as pd
import numpy as np
from utils import statistics


@pytest.mark.asyncio
async def test_descriptive_statistics(sample_dataframe):
    """Test descriptive statistics calculation."""
    result = await statistics.descriptive_statistics(sample_dataframe, ['age', 'salary'])

    assert 'age' in result
    assert 'salary' in result
    assert 'mean' in result['age']
    assert 'median' in result['age']
    assert 'std' in result['age']
    assert result['age']['count'] == 100


@pytest.mark.asyncio
async def test_correlation_analysis(sample_dataframe):
    """Test correlation analysis."""
    result = await statistics.correlation_analysis(sample_dataframe, method='pearson')

    assert 'correlation_matrix' in result
    assert 'method' in result
    assert result['method'] == 'pearson'
    assert 'age' in result['columns']
    assert 'salary' in result['columns']


@pytest.mark.asyncio
async def test_correlation_invalid_method(sample_dataframe):
    """Test correlation with invalid method."""
    with pytest.raises(ValueError):
        await statistics.correlation_analysis(sample_dataframe, method='invalid')


@pytest.mark.asyncio
async def test_t_test_analysis(sample_dataframe):
    """Test t-test analysis."""
    group1 = sample_dataframe[sample_dataframe['group'] == 'Group1']['salary']
    group2 = sample_dataframe[sample_dataframe['group'] == 'Group2']['salary']

    result = await statistics.t_test_analysis(group1, group2)

    assert 't_statistic' in result
    assert 'p_value' in result
    assert 'interpretation' in result
    assert 'significant' in result
    assert isinstance(result['significant'], bool)


@pytest.mark.asyncio
async def test_regression_analysis(sample_dataframe):
    """Test regression analysis."""
    X = sample_dataframe[['age']]
    y = sample_dataframe['salary']

    result = await statistics.regression_analysis(X, y)

    assert 'r_squared' in result
    assert 'coefficients' in result
    assert 'pvalues' in result
    assert 'const' in result['coefficients']
    assert 'age' in result['coefficients']


@pytest.mark.asyncio
async def test_anova_test(sample_dataframe):
    """Test ANOVA analysis."""
    groups = [
        sample_dataframe[sample_dataframe['category'] == cat]['score']
        for cat in ['A', 'B', 'C']
    ]

    result = await statistics.anova_test(groups)

    assert 'f_statistic' in result
    assert 'p_value' in result
    assert 'num_groups' in result
    assert result['num_groups'] == 3
    assert 'interpretation' in result
