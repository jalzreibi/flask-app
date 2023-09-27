import mysql.connector
import os
from mysql.connector import Error
from flask import Flask

seasons = [ 'AUTUMN' , 'WINTER', 'SPRING', 'SUMMER' ]

DB_HOST=os.environ.get('DB_HOST')
DB_NAME=os.environ.get('DB_NAME')
DB_USER=os.environ.get('DB_USER')
DB_PASSWORD=os.environ.get('DB_PASSWORD')


isStatTableCreated=False


def getMYSQLConnection() :
    if (DB_HOST is None):
        print("DB_HOST is not defined")
        exit(1)
    if (DB_NAME is None):
        print("DB_NAME is not defined")
        exit(1)        
    if (DB_USER is None):
        print("DB_USER is not defined")
        exit(1)        
    if (DB_PASSWORD is None):
        print("DB_PASSWORD is not defined")
        exit(1)        

    try:
        connection = mysql.connector.connect(host=DB_HOST,
                                             database=DB_NAME,
                                             user=DB_USER,
                                             password=DB_PASSWORD)
        if connection.is_connected():
            db_Info = connection.get_server_info()
            print("Connected to MySQL Server version ", db_Info)
            cursor = connection.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            print("You're connected to database: ", record)
            cursor.close()
            if (not isStatTableCreated):
               createStatTableIfNotCreated(connection)
            return connection;
    except Error as e:
        print("Error while connecting to MySQL", e)


def createStatTableIfNotCreated(connection):
    try:
        if connection.is_connected():
           cursor = connection.cursor(buffered=True)
           cursor.execute("""create table IF NOT EXISTS seasons_stats (
season varchar(255),
stat int);""")
           connection.commit()
           for season in seasons:
               stmt = "select stat from seasons_stats where season=%s"
               print (stmt,season)
               cursor.execute(stmt,(season,))
               result = cursor.fetchall()
               if result is not None and len(result)==0:
                    stmt = "insert into seasons_stats values (%s,%s)"
                    data = (season,'0')
                    cursor.execute(stmt,data)
                    connection.commit()
               else:
                    print(result)
               isStatTableCreated=True
    except Error as e:
        print("Error while connecting to MySQL", e)


# main
app = Flask(__name__)


@app.route("/")
def hello():
    return "hello"
@app.route("/getall", methods=['GET'])
def getAll():
    try:
        connection = getMYSQLConnection()
        if connection.is_connected():
            cursor = connection.cursor(buffered=True)
            stmt = "select * from seasons_stats"
            cursor.execute(stmt)
            result = cursor.fetchall()
            cursor.close()
            return result
    except Error as e:
        print("Error while connecting to MySQL", e)

@app.route("/get/<season>", methods=['GET'])
def get(season):
  if season.upper() in seasons:
          try:
            connection = getMYSQLConnection()
            if connection.is_connected():
                cursor = connection.cursor(buffered=True)
                stmt = "select stat from seasons_stats where season=%s"
                cursor.execute(stmt,(season.upper(),))
                result = cursor.fetchall()
                cursor.close()
                return result
          except Error as e:
            print("Error while connecting to MySQL", e)
  else:
      return "ERROR: " + season + " is not a valid season\n"

@app.route("/vote/<season>",methods=['POST','PUT'])
def vote(season):
  if season.upper() in seasons:
          try:
            connection = getMYSQLConnection()
            if connection.is_connected():
                cursor = connection.cursor(buffered=True)
                stmt = "update seasons_stats set stat=stat+1 where season=%s"
                cursor.execute(stmt,(season.upper(),))
                connection.commit()
                cursor.close()
                return "OK"
          except Error as e:
            print("Error while connecting to MySQL", e)
  else:
      return "ERROR: " + season + " is not a valid season\n"
