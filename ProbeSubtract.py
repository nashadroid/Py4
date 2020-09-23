import warnings
from numpy import loadtxt, savetxt
import numpy as np
import sys

bgSimHist = "/fs/scratch/PAS0035/nashad/11141350.owens-batch.ten.osc.edu/AllOutletNoTarget/history.p4"
# bgSimHist = "history.p4"
newSimHist = "history.p4"
saveFile= "BGSubtractHistory.p4"

newSimProbes = []
with open(newSimHist, 'r') as f:

    # Get a list of lines
    lines = f.readlines()

    # Check if correct file type
    try:
        if "#File type: probes" not in lines[2]:
            warnings.warn("WARNING: File may not be probe format")
    except:
        print("Cannot Read File")
        exit(1)

    # Make a list with all the probe names
    for line in lines[2:]:
        if line[0] == '#':
            newSimProbes.append(str(line[1:]))

bgSimProbes = []
with open(bgSimHist, 'r') as f:

    # Get a list of lines
    lines = f.readlines()

    # Check if correct file type
    try:
        if "#File type: probes" not in lines[2]:
            warnings.warn("WARNING: File may not be probe format")
    except:
        print("Cannot Read File")
        exit(1)

    # Make a list with all the probe names
    for line in lines[2:]:
        if line[0] == '#':
            bgSimProbes.append(str(line[1:]))

# Check if same exact probes
if newSimProbes != bgSimProbes:
    warnings.warn("NOT SAME PROBES")
    exit(1)

# Load in the actual data, yes I know it's inefficient to open the file twice
print("Loading " + bgSimHist)
bgProbeData = loadtxt(bgSimHist, comments="#", delimiter=" ", unpack=False)
print("Loading " + newSimHist)
newProbeData = loadtxt(newSimHist, comments="#", delimiter=" ", unpack=False)

bgSubtractData = np.subtract(newProbeData, bgProbeData)
bgSubtractData[:,1] = newProbeData[:,1]

header = "#Background Subtracted\n#\n" + "".join(bgSimProbes)

print("Saving " + saveFile)
savetxt(saveFile, bgSubtractData, header=header, comments="#")

