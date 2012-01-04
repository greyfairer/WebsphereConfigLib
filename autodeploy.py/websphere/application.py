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
# 2.0 (10feb2006) initial Jython version, corrected Start/StopApplicationOnNodesAndServers
# 1.3 (22apr2005) additional socket exception checks, fixed GET HTTP/1.1
# 1.2 (14jan2005) fixed startApp returns if exception, does not checkIfRunning
# 1.2 (14jan2005) fixed testApp index into testURLs and testResponses
# 1.1 (17nov2004) initial shipped version
#
from websphere.Definitions import false, true, wsadminToList
from log.log import fail, INFO_, log, MAJOR_, VERBOSE_, ERROR_, DEBUG_, WARNING_,\
    highlight
from websphere import WebSphere
from websphere.server.server import sleepDelay
from websphere.sgml import extractSgmlData
import sys
import os
from java.net import URL
from java.io import BufferedReader, InputStreamReader, IOException

def PreValidateApplicationsExist ( applicationModels ):
        for applicationModel in applicationModels:
                appExists = checkIfAppExists(applicationModel )
                if (appExists):
                        log(INFO_, "PreValidateApplicationsExist OK applicationModel="+`applicationModel` )
                else:
                        fail("PreValidateApplicationsPresent: MISSING application="+applicationModel.name )
                #endElse
        #endFor
#endDef

def PreValidateApplicationsAbsent ( applicationModels ):
        for applicationModel in applicationModels:
                appExists = checkIfAppExists(applicationModel )
                if (appExists):
                        fail("PreValidateApplicationsAbsent: EXISTING application="+applicationModel.name )
                else:
                        log(INFO_, "PreValidateApplicationsAbsent: OK applicationModel="+`applicationModel` )
                #endElse
        #endFor
#endDef

def validateApplication ( applicationModel ):
        log(INFO_, "validateApplication "+applicationModel.name+" ..." )
        WebSphere.AdminConfig.validate(WebSphere.AdminConfig.getid("/Deployment:"+applicationModel.name+"/" ) )
#endDef

def listApplications (  ):
        log(INFO_, "ListApplications:" )
        apps = WebSphere.AdminApp.list( )
        apps = wsadminToList(apps) # running on windows, target is linux (different SEPARATOR)
        for app in apps:
                log(INFO_, "  "+app )
        #endFor
        log(VERBOSE_, "ListApplications: DONE." )
#endDef

def checkIfAppExists ( applicationModel ):
    return checkIfAppNameExists(applicationModel.name)

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

def StartApplication ( applicationModel, nodeName, serverName ):
        log(INFO_, "StartApplication: applicationModel="+applicationModel.name+" nodeName="+nodeName+" serverName="+serverName+" ..." )
        appMgrID = WebSphere.AdminControl.queryNames("type=ApplicationManager,node="+nodeName+",process="+serverName+",*" )
        length = len(appMgrID)
        log(DEBUG_, "StartApplication: appMgrID.length="+`length`+" appMgrID="+appMgrID )
        if (length >= 1):
                log(VERBOSE_, "StartApplication: starting "+applicationModel.name+"  ..." )
                try:
                        _excp_ = 0
                        started = WebSphere.AdminControl.invoke(appMgrID, "startApplication", applicationModel.name )
                except:
                        _type_, _value_, _tbck_ = sys.exc_info()
                        _excp_ = 1
                #endTry
                temp = _excp_
                if (temp > 0):
                        log(WARNING_, "StartApplication: Exception trying to start "+applicationModel.name+" "+nodeName+" "+serverName )
                        return
                else:
                        if (len(started) > 0):
                                log(INFO_, started )
                        #endIf
                #endElse
        else:
                log(ERROR_, "StartApplication: appMgr ERROR, NOT ACCESSABLE, cannot start "+applicationModel.name )
        #endElse
        checkApplicationRunning(nodeName, serverName, applicationModel )
        log(VERBOSE_, "StartApplication: DONE." )
#endDef

