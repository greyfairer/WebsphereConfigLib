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
# 2.0 (10feb2006) initial Jython version
# 1.3 (22apr2005) moved proc getEnvar into new getEnvars.jacl
# 1.2 (14jan2005) added proc getEnvar
# 1.1 (17nov2004) initial shipped version
#

import sys
from java.lang import Runtime

DEBUG_ = 5
VERBOSE_ = 4
INFO_ = 3
MAJOR_ = 2
WARNING_ = 1
ERROR_ = 0

class LogConfig:
    logLevel = INFO_
    syslogTag = "AutoDeploy"
    syslogFacility = "local3"
    errors = []
    warnings = []


def checkErrorsWarnings( level, message ):
    if level == ERROR_:
        message = "ERROR: " + message
        LogConfig.errors.append(message)
    elif level == WARNING_:
        message = "WARNING: " + message
        LogConfig.warnings.append(message)
        #endIf
    return message

#endDef
def syslog( level, message ):
    try:
        ps = Runtime.getRuntime().exec(['logger', '-p', '%s.%s' % (LogConfig.syslogFacility, level), '-t', LogConfig.syslogTag, message])
        return ps.waitFor()
    except:
        log(INFO_, level + " " + message)
        return 0

#    return 0

def log( level, message ):
    if level <= LogConfig.logLevel:
        checkErrorsWarnings(level, message)
        if LogConfig.logLevel != DEBUG_:
            if level == ERROR_:
                print "ERROR: " + message
            elif level == WARNING_:
                print "WARNING: " + message
            else:
                print message
                #endElse
        else:
            if level == ERROR_:
                print ".E ###ERROR### " + message
            elif level == WARNING_:
                print "..W ###WARNING### " + message
            elif level == MAJOR_:
                print "...M " + message
            elif level == INFO_:
                print "....I " + message
            elif level == VERBOSE_:
                print ".....V " + message
            elif level == DEBUG_:
                print "......D " + message
            else:
                print "???????? " + message
                #endElse
                #endElse
                #endIf

#endDef

def fail( msg ):
    msg = "FAILURE: " + msg
    debugHighlight(ERROR_, msg)

#endDef

def debugHighlight( level, message ):
    message = checkErrorsWarnings(level, message)
    if level <= LogConfig.logLevel:
        ##puts ""
        print "#######################################################################"
        print message
        print "#######################################################################"
        ##puts ""
        #endIf

#endDef

def highlight( level, message ):
    message = checkErrorsWarnings(level, message)
    if level <= LogConfig.logLevel:
        print "======================================================================="
        print message
        print "======================================================================="
        #endIf

#endDef

def lowlight( level, message ):
    message = checkErrorsWarnings(level, message)
    if level <= LogConfig.logLevel:
        print "-----------------------------------------------------------------------"
        print message
        print "-----------------------------------------------------------------------"
        #endIf

#endDef
