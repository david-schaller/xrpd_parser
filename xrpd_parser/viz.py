"""Module for plotting the development of parameters over the series of measurements."""
from __future__ import annotations

from pathlib import Path
from typing import Sequence

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


PARAMETERS2LABELS = {
    "a": "a [Å]",
    "b": "b [Å]",
    "c": "c [Å]",
    "al": "alpha",
    "be": "beta",
    "ga": "gamma",
    "r_bragg": "R-Bragg",
    "molar_mass": "molar mass",
    "cell_volume": "cell volume [Å³]",
    "mass_fraction": "mass fraction [%]",
}


def plot_parameters(
    df: pd.DataFrame,
    parameters: Sequence[str] | None = None,
    save_as: str | Path | None = None,
) -> None:
    """Plot the values in a structures dataframe per phase.

    Args:
        df: A table containing structures.
        parameters: The parameters to be plotted.
        save_as: If provided, the plot is saved at this location.

    Raises:
        RuntimeError: If no parameters were found in the dataframe.
        RuntimeError: If no phases were found in the dataframe.
    """    
    if parameters is None:
        parameters = list(PARAMETERS2LABELS)
    
    found_parameters: list[str] = []
    for parameter in parameters:
        if parameter not in df.columns:
            print(f"Skipping {parameter}, not in dataframe")
        elif df[parameter].isna().all():
            print(f"Skipping {parameter}, all NA")
        else:
            found_parameters.append(parameter)
    
    if not found_parameters:
        raise RuntimeError("no parameters to plot")
    parameters = found_parameters
        
    phases = df["phase_name"].unique()
    
    if len(phases) == 0:
        raise RuntimeError("no phases to plot")
    
    fig, axs = plt.subplots(
        len(parameters),
        len(phases),
        figsize = (5 * len(phases), 4 * len(parameters)),
        sharex=True,
    )
    
    if not isinstance(axs, np.ndarray):
        axs = np.array([[axs]])
    elif len(parameters) == 1:
        axs = axs[np.newaxis, :]
    elif len(phases) == 1:
        axs = axs[:, np.newaxis]
    
    for col_idx, phase in enumerate(phases):
        df_phase = df[df["phase_name"] == phase]
        
        for row_idx, parameter in enumerate(parameters):
            ax = axs[row_idx, col_idx]
            
            ax.set_title(phase)
            
            if parameter not in df_phase.columns or df_phase[parameter].isna().all():
                print(f"Could not plot {parameter} for phase {phase}")
            
            param_err = f"{parameter}_err"
            yerr = df_phase[param_err] if param_err in df_phase.columns else None
            
            ax.errorbar(
                df_phase["temperature"],
                df_phase[parameter],
                yerr=yerr,
                color="darkslategray",
                fmt="o",
                markersize=3,
                capsize=3,
            )
            
            ax.set_xlabel("temperature [K]")
            if parameter in PARAMETERS2LABELS:
                ax.set_ylabel(PARAMETERS2LABELS[parameter])
    
    plt.tight_layout()
    
    if save_as is not None:
        plt.savefig(save_as)