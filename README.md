# 📊 Data Insights Chatbot

A conversational data analysis application powered by DeepSeek AI, PandasAI, and Seaborn. Upload CSV/Excel files and ask questions about your data in natural language.

## Features

- **Natural Language Queries**: Ask questions about your data using PandasAI
- **Statistical Analysis**: Descriptive statistics, correlation, t-tests, ANOVA, regression
- **Data Visualization**: Automatic chart generation (scatter, box, violin, heatmap, distribution)
- **Time Series Analysis**: Decomposition into trend, seasonal, and residual components
- **Automated EDA**: Generate comprehensive exploratory data analysis reports with ydata-profiling
- **Interactive UI**: Streamlit-based chat interface with file upload
- **Conversation Memory**: Maintains context across multiple questions

## Installation

### Prerequisites

- Python 3.10 or higher
- DeepSeek API key (get one at [https://platform.deepseek.com/](https://platform.deepseek.com/))

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd data-insights-chatbot
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env and add your DEEPSEEK_API_KEY
```

Example `.env` file:
```
DEEPSEEK_API_KEY=your-api-key-here
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
MAX_DATAFRAME_ROWS=10000
```

## Usage

### Start the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

### How to Use

1. **Upload Data**: Use the sidebar to upload a CSV or Excel file
2. **Ask Questions**: Type your questions in natural language in the chat input
3. **View Results**: Get statistics, visualizations, and insights automatically

### Example Questions

**Descriptive Statistics:**
- "What are the descriptive statistics for all numeric columns?"
- "Show me the mean and median of the salary column"

**Correlations:**
- "Show me a correlation heatmap"
- "What's the correlation between age and salary?"

**Visualizations:**
- "Create a scatter plot of age vs salary"
- "Show me a box plot of score by category"
- "Display the distribution of age"

**Statistical Tests:**
- "Perform a t-test comparing salary between Group1 and Group2"
- "Run an ANOVA on score across all categories"

**Natural Language Queries (PandasAI):**
- "What is the average salary by department?"
- "How many people are in each category?"
- "Show me the top 5 highest salaries"

**Time Series:**
- "Analyze the time series data with frequency 12"

**Comprehensive Analysis:**
- "Generate a comprehensive profile report"

## Project Structure

```
data-insights-chatbot/
├── agent/
│   ├── agent.py          # Main Pydantic AI agent
│   ├── tools.py          # Analysis tools
│   ├── prompts.py        # System prompts
│   ├── dependencies.py   # Agent state management
│   ├── settings.py       # Configuration
│   └── providers.py      # LLM provider setup
├── utils/
│   ├── statistics.py     # Statistical analysis functions
│   ├── visualization.py  # Seaborn chart generation
│   └── data_loader.py    # CSV/Excel loading
├── tests/
│   ├── test_agent.py     # Agent tests
│   ├── test_statistics.py # Statistics tests
│   └── conftest.py       # Pytest fixtures
├── app.py               # Streamlit application
├── requirements.txt     # Python dependencies
├── .env.example        # Environment template
└── README.md           # This file
```

## Architecture

### Components

1. **Streamlit UI** (`app.py`): Web interface for file upload and chat
2. **Pydantic AI Agent** (`agent/agent.py`): Main LLM controller using DeepSeek
3. **Analysis Tools** (`agent/tools.py`): 7 tools for different analysis types
4. **Statistical Utilities** (`utils/statistics.py`): scipy and statsmodels functions
5. **Visualization Utilities** (`utils/visualization.py`): Seaborn chart generation
6. **Data Loader** (`utils/data_loader.py`): CSV/Excel parsing and validation

### Tool Routing

The AI agent intelligently routes requests to appropriate tools:
- Simple statistics → `describe_dataset`
- Correlation analysis → `correlation_analysis_tool`
- Visualizations → `create_visualization`
- Hypothesis tests → `perform_statistical_test`
- Complex queries → `query_data_nl` (PandasAI)
- Time series → `time_series_analysis`
- Comprehensive EDA → `generate_profile_report`

## Development

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=. --cov-report=html

# Run specific test file
pytest tests/test_statistics.py -v
```

### Code Quality

```bash
# Format code
black . --line-length 100

# Lint
ruff check . --fix

# Type checking
mypy . --ignore-missing-imports
```

## Troubleshooting

### API Key Issues

**Error**: `Failed to load settings: deepseek_api_key`

**Solution**: Make sure `.env` file exists with `DEEPSEEK_API_KEY=your-key`

### File Upload Errors

**Error**: `Unsupported file type`

**Solution**: Only CSV (`.csv`) and Excel (`.xlsx`, `.xls`) files are supported

### Memory Issues

**Error**: Application becomes slow with large datasets

**Solution**: The app automatically samples datasets >10,000 rows. Adjust `MAX_DATAFRAME_ROWS` in `.env`

### Import Errors

**Error**: `ModuleNotFoundError`

**Solution**: Make sure you're in the virtual environment and all dependencies are installed:
```bash
pip install -r requirements.txt
```

## Performance

- **Response Time**: < 5 seconds for typical queries
- **Dataset Size**: Optimized for up to 10,000 rows (configurable)
- **Cost**: DeepSeek API at ~$0.27 per 1M input tokens, ~$1.10 per 1M output tokens

## Technologies Used

- **LLM**: DeepSeek API (OpenAI-compatible)
- **NL Data Queries**: PandasAI 2.0+
- **Statistical Analysis**: scipy, statsmodels
- **Visualization**: Seaborn, Matplotlib
- **UI Framework**: Streamlit
- **Agent Framework**: Pydantic AI
- **EDA Profiling**: ydata-profiling

## License

MIT License

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Acknowledgments

- DeepSeek for the powerful and cost-effective LLM API
- PandasAI for natural language data querying
- Seaborn for beautiful statistical visualizations
- Streamlit for the excellent web framework
- Pydantic AI for the agent framework
