from websphere.getApplications import getApplications
from websphere.application import readWebPage
from websphere.sgml import extractSgmlData


import sys


def testUrls(applicationModels):
    for applicationModel in applicationModels:
        for module in applicationModel.modules:
            for target in module.targets:
                for test in target.tests:
                    print "TRY URL FOR %s (%s): %s"%(applicationModel.name, module.name, test.url)
                    lines, cookiePath = readWebPage(test.url)
                    if (lines==None or len(lines) == 0):
                        print "-> FAILED CONNECT FOR: %s"%(test.url)
                    else:
                        found = 0
                        for line in lines:
                            sgmlData = " ".join(extractSgmlData(line))
                            if sgmlData.find("Version") >= 0 or sgmlData.find("version") >= 0:
                                print "-> SUCCESS, New Version:%s, Current %s" %(applicationModel.version, sgmlData)
                                found = 1
                        if found == 0:
                            print "-> FAILED, no version found in: %s"%(test.url)
                        if cookiePath:
                            print "-> CookiePath=%s" % cookiePath

distDir = ""
files = "/*.xml"
if len(sys.argv) > 0:
    param1 = sys.argv[0]
    param1 = param1[len(param1)-3:].lower()
    if(param1==".py" or param1==".jy"):
        if len(sys.argv) > 1:
            distDir=sys.argv[1]
        if len(sys.argv) > 2:
            files=sys.argv[2]
    else:
        distDir=sys.argv[0]
        if len(sys.argv) > 1:
            files=sys.argv[1]

applicationModels = getApplications(distDir, files)
testUrls(applicationModels)