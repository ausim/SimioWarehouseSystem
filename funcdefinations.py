import pandas as pd
import numpy as np
import random
import datetime as dt
import math
from datetime import datetime


# Define the function to read from the file and return the parameter values
#####################################################################################################################
# Input :           FileName: The xlsx file that contains the parameter settings
#                  SheetName: The worksheet name that contains the main parameter settings
#            SKUWeightsSheet: The worksheet name that contains the SKU weights
#
# Output:    The paramter settings
#######################################################################################################################
def readFromExcel(FileName = 'ParameterSetting.xlsx', SheetName = 'Parameter Setting', SKUWeightsSheet = 'SKU Weights'):
    # Read the input csv file and get the parameter settings
    PS = pd.read_excel('ParamterSetting.xlsx',sheet_name = 'Parameter Setting')
    SkuWeights = pd.read_excel('ParamterSetting.xlsx',sheet_name = 'SKU Weights')
    
    NumOrders = int(PS['Value'][PS['Name'] == 'OrderNo'].item())                     # number of orders
    NumSKUs = int(PS['Value'][PS['Name'] == 'SkuNo'].item())                         # number of skus
    NumLocations = int(PS['Value'][PS['Name'] == 'LocationNo'].item())                  # number of locations
    
    BLX = int(PS['Value'][PS['Name'] == 'BL_corner'].item())                # The bottom left corner x coordinate
    BLZ = int(PS['Add_value1'][PS['Name'] == 'BL_corner'].item())           # The bottom left corner z coordinate
    BRX = int(PS['Value'][PS['Name'] == 'BR_corner'].item())                # The bottom right corner x coordinate
    BRZ = int(PS['Add_value1'][PS['Name'] == 'BR_corner'].item())           # The bottom right corner z coordinate
    ULX = int(PS['Value'][PS['Name'] == 'UL_corner'].item())                # The top left corner x coordinate
    ULZ = int(PS['Add_value1'][PS['Name'] == 'UL_corner'].item())           # The top left corner z coordinate
    URX = int(PS['Value'][PS['Name'] == 'UR_corner'].item())                # The top right corner x coordinate
    URZ = int(PS['Add_value1'][PS['Name'] == 'UR_corner'].item())           # The top right corner z coordinate
    Bounding = [BLX, BLZ, ULX, ULZ, URX, URZ, BRX, BRZ]
    
    LineDist = PS['Value'][PS['Name'] == 'LineDistribution'].item()                 # The distribution for the number of lines in an order
    LineOrderDist = getLineItemDistParas(PS, LineDist, 'LineDistribution')
    
    QuantityDist = PS['Value'][PS['Name'] == 'QuantityDistribution'].item()         # The distribution for the quantity in an order line
    QuantityLineDist = getLineItemDistParas(PS, LineDist, 'QuantityDistribution')
    
    SKUWeights = SkuWeights['Weight'].tolist()
    
    return(Bounding, NumOrders, NumSKUs, SKUWeights, NumLocations, LineOrderDist, QuantityLineDist)




# Define the function that get the paramter list corresponding to distribution and the domain name
##################################################################################################################
# Input :      Dataframe: The dataframe contains the distribution information
#                   Dist: The distribution type. Default is 'Uniform'
#             DomainName: The domain name for the distribution. Default is 'LineDistribution'
#
# Output:   DistParaList: A list that contains the distribution name and corresponding parameters
##################################################################################################################
def getLineItemDistParas(Dataframe, Dist = 'Uniform', DomainName = 'LineDistribution'):
    if Dist == 'Uniform':
        Min = int(Dataframe['Add_value1'][Dataframe['Name'] == DomainName].item())   # The min value in uniform distribution
        Max = int(Dataframe['Add_value2'][Dataframe['Name'] == DomainName].item())   # The max value in uniform distribution
    DistParaList = [Dist, Min, Max]
    return  DistParaList


