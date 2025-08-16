"""This module handles file ingestion - moving and renaming source files."""
import os
import glob
import logging
from datetime import datetime
from rich.console import Console
from .config import config

# Initialize the console for rich output
console = Console()

def ingest_file():
    """Handle the ingestion of the source file."""
    # Print the ingestion selection message, log the start of the process
    console.print("📥 [green]Ingestion selected.[/green]")
    logging.info("Started ingestion process.")

    # Get configuration values
    downloads_folder = config.source_directory
    source_file_pattern = config.source_file_pattern
    target_directory = config.target_directory
    
    source_file_list = glob.glob(os.path.join(downloads_folder, source_file_pattern))

    # Check if the target directory exists, create it if not
    if not os.path.exists(target_directory):
        if config.auto_create_directories:
            os.makedirs(target_directory)
            logging.info("Created target directory: %s", target_directory)
        else:
            raise FileNotFoundError(f"Target directory does not exist: {target_directory}")

    # Check if there is a (matching) source file list
    if not source_file_list:
        logging.error("No matching source file found!")
        raise FileNotFoundError(f"No source file matching pattern '{source_file_pattern}' found in {downloads_folder}.")

    # Get the first source file from the list
    source_file_path = source_file_list[0]
    logging.info("Found source file: %s", source_file_path)

    # Define the new file name using config format
    now = datetime.now()
    new_file_name = config.output_filename_format.format(month=now.month, year=now.year)
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
