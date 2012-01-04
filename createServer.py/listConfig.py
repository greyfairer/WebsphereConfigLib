import xml.dom.javadom
import xml.dom.ext
import org.apache.xpath
from listConfigClasses import ConfigClasses
import sys
import os
import sre

global AdminControl, AdminConfig, AdminTask, AdminApp
global xpath
xpath = org.apache.xpath.CachedXPathAPI()

def wsadminToList(inStr):
    outList = []
    tmpList = inStr.splitlines()
    if len(tmpList) < 2 and len(inStr) > 0 and inStr[0] == '[' and inStr[-1] == ']':
        tmpList = inStr[1:-1].split(" ")
        rematched = []
        append = 0
        for item in tmpList:
            if not len(item):
                if append == 1:
                    rematched[-1] = rematched[-1] + " "
                else:
                    continue
            elif append == 0 and item[0] == '"':
                rematched.append(item[1:])
                if item[-1] != '"':
                    append = 1
            elif not append:
                rematched.append(item)
            else: #append == 1
                if item[-1] == '"':
                    rematched[-1] = rematched[-1] + " " + item[:-1]
                    append = 0
                else:
                    rematched[-1] = rematched[-1] + " " + item
        tmpList = rematched
    for item in tmpList:
        if len(item) > 0:
            outList.append(item)
    return outList


def getChild(node, childName):
    for child in node.childNodes:
        if child.nodeType == xml.dom.javadom.ELEMENT_NODE and child.nodeName == childName:
            return child
    return None

#    return xml.dom.javadom._wrap_node(xpath.selectSingleNode(node._impl, childName))

def listApplications(doc, rootElement):
    applicationsElement = doc.createElement("Applications")
    rootElement.appendChild(applicationsElement)
    applications = AdminApp.list().splitlines()
    for applicationName in applications:
        applicationElement = doc.createElement("Application")
        applicationsElement.appendChild(applicationElement)
        applicationElement.setAttribute("name", applicationName)
        lines = AdminApp.listModules(applicationName, "-server").splitlines()
        moduleTargets = {}
        for moduleLine in lines:
            moduleLineItems = moduleLine.split("#")
            moduleName = moduleLineItems[1].split("+")[0]
            moduleTargets[moduleName] = moduleLineItems[2]

        application = AdminConfig.getid("/Deployment:%s/" % applicationName)
        deployedObject = AdminConfig.showAttribute(application, "deployedObject")
        listConfigObject(doc, applicationElement, deployedObject, ConfigClasses.ApplicationDeploymentClass)

        webModuleDeployments = wsadminToList(
            AdminConfig.getid('/Deployment:%s/ApplicationDeployment:/WebModuleDeployment:/' % applicationName))
        for webModuleDeployment in webModuleDeployments:
            moduleName = AdminConfig.showAttribute(webModuleDeployment, "uri")
            moduleElement = listConfigObject(doc, applicationElement, webModuleDeployment,
                ConfigClasses.WebModuleDeploymentClass)
            if moduleTargets.has_key(moduleName):
                moduleTargetLine = moduleTargets[moduleName]
                appendTargets(doc, moduleElement, moduleTargetLine)
        ejbModuleDeployments = wsadminToList(
            AdminConfig.getid('/Deployment:%s/ApplicationDeployment:/EJBModuleDeployment:/' % applicationName))
        for ejbModuleDeployment in ejbModuleDeployments:
            moduleName = AdminConfig.showAttribute(ejbModuleDeployment, "uri")
            moduleElement = listConfigObject(doc, applicationElement, ejbModuleDeployment,
                ConfigClasses.EJBModuleDeploymentClass)
            if moduleTargets.has_key(moduleName):
                moduleTargetLine = moduleTargets[moduleName]
                appendTargets(doc, moduleElement, moduleTargetLine)


