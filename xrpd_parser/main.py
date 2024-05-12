"""Parser for X-ray powder diffraction (XRPD) measurements."""
from __future__ import annotations

import argparse
from collections import deque
from pathlib import Path

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

# example call:
# xrpd-parser -i examples/Beispiel.out -o examples/example_output
def main() -> None:
    """Entry point of the parser."""    
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input_file",
        help="The input file containing the measurements.",
        type=str,
    )
    parser.add_argument(
        "-o",
        "--output_directory",
        help="The output directory to be created.",
        type=str,
    )
    parser.add_argument(
        "-n",
        "--no_plot",
        action="store_true",
        help="If this flag is set, no plots are generated.",
    )
    args = parser.parse_args()
    
    file_path = Path(args.input_file)
    output_directory = Path(args.output_directory)
    output_directory.mkdir(exist_ok=True, parents=False)
    
    measurements = parse_file(file_path)
    df_structures, df_atoms = to_dataframes(measurements)
    
    df_structures.to_csv(output_directory / "structures.csv", index=False)
    df_atoms.to_csv(output_directory / "atoms.csv", index=False)
    
    if not args.no_plot:
        plot_parameters(df_structures, save_as = output_directory / "summary_plot.pdf")
