"""This module implements the first pass for the processing functionality."""
import os
import glob
import logging
import pandas as pd
import csv
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt
from rich.table import Table
from rich import box

# CONSTANTS
BASE_HOURLY_RATE = 20.0  # Default hourly rate in Euros, can be extended to dict or config file
EXTRA_FIELDS = [
        "Dauer-in-Stunden",
        "Stundensatz-Basis",
        "Anmeldequote",
        "Bonus-Faktor",
        "Stundensatz-Final"
    ]

# Configure logging
LOGS_DIR = 'logs'
LOG_NAME = 'action.log'
os.makedirs(LOGS_DIR, exist_ok=True)

logging.basicConfig(
    filename = os.path.join(LOGS_DIR, LOG_NAME),
    level = logging.INFO,
    format = '%(asctime)s %(levelname)s: %(message)s'
)

# Initialize the console for rich output
console = Console()

def main_menu():
    """Display the main menu and return the user's choice."""
    # Display the main menu with options
    console.print(Panel.fit("[bold blue]Rechenmeister Invoice Automation[/bold blue]", border_style="blue"))

    # Create a table for the menu options
    table = Table(show_header=False, box=box.ROUNDED)
    table.add_column("Option", style="cyan", width=8)
    table.add_column("Description", style="white")
    table.add_row("1", "📥 Ingestion (Move and rename source file)")
    table.add_row("2", "🛠  Processing (Extend the source file)")
    table.add_row("3", "🧾 Generation (Create PDF invoice)")
    table.add_row("4", "🚪 Exit")
    console.print(table)

    # Prompt the user for their choice
    choice = IntPrompt.ask("Choose an option", choices=["1", "2", "3", "4"])

    return choice

def ingest_file():
    """Handle the ingestion of the source file."""
    # Print the ingestion selection message, log the start of the process
    console.print("📥 [green]Ingestion selected.[/green]")
    console.print("📥 [yellow]Ingesting...[/yellow]")
    logging.info("Started ingestion process.")

    # Define the source file path, file pattern, the list of files and target directory
    downloads_folder = os.path.expanduser("~/Downloads")
    source_file_pattern = "Aktivitätsbericht von Alle Aktivitätstypen *.csv"
    source_file_list = glob.glob(os.path.join(downloads_folder, source_file_pattern))
    target_directory = "input_csv"

    # Check if the target directory exists, create it if not
    if not os.path.exists(target_directory):
        os.makedirs(target_directory)
        logging.info("Created target directory: %s", target_directory)

    # Check if there is a (matching) source file list
    if not source_file_list:
        logging.error("No matching source file found!")
        raise FileNotFoundError(f"No source file matching pattern '{source_file_pattern}' found in {downloads_folder}.")

    # Get the first source file from the list
    source_file_path = source_file_list[0]
    logging.info("Found source file: %s", source_file_path)

    # Define the new file name
    now = datetime.now()
    new_file_name = f"aktivitaetsbericht-{now.month:02d}-{now.year}.csv"
    target_file_path = os.path.join(target_directory, new_file_name)

    # Move and rename the file
    try:
        os.rename(source_file_path, target_file_path)
        logging.info("File moved and renamed to '%s'.", target_file_path)
        console.print(f"📥 [green]File successfully ingested and renamed to {new_file_name}.[/green]")
    except Exception as e:
        logging.error("Failed to move and rename file: %s", e)
        raise IOError(f"Failed to move and rename file: {e}") from e

    logging.info("Ingestion process completed.")

