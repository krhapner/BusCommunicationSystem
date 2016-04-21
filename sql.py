import sqlite3

with sqlite3.connect('bus_system.db') as connection:

    # get a cursor object used to execute SQL commands
    c = connection.cursor()
    c.execute ('DROP TABLE IF EXISTS USER')
    c.execute ('CREATE TABLE USER (User_id INTEGER PRIMARY KEY AUTOINCREMENT, Username TEXT NOT NULL UNIQUE, Password TEXT NOT NULL UNIQUE, Role TEXT, Student_id REFERENCES STUDENT(Student_id), Driver_id REFERENCES DRIVER(Driver_id) )' )

    c.execute ('INSERT INTO USER(Username, Password, Role) VALUES ("admin", "admin", "administrator")')
    c.execute ('INSERT INTO USER(Username, Password, Role, Driver_id) VALUES ("bus_driver1", "bs1", "bus_driver", 1)')
    c.execute ('INSERT INTO USER(Username, Password, Role, Student_id) VALUES("student_1", "st1", "student_parent", 1)')
    c.execute ('INSERT INTO USER(Username, Password, Role, Student_id) VALUES("student_2", "st2", "student_parent", 2)')
    c.execute ('INSERT INTO USER(Username, Password, Role, Student_id) VALUES("student_3", "st3", "student_parent", 3)')
    c.execute ('INSERT INTO USER(Username, Password, Role, Student_id) VALUES("daddy", "daddy", "student_parent", 4)')


    c.execute('DROP TABLE IF EXISTS MESSAGE')
    c.execute('CREATE TABLE MESSAGE(Message_id INTEGER PRIMARY KEY AUTOINCREMENT, Subject TEXT, Message TEXT, Sender TEXT, Date TEXT, Read INTEGER DEFAULT 0, Student_id REFERENCES STUDENT(Student_id), Driver_id REFERENCES DRIVER(Driver_id))')
    c.execute('INSERT INTO MESSAGE VALUES(1, "Not Riding Today", "John Smith will not be riding the bus today", "John Smith", "2016-01-01", 0, 1, 1)')
    c.execute('INSERT INTO MESSAGE VALUES(2, "Not Riding Today", "Sarah Andrews will not be riding the bus today", "Chris Andrews", "2016-01-01", 0, 1, 1)')
    c.execute('INSERT INTO MESSAGE VALUES(3, "Not Riding Today", "Billy Brown will not be riding the bus today", "Rachael Brown", "2016-01-01", 0, 1, 2)')


    c.execute('DROP TABLE IF EXISTS STUDENT')
    c.execute("CREATE TABLE STUDENT (Student_id INTEGER PRIMARY KEY AUTOINCREMENT, First_name TEXT NOT NULL, Last_name TEXT NOT NULL, Address TEXT, Birthdate TEXT CONSTRAINT Birthdate CHECK(Birthdate < date('now')), Route_number REFERENCES ROUTE(Route_number),Emergency_contact_id REFERENCES EMERGENCY_CONTACT(Emergency_contact_id), Schedule_id REFERENCES SCHEDULE(Schedule_id))")
    c.execute("INSERT INTO STUDENT VALUES(1, 'John', 'Smith', '122 W. Maple Dr.', '1995-11-16', 1, 1, 1)")
    c.execute("INSERT INTO STUDENT VALUES(2, 'Sarah', 'Andrews', '436 Oakwood Ave.', '1992-03-05', 1, 2, 2)")
    c.execute("INSERT INTO STUDENT VALUES(3, 'Billy', 'Brown', '852 S. Glenview Dr.', '1994-02-01', 2, 3, 3)")
    c.execute("INSERT INTO STUDENT VALUES(4, 'Bailey', 'Green', '4001 N. State Road 9', '1997-04-03', 2, 4, 4)")


    c.execute('DROP TABLE IF EXISTS DRIVER')
    c.execute('CREATE TABLE DRIVER (Driver_id INTEGER PRIMARY KEY AUTOINCREMENT, First_name NOT NULL, Last_name NOT NULL,Phone)')
    c.execute("INSERT INTO DRIVER VALUES(1, 'Bob', 'Driver', '765-555-5555')")
    c.execute("INSERT INTO DRIVER VALUES(2, 'Sandy', 'Rogers', '765-142-6573')")
    c.execute("INSERT INTO DRIVER VALUES(3, 'Charlie', 'Jones', '594-245-2854')")
    c.execute("INSERT INTO DRIVER VALUES(4, 'Maren', 'Conely', '765-257-3424')")
    c.execute("INSERT INTO DRIVER VALUES(5, 'Pat', 'Richardson', '854-654-1325')")

    c.execute('DROP TABLE IF EXISTS BUS')
    c.execute('CREATE TABLE BUS (Bus_number INTEGER PRIMARY KEY AUTOINCREMENT, Make TEXT, Model TEXT, Year TEXT, Capacity INTEGER)')
    c.execute('INSERT INTO BUS VALUES (1,"Blue Bird", "Type B", "2002", 1)')
    c.execute('INSERT INTO BUS VALUES (2, "Blue Bird", "Type C", "2007", 100)')
    c.execute('INSERT INTO BUS VALUES (3, "General Motors", "Type A", "1995", 25)')
    c.execute('INSERT INTO BUS VALUES (4, "General Motors", "Type B", "1995", 50)')
    c.execute('INSERT INTO BUS VALUES (5, "Ford", "Type D", "1992", 65)')

    c.execute('DROP TABLE IF EXISTS ROUTE')
    c.execute('CREATE TABLE ROUTE (Route_number INTEGER PRIMARY KEY AUTOINCREMENT, Pick_up_location TEXT,Start_time TEXT,Drop_off_location TEXT,End_time TEXT,Condition_id REFERENCES CONDITION(Condition_id) DEFAULT 1,Bus_number REFERENCES BUS(Bus_number), Driver_id REFERENCES DRIVER(Driver_id))')
    c.execute('INSERT INTO ROUTE VALUES(1, "Hamilton Village", "7:00AM", "West View Middle School", "8:00AM", 1, 1, 1)')
    c.execute('INSERT INTO ROUTE VALUES(2, "Country Village", "8:00AM", "West View High School", "9:00AM", 1, 2, 1)')
    c.execute('INSERT INTO ROUTE VALUES(3, "Haltemon Neighborhood", "6:00AM", "West View Elementary", "7:00AM", 1, 3, 2)')
    c.execute('INSERT INTO ROUTE VALUES(4, "Creekwood Neighborhood", "8:00AM", "West View High School", "9:00AM", 1, 4, 3)')
    c.execute('INSERT INTO ROUTE VALUES(5, "Country Village", "7:00AM", "West View Middle School", "8:00AM", 1, 5, 4)')


    c.execute('DROP TABLE IF EXISTS CONDITION')
    c.execute('CREATE TABLE CONDITION (Condition_id INTEGER PRIMARY KEY AUTOINCREMENT, Color TEXT NOT NULL,Description TEXT,Minutes_late TEXT)')
    c.execute('INSERT INTO CONDITION(Color, Description, Minutes_late) VALUES ("Green", "Route is running on time", "0")')
    c.execute('INSERT INTO CONDITION(Color, Description, Minutes_late) VALUES ("Green", "Route is running a few minutes late.", "3-5")')
    c.execute('INSERT INTO CONDITION(Color, Description, Minutes_late) VALUES ("Yellow", "Route is running on the late side.", "5-8")')
    c.execute('INSERT INTO CONDITION(Color, Description, Minutes_late) VALUES ("Yellow", "Route is late, but students will still get to school on time.", "8-10")')
    c.execute('INSERT INTO CONDITION(Color, Description, Minutes_late) VALUES ("Red", "Route is late, students will get to school a little late", "10-20")')
    c.execute('INSERT INTO CONDITION(Color, Description, Minutes_late) VALUES ("Red", "Route is very late, expect to miss some class time.", "20-30")')
    c.execute('INSERT INTO CONDITION(Color, Description, Minutes_late) VALUES ("Red", "Route is very late, if possible find a ride. If not you will be late to school and miss class, but it will be excused.", "30 and beyond")')

    c.execute('DROP TABLE IF EXISTS EMERGENCY_CONTACT')
    c.execute('CREATE TABLE EMERGENCY_CONTACT (Emergency_contact_id INTEGER PRIMARY KEY AUTOINCREMENT,First_name TEXT NOT NULL,Last_name TEXT NOT NULL, Relationship TEXT NOT NULL, Phone TEXT NOT NULL)')
    c.execute('INSERT INTO EMERGENCY_CONTACT VALUES(1, "Amanda", "Smith", "Mother", "765-333-3333")')
    c.execute('INSERT INTO EMERGENCY_CONTACT VALUES(2, "Chris", "Andrews", "Father", "631-233-1423")')
    c.execute('INSERT INTO EMERGENCY_CONTACT VALUES(3, "Rachael", "Brown", "Mother", "765-123-2346")')
    c.execute('INSERT INTO EMERGENCY_CONTACT VALUES(4, "Janine", "Lyons", "Friend of family", "671-234-5409")')



    c.execute('DROP TABLE IF EXISTS SCHEDULE')
    c.execute('CREATE TABLE SCHEDULE (Schedule_id INTEGER PRIMARY KEY AUTOINCREMENT, Monday INTEGER DEFAULT 0,Tuesday INTEGER DEFAULT 0,Wednesday INTEGER DEFAULT 0,Thursday INTEGER DEFAULT 0, Friday INTEGER DEFAULT 0)')
    c.execute('INSERT INTO SCHEDULE VALUES(1, 1, 1, 1, 1, 1)')
    c.execute('INSERT INTO SCHEDULE VALUES(2, 1, 1, 0, 1, 1)')
    c.execute('INSERT INTO SCHEDULE VALUES(3, 1, 0, 1, 0, 1)')
    c.execute('INSERT INTO SCHEDULE VALUES(4, 0, 1, 0, 1, 0)')





