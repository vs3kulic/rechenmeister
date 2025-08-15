# Notes

## CLI-Tool
Key features to use:

- Panel for banners and section headers
- Table for menu options
- Prompt and IntPrompt for user input
- Modular functions for each menu action:
  -For each option, call a function (e.g., ingest_file(), process_file(), generate_invoice(), inspect_log()).
- Markdown rendering for logs or reports

## Learnings

### String vs. integer arguments

The Table.add_row() method expects its arguments to be strings, not integers.

The choices argument in IntPrompt.ask() expects a list of strings, not integers. This is because user input from the terminal is always received as a string, and choices is used to validate that input before converting it to an integer.

So, you use quotation marks in choices for input validation, but the returned value is an integer, which you then compare as if selection == 1: in your control flow.

```

## Session Summary (15 August 2025)

- Set up a Python CLI tool using the rich library for a visually appealing menu.
- Discussed best practices for main control flow in Python scripts (using the main guard and refactoring into a main() function).
- Explored how to use rich's Table, Panel, and IntPrompt for user interaction.
- Clarified why menu options and IntPrompt choices use strings for display and input validation, but return integers for control flow.
- Confirmed that static analysis errors about rich imports were false positives, and the CLI works as expected.
- Agreed to update this notes.md file with a summary after each exchange for learning and exam preparation.

---

## Next Steps
- Implement logic for each CLI menu option (ingestion, processing, PDF generation, log inspection).
- Continue summarizing key learnings and code changes after each interaction.

---

## Session Summary (15 August 2025, continued)

- Explored logging strategies for CLI tools, comparing file-based logging (like move.log in a7_ex2.py) and Python's logging module.
- Added logging to meister.py using a log file (meister.log) and CLI log inspection, then discussed and reverted changes for further refinement.
- Practiced file ingestion with dynamic file naming using datetime formatting (e.g., aktivitaetsbericht-08-2025.csv).
- Clarified Python string formatting: `02d` means zero-padded, two-digit integer.
- Discussed best practices for main control flow and error handling in CLI scripts.

---
