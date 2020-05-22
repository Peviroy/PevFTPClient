import getpass
import os
import re
import sys
from socket import *


CRLF = '\r\n'


class PevFTPclient:
    def __init__(self, host, port, username, passwd, stdIn=None, stdOut=None):
        self.host = host
        self.port = port
        self.username = username
        self.password = passwd
        self.verifyArgs()

        if stdOut:
            self.stdOutFile = stdOut
        else:
            self.stdOutFile = sys.stdout
        self.clientSocket = None
        # Python file object; can be read from or written to the socket that created it
        self.file = None
        self.initialize()

    def RedirectStdout(func):
        def wrapper(self, *args, **kwargs):
            savedStdout, sys.stdout = sys.stdout, self.stdOutFile
            try:
                return func(self, *args, **kwargs)
            finally:
                sys.stdout = savedStdout
        return wrapper

    """
    @description: Verify host, port, username, passwd
    """

    def verifyArgs(self):
        if not (self.host and self.port):
            exit('Server & Port are required')

        if not (0 < self.port < 65535):
            exit('host port in 0-65535')

        if not (self.username and self.password):
            if not (self.username is None and self.password is None):
                exit('username and password should be a pair')

    """
    @description: Tring to connect to the server
    """

    def initialize(self):
        print("Attempting connection to ",  self.host, "; Port",  self.port)
        try:
            self.clientSocket = socket(AF_INET, SOCK_STREAM)
            self.clientSocket.connect((self.host, self.port))
            self.file = self.clientSocket.makefile('rb')
        except Exception:
            print("Connection fails")
            raise Exception
        self.readMultiline()
        print(self.login())
        print("Connection success")

    """
    @description: Main loop
    """
    @RedirectStdout
    def run(self, query):
        if len(query) == 0:
            print("\tNothing selected")
            return
        else:
            print("PevFTPClient [{}]>".format(self.username), query)
            command = query.split()[0]
            if "help" == command or "h" == command:
                self.helpme()
            elif "quit" == command:
                self.logout()
            elif "ls" == command:
                self.list(query)
            elif "cd" == command:
                self.cwd(query)
            elif "get" == command:
                self.get(query)
            elif "put" == command:
                self.put(query)
            elif "rm" == command:
                self.delete(query)
            else:
                print("\tUnknown command!")

    """
    @description: login via cmdline parameter or interactive input 
    """

    def login(self):
        if self.username and self.password:  # CMDLINE PARAMETER
            return self.authenticate(self.username, self.password)
        else:
            # INTERACTIVE Three chances
            for _ in range(0, 3):
                self.username = input("Username: ")
                self.password = getpass.getpass('Password: ')
                if self.authenticate(self.username, self.password):
                    return True
            print("Tried out chances! Exit")
            return False

    """
    @description: [FTP function] Implement of login function
    """
    @RedirectStdout
    def authenticate(self, username, password):
        self.sendCommand('USER ' + username)
        response = self.readMultiline()
        # print(response)
        if self.__passwordRequired(response):
            self.sendCommand('PASS ' + password)
            response = self.readMultiline()
            # print(response)
        if self.__loginOK(response):
            return True
        return False

    @staticmethod
    def __passwordRequired(response):
        return "331" in response

    @staticmethod
    def __loginOK(response):
        return "230" in response  # 530 ? 230 ?

    """
    @description: help page
    """
    @RedirectStdout
    def helpme(self):
        helppage = '''
        Options:
        ------------------------------------------------
        help             show this help message
        quit             exit->[QUIT]
        ls <directory>   list directory->[LIST]
        cd <directory>   change to the exact directory->[CWD]
        get <filename>   download the file->[RETR]
        put <filename>   upload the file->[STOR]
        rm  <filename>   delete the file->[DELE]             
        '''
        print(helppage)

    """
    @description: [FTP function] QUIT
    @example: FTPClient > quit
    """
    @RedirectStdout
    def logout(self):
        self.sendCommand('QUIT')
        print("\t", self.readLine())
        self.clientSocket.close()
        self.file.close()
        exit()

    """
    @description: [FTP function]List all the files in the directory; Take the current directory as default
    @example: FTPClient > ls
    """
    @RedirectStdout
    def list(self, path):
        path = self.cleanQuery(path, 2)  # removing "ls"
        self.getAsciiFile("LIST " + path)

    """
    @description: [FTP function]Navigating through the directories
    @example: FTPClient > cd <DIRECTORY>
    """
    @RedirectStdout
    def cwd(self, query):
        query = self.cleanQuery(query, 3)  # removing "cd"
        # original CWD cannot handle "../" properly
        cdParentDir = len(re.findall('(\.\./?)', query))
        if cdParentDir != 0:
            for _ in range(0, cdParentDir):
                self.sendCommand('CDUP')
                # print(self.readMultiline())
                self.readMultiline()
        else:
            self.sendCommand('CWD ' + query)
            if self.__isCWDOK(self.readMultiline()):
                print("\tChange directory ok")
            else:
                print("\tNo such directory")
            # self.readMultiline()

    @staticmethod
    def __isCWDOK(response):
        return "250" in response

    """
    @description: [FTP function]Download a file from the server ;
                   1. Init a file with the same name;
                   2. And then copying the binary data into it
    @example: FTPClient > get <filename>
    """
    @RedirectStdout
    def get(self, path):
        path = self.cleanQuery(path, 3).strip()
        command = 'RETR ' + path
        head, tail = os.path.split(path)
        newFile = open(tail, "wb+")
        self.getBinaryFile(command, newFile)
        print("\tSuccess. %s bytes received" % newFile.tell())
        newFile.close()

    """
    @description: [FTP function]Delete file on the server
    @example: FTPClient > rm <filename>
    """
    @RedirectStdout
    def delete(self, path):
        path = self.cleanQuery(path, 2)
        self.sendCommand('DELE' + path)
        # print(self.readMultiline())
        if self.__isDeleteOK(self.readMultiline()):
            print("\tDelete success")
            return
        exit("Delete failed")

    @staticmethod
    def __isDeleteOK(response):
        return "250" in response

    """
    @description: [FTP function]Delete file on the server
    @example: FTPClient > put <filename>
    """
    @RedirectStdout
    def put(self, path):
        path = self.cleanQuery(path, 4).strip()
        file = open(path, 'rb')
        command = 'STOR ' + path
        self.uploadBinaryFile(command, file)
        print("\tSuccess. %s bytes uploaded" % file.tell())
        file.close()

    """
    @description: Command sent should ended with CRLF;and be bytes 
    """
    @RedirectStdout
    def sendCommand(self, command):
        command += CRLF
        self.clientSocket.sendall(str.encode(command))

    """
    @description: Read command line from server via socket in the form of ascii rather than binary
    """
    @RedirectStdout
    def readLine(self, binarymode=True):
        line = self.file.readline()
        if line[-2:] == CRLF:
            line = line[:-2]
        if binarymode:
            return bytes.decode(line)
        return line

    """
    @description: Read line untile no more line left --RFC 959, section 4.2:
    """
    @RedirectStdout
    def readMultiline(self):
        line = self.readLine()
        if line[3:4] == '-':
            code = line[:3]
            while 1:
                nextLine = self.readLine()
                line = line + ('\n' + nextLine)
                # end of lines
                if nextLine[:3] == code and \
                        nextLine[3:4] != '-':
                    break
        return line

    """
    @description: Cleaning the queries to be sent to the server by remove cmd word
    """
    @staticmethod
    def cleanQuery(rawQuery, numberOfCharacters):
        cleanQuery = rawQuery[numberOfCharacters:]
        return cleanQuery

    """
    @description: Key method of function<put>
    @param command{str}: "cmd filepath"
    @param file{FILE}
    """
    @RedirectStdout
    def uploadBinaryFile(self, command, file):
        self.sendCommand('TYPE I')
        responseTypeI = self.readLine()
        # print(responseTypeI)
        dataSocket = self.startConnectionToPassivePort(command)
        while True:
            data = file.readline(1024)
            if not data:
                break
            dataSocket.sendall(data)
        dataSocket.close()
        # print(self.readMultiline())
        self.readMultiline()

    """
    @description: For .txt, .htm and other files, ASCII code should be used for transmission
    """
    @RedirectStdout
    def getAsciiFile(self, command, file=None):
        self.sendCommand('TYPE A')
        responseTypeA = self.readLine()
        # print(responseTypeA)
        dataSocket = self.startConnectionToPassivePort(command)
        datafile = dataSocket.makefile('rb')
        while True:
            line = bytes.decode(datafile.readline())
            if not line:
                break
            elif line[-2:] == CRLF:
                line = line[:-2]
            elif line[-1:] == '\n':
                line = line[:-1]

            if file is None:
                print("\t"+line)
            else:
                file.write(line)
        datafile.close()
        dataSocket.close()
        self.readMultiline()

    """
    @description: For non-text file, binary code should be used for transmission
    @Note: Nonting different with getAsciiFile except no need to deal with format
    """
    @RedirectStdout
    def getBinaryFile(self, command, file=None):
        self.sendCommand('TYPE I')
        responseTypeI = self.readLine()
        # print(responseTypeI)
        dataSocket = self.startConnectionToPassivePort(command)
        while True:
            bytesInfo = dataSocket.recv(1024)
            # print(bytesInfo)
            if file is not None:
                file.write(bytesInfo)
            if not bytesInfo:
                break
        dataSocket.close()
        # print(self.readMultiline())
        self.readMultiline()

    """
    @description: String received is in the format:(h1,h2,h3,h4,p1,p2);So use regexpression to parse it;
    """
    @RedirectStdout
    def getServerPassivePort(self, responsePASV):
        values = re.findall('(\d+)', self.cleanQuery(responsePASV, 3))
        host = '.'.join(values[:4])  # host = h1.h2.h3.h4
        port = (int(values[4]) * 256) + int(values[5])  # port = p1 * 256 + p2
        return host, port

    """
    @description:Initiate the passive mode; Obtain the host and port information from the response \ 
                 to start the data socket connection;
    """
    @RedirectStdout
    def startConnectionToPassivePort(self, command):
        # Passive mode: the server send a newly opened port as data port;
        self.sendCommand('PASV')
        responsePASV = self.readLine()
        # print(responsePASV)
        if self.__isPasiveModeOK(responsePASV):
            host, port = self.getServerPassivePort(responsePASV)
            # print(host, port)
            dataSocket = None
            for res in getaddrinfo(host, port, 0, SOCK_STREAM):
                af, socktype, proto, canonname, sa = res
                dataSocket = socket(af, socktype, proto)
                dataSocket.connect(sa)
                self.sendCommand(command)
                # print(self.readLine())
                self.readLine()
            return dataSocket
        return None

    @staticmethod
    def __isPasiveModeOK(response):
        return "227" in response
