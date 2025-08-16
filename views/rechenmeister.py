"""This module provides a command-line interface for the Rechenmeister invoice automation system."""
import os
import glob
import logging
import pandas as pd
import csv
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table as PDFTable, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt
from rich.table import Table
from rich import box

# Import the ingestion module
from .ingestion import ingest_file

# CONSTANTS
BASE_HOURLY_RATE = 20.0  # Default hourly rate in Euros, can be extended to dict or config file
EXTRA_FIELDS = [
        "Dauer-in-Stunden",
        "Stundensatz-Basis",
        "Anmeldequote",
        "Bonus-Faktor",
        "Stundensatz-Final",
        "Stundenbetrag"
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
    table.add_row("99", "🚪 Exit")
    console.print(table)

    # Prompt the user for their choice
    choice = IntPrompt.ask("Choose an option", choices=["1", "2", "3", "99"])

    return choice

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
    output_file = os.path.join(output_folder, f"processed-{os.path.basename(input_file)}")

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

    # Add a new column "Stundenbetrag" - Total hourly rate
    for row in filtered_rows:
        row["Stundenbetrag"] = f"{float(row['Stundensatz-Final']) * float(row['Dauer-in-Stunden']):.2f}"

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
                row[key] = None # Add missing keys with None value

    # Check if there are any filtered rows after processing
    if not filtered_rows:
        logging.error("No valid classes found in the input file after filtering.")
        console.print("[bold red]Error:[/bold red] No valid classes found in the input file after filtering.")
        raise ValueError("No valid classes found in the input file after filtering.")

    # Add summary row as the final line
    summary_row = {key: "" for key in fieldnames}
    summary_row["Datum"] = "Gesamt (Monat)"
    summary_row["Dauer-in-Stunden"] = f"{total_hours:.1f}"
    summary_row["Stundenbetrag"] = f"{total_payment:.2f}"

    # Define a function to convert values to a format suitable for Excel
    def excel_friendly(value):
        """Convert a value to a format suitable for Excel."""
        if isinstance(value, str) and "." in value:
            return value.replace(".", ",")
        return value

    for row in filtered_rows:
        for col in ["Dauer-in-Stunden", "Stundensatz-Basis", "Bonus-Faktor", "Stundensatz-Final", "Stundenbetrag"]:
            if col in row:
                row[col] = excel_friendly(str(row[col]))

    for col in ["Dauer-in-Stunden", "Stundenbetrag"]:
        summary_row[col] = excel_friendly(str(summary_row[col]))

    try:
        with open(output_file, 'w', newline='', encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=";")
            writer.writeheader()
            writer.writerows(filtered_rows)
            writer.writerow(summary_row)
        logging.info("Processed data written to '%s'.", output_file)
        console.print(f"🛠 [green]Processing completed. Processed data written to {output_file}.[/green]")
    except Exception as e:
        logging.error("Failed to write processed data to output file: %s", e)
        console.print(f"[bold red]Error:[/bold red] Failed to write processed data to output file: {e}")
        raise IOError(f"Failed to write processed data to output file: {e}") from e

def generate_invoice():
    """Handle the generation of the PDF invoice."""
    console.print("🧾 [green]Generate invoice selected.[/green]")

    def get_processed_csv():
        output_folder = "output_csv"
        output_file_pattern = "processed-*.csv"
        output_file_list = glob.glob(os.path.join(output_folder, output_file_pattern))
        if not output_file_list:
            logging.error("No processed CSV file found in 'output_csv' directory.")
            console.print("[bold red]Error:[/bold red] No processed CSV file found in 'output_csv' directory.")
            raise FileNotFoundError("No processed CSV file found in 'output_csv' directory.")
        logging.info("Using processed file: %s", output_file_list[0])
        console.print(f"🧾 [yellow]Using processed file: {output_file_list[0]}...[/yellow]")
        return output_file_list[0]

    def load_dataframe(csv_path):
        dataframe = pd.read_csv(csv_path, delimiter=";")
        if dataframe.empty:
            logging.error("Processed CSV file is empty.")
            console.print("[bold red]Error:[/bold red] Processed CSV file is empty.")
            raise ValueError("Processed CSV file is empty.")
        logging.info("Read processed CSV file into DataFrame.")
        return dataframe

    def build_pdf_table(dataframe):
        columns = ["Datum", "Name", "Stundenbetrag"]
        # Only keep selected columns, fill missing with blank
        df = dataframe.reindex(columns=columns, fill_value="")
        # Keep all rows including summary row
        df = df.replace({pd.NA: "", None: "", float('nan'): "", "nan": ""})
        # Prepare table data
        table_data = [columns]
        for _, row in df.iterrows():
            # For summary row, replace Name with "Summe"
            name_value = "Summe" if row.get("Datum", "").strip() == "Gesamt (Monat)" else row.get("Name", "")
            table_data.append([
                row.get("Datum", ""),
                name_value,
                row.get("Stundenbetrag", "")
            ])
        col_widths = [120, 180, 100]  # px widths for columns
        table = PDFTable(table_data, colWidths=col_widths)
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ])
        table.setStyle(style)
        return table

    csv_path = get_processed_csv()
    df = load_dataframe(csv_path)
    now = datetime.now()
    pdf_file_name = f"invoice-{now.month:02d}-{now.year}.pdf"
    pdf_dir = "output_pdf"
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_path = os.path.join(pdf_dir, pdf_file_name)
    logging.info("Creating PDF document: %s", pdf_path)
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    styles = getSampleStyleSheet()

    # Add header
    elements = [
        Spacer(1, 6),
        Paragraph(f"Stundenabrechnung {now.month:02d}/{now.year}", styles['Title']),
        Spacer(1, 12)
    ]

    # Add table
    table = build_pdf_table(df)
    elements.append(table)
    elements.append(Spacer(1, 12))

    try:
        doc.build(elements)
        logging.info("PDF invoice generated successfully: %s", pdf_path)
        console.print(f"🧾 [green]PDF invoice generated successfully: {pdf_path}.[/green]")
    except Exception as e:
        logging.error("Failed to generate PDF invoice: %s", e)
        console.print(f"[bold red]Error:[/bold red] Failed to generate PDF invoice: {e}")
        raise IOError(f"Failed to generate PDF invoice: {e}") from e

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
            elif selection == 99:
                console.print("👋 [bold blue]Goodbye![/bold blue]")
                break
        except FileNotFoundError as fnf_err:
            console.print(f"[bold red]Error:[/bold red] {fnf_err}")
        except IOError as io_err:
            console.print(f"[bold red]File operation error:[/bold red] {io_err}")

if __name__ == "__main__":
    main()
