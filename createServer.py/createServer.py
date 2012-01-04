__version__ = "$Revision: 481 $"

from warnings import warn
import sys
from xml.dom.javadom import TEXT_NODE, CDATA_SECTION_NODE, NodeList, _wrap_node, XercesDomImplementation
from org.apache.xpath import CachedXPathAPI
import sre




global AdminControl, AdminConfig, AdminTask
global xpath
xpath = CachedXPathAPI()

def wsadminToList(inStr):
    outList = []
    if (len(inStr) > 0 and inStr[0] == '[' and inStr[ -1] == ']'):
            tmpList = inStr[1:-1].split(" ")
    else:
            tmpList = inStr.split("\n")  #splits for Windows or Linux
    for item in tmpList:
            item = item.rstrip();        #removes any Windows "\r"
            if (len(item) > 0):
                    outList.append(item)
    return outList

def mapToAArray(map):
    aarray = []
    for item in map.items():
        aarray.append([item[0], item[1]])
    return aarray

def attributesToAArray(node, filterExpr=lambda a: 1):
    aarray = []
    for attribute in filter(filterExpr, node.attributes.values()):
        aarray.append([attribute.name, attribute.value])
    return aarray

def getText(textNode):
    rc = ""
    for node in textNode.childNodes:
        if node.nodeType == TEXT_NODE or node.nodeType == CDATA_SECTION_NODE:
            rc = rc + node.data
    return rc

def getChildText(node, childName):
    return getText(getChild(node, childName))

def getChild(node, childName):
    if node:
        return _wrap_node(xpath.selectSingleNode(node._impl, childName))
    else:
        return None
    
def getChildElements(node, childName):
    return NodeList(xpath.selectNodeList(node._impl, childName))   

def modifyAttributes(configNode, scope, xpath="Attributes/*"):
    for attributeNode in getChildElements(configNode, xpath):
        aarray = attributesToAArray(attributeNode)
        if len(aarray) > 0 or getChild(attributeNode, "Attributes"):
            if attributeNode.nodeName[0].isupper():
                print 'Creating %s' % attributeNode.nodeName
                attribute = AdminConfig.create(attributeNode.nodeName, scope, aarray)
            else:
                attribute = AdminConfig.showAttribute(scope, attributeNode.nodeName)
                AdminConfig.modify(attribute, aarray)

            if getChild(attributeNode, "Attributes"):
                modifyAttributes(attributeNode, attribute)
        else:
            text = getText(attributeNode)
            if len(text.strip()) > 0:
                print 'Modifying %s: %s' % (attributeNode.nodeName, text)
                if attributeNode.nodeName == 'serviceNames' and text == '[]':
                    AdminConfig.modify(scope, [['serviceNames', '']])
                else:
                    AdminConfig.modify(scope, [[attributeNode.nodeName, text]])
 
def getClusterMembers(clusterId):
    serverIds = []
    nodeNames = []
    members = wsadminToList(AdminConfig.showAttribute(clusterId, 'members'))
    for member in members:
        nodeName = AdminConfig.showAttribute(member, 'nodeName')
        serverName = AdminConfig.showAttribute(member, 'memberName')
        serverId = AdminConfig.getid('/Node:%s/Server:%s/' % (nodeName, serverName))
        serverIds.append({"node": nodeName, "server": serverName, "serverId": serverId})
        if not nodeName in nodeNames:
            nodeNames.append(nodeName)
    return serverIds, nodeNames

