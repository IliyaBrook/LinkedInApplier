import json
import os


class ConfigurationManager:
    @staticmethod
    def load_settings(settings_path):
        """Load browser settings from file."""
        try:
            with open(settings_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            executable_path = data.get("executable_path", "")
            if not os.path.exists(executable_path):
                raise FileNotFoundError("Browser executable path not found.")
            
            return data, "Settings loaded successfully"
        except (FileNotFoundError, json.JSONDecodeError, OSError) as e:
            return None, f"Failed to load settings: {e}"

    @staticmethod
    def load_filters(filters_path):
        """Load job filters from file."""
        if not filters_path:
            return {}, "No filters_path provided"
        
        try:
            with open(filters_path, "r", encoding="utf-8") as f:
                filters = json.load(f)
            return filters, f"Successfully loaded filters from {filters_path}"
        except (FileNotFoundError, json.JSONDecodeError, OSError) as e:
            return {}, f"Failed to load filters: {e}"

    @staticmethod
    def load_autofill_data(autofill_path):
        """Load autofill data from file."""
        try:
            with open(autofill_path, "r", encoding="utf-8") as f:
                autofill_data = json.load(f)
            return autofill_data, "Autofill data loaded successfully"
        except (FileNotFoundError, json.JSONDecodeError, OSError) as e:
            return None, f"Failed to load autofill data: {e}"

    @staticmethod
    def load_configuration(autofill_path, filters_path=None):
        """Load both autofill data and filters in one call."""
        # Load autofill data
        autofill_data, autofill_message = ConfigurationManager.load_autofill_data(autofill_path)
        if autofill_data is None:
            return None, None, autofill_message
        
        # Load filters
        filters, filters_message = ConfigurationManager.load_filters(filters_path)
        
        return autofill_data, filters, f"Configuration loaded: {autofill_message}, {filters_message}"

    @staticmethod
    def validate_configuration(config_data, required_fields=None):
        """Validate configuration data has required fields."""
        if required_fields is None:
            required_fields = []
        
        missing_fields = []
        for field in required_fields:
            if field not in config_data or not config_data[field]:
                missing_fields.append(field)
        
        if missing_fields:
            return False, f"Missing required fields: {missing_fields}"
        
        return True, "Configuration validation passed"

    @staticmethod
    def get_safe_config_value(config_data, key, default_value=None):
        """Safely get configuration value with default fallback."""
        return config_data.get(key, default_value) if config_data else default_value