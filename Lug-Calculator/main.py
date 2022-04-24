"""
This is a lug calculator that calculates the maximum loads a lug can withstand using the Air Force method.
Developed by Ross Alumbaugh, Derek Zhang, and Jonathan Zhang
"""

import tkinter as tk
from PIL import ImageTk
import numpy as np
from scipy.optimize import curve_fit
from matplotlib import pyplot

def loadGUI():  #loads tkinter GUI
    window = tk.Tk()
    window.iconphoto(False, tk.PhotoImage(file='lug.png'))
    window.title("Lug Calculator")
    loadTypesLabel = tk.Label(text="Load Type")
    loadTypesLabel.grid(row=0,column=0,sticky="SW")
    buttonFrame = tk.Frame()
    buttonFrame.grid(row=1,column=0,sticky="SW")
    inputsDiagram = ImageTk.PhotoImage(file="lugInputs.png")
    tk.Label(window, image=inputsDiagram).grid(row=0,column=1,rowspan=8,sticky="NW")
    loadType = tk.StringVar()
    loadType.set("Axial")
    tk.Radiobutton(buttonFrame,text="Axial",variable=loadType,value="Axial").grid(row=0,column=0)    #initializes buttons for load types
    tk.Radiobutton(buttonFrame, text="Transversal",variable=loadType,value="Transversal").grid(row=0,column=1)
    tk.Radiobutton(buttonFrame, text="Oblique",variable=loadType,value="Oblique").grid(row=0,column=2)
    inputFields = []
    holeDiameterLabel = tk.Label(text="Hole Diameter (D)")  #initializes input fields
    holeDiameterLabel.grid(row=2,column=0,sticky="SW")
    holeDiameter = tk.Entry()
    holeDiameter.grid(row=3, column=0,sticky="SW")
    inputFields.append(holeDiameter)
    pinDiameterLabel = tk.Label(text="Pin Diameter (Dp)") 
    pinDiameterLabel.grid(row=4,column=0,sticky="SW")
    pinDiameter = tk.Entry()
    pinDiameter.grid(row=5,column=0,sticky="SW")
    inputFields.append(pinDiameter)
    edgeDistance = tk.Label(text="Edge Distance (e)")
    edgeDistance.grid(row=6,column=0,sticky="SW")
    edgeDistance = tk.Entry()
    edgeDistance.grid(row=7, column=0,sticky="SW")
    inputFields.append(edgeDistance)
    width = tk.Label(text="Lug Width (w)")
    width.grid(row=8,column=0,sticky="SW")
    width = tk.Entry()
    width.grid(row=9, column=0,sticky="SW")
    inputFields.append(width)
    thickness = tk.Label(text="Lug Thickness")
    thickness.grid(row=10,column=0,sticky="SW")
    thickness = tk.Entry()
    thickness.grid(row=11, column=0,sticky="SW")
    inputFields.append(thickness)
    yieldBushingBearingCompressiveStrength = tk.Label(text="Yield Bushing Bearing Compressive Strength")
    yieldBushingBearingCompressiveStrength.grid(row=12,column=0,sticky="SW")
    yieldBushingBearingCompressiveStrength = tk.Entry()
    yieldBushingBearingCompressiveStrength.grid(row=13, column=0,sticky="SW")
    inputFields.append(yieldBushingBearingCompressiveStrength)
    tensileUltimateStrength = tk.Label(text="Ultimate Tensile Strength")
    tensileUltimateStrength.grid(row=8,column=1,sticky="SW")
    tensileUltimateStrength = tk.Entry()
    tensileUltimateStrength.grid(row=9, column=1,sticky="SW")
    inputFields.append(tensileUltimateStrength)
    tensileYieldStrength = tk.Label(text="Yield Tensile Strength")
    tensileYieldStrength.grid(row=10,column=1,sticky="SW")
    tensileYieldStrength = tk.Entry()
    tensileYieldStrength.grid(row=11, column=1,sticky="SW")
    inputFields.append(tensileYieldStrength)
    def allValidComplete(): #returns whether or not all fields are filled out and valid
        for inputField in inputFields:
            entry = inputField.get()
            try:
                if not entry.replace(".","0").isdecimal() or float(entry) <= 0:
                    return False
            except:
                return False
        return True
    def testEnter():
        print(allValidComplete())
    enterButton = tk.Button(text="Enter",command=testEnter)
    enterButton.grid(row=14,column=0,sticky="SW")
    window.mainloop()

loadGUI()

def lineYInt(coord1, coord2):   #returns the Y-intercept of a line between two coordinates
    return coord1[1] - (coord1[0] * ((coord2[1] - coord1[1]) / (coord2[0] - coord1[0])))

def lineSlope(coord1, coord2):  #returns the slope of a line between two coordinates
    return (coord2[1] - coord1[1]) / (coord2[0] - coord1[0])

def axialLoad(holeDiameter, pinDiameter, edgeDistance, width, thickness, tensileUltimateStrength, tensileYieldStrength, yieldBushingBearingCompressiveStrength):
    eOverD = edgeDistance / holeDiameter
    
    # Calculate a Value hole to edge
    holeToEdge = edgeDistance - 0.5 * holeDiameter
    global k
    
    #Calculate K value allowable axial load coefficient    
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
    
    #Calculate Bearing Stress Allowables       
    if eOverD < 1.5:
        ultimateBearingStress = k * (holeToEdge / holeDiameter) * tensileUltimateStrength
        yieldBearingStress = k * (holeToEdge / holeDiameter) * tensileYieldStrength
    else:
        ultimateBearingStress = k * tensileUltimateStrength
        yieldBearingStress = k * tensileYieldStrength   

    #Calculate Ultimate Bearing Load
    if tensileUltimateStrength <= 1.304 * tensileYieldStrength:
        ultimateBearingLoad = ultimateBearingStress * holeDiameter * thickness
    else:
        ultimateBearingLoad = 1.304 * yieldBearingStress * holeDiameter * thickness

    #Bushing Bearing Strength Under Axial Load
    ultimateBushingBearingLoad = 1.304 * yieldBushingBearingCompressiveStrength * pinDiameter * thickness

    #Net Section Under Axial Load
    #Curve Data Sets
    #graph 1, constant 0, x value
    g10x = np.array([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1])
    #graph 1, constant 0, y value
    g10y = np.array([0, 0.8, 1, 1, 1, 1, 1, 1, 1, 1, 1])