def createClusterMembers(clusterName, nodesNodeList, cellName):
    serverNodeList = getChildElements(nodesNodeList[0], 'Server')           
    firstServer = serverNodeList[0].attributes['name'].value
    firstNode = nodesNodeList[0].attributes['name'].value
    nodeNames = [firstNode]
    serverIds = []
    nodeId = AdminConfig.getid('/Node:' + firstNode + '/')
    if (len(nodeId) == 0):
        raise NotImplementedError('Node does not exist: %s, node creation not implemented' % firstNode)
    
    clusterId = AdminConfig.getid('/ServerCluster:%s/' % clusterName)
    if len(clusterId) > 0:
        warn('cluster %s allready exists' % clusterId)
        serverId = AdminConfig.getid('/Node:%s/Server:%s/' % (firstNode, firstServer))
        if len(serverId) > 0:
            warn('server %s allready exists' % serverId)
            serverIds.append({"node": firstNode, "server": firstServer, "serverId": serverId})
    else:
        serverId = AdminConfig.getid('/Node:%s/Server:%s/' % (firstNode, firstServer))
        if len(serverId) > 0:
            warn('server %s allready exists' % serverId)
        else:
            print "First server: %s on %s" % (firstServer, firstNode)
            serverId = AdminConfig.create('Server', nodeId, [['name', firstServer]])
        clusterId = AdminConfig.convertToCluster(serverId, clusterName)
        

        serverIds.append({"node": firstNode, "server": firstServer, "serverId": serverId})
        #for otherServerNode in serverNodeList[1:] does not work -> bug in javadom.NodeList.__getslice__
    for i in range(1, len(serverNodeList)):
        otherServerNode = serverNodeList[i]
        serverName = otherServerNode.attributes['name'].value
        serverId = AdminConfig.getid('/Node:%s/Server:%s/' % (firstNode, serverName))
        if len(serverId) > 0:
            warn('server %s allready exists' % serverId)
        else:
            print "Other server: %s on %s" % (serverName, firstNode)
            AdminConfig.createClusterMember(clusterId, nodeId, [['memberName', serverName]])
            serverId = AdminConfig.getid('/Node:%s/Server:%s/' % (firstNode, serverName))
        serverIds.append({"node": firstNode, "server": serverName, "serverId": serverId})
    for i in range(1, len(nodesNodeList)):
        otherNodeNode = nodesNodeList[i]
        nodeName = otherNodeNode.attributes['name'].value
        nodeNames.append(nodeName)
        nodeId = AdminConfig.getid('/Node:' + nodeName + '/')
        if (len(nodeId) == 0):
            raise NotImplementedError('Node does not exist: %s, node creation not implemented' % nodeName)
        otherServerNodeList = getChildElements(otherNodeNode, 'Server')
        for j in range(0, len(otherServerNodeList)):
            otherServerNode = otherServerNodeList[j]
            serverName = otherServerNode.attributes['name'].value
            serverId = AdminConfig.getid('/Node:%s/Server:%s/' % (nodeName, serverName))
            if len(serverId) > 0:
                warn('server %s allready exists' % serverId)
            else:
                print "Other server: %s on %s" % (serverName, nodeName)
                AdminConfig.createClusterMember(clusterId, nodeId, [['memberName', serverName]])
                serverId = AdminConfig.getid('/Node:%s/Server:%s/' % (nodeName, serverName))
            serverIds.append({"node": nodeName, "server": serverName, "serverId": serverId})
    return clusterId, serverIds, nodeNames

def modifyServerPorts(nodeName, serverName, serverPortNode):
    if serverPortNode.getAttributeNode("host"):
        AdminTask.modifyServerPort(serverName, ['-nodeName', nodeName, '-endPointName', serverPortNode.attributes["endPointName"].value, '-host', serverPortNode.attributes["host"].value, '-port', serverPortNode.attributes["port"].value, '-modifyShared', 'true'])
    else:
        AdminTask.modifyServerPort(serverName, ['-nodeName', nodeName, '-endPointName', serverPortNode.attributes["endPointName"].value, '-port', serverPortNode.attributes["port"].value, '-modifyShared', 'true'])

