"""This is a sample test file for the Rechenmeister CLI tool."""
import unittest
import os
from configs.config import config
from modules.ingestion import ingest_file

class TestIngestion(unittest.TestCase):
    """Test cases for the ingestion functionality of Rechenmeister."""
    def setUp(self):
        """Set up test environment."""
        # Check if the testing mode is enabled
        if not os.getenv("TESTING_MODE", default="false").lower() == "true":
            raise EnvironmentError("Testing mode is not enabled. Set TESTING_MODE to 'true'.")

        # Set the directories and patterns from the config
        self.downloads_folder = config.source_directory
        self.source_file_pattern = config.source_file_pattern
        self.target_directory = config.target_directory

    def test_ingestion_functionality(self):
        """Test the ingestion functionality."""
        # Perform the ingestion
        ingest_file()

        # Assert the file was moved and renamed correctly
        files = os.listdir(self.target_directory)
        self.assertTrue(len(files) > 0, "No files found in target directory.")

if __name__ == "__main__":
    unittest.main()
