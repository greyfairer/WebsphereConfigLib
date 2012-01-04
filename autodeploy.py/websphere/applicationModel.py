
from xml.dom.javadom import TEXT_NODE, CDATA_SECTION_NODE, NodeList, _wrap_node
from org.apache.xpath import XPathAPI

class ApplicationAttribute:
    def __init__(self, name, value):
        self.name = name
        self.value = value
 
class ApplicationModule:
    def __init__(self, name, attributes):
        __init__(self, name, attributes, [])
    def __init__(self, name, attributes, targets):
        self.name = name
        self.attributes = attributes
        self.targets = targets
        self.contextRoot = None
        self.virtualHost='default_host'
        
    def setTargets(self, targets):
        self.targets = targets
                
class ApplicationTarget:
    DEFAULT = "Default"
    CLUSTER = "Cluster"
    SERVER = "Server"
    def __init__(self, tests = [], jvmAttributes = []):
        self.tests = tests
        self.jvmAttributes = jvmAttributes
    def targetName(self):
        return ApplicationTarget.DEFAULT
    def targetType(self):
        return ApplicationTarget.DEFAULT
    
    
        
class ClusterApplicationTarget(ApplicationTarget):
    def __init__(self, clusterName, tests = [], jvmAttributes = []):
        ApplicationTarget.__init__(self, tests, jvmAttributes)
        self.clusterName = clusterName
        self.inactiveServers = []
    def targetName(self):
        return self.clusterName
    def targetType(self):
        return ApplicationTarget.CLUSTER

class ServerApplicationTarget(ApplicationTarget):
    def __init__(self, nodeName, serverName, tests=[], jvmAttributes=[]):
        ApplicationTarget.__init__(self, tests, jvmAttributes)
        self.nodeName = nodeName
        self.serverName= serverName

    def targetName(self):
        return self.nodeName + ":"+self.serverName
    
    def targetType(self):
        return ApplicationTarget.SERVER
        
        
class ApplicationTargetTest:
    def __init__(self, url, response):
        self.url=url
        self.response=response
         
class Application:
    def __init__(self, file, name, installOptions, attributes, modules, targets, configFile=''):
        self.file = file
        self.name=name
        self.installOptions=installOptions
        self.attributes=attributes
        self.modules = modules
        self.setTargets(targets)
        self.configFile = configFile
        self.version = None
        self.serviceCall = None
        self.shortName = None
        self.scripts = {}
        self.virtualHost='default_host'

    def setTargets(self, targets):
        self.servers = []
        self.clusters = []
        self.targets = []
        for target in targets:
            if target.targetType()==ApplicationTarget.CLUSTER:
                self.clusters.append(target)
            elif target.targetType()==ApplicationTarget.SERVER:
                self.servers.append(target)
            else:
                self.targets.append(target)
        
    def __repr__(self):
        repr ="<Application '%s' at '%s' from %s" %(self.name, self.file, self.configFile)
        for installOption in self.installOptions:
            repr = repr + "\n\tInstallOption '%s'" % installOption
        for attribute in self.attributes:
            repr = repr + "\n\tAttribute '%s': '%s'" % (attribute.name, attribute.value)
        for script in self.scripts.items():
            repr = repr + "\n\tScript '%s': '%s'" % script
        for module in self.modules:
            repr = repr + "\n\tModule '%s'" % (module.name)
            for attribute in module.attributes:
                repr = repr + "\n\t\tAttribute '%s': '%s'" % (attribute.name, attribute.value)
            for target in module.targets:
                repr = repr + "\n\t\tTarget '%s'" % (target.targetName())
                if target.targetType()==ApplicationTarget.CLUSTER:
                    for serverTarget in target.inactiveServers:
                        repr = repr + "\n\t\t\tInactiveServer '%s'" % (serverTarget.targetName())
                for test in target.tests:
                    repr = repr + "\n\t\tTest '%s': '%s'" % (test.url, test.response)
        for target in self.servers:
            repr = repr + "\n\tTarget '%s'" % (target.targetName())
            for test in target.tests:
                repr = repr + "\n\t\tTest '%s': '%s'" % (test.url, test.response)
            for attribute in target.jvmAttributes:
                repr = repr + "\n\t\tAttribute '%s': '%s'" % (attribute.name, attribute.value)
        for target in self.clusters:
            repr = repr + "\n\tTarget '%s'" % (target.targetName())
            for serverTarget in target.inactiveServers:
                repr = repr + "\n\t\tInactiveServer '%s'" % (serverTarget.targetName())
            for test in target.tests:
                repr = repr + "\n\t\tTest '%s': '%s'" % (test.url, test.response)
            for attribute in target.jvmAttributes:
                repr = repr + "\n\t\tAttribute '%s': '%s'" % (attribute.name, attribute.value)
        for target in self.targets:
            repr = repr + "\n\tTarget '%s'" % (target.targetName())
            for test in target.tests:
                repr = repr + "\n\t\tTest '%s': '%s'" % (test.url, test.response)
            for attribute in target.jvmAttributes:
                repr = repr + "\n\t\tAttribute '%s': '%s'" % (attribute.name, attribute.value)
        repr = repr + ">"    
        return repr
     