def StopApplication ( applicationModel, nodeName, serverName ):
        log(INFO_, "StopApplication: applicationModel="+applicationModel.name+" nodeName="+nodeName+" serverName="+serverName+" ..." )
        appMgrID = WebSphere.AdminControl.queryNames("type=ApplicationManager,node="+nodeName+",process="+serverName+",*" )
        length = len(appMgrID)
        log(VERBOSE_, "StopApplication: appMgrID.length="+`length`+" appMgrID="+appMgrID )
        if (length >= 1):
                log(VERBOSE_, "StopApplication: stopping "+applicationModel.name+"  ..." )
                stopped = ""
                try:
                        _excp_ = 0
                        stopped = WebSphere.AdminControl.invoke(appMgrID, "stopApplication", applicationModel.name )
                except:
                        _type_, _value_, _tbck_ = sys.exc_info()
                        _excp_ = 1
                #endTry
                temp = _excp_
                if (temp > 0):
                        log(WARNING_, "StopApplication: Exception trying to stop "+applicationModel.name+" "+nodeName+" "+serverName )
                else:
                        if (len(stopped) > 0):
                                log(VERBOSE_, stopped )
                        #endIf
                #endElse
        else:
                log(ERROR_, "StopApplication: appMgr ERROR, NOT ACCESSABLE, cannot stop "+applicationModel.name )
        #endElse
        log(VERBOSE_, "StopApplication: DONE." )
#endDef

def testApplication (applicationModels):
    for applicationModel in applicationModels:
        confirmed = true
        for module in applicationModel.modules:
            cookiePath=None
            for attribute in module.attributes:
                if attribute.name=="WebModuleConfig.sessionManagement.defaultCookieSettings.path":
                    cookiePath=attribute.value
            for target in module.targets:
                for test in target.tests:
                    result = testUrl(test.url, test.response, cookiePath)
                    if not result:
                        confirmed = false
        if confirmed:
            if applicationModel.configFile.endswith('.done'):
                os.rename(applicationModel.configFile, applicationModel.configFile[:-5]+'.confirmed') 
            elif not applicationModel.configFile.endswith('.confirmed'):
                os.rename(applicationModel.configFile, applicationModel.configFile+'.confirmed') 
                    
def testUrl(url, response, cookiePath):                    
    log(VERBOSE_, "testApplication: testURL="+url+"  testResponse="+response )
    
    try:
        lines,realCookiePath = readWebPage(url )
        
        if (lines==None or len(lines) == 0):
            log(ERROR_, "testApplication: FAILED CONNECT: url="+url )
            return false
        
        found = false
        for line in lines:
                if (line.find(response) >= 0):
                        found = true
                #endIf
        #endFor
        if (found):
            log(INFO_, "testApplication: PASSED: url="+url+"  contained="+response )
        else:
            log(ERROR_, "testApplication: WRONG VERSION: url="+url+"  expectedResponse="+response )
            sgmlData = extractSgmlData(lines)
            for line in sgmlData:
                log(ERROR_,  line)
        if cookiePath and cookiePath != realCookiePath:
            log(ERROR_, "testApplication: WRONG CookiePath: "+realCookiePath+"  expected="+cookiePath )
            
        return found
        

    except IOException, e:
        log(ERROR_, "testApplication: FAILED CONNECT: url="+url+"  error="+e.getMessage())
        return false

def readWebPage ( webpageURL ):
    webpageURL = webpageURL.strip( )
    log(VERBOSE_, "readWebpage webpageURL="+webpageURL )
    url = URL(webpageURL)
    conn = url.openConnection()
    conn.setConnectTimeout(30000)
    conn.setReadTimeout(10000)
    conn.connect()
    responseCode = conn.getResponseCode()
    cookie = conn.getHeaderField("Set-Cookie")    
    cookiePath=None
    pathDiscr=" Path="
    if cookie and cookie.find(pathDiscr)>0:
        cookiePath=cookie[cookie.index(pathDiscr)+len(pathDiscr):]
    respLines = []
    if(responseCode >=400):
        log(ERROR_,"HTTP ERROR "+`responseCode`+": "+`conn.getResponseMessage()` )
    else:
        log(VERBOSE_,"WebPageResponse status="+`responseCode`+" reason="+`conn.getResponseMessage()` )
        #log(DEBUG_,"WebPageResponse resp="+`resp` )
        reader = BufferedReader(InputStreamReader(conn.getInputStream()))
        inputLine = reader.readLine()
        while (inputLine != None):
            respLines.append(inputLine)
            inputLine = reader.readLine()
        
        reader.close()
    return respLines, cookiePath