def createDataSources(scopeString, scopePath, jdbcProviderNode):
    jdbcProviderParams = {'scope': scopeString}
    for attribute in jdbcProviderNode.attributes.values():
        jdbcProviderParams[attribute.name] = attribute.value
    jdbcProvider = AdminConfig.getid('%sJDBCProvider:%s/' % (scopePath, jdbcProviderParams['name']))
    if len(jdbcProvider) == 0:
        command = '[-scope %(scope)s -databaseType "%(databaseType)s" -providerType "%(providerType)s" -implementationType "%(implementationType)s" -name "%(name)s" -description "%(description)s"]'
        jdbcProvider = AdminTask.createJDBCProvider(command % jdbcProviderParams)
    else:
        print 'Modify JDBCProvider %s' % jdbcProvider
    for dataSourceNode in getChildElements(jdbcProviderNode, "DataSource"):
        dataSourceProperties = {}
        for attribute in dataSourceNode.attributes.values():
            dataSourceProperties[attribute.name] = attribute.value
        
        dataSourceId = '%sJDBCProvider:%s/DataSource:%s/' % (scopePath, jdbcProviderParams['name'], dataSourceProperties['name'])
        dataSource = AdminConfig.getid(dataSourceId)
        if len(dataSource) == 0:
            resourceProperties = []
            for resourcePropertyNode in getChildElements(dataSourceNode, "ResourceProperties/J2EEResourceProperty"):
                resourceProperties.append("[%s %s \"%s\"]" % (resourcePropertyNode.attributes['name'].value, resourcePropertyNode.attributes['type'].value, resourcePropertyNode.attributes['value'].value))
            dataSourceProperties['resourceProperties'] = "[%s]" % ",".join(resourceProperties)          
            command = '[-name "%(name)s" -jndiName %(jndiName)s -dataStoreHelperClassName %(datasourceHelperClassname)s -configureResourceProperties %(resourceProperties)s -description "%(description)s"]'
            print "Creating Datasource %(name)s" % dataSourceProperties
            dataSource = AdminTask.createDatasource(jdbcProvider, command % dataSourceProperties)
        else:
            print "Modifying Datasource %s" % dataSource
            for resourcePropertyNode in getChildElements(dataSourceNode, "ResourceProperties/J2EEResourceProperty"):
                resourcePropertySet = AdminConfig.getid('%sJDBCProvider:%s/DataSource:%s/J2EEResourcePropertySet:/'
                  % (scopePath, jdbcProviderParams['name'], dataSourceProperties['name']))
                resourceProperty = AdminConfig.getid('%sJDBCProvider:%s/DataSource:%s/J2EEResourcePropertySet:/J2EEResourceProperty:%s/'
                  % (scopePath, jdbcProviderParams['name'], dataSourceProperties['name'], resourcePropertyNode.attributes['name'].value))
                if len(resourceProperty) == 0:
                    AdminConfig.create('J2EEResourceProperty', resourcePropertySet, attributesToAArray(resourcePropertyNode))
                else:
                    AdminConfig.modify(resourceProperty, [['value', resourcePropertyNode.attributes['value'].value]])
        if getChild(dataSourceNode, "Attributes"): 
            modifyAttributes(dataSourceNode, dataSource)

def createMailSessions(scopePath, mailProviderNode):
    mailProvider = wsadminToList(AdminConfig.getid('%sMailProvider:/' % scopePath))[0]
    for mailSessionNode in getChildElements(mailProviderNode, "MailSession"):
        mailSessionProperties = {}
        for attribute in mailSessionNode.attributes.values():
            mailSessionProperties[attribute.name] = attribute.value
        mailSessionId = '%sMailProvider:/MailSession:%s/' % (scopePath, mailSessionProperties['name'])
        mailSession = AdminConfig.getid(mailSessionId)
        if len(mailSession) == 0:
            print "Creating MailSession"
            mailSession = AdminConfig.create('MailSession', mailProvider, mapToAArray(mailSessionProperties))
        else:
            print "Modifying MailSession %s" % mailSession
            for item in mailSessionProperties.items():
                if item[0] != 'name':
                    AdminConfig.modify(mailSession, [[item[0], item[1]]])

        resourcePropertiesNodeList = getChildElements(mailSessionNode, "Attributes/J2EEResourceProperty")
        if len(resourcePropertiesNodeList) > 0:
            resourcePropertySet = AdminConfig.getid('%sMailProvider:/MailSession:%s/J2EEResourcePropertySet:/'
              % (scopePath, mailSessionProperties['name']))
            if len(resourcePropertySet) == 0:
                resourcePropertySet = AdminConfig.create('J2EEResourcePropertySet', mailSession, [])

            for resourcePropertyNode in resourcePropertiesNodeList:
                        
                resourceProperty = AdminConfig.getid('%sMailProvider:/MailSession:%s/J2EEResourcePropertySet:/J2EEResourceProperty:%s/'
                  % (scopePath, mailSessionProperties['name'], resourcePropertyNode.attributes['name'].value))
                if len(resourceProperty) == 0:
                    AdminConfig.create('J2EEResourceProperty', resourcePropertySet, attributesToAArray(resourcePropertyNode))
                else:
                    AdminConfig.modify(resourceProperty, [['value', resourcePropertyNode.attributes['value'].value]])

