
"""This is the first pass for Rechenmeister, implementing the file ingestion functionality."""
import os
import glob
from datetime import datetime

def ingest_file():
    """Handle the ingestion of the source file."""
    # Define the source file path and the target directory
    downloads_folder = os.path.expanduser("~/Downloads")
    source_file_pattern = "Aktivitätsbericht von Alle Aktivitätstypen *.csv"
    source_file_list = glob.glob(os.path.join(downloads_folder, source_file_pattern))
    target_directory = "input_csv"

    # Create the target directory if it does not exist
    if not os.path.exists(target_directory):
        os.makedirs(target_directory)

    # Search for the source file in the Downloads folder
    if not source_file_list:
        raise FileNotFoundError(f"No source file matching pattern '{source_file_pattern}' found in {downloads_folder}.")
    source_file_path = source_file_list[0]

    # Define the new file name
    now = datetime.now()
    new_file_name = f"aktivitaetsbericht-{now.month:02d}-{now.year}.csv"
    target_file_path = os.path.join(target_directory, new_file_name)

    # Move and rename the file
    try:
        os.rename(source_file_path, target_file_path)
        print(f"File moved and renamed to '{target_file_path}'.")
    except Exception as e:
        raise IOError(f"Failed to move and rename file: {e}") from e

def main():
    """Main function to run the ingestion process."""
    try:
        ingest_file()
    except Exception as e:
        print(f"An error occurred during file ingestion: {e}")
    
if __name__ == "__main__":
    main()
