

def create_tables():
    """
    This function is used to create the tables
    """
    sql_commands ="""
    CREATE TABLE IF NOT EXISTS User (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    password VARCHAR(100) NOT NULL,
    token VARCHAR(512) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    );
    """
    from .sqlconnector import MySQLConnector
    # create a connection
    conn = MySQLConnector()
    connection = conn.get_connection()
    cursor = connection.cursor()
    # execute the query
    cursor.execute(sql_commands)
    # commit the connection
    connection.commit()
    # close the connection
    conn.close_connection()
    return True
