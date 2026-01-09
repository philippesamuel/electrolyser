# generate a lookup table (LUT) for V_cell (cell voltage) vs I (cell current).
# assume
# V_cell(I) = V_rev + eta_act + eta_ohm + eta_con
# where:
# V_rev = reversible voltage (constant)
# eta_act = A * ln(I / (Area * j0))  (activation overpotential)
# eta_ohm = I * R_cell  (ohmic overpotential)
# eta_con = R*T/(n*F) * ln(jL/(jL - j))  (concentration overpotential)
# V_cell(I) = V_rev + A*ln(I/Area/j0) + I*R_cell + R*T/(n*F) * ln(jL/(jL - j))


import numpy as np
import pandas as pd

# --- 1. Simulation Setup (Lookup Table) ---
# Parameters for a 10-cell PEM stack at 80°C
N_CELLS = 10
AREA = 250  # cm^2
# V_REV = 1.23
V_REV = 1.18  # adjusted for 80°C (353K) operation
V_TN = 1.48
R_CELL = 0.05  # Ohm (constant for now)
J_LIMIT = 6.0  # A/cm^2
A_TAFEL = 0.06
J0 = 1e-4

R = 8.314  # J/(mol·K)
T_spec = 353  # K
n = 2  # number of electrons
F = 96485  # C/mol

MM_H2 = 2016  # kg/mol
SECONDS_PER_HOUR = 3600


def main():
    lut = generate_lut()
    # lut.to_csv("data/electrolyser_lut.csv", index=False)
    # print("Lookup table generated and saved to data/electrolyser_lut.csv")
    lut.plot(x="I", y=["V_stack", "P", "H2", "Heat"], subplots=True, layout=(2, 2))


def generate_lut():
    currents = np.linspace(1, 5000, 5000) / 10  # 0.1A to 500A
    data = []
    j = currents / AREA
    eta_act = A_TAFEL * np.log(j / J0)
    eta_ohm = currents * R_CELL
    eta_con = np.where(
        j < J_LIMIT, 
        (R * T_spec) / (n * F) * np.log(J_LIMIT / (J_LIMIT - j)), 
        5.0
    )  # cap eta_con to avoid infinity
    v_cell = V_REV + eta_act + eta_ohm + eta_con
    p_stack = currents * v_cell * N_CELLS
    h2_kg_h = (currents * N_CELLS / (n * F)) * MM_H2 * SECONDS_PER_HOUR
    heat_w = currents * (v_cell - V_TN) * N_CELLS

    data = {
        "I": currents,
        "V_stack": v_cell * N_CELLS,
        "P": p_stack,
        "H2": h2_kg_h,
        "Heat": heat_w,
    }

    return pd.DataFrame(data)


if __name__ == "__main__":
    main()
