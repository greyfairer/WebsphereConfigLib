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
# 1.1 (17nov2004) initial shipped version
#
from websphere.Definitions import Globals
from log.log import fail, INFO_, log, MAJOR_, VERBOSE_, ERROR_, DEBUG_, WARNING_
from websphere import WebSphere
from websphere.node.node import execScript
from java.lang import Thread
import sys

def syncRippleStart(action, applicationModels):
    for nodeContainedServers in Globals.uniqueNodesContainedServers:
        nodeName = nodeContainedServers[0]
        syncNDNode(nodeName)
        log(MAJOR_, "syncRippleStart synced: " + nodeName)
    for applicationModel in applicationModels:
        execScript(applicationModel, "afterSync")
    for clusterName in Globals.clusters.keys():
        cluster = WebSphere.AdminControl.completeObjectName('type=Cluster,name=%s,*' % clusterName)
        clusterTarget = Globals.clusters[clusterName]
        if not len(clusterTarget.inactiveServers):
            WebSphere.AdminControl.invoke(cluster, 'rippleStart')
            log(MAJOR_, "syncRippleStart: rippleStart " + clusterName + " invoked")
            sleepDelay(3)
    for nodeServerPair in Globals.unclusteredNodeServerPairs:
        stopNDServer(nodeServerPair[0], nodeServerPair[1])
        startNDServer(nodeServerPair[0], nodeServerPair[1])
    checkClustersStarted(Globals.clusters)
    for applicationModel in applicationModels:
        execScript(applicationModel, "afterRippleStart")


def stopSyncStart(action, nodeName, containedServerNames):
    log(MAJOR_, "stopSyncStart: nodename=" + nodeName + " containedServernames=" + `containedServerNames` + " ...")
    syncNDNode(nodeName)
    if action == "update":
        for serverName in containedServerNames:
            stopNDServer(nodeName, serverName)
            startNDServer(nodeName, serverName)
            #endFor
    if action == "update":
        log(VERBOSE_,
            "stopSyncStart: FUTURE: plugin-cfg.xml RE-ACTIVATE node=" + nodeName + " servers=" + `containedServerNames`)
        #endIf
    log(MAJOR_, "stopSyncStart: DONE. (nodeName=" + nodeName + ")")

#endDef

def syncNDNode(nodeName):
    EarExpandDelay = 10
    log(MAJOR_, "syncNDNode: ReSync of ND Node=" + nodeName + " (actual application distribution to Server(s) ) ...")
    ndSync = WebSphere.AdminControl.completeObjectName("type=NodeSync,node=" + nodeName + ",*")
    if ndSync == "":
        fail("cannot syncNDNode (stopped?) nodeName=" + nodeName)
        #endIf
    sync = WebSphere.AdminControl.invoke(ndSync, "sync")
    log(INFO_, "syncNDNode: " + nodeName + " invoked sync=" + sync + "  DONE.")
    log(VERBOSE_,
        "syncNDNode: FUTURE: check for nodeSync EAR expansion complete (for now just delay " + `EarExpandDelay` + " secs)")
    sleepDelay(EarExpandDelay)

#endDef

def startNDServer(nodeName, serverName):
    log(MAJOR_, "startNDServer: nodeName=" + nodeName + " serverName=" + serverName + " ...")
    log(VERBOSE_, "startNDServer: FUTURE: replace wsAdmin.startserver with NodeAgent.launchProcess+Wait")
    started = ""
    try:
        _excp_ = 0
        started = WebSphere.AdminControl.startServer(serverName, nodeName, 100000)
    except:
        _type_, _value_, _tbck_ = sys.exc_info()
        _excp_ = 1
        #endTry
    temp = _excp_
    log(DEBUG_, "startNDServer: errorcode=" + `temp` + " started=" + started + " ...")
    retries = 0
    while (temp > 0) and (retries < 5):
        retries = retries + 1
        log(ERROR_,
            "startNDServer: start failed exception=" + `temp` + " for " + nodeName + " " + serverName + ", retries=" + `retries` + " ...")
        try:
            _excp_ = 0
            started = WebSphere.AdminControl.startServer(serverName, nodeName, 100000)
        except:
            _type_, _value_, _tbck_ = sys.exc_info()
            _excp_ = 1
            #endTry
        temp = _excp_
        log(DEBUG_, "startNDServer: temp=" + temp + " started=" + started + " ...")
        #endWhile
    checkServerStarted(nodeName, serverName)
    log(VERBOSE_, "startNDServer: DONE.")

#endDef

def checkClustersStarted(clusters):
    unstartedClusters = {}
    result = {}
    for clusterName in clusters.keys():
        if not len(clusters[clusterName].inactiveServers):
            log(VERBOSE_, "checkClusterStarted: clusterName=" + clusterName)
            clusterId = ""
            retryConnect = 0
            while len(clusterId) == 0 and retryConnect < 5:
                try:
                    clusterId = WebSphere.AdminControl.completeObjectName('type=Cluster,name=%s,*' % clusterName)
                except:
                    _type_, _value_, _tbck_ = sys.exc_info()
                    log(WARNING_,
                        "checkClusterStarted WebSphere.AdminControl exception=" + `_type_` + " clusterName=" + clusterName)
                if not len(clusterId):
                    log(VERBOSE_, "checkClusterStarted: cluster not yet started, retries=" + `retryConnect` + " ...")
                    sleepDelay(6)
                    retryConnect = retryConnect + 1
                    #endIf
                #endWhile
            if retryConnect > 0:
                log(INFO_, "checkClusterStarted: " + clusterName + " had slow start, status retries=" + `retries`)
                #endIf
            if clusterId == "":
                log(ERROR_, "checkClusterStarted: " + clusterName + " not started yet.")
            else:
                unstartedClusters[clusterName] = clusterId
                #endIf
    retries = 0
    while len(unstartedClusters) > 0 and retries <= 25:
        for clusterName in unstartedClusters.keys():
            clusterId = unstartedClusters[clusterName]
            state = WebSphere.AdminControl.getAttribute(clusterId, "state")
            result[clusterName] = state
            if state != "websphere.cluster.running":
                log(INFO_, "waiting for cluster: " + clusterName + " state=" + state)
            else:
                log(INFO_, "cluster is running: " + clusterName + " state=" + state)
                del unstartedClusters[clusterName]
            if len(unstartedClusters) > 0:
                sleepDelay(5 + 2 * retries)
                retries += 1
    return result

