#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors
import datetime
import time
from random import randint

#barchart lib
#Initialize the app from Flask
app = Flask(__name__)

#Configure MySQL
conn = pymysql.connect(host='127.0.0.1',
                       user='root',
                       password='',
                       db='final_final',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

#Define a route to hello function
@app.route('/home')
def home():
    
    cursor = conn.cursor();
    query_airport_info = "SELECT Distinct city FROM `Airport`"
    cursor.execute(query_airport_info)
    airports_info = cursor.fetchall()
    airports_city = []
    for each in airports_info:
        airports_city.append(each['city'])
    cursor.close()
    
    
    cursor = conn.cursor();
    query_flight_info = '''SELECT DISTINCT airline_id, flight_id, 
    date(departure_time) as departure_day, 
    date(arrival_time) as arrival_day FROM Flight'''
    cursor.execute(query_flight_info)
    flights_info = cursor.fetchall()
    flights = []
    for i in range(len(flights_info)):
        full_flight_id = flights_info[i]["airline_id"] + flights_info[i]["flight_id"]
        flight_info = {"full_flight_id": full_flight_id,
                       "departure_day": flights_info[i]["departure_day"],
                       "arrival_day": flights_info[i]["arrival_day"]
        }
        flights.append(flight_info)
    cursor.close()
    
    cursor = conn.cursor();
    query_airline_info = "SELECT Distinct airline_name FROM `Airline`"
    cursor.execute(query_airline_info)
    airline_info = cursor.fetchall()
    airlines = []
    for each in airline_info:
        airlines.append(each["airline_name"])
    cursor.close()

    cursor = conn.cursor();
    query_airline_id = "SELECT Distinct airport_id FROM `Airport`"
    cursor.execute(query_airline_id)
    airport_id = cursor.fetchall()
    airportid = []
    for each in airport_id:
        airportid.append(each["airport_id"])
    cursor.close()   
    

    
    
    if 'username' in session:
        username = session['username']
        print(username)
        
        cursor = conn.cursor()
        query_customer_info = "SELECT * FROM `Customer` where customer_email = %s"
        cursor.execute(query_customer_info,(username))
        customer_info = cursor.fetchall()
        cursor.close()
        
        cursor = conn.cursor()
        query_agent_info = "SELECT * FROM `Booking_agent` where agent_email = %s"
        cursor.execute(query_agent_info,(username))
        agent_info = cursor.fetchall()
        cursor.close()
        
        if len(customer_info) != 0:
            return render_template('index_c_logged_in.html', airports_info = airports_info, 
                               username = username, flights = flights)
        elif len(agent_info) != 0:
            return render_template('index_a_logged_in.html', airports_info = airports_info,  
                               username = username, flights = flights)
        else:
            try:
                result = session['result']
                session['result'] = 2
            except:
                result = 2
                
            airline_id = session['airline_id']
            cursor = conn.cursor()
            query_airpline = "SELECT * FROM `Airplane` where airline_id = %s"
            cursor.execute(query_airpline, (airline_id))
            airplane = cursor.fetchall()
            airplaneid = []
            for each in airplane:
                airplaneid.append(each["airplane_id"])
            cursor.close()
            cursor = conn.cursor()
            query_fid = "SELECT * FROM `Flight` where airline_id = %s"
            cursor.execute(query_fid, (airline_id))
            flight_id = cursor.fetchall()
            flightid = []
            for each in flight_id:
                flightid.append(each["flight_id"])
            session['flightid']=flightid
            cursor.close() 
            
            cursor = conn.cursor()
            
            if session['fh_forp'] == 1:
                session['fh_forp'] = 0
                if session['flight_history_s'] == 'past':
                    query_f = 'SELECT * FROM Flight WHERE airline_id = %s and departure_time <= curtime()'
                elif session['flight_history_s'] == 'future':
                    query_f = 'SELECT * FROM Flight WHERE airline_id = %s and departure_time >= curtime()'
                elif session['flight_history_s'] == 'all': 
                    query_f = 'SELECT * FROM Flight WHERE airline_id = %s'                    
                cursor.execute(query_f, (airline_id))
            elif session['fh_dr'] == 1:
                session['fh_dr'] = 0
                from_time = session['from_time']
                to_time = session['to_time']
                query_f = "SELECT * FROM Flight WHERE airline_id = %s and (departure_time between STR_TO_DATE(%s,'%%Y%%m%%d') and STR_TO_DATE(%s,'%%Y%%m%%d'))"
                cursor.execute(query_f, (airline_id,from_time,to_time))
            elif session['fh_ap'] == 1:
                session['fh_ap'] = 0
                departure_airport = session['departure_airport']
                arrival_airport = session['arrival_airport']
                query_f = 'SELECT * FROM Flight WHERE airline_id = %s and departure_airport = %s and arrival_airport = %s'
                cursor.execute(query_f, (airline_id,departure_airport,arrival_airport))
            elif session['fh_c'] == 1:
                session['fh_c'] = 0
                departure_city = session['departure_city']
                arrival_city = session['arrival_city']
                query_f = """SELECT * FROM Flight join airport as da join airport as aa
                on departure_airport = da.airport_id and arrival_airport = aa.airport_id
                WHERE airline_id = %s and da.city = %s and aa.city = %s"""
                cursor.execute(query_f, (airline_id,departure_city,arrival_city))
                
            else:
                query_f = 'SELECT * FROM Flight WHERE airline_id = %s and (departure_time between curdate() and date_add(curdate(), interval 30 day))'
                cursor.execute(query_f, (airline_id))
            flight_info = cursor.fetchall()
            cursor.close()   

            return render_template('index_s_logged_in.html', airportid = airportid, airlines = airlines, result=result, airports_city=airports_city,
                               username = username, airline_id=airline_id, flight_info = flight_info,flightid = flightid, airplane=airplane,airplaneid=airplaneid,flight_history=session['flight_history_s'])
    else:
        return render_template('index.html', airports_info = airports_info, flights = flights)
        
@app.route('/flight_status', methods=['GET', 'POST'])
def flight_status():
    flight_full_id = request.form['flight_id']
    airline_id = flight_full_id[:2]
    flight_id = flight_full_id[2:]
    cursor = conn.cursor()
    query = '''SELECT flight_status FROM Flight WHERE airline_id = %s
     AND flight_id = %s'''
    cursor.execute(query, (airline_id, flight_id ))
    
    status = cursor.fetchone()
    cursor.close()

    return render_template('flight_status.html', flight_full_id  = flight_full_id, status = status)

@app.route('/flight_status_c', methods=['GET', 'POST'])
def flight_status_c():
    username = session['username']
    flight_full_id = request.form['flight_id']
    airline_id = flight_full_id[:2]
    flight_id = flight_full_id[2:]
    cursor = conn.cursor()
    query = '''SELECT flight_status FROM Flight WHERE airline_id = %s
     AND flight_id = %s'''
    cursor.execute(query, (airline_id, flight_id ))
    
    status = cursor.fetchone()
    cursor.close()

    return render_template('flight_status_c.html', username = username,
    flight_full_id  = flight_full_id, status = status)

@app.route('/flight_status_a', methods=['GET', 'POST'])
def flight_status_a():
    username = session['username']
    flight_full_id = request.form['flight_id']
    airline_id = flight_full_id[:2]
    flight_id = flight_full_id[2:]
    cursor = conn.cursor()
    query = '''SELECT flight_status FROM Flight WHERE airline_id = %s
     AND flight_id = %s'''
    cursor.execute(query, (airline_id, flight_id ))
    
    status = cursor.fetchone()
    cursor.close()

    return render_template('flight_status_a.html', username = username,
    flight_full_id  = flight_full_id, status = status)


#Define route for login

@app.route('/loginc')
def loginc():
	return render_template('loginc.html')

@app.route('/logina')
def logina():
	return render_template('logina.html')

@app.route('/logins')
def logins():
	return render_template('logins.html')


@app.route('/loginAuthc', methods=['GET', 'POST'])
def loginAuthc():
	#grabs information from the forms
	username = request.form['username']
	password = request.form['password']

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM Customer WHERE customer_email = %s and user_password = MD5(%s)'
	cursor.execute(query, (username, password))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	cursor.close()
	error = None
	if(data):
		#creates a session for the the user
		#session is a built in
		session['username'] = username
		return redirect(url_for('home'))
	else:
		#returns an error message to the html page
		error = 'Invalid login or username'
		return render_template('loginc.html', error=error)

@app.route('/loginAutha', methods=['GET', 'POST'])
def loginAutha():
    #grabs information from the forms
    username = request.form['username']
    agentid = request.form["agentid"]
    password = request.form["password"]

	#cursor used to send queries
    cursor = conn.cursor()
	#executes query
    query = '''SELECT * FROM Booking_agent WHERE agent_email = %s and booking_agent_ID = %s
    and agent_password = MD5(%s) 
    '''
    cursor.execute(query, (username, agentid, password))
	#stores the results in a variable
    data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
    cursor.close()
    error = None
    if(data):
		#creates a session for the the user
		#session is a built in
        session['username'] = username
        return redirect(url_for('home'))
    else:
		#returns an error message to the html page
        error = 'Invalid login or username or agent ID'
        return render_template('logina.html', error=error)

@app.route('/loginAuths', methods=['GET', 'POST'])
def loginAuths():
 #grabs information from the forms
    airline_id = request.form['airline_id']
    username = request.form['username']
    password = request.form['password']

 #cursor used to send queries
    cursor = conn.cursor()
 #executes query
    query = 'SELECT * FROM Airline_staff WHERE airline_id = %s and username = %s and user_password = MD5(%s)'
    cursor.execute(query, (airline_id, username, password))
 #stores the results in a variable
    data = cursor.fetchone()
 #use fetchall() if you are expecting more than 1 data row
    cursor.close()
    error = None    
    if(data):

        session['username'] = username
        session['airline_id'] = airline_id
        session['flight_history_s'] = ''
        session['fh_forp'] = 0
        session['fh_dr'] = 0
        session['fh_ap'] = 0
        session['fh_c'] = 0
        return redirect(url_for('home'))
    else:
        error = 'Invalid login or username'
        return render_template('logins.html', error=error)
    
#Define route for register
@app.route('/register')
def register():
	return render_template('registerAll.html')
@app.route('/registerc')
def registerc():
	return render_template('registerc.html')
@app.route('/registera')
def registera():
	return render_template('registera.html')
@app.route('/registers')
def registers():
	return render_template('registers.html')


#Authenticates the register
@app.route('/registercAuth', methods=['GET', 'POST'])
def registercAuth():
	#grabs information from the forms
    customer_email = request.form['customer_email']
    username = request.form['username']
    firstname = request.form['first_name']
    lastname = request.form['last_name']
    password = request.form['password']
    building_number = request.form['building_number']   
    street = request.form['street']
    city = request.form['city']
    state = request.form['state']
    phone_number = request.form['phone_number']
    passport_number = request.form['passport_number']
    passport_expiration = request.form['passport_expiration']
    passport_country = request.form['passport_country']
    date_of_birth = request.form['date_of_birth']
	#cursor used to send queries
    cursor = conn.cursor()
	#executes query
    query = 'SELECT * FROM customer WHERE customer_email = %s'
    cursor.execute(query, (customer_email))
	#stores the results in a variable
    data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
    error = None
    if(data):
		#If the previous query returns data, then user exists
        error = "This user already exists. Use another email to register or login directly."
        return render_template('register_failure.html', error = error)
    else:
        ins = 'INSERT INTO customer VALUES(%s,%s,MD5(%s),%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        cursor.execute(ins, (customer_email,username,password,
                             firstname, lastname,
                             building_number,street,city,state,phone_number,passport_number,passport_expiration,passport_country,date_of_birth))
        conn.commit()
        cursor.close()
        return render_template('index.html')

@app.route('/registeraAuth', methods=['GET', 'POST'])
def registeraAuth():
	#grabs information from the forms
    agent_email = request.form['agent_email']
    agent_password = request.form['agent_password']
    booking_agent_ID = request.form['booking_agent_ID']
	#cursor used to send queries
    cursor = conn.cursor()
	#executes query
    query = 'SELECT * FROM booking_agent WHERE agent_email = %s'
    cursor.execute(query, (agent_email))
	#stores the results in a variable
    data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
    error = None
    if(data):
		#If the previous query returns data, then user exists
        error = "This agent already exists"
        return render_template('registera.html', error = error)
    else:
        ins = 'INSERT INTO booking_agent VALUES(%s,MD5(%s),%s)'
        cursor.execute(ins, (agent_email,agent_password,booking_agent_ID))
        conn.commit()
        cursor.close()
        return render_template('index.html')
    
@app.route('/registersAuth', methods=['GET', 'POST'])
def registersAuth():
	#grabs information from the forms
    airline_id = request.form['airline_id']
    username = request.form['username']
    user_password = request.form['user_password']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    date_of_birth = request.form['date_of_birth']
    phone_number_1 = request.form['phone_number_1']
    phone_number_2 = request.form.get('phone_number_2')
    phone_number_3 = request.form.get('phone_number_3')
    phone_numbers = []
    phone_numbers.append(phone_number_1)
    if phone_number_2:
        phone_numbers.append(phone_number_2)
    if phone_number_3:
        phone_numbers.append(phone_number_3)
	#cursor used to send queries
    cursor = conn.cursor()
	#executes query
    query = 'SELECT * FROM airline_staff WHERE airline_id = %s and username = %s'
    cursor.execute(query, (airline_id, username))
	#stores the results in a variable
    data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
    error = None
    if(data):
		#If the previous query returns data, then user exists
        error = "This staff already exists"
        return render_template('registers.html', error = error)
    else:
        ins = 'INSERT INTO airline_staff VALUES(%s,%s,MD5(%s),%s,%s,%s)'
        cursor.execute(ins, (airline_id,username,user_password,first_name,last_name,date_of_birth))
        conn.commit()
        cursor.close()
       
        for i in phone_numbers:
            cursor = conn.cursor()
            ins = 'insert into airline_staff_phonenumber values(%s,%s,%s)'
            cursor.execute(ins, (airline_id,username,i))
            conn.commit()
            cursor.close()            
        return render_template('index.html')
    
    
@app.route('/logout')
def logout():
	session.pop('username')
	return redirect('/home')



    

