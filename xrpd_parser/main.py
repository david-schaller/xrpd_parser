"""Parser for X-ray powder diffraction (XRPD) measurements."""

from __future__ import annotations

from collections import deque
from pathlib import Path
from typing import Any

import pandas as pd

from xrpd_parser.measurement import Measurement
from xrpd_parser.structure import Structure


def parse_file(filepath: str | Path) -> list[Measurement]:
    
    measurements = []
    
    with open(filepath, "r") as f:
        line_queue = deque(f.readlines())
    
    while line_queue:
        line = line_queue.popleft()
        if line.startswith("xdd"):
            measurements.append(Measurement(line, line_queue))
    
    return measurements

def to_dataframes(measurements: list[Measurement]) -> tuple[pd.DataFrame, pd.DataFrame]:
    
    data_structures = []
    data_atoms = []
    
    for measurement_id, measurement in enumerate(measurements):
        for phase_name, structure in measurement.structures.items():
            data_structures.append(
                {
                    "measurement_id": measurement_id,
                    "file_name": measurement.xy_file_path,
                    "temperature": measurement.temperature,
                    "phase_name": phase_name,
                    **structure.to_dict(
                        [
                            "r_bragg",
                            "a",
                            "b",
                            "c",
                            "al",
                            "be",
                            "ga",
                            "molar_mass",
                            "cell_volume",
                            "mass_fraction",
                        ],
                        params_with_error = {
                            "a",
                            "b", 
                            "c",
                            "al",
                            "be",
                            "ga",
                            "molar_mass",
                            "cell_volume",
                            "mass_fraction",
                        }
                    )
                }
            )
        
        for atom in structure.atoms:
            data_atoms.append(
                {
                    "measurement_id": measurement_id,
                    "temperature": measurement.temperature,
                    "phase_name": phase_name,
                    **atom.to_dict(),
                }
            )
    
    return pd.DataFrame(data_structures), pd.DataFrame(data_atoms)


if __name__ == "__main__":
    PATH_EXAMPLES = Path("examples")
    path_example_file = PATH_EXAMPLES / "Beispiel.out"
    
    measurements = parse_file(path_example_file)
    
    df_strutures, df_atoms = to_dataframes(measurements)
    print(df_strutures)
    
    df_strutures.to_csv(PATH_EXAMPLES / "example_output_structures.csv", index=False)
    df_atoms.to_csv(PATH_EXAMPLES / "example_output_atoms.csv", index=False)
