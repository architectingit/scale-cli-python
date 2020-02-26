import requests
from requests.auth import HTTPBasicAuth
import urllib3
import argparse
from datetime import datetime 
import os

def error_strings(argument):
  switcher = {
    401: "user not authorised or username/password incorrect",
    404: "API URL not found on the cluster"
  }  
  return switcher.get(argument)

helpText = "List virtual machines on Scale Cluster."
codeVersion = "0.2.0"
argParams = argparse.ArgumentParser(description = helpText)
argParams.add_argument("-V","--version",help="display version and exit",action="store_true")
argParams.add_argument("-C","--cluster",help="specify cluster DNS name or IP address",action="store")
argParams.add_argument("-U","--user",help="user name credentials",action="store")
argParams.add_argument("-P","--password",help="password credentials",action="store")
argList = argParams.parse_args()
if argList.version:
  print ("GetVMs " + codeVersion)
  exit()
clusterURL = "https://172.17.8.1/"
if "SCCLUSTER" in os.environ: 
  clusterURL = "https://" +  os.environ["SCCLUSTER"] + "/"
if argList.cluster:
  clusterURL = "https://" + argList.cluster + "/"
restVersion = "rest/v1/VirDomain"
if not argList.user and argList.password:
  print("Error: password specified without user name")
  exit()
if argList.user and not argList.password:
  print("Error: user name specified without password")
  exit() 
apiUser = "apiuser"
apiPassword = "P@ssword"  
if "SCUSER" in os.environ: 
  apiUser = os.environ["SCUSER"]
if "SCPASSWORD" in os.environ:  
  apiPassword = os.environ["SCPASSWORD"]
if argList.user:
  apiUser = argList.user
  apiPassword = argList.password  
apiBasicAuth = HTTPBasicAuth(apiUser,apiPassword)

# import libraries for HTTP calls and URL exception processing
#
# disable warnings for insecure certificate
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
#
# call API with fixed basic auth & ignore no certificate
try:
  resp = requests.get(clusterURL + restVersion, verify=False, auth = apiBasicAuth, timeout=5) 
except requests.exceptions.Timeout as e:
  print("Error: timeout waiting for response from cluster")  
  exit()     
  
#
# check the response - < 400 is good, otherwise error out
#
if resp.status_code < 400:
  print("{0:35s}{1:35s}{2:20s}{3:8s}{4:12s}{5:25s}{6:15s}{7:10s}".format("VM Name","Description","State (Desired)","CPUs","Memory (MB)","Operating System","Machine Type","Create Date"))
  for vms in resp.json():
    print("{0:35s}{1:35s}{2:20s}{3:<8d}{4:<12g}{5:25s}{6:15s}{7:10}".format(vms["name"],vms["description"],vms["state"]+" ("+vms["desiredDisposition"]+")",vms["numVCPU"],vms["mem"]/1048576,vms["operatingSystem"],vms["machineType"],datetime.fromtimestamp(vms["created"]).strftime("%Y-%m-%d %H:%M:%S")))
else: 
  print("Error: {} - {}".format(resp.status_code,error_strings(resp.status_code)))
