# Notes

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
