"""Module defining a class for measured or fixed values and their errors."""
from __future__ import annotations

import re

from xrpd_parser.utils import ParsingError


# example: 4.02901455e-007
NUMERIC_REGEX = r"([+-]?([0-9]*[.])?[0-9]+(e[+-]\d+)?)"

# example: @  4.02901455e-007`_6.025e-008_LIMIT_MIN_1e-015
VALUE_REGEX = re.compile(
    r"^(@\s+)?"                     # has been fitted?
    + NUMERIC_REGEX +               # value
    r"(`_" + NUMERIC_REGEX + r")?"  # error 
    r"([\s_](.*))?$",               # additional parameters/restrictions
)

# example: "=1/3; :  0.33333"
FRACTION_REGEX = re.compile(r"^=(\d+)\/([1-9]\d*);\s*:\s*(([0-9]*[.])?[0-9]+)$")


class Value:
    """A class for measured or fixed values and their errors."""
    
    def __init__(self, value_str) -> None:
        """Constructor of the Value class.

        Args:
            value_str: The string to be parsed.
        """
        self._parse(value_str)
    
    
    def __str__(self) -> str:
        """Return a string representation of the value.

        Returns:
            A string representation of the value.
        """
        fitted = "fitted" if self.has_been_fitted else "not fitted"
        param = f", Param: {self.parameters}" if self.parameters else ""
        
        return f"Value({self.value} +/- {self.error}, {fitted}{param})"
    
    def __repr__(self) -> str:
        """Return a string representation of the value.

        Returns:
            A string representation of the value.
        """
        return str(self)
    
    def _parse(self, value_str: str) -> None:
        """Parse a value string and set the attributes of the Value instance.

        Args:
            value_str: The string to be parsed.

        Raises:
            ParsingError: If the parsing was not successful.
        """
        value_str = value_str.strip()
        
        match = VALUE_REGEX.match(value_str)
        
        if match:
            self.value = float(match.group(2))
            self.error = float(match.group(6)) if match.group(6) else 0.0
            self.has_been_fitted = bool(match.group(1))
            # TODO: parse the additional parameters, e.g., limits that were set
            self.parameters = match.group(8)
            return

        match = FRACTION_REGEX.match(value_str)
        
        if match:
            self.value = float(match.group(1)) / float(match.group(2))
            self.error = 0.0
            self.has_been_fitted = False
            self.parameters = match.group(3)
            return
        
        raise ParsingError(value_str, message="could not parse value")
