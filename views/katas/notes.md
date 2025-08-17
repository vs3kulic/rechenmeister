# Notes

## Running the Application

### Run as module (package structure)
python -m views.rechenmeister

### Explanation

• **Import Resolution**: Running as a module ensures Python's import system works correctly with relative imports, avoiding `sys.path.append('..')` hacks
• **Package Structure**: Following Python packaging standards makes the code more maintainable and allows for proper distribution via pip/PyPI
• **Namespace Management**: Module execution keeps all code within proper package namespaces, preventing naming conflicts and import pollution  
• **Development Best Practices**: Industry standard approach that makes the codebase familiar to other Python developers and easier to integrate with testing frameworks
• **Future-Proof Architecture**: Module structure supports advanced features like entry points, plugin systems, and proper dependency management


## CSV values and type conversion

- All values read from a CSV file using Python's `csv` module are strings, even if they look like numbers.
- To perform calculations, always convert string values to the appropriate type (e.g., `int(row.get("Angemeldet", "0"))`).
- This avoids bugs and ensures correct math and comparisons.

## Other recent learnings

- When filtering rows, use list comprehensions for clarity and performance: `[row for row in reader if row.get("Status") not in ("Storniert", "Abgesagt")]`.
- For time calculations, you can convert `HH:MM` to decimal hours using:
	```python
	hours, minutes = map(int, time.split(":"))
	decimal = hours + minutes / 60
	```
- When writing output files, use `os.path.basename(input_file)` to preserve the original extension.
## Python datetime.strptime()

- `datetime.strptime(date_string, format)` converts a string to a `datetime` object using the specified format.
- Example: `datetime.strptime("17:30", "%H:%M")` parses the string "17:30" as a time (5:30 PM).
- Common format codes:
	- `%Y`: Year (e.g., 2025)
	- `%m`: Month (01-12)
	- `%d`: Day (01-31)
	- `%H`: Hour (00-23)
	- `%M`: Minute (00-59)
	- `%S`: Second (00-59)
- Useful for converting time strings from CSV files to Python objects for calculations.

The implemenation would look like this:

```Python
for row in filtered_rows:
        start_time = datetime.strptime(row["Startzeit"], "%H:%M")
        end_time = datetime.strptime(row["Endzeit"], "%H:%M")
        timedelta = end_time - start_time # Calculate the duration as a timedelta object
        duration = timedelta.total_seconds() / 3600
        row["Dauer"] = f"{duration:.1f}"  # Add a new column with duration formatted to one decimal place
```

## Learnings: Filtering and Pandas vs. Python CSV

- When working with CSV files in Python, always check the delimiter. Pandas defaults to commas, but many European exports use semicolons (`;`). Use `pd.read_csv(filename, delimiter=';')` for such files.
- To filter rows in pandas, use boolean indexing: `df = df[df["Status"] != "Storniert"]`. This creates a new DataFrame with only the desired rows.
- In pure Python, use the `csv.DictReader` and build a new list with only the rows you want:
	```python
	import csv
	filtered_rows = []
	with open(filename, newline='', encoding='utf-8') as csvfile:
			reader = csv.DictReader(csvfile, delimiter=';')
			for row in reader:
					if row.get("Status") != "Storniert":
							filtered_rows.append(row)
	```
- It is more pythonic and safer to build a new list of filtered rows than to remove items from a list while iterating.
- If columns are reported missing by pandas, check the delimiter and column names for typos or encoding issues.

## CLI-Tool Features and Learnings

### Key Features
- Panel for banners and section headers to make the CLI visually appealing and organized.
- Table for menu options, allowing for clear and structured presentation of choices.
- Prompt and IntPrompt for user input, enabling interactive selection and validation.
- Modular functions for each menu action: for each option, call a function (e.g., ingest_file(), process_file(), generate_invoice(), inspect_log()).
- Markdown rendering for logs or reports, supporting rich text output in the CLI.

