"""This module performs the processing of activity exports for the Rechenmeister tool."""
import os
import glob
import logging
import pandas as pd
import csv
from rich.console import Console
from config import config

# Initialize the console for rich output
console = Console()

def discover_input_file():
    """Find and return the path to the input CSV file."""
    input_folder = "input_csv"
    input_file_pattern = "aktivitaetsbericht-*.csv"
    input_file_list = glob.glob(os.path.join(input_folder, input_file_pattern))

    if not input_file_list:
        logging.error("No valid input CSV file found in 'input_csv' directory.")
        raise FileNotFoundError("No valid input CSV file found in 'input_csv' directory.")

    input_file = input_file_list[0]
    logging.info("Using input file: %s", input_file)
    return input_file

def load_and_validate_csv(input_file):
    """Load CSV data and validate required columns are present."""
    # Read the CSV file as a DataFrame for validation
    dataframe = pd.read_csv(input_file, delimiter=";")
    required_cols = ["Datum", "Name", "Trainer"]
    missing_cols = [col for col in required_cols if col not in dataframe.columns]

    if not missing_cols:
        logging.info("All required columns are present in the input file.")
        console.print("✅ [yellow]All required columns are present in the input file...[/yellow]")
    else:
        logging.error("Missing required columns: %s", ', '.join(missing_cols))
        console.print(f"[bold red]Error:[/bold red] Missing required columns: {', '.join(missing_cols)}")
        raise ValueError(f"Missing required columns in the input file: {', '.join(missing_cols)}")

    # Load the actual data using csv.DictReader
    with open(input_file, newline='', encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=";")
        if reader.fieldnames is None:
            raise ValueError("Input CSV file is empty or missing header row.")

        fieldnames = [head.strip() for head in reader.fieldnames]
        filtered_rows = [row for row in reader
                        if row.get("Status") not in ("Storniert", "Abgesagt")
                        and row.get("Trainer") == "Victoria"]

    if not filtered_rows:
        logging.error("No valid classes found in the input file after filtering.")
        console.print("[bold red]Error:[/bold red] No valid classes found in the input file after filtering.")
        raise ValueError("No valid classes found in the input file after filtering.")

    logging.info("Loaded %d valid classes for processing.", len(filtered_rows))
    return {"fieldnames": fieldnames, "rows": filtered_rows}

def time_to_decimal(time_str):
    """Helper function to convert time in HH:MM format to decimal hours."""
    hours, minutes = map(int, time_str.split(":"))
    return hours + minutes / 60

def add_duration_calculations(data):
    """Add duration calculations in hours to each row."""
    console.print("⚙️ [yellow]Calculating class durations...[/yellow]")

    for row in data["rows"]:
        start_time = time_to_decimal(row["Startzeit"])
        end_time = time_to_decimal(row["Endzeit"])
        duration = end_time - start_time
        row["Dauer-in-Stunden"] = f"{duration:.1f}"

    return data

def add_base_rates(data):
    """Add base hourly rates to each row."""
    console.print("⚙️ [yellow]Applying base hourly rates...[/yellow]")

    for row in data["rows"]:
        row["Stundensatz-Basis"] = config.base_hourly_rate

    return data

def add_attendance_metrics(data):
    """Calculate and add attendance rate (registration rate) to each row."""
    console.print("⚙️ [yellow]Calculating attendance metrics...[/yellow]")

    for row in data["rows"]:
        registered = int(row.get("Angemeldet", "0"))
        max_participants = int(row.get("Max. Teilnehmer", "8"))
        registration_rate = registered / max_participants
        row["Anmeldequote"] = f"{(registration_rate * 100):.1f}%"

    return data

def apply_bonus_factors(data):
    """Apply bonus factors based on attendance rates."""
    console.print("⚙️ [yellow]Applying bonus factors...[/yellow]")

    for row in data["rows"]:
        if row["Anmeldequote"] == "100.0%":
            row["Bonus-Faktor"] = 2.0
        elif row["Anmeldequote"] == "50.0%":
            row["Bonus-Faktor"] = 1.5
        else:
            row["Bonus-Faktor"] = 1.0

    return data