# Define the function that provides uniform distribution decimal or integer value
###################################################################################################################
# Input :          IsInt: indicate return integer value or float value. Default value is true
#                    Min: the lower bound of the uniform distribution
#                    Max: the upper bound of the uniform distribution
#                  Digit: the decimal digit. Default value is 1
#
# Output:          a uniform distribution value
####################################################################################################################
def uniform(Min, Max,IsInt=True, Digit=1 ):
    if IsInt == True:
        return random.randint(Min, Max)
    else:
        return round(random.uniform(Min, Max), Digit)



# Define the function that selects rows in a dataframe based on weights list
#####################################################################################################################
# Input :      Population: the sample population. List
#                 Weights: the weight value associated with the population. List. If weights=[], use uniform 
#                          distribution to select entries
#                    Size: number of samples we want to get
#                 Replace: whether the sample is with or without replacement
#
# Output:            the sample stored as a np.array 
#####################################################################################################################
def sample(Population, Weights, Size, Replace=False):
    if Weights:
        return np.random.choice(a=Population, size=Size, replace=Replace, p=Weights)
    else:
        return np.random.choice(a=Population, size=Size, replace=Replace)



# Define the function that generates the initial dataframe for Order, Sku and Location
####################################################################################################################
# Input :     Rownumber: the number of rows in the generated dataframe
#         DataframeType: specify the dataframe is for Order or Sku or Location. Ex. df_type = 'Order'
#
# Output:            df: the generated dataframe
####################################################################################################################
def dataframeInitial(Rownumber, DataframeType):
    IDName = DataframeType + 'ID'
    # Generate the order dataframe
    df = pd.DataFrame(np.arange(1,Rownumber+1,1),columns=[IDName])
    # Modify the ID to let it have proper names
    # df[IDName] = df[IDName].apply(lambda x: DataframeType+ str(x))
    return df


# Define the function that generates the initial dataframe for Order_Sku 
#####################################################################################################################
# Input :       OrderDataframe: the initial order dataframe
#                 SKUDataframe: the initial sku dataframe
#                   SKUWeights: the weight values for skus
#                LineOrderDist: the parameter list for the distribution of the number of lines in an order. 
#             QuantityLineDist: the parameter list for the distribution of the sku quantity in an order line. 
#
# Output:              df: the order_sku dataframe
######################################################################################################################
def dataframeOrderSKUInitial(OrderDataframe, SKUDataframe, SKUWeights, LineOrderDist, QuantityLineDist):
    NumOrder = len(OrderDataframe)
    ColNames = ['OrderID','SkuID','Quantity']
    df = pd.DataFrame(columns = ColNames)
    Population = SKUDataframe['SkuID'].tolist()
    for i in range(NumOrder):
        # get the lines for the ith order
        if LineOrderDist[0] == 'Uniform':
            Line = uniform(LineOrderDist[1], LineOrderDist[2])
        # create rows associated with the order
        df = df.append([OrderDataframe.iloc[i]]*Line,ignore_index=True)
        # assign SkuID for each row
        df['SkuID'][-Line:] =  sample(Population, SKUWeights, Line)
    # assign Sku quantities for each row
    df['Quantity'] = 0
    if QuantityLineDist[0] == 'Uniform':
        df['Quantity'] = df['Quantity'].apply(lambda x: uniform(QuantityLineDist[1], QuantityLineDist[2]))
    return df



