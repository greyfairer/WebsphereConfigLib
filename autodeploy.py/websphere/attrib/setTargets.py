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
# 2.0 (10feb2006) initial Jython version
# 1.3 (22apr2005) API:setTargets+setModuleMappings: added 'appFile' parameter,
# 1.3 (22apr2005) major restructure, uses WAS-5.0 compatible "WebSphere.AdminApp taskInfo"
# 1.1 (17nov2004) initial shipped version
#
from websphere.Definitions import wsadminToList, Globals
from log.log import INFO_, log, MAJOR_, VERBOSE_, ERROR_, DEBUG_
from websphere import WebSphere
from websphere.applicationModel import ApplicationTarget
import sys

def setTargets ( applicationModel, appFile ):
        setModuleMappings(applicationModel, appFile )
#endDef

def mapModulesToServers ( applicationModel, appFile ):
    cellName = Globals.wsadminCell
    targets = ""
    for cluster in applicationModel.clusters:
            clusterName = cluster.clusterName
            if clusterName != "":
                t = "+WebSphere:cell="+cellName+",cluster="+clusterName
                targets = targets+t
    for nodeServerPair in applicationModel.servers:
            nodeName = nodeServerPair.nodeName
            serverName = nodeServerPair.serverName
            t = "+WebSphere:cell="+cellName+",node="+nodeName+",server="+serverName
            targets = targets+t
    moduleTargets={}
    for module in applicationModel.modules:
        moduleTarget=""
        for target in module.targets:
            if target.targetType()==ApplicationTarget.CLUSTER and target.clusterName!="":
                t = "+WebSphere:cell="+cellName+",cluster="+target.clusterName
                moduleTarget = moduleTarget+t
            elif target.targetType()==ApplicationTarget.SERVER:
                t = "+WebSphere:cell="+cellName+",node="+target.nodeName+",server="+target.serverName
                moduleTarget = moduleTarget+t
        if moduleTarget!="":
            log(VERBOSE_, "setModuleMappings: target["+module.name+"]="+moduleTarget[1:] )                
            moduleTargets[module.name]=moduleTarget[1:]
    if targets=="" and moduleTargets=={}:
        return
    if targets != "":
        targets = targets[1:]
        log(VERBOSE_, "setModuleMappings: targets="+`targets` )

    log(VERBOSE_, "setModuleMappings: EarFile Mapping query: WebSphere.AdminApp.taskInfo("+appFile+",\"MapModulesToServers\")" )
    lines = WebSphere.AdminApp.taskInfo(appFile, "MapModulesToServers" )

    log(DEBUG_, "EarFile default mapping="+lines )
    lines = wsadminToList(lines)
    mappings = []
    m1 = ""
    MODULE = "MODULE: "
    URI = "URI: "

    for line in lines:
            testMOD = line[0:(len(MODULE) -0)].upper()
            testURI = line[0:(len(URI) -0)].upper()
            if (testMOD == MODULE):
                    m1 = line[len(MODULE):]
                    m1 = m1.strip( )
                    log(VERBOSE_, "MODULE="+m1 )
            elif (testURI == URI):
                    m2 = line[len(URI):]
                    m2 = m2.strip( )
                    log(VERBOSE_, "URI="+m2 )
                    moduleName=m2.split(',')[0]
                    if moduleTargets.has_key(moduleName):
                        mapping = [m1, m2, moduleTargets[moduleName]]
                    else:
                        mapping = [m1, m2, targets]
                    log(INFO_, "setModuleMapping: mapping ["+moduleName+"]="+`mapping` )
                    mappings.append(mapping)
                    m1 = ""
            #endIf
    #endFor

    log(VERBOSE_, "setModuleMappings: combined mappings="+`mappings` )
    return mappings

def mapWebModToVH( applicationModel, appFile ):
    earTarget = applicationModel.virtualHost
    
    moduleTargets={}
    for module in applicationModel.modules:
        if module.virtualHost != "":
            moduleTargets[module.name] = module.virtualHost

    log(VERBOSE_, "setModuleMappings: EarFile Mapping query: WebSphere.AdminApp.taskInfo("+appFile+",\"MapWebModToVH\")" )
    lines = WebSphere.AdminApp.taskInfo(appFile, "MapWebModToVH" )
    #endIf
    log(DEBUG_, "EarFile default mapping="+lines )
    lines = wsadminToList(lines)
    mappings = []
    m1 = ""
    MODULE = "WEB MODULE: "
    URI = "URI: "

    for line in lines:
            testMOD = line[0:(len(MODULE) -0)].upper()
            testURI = line[0:(len(URI) -0)].upper()
            if (testMOD == MODULE):
                    m1 = line[len(MODULE):]
                    m1 = m1.strip( )
                    log(VERBOSE_, "MODULE="+m1 )
            elif (testURI == URI):
                    m2 = line[len(URI):]
                    m2 = m2.strip( )
                    log(VERBOSE_, "URI="+m2 )
                    moduleName=m2.split(',')[0]
                    if moduleTargets.has_key(moduleName):
                        mapping = [m1, m2, moduleTargets[moduleName]]
                    else:
                        mapping = [m1, m2, earTarget]
                    log(INFO_, "setModuleMapping: mapping ["+moduleName+"]="+`mapping` )
                    mappings.append(mapping)
                    m1 = ""
            #endIf
    #endFor

    log(VERBOSE_, "setModuleMappings: combined mappings="+`mappings` )
    return mappings

def setModuleMappings ( applicationModel, appFile ):
        mappings = mapModulesToServers( applicationModel, appFile )
        options = ["-MapModulesToServers", mappings]
        log(DEBUG_, "invoking: WebSphere.AdminApp edit "+applicationModel.name+" "+`options` )
        try:
                _excp_ = 0
                response = WebSphere.AdminApp.edit(applicationModel.name, options )
        except:
                _type_, _value_, _tbck_ = sys.exc_info()
                _excp_ = 1
        #endTry
        temp = _excp_
        if (temp > 0):
                log(ERROR_, "setModuleMappings: Exception trying to WebSphere.AdminApp edit "+applicationModel.name+" "+`options` )
                return
        #endIf
        if (len(response) > 0):
                log(MAJOR_, "setModuleMappings: MapModulesToServers response="+response )
        #endIf
        log(VERBOSE_, "setModuleMappings: DONE." )
#endDef
