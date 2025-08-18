# Rechenmeister - Invoice Automation

## Overview

Automated invoice generation system for partners based on a class-based flat rate billing model with bonus incentives.

## Implementation

- Python-based command-line utility for automated invoice processing.
- Supports four main operations via interactive CLI menu:
  - File Ingestion: Move and rename source CSV to `input_csv/`.
  - Data Processing: Filter, compute billing columns, output to `output_csv/`.
  - PDF Generation: Render invoice data from CSV to PDF and save to `output_pdf/`.
  - Log Inspection: View operation logs for auditing and troubleshooting.
- Modular codebase: CSV I/O, data transformation, PDF rendering, and logging are separated into distinct components.

## Project Structure

```
rechenmeister/
├── configs/          # Configuration files (e.g., config.yaml)
├── input_csv/        # Input CSV files for processing
├── logs/             # Log files for auditing
├── modules/          # Core application modules
│   ├── ingestion.py  # Handles file ingestion
│   ├── processing.py # Data processing logic
│   ├── generation.py # PDF generation logic
│   └── rechenmeister.py # Main CLI entry point
├── output_csv/       # Processed CSV output files
├── output_pdf/       # Generated PDF invoices
├── requirements.txt  # Python dependencies
└── README.md         # Project documentation
```

## Tips for Running the Tool

- Ensure you have Python 3.8 or higher installed.
- Install the required dependencies using:
  ```bash
  pip install -r requirements.txt
  ```
- Run the tool as a module from the project root directory:
  ```bash
  python -m modules.rechenmeister
  ```
- Use the interactive CLI menu to select operations such as ingestion, processing, PDF generation, or log inspection.
- Place input CSV files in the `input_csv/` directory before running the ingestion step.
- Check the `logs/` directory for detailed logs in case of errors or unexpected behavior.
- Output files will be saved in the `output_csv/` and `output_pdf/` directories.

