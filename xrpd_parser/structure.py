from __future__ import annotations

from collections import deque
from typing import Any

import numpy as np

from xrpd_parser.atom import Atom
from xrpd_parser.value import Value


class Structure:
    
    NUMERICAL_PARAMS = (
        'r_bragg',
        'phase_MAC',
        'scale',
        'a',
        'b',
        'c',
        'al',
        'be',
        'ga',
    )
    # M = molar mass
    # V = cell volume
    # W = mass fraction
    
    def __init__(self, line_queue: deque[str]) -> None:
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
                result[f'{p}_err'] = self.params[p].error if p in self.params else np.nan
        
        return result
        
    def _parse(self, line_queue: deque[str]) -> None:
        while line_queue and line_queue[0].startswith('\t\t'):
            line = line_queue.popleft().strip()
            
            if line.startswith('site'):
                self.atoms.append(Atom(line))
            
            line_split = line.split(maxsplit=1)
            if line_split and line_split[0] in self.NUMERICAL_PARAMS:
                if len(line_split) < 2:
                    raise ValueError(f'found parameter {line_split[0]} without value')
                
                param, value_str = line_split
                self.params[param] = Value(value_str)
                # print(f'Set parameter {param}: {self.params[param]}')