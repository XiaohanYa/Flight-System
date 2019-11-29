CREATE DATABASE final;

CREATE TABLE IF NOT EXISTS Airport (
    airport_id VARCHAR(5) NOT NULL,
    airport_name VARCHAR(255) NOT NULL,
    city VARCHAR(255) NOT NULL,
    PRIMARY KEY (airport_id)
);

CREATE TABLE IF NOT EXISTS Airline (
    airline_id VARCHAR(3) NOT NULL,
    airline_name VARCHAR(255) NOT NULL,
    PRIMARY KEY (airline_id)
);

CREATE TABLE IF NOT EXISTS Airplane (
    airplane_id VARCHAR(10) NOT NULL,
    airline_id VARCHAR(3) NOT NULL,
    amount_of_seat Int NOT NULL,
    PRIMARY KEY (airline_id, airplane_id),
    FOREIGN KEY (airline_id)
     REFERENCES Airline(airline_id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Airline_staff (
    airline_id VARCHAR(3) NOT NULL,
    username VARCHAR(10) NOT NULL,
    user_password CHAR(32) NOT NULL,
    first_name VARCHAR(30) NOT NULL,
    last_name VARCHAR(30) NOT NULL,
    date_of_birth VARCHAR(11) NOT NULL,
    PRIMARY KEY (airline_id,username),
    FOREIGN KEY (airline_id)
     REFERENCES Airline(airline_id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Airline_staff_phonenumber (
    airline_id VARCHAR(3) NOT NULL,
    username VARCHAR(10) NOT NULL,  
    phone_number VARCHAR(11) NOT NULL,
    FOREIGN KEY (airline_id,username) REFERENCES Airline_staff(airline_id,username) ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS Flight (
    airline_id VARCHAR(3) NOT NULL,
    flight_id VARCHAR(5) NOT NULL,
    departure_airport VARCHAR(5) NOT NULL,
    arrival_airport  VARCHAR(5) NOT NULL,
    base_price int NOT NULL,
    flight_status VARCHAR(10) NOT NULL,
    departure_time TIMESTAMP NOT NULL,
    arrival_time TIMESTAMP NOT NULL,
    airplane_id VARCHAR(10) NOT NULL,            

    PRIMARY KEY (airline_id,flight_id),
    FOREIGN KEY (airline_id) REFERENCES Airline(airline_id) ON DELETE CASCADE,
    FOREIGN KEY (airline_id, airplane_id) REFERENCES Airplane(airline_id, airplane_id) ON DELETE CASCADE,
    FOREIGN KEY (departure_airport) REFERENCES Airport(airport_id) ON DELETE CASCADE,
    FOREIGN KEY (arrival_airport) REFERENCES Airport(airport_id) ON DELETE CASCADE
    );

CREATE TABLE IF NOT EXISTS Booking_agent (
    agent_email VARCHAR(30) NOT NULL,
    agent_password VARCHAR(32) NOT NULL,
    booking_agent_ID VARCHAR(12) NOT NULL,
    PRIMARY KEY (agent_email)
);


CREATE TABLE IF NOT EXISTS Customer (
    customer_email VARCHAR(30) NOT NULL,
    username VARCHAR(20) NOT NULL,
    user_password VARCHAR(32) NOT NULL,
    first_name VARCHAR(30) NOT NULL,
    last_name VARCHAR(30) NOT NULL,
    building_number VARCHAR(5) NOT NULL,   
    street VARCHAR(15) NOT NULL,
    city VARCHAR(15) NOT NULL,
    state VARCHAR(15) NOT NULL,
    phone_number VARCHAR(15) NOT NULL,
    passport_number VARCHAR(15) NOT NULL,
    passport_expiration VARCHAR(10) NOT NULL,
    passport_country VARCHAR(20) NOT NULL,
    date_of_birth VARCHAR(10) NOT NULL,
    PRIMARY KEY (customer_email)
);



CREATE TABLE IF NOT EXISTS Ticket (
    ticket_id VARCHAR(18) NOT NULL,
    booking_time TIMESTAMP NOT NULL,
    airline_id VARCHAR(5) NOT NULL,
    flight_id VARCHAR(5) NOT NULL,
    sold_price int NOT NULL,
    credit_or_debit VARCHAR(6) NOT NULL,
    card_number VARCHAR(16) NOT NULL,
    name_on_card VARCHAR(20) NOT NULL,
    expiration_date VARCHAR(10) NOT NULL,
    customer_email VARCHAR(30) NOT NULL,
    agent_email VARCHAR(30), 
    commission int,

    PRIMARY KEY (ticket_id),
    FOREIGN KEY (airline_id, flight_id) REFERENCES Flight(airline_id, flight_id) ON DELETE CASCADE, 
    FOREIGN KEY (customer_email) REFERENCES Customer(customer_email) ON DELETE CASCADE,   
    FOREIGN KEY (agent_email) REFERENCES Booking_agent(agent_email) ON DELETE CASCADE   
 );


