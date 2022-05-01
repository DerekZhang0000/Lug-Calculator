"""
This is a lug calculator that calculates the maximum loads a lug can withstand using the Air Force method.
Developed by Ross Alumbaugh, Derek Zhang, Jonathan Zhang, and Chris Hardin
"""

import tkinter as tk
from PIL import ImageTk
import numpy as np
from scipy.interpolate import make_interp_spline
from matplotlib import pyplot as plt
from numpy import polyfit
import scipy.interpolate

# TO DO:
# Case where yield bush bearing strength does not exist
# Ultimate Strain calculation (not something you input usually)
# Other load types
# CSV Pandas Output
# GUI prettyfication
# Simplify / condense code

def loadGUI():  # loads tkinter GUI
    window = tk.Tk()
    window.iconphoto(False, tk.PhotoImage(file='lug.png'))
    window.title("Lug Calculator")
    loadTypesLabel = tk.Label(text="Load Type")
    loadTypesLabel.grid(row=0, column=0, sticky="SW")
    buttonFrame = tk.Frame()
    buttonFrame.grid(row=1, column=0, sticky="SW")
    inputsDiagram = ImageTk.PhotoImage(file="lugInputs.png")
    tk.Label(window, image=inputsDiagram).grid(
        row=0, column=1, rowspan=8, sticky="NW")
    loadType = tk.StringVar()
    loadType.set("Axial")
    tk.Radiobutton(buttonFrame, text="Axial", variable=loadType, value="Axial").grid(
        row=0, column=0)  # initializes buttons for load types
    tk.Radiobutton(buttonFrame, text="Transversal",
                   variable=loadType, value="Transversal").grid(row=0, column=1)
    tk.Radiobutton(buttonFrame, text="Oblique", variable=loadType,
                   value="Oblique").grid(row=0, column=2)
    inputFields = []
    # initializes input fields
    holeDiameterLabel = tk.Label(text="Hole Diameter (D)")
    holeDiameterLabel.grid(row=2, column=0, sticky="SW")
    holeDiameter = tk.Entry()
    holeDiameter.grid(row=3, column=0, sticky="SW")
    inputFields.append(holeDiameter)
    pinDiameterLabel = tk.Label(text="Pin Diameter (Dp)")
    pinDiameterLabel.grid(row=4, column=0, sticky="SW")
    pinDiameter = tk.Entry()
    pinDiameter.grid(row=5, column=0, sticky="SW")
    inputFields.append(pinDiameter)
    edgeDistance = tk.Label(text="Edge Distance (e)")
    edgeDistance.grid(row=6, column=0, sticky="SW")
    edgeDistance = tk.Entry()
    edgeDistance.grid(row=7, column=0, sticky="SW")
    inputFields.append(edgeDistance)
    width = tk.Label(text="Lug Width (w)")
    width.grid(row=8, column=0, sticky="SW")
    width = tk.Entry()
    width.grid(row=9, column=0, sticky="SW")
    inputFields.append(width)
    thickness = tk.Label(text="Lug Thickness")
    thickness.grid(row=10, column=0, sticky="SW")
    thickness = tk.Entry()
    thickness.grid(row=11, column=0, sticky="SW")
    inputFields.append(thickness)
    yieldBushingBearingCompressiveStrength = tk.Label(
        text="Yield Bushing Bearing Compressive Strength")
    yieldBushingBearingCompressiveStrength.grid(row=16, column=1, sticky="SW")
    yieldBushingBearingCompressiveStrength = tk.Entry()
    yieldBushingBearingCompressiveStrength.grid(row=17, column=1, sticky="SW")
    inputFields.append(yieldBushingBearingCompressiveStrength)
    tensileUltimateStrength = tk.Label(text="Ultimate Tensile Strength")
    tensileUltimateStrength.grid(row=12, column=0, sticky="SW")
    tensileUltimateStrength = tk.Entry()
    tensileUltimateStrength.grid(row=13, column=0, sticky="SW")
    inputFields.append(tensileUltimateStrength)
    tensileYieldStrength = tk.Label(text="Yield Tensile Strength")
    tensileYieldStrength.grid(row=14, column=0, sticky="SW")
    tensileYieldStrength = tk.Entry()
    tensileYieldStrength.grid(row=15, column=0, sticky="SW")
    inputFields.append(tensileYieldStrength)
    elasticModulus = tk.Label(text="Elastic Modulus")
    elasticModulus.grid(row=8, column=1, sticky="SW")
    elasticModulus = tk.Entry()
    elasticModulus.grid(row=9, column=1, sticky="SW")
    inputFields.append(elasticModulus)
    ultimateStrain = tk.Label(text="Ultimate Strain")
    ultimateStrain.grid(row=10, column=1, sticky="SW")
    ultimateStrain = tk.Entry()
    ultimateStrain.grid(row=11, column=1, sticky="SW")
    inputFields.append(ultimateStrain)
    designLoad = tk.Label(text="Design Load")
    designLoad.grid(row=12, column=1, sticky="SW")
    designLoad = tk.Entry()
    designLoad.grid(row=13, column=1, sticky="SW")
    inputFields.append(designLoad)
    fos = tk.Label(text="Factor of Safety")
    fos.grid(row=14, column=1, sticky="SW")
    fos = tk.Entry()
    fos.grid(row=15, column=1, sticky="SW")
    inputFields.append(fos)

    def allValidComplete():  # returns whether or not all fields are filled out and valid
        for inputField in inputFields:
            entry = inputField.get()
            try:
                if not entry.replace(".", "0").isdecimal() or float(entry) <= 0:
                    return False
            except:
                return False
        return True

    def testEnter():
        print(allValidComplete())
        if allValidComplete():
            print(axialLoad(float(holeDiameter.get()), float(pinDiameter.get()), float(edgeDistance.get()), float(width.get()), float(thickness.get()),
                      float(tensileUltimateStrength.get()), float(tensileYieldStrength.get()), float(yieldBushingBearingCompressiveStrength.get()),
                      float(elasticModulus.get()), float(ultimateStrain.get()), float(designLoad.get()), float(fos.get())))
    enterButton = tk.Button(text="Enter", command=testEnter)
    enterButton.grid(row=17, column=0, sticky="SW")
    window.mainloop()