@app.route('/flight_one_way_a', methods=['GET','POST'])
def flight_one_way_a():
    dep_day = request.form.get('dep_day')
    dep_day = datetime.datetime.strptime(dep_day, "%m/%d/%Y").date()
    print(dep_day)
    #dep_day = "2019-05-15"
    guest_num = request.form.get('guest_num')
    
    dep_city = request.form.get('dep_city')
    
    ###BUG!!!!
    arr_city = request.form.get('arr_city')
    print(dep_day, dep_city, arr_city)
   
    #arr_city = "New York"
    
    dep_airport = request.form.get('dep_airport')
    
    arr_airport = request.form.get('arr_airport')
    
    
    #Get available flights information
    cursor = conn.cursor();
    if dep_city:
        query_flights_info = '''SELECT airline_name, Flight.airline_id, 
    Flight.flight_id, a.airport_id as ap, d.airport_id as dp, 
    base_price, flight_status, a.city as acity, d.city as dcity,
    DATE(departure_time) as dep_day, TIME(departure_time) as dep_time,
    TIME(arrival_time) as arr_time,  
    (amount_of_seat - COUNT(ticket_id)) as remaining_seats 
    FROM Flight NATURAL JOIN Airline NATURAL JOIN Airplane LEFT OUTER JOIN Ticket ON 
    (Flight.airline_id,  Flight.flight_id)= (Ticket.airline_id,  Ticket.flight_id) 
    JOIN Airport as a JOIN Airport as d 
    WHERE  a.airport_id = arrival_airport AND d.airport_id = departure_airport
    AND d.city = %s AND a.city = %s AND DATE(departure_time) = %s 
    GROUP BY Flight.airline_id, Flight.flight_id having remaining_seats >= %s
    ORDER BY base_price ASC'''
        cursor.execute(query_flights_info, (dep_city, arr_city, dep_day, guest_num))
    elif dep_airport:
        query_flights_info = '''SELECT airline_name, Flight.airline_id, 
    Flight.flight_id, a.airport_id as ap, d.airport_id as dp, 
    base_price, flight_status, a.city as acity, d.city as dcity,
    DATE(departure_time) as dep_day, TIME(departure_time) as dep_time,
    TIME(arrival_time) as arr_time, 
    (amount_of_seat - COUNT(ticket_id)) as remaining_seats 
    FROM Flight NATURAL JOIN Airline NATURAL JOIN Airplane LEFT OUTER JOIN Ticket ON 
    (Flight.airline_id,  Flight.flight_id)= (Ticket.airline_id,  Ticket.flight_id) 
    JOIN Airport as a JOIN Airport as d 
    WHERE  a.airport_id = arrival_airport AND d.airport_id = departure_airport
    AND d.airport_id = %s AND a.airport_id = %s AND DATE(departure_time) = %s 
    GROUP BY Flight.airline_id, Flight.flight_id having remaining_seats >= %s 
    ORDER BY base_price ASC'''
        cursor.execute(query_flights_info, (dep_airport, arr_airport, dep_day, guest_num))
        
    
    flights_info = cursor.fetchall()  
    
    
    cursor.close()
    
    print("number of records is:", len(flights_info))
    
    airline_name = []
    for i in range(len(flights_info)):
        airline_name.append(flights_info[i]["airline_name"])
        
    airline_name = list(set(airline_name))
    
    #Get available airports information
    cursor = conn.cursor();
    query_airport_info = "SELECT Distinct * FROM `Airport`"
    cursor.execute(query_airport_info)
    airports_info = cursor.fetchall()
    
    cursor.close()
    
    cities = []
    for i in range(len(airports_info)):
        cities.append(airports_info[i]["city"])
        
    cities = list(set(cities))
    
    
    
    username = session['username']
        
        
    
    
    return render_template('flight_one_way_logged_in_a.html', 
                               username=username,
                               cities = cities,
                           airports_info = airports_info, 
                           flights_info = flights_info,
                           airline_name = airline_name)
    
@app.route('/flight_round_trip_a', methods=['GET','POST'])
def flight_round_trip_a():
    dep_day = request.form.get('dep_day')
    dep_day = datetime.datetime.strptime(dep_day, "%m/%d/%Y").date()
    
    return_day = request.form.get('return_day')
    return_day = datetime.datetime.strptime(return_day, "%m/%d/%Y").date()

    #dep_day = "2019-05-15"
    guest_num = request.form.get('guest_num')
    
    dep_city = request.form.get('dep_city')
    
    ###BUG!!!!
    arr_city = request.form.get('arr_city')
    print(dep_day, dep_city, arr_city)
   
    #arr_city = "New York"
    
    dep_airport = request.form.get('dep_airport')
    
    arr_airport = request.form.get('arr_airport')
    
    
    #Get available flights information - First Flight
    cursor = conn.cursor();
    if dep_city:
        query_flights_info_first = '''SELECT airline_name, Flight.airline_id, 
    Flight.flight_id, a.airport_id as ap, d.airport_id as dp, 
    base_price, flight_status, a.city as acity, d.city as dcity,
    DATE(departure_time) as dep_day, TIME(departure_time) as dep_time,
    TIME(arrival_time) as arr_time,  
    (amount_of_seat - COUNT(ticket_id)) as remaining_seats 
    FROM Flight NATURAL JOIN Airline NATURAL JOIN Airplane LEFT OUTER JOIN Ticket ON 
    (Flight.airline_id,  Flight.flight_id)= (Ticket.airline_id,  Ticket.flight_id) 
    JOIN Airport as a JOIN Airport as d 
    WHERE  a.airport_id = arrival_airport AND d.airport_id = departure_airport
    AND d.city = %s AND a.city = %s AND DATE(departure_time) = %s 
    GROUP BY Flight.airline_id, Flight.flight_id having remaining_seats >= %s
    ORDER BY base_price ASC'''
        cursor.execute(query_flights_info_first, (dep_city, arr_city, dep_day, guest_num))
    elif dep_airport:
        query_flights_info_first = '''SELECT airline_name, Flight.airline_id, 
    Flight.flight_id, a.airport_id as ap, d.airport_id as dp, 
    base_price, flight_status, a.city as acity, d.city as dcity,
    DATE(departure_time) as dep_day, TIME(departure_time) as dep_time,
    TIME(arrival_time) as arr_time, 
    (amount_of_seat - COUNT(ticket_id)) as remaining_seats 
    FROM Flight NATURAL JOIN Airline NATURAL JOIN Airplane LEFT OUTER JOIN Ticket ON 
    (Flight.airline_id,  Flight.flight_id)= (Ticket.airline_id,  Ticket.flight_id) 
    JOIN Airport as a JOIN Airport as d 
    WHERE  a.airport_id = arrival_airport AND d.airport_id = departure_airport
    AND d.airport_id = %s AND a.airport_id = %s AND DATE(departure_time) = %s 
    GROUP BY Flight.airline_id, Flight.flight_id having remaining_seats >= %s 
    ORDER BY base_price ASC'''
        cursor.execute(query_flights_info_first, (dep_airport, arr_airport, dep_day, guest_num))
        
    
    flights_info_first = cursor.fetchall()  
 
    cursor.close()
    
    
    #Get available flights information - Second Flight
    cursor = conn.cursor();
    if dep_city:
        query_flights_info_second = '''SELECT airline_name, Flight.airline_id, 
    Flight.flight_id, a.airport_id as ap, d.airport_id as dp, 
    base_price, flight_status, a.city as acity, d.city as dcity,
    DATE(departure_time) as dep_day, TIME(departure_time) as dep_time,
    TIME(arrival_time) as arr_time,  
    (amount_of_seat - COUNT(ticket_id)) as remaining_seats 
    FROM Flight NATURAL JOIN Airline NATURAL JOIN Airplane LEFT OUTER JOIN Ticket ON 
    (Flight.airline_id,  Flight.flight_id)= (Ticket.airline_id,  Ticket.flight_id) 
    JOIN Airport as a JOIN Airport as d 
    WHERE  a.airport_id = arrival_airport AND d.airport_id = departure_airport
    AND d.city = %s AND a.city = %s AND DATE(departure_time) = %s 
    GROUP BY Flight.airline_id, Flight.flight_id having remaining_seats >= %s
    ORDER BY base_price ASC'''
        cursor.execute(query_flights_info_second, (arr_city, dep_city, return_day, guest_num))
    elif dep_airport:
        query_flights_info_second = '''SELECT airline_name, Flight.airline_id, 
    Flight.flight_id, a.airport_id as ap, d.airport_id as dp, 
    base_price, flight_status, a.city as acity, d.city as dcity,
    DATE(departure_time) as dep_day, TIME(departure_time) as dep_time,
    TIME(arrival_time) as arr_time, 
    (amount_of_seat - COUNT(ticket_id)) as remaining_seats 
    FROM Flight NATURAL JOIN Airline NATURAL JOIN Airplane LEFT OUTER JOIN Ticket ON 
    (Flight.airline_id,  Flight.flight_id)= (Ticket.airline_id,  Ticket.flight_id) 
    JOIN Airport as a JOIN Airport as d 
    WHERE  a.airport_id = arrival_airport AND d.airport_id = departure_airport
    AND d.airport_id = %s AND a.airport_id = %s AND DATE(departure_time) = %s 
    GROUP BY Flight.airline_id, Flight.flight_id having remaining_seats >= %s 
    ORDER BY base_price ASC'''
        cursor.execute(query_flights_info_second, (arr_airport, dep_airport, return_day, guest_num))
        
    
    flights_info_second = cursor.fetchall()  
 
    cursor.close()
    
    
    
    
    print("number of records of the first trip is:", len(query_flights_info_first))
    print("number of records of the second trip is:", len(query_flights_info_second))
    
    
    
    #Get available airports information
    cursor = conn.cursor();
    query_airport_info = "SELECT Distinct * FROM `Airport`"
    cursor.execute(query_airport_info)
    airports_info = cursor.fetchall()
    
    cursor.close()
    
    cities = []
    for i in range(len(airports_info)):
        cities.append(airports_info[i]["city"])
        
    cities = list(set(cities))
    
    
    
    username = session['username']
        
        
    
    
    return render_template('flight_round_trip_a.html', 
                           username=username,
                           cities = cities,
                           airports_info = airports_info, 
                           flights_info_first = flights_info_first,
                           flights_info_second = flights_info_second,)



@app.route('/flight_one_way_c', methods=['GET','POST'])
def flight_one_way_c():
    dep_day = request.form.get('dep_day')
    dep_day = datetime.datetime.strptime(dep_day, "%m/%d/%Y").date()
    print(dep_day)
    #dep_day = "2019-05-15"
    guest_num = request.form.get('guest_num')
    
    dep_city = request.form.get('dep_city')
    
    ###BUG!!!!
    arr_city = request.form.get('arr_city')
    print(dep_day, dep_city, arr_city)
   
    #arr_city = "New York"
    
    dep_airport = request.form.get('dep_airport')
    
    arr_airport = request.form.get('arr_airport')
    
    
    #Get available flights information
    cursor = conn.cursor();
    if dep_city:
        query_flights_info = '''SELECT airline_name, Flight.airline_id, 
    Flight.flight_id, a.airport_id as ap, d.airport_id as dp, 
    base_price, flight_status, a.city as acity, d.city as dcity,
    DATE(departure_time) as dep_day, TIME(departure_time) as dep_time,
    TIME(arrival_time) as arr_time,  
    (amount_of_seat - COUNT(ticket_id)) as remaining_seats 
    FROM Flight NATURAL JOIN Airline NATURAL JOIN Airplane LEFT OUTER JOIN Ticket ON 
    (Flight.airline_id,  Flight.flight_id)= (Ticket.airline_id,  Ticket.flight_id) 
    JOIN Airport as a JOIN Airport as d 
    WHERE  a.airport_id = arrival_airport AND d.airport_id = departure_airport
    AND d.city = %s AND a.city = %s AND DATE(departure_time) = %s 
    GROUP BY Flight.airline_id, Flight.flight_id having remaining_seats >= %s
    ORDER BY base_price ASC'''
        cursor.execute(query_flights_info, (dep_city, arr_city, dep_day, guest_num))
    elif dep_airport:
        query_flights_info = '''SELECT airline_name, Flight.airline_id, 
    Flight.flight_id, a.airport_id as ap, d.airport_id as dp, 
    base_price, flight_status, a.city as acity, d.city as dcity,
    DATE(departure_time) as dep_day, TIME(departure_time) as dep_time,
    TIME(arrival_time) as arr_time, 
    (amount_of_seat - COUNT(ticket_id)) as remaining_seats 
    FROM Flight NATURAL JOIN Airline NATURAL JOIN Airplane LEFT OUTER JOIN Ticket ON 
    (Flight.airline_id,  Flight.flight_id)= (Ticket.airline_id,  Ticket.flight_id) 
    JOIN Airport as a JOIN Airport as d 
    WHERE  a.airport_id = arrival_airport AND d.airport_id = departure_airport
    AND d.airport_id = %s AND a.airport_id = %s AND DATE(departure_time) = %s 
    GROUP BY Flight.airline_id, Flight.flight_id having remaining_seats >= %s 
    ORDER BY base_price ASC'''
        cursor.execute(query_flights_info, (dep_airport, arr_airport, dep_day, guest_num))
        
    
    flights_info = cursor.fetchall()  
    
    
    cursor.close()
    
    print("number of records is:", len(flights_info))
    
    airline_name = []
    for i in range(len(flights_info)):
        airline_name.append(flights_info[i]["airline_name"])
        
    airline_name = list(set(airline_name))
    
    #Get available airports information
    cursor = conn.cursor();
    query_airport_info = "SELECT Distinct * FROM `Airport`"
    cursor.execute(query_airport_info)
    airports_info = cursor.fetchall()
    
    cursor.close()
    
    cities = []
    for i in range(len(airports_info)):
        cities.append(airports_info[i]["city"])
        
    cities = list(set(cities))
    
    
    
    username = session['username']
        
        
    
    
    return render_template('flight_one_way_logged_in_c.html', 
                               username=username,
                               cities = cities,
                           airports_info = airports_info, 
                           flights_info = flights_info,
                           airline_name = airline_name)
    

