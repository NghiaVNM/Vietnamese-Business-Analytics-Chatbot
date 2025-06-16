# Vietnamese Business Analytics Chatbot

A smart Vietnamese chatbot that converts natural language queries into structured function calls for business analytics operations. The system translates Vietnamese queries to English and generates precise database operations for financial and accounting departments.

## Features

- 🇻🇳 **Vietnamese Language Support**: Native Vietnamese query processing
- 🔄 **Automatic Translation**: Vietnamese to English translation for better LLM processing
- 🎯 **Function Calling**: Structured function generation from natural language
- 📊 **Business Analytics**: Support for reports, employee data, and financial operations
- ⚡ **Local LLM**: Uses Ollama with Llama2 for privacy and offline operation
- 🏢 **Multi-Department**: Supports accounting and finance departments

## Supported Operations

| Function | Description | Example Query |
|----------|-------------|---------------|
| `add` | Create new records | "Thêm báo cáo tài chính tháng này" |
| `get` | Retrieve existing data | "Xem báo cáo nhân viên tuần trước" |
| `delete` | Remove records | "Xóa báo cáo RPT123 ngày hôm qua" |
| `compare` | Analyze differences | "So sánh doanh thu tháng này với tháng trước" |
| `predict` | Forecast trends | "Dự đoán lợi nhuận quý tới" |

## Installation

### Prerequisites
- Python 3.12+
- Ollama installed on your system

### Step 1: Install Ollama
```bash
# On Linux/macOS
curl -fsSL https://ollama.ai/install.sh | sh

# On Windows
# Download and install from https://ollama.ai/download
```

### Step 2: Pull Llama2 Model
```bash
ollama pull llama2:7b
```

### Step 3: Start Ollama Server
```bash
ollama serve
# Server will start on http://localhost:11434
```

### Step 4: Setup Python Environment
```bash
# Clone the repository
git clone <repository-url>
cd Vietnamese-Business-Analytics-Chatbot/chatbot_2

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### Step 5: Configure Settings (Optional)
Edit `config/settings.py` to customize:
- LLM model name
- Temperature settings
- API endpoints
- Debug mode

## Usage

### Activate Environment and Run
```bash
# Activate virtual environment first
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# Run the chatbot
python run.py
```

### Example Conversation
```
Bạn: Xem báo cáo tài chính tháng này
Bot: get(departments='finance', content='report', id='report_123', type_of_time='month', specific_time='2025-06-01')

