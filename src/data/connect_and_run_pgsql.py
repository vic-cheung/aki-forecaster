import pandas as pd
import psycopg2
import time


def connect_database():
    """Connects to mimic3 Database.

    Args:
        None
    Returns:
        psycopg2 connection object
    """
    connection = psycopg2.connect(
        user="postgres",
        password="postgres",
        host="127.0.0.1",
        port="5432",
        database="mimic",
    )
    return connection


def run_query(query: str) -> pd.DataFrame:
    """Creates new connection, runs query, closes connection.

    Args:
        query: query string
    Returns:
        query result in pandas dataframe using pd.read_sql_query
    """
    start = time.time()
    connection = connect_database()
    data = pd.read_sql_query(query, connection)
    connection.close()
    print(f"Took: {time.time() - start} seconds")
    return data
