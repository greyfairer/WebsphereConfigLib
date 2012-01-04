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
import re
import sys
from java.lang import System

global true
global false

true = 1
false = 0

def getEnvar ( envar ):
        result = System.getProperty(envar)
        try:
                _excp_ = 0
                import os
                if(result==None or result==""):
                        result = os.environ[envar]
        except:
                _type_, _value_, _tbck_ = sys.exc_info()
                _excp_ = 1
        #endTry
        temp = _excp_
        if(result==None):
                result = ""
        return result
#endDef

def convertToJaclPath ( path ):
        slash = path.find("\\")
        while (slash > 0):
                r1 = path[0:(slash-0)]
                r2 = path[(slash+1):]
                path = r1+"/"+r2
                slash = path.find("\\")
        #endWhile
        return path
#endDef
class Globals:
    nodeServerPairs = []
    uniqueNodesContainedServers = []
    nodesAutosyncs = []
    clusters = {}
    inactiveServers = []
    unclusteredNodeServerPairs = []
    appsNodesServers = []   
    wsadminCell=""
    wasRoot = convertToJaclPath(getEnvar("was.install.root" ) )


def regexp(pattern, string, flags=0):
        if(re.compile(pattern, flags).search(string)==None): return 0
        else: return 1
def regexpn(pattern, string, flags=0):
        r = re.compile(pattern, flags).subn("", string)
        return r[1]
def wsadminToList(inStr):
        outList=[]
        if (len(inStr)>0 and inStr[0]=='[' and inStr[-1]==']'):
                tmpList = inStr[1:-1].split(" ")
                rematched = []
                append = 0
                for item in tmpList:
                    if(append == 0 and item[0] == '"'):
                        rematched.append(item)
                        if(item[-1] != '"'):
                            append = 1
                    elif(append == 0):
                        rematched.append(item)
                    else: #append == 1
                        rematched[-1] = rematched[-1] + " " + item
                        if(item[-1] == '"'):
                            append = 0
                tmpList = rematched
        else:
                tmpList = inStr.split("\n")  #splits for Windows or Linux
        for item in tmpList:
                item = item.rstrip();        #removes any Windows "\r"
                if (len(item)>0):
                        outList.append(item)
        return outList
#endDef

