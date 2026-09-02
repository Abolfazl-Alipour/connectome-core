"""
Module: qc_generator
Generates high-resolution publication-quality QC visualizations with clean white backgrounds
and clear subcortical boundaries.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def generate_connectome_qc_plot(
    matrix_path: str,
    output_png_path: str,
    subject_id: str,
    resolution: int,
    is_subcortical: bool = False
):
    """
    Plots a high-contrast connectome heatmap on a clean white background.
    Subcortical region boundaries are demarcated with dashed indicator lines.
    """
    mat = np.loadtxt(matrix_path, delimiter=",")
    N = mat.shape[0]
    
    fig, ax = plt.subplots(figsize=(10, 8), facecolor='white')
    
    # Use log10 scale for SIFT2 weights for optimal dynamic range
    plot_data = np.log10(mat + 1e-6)
    np.fill_diagonal(plot_data, np.nan)
    
    sns.heatmap(
        plot_data,
        cmap='inferno',
        cbar_kws={'label': r'$\log_{10}(\text{SIFT2 Weight})$'},
        ax=ax,
        xticklabels=False,
        yticklabels=False
    )
    
    if is_subcortical and N > 14:
        cortex_end = N - 14
        # Add boundary line separating cortex and subcortex
        ax.axhline(cortex_end, color='cyan', linestyle='--', linewidth=1.5, label='Subcortical Boundary')
        ax.axvline(cortex_end, color='cyan', linestyle='--', linewidth=1.5)
        ax.legend(loc='upper right')
        
    title = f"Subject {subject_id} Structural Connectome (N={N})"
    ax.set_title(title, fontsize=14, fontweight='bold', pad=12)
    
    os.makedirs(os.path.dirname(os.path.abspath(output_png_path)), exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_png_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    return output_png_path
