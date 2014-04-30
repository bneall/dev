
masterLayerList = []

def maskStackIterator(layer):
    layers = []
    try:
        stack = layer.maskStack()
        layers = stack.layerList()
    except:
        return

    for sub_layer in layers:
       getLayerInfo(sub_layer)

def layerStackIterator(layer):
    layers = []
    try:
        stack = layer.layerStack()
        layers = stack.layerList()
    except:
        return

    for sub_layer in layers:
       getLayerInfo(sub_layer)

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


def getProceduralLayerInfo(layer):
    procedural_type_name = layer.proceduralType()
    parameter1_dict = {}

    for parameter_name in layer.proceduralParameters():
        parameter_value = layer.getProceduralParameter(parameter_name)
        parameter1_dict[parameter_name]=parameter_value
    return parameter1_dict

def getLayerParent(layer):
    for item in layer.parents():
        node = str(type(item))
        if 'Layer' in node:
            return item.name()
        else:
            return None

def getLayerInfo(layer):
    info = str()
    value = 'No Parameters'

    layerBlendMode = layer.blendMode()
    layerBlendAmount = layer.blendAmount()
    layerName = layer.name()
    layerParent = getLayerParent(layer)
    layerRef = None
    layerType = None
    layerKey = None
    layerMask = None
    layerLock = None
    layerVisible = None
    if layer.hasMask() and not layer.hasMaskStack():
        layerMask = layer.maskImageSet()
    if layer.hasMaskStack():
        layerMask = layer.maskStack()
    if layer.isGroupLayer():
        layerType = "Group"
    if layer.isPaintableLayer():
        layerType = "Paintable"
    if layer.isProceduralLayer():
        layerKey = layer.proceduralType()
        layerType = "Procedural"
        value = getProceduralLayerInfo(layer)
    if layer.isAdjustmentLayer():
        layerKey = layer.primaryAdjustmentType()
        layerType = "Adjustment"
        value = getAdjustmentLayerInfo(layer)
    if layer.isVisible():
        layerVisible = True
    if layer.isLocked():
        layerLock = True

    layerDict = {"Name" : layerName, 
               "Parent" : layerParent, 
               "Type": layerType,
               "Key": layerKey,
               "Mask" : layerMask,
               "Locked" : layerLock, 
               "Visible" : layerVisible, 
               "BlendMode" : layerBlendMode, 
               "BlendAmount" : layerBlendAmount}

    global masterLayerList
    masterLayerList.append(layerDict)
               
    if layer.isGroupLayer():
        layerStackIterator(layer)
    if layer.hasMaskStack():
        maskStackIterator(layer)
# ------------------------------------------------------------------------------

def getAllLayerInfo():
    layers = mari.current.channel().layerList()
    #Build Master Layer List
    for layer in layers:
        getLayerInfo(layer)
    
    for layer in masterLayerList:
        if layer["Type"] == "Group":
            print layer

def buildAllLayers():
    currentChannel = mari.current.channel()

    refLayer = None
    for layer in masterLayerList:
        layerName = layer["Name"]
        layerParent = layer["Parent"]
        layerType = layer["Type"]
        layerKey = layer["Key"]
        layerMask = layer["Mask"]
        layerLocked = layer["Locked"]
        layerVisible = layer["Visible"]
        layerBlendMode = layer["BlendMode"]
        layerBlendAmount = layer["BlendAmount"]

        # if layerType is "Adjustment":
            # newLayer = layerStack.createAdjustmentLayer(layerName, layerKey, refLayer, 32)
        # if layerType is "Procedural":
            # newLayer = layerStack.createProceduralLayer(layerName, layerKey, refLayer, 32)
        # if layerType is "Group":
            # newLayer = layerStack.createGroupLayer(layerName, None, 32)
        # if layerType is "Paintable":
            # newLayer = layerStack.createPaintableLayer(layerName, None, None, 32)

        refLayer = newLayer
    
    
getAllLayerInfo()
