import sys
import os
import requests
import json
from time import sleep
from urlparse import urlparse
from os.path import splitext, basename

##############################
##### Environments
##############################

# Sandbox
# Get token url
# https://sandbox.spark.autodesk.com/api/v1/oauth/authorize?response_type=code&client_id=<your sandbox app key>
#baseURL = 'https://sandbox.spark.autodesk.com/api/v1'

# PRODUCTION
# Get token url
# https://api.spark.autodesk.com/api/v1/oauth/authorize?response_type=code&client_id=<your production app key>
baseURL = 'https://api.spark.autodesk.com/api/v1'

###### Authorization
token    = "Bearer K9bID8RRJqnxAY7U5UGLVvILsbGQ"	
#memberId = 20712118   # Sandbox
memberId = 26777559 #23043771   # Production
secondary_member_id = 20440631

def getBaseHeaders():
	return { "Authorization" : token,
        	 "X-Member-ID"   : memberId
		   }

def getSecondaryHeaders():
	return {"Authorization" : token,
	        "X-Member-ID"   : secondary_member_id
	}

def waitForTask(response):

	taskId = response.json()["id"]

	url = baseURL + "/print/tasks/" + taskId
	headers = getBaseHeaders()

	while True:
		response = requests.get(url, headers=headers)
		if not response:
			continue

		json = response.json()

		print "Progress = %f" % json["progress"]
		if json["progress"] == 1:
			print "\t taks = ", json; import sys; sys.stdout.flush()

		if json["status"] == "done" or json["status"] == "error": 
			return json["result"] if "result" in json else json

		sleep(0.1)


def getTask(taskId):

	url = baseURL + "/print/tasks/" + taskId
	headers = getBaseHeaders()

	maxIterations = 100

	response = requests.get(url, headers=headers)
	if not response:
		return null;

	json = response.json()
	return json


##############################
## File API calls
##############################
def uploadToSparkDrive(fileName):
	
	url = baseURL + "/files/upload"
 
	print "UploadToSparkDrive: ", url; sys.stdout.flush()
	headers = getBaseHeaders()

	files = {'file': open(fileName, 'rb')}

	response = requests.post(url, files=files, headers=headers)
	print "\t RESPONSE: ", response; sys.stdout.flush()

	json = response.json()
	return json["files"][0]["file_id"]


def getFileDetails(fileId):
	url = baseURL + "/files/" + fileId
	headers = getBaseHeaders()

	print "getFileDetais: ", url; sys.stdout.flush()
	payLoad = {"file_id": fileId }

	response = requests.post(url, json={}, headers=headers)
	print "\n\tRESPONSE: ", response.json(); sys.stdout.flush()

	return waitForTask(response)


##############################
## Mesh operation API calls
##############################
def importMesh(fileId, name):
	print "\n### Import mesh: /geom/meshes/import", fileId, name
	url = baseURL + "/geom/meshes/import"

	headers = getBaseHeaders()
        
	payLoad = {"file_id": fileId, "name" : name }
	#payLoad = {"file_id": fileId, "name":name, "transform": [[1,0,0,0],[0,1,0,0],[0,0,1,0]], "generate_visual": True}
	#payLoad = {"file_id": fileId, "name" : name, "file_type" : "stl" }

	response = requests.post(url, json=payLoad, headers = headers)
	print "\n\tRESPONSE: ", response.json(); sys.stdout.flush()
 
        res = waitForTask(response)
        if (res):
             return res["id"]
        else:
             return 0


def analyzeMesh( meshId ):
    print "\n### Analyze mesh: /geom/meshes/analyze %s" % meshId

    url = baseURL + "/geom/meshes/analyze"
    headers = getBaseHeaders()

    payLoad = {"id": meshId}
    response = requests.post(url, json = payLoad, headers=headers)

    print "\n\tRESPONSE: ", response.json()
    if "analyzed" in response.json().keys():
        return response.json()

    return waitForTask(response)


def repairMesh( meshId ):
    print "\n### Repair mesh: /geom/meshes/repair %s" % meshId;

    url = baseURL + "/geom/meshes/repair"
    headers = getBaseHeaders()

    payLoad = { "id": meshId, 
		"all": True, 
		"generate_visual" : True }
    response = requests.post(url, json = payLoad, headers=headers)
    print "\n\tRESPONSE: ", response; sys.stdout.flush()

    return waitForTask(response)["id"]


