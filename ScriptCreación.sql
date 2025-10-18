-- CREACIÓN DE TABLAS DIMENSIONALES

CREATE TABLE DIM_TIEMPO (
    id_fecha INT PRIMARY KEY,
    año INT NOT NULL,
    mes INT NOT NULL,
    dia INT NOT NULL,
    fecha DATE NOT NULL,
    semana INT,
    diaSemana VARCHAR(16),
    tipoCambio DECIMAL(12, 2)
);
CREATE TABLE DIM_ITEM (
    id_item INT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    marca VARCHAR(50),
    precio DECIMAL(12, 2) NOT NULL
);

CREATE TABLE DIM_VENDEDOR (
    id_vendedor INT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL
);

CREATE TABLE DIM_WHS (
    id_bodega INT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL
);

CREATE TABLE DIM_CLIENTE (
    id_cliente INT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    pais VARCHAR(10),
    zona VARCHAR(10)
);

-- TABLA DE HECHOS

CREATE TABLE FACT_VENTAS (
    id_ventas INT PRIMARY KEY,
    quantity INT NOT NULL,
    total_ventas DECIMAL(18, 2) NOT NULL,
    id_fecha INT NOT NULL,
    id_bodega INT NOT NULL,
    id_cliente INT NOT NULL,
    id_item INT NOT NULL,
    id_vendedor INT NOT NULL,
    -- Definición de claves foráneas
    CONSTRAINT FK_FACT_TIEMPO FOREIGN KEY (id_fecha) REFERENCES DIM_TIEMPO(id_fecha),
    CONSTRAINT FK_FACT_WHS FOREIGN KEY (id_bodega) REFERENCES DIM_WHS(id_bodega),
    CONSTRAINT FK_FACT_CLIENTE FOREIGN KEY (id_cliente) REFERENCES DIM_CLIENTE(id_cliente),
    CONSTRAINT FK_FACT_ITEM FOREIGN KEY (id_item) REFERENCES DIM_ITEM(id_item),
    CONSTRAINT FK_FACT_VENDEDOR FOREIGN KEY (id_vendedor) REFERENCES DIM_VENDEDOR(id_vendedor)
);
