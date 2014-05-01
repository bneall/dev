masterLayerList = []
searchMatch = []

#-------------------------------------------------------------------------------------------------------------------------------------------
def stackIterator(layer):

    if layer.hasMaskStack():
        stack = layer.maskStack()
    elif not layer.isAdjustmentLayer() and layer.hasAdjustmentStack():
        stack = layer.adjustmentStack()
    elif layer.isGroupLayer():
        stack = layer.layerStack()
    else:
        return

    layers = stack.layerList()
    for subLayer in layers:
       getLayerInfo(subLayer)


#-------------------------------------------------------------------------------------------------------------------------------------------
def getAdjustmentLayerInfo(layer):
    parameter1_dict = {}

    for parameter_name in layer.primaryAdjustmentParameters():
        parameter_value = str(layer.getPrimaryAdjustmentParameter(parameter_name))
        parameter1_dict[parameter_name]=parameter_value
    return parameter1_dict

    if layer.hasSecondaryAdjustment():
        parameter2_dict = {}
        for parameter_name in layer.secondaryAdjustmentParameters():
            parameter_value = str(layer.getSecondaryAdjustmentParameter(parameter_name))
            parameter2_dict[parameter_name]=parameter_value
        return parameter1_dict, parameter2_dict


#-------------------------------------------------------------------------------------------------------------------------------------------
def getProceduralLayerInfo(layer):
    procedural_type_name = layer.proceduralType()
    parameter1_dict = {}

    for parameter_name in layer.proceduralParameters():
        parameter_value = layer.getProceduralParameter(parameter_name)
        parameter1_dict[parameter_name]=parameter_value
    return parameter1_dict


#-------------------------------------------------------------------------------------------------------------------------------------------
def getLayerParent(layer):
    for item in layer.parents():
        node = str(type(item))
        if 'Layer' in node:
            return item.name()
        else:
            return None


#-------------------------------------------------------------------------------------------------------------------------------------------
def getLayerInfo(layer):

    value = 'No Parameters'
    layerBlendMode = layer.blendMode()
    layerBlendAmount = layer.blendAmount()
    layerName = layer.name()
    layerParent = getLayerParent(layer)
    layerRef = None
    layerType = None
    layerKey = None
    layerMask = None
    layerLock = False
    layerVisible = True

    if layer.hasMask() and not layer.hasMaskStack():
        layerMask = "Mask"
    if layer.hasMaskStack():
        layerMask = "MaskStack"
    if layer.isGroupLayer():
        layerType = "Group"
    if layer.isPaintableLayer():
        layerType = "Paintable"
    if layer.isProceduralLayer():
        layerType = "Procedural"
        layerKey = layer.proceduralType()
        value = getProceduralLayerInfo(layer)
    if layer.isAdjustmentLayer():
        layerType = "Adjustment"
        layerKey = layer.primaryAdjustmentType()
        value = getAdjustmentLayerInfo(layer)
    if layer.isVisible():
        layerVisible = True
    if layer.isLocked():
        layerLock = True

    layerDict = {
                    "Name" : layerName,
                    "Parent" : layerParent,
                    "Type": layerType,
                    "Key": layerKey,
                    "Mask" : layerMask,
                    "Locked" : layerLock,
                    "Visible" : layerVisible,
                    "BlendMode" : layerBlendMode,
                    "BlendAmount" : layerBlendAmount
                    }

    global masterLayerList
    masterLayerList.append(layerDict)

    stackIterator(layer)

#------------------------------------------------------------------------------
def getAllLayerInfo():
    layers = mari.current.channel().layerList()
    #Clear Master Layer
    global masterLayerList
    masterLayerList = []

    #Build Master Layer List
    for layer in layers:
        getLayerInfo(layer)


def searchAllLayers(layerParent):
    layers = mari.current.channel().layerList()
    for layer in layers:
        searchLayers(layer, layerParent)

def searchLayers(layer, layerParent):
    global searchMatch
    if layer.name() == layerParent:
        searchMatch = layer

    stackIterator(layer)

#------------------------------------------------------------------------------
def buildAllLayers():
    currentChannel = mari.current.channel()

    refMask = False
    refGroup = None
    refLayer = None

    for layer in masterLayerList:
        #Layer Attributes
        layerName = layer["Name"]
        layerParent = layer["Parent"]
        layerType = layer["Type"]
        layerKey = layer["Key"]
        layerMask = layer["Mask"]
        layerLocked = layer["Locked"]
        layerVisible = layer["Visible"]
        layerBlendMode = layer["BlendMode"]
        layerBlendAmount = layer["BlendAmount"]

        layerStack = currentChannel

        if layerType == "Group":
            if not layerParent:
                newLayer = layerStack.createGroupLayer(layerName)
            else:
                searchAllLayers(layerParent)
                if searchMatch:
                    layerStack = searchMatch.layerStack()
                    newLayer = layerStack.createGroupLayer(layerName)

getAllLayerInfo()
