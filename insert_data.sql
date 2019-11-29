INSERT INTO Airline
VALUES ('UA','United Airlines Inc.'),
 ('AA','American Airlines Inc.'),
 ('US','US Airways Inc.'),
 ('F9','Frontier Airlines Inc.'),
 ('B6','JetBlue Airways'),
 ('OO','Skywest Airlines Inc.'),
 ('AS','Alaska Airlines Inc.'),
 ('NK','Spirit Air Lines'),
 ('WN','Southwest Airlines Co.'),
 ('DL','Delta Air Lines Inc.'),
 ('EV','Atlantic Southeast Airlines'),
 ('HA','Hawaiian Airlines Inc.'),
 ('MQ','American Eagle Airlines Inc.'),
 ('VX','Virgin America'),
 ('MU','China Eastern Airlines'),
 ('UAE', 'Emirates');


INSERT INTO Airport
VALUES ('JFK','John F. Kennedy International Airport', 'New_York'),
 ('PVG','Shanghai Pudong Airport', 'Shanghai'),
 ('LGA','LaGuardia Airport','New_York'),
 ('SHA','Shanghai Hongqiao International Airport','Shanghai');


INSERT INTO Airplane
VALUES ('773','MU', 500),
 ('773','DL', 500),
 ('773','UA', 500),
 ('789','UA',239),
 ('333','MU',284),
 ('333','UAE',284);


INSERT INTO Flight
VALUES
('MU','297', 'PVG','JFK', 5300,"delay", STR_TO_DATE('20190409 1130','%Y%m%d %H%i'), STR_TO_DATE('20190409 0930', '%Y%m%d %H%i'), 773),
('UA','086', 'JFK', 'PVG', 3300,"on-time", STR_TO_DATE('20190409 2030','%Y%m%d %H%i'), STR_TO_DATE('20190410 1030','%Y%m%d %H%i'),773),
('MU','298', 'PVG','JFK', 5300,"on-time", STR_TO_DATE('20190415 1130','%Y%m%d %H%i'), STR_TO_DATE('20190415 0930','%Y%m%d %H%i'),333),
('UA','088', 'JFK', 'PVG', 3300,"on-time", STR_TO_DATE('20190420 2030','%Y%m%d %H%i'), STR_TO_DATE('20190421 1030','%Y%m%d %H%i'),789),
('UA','010', 'PVG', 'JFK', 3300,"on-time", STR_TO_DATE('20190515 2030','%Y%m%d %H%i'), STR_TO_DATE('20190515 1030','%Y%m%d %H%i'),789)
;

INSERT INTO Flight
VALUES
('MU','299', 'PVG','JFK', 5300,"delay", STR_TO_DATE('20190509 1130','%Y%m%d %H%i'), STR_TO_DATE('20190509 0930', '%Y%m%d %H%i'),773),
('UA','080', 'JFK', 'PVG', 3300,"on-time", STR_TO_DATE('20190509 2030','%Y%m%d %H%i'), STR_TO_DATE('20190510 1030','%Y%m%d %H%i'),773),
('MU','290', 'PVG','JFK', 5300,"on-time", STR_TO_DATE('20190515 1130','%Y%m%d %H%i'), STR_TO_DATE('20190515 0930','%Y%m%d %H%i'),333),
('UA','083', 'JFK', 'PVG', 3300,"on-time", STR_TO_DATE('20190520 2030','%Y%m%d %H%i'), STR_TO_DATE('20190521 1030','%Y%m%d %H%i'),789)
;


INSERT INTO Airline_staff
VALUES ('MU', 'Azura',  MD5('lalala'), 'Xiaohan','Yang', '1997-01-11');


INSERT INTO Airline_staff_phonenumber
VALUES ('MU', 'Azura', '15882044939'),
       ('MU', 'Azura', '15882044910');


INSERT INTO `Customer` (`customer_email`, `username`, `user_password`, `first_name`,`last_name`,
`building_number`, `street`, `city`, `state`, `phone_number`, `passport_number`, `passport_expiration`, `passport_country`, `date_of_birth`) 
VALUES ('qh123@nyu.edu', 'Qixiao He',  MD5('4343123'), 'Qixiao', 'He', '1111', 'Jingqiao Road', 'Shanghai', 'Shanghai', '13708491111', 'E12344311', '2022-01-10', 'China', '1998-12-11');

INSERT INTO `Customer` (`customer_email`, `username`, `user_password`, `first_name`, `last_name`,  `building_number`, `street`, `city`, `state`, `phone_number`, `passport_number`, `passport_expiration`, `passport_country`, `date_of_birth`) 
VALUES ('qq33@nyu.edu', 'Buren Shi',  MD5('78abc123'), 'Buren','Shi','A203', 'Pusan Road', 'Chengdu', 'Sichuan', '18808391111', 'E12743777', '2020-05-08', 'China', '1991-05-21');

INSERT INTO `Booking_agent` (`agent_email`, `agent_password`, `booking_agent_ID`) 
VALUES ('778899@agent.com',  MD5('abcdabcd'), 'agent778899');

INSERT INTO `Ticket` (`ticket_id`, `booking_time`, `airline_id`, `flight_id`, `sold_price`, `credit_or_debit`, `card_number`, `name_on_card`, `expiration_date`,`customer_email`, `agent_email`, `commission`) 
VALUES ('E19856819599', '2019-04-20 17:03:04', 'MU', '297', '5300', 'credit', '4312123456712345', 'Qixiao He', '2020-09-09','qh123@nyu.edu', '778899@agent.com', '530');

INSERT INTO `Ticket` (`ticket_id`, `booking_time`,`airline_id`, `flight_id`, `sold_price`, `credit_or_debit`, `card_number`, `name_on_card`, `expiration_date`, `customer_email`, `agent_email`, `commission`) 
VALUES ('E19856819600', '2019-04-19 17:03:04', 'UA', '086', '3300', 'debit', '4316783478719045', 'Buren Shi', '2019-12-09', 'qq33@nyu.edu', NULL, NULL);