def createVirtualHosts(scopePath, virtualHostNode):
    virtualHost = wsadminToList(AdminConfig.getid('%sVirtualHost:%s/' % (scopePath, virtualHostNode.attributes["name"].value)))[0]
    for hostAliasNode in getChildElements(virtualHostNode, "Attributes/HostAlias"):
        hostAliasProperties = attributesToAArray(hostAliasNode)
        print "Creating HostAlias"
        AdminConfig.create('HostAlias', virtualHost, hostAliasProperties)
    for mimeEntryNode in getChildElements(virtualHostNode, "Attributes/MimeEntry"):
        mimeEntryProperties = attributesToAArray(mimeEntryNode)
        print "Creating MimeEntry"
        AdminConfig.create('MimeEntry', virtualHost, mimeEntryProperties)

def createURLs(scopePath, urlProviderNode):        
    urlProvider = wsadminToList(AdminConfig.getid('%sURLProvider:/' % scopePath))[0]
    for urlNode in getChildElements(urlProviderNode, "URL"):
        urlProperties = {}
        for attribute in urlNode.attributes.values():
            urlProperties[attribute.name] = attribute.value

        urlObjId = '%sURLProvider:/URL:%s/' % (scopePath, urlProperties['name'])
        urlObj = AdminConfig.getid(urlObjId)
        if len(urlObj) == 0:
            print "Creating URL %s" % urlProperties
            urlObj = AdminConfig.create('URL', urlProvider, mapToAArray(urlProperties))  
        else:
            print "Modifying URL %s" % urlObj
            for item in urlProperties.items():
                if item[0] != 'name':
                    AdminConfig.modify(urlObj, [[item[0], item[1]]])
    

def createWorkManagers(scopePath, wmProviderNode):        
    wmProvider = wsadminToList(AdminConfig.getid('%sWorkManagerProvider:/' % scopePath))[0]
    for wmNode in getChildElements(wmProviderNode, "WorkManagerInfo"):
        wmProperties = attributesToAArray(wmNode)
        print "Creating WorkManagerInfo %s" % wmProperties
        workManagerInfo = AdminConfig.create('WorkManagerInfo', wmProvider, wmProperties)  
        if getChild(wmNode, "Attributes"):
            modifyAttributes(wmNode, workManagerInfo)

def createDataReplicationDomain(scope, drdNode):        
    drdProperties = attributesToAArray(drdNode)
    print "Creating DataReplicationDomain %s" % drdProperties
    drd = AdminConfig.create('DataReplicationDomain', scope, drdProperties)  
    if getChild(drdNode, "Attributes"):
        modifyAttributes(drdNode, drd)
        
def createSIBus(sibusNode): 
    params = []
    for attribute in sibusNode.attributes.values():
        params.append('-%s "%s"' % (attribute.name, attribute.value))
    
    print "AdminTask.createSIBus " + " ".join(params)
    sibus = AdminTask.createSIBus(" ".join(params))
    
    if getChild(sibusNode, "Attributes"):
        modifyAttributes(sibusNode, sibus)

