import psycopg2

try:
    conn = psycopg2.connect(database = "201201065", user = "201201065", password="201201065", host="10.100.71.21",port="5432")
    print "success"
except:
    print "I am unable to connect to the database"
cur = conn.cursor()
def getArchives():
    cur.execute("SELECT * FROM cns.archives")
    rows = cur.fetchall()
    return rows
def insertNewLecture(filename):
    print "inserting new lecture"
    cur.execute("INSERT INTO cns.archives (arch_name,course) values (%s,%s)",(filename,filename))
    conn.commit()
    return
def deleteLecture(filename):
    print "deleteLecture me.."
    cur.execute("SELECT * FROM cns.teacher")
    rows = cur.fetchall()
    #command = "DELETE * FROM cns.live_lectures WHERE lecture_name=",
    a="1"
    cur.execute('DELETE FROM cns.live_lectures WHERE live_name=%s or live_name=%s',(filename,a))
    conn.commit()
    return
def getIp(teach_id):
    print "loginCheck me.."
    cur.execute("SELECT * FROM cns.teacher")
    rows = cur.fetchall()
    for row in rows:
        if row[0]==teach_id:
            print "ip from loginCheck: ",row[4]
            return row[4]
def getLiveLecture():
    cur.execute("SELECT * FROM cns.live_lectures")
    rows = cur.fetchall()
    return rows
def addFileName(filename,usrid):
    print "filename:",filename
    print "user: ",usrid
    cur.execute("SELECT * FROM cns.teacher")
    teacher_id = 0
    rows = cur.fetchall()
    for row in rows:
        if row[3]==usrid:
            teacher_id = row[0]
    print teacher_id
    a =7
    cur.execute("INSERT INTO cns.live_lectures (live_name,teach_id) values (%s,%s)",(filename,teacher_id))
    conn.commit()

def get_ip(usrid):
    print type(usrid)
    cur.execute("SELECT * FROM cns.login")
    rows = cur.fetchall()
    print rows
    return rows
def login(usr,pwd):

    cur.execute("SELECT * FROM cns.loginData WHERE userId=%s and pwd=%s",(usr,pwd))
    rows = cur.fetchall()
    print "aman hello..."
    print rows
    if rows:
        for row in rows:
            print " ",row[0]," ",row[1]," ",row[2]
            a = row
            return a
    else:
        return "wrong"
if __name__ == '__main__':
    print(login("chirag","mehta"))
