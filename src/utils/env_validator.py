"""
Environment variable validation utilities for the AI Resume Optimization Tool.
Ensures all required settings are properly configured before running the application.
"""
import os
import sys
from typing import Dict, List, Optional, Set, Tuple


class EnvValidator:
    """Validator for environment variables."""

    def __init__(self):
        """Initialize the environment validator."""
        self.required_vars = {
            "OPENAI_API_KEY": "OpenAI API key for AI functionality"
        }

        self.optional_vars = {
            "OVERLEAF_TOKEN": "Overleaf API token for Overleaf integration",
            "MODEL": "OpenAI model to use (default: gpt-4-turbo)",
            "MAX_TOKENS": "Maximum tokens for AI response (default: 2000)",
            "FLASK_SECRET_KEY": "Secret key for Flask sessions (auto-generated if not set)",
            "PORT": "Port for the web application (default: 5001)",
            "DEBUG": "Enable debug mode for Flask (default: False)"
        }

    def validate(self, suppress_warnings: bool = False) -> Tuple[bool, List[str]]:
        """
        Validate the environment variables.

        Args:
            suppress_warnings: If True, don't print warnings for missing optional vars

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        warnings = []

        # Check required variables
        for var, description in self.required_vars.items():
            if not os.getenv(var):
                errors.append(f"Missing required environment variable: {var} - {description}")

        # Check optional variables
        for var, description in self.optional_vars.items():
            if not os.getenv(var):
                warnings.append(f"Missing optional environment variable: {var} - {description}")

        # Print warnings if needed
        if warnings and not suppress_warnings:
            print("Warning: Some optional environment variables are not set:")
            for warning in warnings:
                print(f"  - {warning}")
            print()

        return len(errors) == 0, errors

    def validate_or_exit(self, suppress_warnings: bool = False) -> None:
        """
        Validate the environment variables or exit if validation fails.

        Args:
            suppress_warnings: If True, don't print warnings for missing optional vars
        """
        is_valid, errors = self.validate(suppress_warnings)
        
        if not is_valid:
            print("Error: Missing required environment variables:")
            for error in errors:
                print(f"  - {error}")
            print("\nPlease set these variables in your .env file or environment and try again.")
            sys.exit(1)

    def get_env(self, var: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get an environment variable with a default value.

        Args:
            var: Variable name
            default: Default value if not set

        Returns:
            The environment variable value or the default
        """
        return os.getenv(var, default)

    def print_config_summary(self) -> None:
        """Print a summary of the current configuration."""
        print("=== Environment Configuration ===")
        
        # Print required variables (safely masked)
        for var in self.required_vars:
            value = os.getenv(var)
            if value:
                masked_value = value[:4] + '*' * (len(value) - 4) if len(value) > 4 else '****'
                print(f"{var}: {masked_value}")
            else:
                print(f"{var}: Not set")
        
        # Print optional variables (safely masked for tokens)
        for var in self.optional_vars:
            value = os.getenv(var)
            if value and ('TOKEN' in var or 'KEY' in var):
                masked_value = value[:4] + '*' * (len(value) - 4) if len(value) > 4 else '****'
                print(f"{var}: {masked_value}")
            else:
                print(f"{var}: {value or 'Not set'}")
        
        print("=================================")