def createSIBMessagingEngine(scopeString, scope, sibMeNode):
    params = '-bus "%s"' % sibMeNode.attributes["busName"].value
    fileStore = getChild(sibMeNode, "fileStore")
    if fileStore:
        params = params + " -fileStore"
        for attribute in fileStore.attributes.values():
            params = params + ' -%s "%s"' % (attribute.name, attribute.value)
    dataStore = getChild(sibMeNode, "dataStore")
    if dataStore:
        params = params + " -dataStore"
        for attribute in dataStore.attributes.values():
            params = params + ' -%s "%s"' % (attribute.name, attribute.value)
    
    if sre.match("Cluster=(.*)", scopeString):
        params = params + ' -cluster "%s"' % sre.match("Cluster=(.*)", scopeString).group(1) 
    elif  sre.match("Node=(.*),Server=(.*)", scopeString):        
        params = params + ' -node "%s" -server "%s"' % sre.match("Node=(.*),Server=(.*)", scopeString).group(1, 2)
    print "AdminTask.addSIBusMember " + params
    AdminTask.addSIBusMember(params)
    if getChild(sibMeNode, "Attributes"):
        messagingEngine = wsadminToList(AdminConfig.list('SIBMessagingEngine', scope))[0]
        print 'me: ' + messagingEngine 
        modifyAttributes(sibMeNode, messagingEngine)
    
    
def createSIBJMSConnectionFactory(scope, cfNode, sibCfNode):
    params = []
    for attribute in cfNode.attributes.values():
        params.append('-%s "%s"' % (attribute.name, attribute.value))
    for attribute in sibCfNode.attributes.values():
        params.append('-%s "%s"' % (attribute.name, attribute.value))
    print "AdminTask.createSIBJMSConnectionFactory " + " ".join(params)
    cf = AdminTask.createSIBJMSConnectionFactory(scope, " ".join(params))
    
    if getChild(cfNode, "Attributes"):
        modifyAttributes(cfNode, cf)

def createSIBQueue(scope, scopePath, adminObjectNode, sibDestinationNode):
    destinationparams = []
    for attribute in sibDestinationNode.attributes.values():
        if not (attribute.name in ("deliveryMode", "timeToLive", "priority", "readAhead")):
            destinationparams.append('-%s "%s"' % (attribute.name, attribute.value))
    if sre.match("/ServerCluster:(.*)/", scopePath) and not sibDestinationNode.attributes.has_key("cluster"):
        destinationparams.append('-cluster "%s"' % sre.match("/ServerCluster:(.*)/", scopePath).group(1))
    elif  sre.match("/Node:(.*)/Server:(.*)/", scopePath)  and not sibDestinationNode.attributes.has_key("server"):        
        destinationparams.append('-node "%s" -server "%s"' % sre.match("/Node:(.*)/Server:(.*)/", scopePath).group(1, 2))

    print "AdminTask.createSIBDestination " + " ".join(destinationparams)
    destination = AdminTask.createSIBDestination(" ".join(destinationparams))
    if getChild(sibDestinationNode, "Attributes"):
        modifyAttributes(sibDestinationNode, destination)

    queueparams = ['-queueName "%s"' % sibDestinationNode.attributes["name"].value]
    for attribute in adminObjectNode.attributes.values():
        queueparams.append('-%s "%s"' % (attribute.name, attribute.value))
    for attribute in sibDestinationNode.attributes.values():
        if attribute.name in ("deliveryMode", "timeToLive", "priority", "readAhead"):
            queueparams.append('-%s "%s"' % (attribute.name, attribute.value))
            
    print "AdminTask.createSIBJMSQueue " + " ".join(queueparams)
    cf = AdminTask.createSIBJMSQueue(scope, " ".join(queueparams))
    
    if getChild(adminObjectNode, "Attributes"):
        modifyAttributes(adminObjectNode, cf)
    


def createJ2CResourceAdapter(scopePath, raNode):
    if raNode.attributes.has_key("type") and raNode.attributes["type"].value == "SIBus":
        scope = AdminConfig.getid(scopePath)
        for cfNode in getChildElements(raNode, "J2CConnectionFactory"):
            sibCfNode = getChild(cfNode, "SIBJMSConnectionFactory")
            if(sibCfNode):
                createSIBJMSConnectionFactory(scope, cfNode, sibCfNode)
        for adminObjectNode in getChildElements(raNode, "J2CAdminObject"):
            sibDestinationNode = getChild(adminObjectNode, "SIBDestination")
            if sibDestinationNode:
                createSIBQueue(scope, scopePath, adminObjectNode, sibDestinationNode)
        