def lineYInt(coord1, coord2):  # returns the Y-intercept of a line between two coordinates
    return coord1[1] - (coord1[0] * ((coord2[1] - coord1[1]) / (coord2[0] - coord1[0])))


def lineSlope(coord1, coord2):  # returns the slope of a line between two coordinates
    return (coord2[1] - coord1[1]) / (coord2[0] - coord1[0])

def valuePull(graphFit, diameterOverWidth):
    # gValue = graphFit[0] * diameterOverWidth ** (5 - 0) + graphFit[1] * diameterOverWidth ** (5 - 1) graphFit[2] * diameterOverWidth ** (5 - 2) ... 
    sum = 0
    for index in range(len(graphFit)):
        sum += graphFit[index] * diameterOverWidth ** (len(graphFit) - index)
    return sum

#Margin Calculator
def getMargin(designLoad, factorOfSafety, designStrength):

    marginOfSafety = (designStrength * factorOfSafety / designLoad) - 1

    return marginOfSafety
 
def axialLoad(holeDiameter, pinDiameter, edgeDistance, width, thickness, tensileUltimateStrength, tensileYieldStrength, yieldBushingBearingCompressiveStrength, elasticModulus, maxStrainAtBreakage, designLoad, factorOfSafety):
    eOverD = edgeDistance / holeDiameter

    # Calculate a Value hole to edge
    holeToEdge = edgeDistance - 0.5 * holeDiameter
    global k

    # Calculate K value allowable axial load coefficient
    if holeDiameter / thickness <= 5:
        if eOverD <= 1.5:
            coord1 = (1.5, 1.35)
            coord2 = (.5, 2)
            k = eOverD * lineSlope(coord1, coord2) + lineYInt(coord1, coord2)
        else:
            coord1 = (1.5, 1.35)
            coord2 = (2.4, 1.95)
            k = eOverD * lineSlope(coord1, coord2) + lineYInt(coord1, coord2)
    else:
        raise RuntimeError("holeDiameter / thickness > 5")

    # Calculate Bearing Stress Allowables
    if eOverD < 1.5:
        ultimateBearingStress = k * \
            (holeToEdge / holeDiameter) * tensileUltimateStrength
        yieldBearingStress = k * \
            (holeToEdge / holeDiameter) * tensileYieldStrength
    else:
        ultimateBearingStress = k * tensileUltimateStrength
        yieldBearingStress = k * tensileYieldStrength

    # Calculate Ultimate Bearing Load
    if tensileUltimateStrength <= 1.304 * tensileYieldStrength:
        ultimateBearingLoad = ultimateBearingStress * holeDiameter * thickness
    else:
        ultimateBearingLoad = 1.304 * yieldBearingStress * holeDiameter * thickness

    # Bushing Bearing Strength Under Axial Load
    ultimateBushingBearingLoad = 1.304 * \
        yieldBushingBearingCompressiveStrength * pinDiameter * thickness

    # Net Section Under Axial Load
    # Curve Data Sets
    # graph 1, constant 0
    g10x = np.array([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]) 
    g10y = np.array([0, 0.8, 1, 1, 1, 1, 1, 1, 1, 1, 1])
    g10Spline = make_interp_spline(g10x,g10y)
    g10xplot = np.linspace(g10x.min(), g10y.max(), 500)
    g10yplot = g10Spline(g10xplot)
    g10fit = polyfit(g10x, g10y, 5)

    # graph 1, constant 0.1
    g101x = np.array([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1])
    g101y = np.array([0, 0.65, 0.95, 1, 1, 1, 1, 1, 1, 1, 1])
    g101Spline = make_interp_spline(g101x,g101y)
    g101xplot = np.linspace(g101x.min(), g101y.max(), 500)
    g101yplot = g101Spline(g101xplot)
    g101fit = polyfit(g101x, g101y, 5)
    
    # graph 1, constant 0.2
    g102x = np.array([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1])
    g102y = np.array([0, 0.45, 0.7, .875, 0.95, 0.95, 0.95, 0.975, 1, 1, 1])
    g102Spline = make_interp_spline(g102x,g102y)
    g102xplot = np.linspace(g102x.min(), g102y.max(), 500)
    g102yplot = g102Spline(g102xplot)
    g102fit = polyfit(g102x, g102y, 5)

    # graph 1, constant 0.4
    g104x = np.array([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1])
    g104y = np.array([0, 0.2, 0.4, 0.6, 0.7, 0.75, 0.85, 0.9, 0.95, 1, 1])
    g104Spline = make_interp_spline(g104x,g104y)
    g104xplot = np.linspace(g104x.min(), g104x.max(), 500)
    g104yplot = g104Spline(g104xplot)
    g104fit = polyfit(g104x, g104y, 5)

    # graph 1, constant 0.6
    g106x = np.array([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1])
    g106y = np.array([0, 0.15, 0.3, 0.425, 0.5, 0.65, 0.7, 0.8, 0.9, 0.95, 1])
    g106Spline = make_interp_spline(g106x,g106y)
    g106xplot = np.linspace(g106x.min(), g106x.max(), 500)
    g106yplot = g106Spline(g106xplot)
    g106fit = polyfit(g106x, g106y, 5)

    # graph 1, constant 0.8
    g108x = np.array([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1])
    g108y = np.array([0, 0.1, 0.25, 0.3, 0.4, 0.5, 0.55, 0.65, 0.75, 0.875, 1])
    g108Spline = make_interp_spline(g108x,g108y)
    g108xplot = np.linspace(g108x.min(), g108x.max(), 500)
    g108yplot = g108Spline(g108xplot)
    g108fit = polyfit(g108x, g108y, 5)

    # graph 1, constant 1
    g11x = np.array([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1])
    g11y = np.array([0, 0.1, 0.2, 0.275, 0.35, 0.4, 0.4375, 0.5, 0.625, 0.775, 1])
    g11Spline = make_interp_spline(g11x,g11y)
    g11xplot = np.linspace(g11x.min(), g11x.max(), 500)
    g11yplot = g11Spline(g11xplot)
    g11fit = polyfit(g11x, g11y, 5)


    plot1 = plt.subplot2grid((3, 1), (0, 0), rowspan = 3)
    plot1.plot(g10xplot, g10yplot)
    plot1.plot(g101xplot, g101yplot)
    plot1.plot(g102xplot, g102yplot)
    plot1.plot(g104xplot, g104yplot)
    plot1.plot(g106xplot, g106yplot)
    plot1.plot(g108xplot, g108yplot)
    plot1.plot(g11xplot, g11yplot)
    plot1.set_aspect(0.5)

    #Plot 2
    # graph 2, constant 0
    g20x = np.array([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]) 
    g20y = np.array([0, 0.65, 0.825, 0.825, 0.825, 0.85, 0.85, 0.9, 0.9, 0.9, 1])
    g20Spline = make_interp_spline(g20x,g20y)
    g20xplot = np.linspace(g20x.min(), g20y.max(), 500)
    g20yplot = g20Spline(g20xplot)
    g20fit = polyfit(g20x, g20y, 5)

    # graph 2, constant 0.1
    g201x = np.array([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1])
    g201y = np.array([0, 0.6, 0.8, 0.85, 0.85, 0.85, 0.875, 0.9, 0.9, 0.95, 1])
    g201Spline = make_interp_spline(g201x,g201y)
    g201xplot = np.linspace(g201x.min(), g201y.max(), 500)
    g201yplot = g201Spline(g201xplot)
    g201fit = polyfit(g201x, g201y, 5)

    # graph 2, constant 0.2
    g202x = np.array([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1])
    g202y = np.array([0, 0.4, 0.675, 0.775, 0.825, 0.825, 0.85, 0.875, 0.9, 0.95, 1])
    g202Spline = make_interp_spline(g202x,g202y)
    g202xplot = np.linspace(g202x.min(), g202y.max(), 500)
    g202yplot = g202Spline(g202xplot)
    g202fit = polyfit(g202x, g202y, 5)

    # graph 2, constant 0.4
    g204x = np.array([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1])
    g204y = np.array([0, 0.2, 0.4, 0.6, 0.7, 0.75, 0.85, 0.9, 0.95, 1, 1])
    g204Spline = make_interp_spline(g204x,g204y)
    g204xplot = np.linspace(g204x.min(), g204x.max(), 500)
    g204yplot = g204Spline(g204xplot)
    g204fit = polyfit(g204x, g204y, 5)

    # graph 2, constant 0.6
    g206x = np.array([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1])
    g206y = np.array([0, 0.175, 0.3, 0.4, 0.5, 0.6, 0.675, 0.7, 0.825, 0.9, 1])
    g206Spline = make_interp_spline(g206x,g206y)
    g206xplot = np.linspace(g206x.min(), g206x.max(), 500)
    g206yplot = g206Spline(g206xplot)
    g206fit = polyfit(g206x, g206y, 5)

    # graph 2, constant 0.8
    g208x = np.array([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1])
    g208y = np.array([0, 0.15, 0.25, 0.35, 0.4, 0.475, 0.55, 0.625, 0.75, 0.85, 1])
    g208Spline = make_interp_spline(g208x,g208y)
    g208xplot = np.linspace(g208x.min(), g208x.max(), 500)
    g208yplot = g208Spline(g208xplot)
    g208fit = polyfit(g208x, g208y, 5)

    # graph 2, constant 1
    g21x = np.array([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1])
    g21y = np.array([0, 0.1, 0.2, 0.3, 0.35, 0.4, 0.475, 0.525, 0.65, 0.8, 1]) 
    g21Spline = make_interp_spline(g21x,g21y)
    g21xplot = np.linspace(g21x.min(), g21x.max(), 500)
    g21yplot = g21Spline(g21xplot)
    g21fit = polyfit(g21x, g21y, 5)

    #Plot 3
    # graph 3, constant 0
    g30x = np.array([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]) 
    g30y = np.array([0, 0.5, 0.65, 0.7, 0.7, 0.75, 0.8, 0.8, 0.85, 0.9, 1])
    g30Spline = make_interp_spline(g30x,g30y)
    g30xplot = np.linspace(g30x.min(), g30y.max(), 500)
    g30yplot = g30Spline(g30xplot)
    g30fit = polyfit(g30x, g30y, 5)

    # graph 3, constant 0.1
    g301x = np.array([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1])
    g301y = np.array([0, 0.5, 0.6125, 0.6375, 0.675, 0.775, 0.8, 0.825, 0.85, 0.9, 1])
    g301Spline = make_interp_spline(g301x,g301y)
    g301xplot = np.linspace(g301x.min(), g301y.max(), 500)
    g301yplot = g301Spline(g301xplot)
    g301fit = polyfit(g301x, g301y, 5)

    # graph 3, constant 0.2
    g302x = np.array([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1])
    g302y = np.array([0, 0.4, 0.6, 0.65, 0.675, 0.7, 0.75, 0.8, 0.925, 0.9, 1])
    g302Spline = make_interp_spline(g302x,g302y)
    g302xplot = np.linspace(g302x.min(), g302y.max(), 500)
    g302yplot = g302Spline(g302xplot)
    g302fit = polyfit(g302x, g302y, 5)

    # graph 3, constant 0.4
    g304x = np.array([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1])
    g304y = np.array([0, 0.25, 0.4, 0.5, 0.6, 0.65, 0.7, 0.75, 0.8, 0.9, 1])
    g304Spline = make_interp_spline(g304x,g304y)
    g304xplot = np.linspace(g304x.min(), g304x.max(), 500)
    g304yplot = g304Spline(g304xplot)
    g304fit = polyfit(g304x, g304y, 5)

    # graph 3, constant 0.6
    g306x = np.array([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1])
    g306y = np.array([0, 0.175, 0.3, 0.4, 0.5, 0.55, 0.6125, 0.675, 0.775, 0.85, 1])
    g306Spline = make_interp_spline(g306x,g306y)
    g306xplot = np.linspace(g306x.min(), g306x.max(), 500)
    g306yplot = g306Spline(g306xplot)
    g306fit = polyfit(g306x, g306y, 5)

    # graph 3, constant 0.8
    g308x = np.array([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1])
    g308y = np.array([0, 0.1, 0.225, 0.3, 0.4, 0.475, 0.525, 0.6, 0.7, 0.8125, 1])
    g308Spline = make_interp_spline(g308x,g308y)
    g308xplot = np.linspace(g308x.min(), g308x.max(), 500)
    g308yplot = g308Spline(g308xplot)
    g308fit = polyfit(g308x, g308y, 5)

    # graph 3, constant 1
    g31x = np.array([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1])
    g31y = np.array([0, 0.1, 0.2, 0.2875, 0.35, 0.4, 0.45, 0.55, 0.65, 0.8, 1])
    g31Spline = make_interp_spline(g31x,g31y)
    g31xplot = np.linspace(g31x.min(), g31x.max(), 500)
    g31yplot = g31Spline(g31xplot)
    g31fit = polyfit(g31x, g31y, 5)

    plot1 = plt.subplot2grid((3, 1), (1, 0), rowspan = 3)
    plot2 = plt.subplot2grid((3, 1), (2, 0), rowspan = 3)

    plt.subplot(3, 1, 1)
    plt.plot(g10xplot, g10yplot)
    plt.plot(g101xplot, g101yplot)
    plt.plot(g102xplot, g102yplot)
    plt.plot(g104xplot, g104yplot)
    plt.plot(g106xplot, g106yplot)
    plt.plot(g108xplot, g108yplot)
    plt.plot(g11xplot, g11yplot)

    plt.subplot(3, 1, 2)
    plt.plot(g20xplot, g20yplot)
    plt.plot(g201xplot, g201yplot)
    plt.plot(g202xplot, g202yplot)
    plt.plot(g204xplot, g204yplot)
    plt.plot(g206xplot, g206yplot)
    plt.plot(g208xplot, g208yplot)
    plt.plot(g21xplot, g21yplot)

    plt.subplot(3, 1, 3)
    plt.plot(g30xplot, g30yplot)
    plt.plot(g301xplot, g301yplot)
    plt.plot(g302xplot, g302yplot)
    plt.plot(g304xplot, g304yplot)
    plt.plot(g306xplot, g306yplot)
    plt.plot(g308xplot, g308yplot)
    plt.plot(g31xplot, g31yplot)

    plt.tight_layout()
    plt.show()

    #Net Tension Stress Coefficient Calculation
    ftuOverModulusMaxStrain = tensileUltimateStrength / elasticModulus * maxStrainAtBreakage
    diameterOverWidth = holeDiameter / width

    netTensionStressCoefficient = 0

    G1 = 0
    G2 = 0
    G3 = 0
    
    #Find G Values
    if ftuOverModulusMaxStrain <= 0.05:
        G1 = valuePull(g10fit, diameterOverWidth)
        G2 = valuePull(g20fit, diameterOverWidth)
        G3 = valuePull(g30fit, diameterOverWidth)
        
    elif ftuOverModulusMaxStrain > 0.05 and ftuOverModulusMaxStrain <= 0.15:
        G1 = valuePull(g101fit, diameterOverWidth)
        G2 = valuePull(g201fit, diameterOverWidth)
        G3 = valuePull(g301fit, diameterOverWidth)

    elif ftuOverModulusMaxStrain > 0.15 and ftuOverModulusMaxStrain <= .3:  
        G1 = valuePull(g102fit, diameterOverWidth)
        G2 = valuePull(g202fit, diameterOverWidth)
        G3 = valuePull(g302fit, diameterOverWidth)

    elif ftuOverModulusMaxStrain > 0.3 and ftuOverModulusMaxStrain <= 0.5:
        G1 = valuePull(g104fit, diameterOverWidth)
        G2 = valuePull(g204fit, diameterOverWidth)
        G3 = valuePull(g304fit, diameterOverWidth)
    
    elif ftuOverModulusMaxStrain > 0.5 and ftuOverModulusMaxStrain <= 0.7:
        G1 = valuePull(g106fit, diameterOverWidth)
        G2 = valuePull(g206fit, diameterOverWidth)
        G3 = valuePull(g306fit, diameterOverWidth)

    elif ftuOverModulusMaxStrain > 0.7 and ftuOverModulusMaxStrain <= 0.9: 
        G1 = valuePull(g108fit, diameterOverWidth)
        G2 = valuePull(g208fit, diameterOverWidth)
        G3 = valuePull(g308fit, diameterOverWidth)
        
    else:
        G1 = valuePull(g11fit, diameterOverWidth)
        G2 = valuePull(g21fit, diameterOverWidth)
        G3 = valuePull(g31fit, diameterOverWidth)

    # Interpolating between the 3 points
    FtyOverFtu = tensileYieldStrength / tensileUltimateStrength
    
    if FtyOverFtu > 0.8:
        xvals = np.array([0.8, 1])
        yvals = np.array([G2, G1])
        f = scipy.interpolate.interp1d(xvals, yvals)
        netTensionStressCoefficient = f(FtyOverFtu)
    else:
        xvals = np.array([0.6, 0.8])
        yvals = np.array([G3, G2])
        f = scipy.interpolate.interp1d(xvals, yvals)
        netTensionStressCoefficient = f(FtyOverFtu)
    
    ultimateNetSectionStress = netTensionStressCoefficient * tensileUltimateStrength
    yieldNetSectionStress = netTensionStressCoefficient * tensileYieldStrength

    netSectionUltimateLoad = 0

    if tensileUltimateStrength <= 1.304*tensileYieldStrength:
        netSectionUltimateLoad = ultimateNetSectionStress*(width-holeDiameter)*thickness
    else:
        netSectionUltimateLoad = 1.304*yieldNetSectionStress*(width-holeDiameter)*thickness

    #Margins
    # designStrengthUnderAxialLoad = min(ultimateBearingLoad, netSectionUltimateLoad, ultimateBushingBearingLoad)

    criterion = {'Ultimate Bearing Load': ultimateBearingLoad, 'Net Section Under Axial Load': netSectionUltimateLoad, 'Ultimate Bushing Bearing Load': ultimateBushingBearingLoad}

    criticalMode = min(criterion, key=criterion.get)

    designStrengthUnderAxialLoad = min(netSectionUltimateLoad, ultimateBearingLoad, ultimateBushingBearingLoad)

    axialMarginOfSafety = getMargin(designLoad, factorOfSafety, designStrengthUnderAxialLoad)


    return [axialMarginOfSafety, designLoad, designStrengthUnderAxialLoad, criticalMode, criterion]


loadGUI()