class DatabaseWrapper:
    def __init__(self, connection):
        """
        Wrap the database connection to provide a consistent interface.
        """
        self.connection = connection

    def ping(self, reconnect=True):
        """
        Ensure the connection is alive, optionally reconnect if needed.
        """
        print(self.connection)
        self.connection.ping(reconnect=reconnect)

    def cursor(self, dictionary=True):
        """
        Return a new cursor from the connection.
        """
        return self.connection.cursor(dictionary=dictionary)

    def commit(self):
        """
        Commit the current transaction.
        """
        self.connection.commit()

    def rollback(self):
        """
        Rollback the current transaction.
        """
        self.connection.rollback()