def createJmsResources(scopePath, jmsProviderNode):
    jmsProviderName = jmsProviderNode.attributes["name"].value       
    jmsProvider = AdminConfig.getid(scopePath + "JMSProvider:%s/" % jmsProviderName)
    for configType in ["MQQueueConnectionFactory", "MQQueue", "WASQueueConnectionFactory", "WASQueue"]:
        for configNode in getChildElements(jmsProviderNode, configType):
            configName = configNode.attributes["name"].value
            attr = attributesToAArray(configNode, lambda a: a.name != "template")
            if configNode.attributes.has_key("template"):
                templateName = configNode.attributes["template"].value
                print "AdminConfig.createUsingTemplate '%s' on '%s' using template %s" % (configName, jmsProviderName, templateName)
                template = AdminConfig.listTemplates(configType, templateName).splitlines()[0]
                configObj = AdminConfig.createUsingTemplate(configType, jmsProvider, attr, template)
            else:
                print "AdminConfig.create '%s' on '%s'" % (configName, jmsProviderName)
                configObj = AdminConfig.create(configType, jmsProvider, attr)

            if getChild(configNode, "Attributes"):
                modifyAttributes(configNode, configObj)
         
def createCacheInstances(scopePath, cacheProviderNode):        
    cacheProvider = wsadminToList(AdminConfig.getid('%sCacheProvider:/' % scopePath))[0]
    for cacheNode in getChildElements(cacheProviderNode, "*"):
        cacheProperties = attributesToAArray(cacheNode)
        print "Creating %s %s" % (cacheNode.nodeName, cacheProperties)
        cacheId = AdminConfig.create(cacheNode.nodeName, cacheProvider, cacheProperties)
        if getChild(cacheNode, "Attributes"):
            modifyAttributes(cacheNode, cacheId)

def createGeneric(scope, genericGroupNode):
    for genericNode in getChildElements(genericGroupNode, "*"):
        print "Creating %s" % genericNode.nodeName
        genericId = AdminConfig.create(genericNode.nodeName, scope, attributesToAArray(genericNode))
        if getChild(genericNode, "Attributes"):
            modifyAttributes(genericNode, genericId)

def updateVariableMap(scopePath, scope, variableMapNode):
    variableMap = wsadminToList(AdminConfig.getid('%sVariableMap:/' % scopePath))[0]
    for variableEntryNode in getChildElements(variableMapNode, "VariableSubstitutionEntry"):
        symbolicName = variableEntryNode.attributes['symbolicName'].value
        value = variableEntryNode.attributes['value'].value
        existing = 0
        for existingVariable in wsadminToList(AdminConfig.showAttribute(variableMap, 'entries')):
            existingSymbolicName = AdminConfig.showAttribute(existingVariable, 'symbolicName')
            if symbolicName == existingSymbolicName:
                print 'updating VariableSubstitutionEntry ' + symbolicName
                AdminConfig.modify(existingVariable, [['value', value]])
                existing = 1
        if not existing:            
            print 'creating VariableSubstitutionEntry ' + symbolicName
            AdminConfig.create('VariableSubstitutionEntry', variableMap, [['symbolicName', symbolicName], ['value', value]])
    

