"""
Plot heat capacity C_V/Nk near T_c for a Bose-Einstein condensate.

For an ideal Bose-Einstein condensate in 3D:
- Below T_c: C_V/Nk = 1.926 * (T/T_c)^(3/2)
- Above T_c: C_V/Nk ≈ 1.926 (constant for ideal gas approximation)

The heat capacity shows a characteristic cusp at the critical temperature.
"""

import numpy as np
import matplotlib.pyplot as plt

def heat_capacity_below_tc(T_ratio, A=1.926):
    """
    Heat capacity below critical temperature.

    Parameters:
    -----------
    T_ratio : array-like
        T/T_c ratio (should be < 1)
    A : float
        Prefactor (default 1.926 for ideal 3D BEC)

    Returns:
    --------
    C_V/Nk : array-like
        Normalized heat capacity
    """
    return A * T_ratio**(3/2)

def heat_capacity_above_tc(T_ratio, A=1.926):
    """
    Heat capacity above critical temperature.

    For an ideal gas in 3D, C_V/Nk approaches a constant value.

    Parameters:
    -----------
    T_ratio : array-like
        T/T_c ratio (should be > 1)
    A : float
        Prefactor (default 1.926 for ideal 3D BEC)

    Returns:
    --------
    C_V/Nk : array-like
        Normalized heat capacity
    """
    return A * np.ones_like(T_ratio)

def plot_bec_heat_capacity():
    """
    Create a plot of C_V/Nk vs T/T_c for a Bose-Einstein condensate.
    """
    # Temperature range
    T_below = np.linspace(0.01, 1.0, 200)  # Below T_c
    T_above = np.linspace(1.0, 2.0, 200)   # Above T_c

    # Calculate heat capacity
    A = 1.926  # Theoretical value for 3D ideal BEC
    C_below = heat_capacity_below_tc(T_below, A)
    C_above = heat_capacity_above_tc(T_above, A)

    # Create the plot
    fig, ax = plt.subplots(figsize=(10, 7))

    # Plot both regions
    ax.plot(T_below, C_below, 'b-', linewidth=2.5, label='Below $T_c$: $C_V/Nk = 1.926(T/T_c)^{3/2}$')
    ax.plot(T_above, C_above, 'r-', linewidth=2.5, label='Above $T_c$: $C_V/Nk ≈ 1.926$')

    # Mark the critical point
    ax.axvline(x=1.0, color='gray', linestyle='--', linewidth=1.5, alpha=0.7, label='$T = T_c$')
    ax.plot(1.0, A, 'ko', markersize=8, label='Critical point')

    # Labels and formatting
    ax.set_xlabel('$T/T_c$', fontsize=14, fontweight='bold')
    ax.set_ylabel('$C_V/Nk$', fontsize=14, fontweight='bold')
    ax.set_title('Heat Capacity of Bose-Einstein Condensate near $T_c$',
                 fontsize=16, fontweight='bold', pad=20)

    # Grid and legend
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(fontsize=11, loc='lower right', framealpha=0.95)

    # Set axis limits
    ax.set_xlim(0, 2)
    ax.set_ylim(0, 2.5)

    # Add annotations
    ax.annotate('Superfluid phase\n(BEC)',
                xy=(0.5, 0.5), fontsize=12,
                ha='center', style='italic', color='blue', alpha=0.7)
    ax.annotate('Normal phase\n(ideal gas)',
                xy=(1.5, 2.1), fontsize=12,
                ha='center', style='italic', color='red', alpha=0.7)

    # Tight layout
    plt.tight_layout()

    # Save the figure
    plt.savefig('bec_heat_capacity.png', dpi=300, bbox_inches='tight')
    print("Plot saved as 'bec_heat_capacity.png'")

    # Show the plot
    plt.show()

if __name__ == "__main__":
    plot_bec_heat_capacity()
