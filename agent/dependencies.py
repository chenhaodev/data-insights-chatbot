"""Agent dependencies for managing data context and state."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import pandas as pd


@dataclass
class AgentDependencies:
    """
    Dependencies for the data insights agent.

    Manages uploaded dataframes, analysis history, and user preferences.
    """

    # Data context
    uploaded_dataframes: Dict[str, pd.DataFrame] = field(default_factory=dict)
    current_df_name: Optional[str] = None

    # Analysis history
    analysis_history: List[Dict[str, Any]] = field(default_factory=list)

    # User preferences
    chart_style: str = "darkgrid"
    max_chart_elements: int = 50

    def get_current_dataframe(self) -> Optional[pd.DataFrame]:
        """
        Get the currently active dataframe.

        Returns:
            Optional[pd.DataFrame]: Current dataframe if one is set, None otherwise
        """
        if self.current_df_name and self.current_df_name in self.uploaded_dataframes:
            return self.uploaded_dataframes[self.current_df_name]
        return None

    def add_to_history(self, query: str, result: str, tool_used: str):
        """
        Track analysis history for context and debugging.

        Args:
            query: The query or request made
            result: Result status (success/error)
            tool_used: Name of the tool that was used
        """
        self.analysis_history.append({
            "query": query,
            "result": result,
            "tool": tool_used
        })

        # Keep only last 50 entries to avoid memory issues
        if len(self.analysis_history) > 50:
            self.analysis_history = self.analysis_history[-50:]

    def set_dataframe(self, name: str, df: pd.DataFrame):
        """
        Add or update a dataframe in the context.

        Args:
            name: Name/identifier for the dataframe
            df: The pandas DataFrame
        """
        self.uploaded_dataframes[name] = df
        if self.current_df_name is None:
            self.current_df_name = name

    def list_dataframes(self) -> List[str]:
        """
        Get list of all uploaded dataframe names.

        Returns:
            List[str]: Names of all uploaded dataframes
        """
        return list(self.uploaded_dataframes.keys())
