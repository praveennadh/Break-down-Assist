from flask import Flask, render_template, request, redirect,session
import mysql.connector
import os
from email.message import EmailMessage
import ssl
import smtplib
from geopy.geocoders import Nominatim
from geopy import distance
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta

def sendbooking(mechanic,user_number):
    rec=mechanic
    sender = 'praveennitt1255@gmail.com'
    pwd = 'smnrxfxdikfzpvmm'

    sub = 'New Booking Alert '
    conn=mysql.connector.connect(**DATABASE)
    c=conn.cursor()
    c.execute('select username from mechdata where mail=%s',(mechanic,))
    mech = c.fetchone()
    conn.commit()
    conn.close()
    body = f"""
    Hello {mech[0]},

    We are excited to inform you that a new booking request has been made by a customer in your service area. Please logon to Gogaadi website for further details.

    Please contact the customer as soon as possible to confirm the booking and provide them with your availability. Remember to provide them with excellent service and make their experience a pleasant one.

    Thank you for being a part of our team and providing your expertise to our valued customers.

    Best regards,
    [Your Company Name]
    [Your Contact Information]
    """
    em = EmailMessage()
    em['From'] = sender
    em['To'] = rec
    em['Subject'] = sub
    em.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com',465,context=context) as smtp:
        smtp.login(sender,pwd)
        smtp.sendmail(sender,rec,em.as_string())

#sendbooking('praveennadhmathi2003@gmail.com','8919140911')

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DATABASE = {
    'host': 'localhost',
    'user': 'praveen',
    'password': 'Bjan24502#',
    'database': 'databaseforuserform'
}

def create_mech_table():
    conn = mysql.connector.connect(**DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS mechdata (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    latitude VARCHAR(255) NOT NULL,
    longitude VARCHAR(255) NOT NULL,
    mobile VARCHAR(255) NOT NULL,
    mail VARCHAR(255) NOT NULL,
    address VARCHAR(256) NOT NULL
    )''')
    conn.commit()
    conn.close()

def requests():
    conn = mysql.connector.connect(**DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS req (
    id INT AUTO_INCREMENT PRIMARY KEY,
    mech VARCHAR(255) NOT NULL,
    mobile VARCHAR(255) NOT NULL,
    address VARCHAR(256) NOT NULL,
    status VARCHAR(256) NOT NULL
    )''')
    conn.commit()
    conn.close()

