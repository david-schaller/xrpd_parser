from __future__ import annotations

import re
from collections import deque
from typing import Any

from xrpd_parser.structure import Structure
from xrpd_parser.value import Value


class Measurement:
    
    def __init__(self, calling_line: str, line_queue: deque[str]) -> None:
        self.xy_file_path, self.temperature = self._parse_xdd_call(calling_line)
        
        self.params: dict[str, Any] = {}
        self.structures: dict[str, Structure] = {}
        
        self._parse(line_queue)
    
    def _parse_xdd_call(self, calling_line: str) -> tuple[str, float]:
    
        match = re.match(r'xdd "(.+)"', calling_line)
        
        if not match:
            raise ValueError(f"Could not parse .xy filename from {calling_line}")
        
        xy_file_path = match.group(1)
        
        temperature_match = re.search(r"_(\d+)-0_C\.xy$", xy_file_path)
        if not temperature_match:
            raise ValueError(
                f"Could not parse temperature from {xy_file_path}, expected filename to end with "
                "something like '_0024-0_C.xy' (which would return 24.0 for 24 degrees Celcius)"
            )
        
        temperature = temperature_match.group(1).lstrip("0")
        temperature = float(temperature) if temperature else 0.0
        
        return xy_file_path, temperature
    
    def _parse(self, line_queue: deque[str]) -> None:
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