#endDef

def StopApplicationOnNodesAndServers ( applicationModel, uniqueNodeServerPairs ):
        log(MAJOR_, "StopApplicationOnNodesAndServers: applicationModel="+applicationModel.name+" nodeServerPairs="+`uniqueNodeServerPairs`+"..." )
        if (len(uniqueNodeServerPairs) == 0):
                fail(ERROR_, "StopApplicationOnNodesAndServers : No nodes/servers/clusters specified" )
        #endIf
        for nodeServer in uniqueNodeServerPairs:
                nodeName = nodeServer.nodeName
                serverName = nodeServer.serverName
                StopApplication(applicationModel, nodeName, serverName )
        #endFor
        highlight(MAJOR_, "StopApplicationOnNodesAndServers  DONE." )
#endDef

def StartApplicationOnNodesAndServers ( applicationModel, uniqueNodeServerPairs ):
        log(INFO_, "" )
        log(MAJOR_, "StartApplicationOnNodesAndServers: applicationModel="+applicationModel.name+" nodeServerPairs="+`uniqueNodeServerPairs`+"..." )
        if (len(uniqueNodeServerPairs) == 0):
                fail(ERROR_, "StartApplicationOnNodesAndServers : No nodes/servers/clusters specified" )
        #endIf
        for nodeServer in uniqueNodeServerPairs:
                nodeName = nodeServer.nodeName
                serverName = nodeServer.serverName
                StartApplication(applicationModel, nodeName, serverName )
        #endFor
        highlight(MAJOR_, "StartApplicationOnNodesAndServers  DONE." )
#endDef

def checkApplicationRunning ( nodeName, serverName, applicationModel ):


        log(VERBOSE_, "checkApplicationRunning: "+nodeName+" "+serverName+" "+applicationModel.name )
        appID = ""
        try:
                _excp_ = 0
                appID = WebSphere.AdminControl.completeObjectName("type=Application,node="+nodeName+",Server="+serverName+",name="+applicationModel.name+",*" )
        except:
                _type_, _value_, _tbck_ = sys.exc_info()
                _excp_ = 1
        #endTry
        temp = _excp_
        if (temp > 0):
                log(WARNING_, "checkApplicationRunning: Exception trying to getID for "+applicationModel.name+" "+nodeName+" "+serverName )
        #endIf
        length = len(appID)
        log(DEBUG_, "checkApplicationRunning: appID.length="+`length` )

        retries = 0
        while (( retries < 20 )  and ( length == 0 ) ):
                retries = retries+1
                log(INFO_, "checkApplicationRunning: not yet started, "+applicationModel.name+" "+nodeName+" "+serverName+", retries="+`retries`+" ..." )
                try:
                        _excp_ = 0
                        sleepDelay(10 )
                        appID = WebSphere.AdminControl.completeObjectName("type=Application,node="+nodeName+",Server="+serverName+",name="+applicationModel.name+",*" )
                        if (len(appID) == 0):
                                appExists = checkIfAppExists(applicationModel )
                                if (appExists):
                                        pass
                                else:
                                        log(ERROR_, "checkApplicationRunning: "+applicationModel.name+" is NOT INSTALLED." )
                                        return
                                #endElse
                        #endIf
                except:
                        _type_, _value_, _tbck_ = sys.exc_info()
                        _excp_ = 1
                #endTry
                temp = _excp_
                if (temp > 0):
                        log(WARNING_, "checkApplicationRunning: Exception trying to getID for "+applicationModel.name+" "+nodeName+" "+serverName )
                #endIf
                length = len(appID)
                log(DEBUG_, "checkApplicationRunning: temp="+`temp`+" appID="+appID+" ..." )
        #endWhile
        if (retries > 0):
                log(INFO_, "checkApplicationRunning: "+nodeName+" "+serverName+" "+applicationModel.name+" had slow start, status retries="+`retries` )
        #endIf

        if (length > 0):
                log(INFO_, "checkApplicationRunning: "+applicationModel.name+" is STARTED." )
        else:
                log(ERROR_, "checkApplicationRunning: "+applicationModel.name+" "+nodeName+" "+serverName+" DID NOT START." )
        #endElse
#endDef