@app.route('/flight_round_trip_c', methods=['GET','POST'])
def flight_round_trip_c():
    dep_day = request.form.get('dep_day')
    dep_day = datetime.datetime.strptime(dep_day, "%m/%d/%Y").date()
    
    return_day = request.form.get('return_day')
    return_day = datetime.datetime.strptime(return_day, "%m/%d/%Y").date()

    #dep_day = "2019-05-15"
    guest_num = request.form.get('guest_num')
    
    dep_city = request.form.get('dep_city')
    
    ###BUG!!!!
    arr_city = request.form.get('arr_city')
    print(dep_day, dep_city, arr_city)
   
    #arr_city = "New York"
    
    dep_airport = request.form.get('dep_airport')
    
    arr_airport = request.form.get('arr_airport')
    
    
    #Get available flights information - First Flight
    cursor = conn.cursor();
    if dep_city:
        query_flights_info_first = '''SELECT airline_name, Flight.airline_id, 
    Flight.flight_id, a.airport_id as ap, d.airport_id as dp, 
    base_price, flight_status, a.city as acity, d.city as dcity,
    DATE(departure_time) as dep_day, TIME(departure_time) as dep_time,
    TIME(arrival_time) as arr_time,  
    (amount_of_seat - COUNT(ticket_id)) as remaining_seats 
    FROM Flight NATURAL JOIN Airline NATURAL JOIN Airplane LEFT OUTER JOIN Ticket ON 
    (Flight.airline_id,  Flight.flight_id)= (Ticket.airline_id,  Ticket.flight_id) 
    JOIN Airport as a JOIN Airport as d 
    WHERE  a.airport_id = arrival_airport AND d.airport_id = departure_airport
    AND d.city = %s AND a.city = %s AND DATE(departure_time) = %s 
    GROUP BY Flight.airline_id, Flight.flight_id having remaining_seats >= %s
    ORDER BY base_price ASC'''
        cursor.execute(query_flights_info_first, (dep_city, arr_city, dep_day, guest_num))
    elif dep_airport:
        query_flights_info_first = '''SELECT airline_name, Flight.airline_id, 
    Flight.flight_id, a.airport_id as ap, d.airport_id as dp, 
    base_price, flight_status, a.city as acity, d.city as dcity,
    DATE(departure_time) as dep_day, TIME(departure_time) as dep_time,
    TIME(arrival_time) as arr_time, 
    (amount_of_seat - COUNT(ticket_id)) as remaining_seats 
    FROM Flight NATURAL JOIN Airline NATURAL JOIN Airplane LEFT OUTER JOIN Ticket ON 
    (Flight.airline_id,  Flight.flight_id)= (Ticket.airline_id,  Ticket.flight_id) 
    JOIN Airport as a JOIN Airport as d 
    WHERE  a.airport_id = arrival_airport AND d.airport_id = departure_airport
    AND d.airport_id = %s AND a.airport_id = %s AND DATE(departure_time) = %s 
    GROUP BY Flight.airline_id, Flight.flight_id having remaining_seats >= %s 
    ORDER BY base_price ASC'''
        cursor.execute(query_flights_info_first, (dep_airport, arr_airport, dep_day, guest_num))
        
    
    flights_info_first = cursor.fetchall()  
 
    cursor.close()
    
    
    #Get available flights information - Second Flight
    cursor = conn.cursor();
    if dep_city:
        query_flights_info_second = '''SELECT airline_name, Flight.airline_id, 
    Flight.flight_id, a.airport_id as ap, d.airport_id as dp, 
    base_price, flight_status, a.city as acity, d.city as dcity,
    DATE(departure_time) as dep_day, TIME(departure_time) as dep_time,
    TIME(arrival_time) as arr_time,  
    (amount_of_seat - COUNT(ticket_id)) as remaining_seats 
    FROM Flight NATURAL JOIN Airline NATURAL JOIN Airplane LEFT OUTER JOIN Ticket ON 
    (Flight.airline_id,  Flight.flight_id)= (Ticket.airline_id,  Ticket.flight_id) 
    JOIN Airport as a JOIN Airport as d 
    WHERE  a.airport_id = arrival_airport AND d.airport_id = departure_airport
    AND d.city = %s AND a.city = %s AND DATE(departure_time) = %s 
    GROUP BY Flight.airline_id, Flight.flight_id having remaining_seats >= %s
    ORDER BY base_price ASC'''
        cursor.execute(query_flights_info_second, (arr_city, dep_city, return_day, guest_num))
    elif dep_airport:
        query_flights_info_second = '''SELECT airline_name, Flight.airline_id, 
    Flight.flight_id, a.airport_id as ap, d.airport_id as dp, 
    base_price, flight_status, a.city as acity, d.city as dcity,
    DATE(departure_time) as dep_day, TIME(departure_time) as dep_time,
    TIME(arrival_time) as arr_time, 
    (amount_of_seat - COUNT(ticket_id)) as remaining_seats 
    FROM Flight NATURAL JOIN Airline NATURAL JOIN Airplane LEFT OUTER JOIN Ticket ON 
    (Flight.airline_id,  Flight.flight_id)= (Ticket.airline_id,  Ticket.flight_id) 
    JOIN Airport as a JOIN Airport as d 
    WHERE  a.airport_id = arrival_airport AND d.airport_id = departure_airport
    AND d.airport_id = %s AND a.airport_id = %s AND DATE(departure_time) = %s 
    GROUP BY Flight.airline_id, Flight.flight_id having remaining_seats >= %s 
    ORDER BY base_price ASC'''
        cursor.execute(query_flights_info_second, (arr_airport, dep_airport, return_day, guest_num))
        
    
    flights_info_second = cursor.fetchall()  
 
    cursor.close()
    
    
    
    
    print("number of records of the first trip is:", len(query_flights_info_first))
    print("number of records of the second trip is:", len(query_flights_info_second))
    
    
    
    #Get available airports information
    cursor = conn.cursor();
    query_airport_info = "SELECT Distinct * FROM `Airport`"
    cursor.execute(query_airport_info)
    airports_info = cursor.fetchall()
    
    cursor.close()
    
    cities = []
    for i in range(len(airports_info)):
        cities.append(airports_info[i]["city"])
        
    cities = list(set(cities))
    
    
    
    username = session['username']
        
        
    
    
    return render_template('flight_round_trip_c.html', 
                               username=username,
                               cities = cities,
                           airports_info = airports_info, 
                           flights_info_first = flights_info_first,
                           flights_info_second = flights_info_second,)

@app.route('/flight_one_way', methods=['GET','POST'])
def flight_one_way():
   
    
    dep_day = request.form.get('dep_day')
    dep_day = datetime.datetime.strptime(dep_day, "%m/%d/%Y").date()
    print(dep_day)
    #dep_day = "2019-05-15"
    guest_num = request.form.get('guest_num')
    
    dep_city = request.form.get('dep_city')
    
    ###BUG!!!!
    arr_city = request.form.get('arr_city')
    print(dep_day, dep_city, arr_city)
   
    #arr_city = "New York"
    
    dep_airport = request.form.get('dep_airport')
    
    arr_airport = request.form.get('arr_airport')
    
    
    #Get available flights information
    cursor = conn.cursor();
    if dep_city:
        query_flights_info = '''SELECT airline_name, Flight.airline_id, 
    Flight.flight_id, a.airport_id as ap, d.airport_id as dp, 
    base_price, flight_status, a.city as acity, d.city as dcity,
    DATE(departure_time) as dep_day, TIME(departure_time) as dep_time,
    TIME(arrival_time) as arr_time,  
    (amount_of_seat - COUNT(ticket_id)) as remaining_seats 
    FROM Flight NATURAL JOIN Airline NATURAL JOIN Airplane LEFT OUTER JOIN Ticket ON 
    (Flight.airline_id,  Flight.flight_id)= (Ticket.airline_id,  Ticket.flight_id) 
    JOIN Airport as a JOIN Airport as d 
    WHERE  a.airport_id = arrival_airport AND d.airport_id = departure_airport
    AND d.city = %s AND a.city = %s AND DATE(departure_time) = %s 
    GROUP BY Flight.airline_id, Flight.flight_id having remaining_seats >= %s
    ORDER BY base_price ASC'''
        cursor.execute(query_flights_info, (dep_city, arr_city, dep_day, guest_num))
    elif dep_airport:
        query_flights_info = '''SELECT airline_name, Flight.airline_id, 
    Flight.flight_id, a.airport_id as ap, d.airport_id as dp, 
    base_price, flight_status, a.city as acity, d.city as dcity,
    DATE(departure_time) as dep_day, TIME(departure_time) as dep_time,
    TIME(arrival_time) as arr_time, 
    (amount_of_seat - COUNT(ticket_id)) as remaining_seats 
    FROM Flight NATURAL JOIN Airline NATURAL JOIN Airplane LEFT OUTER JOIN Ticket ON 
    (Flight.airline_id,  Flight.flight_id)= (Ticket.airline_id,  Ticket.flight_id) 
    JOIN Airport as a JOIN Airport as d 
    WHERE  a.airport_id = arrival_airport AND d.airport_id = departure_airport
    AND d.airport_id = %s AND a.airport_id = %s AND DATE(departure_time) = %s 
    GROUP BY Flight.airline_id, Flight.flight_id having remaining_seats >= %s 
    ORDER BY base_price ASC'''
        cursor.execute(query_flights_info, (dep_airport, arr_airport, dep_day, guest_num))
        
    
    flights_info = cursor.fetchall()  
    
    
    cursor.close()
    
    print("number of records is:", len(flights_info))
    
    airline_name = []
    for i in range(len(flights_info)):
        airline_name.append(flights_info[i]["airline_name"])
        
    airline_name = list(set(airline_name))
    
    #Get available airports information
    cursor = conn.cursor();
    query_airport_info = "SELECT Distinct * FROM `Airport`"
    cursor.execute(query_airport_info)
    airports_info = cursor.fetchall()
    
    cursor.close()
    
    cities = []
    for i in range(len(airports_info)):
        cities.append(airports_info[i]["city"])
        
    cities = list(set(cities))

    
    return render_template('flight_one_way.html', 
                           cities = cities,
                           airports_info = airports_info, 
                           flights_info = flights_info,
                           airline_name = airline_name)
    
@app.route('/flight_round_trip', methods=['GET','POST'])
def flight_round_trip():
    dep_day = request.form.get('dep_day')
    dep_day = datetime.datetime.strptime(dep_day, "%m/%d/%Y").date()
    
    return_day = request.form.get('return_day')
    return_day = datetime.datetime.strptime(return_day, "%m/%d/%Y").date()

    #dep_day = "2019-05-15"
    guest_num = request.form.get('guest_num')
    
    dep_city = request.form.get('dep_city')
    
    ###BUG!!!!
    arr_city = request.form.get('arr_city')
    print(dep_day, dep_city, arr_city)
   
    #arr_city = "New York"
    
    dep_airport = request.form.get('dep_airport')
    
    arr_airport = request.form.get('arr_airport')
    
    
    #Get available flights information - First Flight
    cursor = conn.cursor();
    if dep_city:
        query_flights_info_first = '''SELECT airline_name, Flight.airline_id, 
    Flight.flight_id, a.airport_id as ap, d.airport_id as dp, 
    base_price, flight_status, a.city as acity, d.city as dcity,
    DATE(departure_time) as dep_day, TIME(departure_time) as dep_time,
    TIME(arrival_time) as arr_time,  
    (amount_of_seat - COUNT(ticket_id)) as remaining_seats 
    FROM Flight NATURAL JOIN Airline NATURAL JOIN Airplane LEFT OUTER JOIN Ticket ON 
    (Flight.airline_id,  Flight.flight_id)= (Ticket.airline_id,  Ticket.flight_id) 
    JOIN Airport as a JOIN Airport as d 
    WHERE  a.airport_id = arrival_airport AND d.airport_id = departure_airport
    AND d.city = %s AND a.city = %s AND DATE(departure_time) = %s 
    GROUP BY Flight.airline_id, Flight.flight_id having remaining_seats >= %s
    ORDER BY base_price ASC'''
        cursor.execute(query_flights_info_first, (dep_city, arr_city, dep_day, guest_num))
    elif dep_airport:
        query_flights_info_first = '''SELECT airline_name, Flight.airline_id, 
    Flight.flight_id, a.airport_id as ap, d.airport_id as dp, 
    base_price, flight_status, a.city as acity, d.city as dcity,
    DATE(departure_time) as dep_day, TIME(departure_time) as dep_time,
    TIME(arrival_time) as arr_time, 
    (amount_of_seat - COUNT(ticket_id)) as remaining_seats 
    FROM Flight NATURAL JOIN Airline NATURAL JOIN Airplane LEFT OUTER JOIN Ticket ON 
    (Flight.airline_id,  Flight.flight_id)= (Ticket.airline_id,  Ticket.flight_id) 
    JOIN Airport as a JOIN Airport as d 
    WHERE  a.airport_id = arrival_airport AND d.airport_id = departure_airport
    AND d.airport_id = %s AND a.airport_id = %s AND DATE(departure_time) = %s 
    GROUP BY Flight.airline_id, Flight.flight_id having remaining_seats >= %s 
    ORDER BY base_price ASC'''
        cursor.execute(query_flights_info_first, (dep_airport, arr_airport, dep_day, guest_num))
        
    
    flights_info_first = cursor.fetchall()  
 
    cursor.close()
    
    
    #Get available flights information - Second Flight
    cursor = conn.cursor();
    if dep_city:
        query_flights_info_second = '''SELECT airline_name, Flight.airline_id, 
    Flight.flight_id, a.airport_id as ap, d.airport_id as dp, 
    base_price, flight_status, a.city as acity, d.city as dcity,
    DATE(departure_time) as dep_day, TIME(departure_time) as dep_time,
    TIME(arrival_time) as arr_time,  
    (amount_of_seat - COUNT(ticket_id)) as remaining_seats 
    FROM Flight NATURAL JOIN Airline NATURAL JOIN Airplane LEFT OUTER JOIN Ticket ON 
    (Flight.airline_id,  Flight.flight_id)= (Ticket.airline_id,  Ticket.flight_id) 
    JOIN Airport as a JOIN Airport as d 
    WHERE  a.airport_id = arrival_airport AND d.airport_id = departure_airport
    AND d.city = %s AND a.city = %s AND DATE(departure_time) = %s 
    GROUP BY Flight.airline_id, Flight.flight_id having remaining_seats >= %s
    ORDER BY base_price ASC'''
        cursor.execute(query_flights_info_second, (arr_city, dep_city, return_day, guest_num))
    elif dep_airport:
        query_flights_info_second = '''SELECT airline_name, Flight.airline_id, 
    Flight.flight_id, a.airport_id as ap, d.airport_id as dp, 
    base_price, flight_status, a.city as acity, d.city as dcity,
    DATE(departure_time) as dep_day, TIME(departure_time) as dep_time,
    TIME(arrival_time) as arr_time, 
    (amount_of_seat - COUNT(ticket_id)) as remaining_seats 
    FROM Flight NATURAL JOIN Airline NATURAL JOIN Airplane LEFT OUTER JOIN Ticket ON 
    (Flight.airline_id,  Flight.flight_id)= (Ticket.airline_id,  Ticket.flight_id) 
    JOIN Airport as a JOIN Airport as d 
    WHERE  a.airport_id = arrival_airport AND d.airport_id = departure_airport
    AND d.airport_id = %s AND a.airport_id = %s AND DATE(departure_time) = %s 
    GROUP BY Flight.airline_id, Flight.flight_id having remaining_seats >= %s 
    ORDER BY base_price ASC'''
        cursor.execute(query_flights_info_second, (arr_airport, dep_airport, return_day, guest_num))
        
    
    flights_info_second = cursor.fetchall()  
 
    cursor.close()
    
    
    
    
    print("number of records of the first trip is:", len(query_flights_info_first))
    print("number of records of the second trip is:", len(query_flights_info_second))
    
    
    
    #Get available airports information
    cursor = conn.cursor();
    query_airport_info = "SELECT Distinct * FROM `Airport`"
    cursor.execute(query_airport_info)
    airports_info = cursor.fetchall()
    
    cursor.close()
    
    cities = []
    for i in range(len(airports_info)):
        cities.append(airports_info[i]["city"])
        
    cities = list(set(cities))
    
        
        
    
    
    return render_template('flight_round_trip.html', 
                           cities = cities,
                           airports_info = airports_info, 
                           flights_info_first = flights_info_first,
                           flights_info_second = flights_info_second,)
    