def createResources(scopePath, scopeString, resourcesNode):
    scope = AdminConfig.getid(scopePath)
    for nameBindingsNode in getChildElements(resourcesNode, "NameBindings"):
        createGeneric(scope, nameBindingsNode)
    
    for sharedLibrariesNode in getChildElements(resourcesNode, "SharedLibraries"):
        createGeneric(scope, sharedLibrariesNode)
    
    for variableMapNode in getChildElements(resourcesNode, "VariableMap"):
        updateVariableMap(scopePath, scope, variableMapNode)
    
    for jdbcProviderNode in getChildElements(resourcesNode, "JDBCProvider"):
        createDataSources(scopeString, scopePath, jdbcProviderNode)
    
    for mailProviderNode in getChildElements(resourcesNode, "MailProvider"):
        createMailSessions(scopePath, mailProviderNode)
    
    for virtualHostNode in getChildElements(resourcesNode, "VirtualHost"):
        createVirtualHosts(scopePath, virtualHostNode)
    
    for urlProviderNode in getChildElements(resourcesNode, "URLProvider"):
        createURLs(scopePath, urlProviderNode)
    
    for wmProviderNode in getChildElements(resourcesNode, "WorkManagerProvider"):
        createWorkManagers(scopePath, wmProviderNode)
    
    for cacheProviderNode in getChildElements(resourcesNode, "CacheProvider"):
        createCacheInstances(scopePath, cacheProviderNode)
    
    for drdNode in getChildElements(resourcesNode, "DataReplicationDomain"):
        createDataReplicationDomain(scope, drdNode)

    for jmsProviderNode in getChildElements(resourcesNode, "JMSProvider"):
        createJmsResources(scopePath, jmsProviderNode)
    
    for sibusNode in getChildElements(resourcesNode, "SIBus"):
        createSIBus(sibusNode)

    for sibMeNode in getChildElements(resourcesNode, "SIBMessagingEngine"):
        createSIBMessagingEngine(scopeString, scope, sibMeNode)

    for raNode in getChildElements(resourcesNode, "J2CResourceAdapter"):
        createJ2CResourceAdapter(scopePath, raNode)

def modifyServices(configNode, scope):
    for serviceNode in getChildElements(configNode, "Services/*"):
        if serviceNode.nodeName == 'Chain':
            chainName = serviceNode.attributes['name'].value
            chains = wsadminToList(AdminConfig.list(serviceNode.nodeName, scope))
            for chain in chains:
                if chainName == AdminConfig.showAttribute(chain, 'name'):
                    print "Config %s" % chainName
                    AdminConfig.modify(chain, [['enable', serviceNode.attributes['enable'].value]])
        else:
            service = AdminConfig.list(serviceNode.nodeName, scope)
            print "Config %s" % service
            modifyAttributes(serviceNode, service)

def refreshAndSync(cellName, clusterName, nodeNames):
    clusterMgr = AdminControl.completeObjectName('type=ClusterMgr,cell=' + cellName + ',*')
    if len(clusterMgr) == 0:
        print 'Error -- clusterMgr MBean not found for cell ' + cellName
        return
    
    AdminControl.invoke(clusterMgr, 'retrieveClusters')
    cluster = AdminControl.completeObjectName('type=Cluster,name=' + clusterName + ',*')
    print 'Invoking start for cluster ' + cluster
    AdminControl.invoke(cluster, 'start')
    for nodeName in nodeNames:
        print 'Invoking sync for node ' + nodeName
        nodeSync = AdminControl.completeObjectName('type=NodeSync,node=' + nodeName + ',*')
        isNodeSynchronized = AdminControl.invoke(nodeSync, 'isNodeSynchronized')
        if not isNodeSynchronized:
            AdminControl.invoke(nodeSync, 'sync')    
        else:
            print 'Node was already synchronized.'
        
    print 'Done with synchronization.'

def createSecurityConfig(security, securityNode):
    for securityConfigNode in getChildElements(securityNode, "*"):
        AdminConfig.create(securityConfigNode.nodeName, security, attributesToAArray(securityConfigNode))

def createCellConfig(cellConfigNode, cellName):
    securityNode = getChild(cellConfigNode, "Security")
    if securityNode:
        security = AdminConfig.getid('/Cell:' + cellName + '/Security:/')            
        createSecurityConfig(security, securityNode)
    resourcesNode = getChild(cellConfigNode, "Resources")
    if resourcesNode:
        cellPath = "/Cell:%s/" % cellName
        cellScope = "Cell=%s" % cellName
        createResources(cellPath, cellScope, resourcesNode)
                    
def createNodeConfig(nodeConfigNode):
    nodeName = nodeConfigNode.attributes['name'].value
    resourcesNode = getChild(nodeConfigNode, "Resources")
    if resourcesNode:
        nodePath = "/Node:%s/" % nodeName
        nodeScope = "Cell=%s" % nodeName
        createResources(nodePath, nodeScope, resourcesNode)
                    