# Define the function that generates the initial dataframe for Sku_Location
##########################################################################################################################
# Input :           SKUDataframe: the initial sku dataframe
#              LocationDataframe: the initial location dataframe
#                        Weights: he weight value associated with the population. List. If Weights=[], use uniform 
#                                 distribution to select entries
#                           Rule: the matching Rule for skus and locations. four Rules can be selected:
#                                   'oto': each sku can only be placed in one location and each location can only hold one sku
#                                   'otm': each sku can be placed in multiple locations but each location can only hold one sku
#                                   'mto': each sku can only be placed in one location but each location can hold multiple skus
#                                   'mtm': each sku can be placed in multiple locations and each location can hold multiple skus
#
# Output:                     df: the initial sku-location dataframe      
###########################################################################################################################
def dataframeSKULocationInitial(SKUDataframe, LocationDataframe, Weights=[], Rule='oto'):
    if Rule == 'oto':
        # each sku can only be placed in one location and each location can only hold one sku
        if len(SKUDataframe) > len(LocationDataframe):
            print('The number of Skus cannot be greater than the number of Locations in One_to_One Rule ')
            return
        df = SKUDataframe.copy()
        ColName = 'PickNodeID'
        Replace = False
        Population = LocationDataframe[ColName].tolist()
    elif Rule == 'otm':
        # each sku can be placed in multiple locations but each location can only hold one sku
        df = LocationDataframe.copy()
        ColName = 'SkuID'
        Replace = True
        Population = SKUDataframe[ColName].tolist()
    elif Rule == 'mto':
        # each sku can only be placed in one location but each location can hold multiple skus
        df = SKUDataframe.copy()
        ColName = 'PickNodeID'
        Replace = True
        Population = LocationDataframe[ColName].tolist()
    elif Rule == 'mtm':       
        # each sku can be placed in multiple locations and each location can hold multiple skus
        column_names = ['SkuID','LocationID']
        df = pd.DataFrame(columns = column_names)
        # TBD
    else:
        print('Rule is not recognized,please check the Rule parameter.')
        
    # Pair SKU and PcikNode
    NumRows = len(df)
    df[ColName] = sample(Population, Weights, NumRows, Replace)


    return df



# Define the function that generates a list of datetime(YYYY-MM-DD HH:MM:SS)
##########################################################################################################################
# Input :             Size: the returned list Size
#                Startdate: the start date. Format 'MM/DD/YYYY HH:MM:SS'
#                  Enddate: the end date. Format 'MM/DD/YYYY HH:MM:SS'
#                 TimeRule: specify the time in a date. Can be 'fixed' or 'random'.
#
# Output:        DateList: the return datetime list
##########################################################################################################################
def datatimeGenerator(Size, Startdate='09/05/2020 00:00:00',Enddate='20/05/2020 00:00:00', TimeRule='fixed'):
    
    Start = datetime.strptime( Startdate,'%d/%m/%Y %H:%M:%S')
    End = datetime.strptime( Enddate,'%d/%m/%Y %H:%M:%S')
    # get the zero time (00:00:00)
    ZeroTime = datetime(2019,8,10,0,0,0).time()
    AdjustDate = datetime.combine(Start.date(),ZeroTime)
    DaysBetweenDates = (End-Start).days
    # check if same day
    if DaysBetweenDates == 0:
        DateList = [0]*Size
    else:
        DateList = sample(range(DaysBetweenDates),Weights=[], Size=Size, Replace=True).tolist()
    DateList.sort()
    for i in range(Size):
        if TimeRule == 'fixed':
            DateList[i] = Start + dt.timedelta(days=DateList[i])
        elif TimeRule == 'random':
            DateList[i] = AdjustDate + dt.timedelta(days=DateList[i], seconds=random.randrange(86400))
        else:
            print('Cannot recognize the TimeRule parameter, please check it.')
    return DateList



