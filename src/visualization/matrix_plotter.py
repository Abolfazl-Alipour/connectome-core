"""
Module: matrix_plotter
Renders high-resolution publication-quality heatmaps of connectome matrices
with white background and non-overlapping label annotations.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def plot_consensus_matrix(
    matrix: np.ndarray,
    out_png: str,
    title: str,
    metric_label: str = r"$\log_{10}(\text{SIFT2 Weight})$",
    subcortical_count: int = 14
):
    """
    Renders connectome matrix with white background and clear subcortical boundary markers.
    """
    N = matrix.shape[0]
    fig, ax = plt.subplots(figsize=(10, 8), facecolor='white')
    
    plot_data = np.log10(matrix + 1e-6)
    np.fill_diagonal(plot_data, np.nan)
    
    sns.heatmap(
        plot_data,
        cmap='magma',
        cbar_kws={'label': metric_label},
        ax=ax,
        xticklabels=False,
        yticklabels=False
    )
    
    if subcortical_count > 0 and N > subcortical_count:
        cortex_end = N - subcortical_count
        ax.axhline(cortex_end, color='#00E5FF', linestyle='--', linewidth=1.5)
        ax.axvline(cortex_end, color='#00E5FF', linestyle='--', linewidth=1.5)
        # Place label neatly on top
        ax.text(cortex_end + subcortical_count/2, -15, "Subcortex", color='#00838F',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
                
    ax.set_title(title, fontsize=14, fontweight='bold', pad=25)
    os.makedirs(os.path.dirname(os.path.abspath(out_png)), exist_ok=True)
    plt.tight_layout()
    plt.savefig(out_png, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    return out_png
