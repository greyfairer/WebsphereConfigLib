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
# 3.1 (08may2007) added invocation of processScriptsFile
# 2.0 (10feb2006) initial Jython version
# 1.2 (14jan2005) fixed multiple EARs (start/stop apps on servers using $appsNodesServers)
# 1.1 (17nov2004) initial shipped version
#
from log.log import fail, INFO_, log, MAJOR_, VERBOSE_, highlight
from websphere.Definitions import Globals
from websphere.application import PreValidateApplicationsAbsent, \
    PreValidateApplicationsExist, StartApplicationOnNodesAndServers, testApplication, \
    listApplications, checkIfAppExists, StopApplicationOnNodesAndServers
from websphere.deploy.installConfigure import installAndConfigureApps
from websphere.deploy.prepareNodes import calculateAffectedNodes
from websphere.ear.ear import uninstallEAR
from websphere.getApplications import getApplications
from websphere.node.node import configSave 
from websphere.node.pairsUnique import PreValidateNodesAndServers, ValidateSynched
from websphere.server.server import syncRippleStart
from websphere.server.setJVM import getJvmID,modifyJvmAttrs
from websphere import WebSphere

def deploy (action, failOnError, distDir, wasRoot):
        log(VERBOSE_, "deploy: INPUTS: "+action+" "+distDir+" "+wasRoot)

        action = action.lower()
        if (action == "install" or action == "update"):
                installOrUpdate(action, distDir, wasRoot)
        elif (action == "confirm"):
                confirm(action, distDir, wasRoot)
        elif (action == "syncripplestart"):
                syncRippleStartDone(distDir, wasRoot)
        elif (action == "uninstall"):
                uninstall(action, distDir, wasRoot)
        else:
                msg = "ERROR: deploy: unknown action="+action+" (must be 'install' or 'update' or 'confirm' or 'syncRippleStart' or 'uninstall'"
                fail(msg)
        #endElse
#endDef
def syncRippleStartDone (distDir, wasRoot):
        applicationModels = getApplications(distDir, "*.xml.done")
        applicationModels.extend(getApplications(distDir, "*.xml.confirmed"))
        calculateAffectedNodes("update", wasRoot, applicationModels)
        PreValidateNodesAndServers(Globals.uniqueNodesContainedServers)
        syncRippleStart("update", applicationModels)
        configSave()

def installOrUpdate (action, distDir, wasRoot):

        log(VERBOSE_, "installOrUpdate: "+action+" "+distDir)
        log(VERBOSE_, "installOrUpdate: "+wasRoot+" ...")
        applicationModels = getApplications(distDir)
        ################## PRE-VALIDATE Application TARGETS+SETTINGS files ####################
        if (action == "install"):
                PreValidateApplicationsAbsent(applicationModels)
        else:
                PreValidateApplicationsExist(applicationModels)
        #endElse

        ############### CALCULATE AFFECTED NODES ####################
        calculateAffectedNodes(action, wasRoot, applicationModels)

        ################## PRE-VALIDATE NODES and SERVERS ####################
        PreValidateNodesAndServers(Globals.uniqueNodesContainedServers)

        ############### PREPARE AFFECTED NODES ####################
        #if ((action == "update")):
        #        Globals.nodesAutosyncs = saveAndDisableAutosync(action, Globals.uniqueNodesContainedServers)
        #        log(INFO_, "installOrUpdate: RESULT: nodesAutosyncs="+`Globals.nodesAutosyncs`)
        #endIf
        
        ############### INSTALL APPLICATION AND CONFIGURE ####################
        applicationModels = installAndConfigureApps(action, distDir, wasRoot, applicationModels)
        calculateAffectedNodes(action, wasRoot, applicationModels)

        for item in Globals.appsNodesServers:
            for nodeServer in item[1]:
                nodeName = nodeServer.nodeName
                serverName = nodeServer.serverName
                if len(nodeServer.jvmAttributes)>0:
                    jvmAttributes = []
                    for jvmAttribute in nodeServer.jvmAttributes:
                        log(INFO_, "jvmAttribute "+nodeName+":"+serverName+"("+jvmAttribute.name+")="+jvmAttribute.value)
                        jvmAttributes.append([jvmAttribute.name, jvmAttribute.value])
                    jvmID = getJvmID(nodeName, serverName)
                    modifyJvmAttrs(jvmID, jvmAttributes)

        configSave()

        ################## SYNC NODES (DISTRIBUTE APPS) ####################
        log(MAJOR_, "installOrUpdate: syncRippleStart of affected nodes ...")
        syncRippleStart(action, applicationModels)
        log(MAJOR_, "installOrUpdate: syncRippleStart of affected nodes DONE.")

        ################## START INSTALLED APPLICATIONS ####################
        if ((action == "install")):
                for item in Globals.appsNodesServers:
                        applicationModel = item[0]
                        StartApplicationOnNodesAndServers(applicationModel, item[1])
                #endFor
        #endIf

        ############### RESTORE AFFECTED NODES ####################
        #if ((action == "update")):
        #        log(DEBUG_, "installOrUpdate: nodesAutosyncs="+`Globals.nodesAutosyncs`)
        #        restoreAutosync(action, Globals.nodesAutosyncs)
        #endIf
        configSave()

        ################## TEST: Skipped for now, only on confirm ##
        testApplication(applicationModels)

        highlight(MAJOR_, "installOrUpdate: DONE.")