@app.route('/flight_history_c', methods=['GET','POST'])
def flight_history_c():
    
    username = session['username']
    print(username)
    
    if request.method == 'POST': 
        cursor = conn.cursor();
        airline_ids = request.form.getlist("selected_airline")
        order_date = request.form.get("order_date")
        print(airline_ids, order_date)
        
        if airline_ids:
            query_flights_info = '''SELECT ticket_id, sold_price, Flight.airline_id, Flight.flight_id, 
    a.airport_name, d.airport_name, a.airport_id as ap, d.airport_id as dp,
    flight_status, a.city as acity, d.city as dcity,
    DATE(departure_time) as dep_day, TIME(departure_time) as dep_time,
    TIME(arrival_time) as arr_time, TIMEDIFF(arrival_time,departure_time) as time_diff
    FROM Flight  NATURAL JOIN Ticket
    JOIN Airport as a JOIN Airport as d 
    WHERE  a.airport_id = arrival_airport AND d.airport_id = departure_airport
    AND departure_time <= CURTIME() AND customer_email = %s AND airline_id IN %s
    '''
        
            cursor.execute(query_flights_info, (username, airline_ids))
            tickets_info = cursor.fetchall()  
        elif order_date:
            if order_date == "DESC":
                print("true desc")
                query_flights_info = '''SELECT ticket_id, sold_price, Flight.airline_id, Flight.flight_id, 
    a.airport_name, d.airport_name, a.airport_id as ap, d.airport_id as dp,
    flight_status, a.city as acity, d.city as dcity,
    DATE(departure_time) as dep_day, TIME(departure_time) as dep_time,
    TIME(arrival_time) as arr_time, TIMEDIFF(arrival_time,departure_time) as time_diff
    FROM Flight  NATURAL JOIN Ticket
    JOIN Airport as a JOIN Airport as d 
    WHERE  a.airport_id = arrival_airport AND d.airport_id = departure_airport
    AND departure_time <= CURTIME() AND customer_email = %s ORDER BY departure_time DESC
    '''      
            elif order_date == "ASC":
                query_flights_info = '''SELECT ticket_id, sold_price, Flight.airline_id, Flight.flight_id, 
    a.airport_name, d.airport_name, a.airport_id as ap, d.airport_id as dp,
    flight_status, a.city as acity, d.city as dcity,
    DATE(departure_time) as dep_day, TIME(departure_time) as dep_time,
    TIME(arrival_time) as arr_time, TIMEDIFF(arrival_time,departure_time) as time_diff
    FROM Flight  NATURAL JOIN Ticket
    JOIN Airport as a JOIN Airport as d 
    WHERE  a.airport_id = arrival_airport AND d.airport_id = departure_airport
    AND departure_time <= CURTIME() AND customer_email = %s ORDER BY departure_time ASC
    '''    
                
            cursor.execute(query_flights_info, (username,))
            tickets_info = cursor.fetchall()  
            
            
        cursor.close()
    else:
        query_flights_info = '''SELECT ticket_id, sold_price, Flight.airline_id, Flight.flight_id, 
    a.airport_name, d.airport_name, a.airport_id as ap, d.airport_id as dp,
    flight_status, a.city as acity, d.city as dcity,
    DATE(departure_time) as dep_day, TIME(departure_time) as dep_time,
    TIME(arrival_time) as arr_time, TIMEDIFF(arrival_time,departure_time) as time_diff
    FROM Flight  NATURAL JOIN Ticket
    JOIN Airport as a JOIN Airport as d 
    WHERE  a.airport_id = arrival_airport AND d.airport_id = departure_airport
    AND departure_time <= CURTIME() AND customer_email = %s
    '''
        cursor = conn.cursor();
        cursor.execute(query_flights_info, (username,))
        tickets_info = cursor.fetchall()     
        cursor.close()
    
    
    
   
    print("total amount of tickets: ", len(tickets_info))
    
    cursor = conn.cursor();
    query_airlines_info = '''
    SELECT DISTINCT airline_id, airline_name FROM Flight  NATURAL JOIN Airline NATURAL JOIN Ticket
    JOIN Airport as a JOIN Airport as d 
    WHERE  a.airport_id = arrival_airport AND d.airport_id = departure_airport
    AND departure_time <= CURTIME() AND customer_email = %s'''
    cursor.execute(query_airlines_info, (username))
    airlines_info = cursor.fetchall()     
    cursor.close()
    
    
    return render_template('flight_history_c.html', 
                               username=username, tickets_info = tickets_info,
                               airlines_info = airlines_info)
    

@app.route('/future_flights_c', methods=['GET','POST'])
def future_flights_c():
    
    username = session['username']
    print(username)
    
    if request.method == 'POST': 
        cursor = conn.cursor();
        airline_ids = request.form.getlist("selected_airline")
        order_date = request.form.get("order_date")
        print(airline_ids, order_date)
        
        if airline_ids:
            query_flights_info = '''SELECT ticket_id, sold_price, flight_status, Flight.airline_id, Flight.flight_id, 
    a.airport_name, d.airport_name, a.airport_id as ap, d.airport_id as dp,
    flight_status, a.city as acity, d.city as dcity,
    DATE(departure_time) as dep_day, TIME(departure_time) as dep_time,
    TIME(arrival_time) as arr_time, TIMEDIFF(arrival_time,departure_time) as time_diff
    FROM Flight  NATURAL JOIN Ticket
    JOIN Airport as a JOIN Airport as d 
    WHERE  a.airport_id = arrival_airport AND d.airport_id = departure_airport
    AND departure_time > CURTIME() AND customer_email = %s AND airline_id IN %s
    '''
        
            cursor.execute(query_flights_info, (username, airline_ids))
            tickets_info = cursor.fetchall()  
        elif order_date:
            if order_date == "DESC":
                print("true desc")
                query_flights_info = '''SELECT ticket_id, sold_price, flight_status, Flight.airline_id, Flight.flight_id, 
    a.airport_name, d.airport_name, a.airport_id as ap, d.airport_id as dp,
    flight_status, a.city as acity, d.city as dcity,
    DATE(departure_time) as dep_day, TIME(departure_time) as dep_time,
    TIME(arrival_time) as arr_time, TIMEDIFF(arrival_time,departure_time) as time_diff
    FROM Flight  NATURAL JOIN Ticket
    JOIN Airport as a JOIN Airport as d 
    WHERE  a.airport_id = arrival_airport AND d.airport_id = departure_airport
    AND departure_time > CURTIME() AND customer_email = %s ORDER BY departure_time DESC
    '''      
            elif order_date == "ASC":
                query_flights_info = '''SELECT ticket_id, sold_price, flight_status, Flight.airline_id, Flight.flight_id, 
    a.airport_name, d.airport_name, a.airport_id as ap, d.airport_id as dp,
    flight_status, a.city as acity, d.city as dcity,
    DATE(departure_time) as dep_day, TIME(departure_time) as dep_time,
    TIME(arrival_time) as arr_time, TIMEDIFF(arrival_time,departure_time) as time_diff
    FROM Flight  NATURAL JOIN Ticket
    JOIN Airport as a JOIN Airport as d 
    WHERE  a.airport_id = arrival_airport AND d.airport_id = departure_airport
    AND departure_time > CURTIME() AND customer_email = %s ORDER BY departure_time ASC
    '''    
                
            cursor.execute(query_flights_info, (username,))
            tickets_info = cursor.fetchall()  
            
            
        cursor.close()
    else:
        query_flights_info = '''SELECT ticket_id, sold_price, flight_status, Flight.airline_id, Flight.flight_id, 
    a.airport_name, d.airport_name, a.airport_id as ap, d.airport_id as dp,
    flight_status, a.city as acity, d.city as dcity,
    DATE(departure_time) as dep_day, TIME(departure_time) as dep_time,
    TIME(arrival_time) as arr_time, TIMEDIFF(arrival_time,departure_time) as time_diff
    FROM Flight  NATURAL JOIN Ticket
    JOIN Airport as a JOIN Airport as d 
    WHERE  a.airport_id = arrival_airport AND d.airport_id = departure_airport
    AND departure_time > CURTIME() AND customer_email = %s
    '''
        cursor = conn.cursor();
        cursor.execute(query_flights_info, (username,))
        tickets_info = cursor.fetchall()     
        cursor.close()
    
    
    
   
    print("total amount of tickets: ", len(tickets_info))
    
    cursor = conn.cursor();
    query_airlines_info = '''
    SELECT DISTINCT airline_id, airline_name FROM Flight  NATURAL JOIN Airline NATURAL JOIN Ticket
    JOIN Airport as a JOIN Airport as d 
    WHERE  a.airport_id = arrival_airport AND d.airport_id = departure_airport
    AND departure_time > CURTIME() AND customer_email = %s'''
    cursor.execute(query_airlines_info, (username))
    airlines_info = cursor.fetchall()     
    cursor.close()
    
    
    return render_template('future_flights_c.html', 
                               username=username, tickets_info = tickets_info,
                               airlines_info = airlines_info)
   





@app.route('/flight_booking_c', methods=['GET','POST'])
def flight_booking_c():
    username = session['username']
    print(username)
    
    if request.method == 'POST': 
        flight_full_id = request.form["flight_full_id"]
        
        airline_id = flight_full_id[:2]
        flight_id = flight_full_id[2:]
        print(airline_id, flight_id)
        
        cursor = conn.cursor();
        query_flights_info = '''SELECT airline_name,airline_id, flight_id, a.airport_name, d.airport_name, 
        base_price, a.city as acity, d.city as dcity,
        DATE(departure_time) as dep_day, DATE(arrival_time) as arr_day,
        TIME(departure_time) as dep_time,TIME(arrival_time) as arr_time, 
        TIMEDIFF(arrival_time,departure_time) as time_diff
        
        FROM Flight NATURAL JOIN Airline JOIN Airport as a JOIN Airport as d 
        WHERE a.airport_id = arrival_airport AND d.airport_id = departure_airport
        AND airline_id = %s AND flight_id = %s'''
        cursor.execute(query_flights_info, (airline_id, flight_id))
        flights_info = cursor.fetchone()     
        cursor.close()
        
        
        
        base_price = flights_info["base_price"]
        
        cursor = conn.cursor()
        query_capacity_info = '''SELECT COUNT(ticket_id)/amount_of_seat as booked_ratio  
        FROM Flight NATURAL JOIN Airplane
        LEFT OUTER JOIN Ticket ON 
        (Flight.airline_id,  Flight.flight_id)= (Ticket.airline_id,  Ticket.flight_id) 
        WHERE Flight.airline_id = %s AND Flight.flight_id = %s'''
        cursor.execute(query_capacity_info, (airline_id, flight_id))
        cursor.close()
        booked_ratio = cursor.fetchone()["booked_ratio"]    
        
        if booked_ratio < 0.7:
            price = base_price 
        else:
            price = base_price * 1.2
        
        
    
    cursor = conn.cursor();
    query_user_name = '''SELECT first_name, last_name,passport_number, passport_expiration, 
                      passport_country, date_of_birth, phone_number FROM `Customer` WHERE customer_email = %s'''
    cursor.execute(query_user_name, (username))
    customer_info = cursor.fetchone()
    
    
    cursor.close()
   
    return render_template('flight_booking_c.html', 
                           username=username, flight_full_id = flight_full_id, 
                           flights_info = flights_info, price = price, customer_info = customer_info)
                          # first_name = first_name, last_name = last_name)
                          
@app.route('/flight_booking_round_c', methods=['GET','POST'])
def flight_booking_round_c():
    username = session['username']
    print(username)
    
    if request.method == 'POST': 

        
        flight_full_id1 = request.form["flight_full_id1"]
        flight_full_id2 = request.form["flight_full_id2"]
        
        airline_id1 = flight_full_id1[:2]
        flight_id1 = flight_full_id1[2:]
        
        airline_id2 = flight_full_id2[:2]
        flight_id2 = flight_full_id2[2:]
       
        
        cursor = conn.cursor();
        query_flights_info1 = '''SELECT airline_name,airline_id, flight_id, a.airport_name, d.airport_name, 
        base_price, a.city as acity, d.city as dcity,
        DATE(departure_time) as dep_day, DATE(arrival_time) as arr_day,
        TIME(departure_time) as dep_time,TIME(arrival_time) as arr_time, 
        TIMEDIFF(arrival_time,departure_time) as time_diff
        FROM Flight NATURAL JOIN Airline JOIN Airport as a JOIN Airport as d 
        WHERE a.airport_id = arrival_airport AND d.airport_id = departure_airport
        AND airline_id = %s AND flight_id = %s'''
        cursor.execute(query_flights_info1, (airline_id1, flight_id1))
        flights_info1 = cursor.fetchone()     
        cursor.close()
        
        cursor = conn.cursor();
        query_flights_info2 = '''SELECT airline_name,airline_id, flight_id, a.airport_name, d.airport_name, 
        base_price, a.city as acity, d.city as dcity,
        DATE(departure_time) as dep_day, DATE(arrival_time) as arr_day,
        TIME(departure_time) as dep_time,TIME(arrival_time) as arr_time, 
        TIMEDIFF(arrival_time,departure_time) as time_diff
        FROM Flight NATURAL JOIN Airline JOIN Airport as a JOIN Airport as d 
        WHERE a.airport_id = arrival_airport AND d.airport_id = departure_airport
        AND airline_id = %s AND flight_id = %s'''
        cursor.execute(query_flights_info2, (airline_id2, flight_id2))
        flights_info2 = cursor.fetchone()     
        cursor.close()
        
        
        
        base_price1 = flights_info1["base_price"]
        base_price2 = flights_info2["base_price"]
        
        cursor = conn.cursor()
        query_capacity_info1 = '''SELECT COUNT(ticket_id)/amount_of_seat as booked_ratio  
        FROM Flight NATURAL JOIN Airplane
        LEFT OUTER JOIN Ticket ON 
        (Flight.airline_id,  Flight.flight_id)= (Ticket.airline_id,  Ticket.flight_id) 
        WHERE Flight.airline_id = %s AND Flight.flight_id = %s'''
        cursor.execute(query_capacity_info1, (airline_id1, flight_id1))
        cursor.close()
        booked_ratio1 = cursor.fetchone()["booked_ratio"]  
        
        cursor = conn.cursor()
        query_capacity_info2 = '''SELECT COUNT(ticket_id)/amount_of_seat as booked_ratio  
        FROM Flight NATURAL JOIN Airplane
        LEFT OUTER JOIN Ticket ON 
        (Flight.airline_id,  Flight.flight_id)= (Ticket.airline_id,  Ticket.flight_id) 
        WHERE Flight.airline_id = %s AND Flight.flight_id = %s'''
        cursor.execute(query_capacity_info2, (airline_id2, flight_id2))
        cursor.close()
        booked_ratio2 = cursor.fetchone()["booked_ratio"]  
        
        if booked_ratio1 < 0.7:
            price1 = base_price1 
        else:
            price1 = base_price1 * 1.2
            
        if booked_ratio2 < 0.7:
            price2 = base_price2 
        else:
            price2 = base_price2 * 1.2
        
        
        total_price = price1+price2
        
        
    
    cursor = conn.cursor();
    query_user_info = '''SELECT first_name, last_name,passport_number, passport_expiration, 
                      passport_country, date_of_birth, phone_number FROM `Customer` WHERE customer_email = %s'''
    cursor.execute(query_user_info, (username))
    customer_info = cursor.fetchone()
    
    
    cursor.close()
   
    return render_template('flight_booking_round_c.html', 
                           username=username, 
                           flight_full_id1 = flight_full_id1, flight_full_id2 = flight_full_id2,
                           flights_info1 = flights_info1, flights_info2 = flights_info2, 
                           price1 = price1, price2 = price2,
                           total_price = total_price, 
                           customer_info = customer_info)
                          
 
                          
