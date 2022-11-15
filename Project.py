#!"C:\Python\Python310\python.exe"
#URL: https://dcm.uhcl.edu/c433322sp01ghamarya/h7.py
from dbconfig import *
import pymysql
import cgi
import cgitb
cgitb.enable()

#	Establish a cursor for MySQL connection.
db = get_mysql_param()
cnx = pymysql.connect(user=db['user'], password=db['password'],
                      host=db['host'],
                      database=db['database'])

cursor = cnx.cursor()

#	Create HTTP response header
print("Content-Type: text/html;charset=utf-8")
print()

#	Create a primitive HTML starter
print('''<html>
<head></head>
<body>
''')

#	Get HTTP parameter, ctid (caretaker id) and sid (swimmer id)
form = cgi.FieldStorage()
eid = form.getfirst('eid')

if eid is None:
    #	No HTTP parameter eid submitted: show all meets
    print('<h3>Kinds of events in meets</h3>')

    query = '''
    SELECT DISTINCT e.title, COUNT(m.MeetId) AS meetNum,
    GROUP_CONCAT(CONCAT('<li><a href=?eid=',e.eventid,'>',m.Title,' at ', v.Name,'</a></li>\n')SEPARATOR '') AS meetLocation
    FROM event AS e 
        INNER JOIN meet AS m ON (e.meetId = m.meetId)
        INNER JOIN venue AS v ON (m.venueId = v.VenueId)
    GROUP BY e.title
'''
    cursor.execute(query)
    print('<ol>')
    for (title, meetNum, meetLocation) in cursor:
        print(title + ': in ' + str(meetNum) +' meets \n<ol>\n' + meetLocation + '</ol></li>\n')

    print('</ol>')
    print('</body></html>')
    cursor.close()
    cnx.close()
    quit()

if eid is not None:  # This will always be satisfied at this point.
    #	Show meet information.

    query = '''
    WITH t1 AS(
        SELECT p.eventId,s.swimmerid,CONCAT(s.FName,' ',s.LName) AS swimmer,
        CONCAT(c.FName,' ',c.LName, ' (Primary)') AS PrimaryCaretaker
        FROM swimmer AS s 
        LEFT JOIN caretaker AS c ON (s.main_CT_Id= c.CT_Id)
        LEFT JOIN participation AS p ON (s.swimmerId = p.swimmerId)),
    t2 AS( 
        SELECT SwimmerId, GROUP_CONCAT(DISTINCT(CONCAT(c.FName,' ',c.LName)), ' (Alternate) ') AS AlternateCaretaker
        FROM othercaretaker AS o LEFT JOIN caretaker AS c ON (o.CT_Id=c.CT_Id) 
        GROUP By SwimmerId)
    SELECT eventId,GROUP_CONCAT(swimmer), GROUP_CONCAT(t2.AlternateCaretaker, ', ', t1.PrimaryCaretaker) AS CaretakerInfo
    FROM t1 LEFT JOIN t2 USING (SwimmerId)
    WHERE t1.eventid = %s
'''
    cursor.execute(query, (int(eid),))
    print(f"<h1>Swimmers in event #{eid}</h1>")
    print("<ol>")
    
    for(eventId, swimmer, caretaker) in cursor:
        #print("<li> {},{} </li>".format(swimmer, caretaker))
        constant = 1
        if caretaker == None:
            caretaker = ""
            constant = 0
        print( f"<li>{swimmer} has {caretaker.count(',')+constant} caretakers: {caretaker} </li>")
    print("</ol>")
 
    cursor.close()
    cnx.close()

print('''</body>
</html>''')
