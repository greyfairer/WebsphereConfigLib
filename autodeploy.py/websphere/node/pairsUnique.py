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
# 2.0 (10feb2006) initial Jython version, corrected creation of [nodeContainedServers]
# 1.3 (22apr2005) determineUniqueNodesContainedServers uses "lreplace" instead of code loop
# 1.1 (17nov2004) initial shipped version
#
from websphere.Definitions import false, true, wsadminToList, Globals
from log.log import fail, INFO_, log, MAJOR_, VERBOSE_, ERROR_, DEBUG_,\
    highlight, WARNING_
from websphere import WebSphere
import sys
from websphere.applicationModel import ServerApplicationTarget


def PreValidateNodesAndServers ( uniqueNodesContainedServers ):
        if (len(uniqueNodesContainedServers) == 0):
                log(WARNING_, "PreValidateNodesAndServers: No nodes/servers/clusters specified" )
        #endIf
        for nodeContainedServers in uniqueNodesContainedServers:
                nodeName = nodeContainedServers[0]
                PreValidateNode(nodeName )
                containedServers = nodeContainedServers[1]
                for serverName in containedServers:
                        PreValidateServer(nodeName, serverName )
                #endFor
        #endFor
#endDef

def ValidateSynched ( uniqueNodesContainedServers ):
    for nodeContainedServers in uniqueNodesContainedServers:
        nodeName = nodeContainedServers[0]
        ndSync = WebSphere.AdminControl.completeObjectName("type=NodeSync,node="+nodeName+",*" )
        if (( ndSync == "") ):
            log(WARNING_, "ValidateSynched: failed for nodeName="+nodeName+" (could not access "+nodeName+")" )
        else:
            status = AdminControl.invoke(ndSync, "isNodeSynchronized")
            if(status != true):
                log(WARNING_, "ValidateSynched: failed for nodeName="+nodeName+" (isNodeSynchronized returned "+status+")" )
            else:
                log(INFO_, "Node is Synchronized:"+nodeName )
    #endFor
#endDef


def PreValidateNode ( nodeName ):


        nodeID = WebSphere.AdminConfig.getid("/Node:"+nodeName+"/" )
        if (len(nodeID) == 0):
                msg = "PreValidateNode: failed for node="+nodeName+" (invalid nodeName)"
                log(WARNING_, msg )
        #endIf
        ndSync = WebSphere.AdminControl.completeObjectName("type=NodeSync,node="+nodeName+",*" )
        if (( ndSync == "") ):
                log(WARNING_, "PreValidateNode: failed for nodeName="+nodeName+" (could not access "+nodeName+")" )
        #endIf
        nodeAgent = WebSphere.AdminConfig.getid("/Node:"+nodeName+"/Server:nodeagent/" )
        if (( nodeAgent == "") ):
                log(WARNING_, "PreValidateNode: failed for nodeName="+nodeName+" (nodeAgent STOPPED)" )
        else:
                log(VERBOSE_, "PreValidateNode OK nodeName="+nodeName )
        #endElse
#endDef

def PreValidateServer ( nodeName, serverName ):
    if not [nodeName, serverName] in Globals.inactiveServers:
        serverID = WebSphere.AdminConfig.getid("/Node:"+nodeName+"/Server:"+serverName+"/" )
        if (len(serverID) == 0):
                msg = "PreValidateServer: failed for server="+serverName+" node="+nodeName+" (invalid serverName)"
                log(WARNING_, msg )
        #endIf
        serverID = WebSphere.AdminControl.completeObjectName("node="+nodeName+",name="+serverName+",type=Server,*" )
        if (len(serverID) == 0):
                msg = "PreValidateServer: cannot access node="+nodeName+" server="+serverName+" (server STOPPED)"
                log(WARNING_, msg )
                return 0
        else:
                log(VERBOSE_, "PreValidateSrvr OK serverName="+serverName+" nodeName="+nodeName )
                return 1
        #endElse
    else:
    	return 0
#endDef

def PreValidateCluster ( cluster):
        clusterID = WebSphere.AdminConfig.getid("/ServerCluster:"+cluster.clusterName+"/" )
        if (len(clusterID) == 0):
                msg = "PreValidateCluster: failed for cluster.clusterName="+cluster.clusterName+" (invalid cluster.clusterName)"
                log(WARNING_, msg )
        #endIf
        clusterID = WebSphere.AdminControl.completeObjectName("name="+cluster.clusterName+",*" )
        if (len(clusterID) == 0):
                msg = "PreValidateCluster: cannot access cluster.clusterName="+cluster.clusterName+" (cluster STOPPED)"
                log(WARNING_, msg )
        else:
                state = WebSphere.AdminControl.getAttribute(clusterID, "state" )
                log(VERBOSE_, "PreValidateCluster OK cluster.clusterName="+cluster.clusterName+" state="+state )
        #endElse
#endDef

