"""This module provides a command-line interface for the Rechenmeister invoice automation system."""
import os
import logging
from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt
from rich.table import Table
from rich import box
from modules.ingestion import ingest_file
from modules.processing import process_file
from modules.generation import generate_invoice
from configs.config import config

# Configure logging
logging.basicConfig(
    filename=os.path.join(config.logs_directory, config.log_filename),
    level=getattr(logging, config.get('logging', 'level', 'INFO')),
    format='%(asctime)s %(levelname)s: %(message)s'
)

# Initialize the console for rich output
console = Console()

# Main menu function to display options and handle user input
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