@app.route('/round_booking_complete_c', methods=['GET','POST'])
def round_booking_complete_c():
    username = session['username']
    #dep_day = session['dep_day']
    if request.method == 'POST':
        
        passenger_email = request.form.get("passenger_email")
        passenger_first_name = request.form.get("passenger_first_name")
        passenger_last_name = request.form.get("passenger_last_name")
        passenger_passport = request.form.get("passport_number")
        print('!',passenger_email)
        print('!!!',passenger_passport)
        
        cursor = conn.cursor()
        query_passenger_info = '''SELECT * FROM Customer WHERE 
        customer_email = %s AND first_name = %s AND last_name = %s
        AND passport_number = %s'''
        cursor.execute(query_passenger_info, (passenger_email, passenger_first_name,
                                              passenger_last_name,passenger_passport))
        customer_info = cursor.fetchone()     
        cursor.close()
        if customer_info == None:
            error = "There is no such customer in the database or the customer information is wrong."
            return render_template('booking_failed_c.html', 
                           error = error)
            
        
        
        card_type = request.form.get("card_type")  
        card_holder = request.form.get("card_holder") 
        card_number = request.form.get("card_number")
        
        card_expiration = request.form.get("card_expiration")
        card_expiration = datetime.datetime.strptime(card_expiration, "%m/%d/%Y").date()
        
        flight_full_id1 = request.form.get("flight_full_id1")
        airline_id1 = flight_full_id1[:2]
        flight_id1 = flight_full_id1[2:]
        print(airline_id1, flight_id1)
        
        flight_full_id2 = request.form.get("flight_full_id2")
        airline_id2 = flight_full_id2[:2]
        flight_id2 = flight_full_id2[2:]
        print(airline_id2, flight_id2)
     
        price1 = int(float(request.form.get("price1")[1:]))
        price2 = int(float(request.form.get("price2")[1:]))
        
   
    
    ticket_id1 = "E" + str(int(time.time()*10-randint(0, 9)))
    ticket_id2 = "E" + str(int(time.time()*10-randint(0, 9)))
    print(ticket_id1)
    print(ticket_id2)
    
    
    cursor = conn.cursor();
    query_flights_info1 = '''SELECT airline_id, flight_id,  
    a.city as acity, d.city as dcity,
    DATE(departure_time) as dep_day, DATE(arrival_time) as arr_day,
    TIME(departure_time) as dep_time,TIME(arrival_time) as arr_time
    FROM Flight NATURAL JOIN Airline JOIN Airport as a 
    JOIN Airport as d WHERE a.airport_id = arrival_airport 
    AND d.airport_id = departure_airport
    AND airline_id = %s AND flight_id = %s'''
    cursor.execute(query_flights_info1, (airline_id1, flight_id1))
    flights_info1 = cursor.fetchone()     
    cursor.close()
    
    cursor = conn.cursor();
    query_flights_info2 = '''SELECT airline_id, flight_id,  
    a.city as acity, d.city as dcity,
    DATE(departure_time) as dep_day, DATE(arrival_time) as arr_day,
    TIME(departure_time) as dep_time,TIME(arrival_time) as arr_time
    FROM Flight NATURAL JOIN Airline JOIN Airport as a 
    JOIN Airport as d WHERE a.airport_id = arrival_airport 
    AND d.airport_id = departure_airport
    AND airline_id = %s AND flight_id = %s'''
    cursor.execute(query_flights_info2, (airline_id2, flight_id2))
    flights_info2 = cursor.fetchone()     
    cursor.close()
    
    
    cursor = conn.cursor()
    query1 = 'SELECT * FROM Ticket WHERE customer_email = %s AND airline_id = %s AND flight_id = %s'
    cursor.execute(query1, (passenger_email, airline_id1, flight_id1))
	#stores the results in a variable
    data1 = cursor.fetchone()
    cursor.close()
    
    
    cursor = conn.cursor()
    query2 = 'SELECT * FROM Ticket WHERE customer_email = %s AND airline_id = %s AND flight_id = %s'
    cursor.execute(query2, (passenger_email, airline_id2, flight_id2))
	#stores the results in a variable
    data2 = cursor.fetchone()
    cursor.close()
	
    
    error = None
    
    if(data1):
		#If the previous query returns data, then user exists
        error = '''The customer has already purchased a ticket for the flight %s %s,
                   and the ticket id is %s
                '''%(airline_id1, flight_id1, data1["ticket_id"])
        
        return render_template('booking_failed_c.html', error = error)
    
    elif(data2):
        #If the previous query returns data, then user exists
        error = '''The customer has already purchased a ticket for the flight %s %s,
                   and the ticket id is %s
                '''%(airline_id2, flight_id2, data2["ticket_id"])
        
        return render_template('booking_failed_c.html', error = error)
        
    else:
        cursor = conn.cursor()
        print(ticket_id1, airline_id1, flight_id1, price1, username, card_type,
                          card_number, card_holder, card_expiration, username)
        insert1 = '''INSERT INTO `Ticket` (`ticket_id`, `booking_time`, `airline_id`, `flight_id`, `sold_price`, 
        `credit_or_debit`, `card_number`, `name_on_card`, `expiration_date`,`customer_email`, 
        `agent_email`, `commission`) VALUES (%s, CURRENT_TIMESTAMP(), %s, %s, %s, 
         %s, %s, %s, %s, %s, NULL, NULL)'''
        cursor.execute(insert1, (ticket_id1, airline_id1, flight_id1, price1, card_type,
                          card_number, card_holder, card_expiration, passenger_email))
        
        print(ticket_id2, airline_id2, flight_id2, price2, username, card_type,
                          card_number, card_holder, card_expiration, username)
        insert2 = '''INSERT INTO `Ticket` (`ticket_id`, `booking_time`, `airline_id`, `flight_id`, `sold_price`, 
        `credit_or_debit`, `card_number`, `name_on_card`, `expiration_date`,`customer_email`, 
        `agent_email`, `commission`) VALUES (%s, CURRENT_TIMESTAMP(), %s, %s, %s, 
         %s, %s, %s, %s, %s, NULL, NULL)'''
        cursor.execute(insert2, (ticket_id2, airline_id2, flight_id2, price2, card_type,
                          card_number, card_holder, card_expiration, passenger_email))

        
        conn.commit()
        cursor.close()
        print("insert complete.")
        
        
        
        return render_template('round_booking_complete_c.html', 
                               username=username, flights_info1 = flights_info1,
                               flights_info2 = flights_info2,
                               customer_info = customer_info, ticket_id1 = ticket_id1,
                               ticket_id2 = ticket_id2)
    

                          
@app.route('/booking_complete_c', methods=['GET','POST'])
def booking_complete_c():
    username = session['username']
    #dep_day = session['dep_day']
    if request.method == 'POST':
       
        
        card_type = request.form.get("card_type")  
        card_holder = request.form.get("card_holder") 
        card_number = request.form.get("card_number")
        
        card_expiration = request.form.get("card_expiration")
        card_expiration = datetime.datetime.strptime(card_expiration, "%m/%d/%Y").date()
        
        flight_full_id = request.form.get("flight_full_id")
        airline_id = flight_full_id[:2]
        flight_id = flight_full_id[2:]
        print(airline_id, flight_id)
     
        price = int(float(request.form.get("price")[1:]))
        
    
    
    ticket_id = "E" + str(int(time.time()*10))
    print(ticket_id)
    
    
    cursor = conn.cursor();
    query_flights_info = '''SELECT airline_id, flight_id,  
    a.city as acity, d.city as dcity,
    DATE(departure_time) as dep_day, DATE(arrival_time) as arr_day,
    TIME(departure_time) as dep_time,TIME(arrival_time) as arr_time
    FROM Flight NATURAL JOIN Airline JOIN Airport as a 
    JOIN Airport as d WHERE a.airport_id = arrival_airport 
    AND d.airport_id = departure_airport
    AND airline_id = %s AND flight_id = %s'''
    cursor.execute(query_flights_info, (airline_id, flight_id))
    flights_info = cursor.fetchone()     
    cursor.close()
    
    
    cursor = conn.cursor()
    query = 'SELECT * FROM Ticket WHERE customer_email = %s AND airline_id = %s AND flight_id = %s'
    cursor.execute(query, (username,airline_id, flight_id))
	#stores the results in a variable
    data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
    error = None
    if(data):
		#If the previous query returns data, then user exists
        error = '''You have already purchased a ticket for the flight,
                   and the ticket id is %s
                '''%(data["ticket_id"])
        return render_template('booking_failed_c.html', error = error)
    else:
        print(ticket_id, airline_id, flight_id, price, username, card_type,
                          card_number, card_holder, card_expiration, username)
        insert = '''INSERT INTO `Ticket` (`ticket_id`, `booking_time`, `airline_id`, `flight_id`, `sold_price`, 
        `credit_or_debit`, `card_number`, `name_on_card`, `expiration_date`,`customer_email`, 
        `agent_email`, `commission`) VALUES (%s, CURRENT_TIMESTAMP(), %s, %s, %s, 
         %s, %s, %s, %s, %s, Null, Null)'''
        cursor.execute(insert, (ticket_id, airline_id, flight_id, price, card_type,
                          card_number, card_holder, card_expiration, username,))
        conn.commit()
        cursor.close()
        
        cursor = conn.cursor()
        query_user_name = "SELECT * FROM `Customer` WHERE customer_email = %s"
        cursor.execute(query_user_name, (username))
        customer_info = cursor.fetchone()
        cursor.close()
        
        
        return render_template('booking_complete_c.html', 
                               username=username, flights_info = flights_info,
                               customer_info = customer_info, ticket_id = ticket_id)
    
#                             

@app.route('/flight_history_a', methods=['GET','POST'])
def flight_history_a():
    
    username = session['username']
    print(username)
    
    if request.method == 'POST': 
        cursor = conn.cursor();
        airline_ids = request.form.getlist("selected_airline")
        order_date = request.form.get("order_date")
        print(airline_ids, order_date)
        
        if airline_ids:
            query_flights_info = '''SELECT ticket_id, sold_price, customer_email, 
            Flight.airline_id, Flight.flight_id, 
    a.airport_name, d.airport_name, a.airport_id as ap, d.airport_id as dp,
    flight_status, a.city as acity, d.city as dcity,
    DATE(departure_time) as dep_day, TIME(departure_time) as dep_time,
    TIME(arrival_time) as arr_time, TIMEDIFF(arrival_time,departure_time) as time_diff,
    commission
    FROM Flight  NATURAL JOIN Ticket 
    JOIN Airport as a JOIN Airport as d 
    WHERE  a.airport_id = arrival_airport AND d.airport_id = departure_airport
    AND departure_time <= CURTIME() AND agent_email = %s AND airline_id IN %s
    '''
        
            cursor.execute(query_flights_info, (username, airline_ids))
            tickets_info = cursor.fetchall()  
        elif order_date:
            if order_date == "DESC":
                print("true desc")
                query_flights_info = '''SELECT ticket_id, sold_price, customer_email, 
            Flight.airline_id, Flight.flight_id, 
    a.airport_name, d.airport_name, a.airport_id as ap, d.airport_id as dp,
    flight_status, a.city as acity, d.city as dcity,
    DATE(departure_time) as dep_day, TIME(departure_time) as dep_time,
    TIME(arrival_time) as arr_time, TIMEDIFF(arrival_time,departure_time) as time_diff,
    commission
    FROM Flight  NATURAL JOIN Ticket 
    JOIN Airport as a JOIN Airport as d 
    WHERE  a.airport_id = arrival_airport AND d.airport_id = departure_airport
    AND departure_time <= CURTIME() AND agent_email = %s ORDER BY departure_time DESC
    '''      
            elif order_date == "ASC":
                query_flights_info = '''SELECT ticket_id, sold_price, customer_email, 
            Flight.airline_id, Flight.flight_id, 
    a.airport_name, d.airport_name, a.airport_id as ap, d.airport_id as dp,
    flight_status, a.city as acity, d.city as dcity,
    DATE(departure_time) as dep_day, TIME(departure_time) as dep_time,
    TIME(arrival_time) as arr_time, TIMEDIFF(arrival_time,departure_time) as time_diff,
    commission
    FROM Flight  NATURAL JOIN Ticket 
    JOIN Airport as a JOIN Airport as d 
    WHERE  a.airport_id = arrival_airport AND d.airport_id = departure_airport
    AND departure_time <= CURTIME() AND agent_email = %s ORDER BY departure_time ASC
    '''    
                
            cursor.execute(query_flights_info, (username,))
            tickets_info = cursor.fetchall()  
            
            
        cursor.close()
    else:
        query_flights_info = '''SELECT ticket_id, sold_price, customer_email, 
            Flight.airline_id, Flight.flight_id, 
    a.airport_name, d.airport_name, a.airport_id as ap, d.airport_id as dp,
    flight_status, a.city as acity, d.city as dcity,
    DATE(departure_time) as dep_day, TIME(departure_time) as dep_time,
    TIME(arrival_time) as arr_time, TIMEDIFF(arrival_time,departure_time) as time_diff,
    commission
    FROM Flight  NATURAL JOIN Ticket 
    JOIN Airport as a JOIN Airport as d 
    WHERE  a.airport_id = arrival_airport AND d.airport_id = departure_airport
    AND departure_time <= CURTIME() AND agent_email = %s
    '''
        cursor = conn.cursor();
        cursor.execute(query_flights_info, (username,))
        tickets_info = cursor.fetchall()     
        cursor.close()
    
    
    
   
    print("total amount of tickets: ", len(tickets_info))
    
    cursor = conn.cursor();
    query_airlines_info = '''
    SELECT DISTINCT airline_id, airline_name FROM Flight  NATURAL JOIN Airline NATURAL JOIN Ticket
    JOIN Airport as a JOIN Airport as d 
    WHERE  a.airport_id = arrival_airport AND d.airport_id = departure_airport
    AND departure_time <= CURTIME() AND agent_email = %s'''
    cursor.execute(query_airlines_info, (username))
    airlines_info = cursor.fetchall()     
    cursor.close()
    
    
    return render_template('flight_history_a.html', 
                               username=username, tickets_info = tickets_info,
                               airlines_info = airlines_info)
    

    
