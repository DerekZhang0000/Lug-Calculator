"""
This is a lug calculator that calculates the maximum loads a lug can withstand using the Air Force method.
Developed by Ross Alumbaugh, Derek Zhang, Chris Hardin, and Jonathan Zhang
"""

import tkinter as tk
from tkinter import ttk, filedialog
from PIL import ImageTk, Image
import numpy as np
from scipy.interpolate import make_interp_spline
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from numpy import polyfit
import scipy.interpolate
import pandas as pd
import time
import os
import io
import dataframe_image as dfi
pd.set_option('display.float_format', '{:,}'.format)

# TO DO:
# Automatically adjust cell widths in csv output
# Case where yield bush bearing strength does not exist
# Ultimate Strain calculation (not something you input usually)
# Get Ross to work on the other 2 load types
# Put Tkinter stuff in another file
# Make a bangin readme
# Fix download location setting saving DONE
# Other load types DONE
# CSV Pandas Output DONE
# PDF Output DONE
# GUI prettyfication DONE
# Simplify / condense code DONE

if not os.path.isdir("./settings"):
    os.mkdir("./settings")

try:
    downloadCSV = open("settings/csv.txt", "r").read()
    if downloadCSV not in "YN":
        open("settings/csv.txt", "w").write("N")
except:
    downloadCSV = "Y"
    open("settings/csv.txt", "w").write("Y")

try:
    downloadPDF = open("settings/pdf.txt", "r").read()
    if downloadPDF not in "YN":
        open("settings/pdf.txt", "w").write("N")
except:
    downloadPDF = "Y"
    open("settings/pdf.txt", "w").write("Y")
    
try:
    downloadPath = open("settings/path.txt", "r").read()
except:
    downloadPath = "./exports"
    open("settings/path.txt", "w").write("./exports")

