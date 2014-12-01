import rec_main
import est_tcp_conn
import loginCheck
from PyQt4 import QtGui, QtCore, uic
import sys
import os
import est_udp_rec_conn
import threading
import cv2
import cv2.cv as cv
import pickle
import socket
import struct
import numpy as np
import json
from PyQt4.QtCore import QObject, pyqtSignal, pyqtSlot


#capRead.set(3,160)
#capRead.set(4,120)

# Define the codec and create VideoWriter object
'''try:
    conn = psycopg2.connect(database = "201201063", user = "201201063", password="201201063", host="10.100.71.21",port="5432")
    print "success"
except:
    print "I am unable to connect to the database"
cur = conn.cursor()'''
    
class liveConnect(QtCore.QThread):
	def __init__(self,conn_dict):
		QtCore.QThread.__init__(self)
		self.udp_sock = conn_dict
		'''self.udp_sock = conn_dict['udp']
		self.tcp_sock = conn_dict['tcp']'''
		print "thread __init__"
 	def run(self):
 		print "thread run"
 		#self.tcp_sock.send("live")
 		#self.tcp_sock.recv(1024)
 		while True:
 			print "inside.."
 			c = cv2.waitKey(1) & 0xFF
			d = self.udp_sock.recvfrom(65536)
			data = d[0]
			addr = d[1]
			print addr
			self.emit(QtCore.SIGNAL('display'),data)
			if c==ord('q'):
				#self.quit()
				break
	 	print "oner"
 		return


class StudentGui(QtGui.QMainWindow):
	def __init__(self):
		print "check check"
		QtGui.QMainWindow.__init__(self)
		self.ui = uic.loadUi('RecieverMainWindow.ui')
		self.ui.show()
		print "loaded..."
		self.connect(self.ui.btnLive, QtCore.SIGNAL("clicked()"), self.live)
		self.connect(self.ui.btnArchives, QtCore.SIGNAL("clicked()"), self.archive)
		#self.connect(self.ui.btnArchives, QtCore.SIGNAL("clicked()"), self.archive)
		#self.connect(self.ui.btnArchives, QtCore.SIGNAL("clicked()"), self.buttonFn_2)
		#self.conn_dict = est_udp_rec_conn.create_connection()
	def live(self):
		self.lg = listGui()	
	def archive(self):
		print "archive"
		self.archList = archiveListGui()
class archiveListGui(QtGui.QMainWindow):
	def __init__(self):
		QtGui.QMainWindow.__init__(self)
		print "hello archive"
		self.ui = uic.loadUi('listArchive.ui')
		self.ui.show()
		self.s = est_tcp_conn.create_tcp()
		self.s.send("listArchive")
		data = self.s.recv(4096)
		self.rows = pickle.loads(data)
		print self.rows
		for row in self.rows:
			self.ui.listWidget.addItem(row[1])
		self.ui.listWidget.itemDoubleClicked.connect(self.showItem)
	def showItem(self,item):
		UDP_IP = '192.168.0.103'
		UDP_PORT = 7807
		sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
		sock.bind((UDP_IP,UDP_PORT))
		videoName = str(item.text())
		self.s.send(videoName)
		while True:
			data,addr = sock.recvfrom(65536)
			if data == "ho gaya beta":
				break
			if not data:
				break
			print "data"
			buf = pickle.loads(data)
			frame = cv2.imdecode(buf,0)
			cv2.imshow('ClientRecieving',frame)
			cv2.waitKey(100)
		print "finished"
		cv2.destroyAllWindows()
		sock.close()
		self.ui.close()
class listGui(QtGui.QMainWindow):
	def __init__(self):
		QtGui.QMainWindow.__init__(self)
		self.ui = uic.loadUi('list.ui')
		self.ui.show()
		self.s = est_tcp_conn.create_tcp()
		self.s.send("list")
		data = self.s.recv(4096)
		self.rows = pickle.loads(data)
		print self.rows
		#self.list = QListWidget(self)
		for row in self.rows:
			self.ui.listWidget.addItem(row[1])
		self.ui.listWidget.itemDoubleClicked.connect(self.showItem)
		
	def showItem(self,item):
		lectureName = str(item.text())
		for row in self.rows:
			if row[1]==lectureName:
				teach_id = row[2]
				print teach_id,"showItem wale me.."
				self.s1 = est_tcp_conn.create_tcp()
				self.s1.send("get teacher ip")
				self.s1.recv(1024)
				self.s1.send(str(teach_id))
				self.MCAST_GRP = self.s1.recv(1024)
				#self.ui.close()
				break
		print "stu",self.MCAST_GRP
		self.MCAST_PORT = 7777
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind((self.MCAST_GRP, self.MCAST_PORT))
		self.mreq = struct.pack("4sl", socket.inet_aton(self.MCAST_GRP), socket.INADDR_ANY)
		self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, self.mreq)
		self.live()
	def disp(self, dat):
		buf = pickle.loads(dat)
		#print buf
		frame = cv2.imdecode(buf,0)
		cv2.imshow('ClientRecieving',frame)
		#print frame

	def archive(self):
		self.at = archiveThread(self.conn_dict)
		self.connect(self.at,QtCore.SIGNAL('display'),self.disp)
		self.at.start()

	def live(self):
		print "live"
		
		self.lc = liveConnect(self.sock)
		self.connect(self.lc,QtCore.SIGNAL('display'),self.disp)
		self.lc.start()
