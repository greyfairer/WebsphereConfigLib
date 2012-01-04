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
# 3.0 (25apr2007) added support for installOptions
# 2.0 (10feb2006) initial Jython version
# 1.3 (22apr2005) API: added "appPath" as setTargets parameter
# 1.3 (22apr2005) added "update" code into proc "installAndConfigureApps"
# 1.2 (14jan2005) removed duplicated appends of testURLs and testResponses
# 1.1 (17nov2004) initial shipped version
#
from log.log import fail, INFO_, log, MAJOR_, ERROR_, highlight, WARNING_, syslog
from websphere.application import listApplications, checkIfAppExists, validateApplication
from websphere.attrib.file import applySettings
from websphere.attrib.setTargets import setTargets
from websphere.ear.ear import validateEAR, installEAR
from websphere.node.node import configSave, execScript
from websphere import WebSphere
from com.ibm.websphere.management.exception import AdminException
import os


def installAndConfigureApps ( action, distDir, wasRoot, applicationModels ):
        log(INFO_, "" )
        log(MAJOR_, "installAndConfigureApps: applicationModels="+`applicationModels`+" ..." )

        listApplications( )
        result = []

        ################ INSTALL (or UPDATE) AND CONFIGURE ##############
        for applicationModel in applicationModels:
            try:
                if(applicationModel.file.startswith("/")):
                    appPath=applicationModel.file
                else:
                    appPath = distDir+"/"+applicationModel.file
                if not validateEAR(appPath ):
                    continue

                ################ READ APP INSTALL OPTIONS (from .settings) ##############
                installOptions = ""
                for installOption in applicationModel.installOptions:
                    installOptions = installOptions + " "+installOption
                ################ INSTALL ##############
                nodeName = ""
                serverName = ""
                if (len(applicationModel.servers) > 0):
                        appNodeServerPair = applicationModel.servers[0]
                        nodeName = appNodeServerPair.nodeName
                        serverName = appNodeServerPair.serverName
                #endIf
                clusterName = ""
                if (len(applicationModel.clusters) > 0):
                        clusterName = applicationModel.clusters[0].clusterName
                #endIf
                if (action == "install"):
                        appExists = checkIfAppExists(applicationModel )
                        if (appExists):
                                msg = "application="+applicationModel.name+" EXISTS, CANNOT install with same name"
                                fail(msg )
                                highlight(ERROR_, "application="+applicationModel.name+" EXISTS, will process SETTINGS and TARGETS" )
                        else:
                                installEAR(action, appPath, applicationModel, clusterName, nodeName, serverName, installOptions )
                        #endElse
                elif (action == "update"):
                        appExists = checkIfAppExists(applicationModel )
                        if (appExists):
                                installEAR(action, appPath, applicationModel, clusterName, nodeName, serverName, installOptions )
                        else:
                                msg = "application="+applicationModel.name+" DOES NOT EXIST, will INSTALL instead of UPDATE"
                                log(WARNING_, msg)
                                installEAR("install", appPath, applicationModel, clusterName, nodeName, serverName, installOptions )
                        #endElse
                #endIf

                ################ CONFIG SETTINGS ##############
                applySettings(applicationModel )

                ################ VALIDATE INSTALLED APPLICATION ##############
                validateApplication(applicationModel )
            except AdminException, e:
                log(WARNING_, "AdminException="+e.message)
                WebSphere.AdminConfig.reset( )
                
            else:
                configSave()                
                syslog("info", "successful %s:%s:%s:%s"%(action, applicationModel.serviceCall, applicationModel.name, applicationModel.version))
                execScript(applicationModel, "afterInstall")
                os.rename(applicationModel.configFile, applicationModel.configFile+'.done')
                applicationModel.configFile = applicationModel.configFile+'.done'
                result.append(applicationModel)
        #endFor
        listApplications( )
        highlight(MAJOR_, "installAndConfigureApps DONE. (ready to distribute to nodes/servers)" )
        return result
#endDef
