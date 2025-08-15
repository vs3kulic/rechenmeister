# Notes

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