def loadGUI():  # loads tkinter GUI
    window = tk.Tk()
    window.geometry("575x481")
    window.tk.call('source', 'azure.tcl')
    window.tk.call('set_theme', 'light')
    style = ttk.Style()
    style.configure("Accent.TButton", foreground="white")
    style.configure("TCheckbutton")
    window.iconphoto(False, tk.PhotoImage(file='lug.png'))
    window.title("Lug Calculator")
    loadTypesLabel = ttk.Label(text="Load Type")
    loadTypesLabel.grid(row=0, column=0, sticky="SW")
    radiobuttonFrame = ttk.Frame()
    radiobuttonFrame.grid(row=1, column=0, sticky="SW")
    inputsDiagram = ImageTk.PhotoImage(file="lugInputs.png")
    ttk.Label(window, image=inputsDiagram).grid(row=0, column=1, rowspan=20, sticky="NW")
    loadType = tk.StringVar()
    loadType.set("Axial")
    inputFields = []
    
    def all_children(wid) : # gets all children
        _list = wid.winfo_children()
        for item in _list :
            if item.winfo_children() :
                _list.extend(item.winfo_children())

        return _list
    
    def getSubelements():   # gets all subelements
        subelements = []
        for child in all_children(window):
            if (child.grid_info()['row'] > 1 and child.grid_info()['column'] == 0) or \
                child.grid_info()['row'] > 1 and child.grid_info()['column'] == 1:
                    subelements.append(child)
        return subelements
    
    def axialLoadGUI(default=False):    # initializes input fields for axial load
        [element.destroy() for element in getSubelements()]
        inputFields.clear()
        holeDiameterLabel = ttk.Label(text="Hole Diameter (D)")
        holeDiameterLabel.grid(row=2, column=0, sticky="SW")
        holeDiameter = ttk.Entry()
        holeDiameter.grid(row=3, column=0, sticky="SW")
        pinDiameterLabel = ttk.Label(text="Pin Diameter (Dp)")
        pinDiameterLabel.grid(row=4, column=0, sticky="SW")
        pinDiameter = ttk.Entry()
        pinDiameter.grid(row=5, column=0, sticky="SW")
        edgeDistanceLabel = ttk.Label(text="Edge Distance (e)")
        edgeDistanceLabel.grid(row=6, column=0, sticky="SW")
        edgeDistance = ttk.Entry()
        edgeDistance.grid(row=7, column=0, sticky="SW")
        widthLabel = ttk.Label(text="Lug Width (w)")
        widthLabel.grid(row=8, column=0, sticky="SW")
        width = ttk.Entry()
        width.grid(row=9, column=0, sticky="SW")
        thicknessLabel = ttk.Label(text="Lug Thickness")
        thicknessLabel.grid(row=10, column=0, sticky="SW")
        thickness = ttk.Entry()
        thickness.grid(row=11, column=0, sticky="SW")
        tensileUltimateStrengthLabel = ttk.Label(text="Ultimate Tensile Strength")
        tensileUltimateStrengthLabel.grid(row=12, column=0, sticky="SW")
        tensileUltimateStrength = ttk.Entry()
        tensileUltimateStrength.grid(row=13, column=0, sticky="SW")
        tensileYieldStrengthLabel = ttk.Label(text="Yield Tensile Strength")
        tensileYieldStrengthLabel.grid(row=14, column=0, sticky="SW")
        tensileYieldStrength = ttk.Entry()
        tensileYieldStrength.grid(row=15, column=0, sticky="SW")
        elasticModulusLabel = ttk.Label(text="Elastic Modulus")
        elasticModulusLabel.grid(row=8, column=1, sticky="SW")
        elasticModulus = ttk.Entry()
        elasticModulus.grid(row=9, column=1, sticky="SW")
        ultimateStrainLabel = ttk.Label(text="Ultimate Strain")
        ultimateStrainLabel.grid(row=10, column=1, sticky="SW")
        ultimateStrain = ttk.Entry()
        ultimateStrain.grid(row=11, column=1, sticky="SW")
        designLoadLabel = ttk.Label(text="Design Load")
        designLoadLabel.grid(row=12, column=1, sticky="SW")
        designLoad = ttk.Entry()
        designLoad.grid(row=13, column=1, sticky="SW")
        fosLabel = ttk.Label(text="Factor of Safety")
        fosLabel.grid(row=14, column=1, sticky="SW")
        fos = ttk.Entry()
        fos.grid(row=15, column=1, sticky="SW")
        yieldBushingBearingCompressiveStrengthLabel = ttk.Label(text="Yield Bushing Bearing Compressive Strength")
        yieldBushingBearingCompressiveStrengthLabel.grid(row=16, column=1, sticky="SW")
        yieldBushingBearingCompressiveStrength = ttk.Entry()
        yieldBushingBearingCompressiveStrength.grid(row=17, column=1, sticky="SW")
        buttonFrame = ttk.Frame(window)
        buttonFrame.grid(row=17, column=0, sticky="SW")
        enterButton = ttk.Button(buttonFrame, text="Enter", style="Accent.TButton", command=enter)
        enterButton.grid(row=0, column=0, sticky="SW")
        settingsButton = ttk.Button(buttonFrame, text="Settings", command=openSettings)
        settingsButton.grid(row=0, column=1, padx=10, sticky="SW")
        inputFields.append([holeDiameter, pinDiameter, edgeDistance, width, thickness,
                      tensileUltimateStrength, tensileYieldStrength, yieldBushingBearingCompressiveStrength,
                      elasticModulus, ultimateStrain, designLoad, fos, holeDiameterLabel, pinDiameterLabel, edgeDistanceLabel,
                      widthLabel, thicknessLabel, tensileUltimateStrengthLabel, tensileYieldStrengthLabel,
                      yieldBushingBearingCompressiveStrengthLabel, elasticModulusLabel, ultimateStrainLabel, designLoadLabel, fosLabel])
        loadElements = [holeDiameter, pinDiameter, edgeDistance, width, thickness,
                      tensileUltimateStrength, tensileYieldStrength, yieldBushingBearingCompressiveStrength,
                      elasticModulus, ultimateStrain, designLoad, fos]
        if default:
            holeDiameter.insert(0, 1.6875)
            pinDiameter.insert(0, 1.375)
            edgeDistance.insert(0, 1)
            width.insert(0, 3)
            thickness.insert(0, .75)
            tensileUltimateStrength.insert(0, 45000)
            tensileYieldStrength.insert(0, 40000)
            elasticModulus.insert(0, 10000000)
            ultimateStrain.insert(0, .004)
            designLoad.insert(0, 12000)
            fos.insert(0, 1.5)
            yieldBushingBearingCompressiveStrength.insert(0, 22000)

        return loadElements

    def transversalLoadGUI():   # initializes input fields for transversal load
        [element.destroy() for element in getSubelements()]
        inputFields.clear()
        transversalTestLabel = ttk.Label(text="Transversal")
        transversalTestLabel.grid(row=2, column=0, sticky="SW")
        transversalTest = ttk.Entry()
        transversalTest.grid(row=3, column=0, sticky="SW")
        buttonFrame = ttk.Frame(window)
        buttonFrame.grid(row=4, column=0, sticky="SW")
        enterButton = ttk.Button(buttonFrame, text="Enter", style="Accent.TButton", command=enter)
        enterButton.grid(row=0, column=0, sticky="SW")
        settingsButton = ttk.Button(buttonFrame, text="Settings", command=openSettings)
        settingsButton.grid(row=0, column=1, padx=10, sticky="SW")
        inputFields.append([transversalTest, transversalTestLabel])
        loadElements = [transversalTest]
        return loadElements
    
    def obliqueLoadGUI():   # initializes input fields for oblique load
        [element.destroy() for element in getSubelements()]
        inputFields.clear()
        ObliqueTestLabel = ttk.Label(text="Oblique")
        ObliqueTestLabel.grid(row=2, column=0, sticky="SW")
        ObliqueTest = ttk.Entry()
        ObliqueTest.grid(row=3, column=0, sticky="SW")
        buttonFrame = ttk.Frame(window)
        buttonFrame.grid(row=4, column=0, sticky="SW")
        enterButton = ttk.Button(buttonFrame, text="Enter", style="Accent.TButton", command=enter)
        enterButton.grid(row=0, column=0, sticky="SW")
        settingsButton = ttk.Button(buttonFrame, text="Settings", command=openSettings)
        settingsButton.grid(row=0, column=1, padx=10, sticky="SW")
        inputFields.append([ObliqueTest, ObliqueTestLabel])
        loadElements = [ObliqueTest]
        return loadElements

    def switchAxial():  # switches input type to axial
        return axialLoadGUI(True)
    
    def switchTransversal():    # switches input to transversal
        return transversalLoadGUI()
    
    def switchOblique():    # switches input to oblique
        return obliqueLoadGUI()

    ttk.Radiobutton(radiobuttonFrame, text="Axial", variable=loadType, value="Axial", command=switchAxial).grid(row=0, column=0)  # initializes buttons for load types
    ttk.Radiobutton(radiobuttonFrame, text="Transversal", variable=loadType, value="Transversal", command=switchTransversal).grid(row=0, column=1)
    ttk.Radiobutton(radiobuttonFrame, text="Oblique", variable=loadType, value="Oblique", command=switchOblique).grid(row=0, column=2)
    
    def allValidComplete():  # returns whether or not all fields are filled out and valid
        allGood = True
        invalidEntries = []
        for inputField in inputFields[0][:int(len(inputFields[0]) / 2)]:
            entry = inputField.get()
            try:
                if not entry.replace(".", "0").isdecimal() or float(entry) <= 0:
                    invalidEntries.append(inputField)
                    allGood = False
            except:
                invalidEntries.append(inputField)
                allGood = False
        if allGood == True:
            return True
        else:
            for invalidEntry in invalidEntries:
                invalidEntry.state(["invalid"])
            return False

    def enter(): # submits the data you enter
        if allValidComplete():
            if loadType.get() == "Axial":
                loadElements = switchAxial()
                hD, pD, eD, w, t, tUS, tYS, yBBCS, eM, mS, dL, fos = inputDataList = [float(element.get()) for element in loadElements]
                exportAxialData(inputDataList, axialLoad(hD, pD, eD, w, t, tUS, tYS, yBBCS, eM, mS, dL, fos))
            elif loadType.get() == "Transversal":
                print("Transversal")
            elif loadType.get() == "Oblique":
                print("Oblique")

    def openSettings(): # opens the settings menu
        csv = tk.IntVar()
        pdf = tk.IntVar()
        settingsWindow = tk.Toplevel(window)
        settingsWindow.geometry("300x163")
        settingsWindow.iconphoto(False, tk.PhotoImage(file='lug.png'))
        settingsWindow.title("Settings")

        if not os.path.isdir("./settings"):
            os.mkdir("./settings")
        
        try:
            downloadCSV = open("settings/csv.txt", "r").read()
            if downloadCSV not in "YN":
                open("settings/csv.txt", "w").write("N")
                csv.set(0)
            elif downloadCSV == "Y":
                csv.set(1)
            else:
                csv.set(0)
        except:
            downloadCSV = "N"
            open("settings/csv.txt", "w").write("N")
            csv.set(1)
        
        try:
            downloadPDF = open("settings/pdf.txt", "r").read()
            if downloadPDF not in "YN":
                open("settings/pdf.txt", "w").write("N")
                pdf.set(0)
            elif downloadPDF == "Y":
                pdf.set(1)
            else:
                pdf.set(0)
        except:
            downloadPDF = "Y"
            open("settings/pdf.txt", "w").write("Y")
            pdf.set(1)
            
        try:
            downloadPath = open("settings/path.txt", "r").read()
        except:
            downloadPath = "./exports"
            open("settings/path.txt", "w").write("./exports")
        
        def updatePath():
            global downloadPath
            downloadPath = filedialog.askdirectory()
            open("settings/path.txt", "w").write(downloadPath)
            currentPath.config(text=downloadPath)
            settingsWindow.lift()
        
        csvCheckbutton = ttk.Checkbutton(settingsWindow, text="Save to CSV", style="TCheckbutton", variable=csv, onvalue=1, offvalue=0, takefocus=False)
        csvCheckbutton.grid(row=1, column=0, sticky="SW")
        pdfCheckbutton = ttk.Checkbutton(settingsWindow, text="Save to PDF", style="TCheckbutton", variable=pdf, onvalue=1, offvalue=0, takefocus=False)
        pdfCheckbutton.grid(row=2, column=0, sticky="SW")
        currentPath = ttk.Label(settingsWindow, text="Current Path: " + downloadPath)
        currentPath.grid(row=3, column=0, sticky="SW")
        pathEntry = ttk.Button(settingsWindow, text="Change Download Path", command=updatePath)
        pathEntry.grid(row=4, column=0, sticky="SW")
        
        def applySettings():    # saves settings
            global downloadCSV
            global downloadPDF
            if csv.get() == 1:
                downloadCSV = "Y"
                open("settings/csv.txt", "w").write("Y")
            else:
                downloadCSV = "N"
                open("settings/csv.txt", "w").write("N")
            if pdf.get() == 1:
                downloadPDF = "Y"
                open("settings/pdf.txt", "w").write("Y")
            else:
                downloadPDF = "N"
                open("settings/pdf.txt", "w").write("N")
            
            settingsWindow.destroy()
        
        applyButton = ttk.Button(settingsWindow, text="Apply", style="Accent.TButton", command=applySettings)
        applyButton.grid(row=6, column=0, sticky="SW", pady=20)     
        
    loadElements = switchAxial()    # default load type

    window.mainloop()