def renameMesh( meshId, meshName ):
    print "\n### Rename mesh: /geom/meshes/rename %s" % meshId;

    url = baseURL + "/geom/meshes/rename"
    headers = getBaseHeaders()

    payLoad = {"id": meshId,
               'name' : meshName 
			  }
    response = requests.post(url, json = payLoad, headers=headers)

    print "\n\tRESPONSE: ", response.json()
    return response.json()["id"]


def generateVisual( meshId ):
    print "\n### Generate a visual: /geom/meshes/generateVisual ... %s" % meshId;

    url = baseURL + "/geom/meshes/generateVisual"
    headers = getBaseHeaders()

    payLoad = { 'id' : meshId }
    response = requests.post(url, json = payLoad, headers=headers)

    print "\n\tRESPONSE: ", response.json(); sys.stdout.flush()
    if "visual_file_id" in response.json():
        return response.json()["id"];

    return waitForTask(response)["id"];


def exportMesh( meshId ):
    print "\n### Export mesh: /geom/meshes/export %s" % meshId;

    url = baseURL + "/geom/meshes/export"
    headers = getBaseHeaders()

    payLoad = {"id": meshId, "file_type": "stl_binary" }
    response = requests.post(url, json = payLoad, headers=headers)

    print "\n\tRESPONSE: ", response.json(); sys.stdout.flush()
    return waitForTask(response)["file_id"]


##############################
## Tray operation API callas
##############################
def createTray(meshIds, meshAttr=None):
	print "\n### Create Tray: /print/trays/", meshIds; sys.stdout.flush()

	url = baseURL + "/print/trays"
	headers = getBaseHeaders()

	payLoad = { "printer_type_id": "7FAF097F-DB2E-45DC-9395-A30210E789AA", 
		    	"profile_id": "34F0E39A-9389-42BA-AB5A-4F2CD59C98E4", 
		    	"mesh_ids" : meshIds }

	if (meshAttr):
		payLoad['mesh_attrs'] = meshAttr

	response = requests.post(url, json = payLoad, headers=headers)

	print "\n\tRESPONSE: ", response.json(); sys.stdout.flush()
	return waitForTask(response)["id"]


def prepareTray(trayId):
	print "\n### Prepare Tray: /print/trays/prepare", trayId; sys.stdout.flush()

	url = baseURL + "/print/trays/prepare"
	headers = getBaseHeaders()

	payLoad  = { "id": trayId, "generate_visual": False }
	response = requests.post(url, json = payLoad, headers=headers)

	print "\n\tRESPONSE: Export Supports: ", response.json(); sys.stdout.flush()
	return waitForTask(response)["id"]


def exportSupport( trayId, meshIds ):
    print "\n### Export supports: /print/trays/exportSupport %s" % trayId; sys.stdout.flush()

    url = baseURL + "/print/trays/exportSupport"
    headers = getBaseHeaders()

    payLoad = {"id": trayId, "meshIds": meshIds, "generate_visual": True }
    response = requests.post(url, json = payLoad, headers=headers)

    print "\n\tRESPONSE: Export Supports: ", response.json()
    return waitForTask(response)


def generatePrintable(trayId):
	print "\n### Generate Printable: /print/trays/generatePrintable", trayId; sys.stdout.flush()

	url = baseURL + "/print/trays/generatePrintable"
	headers = getBaseHeaders()

	payLoad = {"id": trayId}
	response = requests.post(url, json = payLoad, headers=headers)

	print "\n\tRESPONSE: ", response.json()
	return waitForTask(response)["file_id"]


