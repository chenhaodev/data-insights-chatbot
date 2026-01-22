"""Pytest fixtures for testing."""

import pytest
import pandas as pd
import numpy as np
from agent.dependencies import AgentDependencies


@pytest.fixture
def sample_dataframe():
    """Create sample dataframe for testing."""
    np.random.seed(42)

    data = {
        'age': np.random.randint(20, 65, 100),
        'salary': np.random.randint(30000, 120000, 100),
        'score': np.random.uniform(0, 100, 100),
        'category': np.random.choice(['A', 'B', 'C'], 100),
        'group': np.random.choice(['Group1', 'Group2'], 100),
        'date': pd.date_range('2020-01-01', periods=100, freq='D')
    }

    return pd.DataFrame(data)


@pytest.fixture
def agent_dependencies(sample_dataframe):
    """Create agent dependencies with sample data."""
    deps = AgentDependencies()
    deps.set_dataframe("test.csv", sample_dataframe)
    return deps


@pytest.fixture
def empty_dataframe():
    """Create empty dataframe for error testing."""
    return pd.DataFrame()