def calculate_final_amounts(data):
    """Calculate final hourly rates and total amounts."""
    console.print("⚙️ [yellow]Calculating final payment amounts...[/yellow]")

    for row in data["rows"]:
        # Final hourly rate with bonus
        final_rate = float(row['Stundensatz-Basis']) * float(row['Bonus-Faktor'])
        row["Stundensatz-Final"] = f"{final_rate:.2f}"

        # Total payment for this class
        total_amount = final_rate * float(row['Dauer-in-Stunden'])
        row["Stundenbetrag"] = f"{total_amount:.2f}"

    return data

def add_summary_row(data):
    """Add a summary row with totals."""
    console.print("⚙️ [yellow]Adding summary totals...[/yellow]")

    # Calculate totals
    total_hours = sum(float(row["Dauer-in-Stunden"]) for row in data["rows"])
    total_payment = sum(float(row["Stundensatz-Final"]) * float(row["Dauer-in-Stunden"])
                       for row in data["rows"])

    # Create summary row
    summary_row = {key: "" for key in data["fieldnames"]}
    summary_row["Datum"] = "Gesamt (Monat)"
    summary_row["Dauer-in-Stunden"] = f"{total_hours:.1f}"
    summary_row["Stundenbetrag"] = f"{total_payment:.2f}"

    data["summary_row"] = summary_row
    return data

def prepare_fieldnames(data):
    """Ensure all extra fields are included in fieldnames."""
    for field in config.extra_fields:
        if field not in data["fieldnames"]:
            data["fieldnames"].append(field)

    # Ensure all rows have all fieldnames
    for row in data["rows"]:
        for key in data["fieldnames"]:
            if key not in row:
                row[key] = None

    return data

def excel_friendly(value):
    """Convert a value to a format suitable for Excel (dots to commas)."""
    if isinstance(value, str) and "." in value:
        return value.replace(".", ",")
    return value

def format_for_excel(data):
    """Convert decimal points to commas for Excel compatibility."""
    console.print("⚙️ [yellow]Formatting for Excel compatibility...[/yellow]")

    numeric_columns = ["Dauer-in-Stunden", "Stundensatz-Basis", "Bonus-Faktor", 
                       "Stundensatz-Final", "Stundenbetrag"]

    # Format data rows
    for row in data["rows"]:
        for col in numeric_columns:
            if col in row:
                row[col] = excel_friendly(str(row[col]))

    # Format summary row
    for col in ["Dauer-in-Stunden", "Stundenbetrag"]:
        if col in data["summary_row"]:
            data["summary_row"][col] = excel_friendly(str(data["summary_row"][col]))

    return data

def save_processed_data(data, input_file):
    """Save processed data to output CSV file."""
    output_folder = config.processing_output_directory or "output_csv"
    os.makedirs(output_folder, exist_ok=True)
    output_file = os.path.join(output_folder, f"processed-{os.path.basename(input_file)}")

    try:
        with open(output_file, 'w', newline='', encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=data["fieldnames"], delimiter=";")
            writer.writeheader()
            writer.writerows(data["rows"])
            writer.writerow(data["summary_row"])

        logging.info("Processed data written to '%s'.", output_file)
        return output_file
    except Exception as e:
        logging.error("Failed to write processed data to output file: %s", e)
        console.print(f"[bold red]Error:[/bold red] Failed to write processed data to output file: {e}")
        raise IOError(f"Failed to write processed data to output file: {e}") from e

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

def process_file():
    """Main orchestrator for the processing workflow."""
    console.print("🛠 [green]Processing selected.[/green]")
    console.print("🛠 [yellow]Processing...[/yellow]")
    logging.info("Started processing file.")

    try:
        input_file = discover_input_file()
        raw_data = load_and_validate_csv(input_file)
        processed_data = transform_data(raw_data)
        output_file = save_processed_data(processed_data, input_file)

        console.print(f"🛠 [green]Processing completed. Processed data written to {output_file}.[/green]")
        logging.info("Processing completed successfully.")
    except Exception as e:
        logging.error("Processing failed: %s", e)
        raise
