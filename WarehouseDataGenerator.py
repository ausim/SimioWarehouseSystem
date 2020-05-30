# -*- coding: utf-8 -*-
"""
Created on Sat May 30 10:47:56 2020

@author: jsmith
"""
# %%
# import associated packages
from funcdefinations import dataframesInitialization,completeOrder,completeSKU,completeLocation,completeOrderSKU,completeSKULocation,outputCSV


# %%
# Set initial values (in case you don't want to use the xlsx file)
Bounding         = [0, 0, 0, 1000, 1000, 1000, 1000, 0]
# 0 - BLx; 1 - BLz; 2 - ULx, etc (going around clockwise - BL, UL, UR, BR)
NumOrders        = 100
NumSKUs          = 2000 # Generate an error if the number of SKUs exceeds the number of locations
SKUWeights       = [] # if empty, all equally likely.  If not empty, verify that the numbers work
NumLocations     = 2000
LineOrderDist    = ['Uniform', 1, 5]
QuantityLineDist = ['Uniform', 1,  3]

# %%

# Generate the initial dataframes
InitializationParaList = [NumOrders, NumSKUs, NumLocations, SKUWeights, LineOrderDist, QuantityLineDist]
[OrderInitial, SKUInitial, LocationInitial, OrderSKUInitial, SKULocationInitial]=dataframesInitialization(InitializationParaList)

# Complete the dataframes
# Complete the order dataframe
FinalOrderParaList = [OrderInitial]
OrderFinalDataframe = completeOrder(FinalOrderParaList)

# Complete the sku dataframe
FinalSKUParaList = [SKUInitial]
SKUFinalDataframe = completeSKU(FinalSKUParaList)

# Complete the location dataframe
FinalLocationParaList = [LocationInitial, Bounding]
LocationFinalDataframe = completeLocation(FinalLocationParaList)

# Complete the order_sku dataframe
FinalOrderSKUParaList = [OrderSKUInitial]
OrderSKUFinalDataframe = completeOrderSKU(FinalOrderSKUParaList)

# Complete the sku_location dataframe
FinalSKULocationParaList = [SKULocationInitial]
SKULocationFinalDataframe = completeSKULocation(FinalSKULocationParaList)

# Output csv files
OutputCSVParaList = [OrderFinalDataframe,SKUFinalDataframe, LocationFinalDataframe, OrderSKUFinalDataframe, SKULocationFinalDataframe]
outputCSV(OutputCSVParaList)