def appendTargets(doc, moduleElement, moduleTargetLine):
    nodeServerRegexp = sre.compile("WebSphere:cell=.*,node=(.*),server=(.*)")
    clusterRegexp = sre.compile("WebSphere:cell=.*,cluster=(.*)")
    for moduleTargetId in moduleTargetLine.split("+"):
        clusterMatch = clusterRegexp.match(moduleTargetId)
        if clusterMatch:
            targetElement = doc.createElement("Target")
            moduleElement.appendChild(targetElement)
            targetElement.setAttribute("cluster", clusterMatch.group(1))
        else:
            nodeServerMatch = nodeServerRegexp.match(moduleTargetId)
            if nodeServerMatch:
                targetElement = doc.createElement("Target")
                moduleElement.appendChild(targetElement)
                targetElement.setAttribute("node", nodeServerMatch.group(1))
                targetElement.setAttribute("server", nodeServerMatch.group(2))


def listConfigAttributes(doc, configElement, configObj, configClass):
    for attribute in configClass.requiredAttributes():
        configElement.setAttribute(attribute.attributeName, AdminConfig.showAttribute(configObj, attribute.configName))
    optionalAttributes = {}
    for attribute in configClass.optionalAttributes():
        try:
            attributeValue = AdminConfig.showAttribute(configObj, attribute.configName)
            if attributeValue is not None and len(attributeValue) > 0:
                optionalAttributes[attribute.attributeName] = attributeValue
        except:
            pass
    compositeAttributes = {}
    for attribute in configClass.complexAttributes():
        attributeValue = AdminConfig.showAttribute(configObj, attribute.configName)
        if attributeValue is not None and len(attributeValue) > 0:
            compositeAttributes[attribute] = attributeValue
    listAttributes = {}
    attributeListAttributes = {}
    for attribute in configClass.listAttributes():
        listAttributesList = wsadminToList(AdminConfig.list(attribute.attributeClass.classname, configObj))
        if len(listAttributesList) > 0:
            if attribute.parentName is None:
                listAttributes[attribute.attributeClass] = listAttributesList
            else:
                attributeListAttributes[attribute.attributeClass] = listAttributesList
    if len(optionalAttributes.keys()) + len(compositeAttributes.keys()) + len(attributeListAttributes.keys()) > 0:
        attributesElement = doc.createElement('Attributes')
        configElement.appendChild(attributesElement)
        for attributeName in optionalAttributes.keys():
            attributeElement = doc.createElement(attributeName)
            attributesElement.appendChild(attributeElement)
            attributeValueNode = doc.createTextNode(optionalAttributes[attributeName])
            attributeElement.appendChild(attributeValueNode)
        for compositeAttribute in compositeAttributes.keys():
            attributeElement = doc.createElement(compositeAttribute.attributeName)
            attributesElement.appendChild(attributeElement)
            compositeObject = compositeAttributes[compositeAttribute]
            listConfigAttributes(doc, attributeElement, compositeObject, compositeAttribute.attributeClass)
        for listAttributeClass in attributeListAttributes.keys():
            for listAttributeObject in attributeListAttributes[listAttributeClass]:
                listConfigObject(doc, attributesElement, listAttributeObject, listAttributeClass)
    for listAttributeClass in listAttributes.keys():
        for listAttributeObject in listAttributes[listAttributeClass]:
            listConfigObject(doc, configElement, listAttributeObject, listAttributeClass)


def listConfigObject(doc, element, configObj, configClass):
    configElement = doc.createElement(configClass.classname)
    element.appendChild(configElement)
    listConfigAttributes(doc, configElement, configObj, configClass)
    return configElement


def listCellResources(doc, resourcesElement, scope):
    for configClass in ConfigClasses.CellResources + ConfigClasses.ClusterResources:
        if configClass.groupName:
            groupElement = getChild(resourcesElement, configClass.groupName)
            for configObj in wsadminToList(AdminConfig.getid('/Cell:/%s:/' % configClass.classname)):
                print 'list: ' + configClass.classname
                if groupElement is None:
                    groupElement = doc.createElement(configClass.groupName)
                    resourcesElement.appendChild(groupElement)
                listConfigObject(doc, groupElement, configObj, configClass)
        else:
            for configObj in wsadminToList(AdminConfig.getid('/Cell:/%s:/' % configClass.classname)):
                print 'list: ' + configClass.classname
                listConfigObject(doc, resourcesElement, configObj, configClass)


