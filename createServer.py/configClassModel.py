class AdminConfigClass:
    def __init__(self, classname):
        self.classname = classname
        self.attributes = []
        self.groupName = None
    
    def withOptional(self, attributeName, configName =  None):
        attribute = AdminConfigAttribute(attributeName)
        if configName != None:
            attribute = attribute.withConfigName(configName)
        self.attributes.append(attribute)
        return self
    
    def withRequired(self, attributeName, configName =  None):
        attribute = AdminConfigAttribute(attributeName, AdminConfigAttribute.requiredAttribute)
        if configName != None:
            attribute = attribute.withConfigName(configName)
        self.attributes.append(attribute)
        return self

    def withComplex(self, attributeName, attributeClass):
        self.attributes.append(AdminConfigAttribute(attributeName, AdminConfigAttribute.complexAttribute, attributeClass ))
        return self
        
    def withList(self, attributeName, attributeClass):
        self.attributes.append(AdminConfigAttribute(attributeName, AdminConfigAttribute.listAttribute, attributeClass, parentName = None ))
        return self
    def withAttributeList(self, attributeName, attributeClass):
        self.attributes.append(AdminConfigAttribute(attributeName, AdminConfigAttribute.listAttribute, attributeClass ))
        return self
    
    def asGroup(self, groupName):
        self.groupName = groupName
        return self    
        
    def requiredAttributes(self):
        return filter(lambda attr: attr.attributeType == AdminConfigAttribute.requiredAttribute, self.attributes)
    def optionalAttributes(self):
        return filter(lambda attr: attr.attributeType == AdminConfigAttribute.optionalAttribute, self.attributes)
    def simpleAttributes(self):
        return filter(lambda attr: attr.attributeType in (AdminConfigAttribute.optionalAttribute, AdminConfigAttribute.requiredAttribute), self.attributes)
    def complexAttributes(self):
        return filter(lambda attr: attr.attributeType == AdminConfigAttribute.complexAttribute, self.attributes)
    def listAttributes(self):
        return filter(lambda attr: attr.attributeType == AdminConfigAttribute.listAttribute, self.attributes)


class AdminConfigAttribute:
    optionalAttribute = 'optionalAttribute'
    complexAttribute = 'complexAttribute'
    listAttribute = 'listAttribute'
    requiredAttribute = 'requiredAttribute'
    
    def __init__(self, attributeName, attributeType=optionalAttribute, attributeClass = None, parentName = 'Attributes'):
        self.attributeName = attributeName
        self.attributeType = attributeType
        self.attributeClass = attributeClass
        self.parentName = parentName
        self.configName = attributeName
        
    def withConfigName(self, aliasName):
        self.configName = aliasName
        return self
    