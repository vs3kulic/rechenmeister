"""Configuration loader for Rechenmeister."""
import yaml
import os
from pathlib import Path

class Config:
    """Configuration manager for Rechenmeister settings."""
    
    def __init__(self, config_path=None):
        """Load configuration from YAML file."""
        config_path = config_path or Path(__file__).parent / "config.yaml"
        self.config_path = config_path
        self._config = self._load_config()
    
    def _load_config(self):
        """Load configuration from YAML file."""
        config_file = Path(self.config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        with open(config_file, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    
    def get(self, section, key, default=None):
        """Get a configuration value."""
        return self._config.get(section, {}).get(key, default)
    
    # Ingestion settings
    @property
    def source_directory(self):
        return os.path.expanduser(self.get('ingestion', 'source_directory'))
    
    @property
    def target_directory(self):
        return self.get('ingestion', 'target_directory')
    
    @property
    def source_file_pattern(self):
        return self.get('ingestion', 'source_file_pattern')
    
    @property
    def output_filename_format(self):
        return self.get('ingestion', 'output_filename_format')
    
    @property
    def auto_create_directories(self):
        return self.get('ingestion', 'auto_create_directories', True)
    
    # Processing settings
    @property
    def base_hourly_rate(self):
        return self.get('processing', 'base_hourly_rate', 20.0)
    
    @property
    def processing_output_directory(self):
        return self.get('processing', 'output_directory')
    
    # Generation settings
    @property
    def generation_output_directory(self):
        return self.get('generation', 'output_directory')
    
    @property
    def pdf_filename_format(self):
        return self.get('generation', 'filename_format')
    
    # Logging settings
    @property
    def logs_directory(self):
        return self.get('logging', 'directory')
    
    @property
    def log_filename(self):
        return self.get('logging', 'filename')

# Global config instance
config = Config()