##############################
## Job operation API calls
##############################
def createJob(printableId, printerId):
	print "\n ============ Create Job", printableId; sys.stdout.flush()

	url = baseURL + "/print/printers/" + printerId +"/jobs"
	headers = getBaseHeaders()
	headers['Content-Type'] = 'application/json';
	
   	payLoad  = {  "printer_id" : printerId,
                   #"printable_id" : printableId,
                   "printable_url" : printableId,
		      	   "job_name": "Ania Job",
		      	   "settings" : { "MotorTimeoutScaleFactor": 1.3,
				     			  "first_layer_approach_rot_jerk" : 6,
				   },
		           "callback_url" : "http://localhost:3001/handlePrinterStatusUpdate",
		           "callback_interval" : 20 
               };

	response = requests.post(url, json=payLoad, headers=headers)
	return response.json(); 


def startPrintJob(printerId, jobId):

	url = baseURL + "/print/printers/" + printerId +"/jobs"
	headers = getBaseHeaders()

   	payLoad  = {  "printer_id" : printerId,
		          "job_id" : jobId
               };
	response = requests.put(url, json = payLoad, headers=headers)

	print "\n\tRESPONSE: ", response.json(); sys.stdout.flush()
	return response.json()  


def setPrinter(jobId, printerId):
	
	url = baseURL + "/print/jobs/" + jobId + "/printer"
	headers = getBaseHeaders()

   	payLoad  = {  "printer_id" : printerId,
		          "job_id" : jobId
                   };
	response = requests.post(url, json = payLoad, headers=headers)

	print "\n\tRESPONSE: ", response, response.json(); sys.stdout.flush()
	return waitForTask(response)


def setPrintable(jobId, printerId, printableId):
	
	url = baseURL + "/print/jobs/" + jobId + "/printable"
	headers = getBaseHeaders()

   	payLoad  = { "printer_id" : printerId,
   		         "printable_id" : printableId,
		         "job_id" : jobId
               };
	response = requests.post(url, json = payLoad, headers=headers)

	print "\n\tRESPONSE: ", response, response.json(); sys.stdout.flush()
	return waitForTask(response)


def setJobStatus(jobId, status):
	
	url = baseURL + "/print/jobs/" + jobId + "?status=" + status
	headers = getBaseHeaders()

	response = requests.put(url, headers=headers)

	print "\n\tRESPONSE: ", response, response.json(); sys.stdout.flush()
	return waitForTask(response)



### =========================== MGMT =============================
def listPrinters():
    
    #url = baseURL + "/print/printers?sort=member_id&member_id=12345678"
    #url = baseURL + "/print/printers?offset=0&limit=1&sort=member_id"
    #url = baseURL + "/print/printers?offset=2&limit=5&sort=member_id&member_id=12345678"
    url = baseURL + "/print/printers" # ?limit=20&offset=90"
    headers = getBaseHeaders()

    response = requests.get(url, headers=headers)

    print "\n\tRESPONSE: ", response.json(); sys.stdout.flush()
    return response.json()


def listMembersById(id):
    
    url = baseURL + "/print/printers/" + id + "/members";
    headers = getBaseHeaders()

    response = requests.get(url, headers=headers)

    print "\n\tRESPONSE: ", response.json(); sys.stdout.flush()
    return response.json()


def listPrintersStatus(id):
    
    url = baseURL + "/print/printers/status/" + id;
    headers = getBaseHeaders()

    response = requests.get(url, headers=headers)

    print "\n\tRESPONSE: ", response.json(); sys.stdout.flush()
    return response.json()


def registerUserPrinter(printerCode):
   
    url = baseURL + "/print/printers/register";
    headers = getBaseHeaders()

    payLoad = { "registration_code" : printerCode,
				"printer_name" 	    : "Ania's SIM"
              }
    response = requests.post(url, json = payLoad, headers=headers)

    print "\n\tRESPONSE: ", response; sys.stdout.flush();
    return response.json()


def registerSecondaryUserPrinter(printerCode):

    url = baseURL + "/print/printers/register";
    headers = getBaseHeaders()

    payLoad = { "printer_name" : "Sharing Ania's SIM Printer",
                "registration_code" : printerCode,
				"secondary_member_id" : secondary_member_id
              }
    response = requests.post(url, json = payLoad, headers=headers)

    print "\n\tRESPONSE: ", response; sys.stdout.flush();
    return response.json()


def getUserPrinter(pId):
    
    url = baseURL + "/print/printers/" + str(pId);
    headers = getBaseHeaders()

    response = requests.get(url, headers=headers)

    print "\n\tRESPONSE: ", response; sys.stdout.flush();
    return response.json()