def create_users_table():
    conn = mysql.connector.connect(**DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS userdata (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL
    )''')
    conn.commit()
    conn.close()


@app.route('/user_welcome')
def user_welcome():
    user_number = session.get('mobile')
    user_address = session.get('address')
    username = session.get('username')
    nearest_mechanics = session.get('nearest_mechanics')
    return render_template('user_welcome.html', username=username,nearest_mechanics=nearest_mechanics,user_number=user_number,user_address=user_address)

@app.route('/mech_welcome')
def mech_welcome():
    username = session.get('username')
    conn=mysql.connector.connect(**DATABASE)
    c=conn.cursor()
    c.execute('select mail from mechdata where username=%s',(username,))
    mail=c.fetchone()
    c.execute("select * from req where mech=%s",(mail))
    tab=c.fetchall()
    conn.commit()
    conn.close()
    return render_template('mech_welcome.html', username=username,tab=tab)

@app.route('/')
def index():
    if 'cnt' not in session:
        session['cnt'] = '0'
    if session['cnt'] == '1':
        session['cnt'] = '0'
        return render_template('form.html',alert=session.get('alert'))
    else:
        return render_template('form.html')

@app.route('/mechregister', methods=['GET', 'POST'])
def mechregister():
    if request.method == 'POST':
        username = request.form['username'] 
        password = request.form['password']
        latitude = request.form['mechlatitude']
        longitude = request.form['mechlongitude']
        mobile = request.form['mobile']
        mail = request.form['mail']
        address = request.form['address']

        # Store data in MySQL
        connection = mysql.connector.connect(**DATABASE)
        cursor = connection.cursor()
        cursor.execute("select * from mechdata where username=%s or mail=%s or mobile=%s",(username,mail,mobile))
        user=cursor.fetchone()
        if user:
            session['cnt'] = '1'
            session['alert']='User Already Exist'
            return redirect('/')
        if latitude=="" or longitude=="":
            geocoder=Nominatim(user_agent="praveen")
            coor= geocoder.geocode(address)
            latitude=coor.latitude
            longitude=coor.longitude
        query = "INSERT INTO mechdata (username, password, latitude, longitude,mobile,mail,address) VALUES (%s, %s, %s, %s, %s, %s,%s)"
        values = (username, password, latitude, longitude, mobile, mail, address)
        cursor.execute(query, values)
        connection.commit()
        connection.close()
        session['cnt'] = '1'
        session['alert']='Registered Successfully'
        return redirect('/')

@app.route('/mechlogin', methods=['GET', 'POST'])
def mechlogin():
    if request.method == 'POST':
        username = request.form['username'] 
        password = request.form['password']
        conn = mysql.connector.connect(**DATABASE)
        c = conn.cursor()
        c.execute("select * from mechdata where username=%s",(username,))
        user = c.fetchone()
        conn.close()
        if user:
            if password == user[2]:
                session['username'] = username
                session['cnt'] = '0'
                session['alert']='None'
                return redirect('/mech_welcome')  # Redirect on successful login
    session['cnt'] = '1'
    session['alert']='Invalid Credentials'
    return redirect('/')

@app.route('/trigger_function', methods=['POST'])
def trigger_function():
    if request.method == 'POST':
        mechanic_id = request.form['mechanic_id']
        user_number = request.form['user_number']
        user_address = request.form['user_address']
        status = 'pending'
        # Call your sendbooking function here, passing mechanic_id, user_number, and user_mobile
        sendbooking(mechanic_id, user_number)
        
        conn=mysql.connector.connect(**DATABASE)
        c=conn.cursor()
        c.execute("INSERT INTO req (mech,mobile,address,status) values(%s,%s,%s,%s)",(mechanic_id,user_number,user_address,status))
        conn.commit()
        conn.close()
        return "Booking request sent to mechanic!"

@app.route('/accept', methods=['POST'])
def accept():
    a=0
    return "Entry marked as accepted"

@app.route('/reject', methods=['POST'])
def reject():
    mob = request.form['user_number']
    mech =request.form['mechanic_id']
    conn=mysql.connector.connect(**DATABASE)
    c=conn.cursor()
    c.execute('select mail from mechdata where username=%s',(mech,))
    mail=c.fetchone()[0]
    status = 'reject'
    c.execute("update req set status=%s where mech=%s and mobile=%s",(status,mail,mob,))
    conn.commit()
    conn.close()
    return "Entry marked as rejected"

def delete_rejected_requests():
    conn = mysql.connector.connect(**DATABASE)
    c = conn.cursor()
    c.execute("DELETE FROM req WHERE status = 'reject'")
    conn.commit()
    conn.close()


@app.route('/userregister', methods=['GET', 'POST'])
def userregister():
    if request.method == 'POST':
        username = request.form['username'] 
        password = request.form['password']

        # Store data in MySQL
        connection = mysql.connector.connect(**DATABASE)
        cursor = connection.cursor()
        cursor.execute("select * from userdata where username=%s",(username,))
        user=cursor.fetchone()
        if user:
            session['cnt']='1'
            session['alert']='User Already Exist'
            return redirect('/')
        query = "INSERT INTO userdata (username, password) VALUES (%s, %s)"
        values = (username, password)
        cursor.execute(query, values)
        connection.commit()
        connection.close()
        session['cnt'] = '1'
        session['alert']='Registration Successful!!!'
    return redirect('/')
    

@app.route('/userlogin', methods=['GET', 'POST'])
def userlogin():
    if request.method == 'POST':
        username = request.form['username'] 
        password = request.form['password']
        latitude = request.form['userlatitude']
        longitude = request.form['userlongitude']
        mobile = request.form['mobile']
        address = request.form['address']
        conn=mysql.connector.connect(**DATABASE)
        c=conn.cursor()
        c.execute("select * from userdata where username=%s",(username,))
        user=c.fetchone()
        if user:
            if password==user[2]:
                session['username'] = username
                session['mobile'] = mobile
                session['address'] = address
                session['cnt'] = '0'
                session['alert'] = None
                if latitude=="" or longitude=="":
                    geocoder=Nominatim(user_agent="praveen")
                    coor= geocoder.geocode(address)
                    latitude=coor.latitude
                    longitude=coor.longitude
                target_latitude = float(latitude)   # Replace with actual latitude
                target_longitude = float(longitude)  # Replace with actual longitude

                # Calculate distance using Haversine formula
                haversine_formula = (
                    "6371 * acos("
                    "cos(radians(%s)) * cos(radians(latitude)) * "
                    "cos(radians(longitude) - radians(%s)) + "
                    "sin(radians(%s)) * sin(radians(latitude))"
                   ")"
                )

                # Query to select nearest mechanics and order by distance
                query = (
                    f"SELECT username, latitude, longitude, address,mail,"
                    f"{haversine_formula} AS distance "
                    "FROM mechdata "
                    "ORDER BY distance "
                    "LIMIT 10"
                )

                c.execute(query, (target_latitude, target_longitude, target_latitude))
                nearest_mechanics = c.fetchall()
                session['nearest_mechanics'] = nearest_mechanics
                return redirect('/user_welcome')
    session['cnt'] = '1'
    session['alert']='invalid credentials'
    return redirect('/')


if __name__ == '__main__':
    create_users_table()
    create_mech_table()
    requests()
    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(delete_rejected_requests, 'interval', minutes=1)
    scheduler.start()

    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    app.run(host=host, port=port, debug=True)
