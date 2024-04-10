from __future__ import annotations

import re

from xrpd_parser.value import Value


class Atom:
    
    def __init__(self, site_str: str) -> None:
        self._parse(site_str)
    
    def __str__(self):
        return (
            f'Atom({self.name}, mult={self.multiplicity}, '
            f'x={self.x_value.value}, y={self.y_value.value}, z={self.z_value.value}, '
            f'occ {self.occ_label} {self.occ_value.value}, '
            f'beq {self.beq_label} {self.beq_value.value})'
        )
    
    def _parse(self, site_str: str) -> None:
        match = re.match(
            r'site\s+(\S+)\s+'
            r'num_posns\s+(\d+)\s+'
            r'x\s+(.+)\s+y\s+(.+)\s?z\s+(.+)\s+'
            r'occ\s+([\w\+\-]+)\s+(([0-9]*[.])?[0-9]+)\s+'
            r'beq\s+(([\w\+\-\=]+)(; :)?\s+)?(\S+)',
            site_str
        )
        
        if not match:
            raise ValueError(f'Could not parse atom line {site_str}')
        
        self.name = match.group(1)
        self.multiplicity = int(match.group(2))
        self.x_value = Value(match.group(3))
        self.y_value = Value(match.group(4))
        self.z_value = Value(match.group(5))
        self.occ_label = match.group(6)
        self.occ_value = Value(match.group(7))
        self.beq_label = match.group(10)
        self.beq_value = Value(match.group(12))
        print(self)