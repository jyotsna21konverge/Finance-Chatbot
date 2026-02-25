import logging
import psycopg2
import boto3
import requests

# Initialize the logger
logger = logging.getLogger("Backend-Service")


class DataConnector:
    """
    A class to establish connections with various data sources such as CouchDB, PostgreSQL, S3, and SharePoint.
    """

    def __init__(self) -> None:
        """
        Initializes a DataConnector object.
        """
        pass

    def connect_postgres(self, host: str, port: int, user: str, password: str, db_name: str):
        """
        Connects to a PostgreSQL database.

        Args:
            host (str): PostgreSQL host address.
            port (int): PostgreSQL port number.
            user (str): Username for PostgreSQL authentication.
            password (str): Password for PostgreSQL authentication.
            db_name (str): Name of the PostgreSQL database to connect to.

        Returns:
            psycopg2.extensions.connection: The PostgreSQL connection object, or None if connection fails.
        """
        conn = None
        try:
            # Establish a connection to the PostgreSQL database
            conn = psycopg2.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                dbname=db_name
            )
        except psycopg2.Error as e:
            logger.error(f"Error connecting to PostgreSQL database: {e}")
        
        return conn

    def connect_s3(self, creds_dict):
        """
        Connects to AWS S3 using provided credentials.

        Args:
            creds_dict (dict): A dictionary containing 'access_key' and 'secret_key'.

        Returns:
            boto3.Client: The S3 client object, or None if connection fails.
        """
        s3_client = None

        try:
            # Extract AWS access and secret keys from credentials
            AWS_ACCESS_KEY_ID = creds_dict.get("access_key")
            AWS_SECRET_ACCESS_KEY = creds_dict.get("secret_key")

            # Validate credentials
            if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
                raise ValueError("Access key or secret key is missing in the credentials.")

            # Initialize a session with AWS
            session = boto3.Session(
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY
            )
            s3_client = session.client('s3')

        except Exception as e:
            logger.error(f"Error connecting to S3: {str(e)}")
        
        return s3_client