# Define the function that outputs the csv files
#########################################################################################################################
# Input :               ParaList: the list stores the paramters
#                                 [0]: OrderFinialDataframe - the final order dataframe
#                                 [1]: SKUFinalDataframe - the final sku dataframe
#                                 [2]: LocationFinalDataframe - the final location dataframe
#                                 [3]: OrderSKUFinalDataframe - the final order_sku dataframe
#                                 [4]: SKULocationFinalDataframe - the final sku_location dataframe
#                 OrderFilenName: the output order file name. Default is 'Orders.csv'
#                    SKUFileName: the output sku file name. Default is 'Skus.csv'
#               LocationFileName: the output location file name. Default is 'Locations.csv'
#               OrderSKUFileName: the output location file name. Default is 'Order_Sku.csv'
#            SKULocationFileName: the output location file name. Default is 'Sku_Location.csv'
#
# Output:        five csv files
#########################################################################################################################
def outputCSV(ParaList, OrderFilenName = 'Orders.csv', SKUFileName = 'Skus.csv', LocationFileName = 'Locations.csv', OrderSKUFileName = 'Order_Sku.csv', SKULocationFileName = 'Sku_Location.csv' ):
    OrderFinalDataframe = ParaList[0]
    SKUFinalDataframe = ParaList[1]
    LocationFinalDataframe = ParaList[2]
    OrderSKUFinalDataframe = ParaList[3]
    SKULocationFinalDataframe = ParaList[4]
       
    # Write csv files
    SKUFinalDataframe.to_csv('Skus.csv',index=False)
    LocationFinalDataframe.to_csv('Locations.csv',index=False)
    OrderFinalDataframe.to_csv('Orders.csv', index=False)
    SKULocationFinalDataframe.to_csv('SkuLoc.csv', index=False)
    OrderSKUFinalDataframe.to_csv('OrderSkus.csv', index=False)
    




# Define the function that creates the initial dataframes
#########################################################################################################################################
# Input :              ParaList: the list stores the paramters
#                                [0]: NumOrders - the number of orders
#                                [1]: NumSKUs - the number of skus
#                                [2]: NumLocations - the number of locations(PcikNode)
#                                [3]: SKUWeights - the weight value associated with the population. List. If weights=[], use uniform 
#                                                  distribution to select entries
#                                [4]: LineOrderDist - the parameter list for the distribution of lines per order
#                                [5]: QuantityLineDist - the parameter list for the distribution of quantity per order line
#
# Output:              five initial dataframes
########################################################################################################################################
def dataframesInitialization(ParaList):
    NumOrders = ParaList[0]
    NumSKUs = ParaList[1]
    NumLocations = ParaList[2]
    SKUWeights = ParaList[3]
    LineOrderDist = ParaList[4]
    QuantityLineDist = ParaList[5]

    # Generate the order, sku and location initial dataframe
    OrderInitial = dataframeInitial(NumOrders,'Order')
    SKUInitial = dataframeInitial(NumSKUs, 'Sku')
    # Location is the PickNode location
    LocationInitial = dataframeInitial(NumLocations,'PickNode')
    # Generate the initial order-sku dataframe
    OrderSKUInitial = dataframeOrderSKUInitial(OrderInitial,SKUInitial,SKUWeights, LineOrderDist, QuantityLineDist)
    # Generate the initial sku-location dataframe
    SKULocationInitial = dataframeSKULocationInitial(SKUInitial, LocationInitial)
    return(OrderInitial, SKUInitial, LocationInitial, OrderSKUInitial, SKULocationInitial)

# Define The function that complete the order dataframe
########################################################################################################################
# Input :                  ParaList: the list stores the paramters
#                                    [0]: OrderDataframe - the initial order dataframe
#                                    
#
# Output:       OrderFinalDataframe: the final order dataframe
########################################################################################################################
def completeOrder(ParaList):
    
    OrderDataframe = ParaList[0]
    NumOrders = len(OrderDataframe)
    # generate a new dataframe
    OrderFinalDataframe = OrderDataframe.copy()

    # Add release date column
    ColName = 'ReleaseDate'
    ReleaseList = datatimeGenerator(NumOrders, Startdate='09/05/2020 00:00:00',Enddate='09/05/2020 00:00:00')
    OrderFinalDataframe[ColName] = ReleaseList
    # Add due date column
    ColName = 'DueDate'
    DueList = datatimeGenerator(NumOrders,Startdate='11/05/2020 23:59:59',Enddate='22/05/2020 23:59:59')
    OrderFinalDataframe[ColName] = DueList

    # Add wave infomation
    ColName = 'Wave' 
    OrderFinalDataframe[ColName] = 1
    
    # Add final destination node column(for Simio)
    ColName = 'FinalDestination' 
    OrderFinalDataframe[ColName] = 'Input@Depot'
    
    return OrderFinalDataframe


