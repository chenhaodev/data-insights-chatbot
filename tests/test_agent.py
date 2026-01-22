"""Tests for agent initialization and functionality."""

import pytest
from pydantic_ai.models.test import TestModel
from agent.agent import data_insights_agent
from agent.dependencies import AgentDependencies


class TestAgentInitialization:
    """Test agent initialization and configuration."""

    def test_agent_has_dependencies_type(self):
        """Test agent has correct dependencies type."""
        assert data_insights_agent.deps_type == AgentDependencies

    def test_agent_has_system_prompt(self):
        """Test agent has system prompt configured."""
        assert data_insights_agent.system_prompt is not None
        assert len(data_insights_agent.system_prompt) > 0

    def test_agent_has_registered_tools(self):
        """Test agent has all required tools registered."""
        tool_names = [tool.name for tool in data_insights_agent.tool_defs]

        expected_tools = [
            'describe_dataset',
            'correlation_analysis_tool',
            'create_visualization',
            'perform_statistical_test',
            'query_data_nl',
            'time_series_analysis',
            'generate_profile_report'
        ]

        for expected_tool in expected_tools:
            assert expected_tool in tool_names, f"Missing tool: {expected_tool}"


class TestAgentWithTestModel:
    """Test agent with TestModel for fast execution."""

    @pytest.mark.asyncio
    async def test_agent_responds_without_data(self, agent_dependencies):
        """Test agent handles missing data gracefully."""
        # Clear dataframes
        agent_dependencies.uploaded_dataframes = {}
        agent_dependencies.current_df_name = None

        test_agent = data_insights_agent.override(model=TestModel())

        result = await test_agent.run(
            "What are the statistics?",
            deps=agent_dependencies
        )

        assert result.output is not None
        assert isinstance(result.output, str)


    @pytest.mark.asyncio
    async def test_agent_with_data(self, agent_dependencies):
        """Test agent with loaded data."""
        test_agent = data_insights_agent.override(model=TestModel())

        result = await test_agent.run(
            "Tell me about the dataset",
            deps=agent_dependencies
        )

        assert result.output is not None
        assert isinstance(result.output, str)


class TestDependencies:
    """Test agent dependencies functionality."""

    def test_dependencies_initialization(self):
        """Test dependencies can be initialized."""
        deps = AgentDependencies()
        assert deps.uploaded_dataframes == {}
        assert deps.current_df_name is None
        assert deps.analysis_history == []

    def test_set_dataframe(self, sample_dataframe):
        """Test setting dataframe in dependencies."""
        deps = AgentDependencies()
        deps.set_dataframe("test.csv", sample_dataframe)

        assert "test.csv" in deps.uploaded_dataframes
        assert deps.current_df_name == "test.csv"
        assert deps.get_current_dataframe() is not None

    def test_add_to_history(self):
        """Test adding to analysis history."""
        deps = AgentDependencies()
        deps.add_to_history("test query", "success", "test_tool")

        assert len(deps.analysis_history) == 1
        assert deps.analysis_history[0]["query"] == "test query"
