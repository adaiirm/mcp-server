# MySQL MCP Server

Un servidor MCP (Model Context Protocol) que permite a los agentes de Claude interactuar con bases de datos MySQL.

## Características

- **query_database**: Ejecuta consultas SELECT
- **execute_statement**: Ejecuta INSERT, UPDATE, DELETE
- **get_tables**: Lista todas las tablas de la base de datos
- **get_table_schema**: Obtiene la estructura (columnas) de una tabla

## Requisitos

- Python 3.13+
- MySQL Server (local o remoto)
- pip o uv

## Instalación

1. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   # o si usas uv:
   uv sync
   ```

2. **Configurar variables de entorno:**
   
   Crea un archivo `.env` o establece las variables:
   ```bash
   # Windows PowerShell
   $env:DB_HOST = "localhost"
   $env:DB_USER = "tu_usuario"
   $env:DB_PASSWORD = "tu_contraseña"
   $env:DB_NAME = "tu_base_datos"
   $env:DB_PORT = "3306"
   ```

   O edita directamente en `main.py` los valores por defecto.

## Uso

1. **Inicia el servidor:**
   ```bash
   python main.py
   ```
   El servidor estará disponible en `http://127.0.0.1:9000`

2. **Configura Claude para usar este MCP:**

   En tu `claude_desktop_config.json` (macOS/Linux: `~/.claude_desktop_config.json` o Windows: `%APPDATA%\Claude\claude_desktop_config.json`):
   
   ```json
   {
     "mcpServers": {
       "mysql": {
         "command": "python",
         "args": ["C:/path/to/main.py"]
       }
     }
   }
   ```

## Herramientas disponibles

### query_database(sql: str)
Ejecuta una consulta SELECT en MySQL.

**Ejemplo:**
```
query_database("SELECT * FROM usuarios WHERE edad > 18 LIMIT 10")
```

**Respuesta:**
```json
{
  "success": true,
  "rows_count": 5,
  "data": [
    {"id": 1, "nombre": "Juan", "edad": 25},
    ...
  ]
}
```

### execute_statement(sql: str)
Ejecuta INSERT, UPDATE o DELETE.

**Ejemplo:**
```
execute_statement("UPDATE usuarios SET edad = 30 WHERE id = 1")
```

**Respuesta:**
```json
{
  "success": true,
  "affected_rows": 1
}
```

### get_tables()
Obtiene la lista de todas las tablas.

**Ejemplo:**
```
get_tables()
```

**Respuesta:**
```json
{
  "success": true,
  "tables": ["usuarios", "productos", "pedidos"]
}
```

### get_table_schema(table_name: str)
Obtiene la estructura de una tabla.

**Ejemplo:**
```
get_table_schema("usuarios")
```

**Respuesta:**
```json
{
  "success": true,
  "table": "usuarios",
  "columns": [
    {
      "Field": "id",
      "Type": "int",
      "Null": "NO",
      "Key": "PRI",
      "Default": null,
      "Extra": "auto_increment"
    },
    ...
  ]
}
```

## Seguridad

- Usa variables de entorno para credenciales
- No hardcodees contraseñas en el código
- Considera usar SSL para conexiones remotas
- Implementa validación de entrada en Claude para prevenir SQL injection

## Troubleshooting

**Conexión rechazada:**
- Verifica que MySQL esté corriendo
- Comprueba las credenciales
- Verifica el host y puerto

**Base de datos no encontrada:**
- Asegúrate de crear la base de datos: `CREATE DATABASE tu_base_datos;`
- Verifica el nombre en `DB_NAME`

**Errores de caracteres:**
- El servidor usa `utf8mb4` por defecto
- Asegúrate de que tu base de datos también usa este charset
