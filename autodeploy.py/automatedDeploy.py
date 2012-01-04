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
# 3.3 (19sep2008) updated to allow update without cluster/server info, reusing existing info
# 3.1 (08may2007) changed hard-coded version number to 3.1 (no code changes)
# 3.1 (08may2007) added load of getScripts.py
# 2.0 (10feb2006) initial Jython version, several code changes (envar handling)
# 1.3 (22apr2005) removed DEPLOY_WAS, optional DistDir, uses getEnvars
# 1.2 (14jan2005) restructured (future: will read DEPLOY_XXXX envars or invocation parameters)
# 1.1 (17nov2004) initial shipped version
# $ChangeLog$
from log.log import LogConfig, debugHighlight, DEBUG_, INFO_, WARNING_, MAJOR_, ERROR_, highlight, log
from websphere import printInformation
from websphere.Definitions import Globals, convertToJaclPath
from websphere.deploy.deploy import deploy


version= "4.0 $Revision: 480 $"
LogConfig.syslogTag="deploy:WebSphere"

import sys
print "@@ sys.path="+`sys.path`
print "@@ sys.prefix="+`sys.prefix`
#print "registry_all="+`sys.registry`


debugHighlight(INFO_, "sys.argv[0]="+`sys.argv[0]`)

print ""
print ""
SCRIPTNAME = "automatedDeploy.py - Version "+version
highlight(MAJOR_, "running "+SCRIPTNAME )
print ""

wasRoot = Globals.wasRoot
log(INFO_, "envar was.install.root="+wasRoot )

action = ""
failOnError = ""
distDir = ""

base = 0
if(len(sys.argv)>0):
        param1 = sys.argv[0]
        param1 = param1[len(param1)-3:].lower()
        if(param1==".py" or param1==".jy"):
                base = 1
        #endIf
#endIf
if ( len(sys.argv) > (base+0) ):
        action = sys.argv[base+0]
        if (len(sys.argv) > (base+1) ):
                        failOnError = sys.argv[(base+1)]
                        if (len(sys.argv) > (base+2) ):
                                distDir = sys.argv[(base+2)]
                                if (len(sys.argv) > (base+3) ):
                                        extra = sys.argv[(base+3)]
                                        log(ERROR_, SCRIPTNAME+": only accepts 3 parameters, ignoring "+extra )
                                #endIf
                        #endIf
                #endIf
        #endIf
elif (len(action) == 0):
        proc_result = SCRIPTNAME+" requires 1-3 params (action failonerror distDir)"
        log(ERROR_, proc_result )
        sys.exit( proc_result)
#endIf
if (len(action) <= 0):
        action = "confirm"
#endIf
if (len(failOnError) <= 0):
        failOnError = "true"
#endIf
if (len(distDir) <= 0):
        distDir = "./dist"
#endIf
distDir = convertToJaclPath(distDir )

printInformation()
log(MAJOR_, ": invoking deploy " + action + " " + failOnError + " " + distDir + " " + `wasRoot`)
deploy(action, failOnError, distDir, wasRoot )

print ""
print ""
print ""
if len(LogConfig.errors) > 0:
        log(DEBUG_, "errors.length="+`len(LogConfig.errors)` )
        msgs = ""
        for msg in LogConfig.errors:
                msgs = msgs+"\n"+msg
        #endFor
        debugHighlight(ERROR_, "ERRORS during "+action+":"+msgs )
#endIf
if len(LogConfig.warnings) > 0:
        log(DEBUG_, "warnings.length="+`len(LogConfig.warnings)` )
        msgs = ""
        for msg in LogConfig.warnings:
                msgs = msgs+"\n"+msg
        #endFor
        highlight(WARNING_, "WARNINGS during "+action+":"+msgs )
#endIf
if len(LogConfig.warnings) == 0 and len(LogConfig.errors) == 0:
        highlight(MAJOR_, "No errors, no warnings during automatedDeployment (action="+action+")" )
#endIf

print ""
highlight(MAJOR_, SCRIPTNAME+" DONE."  )
print ""
print ""
