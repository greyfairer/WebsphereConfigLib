#
# Author: Barry Searle
#
# (C) Copyright IBM Corp. 2004,2007 - All Rights Reserved.
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
# 3.0 (25apr2007) added support for installOptions, removed hardcoded "-nodeployejb"
# 2.0 (10feb2006) initial Jython version
# 1.1 (17nov2004) initial shipped version
#
from log.log import fail, INFO_, log, MAJOR_, VERBOSE_, highlight
from websphere import WebSphere
from websphere.application import checkIfAppExists
from websphere.attrib.setTargets import mapWebModToVH, mapModulesToServers
from com.ibm.websphere.management.exception import AdminException
import os

def AArrayToOptionString(aarray):
    result = []
    for item in aarray:
        qitem = []
        for iitem in item:
            qitem.append('"' + iitem + '"')
        result.append('[' + ' '.join(qitem) + ']')
    return '[' + ''.join(result) + ']'


def validateEAR( appPath ):
    if not os.path.isfile(appPath):
        fail("File does not exist: %s" % appPath)
        return 0
    else:
        return 1
    log(VERBOSE_, "validateEAR: FUTURE: installed EAR-FILE validation")

#endDef

def installEAR( action, appPath, applicationModel, clusterName, nodeName, serverName, installOptions ):
    update = "-appname '%s'" % applicationModel.name
    if action == "update":
        update = "-update " + update
        #endIf
    if serverName != "" and nodeName != "":
        options = update + " -verbose -node " + nodeName + " -server " + serverName + " -distributeApp " + installOptions
        options = options + " -MapWebModToVH " + AArrayToOptionString(mapWebModToVH(applicationModel, appPath))
        options = options + " -MapModulesToServers " + AArrayToOptionString(
            mapModulesToServers(applicationModel, appPath))
        highlight(MAJOR_, "AdminApp.install(" + appPath + "," + options + ")")
        installed = WebSphere.AdminApp.install(appPath, options)
    #endIf
    elif clusterName != "":
        options = update + " -verbose -cluster " + clusterName + " -distributeApp " + installOptions
        options = options + " -MapWebModToVH " + AArrayToOptionString(mapWebModToVH(applicationModel, appPath))
        options = options + " -MapModulesToServers " + AArrayToOptionString(
            mapModulesToServers(applicationModel, appPath))
        highlight(MAJOR_, "AdminApp.install(" + appPath + "," + options + ")")
        installed = WebSphere.AdminApp.install(appPath, options)
    #endIf
    else:
        options = update + " -verbose -distributeApp " + installOptions
        options = options + " -MapWebModToVH " + AArrayToOptionString(mapWebModToVH(applicationModel, appPath))
        options = options + " -MapModulesToServers " + AArrayToOptionString(
            mapModulesToServers(applicationModel, appPath))
        highlight(MAJOR_, "AdminApp.install(" + appPath + "," + options + ")")
        installed = WebSphere.AdminApp.install(appPath, options)
        #endElse
    if len(installed) > 0:
        log(INFO_, installed)
        #endIf
    appExists = checkIfAppExists(applicationModel)
    if appExists:
        pass
    else:
        fail("failed to installEAR application=" + applicationModel.name)
        #endElse
    log(VERBOSE_, "InstallEAR: DONE.")

#endDef

def uninstallEAR( applicationModel ):
    log(MAJOR_, "UninstallEAR: " + applicationModel.name + "...")
    uninstalled = WebSphere.AdminApp.uninstall(applicationModel.name)
    log(INFO_, uninstalled)
    appExists = checkIfAppExists(applicationModel)
    if appExists:
        fail("failed to uninstallEAR application=" + applicationModel.name)
        #endIf
    log(VERBOSE_, "UninstallEAR: DONE.")

#endDef