@app.route('/future_flights_a', methods=['GET','POST'])
def future_flights_a():
    
    username = session['username']
    print(username)
    
    if request.method == 'POST': 
        cursor = conn.cursor();
        airline_ids = request.form.getlist("selected_airline")
        order_date = request.form.get("order_date")
        print(airline_ids, order_date)
        
        if airline_ids:
            query_flights_info = '''SELECT ticket_id, sold_price, commission, flight_status, customer_email, 
            Flight.airline_id, Flight.flight_id, 
    a.airport_name, d.airport_name, a.airport_id as ap, d.airport_id as dp,
    flight_status, a.city as acity, d.city as dcity,
    DATE(departure_time) as dep_day, TIME(departure_time) as dep_time,
    TIME(arrival_time) as arr_time, TIMEDIFF(arrival_time,departure_time) as time_diff
    FROM Flight  NATURAL JOIN Ticket 
    JOIN Airport as a JOIN Airport as d 
    WHERE  a.airport_id = arrival_airport AND d.airport_id = departure_airport
    AND departure_time > CURTIME() AND agent_email = %s AND airline_id IN %s
    '''
        
            cursor.execute(query_flights_info, (username, airline_ids))
            tickets_info = cursor.fetchall()  
        elif order_date:
            if order_date == "DESC":
                print("true desc")
                query_flights_info = '''SELECT ticket_id, sold_price, commission, flight_status, customer_email, 
            Flight.airline_id, Flight.flight_id, 
    a.airport_name, d.airport_name, a.airport_id as ap, d.airport_id as dp,
    flight_status, a.city as acity, d.city as dcity,
    DATE(departure_time) as dep_day, TIME(departure_time) as dep_time,
    TIME(arrival_time) as arr_time, TIMEDIFF(arrival_time,departure_time) as time_diff
    FROM Flight  NATURAL JOIN Ticket 
    JOIN Airport as a JOIN Airport as d 
    WHERE  a.airport_id = arrival_airport AND d.airport_id = departure_airport
    AND departure_time > CURTIME() AND agent_email = %s ORDER BY departure_time DESC
    '''      
            elif order_date == "ASC":
                query_flights_info = '''SELECT ticket_id, sold_price, commission, flight_status, customer_email, 
            Flight.airline_id, Flight.flight_id, 
    a.airport_name, d.airport_name, a.airport_id as ap, d.airport_id as dp,
    flight_status, a.city as acity, d.city as dcity,
    DATE(departure_time) as dep_day, TIME(departure_time) as dep_time,
    TIME(arrival_time) as arr_time, TIMEDIFF(arrival_time,departure_time) as time_diff
    FROM Flight  NATURAL JOIN Ticket 
    JOIN Airport as a JOIN Airport as d 
    WHERE  a.airport_id = arrival_airport AND d.airport_id = departure_airport
    AND departure_time > CURTIME() AND agent_email = %s ORDER BY departure_time ASC
    '''    
                
            cursor.execute(query_flights_info, (username,))
            tickets_info = cursor.fetchall()  
            
            
        cursor.close()
    else:
        query_flights_info = '''SELECT ticket_id, sold_price, commission, flight_status, customer_email, 
            Flight.airline_id, Flight.flight_id, 
    a.airport_name, d.airport_name, a.airport_id as ap, d.airport_id as dp,
    flight_status, a.city as acity, d.city as dcity,
    DATE(departure_time) as dep_day, TIME(departure_time) as dep_time,
    TIME(arrival_time) as arr_time, TIMEDIFF(arrival_time,departure_time) as time_diff
    FROM Flight  NATURAL JOIN Ticket 
    JOIN Airport as a JOIN Airport as d 
    WHERE  a.airport_id = arrival_airport AND d.airport_id = departure_airport
    AND departure_time > CURTIME() AND agent_email = %s
    '''
        cursor = conn.cursor();
        cursor.execute(query_flights_info, (username,))
        tickets_info = cursor.fetchall()     
        cursor.close()
    
    
    
   
    print("total amount of tickets: ", len(tickets_info))
    
    cursor = conn.cursor();
    query_airlines_info = '''
    SELECT DISTINCT airline_id, airline_name FROM Flight  NATURAL JOIN Airline NATURAL JOIN Ticket
    JOIN Airport as a JOIN Airport as d 
    WHERE  a.airport_id = arrival_airport AND d.airport_id = departure_airport
    AND departure_time > CURTIME() AND agent_email = %s'''
    cursor.execute(query_airlines_info, (username))
    airlines_info = cursor.fetchall()     
    cursor.close()
    
    
    return render_template('future_flights_a.html', 
                               username=username, tickets_info = tickets_info,
                               airlines_info = airlines_info)
   




                         
                          
@app.route('/flight_booking_a', methods=['GET','POST'])
def flight_booking_a():
    username = session['username']
    print(username)
    
    if request.method == 'POST': 
        
        
        
        
        flight_full_id = request.form["flight_full_id"]
        
        airline_id = flight_full_id[:2]
        flight_id = flight_full_id[2:]
        print(airline_id, flight_id)
        
        cursor = conn.cursor();
        query_flights_info = '''SELECT airline_name,airline_id, flight_id, a.airport_name, d.airport_name, 
        base_price, a.city as acity, d.city as dcity,
        DATE(departure_time) as dep_day, DATE(arrival_time) as arr_day,
        TIME(departure_time) as dep_time,TIME(arrival_time) as arr_time, 
        TIMEDIFF(arrival_time,departure_time) as time_diff
        FROM Flight NATURAL JOIN Airline JOIN Airport as a JOIN Airport as d 
        WHERE a.airport_id = arrival_airport AND d.airport_id = departure_airport
        AND airline_id = %s AND flight_id = %s'''
        cursor.execute(query_flights_info, (airline_id, flight_id))
        flights_info = cursor.fetchone()     
        cursor.close()
        
        
        
        base_price = flights_info["base_price"]
        
        cursor = conn.cursor()
        query_capacity_info = '''SELECT COUNT(ticket_id)/amount_of_seat as booked_ratio  
        FROM Flight NATURAL JOIN Airplane
        LEFT OUTER JOIN Ticket ON 
        (Flight.airline_id,  Flight.flight_id)= (Ticket.airline_id,  Ticket.flight_id) 
        WHERE Flight.airline_id = %s AND Flight.flight_id = %s'''
        cursor.execute(query_capacity_info, (airline_id, flight_id))
        cursor.close()
        booked_ratio = cursor.fetchone()["booked_ratio"]    
        
        if booked_ratio < 0.7:
            price = base_price 
        else:
            price = base_price * 1.2
        
        commission = int(0.1 * price)
        total_payment = commission + price
        
    
    cursor = conn.cursor();
    query_agent_info= '''SELECT * FROM `Booking_agent` WHERE agent_email = %s'''
    cursor.execute(query_agent_info, (username))
    agent_info = cursor.fetchone()
    
    
    cursor.close()
   
    return render_template('flight_booking_a.html', 
                           username=username, 
                           flight_full_id = flight_full_id, 
                           flights_info = flights_info, 
                           price = price, commission = commission,total_payment = total_payment,
                           agent_info = agent_info)
                          # first_name = first_name, last_name = last_name)
                          

@app.route('/flight_booking_round_a', methods=['GET','POST'])
def flight_booking_round_a():
    username = session['username']
    print(username)
    
    if request.method == 'POST': 

        
        flight_full_id1 = request.form["flight_full_id1"]
        flight_full_id2 = request.form["flight_full_id2"]
        
        airline_id1 = flight_full_id1[:2]
        flight_id1 = flight_full_id1[2:]
        
        airline_id2 = flight_full_id2[:2]
        flight_id2 = flight_full_id2[2:]
       
        
        cursor = conn.cursor();
        query_flights_info1 = '''SELECT airline_name,airline_id, flight_id, a.airport_name, d.airport_name, 
        base_price, a.city as acity, d.city as dcity,
        DATE(departure_time) as dep_day, DATE(arrival_time) as arr_day,
        TIME(departure_time) as dep_time,TIME(arrival_time) as arr_time, 
        TIMEDIFF(arrival_time,departure_time) as time_diff
        FROM Flight NATURAL JOIN Airline JOIN Airport as a JOIN Airport as d 
        WHERE a.airport_id = arrival_airport AND d.airport_id = departure_airport
        AND airline_id = %s AND flight_id = %s'''
        cursor.execute(query_flights_info1, (airline_id1, flight_id1))
        flights_info1 = cursor.fetchone()     
        cursor.close()
        
        cursor = conn.cursor();
        query_flights_info2 = '''SELECT airline_name,airline_id, flight_id, a.airport_name, d.airport_name, 
        base_price, a.city as acity, d.city as dcity,
        DATE(departure_time) as dep_day, DATE(arrival_time) as arr_day,
        TIME(departure_time) as dep_time,TIME(arrival_time) as arr_time, 
        TIMEDIFF(arrival_time,departure_time) as time_diff
        FROM Flight NATURAL JOIN Airline JOIN Airport as a JOIN Airport as d 
        WHERE a.airport_id = arrival_airport AND d.airport_id = departure_airport
        AND airline_id = %s AND flight_id = %s'''
        cursor.execute(query_flights_info2, (airline_id2, flight_id2))
        flights_info2 = cursor.fetchone()     
        cursor.close()
        
        
        
        base_price1 = flights_info1["base_price"]
        base_price2 = flights_info2["base_price"]
        
        cursor = conn.cursor()
        query_capacity_info1 = '''SELECT COUNT(ticket_id)/amount_of_seat as booked_ratio  
        FROM Flight NATURAL JOIN Airplane
        LEFT OUTER JOIN Ticket ON 
        (Flight.airline_id,  Flight.flight_id)= (Ticket.airline_id,  Ticket.flight_id) 
        WHERE Flight.airline_id = %s AND Flight.flight_id = %s'''
        cursor.execute(query_capacity_info1, (airline_id1, flight_id1))
        cursor.close()
        booked_ratio1 = cursor.fetchone()["booked_ratio"]  
        
        cursor = conn.cursor()
        query_capacity_info2 = '''SELECT COUNT(ticket_id)/amount_of_seat as booked_ratio  
        FROM Flight NATURAL JOIN Airplane
        LEFT OUTER JOIN Ticket ON 
        (Flight.airline_id,  Flight.flight_id)= (Ticket.airline_id,  Ticket.flight_id) 
        WHERE Flight.airline_id = %s AND Flight.flight_id = %s'''
        cursor.execute(query_capacity_info2, (airline_id2, flight_id2))
        cursor.close()
        booked_ratio2 = cursor.fetchone()["booked_ratio"]  
        
        if booked_ratio1 < 0.7:
            price1 = base_price1 
        else:
            price1 = base_price1 * 1.2
            
        if booked_ratio2 < 0.7:
            price2 = base_price2 
        else:
            price2 = base_price2 * 1.2
        
        commission = int(0.1 * (price1+price2))
        total_price = price1+price2
        total_payment = commission + total_price
        
    
    cursor = conn.cursor();
    query_agent_info= '''SELECT * FROM `Booking_agent` WHERE agent_email = %s'''
    cursor.execute(query_agent_info, (username))
    agent_info = cursor.fetchone()
    
    
    cursor.close()
   
    return render_template('flight_booking_round_a.html', 
                           username=username, 
                           flight_full_id1 = flight_full_id1, flight_full_id2 = flight_full_id2,
                           flights_info1 = flights_info1, flights_info2 = flights_info2, 
                           price1 = price1, price2 = price2,
                           total_price = total_price, commission = commission,total_payment = total_payment,
                           agent_info = agent_info)
                          # first_name = first_name, last_name = last_name)
 
    


@app.route('/booking_complete_a', methods=['GET','POST'])
def booking_complete_a():
    username = session['username']
    #dep_day = session['dep_day']
    if request.method == 'POST':
        
        passenger_email = request.form.get("passenger_email")
        passenger_first_name = request.form.get("passenger_first_name")
        passenger_last_name = request.form.get("passenger_last_name")
        passenger_passport = request.form.get("passport_number")
#        print(username)
#        print(passenger_passport)
        
        cursor = conn.cursor();
        query_passenger_info = '''SELECT * FROM Customer WHERE 
        customer_email = %s AND first_name = %s AND last_name = %s
        AND passport_number = %s'''
        cursor.execute(query_passenger_info, (passenger_email, passenger_first_name,
                                              passenger_last_name,passenger_passport))
        customer_info = cursor.fetchone()     
        cursor.close()
        if customer_info == None:
            error = "There is no such customer in the database or the customer information is wrong."
            return render_template('booking_failed_a.html', 
                           error = error)
            
        
        
        card_type = request.form.get("card_type")  
        card_holder = request.form.get("card_holder") 
        card_number = request.form.get("card_number")
        
        card_expiration = request.form.get("card_expiration")
        card_expiration = datetime.datetime.strptime(card_expiration, "%m/%d/%Y").date()
        
        flight_full_id = request.form.get("flight_full_id")
        airline_id = flight_full_id[:2]
        flight_id = flight_full_id[2:]
        print(airline_id, flight_id)
     
        price = int(float(request.form.get("price")[1:]))
        commission = int(float(request.form.get("commission")[1:]))
    
    
    ticket_id = "E" + str(int(time.time()*10))
    print(ticket_id)
    
    
    cursor = conn.cursor();
    query_flights_info = '''SELECT airline_id, flight_id,  
    a.city as acity, d.city as dcity,
    DATE(departure_time) as dep_day, DATE(arrival_time) as arr_day,
    TIME(departure_time) as dep_time,TIME(arrival_time) as arr_time
    FROM Flight NATURAL JOIN Airline JOIN Airport as a 
    JOIN Airport as d WHERE a.airport_id = arrival_airport 
    AND d.airport_id = departure_airport
    AND airline_id = %s AND flight_id = %s'''
    cursor.execute(query_flights_info, (airline_id, flight_id))
    flights_info = cursor.fetchone()     
    cursor.close()
    
    
    
    cursor = conn.cursor()
    query = 'SELECT * FROM Ticket WHERE customer_email = %s AND airline_id = %s AND flight_id = %s'
    cursor.execute(query, (passenger_email,airline_id, flight_id))
	#stores the results in a variable
    data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
    error = None
    print(data)
    if(data):
		#If the previous query returns data, then user exists
        error = '''The customer has already purchased a ticket for the flight,
                   and the ticket id is %s
                '''%(data["ticket_id"])
        
        return render_template('booking_failed_a.html', error = error)
    else:
        print(ticket_id, airline_id, flight_id, price, username, card_type,
                          card_number, card_holder, card_expiration, username)
        insert = '''INSERT INTO `Ticket` (`ticket_id`, `booking_time`, `airline_id`, `flight_id`, `sold_price`, 
        `credit_or_debit`, `card_number`, `name_on_card`, `expiration_date`,`customer_email`, 
        `agent_email`, `commission`) VALUES (%s, CURRENT_TIMESTAMP(), %s, %s, %s, 
         %s, %s, %s, %s, %s, %s, %s)'''
        cursor.execute(insert, (ticket_id, airline_id, flight_id, price, card_type,
                          card_number, card_holder, card_expiration, passenger_email, username,commission))
        conn.commit()
        cursor.close()
        print("insert complete.")
        
        cursor = conn.cursor()
        query_agent = 'SELECT * FROM Booking_agent WHERE agent_email = %s'
        cursor.execute(query_agent, (username))
        agent_info = cursor.fetchone()
        
        print(len(agent_info))
        
        
        return render_template('booking_complete_a.html', 
                               username=username, flights_info = flights_info,
                               agent_info = agent_info ,
                               customer_info = customer_info, ticket_id = ticket_id)
    