class CameraCapture(QtCore.QThread):
	def __init__(self,fileName):
		QtCore.QThread.__init__(self)
		self.fourcc = cv.CV_FOURCC('X','V','I','D')
		self.fn = fileName+".avi"
		self.out = cv2.VideoWriter(self.fn,self.fourcc, 20.0, (320,240))
		self.fileName = fileName

		self.cap = cv2.VideoCapture(0) 
		#capRead = cv2.VideoCapture('output.avi')
		self.cap.set(3,320)
		self.cap.set(4,240)
 	def run(self):
 		while True:
 			ret, frame = self.cap.read()
 			print frame
 			print frame/2
 			frame = frame/2
 			if ret:
	 			#out.write(frame)
				#print "aman",frame
				self.out.write(frame)
				(retval,buf) = cv2.imencode(".jpg",frame)
				ser = pickle.dumps(buf)
	 			self.emit(QtCore.SIGNAL('captureNow'),ser)
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
	 			break
	 	self.cap.release()
	 	self.out.release()
	 	s = est_tcp_conn.create_tcp()
	 	s.send("sending lecture")
	 	s.recv(1024)
	 	s.send(self.fn)
	 	f = open(self.fn,"rb")
	 	l = f.read(1024)
	 	print "sending..."
	 	i=1
	 	while len(l)>0:
	 		print i
	 		i=i+1
	 		#print sys.getsizeof(l)
	 		s.send(l)
			l = f.read(8192)
		print "i: ",i
		#print s.recv(1024)
	
		f.close()
		s.close()
	 	print "oner"
 		return
	
class TeacherGui(QtGui.QMainWindow):
	def __init__(self,ip,usr):
		QtGui.QMainWindow.__init__(self)
		self.ui = uic.loadUi('TeacherGui.ui')
		self.ui.show()
		self.MCAST_GRP = ip
		self.connect(self.ui.btnStartLecture,QtCore.SIGNAL("clicked()"),self.startLiveFeed)
		self.usr = usr
	def runCap(self,text):
		#print text
		buff = pickle.loads(text)
		
		frame = cv2.imdecode(buff,0)
		cv2.imshow('serverSending',frame)
		print "size of packet: ",sys.getsizeof(text)
		self.sock.sendto(text, (self.MCAST_GRP, self.MCAST_PORT))	
	def startLiveFeed(self):
		lectureName = self.ui.leLectureName.text()
		lectureName = str(lectureName)
		if lectureName == "":
			print "empty"
		else:
			s = est_tcp_conn.create_tcp()
			s.send("fileName")
			read = s.recv(1024)
			if read=="requesting file name":
				s.send(lectureName)
				s.recv(1024)
				s.send(self.usr)
				s.recv(1024)
		#self.MCAST_GRP = '224.1.1.1'
		self.MCAST_PORT = 7777
		print "teach",self.MCAST_GRP
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
		self.TCP_IP = '192.168.0.103'
		self.TCP_PORT = 5053
		self.BUFFER_SIZE_TCP = 20
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.bind((self.TCP_IP, self.TCP_PORT))
		
		self.capture = CameraCapture(lectureName)
		self.connect(self.capture,QtCore.SIGNAL('captureNow'),self.runCap)
		self.capture.start()
class loginScreen(QtGui.QMainWindow,QtGui.QWidget):
	def __init__(self,app1):
		QtGui.QMainWindow.__init__(self)
		self.ui = uic.loadUi('loginScreen.ui')
		self.ui.show()
		self.ui.lePwd.setEchoMode(2)
		self.connect(self.ui.BtnSignIn, QtCore.SIGNAL("clicked()"), self.getLoginData)
		self.app1 = app1
		self.ui.setStyleSheet("QMainWindow {background-image: url(online-learning.jpg);background-repeat: no-repeat}")
		#self.connect(self.ui.BtnRegister, QtCore.SIGNAL("clicked()"), self.register)
	def getLoginData(self):
		usr = self.ui.leUserId.text()
		usr = str(usr)
		pwd = self.ui.lePwd.text()
		pwd = str(pwd)
		s = est_tcp_conn.create_tcp()
		#print type(s)
		s.send("login")
		data = s.recv(1024)
		#print data
		if data == "requesting login data":
			s.send(usr)
			s.recv(1024)
			s.send(pwd)
			a = s.recv(1024)
			s.send("ack")
			#print type(a)
			#string = "('aman', 'agarwal', 1)"
			a_new = pickle.loads(a)
			if a_new != "wrong":
				print " ",a_new[0]," ",a_new[1]," ",a_new[2]
				login_val = a_new[2]
			
				if login_val == 2:
					print "student"
					self.ui.close()
					self.stu = StudentGui()
				if login_val == 1:
					ip = s.recv(1024)
					'''ipdata = pickle.loads(ipdata)
					print ipdata[1]'''
					print ip
					self.ui.close()
					self.tea = TeacherGui(ip,usr)
			else:
				print "chodina wrong password che.."
				reply = QtGui.QMessageBox.question(self, 'Message',"Wrong Username or password..!", QtGui.QMessageBox.Retry | QtGui.QMessageBox.No)

				if reply == QtGui.QMessageBox.Retry:
					print "g"
				else:
					self.ui.close()
if __name__=='__main__':
	app = QtGui.QApplication(sys.argv)
	win = loginScreen(app)
	sys.exit(app.exec_())