### String vs. Integer Arguments
- The Table.add_row() method expects its arguments to be strings, not integers. This ensures proper formatting and display in the rich table.
- The choices argument in IntPrompt.ask() expects a list of strings, not integers. User input from the terminal is always received as a string, and choices is used to validate that input before converting it to an integer.
- You use quotation marks in choices for input validation, but the returned value is an integer, which you then compare as if selection == 1: in your control flow.

### Exception Handling and User Experience in CLI
- Raising FileNotFoundError when a file is missing is correct, but letting it crash the CLI is not user-friendly.
- Improved user experience by catching FileNotFoundError and IOError in main(), displaying a rich error message instead of crashing.
- Use console.print from the rich library to show styled, colored, and emoji-enhanced error messages for better feedback.

### Logging Strategies and Formatting
- Explored logging strategies for CLI tools, comparing file-based logging (like move.log in a7_ex2.py) and Python's logging module.
- Added logging to meister.py using a log file (meister.log) and CLI log inspection, then discussed and reverted changes for further refinement.
- Lazy formatting in logging (e.g., logging.info("File moved: %s", filename)) is better than f-strings because:
	- The string is only formatted if the log level is enabled, saving CPU and memory.
	- It avoids unnecessary string interpolation when the log message won’t be output.
	- It’s safer for logging large or expensive-to-compute values.
- With f-strings, formatting happens every time, even if the log message is ignored due to log level.
- Lazy formatting is more efficient and recommended for production code.

### File Ingestion and Naming
- Practiced file ingestion with dynamic file naming using datetime formatting (e.g., aktivitaetsbericht-08-2025.csv).
- Clarified Python string formatting: `02d` means zero-padded, two-digit integer, which is useful for consistent file naming.

### Main Control Flow Best Practices
- Refactored main control flow into a main() function and used the main guard for script execution.
- Discussed best practices for structuring CLI scripts for maintainability and clarity.

### Rich Library Usage
- Used rich's Table, Panel, and IntPrompt for user interaction, making the CLI more engaging and easier to use.
- Confirmed that static analysis errors about rich imports were false positives, and the CLI works as expected.

---

## Session Summary (15 August 2025)

- Set up a Python CLI tool using the rich library for a visually appealing menu.
- Explored how to use rich's Table, Panel, and IntPrompt for user interaction.
- Clarified why menu options and IntPrompt choices use strings for display and input validation, but return integers for control flow.
- Improved error handling by catching exceptions and displaying user-friendly messages.
- Practiced file ingestion and dynamic file naming.
- Compared logging strategies and adopted lazy formatting for efficiency.
- Discussed best practices for main control flow and error handling in CLI scripts.
- Agreed to update this notes.md file with a summary after each exchange for learning and exam preparation.

---

## Next Steps: Refactoring the Monolithic Module

The current module has grown into a big, fat, hairy monolith with over 350 lines of code handling ingestion, processing, PDF generation, and CLI orchestration all in one place. Time to refactor for maintainability and testability:

### Step 1: Divide into 3 Smaller Modules
- **`ingestion.py`**: Handle file discovery, moving, and renaming from Downloads to input_csv
- **`processing.py`**: Handle CSV reading, data transformation, calculations, and writing to output_csv
- **`generation.py`**: Handle PDF creation with tables, styling, and output formatting
- Keep the main CLI orchestration in `rechenmeister.py` as a thin controller that imports and calls the other modules

### Step 2: Add Test Cases
- **Unit tests** for each module's core functions (file operations, calculations, PDF structure)
- **Integration tests** to verify the complete workflow end-to-end
- **Edge case testing** for missing files, malformed CSV data, permission errors
- Use pytest with fixtures for test data and temporary directories

### Step 3: Add Configuration and Error Handling
- **Configuration file** (YAML or JSON) for constants like BASE_HOURLY_RATE, file patterns, trainer names
- **Robust error handling** with custom exception classes for different failure modes
- **Input validation** to catch and handle malformed data gracefully
- **Logging improvements** with different log levels and optional console output

