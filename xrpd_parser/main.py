"""Parser for X-ray powder diffraction (XRPD) measurements."""

from __future__ import annotations

from collections import deque
from pathlib import Path
from typing import Any

import pandas as pd

from xrpd_parser.measurement import Measurement


def parse_file(filepath: str | Path) -> list[Measurement]:
    
    measurements = []
    
    with open(filepath, 'r') as f:
        line_queue = deque(f.readlines())
    
    while line_queue:
        line = line_queue.popleft()
        if line.startswith('xdd'):
            measurements.append(Measurement(line, line_queue))
    
    return measurements

def to_dataframe(measurements):
    
    data = []
    
    for measurement in measurements:
        s = measurement.structures[0]
        data.append(
            {
                "file_name": measurement.xy_file_path,
                "temperature": measurement.temperature,
                **s.to_dict(
                    ["r_bragg","a", "b", "c", "al", "be", "ga"],
                    params_with_error = {"a", "b", "c", "al", "be", "ga"}
                )
            }
        )
    
    return pd.DataFrame(data)


if __name__ == '__main__':
    example_folder = Path('examples')
    # path_example_file = example_folder / 'ML08.out'
    path_example_file = example_folder / 'Beispiel.out'
    
    measurements = parse_file(path_example_file)
    
    df = to_dataframe(measurements)
    print(df)
