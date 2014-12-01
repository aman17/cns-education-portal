import socket
import threading
import SocketServer
import loginCheck
import pickle
import json
import cv2
import numpy
import cv2.cv as cv
import sys

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        data = self.request.recv(1024)
        #print data
        cur_thread = threading.current_thread()
        if data=="listArchive":
            rows = loginCheck.getArchives()
            print rows,"in listArchive"
            self.request.sendall(pickle.dumps(rows))
            fn = self.request.recv(1024)
            UDP_IP = '10.100.95.33'
            UDP_PORT = 7806
            sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            cap = cv2.VideoCapture(fn) 
            #capRead = cv2.VideoCapture('output.avi')
            cap.set(3,320)
            cap.set(4,240)
            while True:
                ret, frame = cap.read()
                print frame
                if frame==None:
                    print "none tpy"
                    sock.sendto("ho gaya beta",(UDP_IP,UDP_PORT))
                    break
                print frame/2
                if ret:
                #out.write(frame)
                #print "aman",frame
                    frame = frame/2
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    #self.out.write(frame)
                    (retval,buf) = cv2.imencode(".jpg",gray)
                    if retval:
                        ser = pickle.dumps(buf)
                        if ser:
                            sock.sendto(ser,(UDP_IP,UDP_PORT))
                    cv2.waitKey(140)
                    '''self.emit(QtCore.SIGNAL('captureNow'),ser)
                    c = cv2.waitKey(50) & 0xFF
                    if c==ord('q'):
                        s = est_tcp_conn.create_tcp()
                        s.send("delete lecture")
                        s.recv(1024)
                        s.send(self.fileName)
                    #self.out.release()
                    #cap.release()
                        break
                    else:
                        print "break"
                        break'''
            cap.release()
            sock.close()
            

        if data=="sending lecture":
            print "sending lecture wale me.."
            self.request.sendall("ack")
            fn = self.request.recv(8192)
            f = open(fn,'wb')
            l = self.request.recv(8192)
            print "recieving.."
            i=1
            while len(l)>0:
                print i
                i=i+1
                #print "hello"
                #print l
                f.write(l)
                l = self.request.recv(1024)
            #self.request.sendall("complete")
            f.close()
            loginCheck.insertNewLecture(str(fn))
            print "finished.."
        if data=="delete lecture":
            self.request.sendall("ack")
            fileName = self.request.recv(1024)
            loginCheck.deleteLecture(fileName)
        if data=="get teacher ip":
        	print "teacher ip wale me.."
        	self.request.sendall("ack")
        	teach_id = self.request.recv(1024)
        	ip = loginCheck.getIp(int(teach_id))
        	self.request.sendall(ip)
        if data=="list":
        	print "list wale me.."
        	#self.request.sendall("ack")
        	rows = loginCheck.getLiveLecture()
        	self.request.sendall(pickle.dumps(rows))
        if data=="fileName":
        	print "file wale me.."
        	self.request.sendall("requesting file name")
        	fileName = self.request.recv(1024)
        	self.request.sendall("ack")
        	user = self.request.recv(1024)
        	self.request.sendall("ack")
        	loginCheck.addFileName(fileName,user)
        if data=="login":
            print "login wale me.."
            self.request.sendall("requesting login data")
            usr = self.request.recv(1024)
            self.request.sendall("ack")
            pwd = self.request.recv(1024)
            loginData = loginCheck.login(usr,pwd)
            if loginData == "wrong":
                print "wrong user name or password.."
            self.request.sendall(pickle.dumps(loginData))
            self.request.recv(1024)
            login_val = loginData[2]
            print login_val
            if(login_val==1):
                rows = loginCheck.get_ip(loginData[0])
                print loginData[0],"in here"
                for row in rows:
                    if row[0]==loginData[0]:
                        ip = row[1]
        		print ip,"here"
        		self.request.sendall(ip)
        	#pickle.dumps(ipdata)



class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

if __name__ == "__main__":
	# Port 0 means to select an arbitrary unused port
    HOST, PORT = "10.100.95.33", 5612
    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    ip, port = server.server_address
    print "ip: ",ip
    print "port: ",port
    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()
    print "Server loop running in thread:", server_thread.name
    while(1):
    	inp = raw_input('1.Send client\n2.shutdown server')

    	if inp == "1":
    		client(ip, port, "Hello World")
    	if inp == "2":
			server.shutdown()
			break
