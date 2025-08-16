"""This module provides a command-line interface for the Rechenmeister invoice automation system."""
import os
import glob
import logging
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt
from rich.table import Table
from rich import box

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
    table.add_row("4", "📜 Inspection (Log review)")
    table.add_row("5", "🚪 Exit")
    console.print(table)

    # Prompt the user for their choice
    choice = IntPrompt.ask("Choose an option", choices=["1", "2", "3", "4", "5"])

    return choice

def ingest_file():
    """Handle the ingestion of the source file."""
    # Print the ingestion selection message, log the start of the process
    console.print("📥 [green]Ingestion selected.[/green]")
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
    except Exception as e:
        logging.error("Failed to move and rename file: %s", e)
        raise IOError(f"Failed to move and rename file: {e}") from e

    logging.info("Ingestion process completed.")

def process_file():
    """Handle the processing of the source file."""
    console.print("🛠 [green]Processing selected.[/green]")
    # Implement processing logic here

def generate_invoice():
    """Handle the generation of the PDF invoice."""
    console.print("🧾 [green]Generate invoice selected.[/green]")
    # Implement PDF generation logic here

def inspect_log():
    """Handle the inspection of logs."""
    console.print("📜 [green]Inspect log selected.[/green]")
    # Implement log inspection logic here

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
                inspect_log()
            elif selection == 5:
                console.print("👋 [bold blue]Goodbye![/bold blue]")
                break
        except FileNotFoundError as fnf_err:
            console.print(f"[bold red]Error:[/bold red] {fnf_err}")
        except IOError as io_err:
            console.print(f"[bold red]File operation error:[/bold red] {io_err}")

if __name__ == "__main__":
    main()
