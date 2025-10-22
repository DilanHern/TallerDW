## --- Instalaciones previas ---
## py -m pip install pandas pyodbc python-dotenv

import pandas as pd
from dotenv import load_dotenv
import os
import platform
import pyodbc

# ============================================================
# Cargar variables de entorno y configurar conexión
# ============================================================

load_dotenv()

server = os.getenv("serverenv")
db_origen = os.getenv("databaseenv_origen")
db_dw = os.getenv("databaseenv_dw")
username = os.getenv("usernameenv")
password = os.getenv("passwordenv")

# Conexion con express
"""""
# Detectar driver según sistema operativo
if platform.system() == "Windows":
    driver = "ODBC Driver 17 for SQL Server"
else:
    driver = "ODBC Driver 18 for SQL Server"

# Conexión a base origen
conn_origen = pyodbc.connect(
    f"DRIVER={{{driver}}};SERVER={server};DATABASE={db_origen};UID={username};PWD={password};TrustServerCertificate=yes;"
)

# Conexión a base destino (Data Warehouse)
conn_dw = pyodbc.connect(
    f"DRIVER={{{driver}}};SERVER={server};DATABASE={db_dw};UID={username};PWD={password};TrustServerCertificate=yes;"
)

cursor_dw = conn_dw.cursor()
""""" 

# Conexion con Developer
# Detectar driver según sistema operativo
if platform.system() == "Windows":
    driver = "ODBC Driver 17 for SQL Server"
else:
    driver = "ODBC Driver 18 for SQL Server"

# Construir parte de autenticación: usar Trusted_Connection cuando username/password estén vacíos
if username and password:
    auth_part = f"UID={username};PWD={password};"
else:
    auth_part = "Trusted_Connection=yes;"

conn_str_origen = f"DRIVER={{{driver}}};SERVER={server};DATABASE={db_origen};{auth_part}TrustServerCertificate=yes;"
conn_str_dw = f"DRIVER={{{driver}}};SERVER={server};DATABASE={db_dw};{auth_part}TrustServerCertificate=yes;"

# Debug (oculta contraseña si existe)
if password:
    print("Conn origen:", conn_str_origen.replace(password, "***"))
else:
    print("Conn origen:", conn_str_origen)

conn_origen = pyodbc.connect(conn_str_origen)
conn_dw = pyodbc.connect(conn_str_dw)

cursor_dw = conn_dw.cursor()
# ...existing code...

# ============================================================
# EXTRACT – Obtener datos desde la base origen
# ============================================================

query = """
SELECT 
    SUM(S.Quantity) AS CantidadTotal, 
    SUM(S.LineTotal) AS MontoTotal, 
    S.Dscription AS Producto, 
    I.U_Marca AS Marca, 
    S.DocDate AS Fecha, 
    S.CardName AS Cliente, 
    O.Country AS Pais, 
    O.U_Zona AS Zona
FROM dbo.SALES S
LEFT JOIN OITM I ON S.ItemCode = I.ItemCode
LEFT JOIN OCRD O ON S.CardCode = O.CardCode
GROUP BY 
    S.Dscription, 
    S.DocDate, 
    S.CardName, 
    I.U_Marca, 
    O.Country, 
    O.U_Zona
"""

df = pd.read_sql(query, conn_origen)
print(f"Datos extraídos desde origen: {len(df)} filas")

# ============================================================
# TRANSFORM – Limpieza y preparación
# ============================================================

df["Producto"] = df["Producto"].str.strip()
df["Marca"] = df["Marca"].fillna("SIN MARCA")
df["Cliente"] = df["Cliente"].str.strip()
df["Pais"] = df["Pais"].fillna("DESCONOCIDO")
df["Zona"] = df["Zona"].fillna("DESCONOCIDA")
df["Fecha"] = pd.to_datetime(df["Fecha"]).dt.date

print("Ejemplo de datos transformados:")
print(df.head())

# ============================================================
# LOAD – Insertar en Data Warehouse
# ============================================================

# -------- DIM_ITEM --------
print("Cargando DIM_ITEM...")

for _, row in df.iterrows():
    cursor_dw.execute("""
        IF NOT EXISTS (SELECT 1 FROM DIM_ITEM WHERE nombre = ? AND marca = ?)
        INSERT INTO DIM_ITEM (nombre, marca)
        VALUES (?, ?)
    """, row["Producto"], row["Marca"], row["Producto"], row["Marca"])

conn_dw.commit()

# -------- DIM_CLIENTE --------
print("Cargando DIM_CLIENTE...")

for _, row in df.iterrows():
    cursor_dw.execute("""
        IF NOT EXISTS (SELECT 1 FROM DIM_CLIENTE WHERE nombre = ?)
        INSERT INTO DIM_CLIENTE (nombre, pais, zona)
        VALUES (?, ?, ?)
    """, row["Cliente"], row["Cliente"], row["Pais"], row["Zona"])

conn_dw.commit()

# -------- DIM_TIEMPO  --------
print("Cargando DIM_TIEMPO...")
unique_dates = sorted(df["Fecha"].dropna().unique())
for d in unique_dates:
    año = d.year
    mes = d.month
    dia = d.day
    semana = d.isocalendar()[1]      
    dia_semana = d.isoweekday()      
    tipo_cambio = None

    cursor_dw.execute("""
        IF NOT EXISTS (SELECT 1 FROM DIM_TIEMPO WHERE fecha = ?)
        INSERT INTO DIM_TIEMPO (año, mes, dia, fecha, semana, dia_semana, tipo_cambio)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, d, año, mes, dia, d, semana, dia_semana, tipo_cambio)

conn_dw.commit()

# -------- FACT_VENTAS --------
print("Cargando FACT_VENTAS...")

for _, row in df.iterrows():
    # Buscar id_item
    cursor_dw.execute("SELECT id FROM DIM_ITEM WHERE nombre = ? AND marca = ?", row["Producto"], row["Marca"])
    id_item_row = cursor_dw.fetchone()
    id_item = id_item_row[0] if id_item_row else None

    # Buscar id_cliente
    cursor_dw.execute("SELECT id FROM DIM_CLIENTE WHERE nombre = ?", row["Cliente"])
    id_cliente_row = cursor_dw.fetchone()
    id_cliente = id_cliente_row[0] if id_cliente_row else None

    # Buscar id_fecha desde DIM_TIEMPO
    cursor_dw.execute("SELECT id FROM DIM_TIEMPO WHERE fecha = ?", row["Fecha"])
    id_fecha_row = cursor_dw.fetchone()
    id_fecha = id_fecha_row[0] if id_fecha_row else None

    # Insertar en FACT_VENTAS (sin id_bodega ni id_vendedor)
    cursor_dw.execute("""
        INSERT INTO FACT_VENTAS (cantidad, total_ventas, id_fecha, id_cliente, id_item)
        VALUES (?, ?, ?, ?, ?)
    """, row["CantidadTotal"], row["MontoTotal"], id_fecha, id_cliente, id_item)

conn_dw.commit()
print("Carga completada en FACT_VENTAS")


# ============================================================
# 5️⃣ Cerrar conexiones
# ============================================================
cursor_dw.close()
conn_origen.close()
conn_dw.close()
print("Conexiones cerradas correctamente")