def getText(textNode):
    rc = ""
    if textNode:
        for node in textNode.childNodes:
            if node.nodeType == TEXT_NODE or node.nodeType == CDATA_SECTION_NODE:
                rc = rc + node.data
    return rc

def getChildText(node, childName):
    return getText(getChild(node, childName))

def getChild(node, childName):
    return _wrap_node(XPathAPI.selectSingleNode(node._impl, childName))
    
def getChildElements(node, childName):
    return NodeList(XPathAPI.selectNodeList(node._impl, childName))
  
def parseTargets(applicationNode):  
    targets = []
    for targetNode in getChildElements(applicationNode,"target"):
        tests = []
        jvmAttributes = []
        for attributeNode in getChildElements(targetNode, "jvm-attribute"):
            attributeName=attributeNode.getAttribute("name")
            jvmAttributes.append(ApplicationAttribute(attributeName, getText(attributeNode)))
        for testNode in targetNode.getElementsByTagName("test"):
            url= testNode.getAttribute("url")
            response = testNode.getAttribute("response")
            tests.append(ApplicationTargetTest(url, response))

        if len(targetNode.getElementsByTagName("server"))>0:
            serverName = getChildText(targetNode, "server")
            nodeName = getChildText(targetNode, "node")
            targets.append(ServerApplicationTarget(nodeName, serverName, tests, jvmAttributes))
        elif getChild(targetNode, "cluster"):
            clusterElement = getChild(targetNode, "cluster")
            clusterName=clusterElement.getAttribute("name")
            if clusterName == None or len(clusterName) == 0:
                clusterName = getChildText(targetNode, "cluster")
            clusterTarget = ClusterApplicationTarget(clusterName, tests, jvmAttributes)
            targets.append(clusterTarget)
            inactiveServers = []
            for inactiveServerElement in clusterElement.getElementsByTagName("inactiveServer"):
                serverName = inactiveServerElement.getAttribute("server")
                nodeName = inactiveServerElement.getAttribute("node")
                inactiveServers.append(ServerApplicationTarget(nodeName, serverName))
            clusterTarget.inactiveServers = inactiveServers
        else:            
            targets.append(ApplicationTarget(tests, jvmAttributes))
    return targets
                
def parseApplication(dom):    
    applicationNode = dom.documentElement
    appName = getChildText(applicationNode, "name")
    fileName = getChildText(applicationNode, "file")
    installOptions=[]
    for installOptionNode in getChildElements(applicationNode,"installOption"):
        installOptions.append(getText(installOptionNode))
    attributes=[]
    for attributeNode in getChildElements(applicationNode,"attribute"):
        attributeName=attributeNode.getAttribute("name")
        attributes.append(ApplicationAttribute(attributeName, getText(attributeNode)))
    modules = []
    for moduleNode in getChildElements(applicationNode, "module"):
        moduleName=getChildText(moduleNode, "name")
        contextRoot=getChildText(moduleNode, "contextRoot")
        moduleAttributes=[]
        for attributeNode in getChildElements(moduleNode, "attribute"):
            attributeName=attributeNode.getAttribute("name")
            moduleAttributes.append(ApplicationAttribute(attributeName, getText(attributeNode)))
        moduleTargets = parseTargets(moduleNode)
        module=ApplicationModule(moduleName, moduleAttributes, moduleTargets)
        if len(contextRoot) > 0:
            module.contextRoot=contextRoot        
        virtualHost=getChildText(moduleNode, "virtualHost")
        if len(virtualHost) > 0:
            module.virtualHost = virtualHost
        modules.append(module)
    targets = parseTargets(applicationNode)
    application=Application(fileName, appName, installOptions, attributes, modules, targets)
    application.shortName = getChildText(applicationNode, "shortName")
    if application.shortName == "":
        application.shortName = application.name
    virtualHost=getChildText(applicationNode, "virtualHost")
    if len(virtualHost) > 0:
        application.virtualHost = virtualHost
    application.version = getChildText(applicationNode, "version")
    application.serviceCall = getChildText(applicationNode, "serviceCall")
    return application