def cancelPrintJob(jobId, printerId):
	print "\n### Cancel print job: /print/printers/" + printerId +"/command"; sys.stdout.flush()
	
	url = baseURL + "/print/printers/" + printerId +"/command"
	headers = getBaseHeaders()

   	payLoad  = {  "printer_id" : printerId,
		      	  "job_id" : jobId,
	              "command" : "cancel"
               };
	response = requests.post(url, json = payLoad, headers=headers)

	print "\n\tRESPONSE: ", response.json(); sys.stdout.flush()
	return response  


def resetPrinter(printerId):
	print "Reset printer: print/printers/" + printerId +"/command"; sys.stdout.flush()
	
	url = baseURL + "/print/printers/" + printerId +"/command"
	headers = getBaseHeaders()

   	payLoad  = {  "printer_id" : printerId,
	              "command" : "reset"
               };
	response = requests.post(url, json = payLoad, headers=headers)

	print "\n\tRESPONSE: ", response.json(); sys.stdout.flush()
	return response  


def listJobsPerPrinter( printerId ):
	print "List jobs per printer: /print/printers/" + printerId + "/jobs"; sys.stdout.flush()
	
	url = baseURL + "/print/printers/" + printerId + "/jobs" # + '?status=queued,canceled&limit=2&offset=0'
	headers = getBaseHeaders()

   	payLoad  = {  "printer_id" : printerId,
	              #"status" : ["queued", "completed"] 
	              #"status" : ["queued"] 
                   };
	response = requests.get(url, json = payLoad, headers=headers)

	print "\n\tRESPONSE: ", response.json(); sys.stdout.flush()
	return response.json();  


def listJobsFromPrinter( authCode ):
    print "List jobs for a printer: /print/printers/jobs ", authCode ; import sys; sys.stdout.flush()
    
    url = baseURL + "/print/printers/jobs"  # + '?limit=2&offset=0'
    headers = { "X-Printer-Auth-Token": authCode, } 

    response = requests.get(url, headers=headers)

    print "\n\tRESPONSE: ", response.json(); sys.stdout.flush()
    return response.json()


def listJobsPerMember( memberId ):
	print "List jobs per member /print/jobs ", memberId; sys.stdout.flush()
	
	url = baseURL + "/print/jobs"
	headers = getBaseHeaders()

   	payLoad  = { "status" : ["queued", "canceled"] };
	response = requests.get(url, json = payLoad, headers=headers)

	print "\n\tRESPONSE: ", response.json(); sys.stdout.flush()
	return response.json();  


def getJobStatus( jobId ):
	print "Get job status: /print/jobs/", jobId; sys.stdout.flush()

	url = baseURL + "/print/jobs/" + jobId
	headers = getBaseHeaders()

	response = requests.get(url, headers=headers)

	print "\n\tRESPONSE: ", response.json(); sys.stdout.flush()
	return response.json();  


def usage():
	print "Model file parameter is missing."; sys.stdout.flush();
	print "\nUsage: python %s  [<command>] [<cmd arguments>]" % sys.argv[0]
	print "\nCommands: analyze <fileName> | repair <fileName> | rename <fileName> <meshName>| visual <fileName> | export <fileName> | createTray <fileName> | prepare <trayId>| exportSupports <trayId>| printable <printerId> <trayId> | createJob |"
	print "          start <printerId>| pause <printerId>| resume <printerId>| cancel <printerId>| status <printerId> "
	print "          register <token> | "
	print "\nExamples: "
	print "\n 1. repair a model in <fileName>"
	print "\n\t python print.py <fileName> repair "
	print "\n 2. rename a mesh generated from <fileName>"
	print "\n\t python print.py <fileName> rename 'Bunny' "
	print "\n"


