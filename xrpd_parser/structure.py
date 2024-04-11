from __future__ import annotations

import re
from collections import deque
from typing import Any

import numpy as np

from xrpd_parser.atom import Atom
from xrpd_parser.utils import MissingInformationError
from xrpd_parser.value import Value


class Structure:
    
    NUMERICAL_PARAMS = {
        "r_bragg",
        "phase_MAC",
        "scale",
        "a",
        "b",
        "c",
        "al",
        "be",
        "ga",
    }
    
    REQUIRED_PARAMETERS = {
        "r_bragg",
        "molar_mass",
        "cell_volume",
        "mass_fraction",
    }
    
    def __init__(self, line_queue: deque[str]) -> None:
        self.phase_name: str = ""
        self.params: dict[str, Any] = {}
        self.atoms: list[Atom] = []
        self._parse(line_queue)
    
    def to_dict(
        self,
        params: list[str],
        params_with_error: set[str] | None = None
    ) -> dict[str, float]:
        result = {}
        
        for p in params:
            result[p] = self.params[p].value if p in self.params else np.nan
            
            if params_with_error and p in params_with_error:
                result[f"{p}_err"] = self.params[p].error if p in self.params else np.nan
        
        return result
        
    def _parse(self, line_queue: deque[str]) -> None:
        phase_name_regex = re.compile(r'^phase_name "(.*)"$')
        mvw_regex = re.compile(r'^MVW\((.*),(.*),(.*)\)$')
        
        while line_queue and line_queue[0].startswith("\t\t"):
            line = line_queue.popleft().strip()
            
            # phase name
            match = phase_name_regex.match(line)
            if match:
                self.phase_name = match.group(1)
                continue
            
            # molar mass, cell volume, mass fraction
            match = mvw_regex.match(line)
            if match:
                self.params["molar_mass"] = Value(match.group(1).strip())
                self.params["cell_volume"] = Value(match.group(2).strip())
                self.params["mass_fraction"] = Value(match.group(3).strip())
                continue
            
            # atoms
            if line.startswith("site"):
                self.atoms.append(Atom(line))
                continue
                
            # additional parameters
            
            line_split = line.split(maxsplit=1)
            
            if not line_split:
                continue
            
            if line_split[0] in self.NUMERICAL_PARAMS:
                if len(line_split) < 2:
                    raise ValueError(f"found parameter {line_split[0]} without value")
                
                param, value_str = line_split
                self.params[param] = Value(value_str)
        
        if not self.phase_name:
            raise MissingInformationError("phase_name")
        
        for p in self.REQUIRED_PARAMETERS:
            if p not in self.params:
                raise MissingInformationError(p)