def lineYInt(coord1, coord2):  # returns the Y-intercept of a line between two coordinates
    return coord1[1] - (coord1[0] * ((coord2[1] - coord1[1]) / (coord2[0] - coord1[0])))

def lineSlope(coord1, coord2):  # returns the slope of a line between two coordinates
    return (coord2[1] - coord1[1]) / (coord2[0] - coord1[0])

def calculateG(graphFit, diameterOverWidth):
    # gValue = graphFit[0] * diameterOverWidth ** (5 - 0) + graphFit[1] * diameterOverWidth ** (5 - 1) graphFit[2] * diameterOverWidth ** (5 - 2) ... 
    sum = 0
    for index in range(len(graphFit)):
        sum += graphFit[index] * diameterOverWidth ** (len(graphFit) - index)
    return sum

#Margin Calculator
def getMargin(designLoad, factorOfSafety, designStrength):

    marginOfSafety = (designStrength * factorOfSafety / designLoad) - 1

    return marginOfSafety
 
# returns [graphFit, plotX, plotY]
def curveDataSets(graphY):
    graphX = np.array([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1])
    spline = make_interp_spline(graphX, graphY)
    plotX = np.linspace(graphX.min(), graphY.max(), 500)
    plotY = spline(plotX)
    return [polyfit(graphX, graphY, 5), plotX, plotY]

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
    g10fit, g10xplot, g10yplot = curveDataSets(np.array([0, 0.8, 1, 1, 1, 1, 1, 1, 1, 1, 1]))

    # graph 1, constant 0.1
    g101fit, g101xplot, g101yplot = curveDataSets(np.array([0, 0.65, 0.95, 1, 1, 1, 1, 1, 1, 1, 1]))
    # graph 1, constant 0.2
    g102fit, g102xplot, g102yplot = curveDataSets(np.array([0, 0.45, 0.7, .875, 0.95, 0.95, 0.95, 0.975, 1, 1, 1]))
    # graph 1, constant 0.4
    g104fit, g104xplot, g104yplot = curveDataSets(np.array([0, 0.2, 0.4, 0.6, 0.7, 0.75, 0.85, 0.9, 0.95, 1, 1]))
    # graph 1, constant 0.6
    g106fit, g106xplot, g106yplot = curveDataSets(np.array([0, 0.15, 0.3, 0.425, 0.5, 0.65, 0.7, 0.8, 0.9, 0.95, 1]))
    # graph 1, constant 0.8
    g108fit, g108xplot, g108yplot = curveDataSets(np.array([0, 0.1, 0.25, 0.3, 0.4, 0.5, 0.55, 0.65, 0.75, 0.875, 1]))
    # graph 1, constant 1
    g11fit, g11xplot, g11yplot = curveDataSets(np.array([0, 0.1, 0.2, 0.275, 0.35, 0.4, 0.4375, 0.5, 0.625, 0.775, 1]))

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
    g20fit, g20xplot, g20yplot = curveDataSets(np.array([0, 0.65, 0.825, 0.825, 0.825, 0.85, 0.85, 0.9, 0.9, 0.9, 1]))
    # graph 2, constant 0.1
    g201fit, g201xplot, g201yplot = curveDataSets(np.array([0, 0.6, 0.8, 0.85, 0.85, 0.85, 0.875, 0.9, 0.9, 0.95, 1]))
    # graph 2, constant 0.2
    g202fit, g202xplot, g202yplot = curveDataSets(np.array([0, 0.4, 0.675, 0.775, 0.825, 0.825, 0.85, 0.875, 0.9, 0.95, 1]))
    # graph 2, constant 0.4
    g204fit, g204xplot, g204yplot = curveDataSets(np.array([0, 0.2, 0.4, 0.6, 0.7, 0.75, 0.85, 0.9, 0.95, 1, 1]))
    # graph 2, constant 0.6
    g206fit, g206xplot, g206yplot = curveDataSets(np.array([0, 0.175, 0.3, 0.4, 0.5, 0.6, 0.675, 0.7, 0.825, 0.9, 1]))
    # graph 2, constant 0.8
    g208fit, g208xplot, g208yplot = curveDataSets(np.array([0, 0.15, 0.25, 0.35, 0.4, 0.475, 0.55, 0.625, 0.75, 0.85, 1]))
    # graph 2, constant 1
    g21fit, g21xplot, g21yplot = curveDataSets(np.array([0, 0.1, 0.2, 0.3, 0.35, 0.4, 0.475, 0.525, 0.65, 0.8, 1]))

    #Plot 3
    # graph 3, constant 0
    g30fit, g30xplot, g30yplot = curveDataSets(np.array([0, 0.5, 0.65, 0.7, 0.7, 0.75, 0.8, 0.8, 0.85, 0.9, 1]))
    # graph 3, constant 0.1
    g301fit, g301xplot, g301yplot = curveDataSets(np.array([0, 0.5, 0.6125, 0.6375, 0.675, 0.775, 0.8, 0.825, 0.85, 0.9, 1]))
    # graph 3, constant 0.2
    g302fit, g302xplot, g302yplot = curveDataSets(np.array([0, 0.4, 0.6, 0.65, 0.675, 0.7, 0.75, 0.8, 0.925, 0.9, 1]))
    # graph 3, constant 0.4
    g304fit, g304xplot, g304yplot = curveDataSets(np.array([0, 0.25, 0.4, 0.5, 0.6, 0.65, 0.7, 0.75, 0.8, 0.9, 1]))
    # graph 3, constant 0.6
    g306fit, g306xplot, g306yplot = curveDataSets(np.array([0, 0.175, 0.3, 0.4, 0.5, 0.55, 0.6125, 0.675, 0.775, 0.85, 1]))
    # graph 3, constant 0.8
    g308fit, g308xplot, g308yplot = curveDataSets(np.array([0, 0.1, 0.225, 0.3, 0.4, 0.475, 0.525, 0.6, 0.7, 0.8125, 1]))
    # graph 3, constant 1
    g31fit, g31xplot, g31yplot = curveDataSets(np.array([0, 0.1, 0.2, 0.2875, 0.35, 0.4, 0.45, 0.55, 0.65, 0.8, 1]))
    plot1 = plt.subplot2grid((3, 1), (1, 0), rowspan=3)

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
    global plotsAxial
    plotsAxial = io.BytesIO()
    plt.savefig(plotsAxial, format='png')
    
    #Net Tension Stress Coefficient Calculation
    ftuOverModulusMaxStrain = tensileUltimateStrength / elasticModulus * maxStrainAtBreakage
    diameterOverWidth = holeDiameter / width
    netTensionStressCoefficient = 0

    G1 = 0
    G2 = 0
    G3 = 0
    
    #Find G Values
    if ftuOverModulusMaxStrain <= 0.05:
        G1 = calculateG(g10fit, diameterOverWidth)
        G2 = calculateG(g20fit, diameterOverWidth)
        G3 = calculateG(g30fit, diameterOverWidth)
        
    elif ftuOverModulusMaxStrain > 0.05 and ftuOverModulusMaxStrain <= 0.15:
        G1 = calculateG(g101fit, diameterOverWidth)
        G2 = calculateG(g201fit, diameterOverWidth)
        G3 = calculateG(g301fit, diameterOverWidth)

    elif ftuOverModulusMaxStrain > 0.15 and ftuOverModulusMaxStrain <= .3:  
        G1 = calculateG(g102fit, diameterOverWidth)
        G2 = calculateG(g202fit, diameterOverWidth)
        G3 = calculateG(g302fit, diameterOverWidth)

    elif ftuOverModulusMaxStrain > 0.3 and ftuOverModulusMaxStrain <= 0.5:
        G1 = calculateG(g104fit, diameterOverWidth)
        G2 = calculateG(g204fit, diameterOverWidth)
        G3 = calculateG(g304fit, diameterOverWidth)
    
    elif ftuOverModulusMaxStrain > 0.5 and ftuOverModulusMaxStrain <= 0.7:
        G1 = calculateG(g106fit, diameterOverWidth)
        G2 = calculateG(g206fit, diameterOverWidth)
        G3 = calculateG(g306fit, diameterOverWidth)

    elif ftuOverModulusMaxStrain > 0.7 and ftuOverModulusMaxStrain <= 0.9: 
        G1 = calculateG(g108fit, diameterOverWidth)
        G2 = calculateG(g208fit, diameterOverWidth)
        G3 = calculateG(g308fit, diameterOverWidth)
        
    else:
        G1 = calculateG(g11fit, diameterOverWidth)
        G2 = calculateG(g21fit, diameterOverWidth)
        G3 = calculateG(g31fit, diameterOverWidth)

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

