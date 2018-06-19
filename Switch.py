#!/usr/bin/python
import sys
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import RPi.GPIO as GPIO
from gpioController import GPIOController

DEVICE_NAME = ""
UUID = ""
PORT_NUMBER = -1

SWITCH_STATE = 0

IS_GPIO = False
GPIO_CONTROL = GPIOController(0,0)

class Switch(BaseHTTPRequestHandler):

    switchStatus = SWITCH_STATE
    name = DEVICE_NAME
    uuid = UUID

    """
    def __init__(self, name, uuid):
        self.name = name
        self.uuid = uuid
    """

    def getPostData(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        return post_data, content_length

    def handleRoot(self):
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        self.wfile.write("use Amazon Alexa to discover this device")
        return

    def handleSetupXml(self):

        print("handling setup ...");

        setupXml = (
        "<?xml version=\"1.0\"?>"
            "<root>"
             "<device>"
                "<deviceType>urn:Belkin:device:controllee:1</deviceType>"
                "<friendlyName>"+ DEVICE_NAME +"</friendlyName>"
                "<manufacturer>Belkin International Inc.</manufacturer>"
                "<modelName>Socket</modelName>"
                "<modelNumber>3.1415</modelNumber>"
                "<modelDescription>Belkin Plugin Socket 1.0</modelDescription>\r\n"
                "<UDN>uuid:"+ UUID +"</UDN>"
                "<serialNumber>221517K0101769</serialNumber>"
                "<binaryState>0</binaryState>"
                "<serviceList>"
                  "<service>"
                      "<serviceType>urn:Belkin:service:basicevent:1</serviceType>"
                      "<serviceId>urn:Belkin:serviceId:basicevent1</serviceId>"
                      "<controlURL>/upnp/control/basicevent1</controlURL>"
                      "<eventSubURL>/upnp/event/basicevent1</eventSubURL>"
                      "<SCPDURL>/eventservice.xml</SCPDURL>"
                  "</service>"
              "</serviceList>"
              "</device>"
            "</root>\r\n"
            "\r\n"
        )

        self.send_response(200)
        self.send_header('Content-type','text/xml')
        self.end_headers()
        self.wfile.write(setupXml)

        print(">>>>> SETUP RESPONSE SENT")
        print(setupXml)

        return

    def turnOnRequested(self):
    	GPIO_CONTROL.output(GPIO.HIGH)
        global SWITCH_STATE
        SWITCH_STATE = GPIO_CONTROL.input()
        print('SWITCH state =', SWITCH_STATE)
        return

    def turnOffRequested(self):
    	GPIO_CONTROL.output(GPIO.LOW)
        global SWITCH_STATE
        SWITCH_STATE = GPIO_CONTROL.input()
        print('SWITCH state =', SWITCH_STATE)
        return

    def sendSwitchState(self):

        #print("CURRENT SWITCH STATUS=",SWITCH_STATE)

        content = (
        "<s:Envelope xmlns:s=\"http://schemas.xmlsoap.org/soap/envelope/\" "
        "s:encodingStyle=\"http://schemas.xmlsoap.org/soap/encoding/\"><s:Body>\r\n"
        "<u:GetBinaryStateResponse xmlns:u=\"urn:Belkin:service:basicevent:1\">\r\n"
        "<BinaryState>" + str(SWITCH_STATE) + "</BinaryState>\r\n"
        "</u:GetBinaryStateResponse>\r\n"
        "</s:Body> </s:Envelope>\r\n")

        self.send_response(200)
        self.send_header('Content-type','text/xml')
        self.end_headers()
        self.wfile.write(content)

        print(">>>>> CONTROL RESPONSE SENT")
        #print(content)

        return

    def handleControl(self):

        print("handling control ...");


        #(content, length)
        post_data = self.getPostData()
        #print(post_data)
        content = post_data[0]

        """
        print("--------------------------------------")
        print(content)
        print("--------------------------------------")
        """

        # BINARY STATES
        if(content.find("SetBinaryState") > -1):
            if(content.find("<BinaryState>1</BinaryState>") > -1):
                print("TURN ON REQUESTED");
                self.turnOnRequested()
                self.sendSwitchState();

            elif(content.find("<BinaryState>0</BinaryState>") > -1):
                print("TURN OFF REQUESTED");
                self.turnOffRequested()
                self.sendSwitchState();

        elif(content.find("GetBinaryState") > -1):
                print("BINARY STATE REQUESTED");
                self.sendSwitchState();

        self.send_response(200)
        self.send_header('Content-type','text/plain')
        self.end_headers()
        self.wfile.write("")

        return

    def handleEventService(self):

        print("handling event service ...");

        eventServiceXml = (
        "<scpd xmlns=\"urn:Belkin:service-1-0\">"
        "<actionList>"
          "<action>"
            "<name>SetBinaryState</name>"
            "<argumentList>"
              "<argument>"
                "<retval/>"
                "<name>BinaryState</name>"
                "<relatedStateVariable>BinaryState</relatedStateVariable>"
                "<direction>in</direction>"
                "</argument>"
            "</argumentList>"
          "</action>"
          "<action>"
            "<name>GetBinaryState</name>"
            "<argumentList>"
              "<argument>"
                "<retval/>"
                "<name>BinaryState</name>"
                "<relatedStateVariable>BinaryState</relatedStateVariable>"
                "<direction>out</direction>"
                "</argument>"
            "</argumentList>"
          "</action>"
      "</actionList>"
        "<serviceStateTable>"
          "<stateVariable sendEvents=\"yes\">"
            "<name>BinaryState</name>"
            "<dataType>Boolean</dataType>"
            "<defaultValue>0</defaultValue>"
           "</stateVariable>"
           "<stateVariable sendEvents=\"yes\">"
              "<name>level</name>"
              "<dataType>string</dataType>"
              "<defaultValue>0</defaultValue>"
           "</stateVariable>"
        "</serviceStateTable>"
        "</scpd>\r\n"
        "\r\n"
        )

        self.send_response(200)
        self.send_header('Content-type','text/xml')
        self.end_headers()
        self.wfile.write(eventServiceXml)

        print(">>>>> SETUP EVENTSEVICE SENT")
        #print(eventServiceXml)

        return

    def handleAlexaRequests(self, path):

        print("")
        print("")
        print("PROCESSING A NEW REQUEST:")
        print("-------------------------")
        #print("path=", path)

        if(path == "/"):
            self.handleRoot();
        elif(path == "/setup.xml"):
            self.handleSetupXml();
        elif(path == "/upnp/control/basicevent1"):
            self.handleControl()
        elif(path == "/eventservice.xml"):
            self.handleEventService()
        return

    #handler for the GET request
    def do_GET(self):
        #print("GET recieved:", self.path)
        self.handleAlexaRequests(self.path)
        return

    def do_POST(self):
        #print("POST recieved:", self.path)
        self.handleAlexaRequests(self.path)
        return



def commandArguments():

    if(len(sys.argv) < 5):
        print("")
        print("usage: " + sys.argv[0] + " [DEVICE_NAME] [PORT_NUMBER] [UUID] [PCM -1 disabled]")
        print("")
        return False

    global DEVICE_NAME
    DEVICE_NAME = sys.argv[1]
    global PORT_NUMBER
    PORT_NUMBER = int(sys.argv[2])
    global UUID
    UUID = sys.argv[3]
    if(sys.argv[4] != -1):
        global GPIO_CONTROL
        GPIO_CONTROL = GPIOController(int(sys.argv[4]),GPIO.LOW)
        global IS_GPIO
        IS_GPIO = True
    
    return True
    
if(commandArguments()):

    try:

        # create a web server and define a handler to manage
        # imcoming requests
        server = HTTPServer(('', PORT_NUMBER), Switch)
        print("")
        print("Started HTTPServer on port " + str(PORT_NUMBER))
        print("Device name: " + DEVICE_NAME)
        print("UUID: " + UUID)
        print("BCM pin number: " + str(GPIO_CONTROL.bcmPinNumber))
        print("ready to handle requests from Alexa ...")
        print("")

        #wait forever for incoming http requests
        server.serve_forever()

    except KeyboardInterrupt:
        print ( '^c recieved, shutting down the web server' )
        server.socket.close();
        GPIO_CONTROL.cleanupGPIO()
