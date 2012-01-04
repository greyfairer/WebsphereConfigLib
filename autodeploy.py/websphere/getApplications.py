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
# 1.1 (17nov2004) initial shipped version
#
from log.log import fail
import applicationModel
import glob
import os
import sys
import xml

def getApplications(distDir, pattern="*.xml"):
    if not os.path.isdir(distDir):
        msg = "readDistributionDirectory: ERROR: is not a directory, distDir=" + distDir
        fail(msg)
    if not os.path.exists(distDir):
        msg = "readDistributionDirectory: ERROR: does not exist, distDir=" + distDir
        fail(msg)
    files = glob.glob(distDir + "/" + pattern)
    applications = {}
    impl = xml.dom.javadom.XercesDomImplementation()
    for file in files:
        dom = impl.buildDocumentFile(file)
        model = applicationModel.parseApplication(dom)
        model.configFile = file
        applications[model.name] = model
    extrafiles = glob.glob(distDir + "/*.extraxml")
    for extrafile in extrafiles:
        extradom = impl.buildDocumentFile(extrafile)
        applicationModel.addExtra(applications, extradom)
    return applications.values()
