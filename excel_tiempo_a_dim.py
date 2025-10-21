## py -m pip install pandas openpyxl
## py -m pip install pyodbc
import pandas as pd
from dotenv import load_dotenv
import os
load_dotenv()
import pyodbc
from datetime import datetime
import locale
locale.setlocale(locale.LC_TIME, "es_ES.utf8")
import pyodbc
server = os.getenv("serverenv")
database = os.getenv("databaseenv")
username = os.getenv("usernameenv")
password = os.getenv("passwordenv")


connectionsql = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    f'SERVER={server};'
    f'DATABASE={database};'
    f'UID={username};'
    f'PWD={password};'
    'TrustServerCertificate=yes;'
)
cursor = connectionsql.cursor()

def parseador(excel):
    for i in range((len(excel))):
        columnaFecha = excel.loc[i, 'Fecha']
        columnaCambio = excel.loc[i, 'TipoCambio_USD_CRC']

        fecha = columnaFecha
        year = fecha.year
        month = fecha.month
        day = fecha.day
        fecha_sola = fecha.date()
        semana = fecha.isocalendar().week
        dia_semana = fecha.strftime("%A")

        print(columnaCambio, fecha_sola, dia_semana)  

        cursor.execute("""
            INSERT INTO DIM_TIEMPO (año, mes, dia, fecha, semana, diaSemana, tipoCambio)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            year,
            month,
            day,
            fecha_sola,
            semana,
            dia_semana,
            columnaCambio
        ))

    connectionsql.commit() 

tiposDeCambioExcel = pd.read_excel("TiposCambio_USD_CRC_2024_2025.xlsx")
parseador(tiposDeCambioExcel)
cursor.close()
connectionsql.close()