### Additional Future Enhancements
- Add a `--batch` mode for processing multiple months at once
- **Dynamic trainer selection**: Allow user to select from available trainers in the input CSV instead of hardcoding "Victoria"
  - Read the input CSV and extract unique trainer names
  - Present a rich Table menu for trainer selection
  - Pass selected trainer to processing function for filtering
  - Store trainer selection in configuration for future runs
- Support for multiple trainers with different rates
- Export to Excel format in addition to PDF
- Add command-line arguments for non-interactive usage

---

## Configuration File Formats: YAML vs JSON

When choosing a format for configuration files, YAML generally wins over JSON for several reasons:

### YAML Advantages
**1. Human Readability & Comments**
```yaml
# Processing Settings - these control how invoices are calculated
processing:
  base_hourly_rate: 20.0    # Default rate in Euros
  bonus_multiplier: 1.5     # Applied for high attendance
```

**2. Less Syntax Noise** - No quotes around keys, no trailing commas
**3. Multi-line Strings** - Perfect for descriptions or SQL queries
**4. Industry Standard** - Docker Compose, Kubernetes, GitHub Actions all use YAML

### When JSON Might Be Better
- **Performance**: JSON parsing is faster
- **Ubiquity**: Every programming language supports JSON natively
- **Data Exchange**: Better for APIs and data transfer
- **Validation**: Easier schema validation with JSON Schema

### Our Choice
For Rechenmeister, YAML is perfect because:
- Humans need to read/modify settings (rates, paths, etc.)
- Comments explain what each setting does
- Multi-line descriptions are useful for complex configurations
- It's more maintainable for configuration management

---

## Refactoring Success: From Monolith to Beautiful Pipeline

**Date:** August 17, 2025

Successfully refactored the monolithic `processing.py` module from a single 164-line function into a clean, pipeline-based architecture.

### Before: The Monolith Problem
```python
def process_file():
    # 164 lines of mixed responsibilities:
    # - File discovery and validation
    # - CSV parsing and filtering  
    # - Time calculations and conversions
    # - Bonus factor applications
    # - Excel formatting
    # - File output operations
    # Hard to test, debug, modify, or understand
```

### After: Beautiful Logical Sub-modules
```python
def process_file():
    """Clean 4-step orchestrator"""
    input_file = discover_input_file()
    raw_data = load_and_validate_csv(input_file)
    processed_data = transform_data(raw_data)
    output_file = save_processed_data(processed_data, input_file)
```

### Refactored Function Structure

**📂 Data Discovery & Loading**
- `discover_input_file()` - Finds the input CSV file
- `load_and_validate_csv()` - Loads data and validates required columns

**⚙️ Data Transformation Pipeline**
- `add_duration_calculations()` - Converts HH:MM to decimal hours
- `add_base_rates()` - Applies hourly rates from config
- `add_attendance_metrics()` - Calculates attendance percentages
- `apply_bonus_factors()` - Applies attendance-based bonuses (100%=2x, 50%=1.5x)
- `calculate_final_amounts()` - Calculates final payments per class
- `add_summary_row()` - Adds monthly totals row

**💾 Data Preparation & Output**  
- `prepare_fieldnames()` - Ensures all required fields are present
- `format_for_excel()` - Converts decimals (dots to commas) for Excel
- `save_processed_data()` - Writes final CSV with proper formatting

**🎭 Orchestration**
- `transform_data()` - Runs all transformations in sequence
- `process_file()` - Main coordinator (reduced to 25 lines!)

### Key Benefits Achieved

✅ **Single Responsibility Principle** - Each function does exactly one thing  
✅ **Testability** - Easy to unit test individual transformation steps  
✅ **Readability** - Clear pipeline flow with visual progress indicators  
✅ **Maintainability** - Business logic changes are isolated to specific functions  
✅ **Debuggability** - Can run and test individual transformation steps  
✅ **Professional Code Quality** - Clean data structures flow through pipeline  

