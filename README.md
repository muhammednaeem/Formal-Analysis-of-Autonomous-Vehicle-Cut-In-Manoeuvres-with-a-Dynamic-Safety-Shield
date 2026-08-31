# Formal Analysis of Autonomous Vehicle Cut-In Maneuvers

This repository contains the UPPAAL model and supporting scripts used to simulate and analyze an autonomous vehicle cut-in maneuver with a dynamic safety shield.

The ego car follows a predefined cut-in trajectory while interacting with surrounding vehicles. The UPPAAL model evaluates the maneuver and detects possible safety-shield violations. Python scripts are used to visualize the simulated vehicle trajectories and the dynamic safety shield.

## Repository Structure

```text
UPPAAL_Model_cutin/
├── Model/
│   └── CutInModel.xml
├── TextFiles/
│   ├── clock_values.txt
│   ├── Results.txt
│   └── plot_cars.py
├── mylib/
│   └── myExLib.dylib
├── figures/
└── run.sh
```

## Requirements

- UPPAAL / UPPAAL SMC
- Python 3
- NumPy
- Matplotlib

Install the required Python packages with:

```bash
pip3 install numpy matplotlib
```

## How to Simulate

### 1. Open the UPPAAL model

Open the following file in UPPAAL:

```text
Model/CutInModel.xml
```

The model can be explored using the **Simulator** and analyzed using the **Verifier**.

### 2. Configure the external library

The model uses the external library:

```text
mylib/myExLib.dylib
```

Update the library path in `CutInModel.xml` if the path does not match the location of the repository on your computer.

### 3. Run the model in UPPAAL

Use the **Simulator** tab to execute the cut-in maneuver and inspect the evolution of the ego car, surrounding vehicles, and safety shield.

Safety properties can be evaluated from the **Verifier** using the UPPAAL SMC queries included in the model.

For example:

```text
Pr[<=TOTAL_TIME] ([] !shieldbreach)
```

checks the probability that no safety-shield violation occurs during the simulation horizon.

### 4. Run from the command line

The complete verification and plotting workflow can also be started using:

```bash
chmod +x run.sh
./run.sh
```

Make sure the path to `verifyta` inside `run.sh` matches your local UPPAAL installation.

The verification output is stored in:

```text
TextFiles/Results.txt
```

### 5. Generate trajectory figures

The simulation data used for visualization is stored in:

```text
TextFiles/clock_values.txt
```

To generate the trajectory figures manually, run:

```bash
python3 TextFiles/plot_cars.py
```

The generated figures are saved in:

```text
figures/
```

## Notes

This repository contains research code and is intended for simulation and formal analysis of predefined cut-in maneuvers. It does not generate or optimize the cut-in trajectory itself.