def listClusterResources(doc, resourcesElement, scope):
    for configClass in ConfigClasses.ClusterResources:
        if configClass.groupName:
            groupElement = getChild(resourcesElement, configClass.groupName)
            for configObj in wsadminToList(AdminConfig.list(configClass.classname, scope)):
                if groupElement is None:
                    groupElement = doc.createElement(configClass.groupName)
                    resourcesElement.appendChild(groupElement)
                print 'list: ' + configClass.classname
                listConfigObject(doc, groupElement, configObj, configClass)
        else:
            for configObj in wsadminToList(AdminConfig.list(configClass.classname, scope)):
                print 'list: ' + configClass.classname
                listConfigObject(doc, resourcesElement, configObj, configClass)


def listServerConfigServices(doc, serverServicesElement, scope):
    for configClass in ConfigClasses.ServerConfigServices:
        for configObj in wsadminToList(AdminConfig.list(configClass.classname, scope)):
            print 'list: ' + configClass.classname
            listConfigObject(doc, serverServicesElement, configObj, configClass)
    tcs = AdminConfig.list('TransportChannelService', scope)
    for chain in wsadminToList(AdminConfig.list('Chain', tcs)):
        chainName = AdminConfig.showAttribute(chain, 'name')
        if 'WCInboundDefaultSecure' == chainName:
            chainElement = doc.createElement('Chain')
            serverServicesElement.appendChild(chainElement)
            chainElement.setAttribute('name', chainName)
            chainElement.setAttribute('enable', AdminConfig.showAttribute(chain, 'enable'))


def listCluster(doc, clusterElement, cluster):
    clusterName = AdminConfig.showAttribute(cluster, 'name')
    print 'listCluster: ' + clusterName
    clusterElement.setAttribute('name', clusterName)
    members = wsadminToList(AdminConfig.showAttribute(cluster, 'members'))
    for member in members:
        nodeElement = doc.createElement('Node')
        clusterElement.appendChild(nodeElement)
        nodeName = AdminConfig.showAttribute(member, 'nodeName')
        nodeElement.setAttribute('name', nodeName)
        serverElement = doc.createElement('Server')
        nodeElement.appendChild(serverElement)
        serverName = AdminConfig.showAttribute(member, 'memberName')
        serverElement.setAttribute('name', serverName)
        serverPortRegex = sre.compile("\[(.*) \[ \[port (.*)\] \[node (.*)\] \[host (.*)\] \[server (.*)\] \]\]")
        for serverPort in AdminTask.listServerPorts(serverName, '-nodeName %s' % nodeName).splitlines():
            serverPortMatch = serverPortRegex.match(serverPort)
            if serverPortMatch:
                serverPortElement = doc.createElement("ServerPort")
                serverElement.appendChild(serverPortElement)
                serverPortElement.setAttribute("endPointName", serverPortMatch.group(1))
                serverPortElement.setAttribute("host", serverPortMatch.group(4))
                serverPortElement.setAttribute("port", serverPortMatch.group(2))
    clusterConfigElement = doc.createElement('ClusterConfig')
    clusterElement.appendChild(clusterConfigElement)
    clusterResourcesElement = doc.createElement('Resources')
    clusterConfigElement.appendChild(clusterResourcesElement)
    listClusterResources(doc, clusterResourcesElement, cluster)
    for member in members:
        nodeName = AdminConfig.showAttribute(member, 'nodeName')
        serverName = AdminConfig.showAttribute(member, 'memberName')
        print 'listMember: ' + serverName
        server = AdminConfig.getid('/Node:%s/Server:%s/' % (nodeName, serverName))
        serverConfigElement = doc.createElement('ServerConfig')
        clusterElement.appendChild(serverConfigElement)
        serverConfigElement.setAttribute('match', serverName)
        serverResourcesElement = doc.createElement('Resources')
        serverConfigElement.appendChild(serverResourcesElement)
        listClusterResources(doc, serverResourcesElement, server)
        serverServicesElement = doc.createElement('Services')
        serverConfigElement.appendChild(serverServicesElement)
        listServerConfigServices(doc, serverServicesElement, server)
        listConfigAttributes(doc, serverConfigElement, server, ConfigClasses.ServerConfigClass)


