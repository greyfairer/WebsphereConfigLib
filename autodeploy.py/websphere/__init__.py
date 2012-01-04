from com.ibm.ws.scripting import AdminAppClient, AdminConfigClient, AdminControlClient
from log.log import fail, log, MAJOR_, INFO_, VERBOSE_
from websphere.Definitions import Globals
import sys

class WebSphere:
    AdminControl = AdminControlClient.getInstance()
    AdminApp = AdminAppClient.getInstance()
    AdminConfig = AdminConfigClient.getInstance()

Globals.wsadminCell = WebSphere.AdminControl.getCell()

def printInformation():
    wsadminSvr = WebSphere.AdminControl.queryNames("node=" + WebSphere.AdminControl.getNode() + ",type=Server,*")
    v = wsadminSvr.find(",version=")
    serverVers = wsadminSvr[v + 9:]
    v = serverVers.find(",")
    serverVers = serverVers[0:v]
    wsadminSvrId = WebSphere.AdminControl.getConfigId(wsadminSvr)
    wsadminType = WebSphere.AdminConfig.showAttribute(wsadminSvrId, "serverType")
    wsadminVers = WebSphere.AdminControl.getAttribute(wsadminSvr, "platformVersion")
    wsadminConn = WebSphere.AdminControl.getType()
    wsadminServer = WebSphere.AdminControl.getAttribute(wsadminSvr, "name")
    wsadminNode = WebSphere.AdminControl.getNode()

    wsadminHost = WebSphere.AdminControl.getHost()
    wsadminPort = WebSphere.AdminControl.getPort()
    if wsadminType != "DEPLOYMENT_MANAGER":
        fail(" currently only tested for AppServers connected to NetworkDeployment DeploymentManager")
        #endIf

    if wsadminConn != "SOAP":
        fail(" currently only tested for AppServers connected using type=SOAP")
        #endIf

    log(MAJOR_, ": WSADMIN: AdminType=" + wsadminType)
    log(MAJOR_, ": WSADMIN: AdminVers=" + wsadminVers)
    log(MAJOR_, ": WSADMIN: ServrVers=" + serverVers)
    log(MAJOR_, ": WSADMIN: AdminCell=" + Globals.wsadminCell)
    log(MAJOR_, ": WSADMIN: AdminNode=" + wsadminNode)
    log(MAJOR_, ": WSADMIN: AdminConn=" + wsadminConn)
    log(MAJOR_, ": WSADMIN: AdminHost=" + wsadminHost)
    log(MAJOR_, ": WSADMIN: AdminSevr=" + wsadminServer)
    log(MAJOR_, ": WSADMIN: AdminPort=" + wsadminPort)
    log(VERBOSE_, "JYTHON vers=" + sys.version[0:3])
    log(INFO_, "")
