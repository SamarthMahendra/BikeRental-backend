user_create_sql = """
CREATE TABLE IF NOT EXISTS User (
    UserID INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    password VARCHAR(100) NOT NULL,
    token VARCHAR(512) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
"""

bike_card_create_sql = """
CREATE TABLE BikeCard (
    CardID INT AUTO_INCREMENT PRIMARY KEY,
    Balance DECIMAL(10,2),
    UserID INT,
    FOREIGN KEY (UserID) REFERENCES User(UserID)
);
"""

bike_create_sql = """
CREATE TABLE Bike (
    BikeID INT AUTO_INCREMENT PRIMARY KEY,
    Status VARCHAR(100),
    Location_lat DECIMAL(10,6),
    Location_lon DECIMAL(10,6),
    InUse BOOLEAN,
    StationID INT,
    FOREIGN KEY (StationID) REFERENCES Stations(StationID)
);
"""

classic_create_sql = """
CREATE TABLE Classic (
    BikeID INT PRIMARY KEY,
    FOREIGN KEY (BikeID) REFERENCES Bike(BikeID)
);
"""

ebike_create_sql = """
CREATE TABLE Ebike (
    BikeID INT,
    Bike_range INT,
    FOREIGN KEY (BikeID) REFERENCES Bike(BikeID),
    UNIQUE(BikeID, Bike_range)
);
"""

rate_create_sql = """
CREATE TABLE Rate (
    RateID INT PRIMARY KEY,
    Price DECIMAL(10,2)
);
"""

transaction_create_sql = """
CREATE TABLE Transaction (
    TransactionID INT PRIMARY KEY,
    StartTime DATETIME,
    EndTime DATETIME,
    Cost DECIMAL(10,2),
    BikeID INT,
    FOREIGN KEY (BikeID) REFERENCES Bike(BikeID)
);
"""

maintenance_record_create_sql = """
CREATE TABLE MaintenanceRecord (
    RecordID INT PRIMARY KEY,
    DateOfMaintenance DATE,
    Details VARCHAR(255),
    BikeID INT,
    FOREIGN KEY (BikeID) REFERENCES Bike(BikeID),
    CONSTRAINT AK_MaintenanceRecord UNIQUE (Details)
);
"""

booking_schedule_create_sql = """
CREATE TABLE BookingSchedule (
    ScheduleID INT PRIMARY KEY,
    StartDate DATETIME,
    EndDate DATETIME,
    UserID INT,
    BikeID INT,
    FOREIGN KEY (UserID) REFERENCES User(UserID),
    FOREIGN KEY (BikeID) REFERENCES Bike(BikeID)
);
"""

feedback_create_sql = """
CREATE TABLE Feedback (
    FeedbackID INT PRIMARY KEY,
    Rating INT,
    Comments VARCHAR(1024),
    UserID INT,
    BikeID INT,
    FOREIGN KEY (UserID) REFERENCES User(UserID),
    FOREIGN KEY (BikeID) REFERENCES Bike(BikeID),
    CONSTRAINT AK_Feedback UNIQUE (Comments)
);
"""

payment_history_create_sql = """
CREATE TABLE PaymentHistory (
    PaymentID INT PRIMARY KEY,
    Amount DECIMAL(10,2),
    PaymentDate DATETIME,
    UserID INT,
    FOREIGN KEY (UserID) REFERENCES User(UserID)
);
"""

location_history_create_sql = """
CREATE TABLE LocationHistory (
    HistoryID INT PRIMARY KEY,
    Latitude DECIMAL(10,6),
    Longitude DECIMAL(10,6),
    Timestamp DATETIME,
    BikeID INT,
    FOREIGN KEY (BikeID) REFERENCES Bike(BikeID)
);
"""

stations_create_sql = """
CREATE TABLE Stations (
    StationID INT PRIMARY KEY,
    Location_lat DECIMAL(10,6),
    Location_lon DECIMAL(10,6),
    Capacity INT
);
"""
