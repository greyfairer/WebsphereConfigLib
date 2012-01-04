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
# 3.1 (08may2007) moved installOptions from getTargets
# 2.0 (10feb2006) initial Jython version,
# 2.0 (10feb2006) API: changed WebModuleName test into ModuleName
# 1.1 (17nov2004) initial shipped version
#
from websphere.Definitions import true
from websphere.attrib.showSet import setAttribute


def applySettings( applicationModel ):
    for attribute in applicationModel.attributes:
        setAttribute(applicationModel.name, "Application", attribute.name, attribute.value, applicationModel.name, true)

    for module in applicationModel.modules:
        for attribute in module.attributes:
            setAttribute(module.name, "Module", attribute.name, attribute.value, applicationModel.name, true)


#endDef