@app.route('/round_booking_complete_a', methods=['GET','POST'])
def round_booking_complete_a():
    username = session['username']
    #dep_day = session['dep_day']
    if request.method == 'POST':
        
        passenger_email = request.form.get("passenger_email")
        passenger_first_name = request.form.get("passenger_first_name")
        passenger_last_name = request.form.get("passenger_last_name")
        passenger_passport = request.form.get("passport_number")
        print(username)
        print(passenger_passport)
        
        cursor = conn.cursor();
        query_passenger_info = '''SELECT * FROM Customer WHERE 
        customer_email = %s AND first_name = %s AND last_name = %s
        AND passport_number = %s'''
        cursor.execute(query_passenger_info, (passenger_email, passenger_first_name,
                                              passenger_last_name,passenger_passport))
        customer_info = cursor.fetchone()     
        cursor.close()
        if customer_info == None:
            error = "There is no such customer in the database or the customer information is wrong."
            return render_template('booking_failed_a.html', 
                           error = error)
            
        
        
        card_type = request.form.get("card_type")  
        card_holder = request.form.get("card_holder") 
        card_number = request.form.get("card_number")
        
        card_expiration = request.form.get("card_expiration")
        card_expiration = datetime.datetime.strptime(card_expiration, "%m/%d/%Y").date()
        
        flight_full_id1 = request.form.get("flight_full_id1")
        airline_id1 = flight_full_id1[:2]
        flight_id1 = flight_full_id1[2:]
        print(airline_id1, flight_id1)
        
        flight_full_id2 = request.form.get("flight_full_id2")
        airline_id2 = flight_full_id2[:2]
        flight_id2 = flight_full_id2[2:]
        print(airline_id2, flight_id2)
     
        price1 = int(float(request.form.get("price1")[1:]))
        price2 = int(float(request.form.get("price2")[1:]))
        
        
        commission1 = int(price1*0.1)
        commission2 = int(price2*0.1)
    
    
    ticket_id1 = "E" + str(int(time.time()*10-randint(0, 9)))
    ticket_id2 = "E" + str(int(time.time()*10-randint(0, 9)))
    print(ticket_id1)
    print(ticket_id2)
    
    
    cursor = conn.cursor();
    query_flights_info1 = '''SELECT airline_id, flight_id,  
    a.city as acity, d.city as dcity,
    DATE(departure_time) as dep_day, DATE(arrival_time) as arr_day,
    TIME(departure_time) as dep_time,TIME(arrival_time) as arr_time
    FROM Flight NATURAL JOIN Airline JOIN Airport as a 
    JOIN Airport as d WHERE a.airport_id = arrival_airport 
    AND d.airport_id = departure_airport
    AND airline_id = %s AND flight_id = %s'''
    cursor.execute(query_flights_info1, (airline_id1, flight_id1))
    flights_info1 = cursor.fetchone()     
    cursor.close()
    
    cursor = conn.cursor();
    query_flights_info2 = '''SELECT airline_id, flight_id,  
    a.city as acity, d.city as dcity,
    DATE(departure_time) as dep_day, DATE(arrival_time) as arr_day,
    TIME(departure_time) as dep_time,TIME(arrival_time) as arr_time
    FROM Flight NATURAL JOIN Airline JOIN Airport as a 
    JOIN Airport as d WHERE a.airport_id = arrival_airport 
    AND d.airport_id = departure_airport
    AND airline_id = %s AND flight_id = %s'''
    cursor.execute(query_flights_info2, (airline_id2, flight_id2))
    flights_info2 = cursor.fetchone()     
    cursor.close()
    
    
    cursor = conn.cursor()
    query1 = 'SELECT * FROM Ticket WHERE customer_email = %s AND airline_id = %s AND flight_id = %s'
    cursor.execute(query1, (passenger_email, airline_id1, flight_id1))
	#stores the results in a variable
    data1 = cursor.fetchone()
    cursor.close()
    
    
    cursor = conn.cursor()
    query2 = 'SELECT * FROM Ticket WHERE customer_email = %s AND airline_id = %s AND flight_id = %s'
    cursor.execute(query2, (passenger_email, airline_id2, flight_id2))
	#stores the results in a variable
    data2 = cursor.fetchone()
    cursor.close()
	
    
    error = None
    
    if(data1):
		#If the previous query returns data, then user exists
        error = '''The customer has already purchased a ticket for the flight %s %s,
                   and the ticket id is %s
                '''%(airline_id1, flight_id1, data1["ticket_id"])
        
        return render_template('booking_failed_a.html', error = error)
    
    elif(data2):
        #If the previous query returns data, then user exists
        error = '''The customer has already purchased a ticket for the flight %s %s,
                   and the ticket id is %s
                '''%(airline_id2, flight_id2, data2["ticket_id"])
        
        return render_template('booking_failed_a.html', error = error)
        
    else:
        cursor = conn.cursor()
        print(ticket_id1, airline_id1, flight_id1, price1, username, card_type,
                          card_number, card_holder, card_expiration, username)
        insert1 = '''INSERT INTO `Ticket` (`ticket_id`, `booking_time`, `airline_id`, `flight_id`, `sold_price`, 
        `credit_or_debit`, `card_number`, `name_on_card`, `expiration_date`,`customer_email`, 
        `agent_email`, `commission`) VALUES (%s, CURRENT_TIMESTAMP(), %s, %s, %s, 
         %s, %s, %s, %s, %s, %s, %s)'''
        cursor.execute(insert1, (ticket_id1, airline_id1, flight_id1, price1, card_type,
                          card_number, card_holder, card_expiration, passenger_email, username,commission1))
        
        print(ticket_id2, airline_id2, flight_id2, price2, username, card_type,
                          card_number, card_holder, card_expiration, username,commission1)
        insert2 = '''INSERT INTO `Ticket` (`ticket_id`, `booking_time`, `airline_id`, `flight_id`, `sold_price`, 
        `credit_or_debit`, `card_number`, `name_on_card`, `expiration_date`,`customer_email`, 
        `agent_email`, `commission`) VALUES (%s, CURRENT_TIMESTAMP(), %s, %s, %s, 
         %s, %s, %s, %s, %s, %s, %s)'''
        cursor.execute(insert2, (ticket_id2, airline_id2, flight_id2, price2, card_type,
                          card_number, card_holder, card_expiration, passenger_email, username,commission2))

        
        conn.commit()
        cursor.close()
        print("insert complete.")
        
        cursor = conn.cursor()
        query_agent = 'SELECT * FROM Booking_agent WHERE agent_email = %s'
        cursor.execute(query_agent, (username))
        agent_info = cursor.fetchone()
        
        print(len(agent_info))
        
        
        return render_template('round_booking_complete_a.html', 
                               username=username, flights_info1 = flights_info1,
                               flights_info2 = flights_info2,
                               agent_info = agent_info ,
                               customer_info = customer_info, ticket_id1 = ticket_id1,
                               ticket_id2 = ticket_id2)
    




@app.route('/customer_spending',  methods=['GET','POST'])
def customer_spending():
    
    
    if request.method == 'POST':
        begin = request.form.get("begin")
        end = request.form.get("end")
        
        begin_date = datetime.datetime.strptime(begin, "%m/%d/%Y")
        end_date = datetime.datetime.strptime(end, "%m/%d/%Y")
        
        begin_month = datetime.datetime.strptime(begin, "%m/%d/%Y").month
        end_month = datetime.datetime.strptime(end, "%m/%d/%Y").month
        
        begin_year = datetime.datetime.strptime(begin, "%m/%d/%Y").year
        end_year = datetime.datetime.strptime(end, "%m/%d/%Y").year
        
        
        
    else:
        range_ = 6
       
        
        end_date = datetime.datetime.now()
        begin_date = datetime.datetime.now().replace(year=end_date.year-1)
        

        
        end_month = datetime.datetime.now().month   
        end_year = datetime.datetime.now().year
        
        begin_month = end_month - (range_-1)
        if begin_month <= 0:
            begin_year = end_year -1
            begin_month = 12 + begin_month
        else:
            begin_year = end_year
              
    
    bar = {}
    if begin_year == end_year:
        
        for month in range(begin_month, end_month+1):
            bar["%s/%s"%(month, begin_year)] = 0
            
        
    elif  begin_year + 1 == end_year:
       
        for month in range(begin_month, 13):
            bar["%s/%s"%(month, begin_year)] = 0
           
        for month in range(1, end_month+1):
            bar["%s/%s"%(month, end_year)] = 0
            
    else:
        for month in range(begin_month, 13):
            bar["%s/%s"%(month, begin_year)] = 0
            #print(bar)  
            
        for year in range(begin_year+1, end_year-1):
            for month in range(1,13):
                bar["%s/%s"%(month, year)] = 0
    
        for month in range(1, end_month+1):
            bar["%s/%s"%(month, end_year)] = 0
        
        
    #print(bar)  
            
        
    username = session['username']
    cursor = conn.cursor()
    query_spending_bar = '''SELECT SUM(sold_price) as flight_spending, SUM(commission) as commission_spending, 
    MONTH(booking_time) as month, YEAR(booking_time) as year FROM `Ticket` 
    WHERE customer_email = %s
    AND booking_time <= %s  AND booking_time >= %s
    GROUP BY year, month'''
    cursor.execute(query_spending_bar, (username, end_date, begin_date))
    
    
    spending_info = cursor.fetchall()
    
    total_spendings = bar.copy()
    spending_on_tickets = bar.copy()
    spending_on_commission = bar.copy()
    for i in range(len(spending_info)):
        year = spending_info[i]["year"]
        month = spending_info[i]["month"]
        
        
        flight_spending = spending_info[i]["flight_spending"]
        commission_spending = spending_info[i]["commission_spending"]
        if commission_spending:
            total_spending = flight_spending + commission_spending
        elif flight_spending:
            total_spending = flight_spending
        else:
            total_spending = 0

        
        
        index = "%s/%s"%(month, year)
       
        
        #print("index is", index)
        
        total_spendings[index] = total_spending
        spending_on_tickets[index] = flight_spending
        spending_on_commission[index] = commission_spending
    
    
        
    max_spending = max(total_spendings.values())
    total_spending_all_range = sum(total_spendings.values())
    
    return render_template('customer_spending.html', 
                           title='Monthly Spending from %s-%s to %s-%s'%(begin_year,
                                                                         begin_month, 
                                                                         end_year,
                                                                         end_month),
                           max=max_spending, 
                           total_spending_all_range = total_spending_all_range,
                           spending_on_tickets = spending_on_tickets,
                           spending_on_commission = spending_on_commission,
                           total_spendings = total_spendings)



@app.route('/view_my_commission',  methods=['GET','POST'])
def view_my_commission():
    
    
    if request.method == 'POST':
        begin = request.form.get("begin")
        end = request.form.get("end")
        
        begin_date = datetime.datetime.strptime(begin, "%m/%d/%Y").date()
        end_date = datetime.datetime.strptime(end, "%m/%d/%Y").date()
        
        
        
    else:
        end_date = datetime.datetime.now().date()
        begin_date = (datetime.datetime.now() + datetime.timedelta(-30)).date()
    
    day_count = (end_date - begin_date).days + 1
    
    
    bar = {}
    
    if day_count <= 31:
        for i in range(day_count):
            index = (begin_date + datetime.timedelta(i))
            bar["%s"%index] = 0
            
    else:
        begin_year = begin_date.year
        begin_month= begin_date.month
        end_year = end_date.year
        end_month = end_date.month
        
        
        
        if begin_year == end_year:
            for month in range(begin_month, end_month+1):
                bar["%s/%s"%(month, begin_year)] = 0
            
        elif  begin_year + 1 == end_year:
        
            for month in range(begin_month, 13):
                bar["%s/%s"%(month, begin_year)] = 0
            
            for month in range(1, end_month+1):
                bar["%s/%s"%(month, end_year)] = 0
            
            
            
        else:
            for month in range(begin_month, 13):
                bar["%s/%s"%(month, begin_year)] = 0
            
            for year in range(begin_year+1, end_year-1):
                for month in range(1,13):
                    bar["%s/%s"%(month, year)] = 0
    
            for month in range(1, end_month+1):
                bar["%s/%s"%(month, end_year)] = 0
        

        
    username = session['username']
    
    cursor = conn.cursor()
    query_daily_bar = '''SELECT (SUM(commission)/COUNT(ticket_id)) as avg_commission, SUM(commission) as total_commission, 
    COUNT(ticket_id) as sold_tickets_num, date(booking_time) as date FROM `Ticket` 
    WHERE agent_email = %s
    AND (booking_time < %s OR booking_time = %s) AND booking_time >= %s
    GROUP BY date(booking_time)'''
    cursor.execute(query_daily_bar, (username, end_date, end_date, begin_date))
    daily_info = cursor.fetchall()
    cursor.close()
    
    
    cursor = conn.cursor()
    query_monthly_bar = '''SELECT (SUM(commission)/COUNT(ticket_id)) as avg_commission, 
    SUM(commission) as total_commission, 
    COUNT(ticket_id) as sold_tickets_num,
    MONTH(booking_time) as month, YEAR(booking_time) as year FROM `Ticket` 
    WHERE agent_email = %s
    AND (booking_time < %s OR booking_time = %s) AND booking_time >= %s
    GROUP BY year, month'''
    cursor.execute(query_monthly_bar, (username, end_date,end_date, begin_date))
    monthly_info = cursor.fetchall()
    cursor.close()
    
    
    cursor = conn.cursor()
    query_total = '''SELECT (SUM(commission)/COUNT(ticket_id)) as avg_commission, SUM(commission) as total_commission, 
    COUNT(ticket_id) as sold_tickets_num FROM `Ticket` 
    WHERE agent_email = %s
    AND (booking_time < %s OR booking_time = %s)  AND booking_time >= %s
    '''
    cursor.execute(query_total, (username, end_date, end_date, begin_date))
    total_info = cursor.fetchone()
    cursor.close()
    
    commission = bar.copy()
    avg_commission = bar.copy()
    sold_tickets = bar.copy()
    
    if day_count <= 31:
        
        for i in range(len(daily_info)):
            date = str(daily_info[i]["date"])
            print(date)
            total_commission = daily_info[i]["total_commission"]
            avg_commission_ = daily_info[i]["avg_commission"]
            sold_tickets_num = daily_info[i]["sold_tickets_num"]
            commission[date] = total_commission
            avg_commission[date] = avg_commission_
            sold_tickets[date] = sold_tickets_num
            print(commission)
            
    else:
        for i in range(len(monthly_info)):
            year = monthly_info[i]["year"]
            month = monthly_info[i]["month"]
            
            total_commission = monthly_info[i]["total_commission"]
            sold_tickets_num = monthly_info[i]["sold_tickets_num"]
            avg_commission_ = monthly_info[i]["avg_commission"]
            
            index = "%s/%s"%(month, year)
            
            commission[index] = total_commission
            avg_commission[index] = avg_commission_
            sold_tickets[index] = sold_tickets_num
            
       
    
        
    max_commission = max(commission.values())
    max_tickets_amount = max(sold_tickets.values())
    
    
    
    return render_template('view_my_commission.html', 
                           title='Commission Summary from %s to %s'%(begin_date,
                                                                         end_date),
                           max_commission=max_commission, 
                           
                           max_tickets_amount = max_tickets_amount,
                           commission = commission,
                           avg_commission = avg_commission,
                           sold_tickets = sold_tickets,
                           total_info = total_info)
	

@app.route('/view_top_customers',  methods=['GET','POST'])
def view_top_customers():
     
    username = session['username']
    
    cursor = conn.cursor()
    query_ticket_bar = '''SELECT COUNT(ticket_id) as sold_tickets_num, customer_email FROM `Ticket` 
    WHERE agent_email = %s AND (CURRENT_DATE - DATE(booking_time) < 6*30 )
    GROUP BY customer_email ORDER BY sold_tickets_num DESC'''
    cursor.execute(query_ticket_bar, (username,))
    ticket_info = cursor.fetchall()
    ticket_info = ticket_info[:5]
    cursor.close()
    
    
    cursor = conn.cursor()
    query_commission_bar = '''SELECT SUM(commission) as total_commission, customer_email FROM `Ticket` 
    WHERE agent_email = %s AND (CURRENT_DATE - DATE(booking_time) < 365 )
    GROUP BY customer_email ORDER BY total_commission DESC'''
    cursor.execute(query_commission_bar, (username, ))
    commission_info = cursor.fetchall()
    commission_info = commission_info[:5]
    cursor.close()

    bar_tickets = {}
    for i in range(len(ticket_info)):
        index = ticket_info[i]["customer_email"]
        value = ticket_info[i]["sold_tickets_num"]
        bar_tickets["%s"%index] = value
        
    bar_commission = {}
    for i in range(len(commission_info)):
        index = commission_info[i]["customer_email"]
        value = commission_info[i]["total_commission"]
        bar_commission["%s"%index] = value
       
        
        
    max_commission = max(bar_commission.values())
    max_tickets_amount = max(bar_tickets.values())
    
    
    
    return render_template('view_top_customers.html', 
                           title='Top Customers',
                           max_commission=max_commission, 
                           
                           max_tickets_amount = max_tickets_amount,
                           bar_tickets = bar_tickets,
                           bar_commission = bar_commission)
    
#####Staff-related Function