# Define The function that complete the sku dataframe
########################################################################################################################
# Input :                ParaList: the list stores the paramters 
#                                  [0]: SKUDataframe - the initial sku dataframe
#
# Output:       SKUFinalDataframe: the final sku dataframe
########################################################################################################################
def completeSKU(ParaList):

    SKUDataframe = ParaList[0]
    NumSKUs = len(SKUDataframe)

    # generate a new dataframe
    SKUFinalDataframe = SKUDataframe.copy()

    # Add volumn column
    ColName = 'Volume'
    VolumeArray = sample(range(10),Weights=[], Size=NumSKUs, Replace=True)
    SKUFinalDataframe[ColName] = VolumeArray

    # Add weight column
    ColName = 'Weight'
    SKUFinalDataframe[ColName] = 0
    SKUFinalDataframe[ColName] = SKUFinalDataframe[ColName].apply(lambda x: uniform(5, 10,IsInt=False, Digit=1 ))

    return SKUFinalDataframe


# Define The function that complete the location dataframe
########################################################################################################################
# Input :                     ParaList: the list stores the paramters 
#                                       [0]: LocationDataframe - the initial location dataframe
#                                       [1]: Boudning - the bounding values of the layout
#
# Output:       LocationFinalDataframe: the final location dataframe
########################################################################################################################
def completeLocation(ParaList):

    LocationDataframe = ParaList[0]
    Bounding = ParaList[1]
    # generate a new dataframe
    LocationFinalDataframe = LocationDataframe.copy()

    # Add X-coordinate value column
    ColName = 'Xloc'
    LocationFinalDataframe[ColName] = 0.0
    LocationFinalDataframe[ColName] = LocationFinalDataframe[ColName].apply(lambda x: uniform(Bounding[0], Bounding[6],IsInt=False, Digit=1 ))
    # Add Z-coordinate value column
    ColName = 'Zloc'
    LocationFinalDataframe[ColName] = 0.0
    LocationFinalDataframe[ColName] = LocationFinalDataframe[ColName].apply(lambda x: uniform(Bounding[1], Bounding[3],IsInt=False, Digit=1 ))

    return LocationFinalDataframe


# Define The function that complete the order_sku dataframe
########################################################################################################################
# Input :                     ParaList: the list stores the paramters 
#                                       [0]: OrderSKUDataframe - the initial order_sku dataframe
#
# Output:       OrderSKUFinalDataframe: the final order_sku dataframe
########################################################################################################################
def completeOrderSKU(ParaList):

    OrderSKUDataframe = ParaList[0]
    
    OrderSKUDataframe['PickTime'] = '60'
    OrderSKUDataframe['LoadTime'] = '30'
    # generate a new dataframe
    OrderSKUFinalDataframe = OrderSKUDataframe

    return OrderSKUFinalDataframe


# Define The function that complete the sku_location dataframe
########################################################################################################################
# Input :                        ParaList: the list stores the paramters
#                                          [0]: SKULocationDataframe - the initial sku_location dataframe
#                                          [1]: PickNode and CoopNode combination dtatframe
#
# Output:       SKULocationFinalDataframe: the final sku_location dataframe
########################################################################################################################
def completeSKULocation(ParaList):

    SKULocationDataframe = ParaList[0]
    PickCoopPair = ParaList[1]
       
    # generate a new dataframe
    SKULocationFinalDataframe = pd.merge(SKULocationDataframe, PickCoopPair, how = 'left', on='PickNodeID'  )

    return SKULocationFinalDataframe