def listNodeResources(doc, resourcesElement, scope):
    nodeName = AdminConfig.showAttribute(scope, 'name')
    for configClass in ConfigClasses.NodeConfigResources + ConfigClasses.ClusterResources:
        if configClass.groupName:
            groupElement = getChild(resourcesElement, configClass.groupName)
            for configObj in wsadminToList(
                AdminConfig.getid('/Cell:/Node:%s/%s:/' % (nodeName, configClass.classname))):
                print 'list: ' + configClass.classname
                if groupElement is None:
                    groupElement = doc.createElement(configClass.groupName)
                    resourcesElement.appendChild(groupElement)
                listConfigObject(doc, groupElement, configObj, configClass)
        else:
            for configObj in wsadminToList(
                AdminConfig.getid('/Cell:/Node:%s/%s:/' % (nodeName, configClass.classname))):
                print 'list: ' + configClass.classname
                listConfigObject(doc, resourcesElement, configObj, configClass)


def listNodeConfig(doc, nodeElement, node):
    nodeName = AdminConfig.showAttribute(node, 'name')
    print 'listnode: ' + nodeName
    nodeElement.setAttribute('name', nodeName)
    nodeElement.setAttribute('hostName', AdminConfig.showAttribute(node, 'hostName'))
    nodeServicesElement = doc.createElement('Resources')
    nodeElement.appendChild(nodeServicesElement)
    listNodeResources(doc, nodeServicesElement, node)
    serverPortRegex = sre.compile("\[(.*) \[ \[port (.*)\] \[node (.*)\] \[host (.*)\] \[server (.*)\] \]\]")
    for webServer in AdminConfig.list('WebServer', node).splitlines():
        webServerElement = doc.createElement('WebServer')
        nodeElement.appendChild(webServerElement)
        server = AdminConfig.showAttribute(webServer, 'server')
        serverName = AdminConfig.showAttribute(server, 'name')
        webServerElement.setAttribute("name", serverName)
        print 'list: WebServer ' + serverName
        for serverPort in AdminTask.listServerPorts(serverName, '-nodeName %s' % nodeName).splitlines():
            serverPortMatch = serverPortRegex.match(serverPort)
            if serverPortMatch:
                serverPortElement = doc.createElement("ServerPort")
                webServerElement.appendChild(serverPortElement)
                serverPortElement.setAttribute("endPointName", serverPortMatch.group(1))
                serverPortElement.setAttribute("host", serverPortMatch.group(4))
                serverPortElement.setAttribute("port", serverPortMatch.group(2))


