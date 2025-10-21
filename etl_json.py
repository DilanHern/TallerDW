## ETL para traer las ventas del json
## pip install pandas pyodbc python-dotenv

import json
import pandas as pd
from dotenv import load_dotenv
import os
import platform
load_dotenv()
import pyodbc
from datetime import datetime
import locale


try:
    locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")
except locale.Error:
    try:
        locale.setlocale(locale.LC_TIME, "es_ES")
    except locale.Error:
        pass


server = os.getenv("serverenv")
database = os.getenv("databaseenv")
username = os.getenv("usernameenv")
password = os.getenv("passwordenv")

# detectar driver pq mac usa 18 y windows 17
if platform.system() == "Windows":
    driver = "ODBC Driver 17 for SQL Server"
else:
    driver = "ODBC Driver 18 for SQL Server"

connectionsql = pyodbc.connect(
    f'DRIVER={{{driver}}};'
    f'SERVER={server};'
    f'DATABASE={database};'
    f'UID={username};'
    f'PWD={password};'
    'TrustServerCertificate=yes;'
)
cursor = connectionsql.cursor()

def obtener_id_fecha(año, mes, dia=1):
    """Obtiene el id_fecha de la tabla DIM_TIEMPO"""
    cursor.execute("""
        SELECT id_fecha FROM DIM_TIEMPO 
        WHERE año = ? AND mes = ? AND dia = ?
    """, (año, mes, dia))
    resultado = cursor.fetchone()
    return resultado[0] if resultado else None

def obtener_tipo_cambio(año, mes, dia=1):
    """Obtiene el tipo de cambio de la tabla DIM_TIEMPO"""
    cursor.execute("""
        SELECT tipoCambio FROM DIM_TIEMPO 
        WHERE año = ? AND mes = ? AND dia = ?
    """, (año, mes, dia))
    resultado = cursor.fetchone()
    return resultado[0] if resultado else None

def obtener_o_crear_item(nombre_item):
    """Obtiene el id del item o lo crea si no existe"""
    cursor.execute("SELECT id_item FROM DIM_ITEM WHERE nombre = ?", (nombre_item,))
    resultado = cursor.fetchone()
    
    if resultado:
        return resultado[0]
    else:
        cursor.execute("""
            INSERT INTO DIM_ITEM (nombre, marca) 
            VALUES (?, ?)
        """, (nombre_item, "panameño"))
        
        cursor.execute("SELECT @@IDENTITY")
        nuevo_id = cursor.fetchone()[0]
        return nuevo_id

def obtener_o_crear_cliente():
    """Obtiene el id del cliente panameño o lo crea si no existe"""
    nombre_cliente = "Cliente panameño"
    
    cursor.execute("SELECT id_cliente FROM DIM_CLIENTE WHERE nombre = ?", (nombre_cliente,))
    resultado = cursor.fetchone()
    
    if resultado:
        return resultado[0]
    else:
        cursor.execute("""
            INSERT INTO DIM_CLIENTE (nombre, pais, zona) 
            VALUES (?, ?, ?)
        """, (nombre_cliente, "panama", "america"))
        
        cursor.execute("SELECT @@IDENTITY")
        nuevo_id = cursor.fetchone()[0]
        return nuevo_id

def procesar_ventas_json(archivo_json):
    """Procesa el archivo JSON de ventas e inserta en FACT_VENTAS"""
    
    
    with open(archivo_json, 'r', encoding='utf-8') as file:
        datos_ventas = json.load(file)
    
    
    id_cliente = obtener_o_crear_cliente()
    print(f"ID Cliente panameño: {id_cliente}")
    
    contador_registros = 0
    
    
    for registro in datos_ventas:
        año = registro['anio']
        mes = registro['mes']
        
        print(f"\nProcesando ventas de {mes}/{año}")
        
        
        id_fecha = obtener_id_fecha(año, mes, 1)
        tipo_cambio = obtener_tipo_cambio(año, mes, 1)
        
        if not id_fecha or not tipo_cambio:
            print(f"No se encontró fecha {año}-{mes:02d}-01 en DIM_TIEMPO")
            continue
        
        print(f"  ID Fecha: {id_fecha}, Tipo Cambio: {tipo_cambio}")
        
        
        for venta in registro['ventas']:
            item_nombre = venta['item']
            cantidad = venta['cantidad']
            precio_usd = venta['precio']
            
           
            total_ventas = float(precio_usd) * float(tipo_cambio)
            
            
            id_item = obtener_o_crear_item(item_nombre)
            
           
            try:
                cursor.execute("""
                    INSERT INTO FACT_VENTAS (quantity, total_ventas, id_fecha, id_cliente, id_item)
                    VALUES (?, ?, ?, ?, ?)
                """, (cantidad, total_ventas, id_fecha, id_cliente, id_item))
                
                contador_registros += 1
                
                if contador_registros % 50 == 0:
                    print(f"Procesados {contador_registros} registros.")
                
            except Exception as e:
                print(f"Error insertando {item_nombre}: {e}")
        
        
        connectionsql.commit()
    
    print(f"\n Total de registros procesados: {contador_registros}")

if __name__ == "__main__":
    print("ETL de ventas JSON")
    
    try:
        procesar_ventas_json("ventas_resumen_2024_2025.json")
        print("ETL finalizado exitosamente!")
        
    except Exception as e:
        print(f"Error en el ETL: {e}")
        
    finally:
        cursor.close()
        connectionsql.close()
        print("Conexión a base de datos cerrada")
