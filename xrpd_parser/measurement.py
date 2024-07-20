"""Module defining a class for measurements."""
from __future__ import annotations

import re
from collections import deque
from typing import Any

from xrpd_parser.structure import Structure
from xrpd_parser.value import Value


XDD_REGEX = re.compile(r'xdd "(.+)"')
TEMPERATURE_REGEX = re.compile(r"_(\d+)-0_C\.xy$")


class Measurement:
    """Class for measurements."""
    
    def __init__(self, calling_line: str, line_queue: deque[str]) -> None:
        """Constructor of the Measurement class.

        Args:
            calling_line: The line containing the 'xdd' call.
            line_queue: The queue of lines to be parsed.
        """        
        self.xy_file_path, self.temperature = self._parse_xdd_call(calling_line)
        
        self.params: dict[str, Any] = {}
        self.structures: dict[str, Structure] = {}
        
        self._parse(line_queue)
    
    def _parse_xdd_call(self, calling_line: str) -> tuple[str, float]:
        """Parse the first line of the measurement, i.e., the starting with 'xdd'.

        Args:
            calling_line: The line containing the 'xdd' call.

        Raises:
            ValueError: If the file name could not be parsed from the line.
            ValueError: If the temperature could not be parsed from the file name.

        Returns:
            The parsed file name and temperature.
        """        
        match = XDD_REGEX.match(calling_line)
        
        if not match:
            raise ValueError(f"Could not parse .xy filename from {calling_line}")
        
        xy_file_path = match.group(1)
        
        temperature_match = TEMPERATURE_REGEX.search(xy_file_path)
        if not temperature_match:
            raise ValueError(
                f"Could not parse temperature from {xy_file_path}, expected filename to end with "
                "something like '_0024-0_C.xy' (which would return 24.0 for 24 degrees Celcius)"
            )
        
        temperature = temperature_match.group(1).lstrip("0")
        temperature = float(temperature) if temperature else 0.0
        
        return xy_file_path, temperature
    
    def _parse(self, line_queue: deque[str]) -> None:
        """Parse the lines belonging to the measurement.
        
        The function parses line until a new measurement starts (as defined by indentation) or no
        more lines are in the queue.

        Args:
            line_queue: The queue of lines to be parsed.
        """        
        while line_queue and line_queue[0].startswith("\t"):
            line = line_queue.popleft()
            
            if line.startswith("\tstr"):
                structure = Structure(line_queue)
                self.structures[structure.phase_name] = structure
            
            elif line.startswith("\tr_exp"):
                line_split = line.strip().split()
                for i in range(0, len(line_split), 2):
                    self.params[line_split[i]] = Value(line_split[i + 1])
        
            # TODO: parse more measurement parameters
