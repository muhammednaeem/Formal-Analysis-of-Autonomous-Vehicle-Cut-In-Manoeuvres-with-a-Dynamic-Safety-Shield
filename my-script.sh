#!/bin/bash
echo "Hello World1"
echo "Formal Verification and Robustness Analysis of Autonomous
Vehicle Cut-In Manoeuvres with a Dynamic Safety Shield"
# ==============================================================================
#: > ./TextFiles/clock_values.txt

#/Applications/UPPAAL-5.0.0.app/Contents/Resources/uppaal/bin/verifyta ./Model/CutInModel.xml > ./TextFiles/Results.txt
#./UPPAAL-5.0.0.app/Contents/Resources/uppaal/bin/verifyta ./Model/CutInModel_rotated_shield.xml > ./TextFiles/Results.txt
./UPPAAL-5.0.0.app/Contents/Resources/uppaal/bin/verifyta ./Model/CutInModel_two_layer_shield(Simulation).xml > ./TextFiles/Results.txt

#python3 ./TextFiles/plot_cars.py
#python3 ./TextFiles/plot_cars_rotated_shield.py
python3 ./TextFiles/plot_cars_two_layer_shield.py