# Scheduler
class CoopScheduler():
    
    # initialization
    def __init__(self,PickerNum, TransNum):
        self.pickerno = PickerNum
        self.transno = TransNum
        # dictionary that store routes for pickers and transporters
        self.routes = dict()
        # OrderSkus information
        self.lineitem = pd.DataFrame()
        
    def simple_scheduler(self, Order, OrderSku, Capacity, Ctype = 'Order'):
        
        # go through each row in the ordersku df
        # assign picker transporter pair
        tempdf = Order.copy()
        tempdf['PickerID'] = 0
        tempdf['TransporterID'] = 0
        for i in range(len(Order)):
            if (i+1) % self.pickerno == 0:
                pickerID = self.pickerno
            else:
                pickerID = (i+1) % self.pickerno
                
            if (i+1) % self.transno == 0:
                transID = self.transno
            else:
                transID = (i+1) % self.transno
            tempdf['PickerID'].iloc[i] = pickerID 
            tempdf['TransporterID'].iloc[i] = transID 
        
        OrderSku = pd.merge(OrderSku, tempdf[['OrderID','PickerID','TransporterID']], how = 'left', on = 'OrderID')
        
        
        # assign batch
        # empty dataframe 
        df = pd.DataFrame()       
        for trans in range(self.transno):
            # filter lines for current picker
            gp = tempdf[['OrderID','TransporterID']][tempdf['TransporterID'] == trans+1].groupby('OrderID').size().reset_index(name = 'Drop')
            # batch empty list
            batchlist = []
            for i in gp.index:
                batchlist.append(math.ceil((i+1)/Capacity))
            
            gp['TransporterID'] = trans + 1
            gp['BatchID'] = batchlist
            df = pd.concat([df,gp])
        # drop unrelated colum    
        df = df.drop('Drop',axis = 1)
        OrderSku = pd.merge(OrderSku, df, how = 'left', on=['OrderID','TransporterID'])
        
        return(OrderSku)
    
    def route_generator(self, OrderSkus, Skus):
        
        # dataframe contains Orderskus information and corresponding Pick and Coop Node ID
        tempdf = pd.merge(OrderSkus, Skus, how='left', on='SkuID')
        # add a frequency column
        freq = tempdf.groupby(['TransporterID','BatchID','CoopNodeID']).size().reset_index(name = 'frequency')
        df = pd.merge(tempdf, freq, how='left', on=['TransporterID','BatchID','CoopNodeID']).sort_values(['BatchID','frequency','CoopNodeID'])
        self.lineitem = df
        
        # picker route
        for picker in range(1, self.pickerno+1):
            mask = df['PickerID'] == picker
            filter_df = df[['PickNodeID','CoopNodeID']][mask]
            # route list
            route = []
            for i in range(len(filter_df)):
                route.append('MyPickNode' + filter_df['PickNodeID'].iloc[i].astype(str))
                route.append('MyCoopNode' + filter_df['CoopNodeID'].iloc[i].astype(str))
            route.append('EndNode')
            self.routes['route_p{}'.format(picker)] = route
            
        # transpoter route
        for trans in range(1, self.transno+1):
            # get batch number for that transporter
            batchno = len(OrderSkus[OrderSkus['TransporterID'] == trans]['BatchID'].unique())
            # route list
            route = []
            for batch in range(1, batchno+1):
                # filter the data fro correct batch and transporter
                mask = (df['TransporterID'] == trans) & (df['BatchID'] == batch)
                coopcol = df[mask]['CoopNodeID']
                # track last value
                lastv = coopcol.iloc[0]
                # build route
                route.append('MyCoopNode' + lastv.astype(str))
                for i in range(1,len(coopcol)):
                    if coopcol.iloc[i] != lastv:
                        lastv = coopcol.iloc[i]
                        route.append('MyCoopNode' + lastv.astype(str))
                route.append('Input@Depot')
            route.append('EndNode')
            self.routes['route_t{}'.format(trans)] = route
                