from __future__ import annotations

import re

class Value:
    
    def __init__(self, value_str) -> None:
        self._parse(value_str)
    
    
    def __str__(self) -> str:
        fitted = 'fitted' if self.has_been_fitted else 'not fitted'
        param = f', Param: {self.parameters}' if self.parameters else ''
        
        return f'Value({self.value} +/- {self.error}, {fitted}{param})'
    
    def __repr__(self) -> str:
        return str(self)
    
    def _parse(self, value_str: str) -> None:
        value_str = value_str.strip()
        
        match = re.match(
            r'^(@\s+)?'                     # has been fitted?
            r'([+-]?([0-9]*[.])?[0-9]+)'    # position
            r'(`_(([0-9]*[.])?[0-9]+))?'    # error 
            r'(_([\w\-\.]*))?',             # additional parameters/restrictions
            value_str
        )
        
        if match:
            self.value = float(match.group(2))
            self.error = float(match.group(5)) if match.group(5) else 0.0
            self.has_been_fitted = bool(match.group(1))
            self.parameters = match.group(8)
            return

        # special cases such as '=1/3; :  0.33333'
        match = re.match(r'^=(\d+)\/([1-9]\d*);\s*:\s*(([0-9]*[.])?[0-9]+)$', value_str)
        
        if match:
            self.value = float(match.group(1)) / float(match.group(2))
            self.error = 0.0
            self.has_been_fitted = False
            self.parameters = match.group(3)
            return
        
        raise ValueError(f'Could not parse value string {value_str}')