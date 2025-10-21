CREATE DATABASE DW_VENTAS;
GO

USE DW_VENTAS;
GO

-- Tabla Dimensión: TIEMPO
CREATE TABLE DIM_TIEMPO (
    id_fecha INT PRIMARY KEY,
    anio INT,
    mes INT,
    dia INT,
    fecha DATE,
    semana INT,
    diaSemana VARCHAR(15),
    tipoCambio DECIMAL(12, 2)
);
GO


-- Tabla Dimensión: ITEM
CREATE TABLE DIM_ITEM (
    id_item INT PRIMARY KEY,
    nombre VARCHAR(50),
    marca VARCHAR(25)
);
GO

-- Tabla Dimensión: CLIENTE
CREATE TABLE DIM_CLIENTE (
    id_cliente INT PRIMARY KEY,
    nombre VARCHAR(50),
    pais VARCHAR(25),
    zona VARCHAR(25)
);
GO

-- Tabla de Hechos: VENTAS
CREATE TABLE FACT_VENTAS (
    id_ventas INT PRIMARY KEY,
    cantidad INT,
    total_ventas DECIMAL(15, 2),
    id_fecha INT,
    id_cliente INT,
    id_item INT

    CONSTRAINT FK_VENTAS_TIEMPO FOREIGN KEY (id_fecha)
    REFERENCES DIM_TIEMPO(id_fecha),
    CONSTRAINT FK_VENTAS_CLIENTE FOREIGN KEY (id_cliente)
    REFERENCES DIM_CLIENTE(id_cliente),
    CONSTRAINT FK_VENTAS_ITEM FOREIGN KEY (id_item)
    REFERENCES DIM_ITEM(id_item)
);
GO
