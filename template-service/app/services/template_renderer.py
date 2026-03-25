import re
from typing import Dict, List, Tuple


class TemplateRenderer:
    """Service for rendering templates with variable substitution"""

    @staticmethod
    def extract_variables(text: str) -> List[str]:
        """
        Extract all variables from template text.
        Variables are in the format: {{variable_name}}
        """
        if not text:
            return []
        pattern = r'\{\{([a-zA-Z_][a-zA-Z0-9_]*)\}\}'
        matches = re.findall(pattern, text)
        return list(set(matches))  # Return unique variables

    @staticmethod
    def render(text: str, variables: Dict[str, any]) -> Tuple[str, List[str]]:
        """
        Render template by substituting variables.

        Args:
            text: Template text with {{variable}} placeholders
            variables: Dictionary of variable name -> value

        Returns:
            Tuple of (rendered_text, list_of_missing_variables)
        """
        if not text:
            return text, []

        # Extract all variables from template
        template_vars = TemplateRenderer.extract_variables(text)

        # Find missing variables
        missing_vars = [var for var in template_vars if var not in variables]

        # Replace variables
        rendered_text = text
        for var_name, var_value in variables.items():
            pattern = r'\{\{' + var_name + r'\}\}'
            rendered_text = re.sub(pattern, str(var_value), rendered_text)

        return rendered_text, missing_vars

    @staticmethod
    def validate_template(text: str) -> Tuple[bool, str, List[str]]:
        """
        Validate template syntax.

        Returns:
            Tuple of (is_valid, error_message, variables)
        """
        if not text:
            return False, "Template text cannot be empty", []

        # Check for mismatched braces
        open_count = text.count('{{')
        close_count = text.count('}}')

        if open_count != close_count:
            return False, "Mismatched template braces {{ }}", []

        # Extract variables
        variables = TemplateRenderer.extract_variables(text)

        # Check for invalid variable names
        pattern = r'\{\{([^}]*)\}\}'
        all_placeholders = re.findall(pattern, text)

        for placeholder in all_placeholders:
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', placeholder.strip()):
                return False, f"Invalid variable name: {placeholder}", []

        return True, "", variables
