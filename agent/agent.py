"""Main Data Insights Agent implementation."""

from pydantic_ai import Agent
from .providers import get_llm_model
from .dependencies import AgentDependencies
from .prompts import MAIN_SYSTEM_PROMPT
from . import tools


# Initialize the data insights agent
data_insights_agent = Agent(
    get_llm_model(),
    deps_type=AgentDependencies,
    system_prompt=MAIN_SYSTEM_PROMPT
)

# Register all analysis tools
data_insights_agent.tool(tools.initial_data_exploration)
data_insights_agent.tool(tools.describe_dataset)
data_insights_agent.tool(tools.correlation_analysis_tool)
data_insights_agent.tool(tools.create_visualization)
data_insights_agent.tool(tools.perform_statistical_test)
data_insights_agent.tool(tools.query_data_nl)
data_insights_agent.tool(tools.time_series_analysis)
data_insights_agent.tool(tools.generate_profile_report)