def mergeImages(images):
    """Merge two images into one
    :param images: list of images using PIL
    :return: the merged Image object
    """
    # input, output, plots
    image1 = images[0]
    image2 = images[1]
    image3 = images[2]

    (width1, height1) = image1.size
    (width2, height2) = image2.size
    (width3, height3) = image3.size

    result_width = max(width1, width2) + width3
    result_height = max(height1 + height2, height3)

    result = Image.new('RGB', (result_width, result_height), color="white")
    result.paste(im=image1, box=(0, 0))
    result.paste(im=image2, box=(0, height1))
    result.paste(im=image3, box=(max(width1, width2), 0))
    return result

def exportAxialData(inputDataList, dataList):
    
    outputData = {
        "Axial Margin Of Safety": [dataList[0]],
        "Design Load": [dataList[1]],
        "Design Strength Under Axial Load": [dataList[2]],
        "Critical Load": [dataList[3]],
        "Ultimate Bearing Load": [dataList[4]["Ultimate Bearing Load"]],
        "Net Section Under Axial Load": [dataList[4]["Net Section Under Axial Load"]],
        "Ultimate Bushing Bearing Load": [dataList[4]["Ultimate Bushing Bearing Load"]]
    }
    outputTable = pd.DataFrame(outputData).transpose()

    inputData = {
        "Load Type": ["Axial"],
        "Hole Diameter": [inputDataList[0]], 
        "Pin Diameter": [inputDataList[1]],
        "Edge Distance": [inputDataList[2]], 
        "Width": [inputDataList[3]],
        "Thickness": [inputDataList[4]],
        "Tensile Ultimate Strength": [inputDataList[5]],
        "Tensile Yield Strength": [inputDataList[6]],
        "Elastic Modulus": [inputDataList[7]], 
        "Maximum Strain": [inputDataList[8]],
        "Design Load": [inputDataList[9]],
        "Factor Of Safety": inputDataList[10],
        "Yield Bush Bearing Compressive Strength": [inputDataList[11]]
    }
    inputTable = pd.DataFrame(inputData).transpose()

    inputTable.columns = [""]
    outputTable.columns = [""]

    date = time.strftime("%Y-%m-%d_%H%M%S")
    concatTable = pd.concat([outputTable, inputTable])

    if downloadPath == "./exports":
        if not os.path.isdir("./exports"):
            os.mkdir("./exports")

    if downloadCSV == "Y":
        filename = downloadPath + "/Axial_Load_Analysis_" + date + ".csv"
        concatTable.to_csv(filename, mode="w", encoding="utf-8", header=False)
    if downloadPDF == "Y":
        filename = downloadPath + "/Axial_Load_Analysis_" + date + ".pdf"
        inputBuffer = io.BytesIO()
        dfi.export(inputTable, inputBuffer)
        outputBuffer = io.BytesIO()
        dfi.export(outputTable, outputBuffer)
        images = [Image.open(img).convert('RGB') if Image.open(img).mode == 'RGBA' else Image.open(img) for img in [inputBuffer, outputBuffer, plotsAxial]]
        mergeImages(images).save(filename)

loadGUI()