@app.route('/addflight', methods=['GET', 'POST'])
def addflight():
    airline_id = session["airline_id"]
    username = session["username"]
    flight_id = request.form['flight_id']
 #cursor used to send queries
    cursor = conn.cursor()
 #executes query
    query = 'SELECT * FROM flight WHERE flight_id = %s'
    cursor.execute(query, (flight_id))
 #stores the results in a variable
    data = cursor.fetchone()   
    if data:
        return render_template('staff_failure.html',error='Flight ID exists!',username=username,airline_id=airline_id)
    departure_airport = request.form['departure_airport']
    arrival_airport = request.form['arrival_airport']
    base_price = request.form['base_price']
    flight_status = "on-time"
    dep_day = request.form['dep_day']
    dep_day = dep_day.split("/")
    dep_time = request.form['dep_time']
    dep_time = dep_time.split(":")
    arr_day = request.form['arr_day']
    arr_day = arr_day.split("/")
    arr_time = request.form['arr_time']
    arr_time = arr_time.split(":")
    departure_time = dep_day[2]+dep_day[0]+dep_day[1]+" "+dep_time[0]+dep_time[1]
    arrival_time = arr_day[2]+arr_day[0]+arr_day[1]+" "+arr_time[0]+arr_time[1]
    airplane_id = request.form['airplane_id']
    ins = "INSERT INTO Flight VALUES(%s,%s,%s,%s,%s,%s,STR_TO_DATE(%s,'%%Y%%m%%d %%H%%i'),STR_TO_DATE(%s,'%%Y%%m%%d %%H%%i'),%s)"
    cursor = conn.cursor()
    cursor.execute(ins, (airline_id,flight_id,departure_airport,arrival_airport,base_price,flight_status,departure_time,arrival_time,airplane_id))
    conn.commit()
    cursor.close()
    session['result'] = 1
    return redirect(url_for('home'))

@app.route('/addplane', methods=['GET', 'POST'])
def addplane():
    username = session["username"]
    airline_id = session["airline_id"]
    airplane_id = request.form['airplane_id']
    cursor = conn.cursor()
 #executes query
    query = 'SELECT * FROM airplane WHERE airplane_id = %s'
    cursor.execute(query, (airplane_id))
 #stores the results in a variable
    data = cursor.fetchone()   
    if data:
        return render_template('staff_failure.html',error='Airplane ID exists!',username=username,airline_id=airline_id)    
    amount_of_seat = request.form['amount_of_seat']
    ins = "INSERT INTO Airplane VALUES(%s,%s,%s)"
    cursor = conn.cursor()
    cursor.execute(ins, (airplane_id,airline_id,amount_of_seat))
    conn.commit()
    cursor.close()
    session['result'] = 1
    return redirect(url_for('home'))
    
@app.route('/addairport', methods=['GET', 'POST'])
def addairport():
    username = session["username"]
    airline_id = session["airline_id"]    
    airport_id = request.form['airport_id']
    cursor = conn.cursor()
 #executes query
    query = 'SELECT * FROM Airport WHERE airport_id = %s'
    cursor.execute(query, (airport_id))
 #stores the results in a variable
    data = cursor.fetchone()   
    if data:
        return render_template('staff_failure.html',error='Airport ID exists!',username=username,airline_id=airline_id)    
    
    airport_name = request.form['airport_name']
    city = request.form['city']
    ins = "INSERT INTO Airport VALUES(%s,%s,%s)"
    cursor = conn.cursor()
    cursor.execute(ins, (airport_id,airport_name,city))
    conn.commit()
    cursor.close()
    session['result'] = 1
    return redirect(url_for('home'))

@app.route('/changestatus', methods=['GET', 'POST'])
def changestatus():
    airline_id = session['airline_id']
    flight_id = request.form['flight_id']
    flight_status = request.form['flight_status']
    upd = "UPDATE Flight SET flight_status = %s WHERE airline_id = %s and flight_id = %s"
    cursor = conn.cursor()
    cursor.execute(upd, (flight_status,airline_id,flight_id))
    conn.commit()
    cursor.close()
    return redirect(url_for('home'))

@app.route('/customer_of_flight', methods=['GET', 'POST'])
def customer_of_flight():
    username = session['username']
    airline_id = session['airline_id']
    flightid = session['flightid']
    flight_id = request.form['flight_id']
    query = "SELECT * from Ticket WHERE airline_id = %s and flight_id = %s"
    cursor = conn.cursor()
    cursor.execute(query, (airline_id,flight_id))
    customer_info = cursor.fetchall()
    cursor.close()
    return render_template('customer_of_flight.html',username=username, customer_info=customer_info,airline_id=airline_id,flight_id=flight_id,flightid=flightid)
@app.route('/flight_of_customer', methods=['GET', 'POST'])
def flight_of_customer():
    username = session['username']
    airline_id = session['airline_id']
    customer_email = request.form['customer_email']
    query = "SELECT * from Ticket WHERE airline_id = %s and customer_email = %s"
    cursor = conn.cursor()
    cursor.execute(query, (airline_id,customer_email))
    flight_info = cursor.fetchall()
    cursor.close()
    return render_template('flight_of_customer.html',username=username, flight_info=flight_info,airline_id=airline_id,customer_email=customer_email)
@app.route('/view_top_des', methods=['GET','POST'])
def view_top_des():
    
    username = session['username']
    airline_id = session['airline_id']
    if request.method == 'POST':
        time_range = request.form['time_range']
        if time_range == '3m':
            query = """SELECT city, arrival_airport, count(arrival_airport) as times 
            FROM ticket natural join Flight join airport 
            on flight.arrival_airport = Airport.airport_id 
            where (departure_time between date_sub(curdate(), interval 3 month) and curdate()) 
            group BY arrival_airport ORDER BY times DESC"""
        elif time_range == '1y':
            query = """SELECT city, arrival_airport, count(arrival_airport) as times 
            FROM ticket natural join Flight join airport 
            on flight.arrival_airport = Airport.airport_id 
            where (departure_time between date_sub(curdate(), interval 1 year) and curdate()) 
            group BY arrival_airport ORDER BY times DESC"""
    else:
        query = """SELECT city, arrival_airport, count(arrival_airport) as times 
        FROM ticket natural join Flight join airport 
        on flight.arrival_airport = Airport.airport_id 
        where (departure_time between date_sub(curdate(), interval 3 month) and curdate()) 
        group BY arrival_airport ORDER BY times DESC"""                
    cursor = conn.cursor()
    cursor.execute(query)
    des = cursor.fetchall()
    if len(des)>= 3:
        des = des[:3]
    cursor.close()    
    return render_template('view_top_des.html',username = username, airline_id = airline_id, des=des)
@app.route('/view_fre_cus', methods=['GET','POST'])
def view_fre_cus():
    
    username = session['username']
    airline_id = session['airline_id']
    query = """SELECT customer_email, count(customer_email) as times 
    FROM ticket   
    where airline_id = %s and (booking_time between date_sub(curdate(), interval 1 year) and curdate()) 
    group BY customer_email ORDER BY times DESC"""               
    cursor = conn.cursor()
    cursor.execute(query,(airline_id))
    cus = cursor.fetchall()
    if len(cus)>= 5:
        cus = cus[:5]
    cursor.close()    
    return render_template('view_fre_cus.html',username = username, airline_id = airline_id, cus=cus)
@app.route('/view_top_agent', methods=['GET','POST'])
def view_top_agent():
    
    username = session['username']
    airline_id = session['airline_id']
    query_lm = """SELECT agent_email, count(agent_email) as n_tickets 
    FROM ticket natural join booking_agent 
    where airline_id = %s and (booking_time between date_sub(curdate(), interval 1 month) and curdate()) 
    group BY agent_email ORDER BY n_tickets DESC"""
    cursor = conn.cursor()
    cursor.execute(query_lm,(airline_id))
    agent_lm = cursor.fetchall()
    cursor.close()
    query_ly = """SELECT agent_email, count(agent_email) as n_tickets 
    FROM ticket natural join booking_agent 
    where airline_id = %s and (booking_time between date_sub(curdate(), interval 1 year) and curdate()) 
    group BY agent_email ORDER BY n_tickets DESC"""
    cursor = conn.cursor()
    cursor.execute(query_ly,(airline_id))
    agent_ly = cursor.fetchall()   
    cursor.close()
    query_ly_c = """SELECT agent_email, sum(commission) as s_com 
    FROM ticket natural join booking_agent  
    where airline_id = %s and (booking_time between date_sub(curdate(), interval 1 year) and curdate()) 
    group BY agent_email ORDER BY s_com DESC"""                
    cursor = conn.cursor()
    cursor.execute(query_ly_c,(airline_id))
    agent_ly_c = cursor.fetchall()   
    cursor.close()
    if len(agent_lm)>= 5:
        agent_lm = agent_lm[:5]
    if len(agent_ly)>= 5:
        agent_ly = agent_ly[:5]
    if len(agent_ly_c)>= 5:
        agent_ly_c = agent_ly_c[:5]
    return render_template('view_top_agent.html',username = username, airline_id = airline_id, agent_lm=agent_lm, agent_ly=agent_ly, agent_ly_c=agent_ly_c)


@app.route('/flight_history_s', methods=['GET','POST'])
def flight_history_s():
    

    
    if request.method == 'POST': 
        order_date = request.form.get("order_date")
        session['fh_forp'] = 1
          
        if order_date:
            if order_date == "PAST":
                session['flight_history_s'] = 'past'
   
            elif order_date == "FUTURE":
                session['flight_history_s'] = 'future'
            
            elif order_date == "ALL":
                session['flight_history_s'] = 'all'
    return redirect(url_for('home'))

@app.route('/flight_history_s_date_range', methods=['GET','POST'])
def flight_history_s_date_range():
    if request.method == 'POST': 
        from_time = request.form["from"]
        to_time = request.form["to"]
        session['fh_dr'] = 1        
          
        if from_time and to_time:
              from_time = from_time.split('/')
              from_time = from_time[2] + from_time[0] + from_time[1]
              to_time = to_time.split('/')
              to_time = to_time[2] + to_time[0] + to_time[1]
              session['from_time'] = from_time
              session['to_time'] = to_time
    return redirect(url_for('home'))
@app.route('/flight_history_s_airport', methods=['GET','POST'])
def flight_history_s_airport():
    if request.method == 'POST': 
        departure_airport = request.form["departure_airport"]
        arrival_airport = request.form["arrival_airport"]
        session['fh_ap'] = 1        
          
        if departure_airport and arrival_airport:
            session['departure_airport']=departure_airport
            session['arrival_airport']=arrival_airport
    return redirect(url_for('home'))

@app.route('/flight_history_s_city', methods=['GET','POST'])
def flight_history_s_city():
    if request.method == 'POST': 
        departure_city = request.form["departure_city"]
        arrival_city = request.form["arrival_city"]
        session['fh_c'] = 1        
          
        if departure_city and arrival_city:
            session['departure_city']=departure_city
            session['arrival_city']=arrival_city
    return redirect(url_for('home'))

@app.route('/report',  methods=['GET','POST'])
def report():
    
    
    if request.method == 'POST':
        begin = request.form.get("begin")
        end = request.form.get("end")
        
        begin_date = datetime.datetime.strptime(begin, "%m/%d/%Y")
        end_date = datetime.datetime.strptime(end, "%m/%d/%Y")
        
        begin_month = datetime.datetime.strptime(begin, "%m/%d/%Y").month
        end_month = datetime.datetime.strptime(end, "%m/%d/%Y").month
        
        begin_year = datetime.datetime.strptime(begin, "%m/%d/%Y").year
        end_year = datetime.datetime.strptime(end, "%m/%d/%Y").year
        
        
        
    else:
        range_ = 6
       
        
        end_date = datetime.datetime.now()
        begin_date = datetime.datetime.now().replace(year=end_date.year-1)
        

        
        end_month = datetime.datetime.now().month   
        end_year = datetime.datetime.now().year
        
        begin_month = end_month - (range_-1)
        if begin_month <= 0:
            begin_year = end_year -1
            begin_month = 12 + begin_month
        else:
            begin_year = end_year
              
    
    bar = {}
    if begin_year == end_year:
        
        for month in range(begin_month, end_month+1):
            bar["%s/%s"%(month, begin_year)] = 0
            
        
    elif  begin_year + 1 == end_year:
       
        for month in range(begin_month, 13):
            bar["%s/%s"%(month, begin_year)] = 0
           
        for month in range(1, end_month+1):
            bar["%s/%s"%(month, end_year)] = 0
            
    else:
        for month in range(begin_month, 13):
            bar["%s/%s"%(month, begin_year)] = 0
            #print(bar)  
            
        for year in range(begin_year+1, end_year-1):
            for month in range(1,13):
                bar["%s/%s"%(month, year)] = 0
    
        for month in range(1, end_month+1):
            bar["%s/%s"%(month, end_year)] = 0
        
        
    #print(bar)  
            
        
    username = session['username']
    airline_id = session['airline_id']
    cursor = conn.cursor()
    query_tickets_bar = '''SELECT Count(ticket_id) as num_tickets, SUM(sold_price) as flight_spending, SUM(commission) as commission_spending, 
    MONTH(booking_time) as month, YEAR(booking_time) as year FROM `Ticket` 
    WHERE airline_id = %s
    AND booking_time <= %s  AND booking_time >= %s
    GROUP BY year, month'''
    cursor.execute(query_tickets_bar, (airline_id, end_date, begin_date))
        
    
    report_info = cursor.fetchall()
    cursor.close()
    
    tickets_solds = bar.copy()

    for i in range(len(report_info)):
        year = report_info[i]["year"]
        month = report_info[i]["month"]
        
        
        tickets_sold = report_info[i]["num_tickets"]


        
        
        index = "%s/%s"%(month, year)
       
        
        #print("index is", index)
        
        tickets_solds[index] = tickets_sold
    
    
        
    max_sold = max(tickets_solds.values())
    tickets_sold_all_range = sum(tickets_solds.values())
    
    cursor = conn.cursor()
    query_pie_ds = '''SELECT SUM(sold_price) as revenue, 
    MONTH(booking_time) as month, YEAR(booking_time) as year FROM `Ticket` 
    WHERE airline_id = %s and commission is null
    AND booking_time <= %s  AND booking_time >= %s
    '''
    cursor.execute(query_pie_ds, (airline_id, end_date, begin_date))
        
    
    ds_info = cursor.fetchone()
    if ds_info:
        print("here", ds_info)
        pie_ds = ds_info['revenue']
    else:
        pie_ds = 0
    
    cursor.close()    
    cursor = conn.cursor()
    query_pie_is = '''SELECT SUM(sold_price) as revenue, 
    MONTH(booking_time) as month, YEAR(booking_time) as year FROM `Ticket` 
    WHERE airline_id = %s and commission is not null
    AND booking_time <= %s  AND booking_time >= %s
    '''
    cursor.execute(query_pie_is, (airline_id, end_date, begin_date))
        
    
    is_info = cursor.fetchone()
    if is_info:
        pie_is = is_info['revenue']
    else:
        pie_is = 0
    print(pie_ds)
    print(pie_is)    
    cursor.close()    
    
    return render_template('report.html', username=username,airline_id=airline_id,
                           title='Monthly Sales from %s-%s to %s-%s'%(begin_year,begin_month,end_year,end_month),
                           max=max_sold, 
                           tickets_sold_all_range = tickets_sold_all_range,
                           tickets_solds = tickets_solds,pie_ds = pie_ds,pie_is=pie_is)


app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = True)
