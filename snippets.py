import logging
import sys
import argparse
import psycopg2

#Set the log output file, and the log level
logging.basicConfig(filename = "snippets.log", level = logging.DEBUG)
logging.debug("Connecting to PostgreSQL")
connection = psycopg2.connect("dbname='snippets' user='action' host='localhost'")
logging.debug("Database connection established.")

def put(hide, name, snippet):
    """Store a snippet with an associated name."""
    logging.info("Storing snippet {!r}: {!r}".format(name, snippet))
    with connection, connection.cursor() as cursor:
        try:
            command = "insert into snippets values (%s, %s)"
            cursor.execute(command, (name, snippet))
            if hide == 1:
                command = "update snippets set hidden = true where keyword = %s"
                cursor.execute(command, (name,))
                
        except psycopg2.IntegrityError as e:
            connection.rollback()
            command = "update snippets set message=%s where keyword=%s"
            cursor.execute(command, (snippet, name))
    logging.debug("Snippet stored successfully.")
    return name, snippet

def get(name):
    """Retrieve the snippet with a given name.
    If there is no such snippet...
    Returns the snippet.
    """
    logging.info("Retrieve the snippet with a given name {!r}".format(name))
    #cursor = connection.cursor()
    #command = "select message from snippets where keyword=%s"
    #cursor.execute(command,( name,))
    #message = cursor.fetchone()
    #connection.commit()
    with connection, connection.cursor() as cursor:
        cursor.execute("select message from snippets where keyword=%s", (name,))
        message = cursor.fetchone()
    logging.debug("Snippet retrieved successfully.")
    return message

def catalog():
    logging.info("query the keywords from the snippets table")
    with connection, connection.cursor() as cursor:
        command = "select * from snippets where hidden is false order by keyword"
        cursor.execute(command)
        rows = cursor.fetchall()
        for row in rows:
            print row[0]
                    

def search(searchString):
    logging.info("search for a string within the snippet messages")
    with connection, connection.cursor() as cursor:
        command = "select * from snippets where message like %s and not hidden"
        cursor.execute(command, ('%'+searchString+'%',))
        rows = cursor.fetchall()
    searchedRows = []
    for row in rows:
        searchedRows.append(row[1])
    return searchedRows

def main():
    logging.info("Construting parser")
    parser = argparse.ArgumentParser(description="Store and retrieve snippets of the text")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    #Subparser for the put command
    logging.debug("Constructing put subparser")
    put_parser = subparsers.add_parser("put", help="Store a snippet")
    put_parser.add_argument("name", help="The name of the snippet")
    put_parser.add_argument("snippet", help="The snippet text")    
    put_parser.add_argument("--hide", type=int, choices=[0, 1], help="not show snippets in the catalog") 
    #Subparser for the get command
    logging.debug("Constructing get subparser")
    get_parser = subparsers.add_parser("get", help="Retrieve a snippet")
    get_parser.add_argument("name", help="The name of the snippet")
    
    #Subparser for the catalog command
    logging.debug("Constructing catalog subparser")
    catalog_parser = subparsers.add_parser("catalog", help="look up keywords")
     #Subparser for the search command
    logging.debug("Constructing search subparser")
    search_parser = subparsers.add_parser("search", help="search for a string within the snippet messages")
    search_parser.add_argument("searchString", help="The string used to search withing messages")
 
    arguments = parser.parse_args()
    #Convert parsed arguments from Namespace to dictionary
    arguments = vars(arguments)
    command = arguments.pop("command")

    if command == "put":
        name, snippet = put(**arguments)
        print ("Stored {!r} as {!r}".format(snippet, name))
    elif command == "get":
        snippet = get(**arguments)
        print ("Retrived snipped: {!r}".format(snippet))
    elif command == "catalog":
        catalog()
        print ("The keywords stored in snippet")
    elif command == "search":
        searchM = search(**arguments)
        print ("The messages containing the string are {}".format(searchM))  

if __name__=="__main__":
    main()
