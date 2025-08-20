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
- Testing is supported through Python's built-in `unittest` framework.

## Project Structure

```
rechenmeister/
├── configs/          # Configuration files (e.g., config.yaml)
├── input_csv/        # Input CSV files for processing
├── logs/             # Log files for auditing
├── tests/            # Testing directories and files
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

## Testing

The Rechenmeister CLI tool includes unit tests to ensure the functionality of its modules. The tests are written using Python's built-in `unittest` framework.

### Setting Up Testing Mode
To run the tests, you need to enable the testing mode by setting the `TESTING_MODE` environment variable to `true`. This ensures that the application uses the testing-specific configuration defined in the `config.yaml` file.

#### Steps to Enable Testing Mode
1. Open your terminal.
2. Set the `TESTING_MODE` environment variable:
   ```bash
   export TESTING_MODE=true
   ```
3. Run the tests using the following command:
   ```bash
   python -m unittest discover tests
   ```

### Configuration for Testing
The `config.yaml` file includes dedicated sections for testing configurations e.g., `ingestion_testing`. This section defines the directories and file patterns used during testing. For example:

```yaml
ingestion_testing:
  source_directory: tests/mock_source_dir
  target_directory: tests/mock_target_dir
  source_file_pattern: "*.csv"
```

When `TESTING_MODE` is set to `true`, the application automatically uses the `ingestion_testing` configuration instead of the production `ingestion` configuration.

### Notes
- Ensure that the mock directories and files required for testing are set up before running the tests.
- Reset the `TESTING_MODE` environment variable to `false` after testing to return to production mode:
  ```bash
  export TESTING_MODE=false
  ```

