CREATE TABLE DIM_TIEMPO (
    id_fecha INT IDENTITY(1,1) PRIMARY KEY,
    año INT NOT NULL,
    mes INT NOT NULL,
    dia INT NOT NULL,
    fecha DATE NOT NULL,
    semana INT,
    diaSemana NVARCHAR(16),
    tipoCambio DECIMAL(12, 2)
);

CREATE TABLE DIM_ITEM (
    id_item INT IDENTITY(1,1) PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    marca VARCHAR(50)
);

CREATE TABLE DIM_CLIENTE (
    id_cliente INT IDENTITY(1,1) PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    pais VARCHAR(10),
    zona VARCHAR(10)
);

CREATE TABLE FACT_VENTAS (
    id_ventas INT IDENTITY(1,1) PRIMARY KEY,  
    quantity INT NOT NULL,
    total_ventas DECIMAL(18, 2) NOT NULL,
    id_fecha INT NOT NULL,
    id_cliente INT NOT NULL,
    id_item INT NOT NULL,
    CONSTRAINT FK_FACT_TIEMPO FOREIGN KEY (id_fecha) REFERENCES DIM_TIEMPO(id_fecha),
    CONSTRAINT FK_FACT_CLIENTE FOREIGN KEY (id_cliente) REFERENCES DIM_CLIENTE(id_cliente),
    CONSTRAINT FK_FACT_ITEM FOREIGN KEY (id_item) REFERENCES DIM_ITEM(id_item)
);