def getNodeServerPairs ( clusters ):
        nodeServerPairs = []
        for cluster in clusters:
                cluster_id = WebSphere.AdminConfig.getid("/ServerCluster:"+cluster.clusterName+"/" )
                members = WebSphere.AdminConfig.list("ClusterMember", cluster_id )
                members = wsadminToList(members)
                for member in members:
                        node = WebSphere.AdminConfig.showAttribute(member, "nodeName" )
                        server = WebSphere.AdminConfig.showAttribute(member, "memberName" )
                        log(DEBUG_, "getNodeServerPairs: cluster="+cluster.clusterName+" contains node="+node+" server="+server )
                        nodeServerPair = ServerApplicationTarget(node, server, cluster.tests, cluster.jvmAttributes)
                        nodeServerPairs.append(nodeServerPair)
                #endFor
        #endFor
        log(DEBUG_, "getNodeServerPairs: returning nodeServerPairs="+`nodeServerPairs` )
        return nodeServerPairs
#endDef

def getPartialClusterNodeServerPairs( clusters ):
        nodeServerPairs = []
        for cluster in clusters:
            if len(cluster.inactiveServers) > 0:
                cluster_id = WebSphere.AdminConfig.getid("/ServerCluster:"+cluster.clusterName+"/" )
                members = WebSphere.AdminConfig.list("ClusterMember", cluster_id )
                members = wsadminToList(members)
                for member in members:
                        node = WebSphere.AdminConfig.showAttribute(member, "nodeName" )
                        server = WebSphere.AdminConfig.showAttribute(member, "memberName" )
                        log(DEBUG_, "getNodeServerPairs: cluster="+cluster.clusterName+" contains node="+node+" server="+server )
                        inactive = 0
                        for inactiveServer in cluster.inactiveServers:
                            if (node, server) == (inactiveServer.nodeName, inactiveServer.serverName):
                                inactive = 1
                        if inactive == 0:
                            nodeServerPair = ServerApplicationTarget(node, server, cluster.tests, cluster.jvmAttributes)
                            nodeServerPairs.append(nodeServerPair)
                #endFor
        #endFor
        log(DEBUG_, "getNodeServerPairs: returning nodeServerPairs="+`nodeServerPairs` )
        return nodeServerPairs
#endDef

def getInactiveServers ( cluster ):
        inactiveServers = []
        cluster_id = WebSphere.AdminConfig.getid("/ServerCluster:"+cluster.clusterName+"/" )
        members = WebSphere.AdminConfig.list("ClusterMember", cluster_id )
        members = wsadminToList(members)
        for member in members:
                nodeName = WebSphere.AdminConfig.showAttribute(member, "nodeName" )
                serverName = WebSphere.AdminConfig.showAttribute(member, "memberName" )
                log(DEBUG_, "getNodeServerPairs: cluster="+cluster.clusterName+" contains node="+nodeName+" server="+serverName )
                if not PreValidateServer(nodeName, serverName):
                    nodeServerPair = ServerApplicationTarget(nodeName, serverName, cluster.tests, cluster.jvmAttributes)
                    inactiveServers.append(nodeServerPair)                            
        #endFor
        return inactiveServers
#endDef

def determineUniqueNodesContainedServers ( nodeServerPairs ):


        log(DEBUG_, "determineUniqueNodesContainedServers: nodeServerPairs="+`nodeServerPairs` )
        nodesContainedServers = []
        for nodeServer in nodeServerPairs:
                nodeName = nodeServer.nodeName
                serverName = nodeServer.serverName
                nodeIndex = 0
                for uniquenodeContainedServers in nodesContainedServers:
                        uniquenode = uniquenodeContainedServers[0]
                        if (uniquenode == nodeName):
                                containedServers = uniquenodeContainedServers[1]
                                for server in containedServers:
                                        if (server == serverName):
                                                serverName = ""
                                                break
                                        #endIf
                                #endFor
                                if (serverName != ""):
                                        containedServers.append(serverName)
                                        nodeContainedServers = [nodeName, containedServers]
                                        log(DEBUG_, "determineUniqueNodesContainedServers: Replacing node="+nodeName+" with NEW containedServers="+`containedServers` )
                                        del nodesContainedServers[nodeIndex]
                                        nodesContainedServers.insert( nodeIndex, nodeContainedServers )
                                        log(DEBUG_, "determineUniqueNodesContainedServers: New nodesContainedServers="+`nodesContainedServers` )
                                #endIf
                                nodeName = ""
                                break
                        #endIf
                        nodeIndex = nodeIndex+1
                #endFor
                if (nodeName != "" and serverName != ""):
                        nodeContainedServers = [nodeName, [serverName]]
                        log(DEBUG_, "################## determineUniqueNodesContainedServers: new node="+nodeName+" new server="+serverName )
                        nodesContainedServers.append(nodeContainedServers)
                #endIf
                log(DEBUG_,"nodesContainedServers="+`nodesContainedServers`)
        #endFor
        log(DEBUG_, "determineUniqueNodesContainedServers: returning LIST nodesContainedServers="+`nodesContainedServers` )
        return nodesContainedServers
#endDef
