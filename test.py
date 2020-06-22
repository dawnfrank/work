# coding: utf-8

import os
import json
import subprocess

SYSTEM_PATH = r"C:\Windows\System32"
PROJECT_PATH = "D:/Haroopad"
DUMPBIN_DIR = r"C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Tools\MSVC\14.26.28801\bin\Hostx64\x64"
DEPENDENTS_DATA = "./denpendents_data.json"

def Execute(cmdStr):
    p = subprocess.Popen(cmdStr, shell = True,stdin=subprocess.PIPE,stdout=subprocess.PIPE,cwd=DUMPBIN_DIR)
    return p.communicate()

def GetProjDlls():
    projDlls = []
    for filename in os.listdir(PROJECT_PATH):
        if filename.endswith("dll"):
            projDll = "%s/%s"%(PROJECT_PATH,filename)
            projDlls.append(projDll)
    return projDlls

def GetDependencyDLLs(projDll):
    cmdStr = "dumpbin /dependents %s" % projDll
    resTxt = Execute(cmdStr)[0]
    resTxt = resTxt.decode("gbk")
    dependencyDllList = []
    start = False
    for txt in resTxt.split("\n"):
        if "Image has the following dependencies" in txt:
            start=True
        if not start:
            continue

        txt = txt.replace(" ", "")
        txt = txt.replace("\r", "")
        if txt.endswith("dll"):
            dependencyDllList.append(txt)
    return dependencyDllList

def CheckDllExists(projDll,dependencyDllList):
    for dependencyDll in dependencyDllList:
        projDllPath = "%s/%s"%(PROJECT_PATH,dependencyDll)
        if os.path.exists(projDllPath):
            continue
        sysDllPath = "%s/%s"%(SYSTEM_PATH,dependencyDll)
        if os.path.exists(sysDllPath):
            continue
        print("%s缺少依赖%s"%(projDll,dependencyDll))

def CheckDllChange(newDllSet):
    if not os.path.exists(DEPENDENTS_DATA):
        return
    oldDllSet = set(JsonLoad(DEPENDENTS_DATA))
    for dependencyDll in newDllSet-oldDllSet:
        print("新增依赖%s"%dependencyDll)

def JsomDump(dependencyList):
    with open(DEPENDENTS_DATA,"w") as f:
        json.dump(dependencyList,f)

def JsonLoad(path):
    with open(path,"r") as f:
        return json.load(f)

if __name__ == "__main__":
    projDlls = GetProjDlls()
    dependencySet = set()
    for projDll in projDlls:
        dependencyDllList = GetDependencyDLLs(projDll)
        CheckDllExists(projDll,dependencyDllList)
        dependencySet.update(dependencyDllList)
    CheckDllChange(dependencySet)
    JsomDump(list(dependencySet))