def addExtra(applications, dom):
    applicationNode = dom.documentElement
    appName = getChildText(applicationNode, "name")
    if applications.has_key(appName):
        for scriptNode in getChildElements(applicationNode,"script"):
            scriptName = scriptNode.getAttribute("name")
            applications[appName].scripts[scriptName]=getText(scriptNode)
        for installOptionNode in getChildElements(applicationNode,"installOption"):
            applications[appName].installOptions.append(getText(installOptionNode))
        targets = parseTargets(applicationNode)
        if len(targets) > 0:
            for target in targets:
                for test in target.tests:
                    if test.response == None or len(test.response)==0:
                        test.response = applications[appName].version
            applications[appName].setTargets(targets)
        for moduleNode in getChildElements(applicationNode, "module"):
            moduleName=getChildText(moduleNode, "name")
            moduleTargets = parseTargets(moduleNode)
            if len(moduleTargets) > 0: 
                for module in applications[appName].modules:
                    if module.name == moduleName:
                        module.setTargets(moduleTargets)
            
     

def addDomAttribute(dom, moduleNode, attributeKey, attributeValue):
    attrElement= dom.createElement("attribute")
    moduleNode.appendChild(attrElement)
    attrElement.setAttribute("name", attributeKey)
    textNode = dom.createTextNode(attributeValue)
    attrElement.appendChild(textNode)


def addDomTarget(dom, moduleNode, target):
    targetElement = dom.createElement("target")
    moduleNode.appendChild(targetElement)
    if target.targetType() == ApplicationTarget.CLUSTER:
        clusterElement = dom.createElement("cluster")
        targetElement.appendChild(clusterElement)
        clusterElement.setAttribute("name", target.clusterName)
        
    elif target.targetType() == ApplicationTarget.SERVER:
        nodeElement = dom.createElement("node")
        targetElement.appendChild(nodeElement)
        textElement = dom.createTextNode(target.nodeName)
        nodeElement.appendChild(textElement)
        serverElement = dom.createElement("server")
        targetElement.appendChild(serverElement)
        textElement = dom.createTextNode(target.serverName)
        serverElement.appendChild(textElement)
        
    contextRoot=getChildText(moduleNode, "context-root")
    for test in target.tests:
        testElement = dom.createElement("test")
        targetElement.appendChild(testElement)
        if contextRoot[0] == '/':
            contextRoot = contextRoot[1:]
        if contextRoot[-1] == '/':
            contextRoot = contextRoot[:-1]
            
        testElement.setAttribute("url", test.url+contextRoot+"/version.jsp")
        
        testElement.setAttribute("response", test.response)
        
    
def updateApplicationModel(dom, moduleConfigs, applicationAttributes, comment):
    error = 0
    applicationNode = dom.documentElement
    firstClusterTarget = None
    for moduleNode in getChildElements(applicationNode,"module"):
        moduleName=getChildText(moduleNode, "name")
        if moduleConfigs.has_key(moduleName):
            for target in moduleConfigs[moduleName]["targets"]:
                if firstClusterTarget == None and target.targetType() == ApplicationTarget.CLUSTER:
                    firstClusterTarget = target                    
                addDomTarget(dom, moduleNode, target)
            for attributeKey, attributeValue in moduleConfigs[moduleName]["attributes"]:
                addDomAttribute(dom, moduleNode, attributeKey, attributeValue)
        else:
            targetElement = dom.createComment("<target><cluster>UNKNOWN</cluster></target>")
            moduleNode.appendChild(targetElement)
            error += 1
    if len(comment) > 0:
        commentNode = dom.createComment(comment)
        applicationNode.insertBefore(commentNode, getChild(applicationNode, "name"))
    for attributeKey, attributeValue in applicationAttributes:
        addDomAttribute(dom, applicationNode, attributeKey, attributeValue)

    if firstClusterTarget == None:
        for moduleConfig in moduleConfigs.values():
            for target in moduleConfig["targets"]:
                if firstClusterTarget == None and target.targetType() == ApplicationTarget.CLUSTER:
                    firstClusterTarget = target
                
    targetNode = getChild(applicationNode, "target")
    if targetNode == None:
        targetNode = dom.createElement("target")
        applicationNode.appendChild(targetNode)
    if firstClusterTarget != None:
        clusterElement = dom.createElement("cluster")
        testNode = getChild(targetNode, "test")
        if testNode == None:
            targetNode.appendChild(clusterElement)
        else:
            targetNode.insertBefore(clusterElement, testNode)
        clusterElement.setAttribute("name", firstClusterTarget.clusterName)
        for inactiveServer in firstClusterTarget.inactiveServers:
            inactiveServerElement = dom.createElement("inactiveServer")
            clusterElement.appendChild(inactiveServerElement)
            inactiveServerElement.setAttribute("node", inactiveServer.nodeName)
            inactiveServerElement.setAttribute("server", inactiveServer.serverName)
    else:
        error += 1
        clusterElement = dom.createComment("<cluster>UNKNOWN<cluster>")
        testNode = getChild(targetNode, "test")
        if testNode == None:
            targetNode.appendChild(clusterElement)
        else:
            targetNode.insertBefore(clusterElement, testNode)    
    
    return error
