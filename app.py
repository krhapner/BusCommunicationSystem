# import the Flask class from the flask module
from flask import Flask, render_template, redirect, url_for, request, session, flash, g
from functools import wraps
import sqlite3
import datetime

# create the application object
app = Flask(__name__)

# config
app.secret_key = 'my precious'
app.database = 'bus_system.db'




# login required decorator
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap

def is_admin(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'is_admin' in session:
            return f(*args, **kwargs)
        else:
            flash('Only Admin is Allowed To Access That Page')
            return redirect(url_for('login'))
    return wrap

def is_bus_driver(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'is_bus_driver' in session:
            return f(*args, **kwargs)
        else:
            flash('Only Admin/Bus Driver is Allowed To Access That Page')
            return redirect(url_for('login'))
    return wrap

# use decorators to link the function to a url
@app.route('/')
def home():
  return render_template('index.html')


@app.route('/admin', methods=['GET', 'POST'])
@login_required
@is_admin
def admin():
    g.db = connect_db()
    g.db.text_factory = str
    cur = g.db.execute('select COUNT(Route_number) from ROUTE WHERE Condition_id > 1 AND Condition_id < 4')
    yellow_buses = cur.fetchone()
    cur = g.db.execute('select COUNT(Route_number) from ROUTE WHERE Condition_id < 2')
    On_time_buses = cur.fetchone()
    cur = g.db.execute('select COUNT(Route_number) from ROUTE WHERE Condition_id > 3')
    very_late = cur.fetchone()
    cur = g.db.execute('SELECT Route_number FROM ROUTE AS R JOIN BUS AS B ON R.Bus_number = B.Bus_number GROUP BY Route_number HAVING (SELECT COUNT(Student_id) FROM ROUTE AS R JOIN STUDENT AS S ON R.Route_number = S.Route_number GROUP BY R.Route_number) >= capacity')
    past_capacity = [dict(Route_number = row[0]) for row in cur.fetchall()]


        #cur = g.db.execute('SELECT * FROM USER ')
        #return   render_template('student_added.html', Students = Students)
    g.db.close()
    return render_template('admin.html', yellow_buses = yellow_buses, On_time_buses = On_time_buses, very_late = very_late, past_capacity = past_capacity)  # render a template
    # return "Hello, World!"  # return a string

@app.route('/show_all_students', methods = ['GET', 'POST'])
@is_admin
def show_all_students():
    g.db = connect_db()
    stud = g.db.execute('select * from STUDENT AS S JOIN EMERGENCY_CONTACT AS E ON S.Emergency_contact_id = E.Emergency_contact_id JOIN SCHEDULE AS SCH ON S.Schedule_id = SCH.Schedule_id')
    Students = [dict(Student_id = row[0], First_name = row[1], Last_name = row[2], Address = row[3], Birthdate = row[4], Route_number = row[5], Emergency_Contact_id = row[8], Emer_First_name = row[9], Emer_Last_name = row[10], Relationship = row[11], Phone = row[12], Schedule_id = row[13], Monday = row[14], Tuesday = row [15], Wednesday = row[16], Thursday = row[17], Friday = row[18]) for row in stud.fetchall()]
    g.db.close()
    return render_template('show_all_students.html', Students = Students)

@app.route('/edit_student/<student_id>', methods = ['GET', 'POST'])
@is_admin
def edit_student(student_id):
    g.db = connect_db()
    route = g.db.execute('SELECT Route_number FROM ROUTE')
    Routes = [dict(Route_number = row[0])  for row in route.fetchall()]
    stud = g.db.execute('select * from STUDENT AS S JOIN EMERGENCY_CONTACT AS E ON S.Emergency_contact_id = E.Emergency_contact_id JOIN SCHEDULE AS SCH ON S.Schedule_id = SCH.Schedule_id WHERE S.Student_id = %s' % student_id)
    Students = [dict(Student_id = row[0], First_name = row[1], Last_name = row[2], Address = row[3], Birthdate = row[4], Route_number = row[5], Emergency_Contact_id = row[8], Emer_First_name = row[9], Emer_Last_name = row[10], Relationship = row[11], Phone = row[12], Schedule_id = row[13], Monday = row[14], Tuesday = row [15], Wednesday = row[16], Thursday = row[17], Friday = row[18]) for row in stud.fetchall()]
    if request.method == 'POST':
        g.db = connect_db()
        emer_firstname = request.form.get('emer_firstname')
        emer_lastname = request.form.get('emer_lastname')
        relationship = request.form.get('relationship')
        phone = request.form.get('phone')
        cur = g.db.execute('Select Emergency_contact_id FROM STUDENT WHERE Student_id = %s' % student_id)
        emer_contact_id = cur.fetchone()[0]
        emer_values = (emer_firstname, emer_lastname, relationship, phone, emer_contact_id)
        g.db.execute("UPDATE EMERGENCY_CONTACT SET First_name = '%s',  Last_name = '%s', Relationship = '%s', Phone = '%s' WHERE Emergency_contact_id = %s" % emer_values)
        g.db.commit()
        monday = (0 if request.form.get('monday') != '1' else 1)
        tuesday = (0 if request.form.get('tuesday') != '1' else 1)
        wednesday = (0 if request.form.get('wednesday')!= '1' else 1)
        thursday = (0 if request.form.get('thursday') != '1' else 1)
        friday = (0 if request.form.get('friday') !='1' else 1)
        cur = g.db.execute('SELECT Schedule_id FROM STUDENT WHERE Student_id = %s' % student_id)
        schedule_id = cur.fetchone()[0]
        g.db.execute('UPDATE SCHEDULE SET Monday = %s, Tuesday = %s, Wednesday = %s, Thursday =%s, Friday =%s WHERE Schedule_id = %s' % (monday, tuesday, wednesday, thursday, friday, schedule_id))
        g.db.commit()
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        address = request.form.get('address')
        birthdate = request.form.get('birthdate')
        route_number = request.form.get('route_number')
        route_number = int(route_number)
        g.db.text_factory = str
        values = ( firstname, lastname, address, birthdate, route_number, emer_contact_id, schedule_id, student_id)
        g.db.execute("UPDATE STUDENT SET First_name = '%s', Last_name = '%s', Address = '%s', Birthdate = '%s', Route_number = %s, Emergency_contact_id = %s, Schedule_id = %s WHERE Student_id = %s" % values)
        g.db.commit()
        g.db.close()

        return redirect(url_for('show_all_students'))
    return render_template('edit_student.html', Students = Students, Routes = Routes)

@app.route('/student_message/<student_id>', methods = ['GET', 'POST'])
def student_message(student_id):
  if request.method == "POST":
    g.db = connect_db()
    cur = g.db.execute('SELECT Driver_id FROM STUDENT AS S JOIN ROUTE AS R ON S.Route_number = R.Route_number WHERE Student_id = %s' % student_id)
    driver_id = cur.fetchone()[0]
    subject = request.form['subject']
    message = request.form.get('message')
    sender = request.form['sender']
    date  = datetime.datetime.today().strftime("%Y-%m-%d")
    values = (subject, message, sender, date, student_id, driver_id)
    g.db.execute('INSERT INTO MESSAGE(Subject, Message, Sender, Date, Student_id, Driver_id) VALUES (?,?,?,?,?,?)', values)
    g.db.commit()
    route_info = g.db.execute("SELECT * FROM STUDENT AS S JOIN ROUTE AS R ON S.Route_number = R.Route_number JOIN CONDITION AS C ON R.Condition_id = C.Condition_id WHERE Student_id = '%s' " % (student_id))
    Route_info = [dict(First_name = row[1], Last_name = row[2], Address = row[3], Birthdate = row[4], Pick_up_location = row[9], Start_time = row[10], Drop_off_location = row[11], End_time = row[12], Color = row[17], Description = row[18], Minutes_late = row[19]) for row in route_info.fetchall()]
    g.db.close()
    flash('Message Sent!')
    return render_template('student_parent_view.html', student_id = student_id, Route_info = Route_info)

  return render_template('student_message.html', student_id = student_id)

@app.route('/bus_driver_message/<driver_id>', methods = ['GET', 'POST'])
def bus_driver_message(driver_id):
  g.db = connect_db()
  cur = g.db.execute('SELECT * FROM MESSAGE WHERE Driver_id = %s' % driver_id )
  messages = [dict(Message_id = row[0], Subject = row[1], Message = row[2], Sender = row[3], Date = row[4], Read = row[5], Student_id = row[6], Driver_id = row[7]) for row in cur.fetchall()]
  return render_template('bus_driver_message.html', driver_id = driver_id, messages = messages)

@app.route('/delete_message/<driver_id>/<message_id>', methods=['GET','POST'])
def delete_message(driver_id,message_id):
  g.db = connect_db()
  g.db.execute('DELETE FROM MESSAGE WHERE Message_id = %s' % message_id)
  g.db.commit()
  cur = g.db.execute('SELECT * FROM MESSAGE WHERE Driver_id = %s' % driver_id )
  messages = [dict(Message_id = row[0], Subject = row[1], Message = row[2], Sender = row[3], Date = row[4], Read = row[5], Student_id = row[6], Driver_id = row[7]) for row in cur.fetchall()]
  g.db.close()
  flash('Message Deleted')
  return render_template('bus_driver_message.html', driver_id = driver_id, messages=messages)

@app.route('/update_message/<driver_id>/<message_id>', methods=['GET','POST'])
def update_message(driver_id, message_id):
  g.db = connect_db()
  cur = g.db.execute('UPDATE MESSAGE SET Read = 1 WHERE Message_id =%s' % message_id)
  g.db.commit()
  cur = g.db.execute('SELECT * FROM MESSAGE WHERE Driver_id = %s' % driver_id )
  messages = [dict(Message_id = row[0], Subject = row[1], Message = row[2], Sender = row[3], Date = row[4], Read = row[5], Student_id = row[6], Driver_id = row[7]) for row in cur.fetchall()]
  g.db.close()
  return render_template('bus_driver_message.html', driver_id = driver_id, messages=messages)

@app.route('/new_student', methods = ['GET', 'POST'])
@is_admin
def new_student():
    g.db = connect_db()
    route = g.db.execute('SELECT Route_number FROM ROUTE')
    Routes = [dict(Route_number = row[0])  for row in route.fetchall()]
    if request.method == 'POST':
        g.db = connect_db()
        emer_firstname = request.form['emer_firstname']
        emer_lastname = request.form['emer_lastname']
        relationship = request.form['relationship']
        phone = request.form['phone']
        emer_values = (emer_firstname, emer_lastname, relationship, phone)
        g.db.execute('INSERT INTO EMERGENCY_CONTACT(First_name, Last_name, Relationship, Phone) VALUES(?,?,?,?)', emer_values)
        g.db.commit()

        monday = (0 if request.form.get('monday') != '1' else 1)
        tuesday = (0 if request.form.get('tuesday') != '1' else 1)
        wednesday = (0 if request.form.get('wednesday')!= '1' else 1)
        thursday = (0 if request.form.get('thursday') != '1' else 1)
        friday = (0 if request.form.get('friday') !='1' else 1)
        g.db.execute('INSERT INTO SCHEDULE(Monday, Tuesday, Wednesday, Thursday, Friday) VALUES(?,?,?,?,?)', (monday, tuesday, wednesday, thursday, friday))
        g.db.commit()
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        address = request.form['address']
        birthdate = request.form['birthdate']
        route_number = request.form.get('route_number')
        route_number = int(route_number)
        g.db.text_factory = str
        cur = g.db.execute('SELECT MAX(Emergency_contact_id) FROM EMERGENCY_CONTACT')
        emergency_contact_id = cur.fetchone()[0]
        cur1 = g.db.execute('SELECT MAX(Schedule_id) FROM SCHEDULE')
        schedule_id = cur1.fetchone()[0]
        values = ( firstname, lastname, address, birthdate, route_number, emergency_contact_id, schedule_id)
        g.db.execute('INSERT INTO STUDENT(First_name, Last_name, Address, Birthdate, Route_number, Emergency_contact_id, Schedule_id) VALUES(?,?,?,?,?,?,?)', values)
        g.db.commit()
        g.db.close()
        flash('Record was successfully added')
        return redirect(url_for('show_all_students'))
    return render_template('new_student.html', Routes=Routes)

@app.route('/show_all_bus_drivers', methods = ['GET', 'POST'])
@is_admin
def show_all_bus_drivers():

    g.db = connect_db()
    driver = g.db.execute('select * from DRIVER')
    Drivers = [dict(Driver_id = row[0], First_name = row[1], Last_name = row[2], Phone = row[3]) for row in driver.fetchall()]
    g.db.close()
    return render_template('show_all_bus_drivers.html', Drivers = Drivers)

@app.route('/edit_bus_driver/<driver_id>', methods = ['GET', 'POST'])
@is_admin
def edit_bus_driver(driver_id):
    g.db = connect_db()
    driver = g.db.execute('select * from DRIVER where Driver_id = %s' % driver_id)
    Drivers = [dict(Driver_id = row[0], First_name = row[1], Last_name = row[2], Phone = row[3]) for row in driver.fetchall()]
    if request.method == 'POST':
        g.db = connect_db()
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        phone = request.form.get('phone')
        values = ( firstname, lastname, phone, driver_id)
        g.db.execute("UPDATE DRIVER SET First_name = '%s', Last_name = '%s', Phone = '%s' WHERE Driver_id = %s" % values)
        g.db.commit()
        return redirect(url_for('show_all_bus_drivers'))
    g.db.close()
    return render_template('edit_bus_driver.html', Drivers = Drivers)


@app.route('/new_bus_driver', methods = ['GET', 'POST'])
@is_admin
def new_bus_driver():
    if request.method == 'POST':
        g.db = connect_db()
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        phone = request.form['phone']
        values = ( firstname, lastname, phone)
        g.db.execute('INSERT INTO DRIVER(First_name, Last_name, Phone) VALUES(?,?,?)', values)
        g.db.commit()
        g.db.close()
        flash('Record was successfully added')
        return redirect(url_for('show_all_bus_drivers'))
    return render_template('new_bus_driver.html')


@app.route('/show_all_buses', methods = ['GET', 'POST'])
@is_admin
def show_all_buses():
    g.db = connect_db()
    bus = g.db.execute('select * from BUS')
    Buses = [dict(Bus_number = row[0], Make = row[1], Model = row[2], Year = row[3], Capacity = row[4]) for row in bus.fetchall()]
    g.db.close()
    return render_template('show_all_buses.html', Buses = Buses)

@app.route('/edit_bus/<bus_number>', methods = ['GET', 'POST'])
@is_admin
def edit_bus(bus_number):
    bus_number = int(bus_number)
    g.db = connect_db()
    bus = g.db.execute("Select * from BUS WHERE Bus_number = %s" % bus_number)
    Buses = [dict(Make = row[1], Model = row[2], Year = row[3], Capacity = row[4]) for row in bus.fetchall()]
    g.db.close()
    if request.method =="POST":
        make= request.form.get('make')
        model = request.form.get('model')
        year = request.form.get('year')
        capacity = request.form.get('capacity')
        values = (make, model, year, capacity, bus_number)
        g.db = connect_db()
        g.db.execute("UPDATE BUS SET Make = '%s', Model = '%s', Year ='%s', Capacity = '%s' WHERE Bus_number = %s " % values)
        g.db.commit()
        g.db.close()

        return redirect(url_for('show_all_buses'))
    return render_template('edit_bus.html', Buses = Buses)

@app.route('/new_bus', methods = ['GET', 'POST'])
@is_admin
def new_bus():
    if request.method == 'POST':
        g.db = connect_db()
        make= request.form['make']
        model = request.form['model']
        year = request.form['year']
        capacity = request.form['capacity']
        values = (make, model, year, capacity)
        g.db.execute('INSERT INTO BUS(Make, Model, Year, Capacity) VALUES(?,?,?,?)', values)
        g.db.commit()
        g.db.close()
        flash('Record was successfully added')
        return redirect(url_for('show_all_buses'))
    return render_template('new_bus.html')

@app.route('/new_route', methods = ['GET', 'POST'])
@is_admin
def new_route():
    g.db = connect_db()
    bus = g.db.execute('SELECT Bus_number FROM BUS')
    Buses = [dict(Bus_number = row[0])  for row in bus.fetchall()]
    driver = g.db.execute('SELECT * FROM DRIVER')
    Drivers = [dict(Driver_id = row[0], First_name = row[1], Last_name = row[2], Phone = row[3]) for row in driver.fetchall()]
    if request.method == 'POST':
        pick_up_location = request.form['pick_up_location']
        start_time = request.form['start_time']
        drop_off_location = request.form['drop_off_location']
        end_time = request.form['end_time']
        bus_number = request.form.get('bus_number')
        driver_id = request.form.get('driver_id')
        driver_id = int(driver_id)
        bus_number = int(bus_number)
        values = (pick_up_location, start_time, drop_off_location, end_time, bus_number, driver_id)
        g.db.execute('INSERT INTO ROUTE(Pick_up_location, Start_time, Drop_off_location, End_time, Bus_number, Driver_id) VALUES(?,?,?,?,?,?)', values)
        g.db.commit()
        g.db.close()
        flash('Record was successfully added')
        return redirect(url_for('show_all_routes'))
    g.db.close()
    return render_template('new_route.html', Drivers=Drivers, Buses=Buses)

@app.route('/edit_route/<route_number>', methods = ['GET', 'POST'])
@is_admin
def edit_route(route_number):
    route_number = int(route_number)
    g.db = connect_db()
    route = g.db.execute("Select * from route AS R JOIN CONDITION AS C ON R.Condition_id = C.Condition_id WHERE route_number = %s" % route_number)
    Routes = [dict(Route_number = row[0], Pick_up_location = row[1], Start_time = row[2], Drop_off_location = row[3], End_time = row[4], Bus_number = row[6], Driver_id = row[7], Minutes_late = row[11]) for row in route.fetchall()]
    bus = g.db.execute('SELECT Bus_number FROM BUS')
    Buses = [dict(Bus_number = row[0])  for row in bus.fetchall()]
    driver = g.db.execute('SELECT * FROM DRIVER')
    Drivers = [dict(Driver_id = row[0], First_name = row[1], Last_name = row[2], Phone = row[3]) for row in driver.fetchall()]
    minutes = g.db.execute('SELECT Condition_id,Minutes_late FROM CONDITION')
    Condition = [dict(Condition_id = row[0], Minutes_late = row[1]) for row in minutes.fetchall()]
    if request.method =="POST":
        pick_up_location = request.form['pick_up_location']
        start_time = request.form['start_time']
        drop_off_location = request.form['drop_off_location']
        end_time = request.form['end_time']
        bus_number = request.form.get('bus_number')
        driver_id = request.form.get('driver_id')
        driver_id = int(driver_id)
        bus_number = int(bus_number)
        condition_id = request.form.get('condition_id')
        values = (pick_up_location, start_time, drop_off_location, end_time, bus_number, driver_id, condition_id, route_number)
        g.db.execute("UPDATE ROUTE SET Pick_up_location = '%s', Start_time = '%s', Drop_off_location = '%s', End_time = '%s', Bus_number = %s, Driver_id = %s, Condition_id = %s WHERE Route_number = %s" % values)

        g.db.commit()
        g.db.close()

        return redirect(url_for('show_all_routes'))
    g.db.close()
    return render_template('edit_route.html', Routes = Routes, Drivers = Drivers, Buses = Buses, Condition = Condition)

@app.route('/show_all_routes', methods = ['GET', 'POST'])
@is_admin
def show_all_routes():
    g.db = connect_db()
    route = g.db.execute('select Route_number, Pick_up_location, Start_time, Drop_off_location, End_Time, Minutes_Late from ROUTE JOIN CONDITION ON ROUTE.Condition_id = CONDITION.condition_id')
    Routes = [dict(Route_number = row[0], Pick_up_location = row[1], Start_time = row[2], Drop_off_location = row[3], End_time = row[4], Minutes_late = row[5] ) for row in route.fetchall()]
    g.db.close()
    return render_template('show_all_routes.html', Routes = Routes)



@app.route('/bus_driver/<driver_id>', methods = ['GET', 'POST'])
@is_bus_driver
def bus_driver(driver_id):
    g.db = connect_db()
    cur = g.db.execute('SELECT Route_number FROM ROUTE WHERE Driver_id = %s' % driver_id)
    route_number = cur.fetchone()[0]
    emergency = g.db.execute("Select S.First_name, S.Last_name, E.First_name, E.Last_name, Relationship, Phone FROM STUDENT AS S JOIN EMERGENCY_CONTACT AS E ON S.Emergency_contact_id = E.Emergency_contact_id WHERE Route_number = %s " % route_number)
    Emergency_contact = [dict(First_name = row[0], Last_name = row[1], Emer_First_name = row[2], Emer_Last_name = row[3], Relationship = row[4], Phone = row[5]) for row in emergency.fetchall()]
    cur = g.db.execute('SELECT COUNT(*) FROM MESSAGE WHERE Driver_id = %s AND Read = 0' % driver_id)
    show_red = cur.fetchone()[0]


    return render_template('bus_driver.html', driver_id = driver_id,  Emergency_contact = Emergency_contact, route_number = route_number, show_red = show_red)




@app.route('/view_students_riding_today/<driver_id>', methods = ['GET', 'POST'])
@is_bus_driver
def view_students_riding_today(driver_id):
  cur = datetime.datetime.today().weekday()
  if cur == 1:
    day = "Tuesday"
  elif cur == 2:
    day = "Wednesday"
  elif cur == 3:
    day = "Thursday"
  elif cur == 4:
    day = "Friday"
  else:
    day = "Monday"

  g.db = connect_db()

  cur = g.db.execute('SELECT * FROM STUDENT AS S JOIN SCHEDULE AS SCH on S.Schedule_id = SCH.Schedule_id JOIN ROUTE AS R ON S.Route_number = R.Route_number WHERE %s = 1 AND Driver_id = %s' % (day,driver_id))
  Students = [dict(Student_id = row[0], First_name = row[1], Last_name = row[2], Address = row[3], Birthdate = row[4]) for row in cur.fetchall()]
  return render_template('view_students_riding_today.html', driver_id = driver_id, Students = Students, day = day)

@app.route('/bus_driver_edit_route/<driver_id>', methods = ['GET', 'POST'])
@is_bus_driver
def bus_driver_edit_route(driver_id):
  g.db = connect_db()
  cur = g.db.execute('SELECT Condition_id, Minutes_late FROM CONDITION')
  Conditions = [dict(Condition_id = row[0], Minutes_late = row[1]) for row in cur.fetchall()]
  route = g.db.execute('SELECT Route_number FROM ROUTE WHERE Driver_id = %s' % driver_id)
  Routes = [dict(Route_number = row[0])  for row in route.fetchall()]
  if request.method == 'POST':
    route_number = request.form.get('route_number')
    route_number = int(route_number)
    condition_id = request.form.get('condition_id')
    g.db.execute("UPDATE ROUTE SET Condition_id = %s WHERE Route_number = %s" % (condition_id, route_number))
    g.db.commit()
    g.db.close()
    flash('Route has been updated!')
    return redirect(url_for('bus_driver', driver_id = driver_id))
  g.db.close()
  return render_template('bus_driver_edit_route.html', driver_id = driver_id,  Conditions = Conditions, Routes = Routes)



@app.route('/student_parent_view/<student_id>', methods = ['GET', 'POST'])
@login_required
def student_parent_view(student_id):
    g.db = connect_db()
    student_id = int(student_id)
    route_info = g.db.execute("SELECT * FROM STUDENT AS S JOIN ROUTE AS R ON S.Route_number = R.Route_number JOIN CONDITION AS C ON R.Condition_id = C.Condition_id WHERE Student_id = %s " % (student_id))
    Route_info = [dict(First_name = row[1], Last_name = row[2], Address = row[3], Birthdate = row[4], Pick_up_location = row[9], Start_time = row[10], Drop_off_location = row[11], End_time = row[12], Color = row[17], Description = row[18], Minutes_late = row[19]) for row in route_info.fetchall()]
    cur = g.db.execute('SELECT D.First_name, D.Last_name, D.Phone FROM DRIVER AS D JOIN ROUTE AS R ON R.Driver_id = D.Driver_id JOIN STUDENT AS S ON S.Route_number = R.Route_number WHERE Student_id = %s' % student_id)
    driver_info = [dict(Driver_First_name = row[0], Driver_Last_name = row[1], Driver_Phone = row[2]) for row in cur.fetchall()]
    return render_template('student_parent_view.html', Route_info = Route_info, student_id = student_id, driver_info = driver_info)

@app.route('/welcome')
def welcome():
    return render_template('welcome.html')  # render a template

@app.route('/sign_up', methods = ['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        g.db = connect_db()
        emer_firstname = request.form['emer_firstname']
        emer_lastname = request.form['emer_lastname']
        relationship = request.form['relationship']
        phone = request.form['phone']
        emer_values = (emer_firstname, emer_lastname, relationship, phone)
        g.db.execute('INSERT INTO EMERGENCY_CONTACT(First_name, Last_name, Relationship, Phone) VALUES(?,?,?,?)', emer_values)
        g.db.commit()

        monday = (0 if request.form.get('monday') != '1' else 1)
        tuesday = (0 if request.form.get('tuesday') != '1' else 1)
        wednesday = (0 if request.form.get('wednesday')!= '1' else 1)
        thursday = (0 if request.form.get('thursday') != '1' else 1)
        friday = (0 if request.form.get('friday') !='1' else 1)
        g.db.execute('INSERT INTO SCHEDULE(Monday, Tuesday, Wednesday, Thursday, Friday) VALUES(?,?,?,?,?)', (monday, tuesday, wednesday, thursday, friday))
        g.db.commit()
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        address = request.form['address']
        birthdate = request.form['birthdate']
        g.db.text_factory = str
        cur = g.db.execute('SELECT MAX(Emergency_contact_id) FROM EMERGENCY_CONTACT')
        emergency_contact_id = cur.fetchone()[0]
        cur1 = g.db.execute('SELECT MAX(Schedule_id) FROM SCHEDULE')
        schedule_id = cur1.fetchone()[0]
        values = ( firstname, lastname, address, birthdate, emergency_contact_id, schedule_id)
        g.db.execute('INSERT INTO STUDENT(First_name, Last_name, Address, Birthdate, Emergency_contact_id, Schedule_id) VALUES(?,?,?,?,?,?)', values)
        cur = g.db.execute('SELECT MAX(Student_id) FROM STUDENT')
        student_id = cur.fetchone()[0]
        username = request.form['username']
        password = request.form['password']
        role = 'student_parent'
        values = (username, password, role, student_id)
        g.db.execute('INSERT INTO USER(Username, Password, Role, Student_id) VALUES(?,?,?,?)', values)
        g.db.commit()
        g.db.close()
        flash('Account Successfully Created')
        return redirect(url_for('login'))
    return render_template('sign_up.html')

# route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        g.db = connect_db()
        g.db.text_factory = str
        username = request.form['username']
        password = request.form['password']
        cur = g.db.execute("SELECT Role FROM USER WHERE Username = '" + username + "' AND Password = '" + password + "'" )
        role = cur.fetchone();
        if not role:
          error = 'Invalid Credentials. Please try again.'
        elif role[0]== 'administrator':
            session['logged_in'] = True
            session['is_admin'] = True
            session['is_bus_driver'] = True
            flash('You were logged in.')
            return redirect(url_for('admin'))
        elif role[0] == 'bus_driver':
            session['logged_in'] = True
            session['is_bus_driver'] = True
            cur = g.db.execute("SELECT Driver_id FROM USER WHERE Username = '" + username + "' AND Password = '" + password + "'" )
            driver_id = cur.fetchone()[0]
            return redirect(url_for('bus_driver', driver_id = driver_id))
        elif role[0] == 'student_parent':
          session['logged_in'] = True
          flash('You were logged in.')
          cur = g.db.execute("SELECT Student_id FROM USER WHERE Username = '" + username + "' AND Password = '" + password + "'" )
          student_id = cur.fetchone()[0]
          return redirect(url_for('student_parent_view', student_id = student_id))
        else:
          session['logged_in'] = True
          flash('You were logged in.')

    return render_template('login.html', error=error)

@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    session.pop('is_admin', None)
    session.pop('is_bus_driver', None)
    flash('You were logged out.')
    return redirect(url_for('login'))


def connect_db():
  return sqlite3.connect(app.database)


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000, debug=True)