def createCluster(clusterNode, cellName):
    cellConfigNode = getChild(clusterNode, "CellConfig")
    if cellConfigNode:
        createCellConfig(cellConfigNode, cellName)
    
    for nodeConfigNode in getChildElements(clusterNode, "NodeConfig"):
        createNodeConfig(nodeConfigNode)
    

    clusterName = clusterNode.attributes['name'].value

    nodesNodeList = getChildElements(clusterNode, 'Node')
    if len(nodesNodeList) > 0:
        clusterId, serverIds, nodeNames = createClusterMembers(clusterName, nodesNodeList, cellName)
        for nodesNode in nodesNodeList:
            nodeName = nodesNode.attributes["name"].value
            for serverNode in getChildElements(nodesNode, "Server"):
                serverName = serverNode.attributes["name"].value
                for serverPortNode in getChildElements(serverNode, "ServerPort"):
                    modifyServerPorts(nodeName, serverName, serverPortNode)
    else:
        clusterId = AdminConfig.getid('/ServerCluster:%s/' % clusterName)
        serverIds, nodeNames = getClusterMembers(clusterId)

    clusterConfigNode = getChild(clusterNode, "ClusterConfig")
    if clusterConfigNode:
        resourcesNode = getChild(clusterConfigNode, "Resources")
        if resourcesNode:
            clusterScope = "Cluster=%s" % clusterName
            clusterPath = "/ServerCluster:%s/" % clusterName
            createResources(clusterPath, clusterScope, resourcesNode)
        modifyServices(clusterConfigNode, clusterId)
        modifyAttributes(clusterConfigNode, clusterId)
    
    for serverConfigNode in getChildElements(clusterNode, "ServerConfig"):
        if serverConfigNode.getAttributeNode("match"):
            match = sre.compile(serverConfigNode.attributes["match"].value)
        else:
            match = sre.compile(".*")
        for serverItem in serverIds:
            if match.match(serverItem["server"]):
                print "Applying ServerConfig to " + serverItem["server"]
                serverId = serverItem["serverId"]
                modifyServices(serverConfigNode, serverId)
                modifyAttributes(serverConfigNode, serverId)
                
                resourcesNode = getChild(serverConfigNode, "Resources")
                if resourcesNode:
                    serverScope = "Node=%(node)s,Server=%(server)s" % serverItem
                    serverPath = "/Node:%(node)s/Server:%(server)s/" % serverItem
                    createResources(serverPath, serverScope, resourcesNode)    
                    
    print "Saving Config..."
    AdminConfig.save()                    
    print "Config saved."
    print "Refresh and sync..."
    refreshAndSync(cellName, clusterName, nodeNames)
        

impl = XercesDomImplementation()
dom = impl.buildDocumentFile(sys.argv[-1])

cellName = AdminControl.getCell()

documentNode = dom.documentElement
print("=======> createServer.py v1.3.1 creating %s on cell %s" % (documentNode.nodeName, cellName))
if documentNode.nodeName == "ServerCluster":
    createCluster(documentNode, cellName)
    
elif documentNode.nodeName == "CellConfig":
    createCellConfig(documentNode, cellName)
    print "Saving Config..."
    AdminConfig.save()                    
    print "Config saved."
    
elif documentNode.nodeName == "NodeConfig":
    createNodeConfig(documentNode)
    print "Saving Config..."
    AdminConfig.save()                    
    print "Config saved."
    
elif documentNode.nodeName == "Cell":
    cellConfigNode = getChild(documentNode, "CellConfig")
    if cellConfigNode:
        createCellConfig(cellConfigNode, cellName)
        print "Saving Config ..."
        AdminConfig.save()                    
        print "Config saved."
    
    for nodeConfigNode in getChildElements(documentNode, "NodeConfig"):
        createNodeConfig(nodeConfigNode)
        print "Saving Config..."
        AdminConfig.save()                    
        print "Config saved."
        
    for clusterNode in getChildElements(documentNode, "ServerCluster"):
        createCluster(clusterNode, cellName)