Bạn: Thêm nhân viên mới vào phòng kế toán
Bot: add(departments='accountant', content='employee', id='employee_456', type_of_time='day', specific_time='2025-06-11')
```

## Test Cases

### 1. ADD Function Test Cases

#### Test Case 1.1: Add Specific Report Today
```
Input: "Thêm báo cáo mới abc123 cho phòng kế toán hôm nay"
Expected Output: add(departments='accountant', content='report', id='abc123', type_of_time='day', specific_time='2025-06-11')
```

#### Test Case 1.2: Add Monthly Financial Report
```
Input: "Thêm báo cáo tài chính tháng này"
Expected Output: add(departments='finance', content='report', id='report_001', type_of_time='month', specific_time='2025-06-01')
```

#### Test Case 1.3: Add New Employee
```
Input: "Tạo hồ sơ nhân viên mới cho phòng kế toán"
Expected Output: add(departments='accountant', content='employee', id='employee_001', type_of_time='day', specific_time='2025-06-11')
```

### 2. GET Function Test Cases

#### Test Case 2.1: Get Daily Report
```
Input: "Xem báo cáo hôm nay"
Expected Output: get(departments='finance', content='report', id='report_002', type_of_time='day', specific_time='2025-06-11')
```

#### Test Case 2.2: Get Employee Data Range
```
Input: "Lấy dữ liệu nhân viên từ đầu tháng đến nay"
Expected Output: get(departments='finance', content='employee', id='employee_002', type_of_time='range', specific_time='2025-06-01 to 2025-06-11')
```

#### Test Case 2.3: Get Specific Report
```
Input: "Xem báo cáo xyz789 của phòng tài chính"
Expected Output: get(departments='finance', content='report', id='xyz789', type_of_time='day', specific_time='2025-06-11')
```

### 3. DELETE Function Test Cases

#### Test Case 3.1: Delete Specific Employee
```
Input: "Xóa nhân viên emp789 khỏi hệ thống"
Expected Output: delete(departments='finance', content='employee', id='emp789', type_of_time='day', specific_time='2025-06-11')
```

#### Test Case 3.2: Delete Specific Report
```
Input: "Xóa báo cáo RPT123 của tuần trước"
Expected Output: delete(departments='finance', content='report', id='RPT123', type_of_time='week', specific_time='2025-06-02')
```

#### Test Case 3.3: Remove Employee Record
```
Input: "Xóa hồ sơ nhân viên EMP456 khỏi phòng kế toán"
Expected Output: delete(departments='accountant', content='employee', id='EMP456', type_of_time='day', specific_time='2025-06-11')
```

### 4. COMPARE Function Test Cases

#### Test Case 4.1: Compare Monthly Reports
```
Input: "So sánh báo cáo tháng này với tháng trước"
Expected Output: compare(departments='finance', content='report', type_of_time='month', specific_time='2025-06-01')
```

#### Test Case 4.2: Compare Employee Performance
```
Input: "Phân tích hiệu suất nhân viên quý này"
Expected Output: compare(departments='accountant', content='employee', type_of_time='range', specific_time='2025-04-01 to 2025-06-30')
```

#### Test Case 4.3: Compare Financial Data
```
Input: "So sánh doanh thu năm nay với năm trước"
Expected Output: compare(departments='finance', content='report', type_of_time='year', specific_time='2025-01-01')
```

### 5. PREDICT Function Test Cases

#### Test Case 5.1: Predict Specific Report Trend
```
Input: "Dự đoán xu hướng báo cáo def456 tuần tới"
Expected Output: predict(departments='finance', content='report', id='def456', type_of_time='week', specific_time='2025-06-16')
```

#### Test Case 5.2: Forecast Financial Trends
```
Input: "Dự đoán lợi nhuận quý tới"
Expected Output: predict(departments='finance', content='report', type_of_time='range', specific_time='2025-07-01 to 2025-09-30')
```

#### Test Case 5.3: Predict Staffing Needs
```
Input: "Dự báo nhu cầu nhân sự năm sau"
Expected Output: predict(departments='accountant', content='employee', type_of_time='year', specific_time='2026-01-01')
```

## Running Test Cases

You can test these cases manually by running the chatbot and entering the Vietnamese queries, or create automated tests:

```bash
# Activate environment
source venv/bin/activate

# Run with debug mode for detailed output
python -c "
from config.settings import config
config.DEBUG = True
from run import main
main()
"
```

## Project Structure

```
chatbot_2/
├── venv/                   # Virtual environment (created after setup)
├── config/
│   ├── settings.py          # Configuration settings
│   └── schema.json         # Function calling schema
├── core/
│   ├── chatbot.py          # Main chatbot logic
│   ├── llm_handler.py      # LLM interaction handler
│   └── translator.py       # Vietnamese-English translation
├── prompts/
│   └── templates.py        # Prompt templates
├── utils/
│   ├── date_utils.py       # Date/time utilities
│   └── validators.py       # Schema validation
├── data/
│   └── test_queries.json   # Test queries dataset
├── requirements.txt        # Python dependencies
├── run.py                 # Main application entry
└── README.md              # This file
```

## Configuration

### Settings (config/settings.py)
- `LLM_BASE_URL`: Ollama server URL (default: http://localhost:11434)
- `LLM_MODEL`: Model name (default: llama2:7b)
- `LLM_TEMPERATURE`: Response randomness (default: 0.05)
- `DEBUG`: Enable debug mode for detailed logging

### Schema (config/schema.json)
Defines the structure for all supported functions with parameters, types, and validation rules.

## Troubleshooting

### Common Issues

1. **Virtual Environment Issues**
   ```bash
   # If activation fails, recreate venv
   rm -rf venv
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Ollama Connection Error**
   ```bash
   # Check if Ollama is running
   curl http://localhost:11434/api/tags
   
   # Restart Ollama service
   ollama serve
   ```

3. **Model Not Found**
   ```bash
   # Pull the required model
   ollama pull llama2:7b
   
   # List available models
   ollama list
   ```

4. **Translation Issues**
   - Ensure Vietnamese input is properly encoded (UTF-8)
   - Check if the query contains business-related keywords

5. **Function Call Parsing Errors**
   - Enable DEBUG mode in settings.py
   - Check logs for detailed error information

## Development

### Setting up Development Environment
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run in debug mode
python -c "
from config.settings import config
config.DEBUG = True
config.LOG_LEVEL = 'DEBUG'
from run import main
main()
"
```

### Deactivate Environment
When done working:
```bash
deactivate
```

## Contributing

1. Fork the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate environment: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Create a feature branch
6. Add test cases for new functionality
7. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review test cases for usage examples
