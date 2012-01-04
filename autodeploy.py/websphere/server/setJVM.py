#
# Author: Barry Searle
#
# (C) Copyright IBM Corp. 2006,2007 - All Rights Reserved.
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
# 3.1 (08may2007) initial shipped version
#
from websphere import WebSphere
from log.log import log, INFO_

def setJvmHeapSize ( nodeName, serverName, initialHeap, maxHeap ):
        aJvmID = getJvmID(nodeName, serverName)
        aJvmAttrs = [["initialHeapSize", initialHeap], ["maximumHeapSize", maxHeap]]
        modifyJvmAttrs(aJvmID, aJvmAttrs)
#endDef

################### Utility methods ###########################
def getJvmID ( nodeName, serverName ):
        aServerID = WebSphere.AdminConfig.getid("/Node:"+nodeName+"/Server:"+serverName+"/" )
        aJvmID = WebSphere.AdminConfig.list("JavaVirtualMachine", aServerID )
        return aJvmID
#endDef


def modifyJvmAttrs ( aJvmID, ajvmAttrs ):
        WebSphere.AdminConfig.modify(aJvmID, ajvmAttrs )
        aJvmSettings = WebSphere.AdminConfig.show(aJvmID )
        log(INFO_, "\nsetJVM changedJvmSettings: \n"+aJvmSettings )
#endDef