def listCellConfig(doc, cellConfigElement):
    security = AdminConfig.getid('/Cell:/Security:/')
    securityElement = doc.createElement("Security")
    cellConfigElement.appendChild(securityElement)
    for configClass in ConfigClasses.CellConfigSecurity:
        for configObj in AdminConfig.list(configClass.classname, security).splitlines():
            configElement = doc.createElement(configClass.classname)
            securityElement.appendChild(configElement)
            for attribute in configClass.requiredAttributes():
                configElement.setAttribute(attribute.attributeName,
                    AdminConfig.showAttribute(configObj, attribute.attributeName))
    signerCertRegExp = sre.compile(
        "\[ \[issuedTo (.*)\] \[fingerPrint .*\] \[signatureAlgorithm .*\] \[serialNumber .*\] \[alias (.*)\] \[validity (.*)\] \[version .*\] \[issuedBy .*\] \[size .*\] \]")
    for keystoreName in ['CellDefaultKeyStore', 'CellDefaultTrustStore']:
        keystoreElement = doc.createElement(keystoreName)
        securityElement.appendChild(keystoreElement)
        for line in AdminTask.listSignerCertificates('[-keyStoreName %s]' % keystoreName).splitlines():
            signerCertMatch = signerCertRegExp.match(line)
            if signerCertMatch:
                signerCertElement = doc.createElement('SignerCertificate')
                keystoreElement.appendChild(signerCertElement)
                signerCertElement.setAttribute("alias", signerCertMatch.group(2))
                signerCertElement.setAttribute("issuedTo", signerCertMatch.group(1))
                signerCertElement.setAttribute("validity", signerCertMatch.group(3))
        for line in AdminTask.listPersonalCertificates('[-keyStoreName %s]' % keystoreName).splitlines():
            signerCertMatch = signerCertRegExp.match(line)
            if signerCertMatch:
                signerCertElement = doc.createElement('PersonalCertificate')
                keystoreElement.appendChild(signerCertElement)
                signerCertElement.setAttribute("alias", signerCertMatch.group(2))
                signerCertElement.setAttribute("issuedTo", signerCertMatch.group(1))
                signerCertElement.setAttribute("validity", signerCertMatch.group(3))
    cellResourcesElement = doc.createElement('Resources')
    cellConfigElement.appendChild(cellResourcesElement)
    listCellResources(doc, cellResourcesElement, AdminConfig.getid('/Cell:/'))


def listConfig(distDir):
    xml.dom.javadom.Node.namespaceURI = None
    impl = xml.dom.javadom.XercesDomImplementation()
    cellName = AdminControl.getCell()
    dirName = distDir + "/" + cellName
    if not os.path.isdir(dirName):
        os.makedirs(dirName)

    doc = impl.createDocument()
    cellElement = doc.createElement("Cell")
    cellElement._impl.setAttribute('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
    cellElement._impl.setAttributeNS('http://www.w3.org/2001/XMLSchema-instance', 'xsi:noNamespaceSchemaLocation',
        'file://configsrv/configurations/Servers/APPSRVs/MLEwsadmin/bin/createServer.py/WASConfig.xsd')
    doc.appendChild(cellElement)
    cellElement.setAttribute("name", cellName)

    listApplications(doc, cellElement)

    cellConfigElement = doc.createElement("CellConfig")
    cellElement.appendChild(cellConfigElement)
    print 'listCellConfig: ' + cellName
    listCellConfig(doc, cellConfigElement)

    for cluster in wsadminToList(AdminConfig.list("ServerCluster")):
        clusterElement = doc.createElement("ServerCluster")
        cellElement.appendChild(clusterElement)
        listCluster(doc, clusterElement, cluster)

    for node in wsadminToList(AdminConfig.list("Node")):
        nodeElement = doc.createElement("NodeConfig")
        cellElement.appendChild(nodeElement)
        listNodeConfig(doc, nodeElement, node)

    file = "%s/%s.xml" % (dirName, cellName)
    if os.path.isfile(file):
        if os.path.isfile(file + ".bak"):
            os.remove(file + ".bak")
        os.rename(file, file + ".bak")
    stream = open(file, "wt")
    xml.dom.ext.PrettyPrint(doc, stream)
    stream.close()


distDir = "."
if len(sys.argv) > 0:
    param1 = sys.argv[0]
    param1 = param1[len(param1) - 3:].lower()
    if sys.argv[0][-3:].lower() == ".py" or sys.argv[0][-3:].lower() == ".jy":
        if len(sys.argv) > 1:
            distDir = sys.argv[1]
    else:
        distDir = sys.argv[0]

listConfig(distDir)
