import MySQLdb, re
from getpass import getpass
from gradesource import Gradesource
from BeautifulSoup import BeautifulSoup
from termcolor import *

def importNames():
    g = Gradesource('qpleple', getpass())

    conn = MySQLdb.connect(host = "localhost", user = "root", passwd = "root", db = "ta")
    cursor = conn.cursor()

    for (gs_name, email) in g.emails().items():
        print "%s, %s" % (gs_name, email)
        cursor.execute("SELECT id FROM students WHERE email = '%s'" % email)
        if cursor.fetchone() == None:
            sql = "INSERT INTO students (gs_name, email, class) VALUES ('%s', '%s', '101')" % (gs_name, email)
            cursor.execute(sql)

    cursor.close()
    conn.commit()
    conn.close()

def importPictureIds():
    conn = MySQLdb.connect(host = "localhost", user = "root", passwd = "root", db = "ta")
    cursor = conn.cursor()

    for i in xrange(1,7):
        cprint('Processing file %s' % i, 'green')
        with open('/Users/qt/Dropbox/101/photos fa12/photo%s/index.html' % i, 'r') as html:
            soup = BeautifulSoup(html)
            table = soup('font', text = re.compile("Class List Photos"))[0].parent.parent.parent.find('table')

            for td in table('td', valign='top'):
                gs_name = td.text
                cprint(gs_name, 'yellow')
                m = re.match(r"^.*=(.*)\.jpg.*$", td.a['href'])
                try:
                    picId = m.group(1)
                    print 'pic id: ' + picId
                    sql = "UPDATE students SET picture_id = '%s' WHERE gs_name = '%s'" % (picId, gs_name)
                    cursor.execute(sql)
                except:
                    cprint('Error in parsing pic id', 'red')

    cursor.close()
    conn.commit()
    conn.close()

def fetchOneAssoc(cursor) :
    data = cursor.fetchone()
    if data == None :
        return None
    desc = cursor.description

    dict = {}

    for (name, value) in zip(desc, data) :
        dict[name[0]] = value

    return dict

def syncAssignment(gradesourceId, taId):
    conn = MySQLdb.connect(host = "localhost", user = "root", passwd = "root", db = "ta")
    cursor = conn.cursor()

    sql = """SELECT sc.*, st.gs_name
             FROM scores sc
             LEFT JOIN students st ON st.id = sc.student_id
             WHERE assignment_id = '%s'
             """ % taId
    cursor.execute(sql)

    scores = {}
    while True:
        row = fetchOneAssoc(cursor)
        if row == None:
            break
        print colored(row['score'], 'green'), row['gs_name']
        scores[row['gs_name']] = row['score']

    g = Gradesource('qpleple', getpass())
    g.importScores(scores, gradesourceId)

    cursor.close()
    conn.commit()
    conn.close()

# syncAssignment(gradesourceId = 435682, taId = 2)








