"""Module to define utils functions and classes."""
from __future__ import annotations


class ParsingError(Exception):
    """Exception raises when the parsing failed."""
    
    def __init__(self, str_to_parse: str, message: str = "could not parse") -> None:
        """Constructor of the ParsingError.

        Args:
            str_to_parse: String that could not be parsed.
            message: Custom error message.
        """        
        self.str_to_parse = str_to_parse
        self.message = f"{message}: {str_to_parse}"
        super().__init__(self.message)


class MissingInformationError(Exception):
    """Exception raises when required information is missing or could not be parsed."""
    
    def __init__(self, missing_information: str, message: str = "is missing") -> None:
        """Constructor of the MissingInformationError.

        Args:
            missing_information: Information that is missing.
            message: Custom error message after 'missing_information'.
        """
        self.missing_information = missing_information
        self.message = f"'{missing_information}' {message}"
        super().__init__(self.message)


class DuplicatedParameterError(Exception):
    """Exception raises when a parameter has already been set."""
    
    def __init__(self, parameter: str, message: str = "has already been set") -> None:
        """Constructor of the DuplicatedParameterError.

        Args:
            parameter: Name of the parameter.
            message: Custom error message after 'parameter'.
        """
        self.parameter = parameter
        self.message = f"'{parameter}' {message}"
        super().__init__(self.message)
