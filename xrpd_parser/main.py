"""Parser for X-ray powder diffraction (XRPD) measurements."""

from __future__ import annotations

from collections import deque
from pathlib import Path
from typing import Any

import pandas as pd

from xrpd_parser.measurement import Measurement
from xrpd_parser.viz import plot_parameters


def parse_file(filepath: str | Path) -> list[Measurement]:
    """Parse a TOPAS output file.

    Args:
        filepath: Path to the file.

    Returns:
        A list of measurement objects.
    """    
    measurements = []
    
    with open(filepath, "r") as f:
        line_queue = deque(f.readlines())
    
    while line_queue:
        line = line_queue.popleft()
        if line.startswith("xdd"):
            measurements.append(Measurement(line, line_queue))
    
    return measurements

def to_dataframes(measurements: list[Measurement]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Convert a list of measurements to dataframes.

    Args:
        measurements: A list of measurement objects.

    Returns:
        Two dataframes where the first contains one row per structure and the second one row per
        atom. The columns 'measurement_id' and 'phase_name' can be used as foreign key in the atoms
        table.
    """    
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
                    **structure.to_dict()
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
    
    df_structures, df_atoms = to_dataframes(measurements)
    print(df_structures)
    
    df_structures.to_csv(PATH_EXAMPLES / "example_output_structures.csv", index=False)
    df_atoms.to_csv(PATH_EXAMPLES / "example_output_atoms.csv", index=False)
    
    plot_parameters(df_structures, save_as = PATH_EXAMPLES / "example_output_plot.pdf")
