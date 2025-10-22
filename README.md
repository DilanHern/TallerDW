# TallerDW - Data Warehouse de Ventas

##  Instalación

```powershell
py -m pip install pandas pyodbc python-dotenv openpyxl
```

## ⚙️ Configuración

Crear archivo `.env` con tus credenciales:

```properties
serverenv=TU_SERVIDOR\SQLEXPRESS
databaseenv=DW_VENTAS
databaseenv_origen=DB_SALES
databaseenv_dw=DW_VENTAS
usernameenv=
passwordenv=
```

## 🚀 Ejecutar (en orden)

```powershell
# 1. Cargar dimensión de tiempo
py excel_tiempo_a_dim.py

# 2. Cargar ventas desde JSON
py etl_json.py

# 3. Cargar ventas desde DB origen
py etl_DB_SALES.py
```
