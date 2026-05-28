from fastmcp import FastMCP
import pymysql
import os
from typing import Any, Dict, List

mcp = FastMCP("MySQL Database MCP Server")

# Configuration from environment variables
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "")
DB_PORT = int(os.getenv("DB_PORT", "3306"))

# Lista de bases de datos permitidas (whitelist)
ALLOWED_DATABASES = os.getenv("ALLOWED_DATABASES", "").split(",") if os.getenv("ALLOWED_DATABASES") else [DB_NAME]
ALLOWED_DATABASES = [db.strip() for db in ALLOWED_DATABASES if db.strip()]

def is_database_allowed(database_name: str) -> bool:
    """Verificar si una base de datos está permitida."""
    if not ALLOWED_DATABASES:
        return True  # Si no hay restricciones, permitir todas
    return database_name in ALLOWED_DATABASES

def get_db_connection(database: str = None):
    """Create a new database connection.
    
    Args:
        database: Base de datos específica a conectar. Si no se especifica, usa DB_NAME
        
    Returns:
        Conexión a la base de datos
        
    Raises:
        ValueError: Si la base de datos no está permitida
    """
    db_to_use = database if database else DB_NAME
    
    # Validar que la base de datos esté permitida
    if not is_database_allowed(db_to_use):
        raise ValueError(f"Base de datos '{db_to_use}' no está permitida. Bases de datos permitidas: {ALLOWED_DATABASES}")
    
    if not DB_PASSWORD:
        raise ValueError("DB_PASSWORD no configurada. Configura antes de ejecutar.")
    
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=db_to_use,
        port=DB_PORT,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

def is_safe_query(sql: str, allowed_operations: list = None) -> bool:
    """Validar que solo sea SELECT o permitidas."""
    if allowed_operations is None:
        allowed_operations = ["SELECT"]
    
    statement_type = sql.strip().split()[0].upper()
    if statement_type not in allowed_operations:
        raise ValueError(f"Operación '{statement_type}' no permitida")
    return True

@mcp.tool
def query_database(sql: str, limit: int = 1000) -> Dict[str, Any]:
    """Execute a SELECT query with safety limits.
    
    Args:
        sql: The SELECT query
        limit: Maximum rows to return (default 1000)
    """
    try:
        if not sql.strip().upper().startswith("SELECT"):
            return {"success": False, "error": "Only SELECT queries allowed"}
        
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                results = cursor.fetchall()[:limit]
                return {
                    "success": True,
                    "rows_count": len(results),
                    "data": results,
                    "truncated": cursor.rowcount > limit
                }
        finally:
            connection.close()
    except Exception as e:
        return {"success": False, "error": str(e)}
    
@mcp.tool
def execute_transaction(statements: List[str]) -> Dict[str, Any]:
    """Execute multiple statements as a transaction.
    
    Args:
        statements: List of INSERT/UPDATE/DELETE statements
        
    Returns:
        Dictionary with success status or rollback info
    """
    try:
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                for sql in statements:
                    cursor.execute(sql)
                connection.commit()
                return {
                    "success": True,
                    "statements_executed": len(statements)
                }
        except Exception as e:
            connection.rollback()
            return {
                "success": False,
                "error": str(e),
                "rolled_back": True
            }
        finally:
            connection.close()
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool
def get_tables(database: str = None) -> Dict[str, Any]:
    """Get tables from a specific database or current one."""
    try:
        db_to_use = database if database else DB_NAME
        if not is_database_allowed(db_to_use):
            return {"success": False, "error": "Database not allowed"}
        
        connection = get_db_connection(db_to_use)
        try:
            with connection.cursor() as cursor:
                cursor.execute("SHOW TABLES;")
                key = f'Tables_in_{db_to_use}'
                tables = [row[key] for row in cursor.fetchall()]
                return {"success": True, "tables": tables}
        finally:
            connection.close()
    except Exception as e:
        return {"success": False, "error": str(e)}
    
@mcp.tool
def get_allowed_databases() -> Dict[str, Any]:
    """Get the list of allowed databases.
    
    Returns:
        Dictionary with list of allowed databases
    """
    return {
        "success": True,
        "allowed_databases": ALLOWED_DATABASES,
        "current_database": DB_NAME
    }

@mcp.tool
def query_database_in(database: str, sql: str) -> Dict[str, Any]:
    """Execute a SELECT query on a specific MySQL database (if allowed).
    
    Args:
        database: The database name to query
        sql: The SELECT SQL query to execute
        
    Returns:
        Dictionary with 'success' status and 'data' or 'error'
    """
    try:
        connection = get_db_connection(database)
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                results = cursor.fetchall()
                return {
                    "success": True,
                    "database": database,
                    "rows_count": len(results),
                    "data": results
                }
        finally:
            connection.close()
    except ValueError as e:
        return {
            "success": False,
            "error": str(e)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool
def get_table_schema(table_name: str) -> Dict[str, Any]:
    """Get the schema (columns) of a table.
    
    Args:
        table_name: Name of the table
        
    Returns:
        Dictionary with 'success' status and 'columns' information
    """
    try:
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"DESCRIBE `{pymysql.escape_string(table_name)}`;")
                columns = cursor.fetchall()
                return {
                    "success": True,
                    "table": table_name,
                    "columns": columns
                }
        finally:
            connection.close()
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    mcp.run(
        transport="HTTP",
        log_level="DEBUG",
    )