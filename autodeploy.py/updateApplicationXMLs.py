from websphere.Definitions import false, true, wsadminToList, Globals
from log.log import fail, INFO_, log, MAJOR_, VERBOSE_, ERROR_, DEBUG_, WARNING_,\
    highlight
from websphere import WebSphere
from websphere.applicationModel import parseApplication, updateApplicationModel, ServerApplicationTarget, ClusterApplicationTarget, ApplicationTargetTest
from websphere.attrib.showSet import showAttribute
from websphere.node.pairsUnique import getInactiveServers 
import sys
import os
import glob
import re
import xml

nodeServerRegexp = re.compile("WebSphere:cell=.*,node=(.*),server=(.*)")
clusterRegexp = re.compile("WebSphere:cell=.*,cluster=(.*)")
nodeSyncStatus={}

def getDefaultPort(node, server):
    serverPortRegex = re.compile("\[WC_defaulthost \[ \[port (.*)\] \[node (.*)\] \[host (.*)\] \[server (.*)\] \]\]")
    serverPortRegex2 = re.compile("\[WEBSERVER_ADDRESS \[ \[port (.*)\] \[node (.*)\] \[host (.*)\] \[server (.*)\] \]\]")
    for serverPort in AdminTask.listServerPorts(server, '-nodeName %s' % node ).splitlines():
        serverPortMatch=serverPortRegex.match(serverPort)
        if serverPortMatch:
            return serverPortMatch.group(1)
        else:
            serverPortMatch2 = serverPortRegex2.match(serverPort)
            if serverPortMatch2:
                return serverPortMatch2.group(1)
    return "00"
            
        
        

def getModuleConfigs(application):
    moduleConfigMap={}
    lines = WebSphere.AdminApp.listModules(application.name, "-server")
    for moduleLine in lines.split("\n"):
        moduleLine = moduleLine.rstrip() #removes any Windows "\r"
        moduleLineItems = moduleLine.split("#")
        moduleName = moduleLineItems[1].split("+")[0]
        moduleTargets= []
        for moduleTargetId in moduleLineItems[2].split("+"):
            clusterMatch = clusterRegexp.match(moduleTargetId)
            if clusterMatch:
                clusterTarget = ClusterApplicationTarget(clusterMatch.group(1))
                clusterTarget.inactiveServers = getInactiveServers(clusterTarget)
                clusterTarget.tests=[]
                cluster_id = WebSphere.AdminConfig.getid("/ServerCluster:"+clusterTarget.clusterName+"/" )
                members = WebSphere.AdminConfig.list("ClusterMember", cluster_id )
                members = wsadminToList(members)
                for member in members:
                        node = WebSphere.AdminConfig.showAttribute(member, "nodeName" )
                        server = WebSphere.AdminConfig.showAttribute(member, "memberName" )
                        log(DEBUG_, "getNodeServerPairs: cluster="+clusterTarget.clusterName+" contains node="+node+" server="+server )
                        inactive = 0
                        for inactiveServer in clusterTarget.inactiveServers:
                            if (node, server) == (inactiveServer.nodeName, inactiveServer.serverName):
                                inactive = 1
                        if inactive == 0:
                            nodeObj=WebSphere.AdminConfig.getid('/Cell:/Node:%s/'%node)
                            nodeHostName=WebSphere.AdminConfig.showAttribute(nodeObj, 'hostName')
                            defaultPort=getDefaultPort(node,server)
                            url = 'http://%s:%s/'%(nodeHostName, defaultPort)
                            clusterTarget.tests.append(ApplicationTargetTest(url,application.version))
                            if not node in nodeSyncStatus.keys():
                                nodeSync = WebSphere.AdminControl.completeObjectName("type=NodeSync,node=%s,*"%node)
                                nodeSyncStatus[node]=WebSphere.AdminControl.invoke(nodeSync, "isNodeSynchronized")
                moduleTargets.append(clusterTarget)
            else:
                nodeServerMatch = nodeServerRegexp.match(moduleTargetId)
                if nodeServerMatch:
                    serverTarget=ServerApplicationTarget(nodeServerMatch.group(1), nodeServerMatch.group(2))
                    #nodeObj=WebSphere.AdminConfig.getid('/Cell:/Node:%s/'%serverTarget.nodeName)
                    #nodeHostName=WebSphere.AdminConfig.showAttribute(nodeObj, 'hostName')
                    defaultPort=getDefaultPort(serverTarget.nodeName,serverTarget.serverName)
                    if defaultPort.endswith("43"):
                        url = 'https://%s:%s/'%(serverTarget.nodeName, defaultPort)
                    else:
                        url = 'http://%s:%s/'%(serverTarget.nodeName, defaultPort)
                    
                    serverTarget.tests = [ApplicationTargetTest(url,application.version)]
                    moduleTargets.append(serverTarget)
        attributes=[]
        for attributeKey in ["classloaderMode","startingWeight","WebModuleConfig.sessionManagement.defaultCookieSettings.name","WebModuleConfig.sessionManagement.defaultCookieSettings.path","WebModuleConfig.sessionManagement.enable"]:
            attr = showAttribute(moduleName, "Module", attributeKey, application.name )
            if attr:
                attributes.append((attributeKey,attr))
        moduleConfigMap[moduleName]={"targets": moduleTargets, "attributes": attributes}
        
    applicationAttributes=[]
    for attributeKey in ["classloader.mode", "warClassLoaderPolicy","ApplicationConfig.sessionManagement.defaultCookieSettings.name","ApplicationConfig.sessionManagement.defaultCookieSettings.path","ApplicationConfig.sessionManagement.enable"]:
        attr = showAttribute(application.name , "Application", attributeKey, application.name )
        if attr:
            applicationAttributes.append((attributeKey,attr))
    return moduleConfigMap, applicationAttributes 