################# MAIN ######################
def main():

	import sys

	print "\n In main: arg:", len(sys.argv), sys.argv
	# Parse the arguments. 
	if len(sys.argv) < 2:
		usage(); sys.exit(1)

    # Read the command 
	command = sys.argv[1]

	print "COMMAND:", command; sys.stdout.flush()
	meshId = None
	if command in [ 'analyze', 'rename', 'repair', 'visual', 'export', 'createTray']:
		if len(sys.argv) < 3:
			usage(); sys.exit(1)

		# Read the input geometry file (stl, obj, mtl)
		fileName = sys.argv[2] 
		
	    # Upload a file to Spark Drive 
		modelFileId = uploadToSparkDrive( fileName )
		print "Uploaded file to Spark Drive and got FileId", modelFileId

	    # Import mesh
		meshNm = "Mesh 1"
		meshId = importMesh( modelFileId, meshNm )

	if command == "analyze":
		result = analyzeMesh( meshId )
		print "\n==> Analyzed mesh and got meshId: ", result['id']
		print "==> Problems: ", result['problems']

	elif command == "rename":
		meshName  = sys.argv[3] if len(sys.argv) > 3 else "Renamed Mesh"
		meshIdOut = renameMesh( meshId, meshName )
		print "\n==> Renamed mesh and got meshId: ", meshIdOut

	elif command == "repair":
		meshIdOut = repairMesh( meshId )
		print "\n==> Repaired mesh and got meshId: ", meshIdOut

	elif command == "visual":
		boltFileId = generateVisual( meshId )
		print "\n==> Generated a visual and got bolt fileId: ", boltFileId

	elif command == "export":
		fileIdE = exportMesh( meshId )
		print "\n==> Exported mesh and got fileId", fileIdE

	elif command == "createTray":
		trayId = createTray( [meshId] )
		print "\n==> Created Tray for Ember with Id", trayId

	elif command == "prepare":
		trayId    = createTray( [meshId] )
		trayIdOut = prepareTray(trayId)
		print "\n==> Prepared Tray with Id", trayId

	elif command == "printable":
		trayIdIn  = sys.argv[3] if len(sys.argv) > 3 else None
		if not trayIdIn:
			trayId   = createTray( [meshId] )
			trayIdIn = prepareTray(trayId)
		printableId = generatePrintable(trayIdIn)
		print "\n==> Generate printable with printableId", printableId

	elif command == "exportSupports":
		trayIdIn  = sys.argv[3] if len(sys.argv) > 3 else None
		if not trayIdIn:
			trayId   = createTray( [meshId] )
			trayIdIn = prepareTray(trayId)
		fileIdSupports = exportSupport(trayIdIn, [meshId])
		print "\n==> Exported Supports to file: ", fileIdSupports

	elif command == "createJob":
		printerId = sys.argv[3] if len(sys.argv) > 3 else None

		trayId   = createTray( [meshId] )
		trayIdIn = prepareTray(trayId)
		printableId = generatePrintable(trayIdIn)

		# If the printer is not busy, it will send it to the printer. 
		jobId = createJob(printableId, printerId)
		print "\n==> Created job with id:", jobId

	elif command == "register":
		token = sys.argv[3] if len(sys.argv) > 3 else None
		if not token: 
			usage()
			sys.exit(1)

		codes = registerUserPrinter( token )
		print "\n==> Printer: ", codes; sys.stdout.flush()

	elif command == "jobStatus":
		jobId = sys.argv[3] if len(sys.argv) > 3 else None
		if not token: 
			usage(); sys.exit(1)

		response = getJobStatus(jobId)
		print "\n==> Status: ", response

	elif command == "start":
		printerId = sys.argv[3] if len(sys.argv) > 3 else None

	elif command == "pause":
		printerId = sys.argv[3] if len(sys.argv) > 3 else None

	elif command == "resume":
		printerId = sys.argv[3] if len(sys.argv) > 3 else None

	elif command == "cancel":
		printerId = sys.argv[3] if len(sys.argv) > 3 else None
		jobId = sys.argv[4] if len(sys.argv) > 4 else None
		response = cancelPrintJob(jobId, printerId)
		print "\n==> Response: ", response; sys.stdout.flush()

	elif command == "reset":
		printerId = sys.argv[3] if len(sys.argv) > 3 else None
		response = resetPrinter(printerId)
		print "\n==> Response: ", response; import sys; sys.stdout.flush()

	elif command == "list":
		result = listPrinters()


if __name__ == "__main__":
    main()