def process_file():
    """Handle the processing of the source file."""
    console.print("🛠 [green]Processing selected.[/green]")
    console.print("🛠 [yellow]Processing...[/yellow]")
    logging.info("Started processing file.")

    # Define the input file path and check if it exists
    input_folder = "input_csv"
    input_file_pattern = "aktivitaetsbericht-*.csv"
    input_file_list = glob.glob(os.path.join(input_folder, input_file_pattern))
    if not input_file_list:
        logging.error("No valid input CSV file found in 'input_csv' directory.")
        raise FileNotFoundError("No valid input CSV file found in 'input_csv' directory.")
    input_file = input_file_list[0]
    
    # Define the output file path
    output_folder = "output_csv"
    os.makedirs(output_folder, exist_ok=True)
    output_file = os.path.join(output_folder, f"processed_{os.path.basename(input_file)}")    

    # Read the CSV file as a DataFrame, check for missing columns
    dataframe = pd.read_csv(input_file, delimiter = ";")
    required_cols = ["Datum", "Name", "Trainer"]
    missing_cols = [col for col in required_cols if col not in dataframe.columns]

    if not missing_cols:
        logging.info("All required columns are present in the input file.")
        console.print("✅ [yellow]All required columns are present in the input file...[/yellow]")
    else:
        logging.error("Missing required columns: %s", ', '.join(missing_cols))
        console.print(f"[bold red]Error:[/bold red] Missing required columns: {', '.join(missing_cols)}")
        raise ValueError(f"Missing required columns in the input file: {', '.join(missing_cols)}")

    # Open the input file and assign a file handle
    with open(input_file, newline='', encoding="utf-8") as csvfile:
        # Read the CSV file into a DictReader object
        reader = csv.DictReader(csvfile, delimiter = ";")
        if reader.fieldnames is None:
            raise ValueError("Input CSV file is empty or missing header row.")
        # Get the fieldnames from the reader, store them in a list
        fieldnames = [head.strip() for head in reader.fieldnames]

        # Filter rows based on status and trainer
        filtered_rows = [row for row in reader 
                         if row.get("Status") not in ("Storniert", "Abgesagt")
                         and row.get("Trainer") == "Victoria"
                         ]

    # Add a new column "Dauer-in-Stunden" - Duration in hours
    def time_to_decimal(time):
        """Helper function to convert time in HH:MM format to decimal hours."""
        hours, minutes = map(int, time.split(":"))
        return hours + minutes / 60

    for row in filtered_rows:
        start_time = time_to_decimal(row["Startzeit"])
        end_time = time_to_decimal(row["Endzeit"])
        duration = end_time - start_time
        row["Dauer-in-Stunden"] = f"{duration:.1f}"

    # Add a new column "Stundensatz" with a default value
    for row in filtered_rows:
        row["Stundensatz-Basis"] = BASE_HOURLY_RATE
 
    # Add a new column "Anmeldequote" - Registration rate
    for row in filtered_rows:
        registered = int(row.get("Angemeldet", "0"))
        max_participants = int(row.get("Max. Teilnehmer", "8"))
        registration_rate = registered / max_participants
        row["Anmeldequote"] = f"{(registration_rate * 100):.1f}%"

    # Add a new column "Bonus-Faktor", based on the registration rate
    for row in filtered_rows:
        if row["Anmeldequote"] == "100.0%":
            row["Bonus-Faktor"] = 2.0
        elif row["Anmeldequote"] == "50.0%":
            row["Bonus-Faktor"] = 1.5
        else:
            row["Bonus-Faktor"] = 1.0

    # Add a new column "Stundensatz_Final" - Final hourly rate including bonus
    for row in filtered_rows:
        row["Stundensatz-Final"] = f"{float(row['Stundensatz-Basis']) * float(row['Bonus-Faktor']):.2f}"

    # Calculate the total hours
    total_hours = sum(float(row["Dauer-in-Stunden"]) for row in filtered_rows)

    # Calculate the total payment
    total_payment = sum(float(row["Stundensatz-Final"]) * float(row["Dauer-in-Stunden"])
                         for row in filtered_rows
                        )

    # Add new columns to the fieldnames object (if they are not already present)
    for field in EXTRA_FIELDS:
        if field not in fieldnames:
            fieldnames.append(field)

    # Checks if each key (column head from fieldnames) exists in the current row's dictionary.
    for row in filtered_rows:
        for key in fieldnames:
            if key not in row:
                row[key] = "n/a" # Fill missing fields with 'n/a'

    # Check if there are any filtered rows after processing
    if not filtered_rows:
        logging.error("No valid classes found in the input file after filtering.")
        console.print("[bold red]Error:[/bold red] No valid classes found in the input file after filtering.")
        raise ValueError("No valid classes found in the input file after filtering.")

    # Write the CSV
    try:
        with open(output_file, 'w', newline='', encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=";")
            writer.writeheader()
            writer.writerows(filtered_rows)
        logging.info("Processed data written to '%s'.", output_file)
        console.print(f"🛠 [green]Processing completed. Processed data written to {output_file}.[/green]")
    except Exception as e:
        logging.error("Failed to write processed data to output file: %s", e)
        console.print(f"[bold red]Error:[/bold red] Failed to write processed data to output file: {e}")
        raise IOError(f"Failed to write processed data to output file: {e}") from e

def generate_invoice():
    """Handle the generation of the PDF invoice."""
    console.print("🧾 [green]Generate invoice selected.[/green]")
    # Implement PDF generation logic here

def main():
    """The main function to run the Rechenmeister CLI."""
    while True:
        selection = main_menu()
        try:
            if selection == 1:
                ingest_file()
            elif selection == 2:
                process_file()
            elif selection == 3:
                generate_invoice()
            elif selection == 4:
                console.print("👋 [bold blue]Goodbye![/bold blue]")
                break
        except FileNotFoundError as fnf_err:
            console.print(f"[bold red]Error:[/bold red] {fnf_err}")
        except IOError as io_err:
            console.print(f"[bold red]File operation error:[/bold red] {io_err}")

if __name__ == "__main__":
    main()
