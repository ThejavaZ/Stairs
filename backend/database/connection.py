import psycopg2 as ps

def query(query:str):
    try:
        connection = ps.connect(
            dbname = "",
            user = "",
            password = "",
            host = "",
            port = "",
        )

        cursor = connection.cursor()
        cursor.execute(query)

        if query.strip().lower().startswith("select"):
            result = cursor.fetchall()
            return result

        connection.commit()
        
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Connection closed")
