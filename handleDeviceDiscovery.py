import sys
import socket
import struct

MCAST_GRP = ''
MCAST_PORT = 0
UUID = ''
NAME_LIST = ""
PORT_LIST = ""

def getLocalAddress():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    sockname = s.getsockname()
    s.close()
    return sockname

def UDPMulticastListener(group, port, messageHandlerCallback = None):

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', port))  # use MCAST_GRP instead of '' to listen only
                             # to MCAST_GRP, not all groups on MCAST_PORT
    mreq = struct.pack("4sl", socket.inet_aton(group), socket.INADDR_ANY)

    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    localHost = getLocalAddress();

    print()
    print("UDP started on", localHost[0], "port", localHost[1])
    print("device UUID: " + UUID)
    print("listening to device discovery on group ",group,"port", port, "...")
    print("^c to quit")
    print()

    try:
        while True:
            #data, addr = sock.recv(10240) #buffer size 1024 bytes
            data, hostAddress = sock.recvfrom(10240)
            #print("remote addr:", hostAddress[0], " port ", hostAddress[1])
            if messageHandlerCallback:
                messageHandlerCallback(hostAddress,data)

    except KeyboardInterrupt:
        print ( '^c recieved, shutting down the socket' )
        sock.close();

def MessageHandlerCallback(hostAddress,data):
    remoteIP = hostAddress[0]
    remotePort = hostAddress[1]
    message = data.decode('utf-8')
    print("")
    print("recieved broadcast from:", remoteIP, " port ", remotePort)
    print("size=", len(data), "byte(s)")
    print("message = [" + message + "]")

    if(message.find("M-SEARCH") > -1):
        if(message.find("ssdp:all") > -1) or (message.find("upnp:rootdevice") > -1):

            print(">>>>>>>>> SEARCH recieved")
            RespondToSearch(remoteIP, remotePort, message)
    return

def RespondToSearch(remoteIP, remotePort, message):

    """
    HTTP/1.1 200 OK
    CACHE-CONTROL: max-age=86400
    DATE: Sat, 26 Nov 2016 04:56:29 GMT
    EXT:
    LOCATION: http://192.168.1.43:80/setup.xml
    OPT: "http://schemas.upnp.org/upnp/1/0/"; ns=01
    01-NLS: b9200ebb-736d-4b93-bf03-835149d13983
    SERVER: Unspecified, UPnP/1.0, Unspecified
    ST: urn:Belkin:device:**
    USN: uuid:Socket-1_0-38323636-4558-4dda-9188-cda0e6196b1f-80::urn:Belkin:device:**
    X-User-Agent: redsonic
    """

    localHost = getLocalAddress();
    webserverIP = localHost[0]
    #webserverPort = 8001

    i=0
    for name in NAME_LIST:

        persistent_uuid = UUID + str(PORT_LIST[i])

        response = (
        "HTTP/1.1 200 OK\r\n"
        "CACHE-CONTROL: max-age=86400\r\n"
        "DATE: Sat, 26 Nov 2016 04:56:29 GMT\r\n"
        "EXT:\r\n"
        "LOCATION: http://" + str(webserverIP) + ":" + str(PORT_LIST[i]) + "/setup.xml\r\n"
        "OPT: \"http://schemas.upnp.org/upnp/1/0/\"; ns=01\r\n"
        "01-NLS: b9200ebb-736d-4b93-bf03-835149d13983\r\n"
        "SERVER: Unspecified, UPnP/1.0, Unspecified\r\n"
        "ST: urn:Belkin:device:**\r\n"
        "USN: uuid:" + persistent_uuid + "::urn:Belkin:device:**\r\n"
        "X-User-Agent: redsonic\r\n\r\n"
        )

        sock = socket.socket( socket.AF_INET,     # internet
                        socket.SOCK_DGRAM   # UDP
                        )
        sock.sendto(response.encode('utf-8'), (remoteIP, remotePort))

        print("responst sent to",remoteIP," port ",remotePort)
        print("device name: " + name)
        print("port: " + PORT_LIST[i])
        print("[" + response + "]")

        i=i+1

def commandArguments():

    if(len(sys.argv) < 6):
        print("")
        print("usage: " + sys.argv[0] + " [MCAST_GRP] [MCAST_GRP] [UUID] [NAME LIST] [PORT LIST]")
        print("")
        return False

    global MCAST_GRP
    MCAST_GRP = sys.argv[1]
    global MCAST_PORT
    MCAST_PORT = int(sys.argv[2])
    global UUID
    UUID = sys.argv[3]
    global NAME_LIST
    NAME_LIST = sys.argv[4].split("|")
    global PORT_LIST
    PORT_LIST = sys.argv[5].split("|")

    print(NAME_LIST)
    print(PORT_LIST)

    return True


if(commandArguments()):

    # start the multicast listener
    UDPMulticastListener(MCAST_GRP,MCAST_PORT,MessageHandlerCallback)