def updateApplicationDom(dom):
    cellName = WebSphere.AdminControl.getCell()
    application = parseApplication(dom)
    comment = ""
    moduleTargets={}
    applicationAttributes = []
    error = 0
    if not checkIfAppNameExists(application.name):
        comment = "Application does not exist on %s" % (cellName)
        error = 1
    else:
        comment = "Validated on %s" % (cellName)
        moduleTargets, applicationAttributes = getModuleConfigs(application)
        
    error += updateApplicationModel(dom, moduleTargets, applicationAttributes, comment)
    return error

def listApplications (  ):
    log(INFO_, "ListApplications:" )
    apps = WebSphere.AdminApp.list( )
    apps = wsadminToList(apps) # running on windows, target is linux (different SEPARATOR)
    for app in apps:
            log(INFO_, "  "+app )
    #endFor
    log(VERBOSE_, "ListApplications: DONE." )
#endDef

def checkIfAppNameExists ( appName ):
        appExists = true
        application = WebSphere.AdminConfig.getid("/Deployment:"+appName+"/" )
        log(DEBUG_, "checkIfAppExists applicationModel="+appName+" installedAppID="+application )
        if (len(application) == 0):
                appExists = false
                log(VERBOSE_, "checkIfAppExists: FALSE for applicationModel="+appName )
        else:
                log(VERBOSE_, "checkIfAppExists: TRUE for applicationModel="+appName )
        #endElse
        return appExists    
#endDef

def updateApplicationXMLs(distDir):
    if os.path.isdir(distDir) == 0:
            msg = "readDistributionDirectory: ERROR: is not a directory, distDir="+distDir
            fail(msg)
    if os.path.exists(distDir) == 0:
        msg = "readDistributionDirectory: ERROR: does not exist, distDir="+distDir
        fail(msg)
    files = glob.glob(distDir+"/*.xml.in")
    xml.dom.javadom.Node.namespaceURI=None
    impl = xml.dom.javadom.XercesDomImplementation()
    for file in files:
        dom = impl.buildDocumentFile(file)
        error = updateApplicationDom(dom)
        applicationModel=parseApplication(dom)
        file=file[0:len(file)-3]
        stream = open(file, "wt")
        xml.dom.ext.PrettyPrint(dom, stream)
        stream.close()
        if error > 0:
            os.rename(file, file+".err")
            print "GENERATE ERR "+file+".err for "+applicationModel.name+" at "+applicationModel.file
        else:
            print "GENERATE OK "+file+" for "+applicationModel.name+" at "+applicationModel.file
    print "NODE SYNC STATUS: %s" % nodeSyncStatus
            


distDir = ""
if len(sys.argv) > 0:
        param1 = sys.argv[0]
        param1 = param1[len(param1)-3:].lower()
        if(param1==".py" or param1==".jy"):
            if len(sys.argv) > 1:
                distDir=sys.argv[1]
        else:
            distDir=sys.argv[0]
            
            
updateApplicationXMLs(distDir)

