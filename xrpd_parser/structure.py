"""Module defining a class for measured structures."""
from __future__ import annotations

import re
from collections import deque
from typing import Any
from typing import Iterable

import numpy as np

from xrpd_parser.atom import Atom
from xrpd_parser.utils import DuplicatedParameterError
from xrpd_parser.utils import MissingInformationError
from xrpd_parser.value import Value


class Structure:
    """Class for measured structures."""
    
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
    
    CRYSTAL_SYSTEMS = {
        "Triclinic": ("a", "b", "c", "al", "be", "ga",),
        "Monoclinic": ("a", "b", "c", "be",),
        "Orthorhombic": ("a", "b", "c",),
        "Tetragonal": ("a=b", "c",),
        "Hexagonal": ("a=b", "c",),
        "Trigonal": ("a=b", "c",),
        "Cubic": ("a=b=c",),
    }
    
    REQUIRED_PARAMS = {
        "r_bragg",
        "molar_mass",
        "cell_volume",
        "mass_fraction",
    }
    
    PARAM2HAS_ERROR = {
        "r_bragg": False,
        "a": True,
        "b": True,
        "c": True,
        "al": True,
        "be": True,
        "ga": True,
        "molar_mass": True,
        "cell_volume": True,
        "mass_fraction": True,
    } 
    
    def __init__(self, line_queue: deque[str]) -> None:
        """Constructor of the Structure class.

        Args:
            line_queue: The queue of lines to be parsed.
        """
        self.phase_name: str = ""
        self.params: dict[str, Any] = {}
        self.atoms: list[Atom] = []
        self._parse(line_queue)
    
    def to_dict(
        self,
        parameters: Iterable[str] | None = None,
    ) -> dict[str, float]:
        """Return a dictionary representation of the structure.
        
        The returned dictionary returns 'np.nan' for all parameters that are not available for this
        instance. If the parameter is known to come with a measurement error, then the dictionary
        will also contain the column '{parameter}_err'.
        
        Args:
            parameters: If this is provided, only these parameters are returned in the dictionary.

        Returns:
            A dictionary representation of the structure.
        """
        result = {}
        
        if parameters is None:
            parameters = self.PARAM2HAS_ERROR.keys()
        
        for p in parameters:
            result[p] = self.params[p].value if p in self.params else np.nan
            
            if self.PARAM2HAS_ERROR.get(p):
                result[f"{p}_err"] = self.params[p].error if p in self.params else np.nan
        
        return result
    
    def _set_parameter(self, parameter_name: str, value: str | Value):
        """Set a parameter.

        Args:
            parameter_name: Name of the parameter.
            value: Value to be set.

        Raises:
            DuplicatedParameterError: If the parameter has already been set.
        """        
        if parameter_name in self.params:
            raise DuplicatedParameterError(parameter_name)
        
        self.params[parameter_name] = value

    def _parse_crystal_system(self, crystal_system: str, values_str: str) -> None:
        """Set the crystal system and the corresponding values.

        Args:
            crystal_system: Name of the crystal system.
            values_str: Values to be parsed (comma-separated).

        Raises:
            ValueError: If the crystal system is not available.
            ValueError: If the number of given values and the number of required parameters for the
                crystal system do not match. 
        """        
        if crystal_system not in self.CRYSTAL_SYSTEMS:
            raise ValueError(f"crystal system '{crystal_system}' is not available")
        
        self._set_parameter("crystal_system", crystal_system)
            
        values = [value_str.strip() for value_str in values_str.split(",")]
        if len(values) != len(self.CRYSTAL_SYSTEMS[crystal_system]):
            raise ValueError(
                f"number of parsed values ({len(values)}) and of values required for crystal"
                f"system '{crystal_system}' ({len(self.CRYSTAL_SYSTEMS[crystal_system])}) do not "
                "match"
            )
        
        for value_str, parameters in zip(values, self.CRYSTAL_SYSTEMS[crystal_system]):
            for p in parameters.split("="):
                self._set_parameter(p, Value(value_str))
        
    def _parse(self, line_queue: deque[str]) -> None:
        """Parse the lines belonging to the structure.
        
        The function parses line until a new measurement starts (as defined by indentation) or no
        more lines are in the queue.

        Args:
            line_queue: The queue of lines to be parsed.
        """
        phase_name_regex = re.compile(r'^phase_name "(.*)"$')
        
        # example: MVW( 842.082, 166.671`_0.069, 12.468`_0.290)
        mvw_regex = re.compile(r"^MVW\((.*),(.*),(.*)\)$")
        
        # example: Hexagonal(@  6.810339`_0.001012,@  4.149473`_0.001189)
        param_with_parentheses_regex = re.compile(r"^([a-zA-Z]+)\((.*)\)$")
        
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
                self._set_parameter("molar_mass", Value(match.group(1).strip()))
                self._set_parameter("cell_volume", Value(match.group(2).strip()))
                self._set_parameter("mass_fraction", Value(match.group(3).strip()))
                continue
            
            # parameters with values in parentheses
            match = param_with_parentheses_regex.match(line)
            if match:
                if match.group(1) in self.CRYSTAL_SYSTEMS:
                    self._parse_crystal_system(match.group(1), match.group(2))
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
                self._set_parameter(param, Value(value_str))
        
        if not self.phase_name:
            raise MissingInformationError("phase_name")
        
        for p in self.REQUIRED_PARAMS:
            if p not in self.params:
                raise MissingInformationError(p)