#endDef

def confirm (action, distDir, wasRoot):
        log(VERBOSE_, "confirm: "+action+" "+distDir)
        log(VERBOSE_, "confirm: "+wasRoot+" ...")

        ############### FIND APPLICATIONS ####################

        applicationModels = getApplications(distDir, "*.xml.done")
        applicationModels.extend(getApplications(distDir, "*.xml.confirmed"))
        for applicationModel in applicationModels:
            log(INFO_, "confirm: Deployment applicationModel="+`applicationModel.name`) 

        ################## PRE-VALIDATE APPLICATIONS (exists) ####################
        PreValidateApplicationsExist(applicationModels)

        ############### CALCULATE AFFECTED NODES ####################
        calculateAffectedNodes(action, wasRoot, applicationModels)

        ################## PRE-VALIDATE NODES and SERVERS ####################
        PreValidateNodesAndServers(Globals.uniqueNodesContainedServers)

        ################## TEST ####################
        testApplication(applicationModels)
        
        nodeSyncStatus={}
        for nodeContainedServers in Globals.uniqueNodesContainedServers:
            node = nodeContainedServers[0] 
            if not node in nodeSyncStatus.keys():
                nodeSync = WebSphere.AdminControl.completeObjectName("type=NodeSync,node=%s,*"%node)
                nodeSyncStatus[node]=WebSphere.AdminControl.invoke(nodeSync, "isNodeSynchronized")
        print "NODE SYNC STATUS: %s" % nodeSyncStatus

        highlight(MAJOR_, "confirm: DONE.")
#endDef

def uninstall (action, distDir, wasRoot):
        log(VERBOSE_, "uninstall: "+action+" "+distDir)
        log(VERBOSE_, "uninstall: "+wasRoot+" ...")

        ############### FIND APPLICATIONS ####################
        applicationModels = getApplications(distDir)
        for applicationModel in applicationModels:
            log(INFO_, "uninstall: Deployment applicationModel="+`applicationModel.name`) 

        ################## PRE-VALIDATE APPLICATIONS (exists) ####################
        PreValidateApplicationsExist(applicationModels)

        ############### CALCULATE AFFECTED NODES ####################
        calculateAffectedNodes(action, wasRoot, applicationModels)

        ################## PRE-VALIDATE NODES and SERVERS ####################
        PreValidateNodesAndServers(Globals.uniqueNodesContainedServers)
        ValidateSynched(Globals.uniqueNodesContainedServers)

        listApplications()

        #endFor
        for item in Globals.appsNodesServers:
                applicationModel = item[0]
                appExists = checkIfAppExists(applicationModel)
                if (appExists):
                        StopApplicationOnNodesAndServers(applicationModel, item[1])
                        uninstallEAR(applicationModel)
                #endIf
        #endFor
 
        listApplications()
        configSave()
        for applicationModel in applicationModels:
            log(INFO_, "DONE: uninstall application="+`applicationModel.name`) 
#endDef

