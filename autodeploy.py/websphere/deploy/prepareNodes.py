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
# 2.0 (10feb2006) initial Jython version
# 1.2 (14jan2005) fixed multiple EARs (start/stop apps on servers using $appsNodesServers per app)
# 1.1 (17nov2004) initial shipped version
#
from websphere.Definitions import wsadminToList, Globals
from log.log import fail, INFO_, log, MAJOR_, VERBOSE_,  DEBUG_, \
    highlight
from websphere import WebSphere
from websphere.node.pairsUnique import PreValidateCluster, getNodeServerPairs, \
    determineUniqueNodesContainedServers, getPartialClusterNodeServerPairs, getInactiveServers
from websphere.applicationModel import ClusterApplicationTarget, ServerApplicationTarget, ApplicationTarget
import re

def getServerType(nodeName, serverName):
    server = WebSphere.AdminConfig.getid("/Node:%s/Server:%s/"%(nodeName, serverName))
    return WebSphere.AdminConfig.showAttribute(server, "serverType")

def addExistingTargets(applicationName, applicationTarget, applicationClusters, applicationServers):
    deployment = WebSphere.AdminConfig.getid("/Deployment:"+applicationName+"/")
    deployedObject = WebSphere.AdminConfig.showAttribute(deployment, "deployedObject")
    modules = wsadminToList(WebSphere.AdminConfig.showAttribute(deployedObject, "modules"))
    clusters = []
    serverNodes = []
    for module in modules:
        targetMappings = wsadminToList(WebSphere.AdminConfig.showAttribute(module, "targetMappings"))
        for targetMapping in targetMappings:
            target = WebSphere.AdminConfig.showAttribute(targetMapping, "target")
            if re.search("#ClusteredTarget", target):
                clusterName= WebSphere.AdminConfig.showAttribute(target, "name")
                if clusterName not in clusters:
                    log(INFO_, "existing clusterName: "+clusterName)
                    clusters.append(clusterName)
            elif re.search("#ServerTarget", target):
                serverName= WebSphere.AdminConfig.showAttribute(target, "name")
                nodeName= WebSphere.AdminConfig.showAttribute(target, "nodeName")
                if [nodeName, serverName] not in serverNodes:
                    log(INFO_, "existing node server: %s:%s"%(nodeName, serverName))
                    serverNodes.append([nodeName, serverName])
    for serverNode in serverNodes:
        if getServerType(serverNode[0], serverNode[1])=="APPLICATION_SERVER":
            applicationServers.append(ServerApplicationTarget(serverNode[0], serverNode[1], applicationTarget.tests, applicationTarget.jvmAttributes))
    for clusterName in clusters:
        clusterTarget = ClusterApplicationTarget(clusterName, applicationTarget.tests, applicationTarget.jvmAttributes)
        clusterTarget.inactiveServers = getInactiveServers(clusterTarget)
        applicationClusters.append(clusterTarget)

def addUniqueClusters(clusterTargets):
    
    for clusterTarget in clusterTargets:
        if not clusterTarget.clusterName in Globals.clusters.keys():
            Globals.clusters[clusterTarget.clusterName]=clusterTarget

    
def calculateAffectedNodes (action, wasRoot, applicationModels):
        Globals.appsNodesServers = []
        Globals.nodeServerPairs = []
        Globals.uniqueNodesContainedServers = []
        Globals.nodesAutosyncs = []
        Globals.unclusteredNodeServerPairs = []
        Globals.clusters = {}
        Globals.inactiveServers = []

        ############### FIND NODES/SERVERS ####################
        if (len(applicationModels) == 0):
                fail("calculateAffectedNodes: No applicationModels in distDir ")
        #endIf
        for applicationModel in applicationModels:

                ################ READ TARGETS ##############
                tmpNodeServerPairs = []
                
                applicationClusters = []
                applicationClusters.extend(applicationModel.clusters)
                applicationServers = []
                applicationServers.extend(applicationModel.servers)
                for module in applicationModel.modules:
                    for target in module.targets:
                        if target.targetType()==ApplicationTarget.CLUSTER:
                            applicationClusters.append(target)
                        elif target.targetType()==ApplicationTarget.SERVER:
                            applicationServers.append(target)
                
                if action == "update":
                    for target in applicationModel.targets:
                        addExistingTargets(applicationModel.name, target, applicationClusters, applicationServers)
                    
                    

                ################## PRE-VALIDATE CLUSTERS ####################
                for cluster in applicationClusters:
                    for server in cluster.inactiveServers:
                        inactiveServerPair = [server.nodeName, server.serverName]  
                        if inactiveServerPair not in Globals.inactiveServers:
                            Globals.inactiveServers.append(inactiveServerPair)                  
                    PreValidateCluster(cluster)
                #endFor

                ################## APPEND TOTAL NODES/SERVERS/TESTS ############
                for server in applicationServers:
                        if getServerType(server.nodeName, server.serverName)=="APPLICATION_SERVER":
                            Globals.nodeServerPairs.append(server)
                            if not [server.nodeName, server.serverName] in Globals.unclusteredNodeServerPairs:
                                Globals.unclusteredNodeServerPairs.append([server.nodeName, server.serverName])
                            tmpNodeServerPairs.append(server)
                #endFor
                addUniqueClusters(applicationClusters)
                clusterNodeServerPairs = getNodeServerPairs(applicationClusters)
                log(DEBUG_, "clusterNodeServerPairs="+`clusterNodeServerPairs`)
                for clusterNodeServerPair in clusterNodeServerPairs:
                        Globals.nodeServerPairs.append(clusterNodeServerPair)
                        tmpNodeServerPairs.append(clusterNodeServerPair)
                #endFor
                partialClusterNodeServerPairs = getPartialClusterNodeServerPairs(applicationClusters)
                for server in partialClusterNodeServerPairs:
                    if not [server.nodeName, server.serverName] in Globals.unclusteredNodeServerPairs:
                        Globals.unclusteredNodeServerPairs.append([server.nodeName, server.serverName])

                Globals.appsNodesServers.append([applicationModel, tmpNodeServerPairs])
        #endFor
        log(VERBOSE_, "calculateAffectedNodes: RESULT: appsNodesServers="+`Globals.appsNodesServers`)
        log(VERBOSE_, "calculateAffectedNodes: RESULT: nodeServerPairs="+`Globals.nodeServerPairs`)

        ################## UNIQUE NODES (AND THEIR UNIQUE SERVERS) ############
        if (len(Globals.nodeServerPairs) == 0):
                fail("calculateAffectedNodes: No node/server/cluster (Targets) specified")
        #endIf
        Globals.uniqueNodesContainedServers = determineUniqueNodesContainedServers(Globals.nodeServerPairs)
        log(INFO_, "calculateAffectedNodes: RESULT: Globals.uniqueNodesContainedServers="+`Globals.uniqueNodesContainedServers`)
        if len(Globals.inactiveServers) > 0:
            log(INFO_, "calculateAffectedNodes: RESULT: Globals.inactiveServers="+`Globals.inactiveServers`)

        highlight(MAJOR_, "calculateAffectedNodes DONE.")
#endDef

