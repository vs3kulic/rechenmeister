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

## Next Steps
- Implement logic for each CLI menu option (ingestion, processing, PDF generation, log inspection).
- Continue summarizing key learnings and code changes after each interaction.

---

## Next Steps
- Implement logic for each CLI menu option (ingestion, processing, PDF generation, log inspection).
- Continue summarizing key learnings and code changes after each interaction.

---
