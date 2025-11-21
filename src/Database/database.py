import mysql.connector
from mysql.connector import Error

class DB:
    def __init__(self):
        self.config = {
            "host": "127.0.0.1",
            "port": 3307,            
            "user": "root", 
            "password": "root", 
            "database": "hipoaposta"
        }

    def get_connection(self):
        return mysql.connector.connect(**self.config)

    def fetch_clients(self, filtro_nom=""):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            sql = "SELECT id, dni_nie, nom, cognoms, email, telefon, saldo_actual, tipus_client, estat FROM clients"
            if filtro_nom:
                sql += " WHERE nom LIKE %s OR cognoms LIKE %s"
                params = (f"%{filtro_nom}%", f"%{filtro_nom}%")
                cursor.execute(sql, params)
            else:
                sql += " ORDER BY id DESC"
                cursor.execute(sql)
            return cursor.fetchall()
        except Error as e:
            print(f"Error SQL fetch: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    def insert_client(self, dni, nom, cognoms, email, telefon, tipus, estat):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            sql = """INSERT INTO clients 
                     (dni_nie, nom, cognoms, email, telefon, tipus_client, estat, data_registre, saldo_actual) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s, CURDATE(), 0)"""
            vals = (dni, nom, cognoms, email, telefon, tipus, estat)
            cursor.execute(sql, vals)
            conn.commit()
            return True, "Client creat correctament"
        except Error as e:
            return False, str(e)
        finally:
            cursor.close()
            conn.close()

    def update_client(self, client_id, dni, nom, cognoms, email, telefon, tipus, estat):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            sql = """UPDATE clients SET 
                     dni_nie=%s, nom=%s, cognoms=%s, email=%s, telefon=%s, tipus_client=%s, estat=%s
                     WHERE id=%s"""
            vals = (dni, nom, cognoms, email, telefon, tipus, estat, client_id)
            cursor.execute(sql, vals)
            conn.commit()
            return True, "Client actualitzat correctament"
        except Error as e:
            return False, str(e)
        finally:
            cursor.close()
            conn.close()

    def delete_client(self, client_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM clients WHERE id = %s", (client_id,))
            conn.commit()
            return True, "Client eliminat"
        except Error as e:
            return False, str(e)
        finally:
            cursor.close()
            conn.close()