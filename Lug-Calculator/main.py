"""
This is a lug calculator that calculates the maximum loads a lug can withstand using the Air Force method.
Developed by Ross Alumbaugh, Derek Zhang, and Jonathan Zhang
"""

import tkinter

loadTypes = ("Axial", "Transversal", "Oblique")

def lineYInt(coord1, coord2):   #returns the Y-intercept of a line between two coordinates
    return coord1[1] - (coord1[0] * ((coord2[1] - coord1[1]) / (coord2[0] - coord1[0])))

def lineSlope(coord1, coord2):  #returns the slope of a line between two coordinates
    return (coord2[1] - coord1[1]) / (coord2[0] - coord1[0])

def axialLoad(holeDiameter, pinDiameter, edgeDistance, width, thickness, tensileUltimateStrength, tensileYieldStrength):
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