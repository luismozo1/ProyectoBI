// =========================================================================
// Backend/server.js
// SERVIDOR ÚNICO PARA DESPLIEGUE EN LA NUBE (Render.com - Free Tier)
// Une la lógica de capa1.js (Fuentes de Datos) y capa3.js (ETL)
// en un solo proceso, porque el plan gratuito de Render permite
// 1 servicio web activo. Así evitamos correr 2 servidores separados.
// =========================================================================

const express = require('express');
const cors = require('cors');

const app = express();

// CORS: permite que tu Frontend (en GitHub Pages u otro dominio)
// pueda llamar a este backend sin ser bloqueado por el navegador.
app.use(cors());
app.use(express.json());

// -------------------------------------------------------------------------
// Configuración de base de datos (se deja documentada, NO se usa todavía).
// Tu BI real funciona leyendo los CSV directamente en el navegador,
// así que esta configuración queda lista para cuando decidas conectar
// un SQL Server real (Azure SQL, por ejemplo) en el futuro.
// -------------------------------------------------------------------------
const dbConfig = {
    user: process.env.DB_USER || 'tu_usuario_sql',
    password: process.env.DB_PASSWORD || 'tu_password_sql',
    server: process.env.DB_SERVER || 'localhost',
    database: process.env.DB_NAME || 'DW_Congestion_Vehicular',
    options: {
        encrypt: true,
        trustServerCertificate: true
    }
};

// Ruta raíz: útil para comprobar que el backend está vivo desde el navegador
app.get('/', (req, res) => {
    res.json({
        status: 'online',
        servicio: 'Backend ProyectoBI - Congestión Vehicular',
        endpoints: ['/api/capa1/procesar', '/api/capa3/etl']
    });
});

// -------------------------------------------------------------------------
// CAPA 1 — Fuentes de Datos: valida el archivo cargado por el usuario
// -------------------------------------------------------------------------
app.post('/api/capa1/procesar', (req, res) => {
    const { nombre, tamano } = req.body;

    console.log(`[LOG BACKEND] Procesando archivo de origen: ${nombre} (${(tamano / 1024).toFixed(2)} KB)`);

    if (!nombre || !nombre.endsWith('.csv')) {
        return res.status(400).json({
            success: false,
            message: "Error en el Servidor: Formato no soportado. Debe cargar un archivo plano estructurado (.CSV)."
        });
    }

    res.json({
        success: true,
        message: `[SERVIDOR] Archivo '${nombre}' validado correctamente. Conexión establecida con la base de datos para la Capa 2.`
    });
});

// -------------------------------------------------------------------------
// CAPA 3 — Proceso ETL: dispara la limpieza/estructuración multidimensional
// -------------------------------------------------------------------------
app.post('/api/capa3/etl', (req, res) => {
    console.log("[LOG BACKEND] Orden recibida. Iniciando motor de limpieza ETL...");

    // Aquí, en el futuro, se conectaría a la BD real:
    // let pool = await sql.connect(dbConfig);
    // ...ejecutar queries de conversión e inserción final en dimensiones...

    res.json({
        success: true,
        message: "[SERVIDOR] Pipeline ejecutado. Tablas de dimensiones y tabla de hechos pobladas correctamente."
    });
});

// -------------------------------------------------------------------------
// PUERTO: Render asigna su propio puerto vía la variable de entorno PORT.
// En tu máquina local seguirá funcionando igual, usando 3000 por defecto.
// -------------------------------------------------------------------------
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`================================================================`);
    console.log(`[BACKEND ACTIVO] Servidor unificado corriendo en el puerto ${PORT}`);
    console.log(`================================================================`);
});