#endDef

def checkServerStarted(nodeName, serverName):
    log(VERBOSE_, "checkServerStarted: nodeName=" + nodeName + " serverName=" + serverName + " ...")
    serverID = ""
    retries = 0
    try:
        serverID = WebSphere.AdminControl.completeObjectName(
            "node=" + nodeName + ",name=" + serverName + ",type=Server,*")
    except:
        _type_, _value_, _tbck_ = sys.exc_info()
        log(WARNING_, "checkServerStarted WebSphere.AdminControl exception=" + `_type_` + " serverID=" + serverID)
    while len(serverID) == 0 and retries <= 15:
        log(VERBOSE_, "checkServerStarted: server not yet started, retries=" + `retries` + " ...")
        sleepDelay(5 + 2 * retries)
        retries = retries + 1
        try:
            serverID = WebSphere.AdminControl.completeObjectName(
                "node=" + nodeName + ",name=" + serverName + ",type=Server,*")
        except:
            _type_, _value_, _tbck_ = sys.exc_info()
            log(WARNING_, "checkServerStarted WebSphere.AdminControl exception=" + `_type_` + " serverID=" + serverID)
            #endIf
        #endWhile
    if retries > 0:
        log(INFO_,
            "checkServerStarted: " + nodeName + " " + serverName + " had slow start, status retries=" + `retries`)
        #endIf
    if serverID == "":
        log(ERROR_, "checkServerStarted: " + nodeName + " " + serverName + " server FAILED TO START.")
        return
        #endIf
    state = WebSphere.AdminControl.getAttribute(serverID, "state")
    state = state.upper()
    if state == "STARTED":
        log(INFO_, "checkServerStarted: " + nodeName + " " + serverName + " state=" + state)
    else:
        log(ERROR_, "checkServerStarted: " + nodeName + " " + serverName + " INCORRECT state=" + state)
        #endElse
    log(VERBOSE_, "checkServerStarted: DONE.")

#endDef

def stopNDServer(nodeName, serverName):
    log(DEBUG_, "stopNDServer: nodeName=" + nodeName + " serverName=" + serverName)
    serverID = WebSphere.AdminControl.completeObjectName("node=" + nodeName + ",name=" + serverName + ",type=Server,*")
    if not len(serverID):
        msg = "stopNDServer: cannot access node=" + nodeName + " server=" + serverName + " state=STOPPED?"
        log(WARNING_, msg)
        return
        #endIf
    state = WebSphere.AdminControl.getAttribute(serverID, "state")
    state = state.upper()
    log(INFO_, "stopNDServer: nodeName=" + nodeName + " serverName=" + serverName + " state=" + state)
    if state == "STOPPED":
        log(INFO_, nodeName + " " + serverName + " state=STOPPED")
    else:
        stopped = WebSphere.AdminControl.stopServer(serverName, nodeName, "immediate")
        if len(stopped):
            log(VERBOSE_, "stopNDServer: stopServer response=" + stopped)
            #endIf
        checkServerStopped(nodeName, serverName)
        #endElse
    log(VERBOSE_, "stopNDServer: DONE.")

#endDef

def checkServerStopped(nodeName, serverName):
    log(DEBUG_, "checkServerStopped: nodeName=" + nodeName + " serverName=" + serverName)
    desiredState = "STOPPED"
    serverID = ""
    try:
        serverID = WebSphere.AdminControl.completeObjectName(
            "node=" + nodeName + ",name=" + serverName + ",type=Server,*")
    except:
        _type_, _value_, _tbck_ = sys.exc_info()
        log(WARNING_, "checkServerStopped: exception=" + `_type_` + " trying to access " + nodeName + " " + serverName)
        #endIf
    if not len(serverID):
        log(VERBOSE_, "checkServerStopped: cannot access node=" + nodeName + " server=" + serverName + " (STOPPED?)")
        actualState = desiredState
    else:
        actualState = WebSphere.AdminControl.getAttribute(serverID, "state")
        #endElse
    actualState = actualState.upper()
    log(VERBOSE_,
        "checkServerStopped: " + nodeName + " " + serverName + " actualState=" + actualState + " desiredState=" + desiredState)
    if actualState != desiredState:
        msg = "ERROR: checkServerStopped: " + nodeName + " " + serverName + " actualState=" + actualState + " instead of desiredState=" + desiredState
        fail(msg)
        #endIf

#endDef

def sleepDelay(secs):
    try:
        Thread.currentThread().sleep(secs * 1000)
    except:
        _type_, _value_, _tbck_ = sys.exc_info()
        log(VERBOSE_, "sleep interrupted " + `_value_`)
        #endTry

#endDef

