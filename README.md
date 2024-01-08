# common-ip-pdu-library
# A Common Python Library for IP PDU Services, which acts as a common platform to communicate with any IP PDU models and exposes REST APIs.

The current supported IP PDU Models are provided below.
1. Raritan (PX3567V)
2. APC (AP7921B)
3. DLI (Web Power Switch - Version 1.8.4)
4. Aten (PE6108) 

Command to Start the REST Server
PduLibraryApp.py restserver restart

The above command will start the REST Server on default port 3486, which can be accessible using the below link and API documents for each REST API is available in the below Swagger link.
http://localhost:3486/v1/spec.html
