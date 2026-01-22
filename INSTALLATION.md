# Installation and Testing Guide

## Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install all required packages
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your DeepSeek API key
# DEEPSEEK_API_KEY=your-api-key-here
```

### 3. Run the Application

```bash
streamlit run app.py
```

The application will open at `http://localhost:8501`

## Testing

### Run Unit Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ -v --cov=. --cov-report=html

# Run specific test file
pytest tests/test_statistics.py -v
pytest tests/test_agent.py -v
```

### Manual Testing Checklist

1. **File Upload**
   - Upload `tests/test_data/sample.csv`
   - Verify preview shows 50 rows
   - Check column information displays correctly

2. **Descriptive Statistics**
   - Ask: "What are the descriptive statistics for all numeric columns?"
   - Verify mean, median, std, min, max are displayed

3. **Correlation Analysis**
   - Ask: "Show me a correlation heatmap"
   - Verify heatmap is generated and displayed

4. **Visualizations**
   - Ask: "Create a scatter plot of age vs salary"
   - Ask: "Show me a box plot of score by category"
   - Verify charts are displayed

5. **Statistical Tests**
   - Ask: "Perform a t-test comparing salary between Group1 and Group2"
   - Verify t-statistic, p-value, and interpretation are shown

6. **Natural Language Queries** (requires API key)
   - Ask: "What is the average salary by category?"
   - Verify PandasAI returns the correct aggregation

## Code Quality Checks

### Syntax Validation

```bash
# Check Python syntax
python -m py_compile agent/*.py utils/*.py app.py
```

### Formatting (Optional)

```bash
# Install black and ruff
pip install black ruff

# Format code
black . --line-length 100

# Lint code
ruff check . --fix
```

## Troubleshooting

### Missing Dependencies

If you get `ModuleNotFoundError`:

```bash
pip install -r requirements.txt
```

### API Key Issues

If you get `Failed to load settings`:

1. Check `.env` file exists
2. Verify `DEEPSEEK_API_KEY` is set
3. Make sure there are no quotes around the key

### Import Errors

If imports fail, make sure you're in the project directory:

```bash
cd data-insights-chatbot
python -c "import sys; sys.path.insert(0, '.'); from agent import settings"
```

## Validation Status

### ✅ Completed

- [x] All Python files have valid syntax
- [x] Project structure created
- [x] All modules implemented
- [x] Documentation complete
- [x] Test suite created
- [x] Example data provided

### ⏳ Requires Dependencies

- [ ] Run unit tests (requires: pip install -r requirements.txt)
- [ ] Test with DeepSeek API (requires: API key in .env)
- [ ] Generate visualizations (requires: matplotlib, seaborn)
- [ ] PandasAI queries (requires: pandasai, DeepSeek API key)

## Next Steps

1. Install dependencies: `pip install -r requirements.txt`
2. Set up `.env` with your DeepSeek API key
3. Run tests: `pytest tests/ -v`
4. Start the app: `streamlit run app.py`
5. Upload test data and start analyzing!