### Visual Progress Indicators
Each transformation step shows progress:
```
⚙️ Calculating class durations...
⚙️ Applying base hourly rates...  
⚙️ Calculating attendance metrics...
⚙️ Applying bonus factors...
⚙️ Calculating final payment amounts...
⚙️ Adding summary totals...
⚙️ Formatting for Excel compatibility...
```

### Technical Implementation Notes
- **Data Structure:** Uses consistent `{"fieldnames": [...], "rows": [...]}` format
- **Error Handling:** Proper exceptions with logging and user-friendly console messages  
- **Configuration Integration:** Uses `config.base_hourly_rate` and `config.extra_fields`
- **Pipeline Pattern:** Functional approach where each step takes data and returns transformed data

This refactoring demonstrates the transformation from "works but ugly" code to professional, maintainable software architecture.

---

## Functional Pipeline Pattern: The Heart of Beautiful Data Processing

**Date:** August 17, 2025

During the processing.py refactoring, we implemented a beautiful **functional pipeline pattern** that deserves special attention:

### The Core Pattern
```python
def transform_data(raw_data):
    """Apply all transformation steps to the raw data."""
    transformations = [
        add_duration_calculations,
        add_base_rates,
        add_attendance_metrics,
        apply_bonus_factors,
        calculate_final_amounts,
        add_summary_row,
        prepare_fieldnames,
        format_for_excel,
    ]

    data = raw_data
    for transform in transformations:
        data = transform(data)
    
    return data
```

### How It Works Step-by-Step

1. **Start with raw data**: `data = raw_data` (contains fieldnames and filtered rows)

2. **Apply each transformation sequentially**: The loop calls each function in the transformations list, where each function takes the current data state and returns the enhanced data state.

3. **Data flows through the pipeline**:
   ```
   Raw CSV Data 
       ↓
   add_duration_calculations() → Data with "Dauer-in-Stunden" 
       ↓
   add_base_rates() → Data with base hourly rates
       ↓  
   add_attendance_metrics() → Data with attendance percentages
       ↓
   apply_bonus_factors() → Data with bonus multipliers
       ↓
   calculate_final_amounts() → Data with final payments
       ↓
   add_summary_row() → Data with monthly totals
       ↓
   prepare_fieldnames() → Data with all fields
       ↓
   format_for_excel() → Final processed data
   ```

### Why This Pattern is Brilliant

- **🔗 Composable**: Easy to add/remove/reorder transformations by modifying the list
- **🧪 Testable**: Each step can be tested independently with known input/output
- **📖 Readable**: The pipeline clearly shows the data transformation flow
- **🔧 Maintainable**: Changes to one step don't affect others (single responsibility)
- **🎯 Functional**: Each function is pure - takes data, returns transformed data
- **🚀 Scalable**: Can easily parallelize or optimize individual steps

### Technical Benefits

**Function Signature Pattern**: All transformation functions follow the same signature:
```python
def transform_step(data: dict) -> dict:
    # Modify data["rows"] and/or data structure
    return data
```

**Immutable-Style Processing**: While we modify the data dict for performance, the pattern encourages thinking about data transformations as pure functions.

**Error Isolation**: If one transformation fails, it's immediately clear which step caused the problem.

**Visual Progress**: Each step provides console feedback, making the pipeline execution transparent to users.

### Alternative Implementations

This pattern is also known as **"Pipes and Filters"** architecture and could be implemented with:

- **Functional reduce**: `data = functools.reduce(lambda d, f: f(d), transformations, raw_data)`
- **Method chaining**: `data.add_duration().add_rates().add_metrics()...` 
- **Async pipelines**: For I/O bound transformations
- **Stream processing**: For large datasets that don't fit in memory

This pipeline pattern is a cornerstone of functional programming and data processing systems, making complex transformations both understandable and maintainable.

---
