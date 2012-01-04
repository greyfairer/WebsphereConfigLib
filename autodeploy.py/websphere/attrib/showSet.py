#
# Author: Barry Searle
#
# (C) Copyright IBM Corp. 2004,2006 - All Rights Reserved.
# DISCLAIMER:
# The following source code is sample code created by IBM Corporation.
# This sample code is not part of any standard IBM product and is provided
# to you solely for the purpose of assisting you in the development of your
# applications. The code is provided 'AS IS', without warranty or condition
# of any kind. IBM shall not be liable for any damages arising out of your
# use of the sample code, even if IBM has been advised of the possibility of
# such damages.
#
# Change History:
# 2.0 (10feb2006) initial Jython version, removed unneeded modules[0] from getModuleID
# 2.0 (10feb2006) removed getModuleID WebModuleDeployment (works for any module)
# 1.1 (17nov2004) initial shipped version
#
from websphere.Definitions import wsadminToList
from log.log import INFO_, log, VERBOSE_, ERROR_, DEBUG_
from websphere import WebSphere

def getModuleID(appName, moduleName):
    objID = WebSphere.AdminConfig.getid("/Deployment:" + appName + "/")
    objID = WebSphere.AdminConfig.showAttribute(objID, "deployedObject")
    modules = WebSphere.AdminConfig.showAttribute(objID, "modules")
    #modules = WebSphere.AdminConfig.showAttribute(WebSphere.AdminConfig.showAttribute(WebSphere.AdminConfig.getid("/Deployment:"+appName+"/" ), "deployedObject" ), "modules" )
    log(DEBUG_, "getModuleID: modules[]=" + `modules`)
    modules = wsadminToList(modules)
    log(DEBUG_, "getModuleID: modules=" + `modules`)
    for module in modules:
        id = WebSphere.AdminConfig.showAttribute(module, "uri")
        if id == moduleName:
            log(DEBUG_, "getModuleID: =" + `module`)
            return module
            #endIf
        #endFor
    return ""

#endDef

def showAttribute(objName, objType, attName, appName):
    try:
        if "Application" == objType:
            objID = WebSphere.AdminConfig.getid("/Deployment:" + objName + "/")
            objID = WebSphere.AdminConfig.showAttribute(objID, "deployedObject")
        else:
            objID = getModuleID(appName, objName)
            #endElse

        if attName == "ALL" or attName == "all" or attName == "*" or attName == "":
            att = WebSphere.AdminConfig.show(objID)
        else:
            attNameSplit = attName.split('.')
            for attNamePrefix in attNameSplit[:-1]:
                if attNamePrefix[0].isupper():
                    configObjs = WebSphere.AdminConfig.list(attNamePrefix, objID).splitlines()
                    if len(configObjs) > 0:
                        objID = configObjs[0]
                    else:
                        return None
                else:
                    objID = WebSphere.AdminConfig.showAttribute(objID, attNamePrefix)

            attName = attNameSplit[-1]
            att = WebSphere.AdminConfig.showAttribute(objID, attName)
            #endElse
        log(VERBOSE_, "showAtribute: " + objName + " " + attName + "=" + att)
        return att
    except:
        return None

#endDef

def setAttribute(objName, objType, attName, attValue, appName, showSetResult):
    log(INFO_,
        "setAttribute: Type=" + objType + "  Name=" + objName + "  App=" + appName + "  Attribute=" + attName + "  Value=" + attValue)

    if "Application" == objType:
        objID = WebSphere.AdminConfig.showAttribute(WebSphere.AdminConfig.getid("/Deployment:" + objName + "/"),
            "deployedObject")
    else:
        objID = getModuleID(appName, objName)
        #endElse
    if attName.count('.') > 0:
        attNameSplit = attName.split('.')
        realAttName = attNameSplit[-1]
        realObjID = objID

        for i in xrange(0, len(attNameSplit) - 1):
            attNamePrefix = attNameSplit[i]
            if attNamePrefix[0].isupper():
                configObjs = WebSphere.AdminConfig.list(attNamePrefix, objID).splitlines()
                if len(configObjs) > 0:
                    realObjID = configObjs[0]
                else:
                    attributes = [[realAttName, attValue]]

                    for j in xrange(len(attNameSplit) - 2, i, -1):
                        attributes = [[attNameSplit[j], attributes]]
                    log(INFO_, "create %s with %s" % (attNamePrefix, attributes))
                    realObjID = WebSphere.AdminConfig.create(attNamePrefix, realObjID, attributes)
                    return
            else:
                realObjID = WebSphere.AdminConfig.showAttribute(realObjID, attNamePrefix)
            log(INFO_, "prefix %s = %s" % (attNamePrefix, realObjID))
    else:
        realAttName, realObjID = attName, objID

    if len(realObjID) > 0:
        log(INFO_, "modify %s = %s" % (realObjID, realAttName))
        modified = WebSphere.AdminConfig.modify(realObjID, [[realAttName, attValue]])
    else:
        modified = ""
        log(ERROR_, "could not get objID for Type=" + objType + "  Name=" + objName + "  Attribute=" + attName)
        return
        #endIf
    if len(modified) > 0:
        log(INFO_, modified)
        #endIf

    if showSetResult:
        showAttribute(objName, objType, attName, appName)
        #endIf

#endDef
