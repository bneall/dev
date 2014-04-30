def printGroupLayerInfo(layer):
    layers = []
    try:
        stack = layer.layerStack()
        layers = stack.layerList()
    except:
        return

    for sub_layer in layers:
       printLayerInfo(sub_layer)


def printAdjustmentStackLayerInfo(layer):
    layers = []
    try:
        if not layer.hasAdjustmentStack():
            return

        stack = layer.adjustmentStack()
        layers = stack.layerList()
    except:
        return

    for sub_layer in layers:
       printLayerInfo(sub_layer)


def printMaskStackLayerInfo(layer):
    layers = []
    try:
        if not layer.hasMaskStack():
            return

        stack = layer.maskStack()
        layers = stack.layerList()
    except:
        return

    for sub_layer in layers:
       printLayerInfo(sub_layer)


def printAdjustmentLayerInfo(layer):
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


def printProceduralLayerInfo(layer):
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

def printLayerInfo(layer):
    info = str()
    value = 'No Parameters'

    layerBlendMode = layer.blendMode()
    layerBlendAmount = layer.blendAmount()
    #info += " Blend" + str( blend_mode) + " '" + layer.blendModeName( blend_mode) + "' " + str( int( 100.0 * layer.blendAmount())) + "%"

    layerName = layer.name()
    layerParent = getLayerParent(layer)
    layerType = None
    layerMask = None
    layerLock = None
    layerVisible = None
    if layer.hasMask() and not layer.hasMaskStack():
        layerMask = layer.maskImageSet()
    if layer.isGroupLayer():
       layerType = "Group"
    if layer.isPaintableLayer():
        layerType = "Paintable"
    if layer.isProceduralLayer():
        layerType = "Procedural Layer"
        value = printProceduralLayerInfo(layer)
    if layer.isAdjustmentLayer():
        layerType = "Ajustment"
        value = printAdjustmentLayerInfo(layer)
    if layer.isVisible():
        layerVisible = True
    if layer.isLocked():
        layerLock = True

    layerDict = {"Name" : layerName, "Parent" : layerParent, "Mask" : layerMask, "Type": layerType, "Locked" : layerLock, "Visible" : layerVisible, "BlendMode" : layerBlendMode, "BlendAmount" : layerBlendAmount}
    print layerDict

    #print "Name: " + layer.name(), "Parent: ", getLayerParent(layer), info, value

    printAdjustmentStackLayerInfo(layer)
    printMaskStackLayerInfo(layer)
    printGroupLayerInfo(layer)

# ------------------------------------------------------------------------------

def printAllLayersInfo():
    layers = mari.current.channel().layerList()
    for layer in layers:
        printLayerInfo(layer)

# ------------------------------------------------------------------------------

printAllLayersInfo()
