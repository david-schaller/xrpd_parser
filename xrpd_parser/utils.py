"""Module to define utils functions and classes"""
from __future__ import annotations


class ParsingError(Exception):
    """Exception raises when the parsing failed."""
    
    def __init__(self, str_to_parse, message="could not parse"):
        self.str_to_parse = str_to_parse
        self.message = f"{message}: {str_to_parse}"
        super().__init__(self.message)


class MissingInformationError(Exception):
    """Exception raises when required information is missing or could not be parsed."""
    
    def __init__(self, missing_information, message="is missing"):
        self.missing_information = missing_information
        self.message = f"'{missing_information}' {message}"
        super().__init__(self.message)