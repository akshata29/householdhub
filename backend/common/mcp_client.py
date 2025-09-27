"""
Model Context Protocol (MCP) Client for MSSQL Server Integration
"""

import asyncio
import logging
import json
import os
import re
import pyodbc
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from contextlib import asynccontextmanager

from common.config import get_settings
from common.auth import get_sql_access_token

logger = logging.getLogger(__name__)


class MCPSQLTool:
    """Base class for MCP SQL Tools"""
    
    def __init__(self, name: str, description: str, connection_factory):
        self.name = name
        self.description = description
        self.connection_factory = connection_factory
        self.input_schema = {}
    
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool with given arguments"""
        raise NotImplementedError


class ReadDataTool(MCPSQLTool):
    """Tool for executing SELECT queries safely"""
    
    def __init__(self, connection_factory):
        super().__init__(
            name="read_data",
            description="Execute SELECT queries to read data from the database. Query must start with SELECT and cannot contain destructive operations.",
            connection_factory=connection_factory
        )
        self.input_schema = {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "SQL SELECT query to execute. Must start with SELECT and cannot contain destructive operations."
                }
            },
            "required": ["query"]
        }
    
    def _validate_query(self, query: str) -> Dict[str, Any]:
        """Validate SQL query for security"""
        if not query or not isinstance(query, str):
            return {"valid": False, "error": "Query must be a non-empty string"}
        
        # Clean and normalize query
        clean_query = re.sub(r'--.*$', '', query, flags=re.MULTILINE)  # Remove line comments
        clean_query = re.sub(r'/\*.*?\*/', '', clean_query, flags=re.DOTALL)  # Remove block comments
        clean_query = re.sub(r'\s+', ' ', clean_query).strip().upper()
        
        if not clean_query:
            return {"valid": False, "error": "Query cannot be empty after removing comments"}
        
        # Check if query starts with SELECT
        if not clean_query.startswith('SELECT'):
            return {"valid": False, "error": "Only SELECT queries are allowed"}
        
        # Check for dangerous keywords
        dangerous_keywords = [
            'DELETE', 'DROP', 'UPDATE', 'INSERT', 'ALTER', 'CREATE',
            'TRUNCATE', 'EXEC', 'EXECUTE', 'MERGE', 'REPLACE',
            'GRANT', 'REVOKE', 'COMMIT', 'ROLLBACK', 'TRANSACTION'
        ]
        
        for keyword in dangerous_keywords:
            if keyword in clean_query:
                return {"valid": False, "error": f"Dangerous keyword '{keyword}' detected in query"}
        
        # Check for multiple statements
        if ';' in clean_query.rstrip(';'):
            return {"valid": False, "error": "Multiple statements not allowed"}
        
        # Limit query length
        if len(query) > 10000:
            return {"valid": False, "error": "Query too long. Maximum 10,000 characters allowed"}
        
        return {"valid": True}
    
    def _sanitize_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sanitize query results"""
        max_records = 10000
        if len(results) > max_records:
            logger.warning(f"Query returned {len(results)} records, limiting to {max_records}")
            results = results[:max_records]
        
        # Sanitize each record
        sanitized = []
        for record in results:
            if isinstance(record, dict):
                sanitized_record = {}
                for key, value in record.items():
                    # Sanitize column names
                    clean_key = re.sub(r'[^\w\s\-_.]', '', str(key))
                    sanitized_record[clean_key] = value
                sanitized.append(sanitized_record)
            else:
                sanitized.append(record)
        
        return sanitized
    
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute SELECT query"""
        try:
            query = arguments.get("query")
            if not query:
                return {
                    "success": False,
                    "error": "Query parameter is required"
                }
            
            # Validate query
            validation = self._validate_query(query)
            if not validation["valid"]:
                return {
                    "success": False,
                    "error": f"Query validation failed: {validation['error']}"
                }
            
            # Execute query
            conn = await self.connection_factory.get_connection()
            cursor = conn.cursor()
            
            start_time = datetime.now()
            cursor.execute(query)
            results = []
            
            # Fetch results
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            rows = cursor.fetchall()
            
            for row in rows:
                record = {}
                for i, value in enumerate(row):
                    record[columns[i]] = value
                results.append(record)
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Sanitize results
            sanitized_results = self._sanitize_results(results)
            
            cursor.close()
            conn.close()
            
            return {
                "success": True,
                "data": sanitized_results,
                "row_count": len(sanitized_results),
                "total_rows": len(results),
                "execution_time_ms": int(execution_time),
                "message": f"Query executed successfully. Retrieved {len(sanitized_results)} record(s)"
            }
            
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            error_message = str(e)
            # Don't expose internal error details
            if "Invalid object name" in error_message:
                safe_error = error_message
            else:
                safe_error = "Database query execution failed"
            
            return {
                "success": False,
                "error": safe_error
            }


class ListTablesTool(MCPSQLTool):
    """Tool for listing database tables"""
    
    def __init__(self, connection_factory):
        super().__init__(
            name="list_tables",
            description="List all tables in the database",
            connection_factory=connection_factory
        )
        self.input_schema = {
            "type": "object",
            "properties": {}
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """List all tables"""
        try:
            conn = await self.connection_factory.get_connection()
            cursor = conn.cursor()
            
            query = """
            SELECT 
                TABLE_SCHEMA,
                TABLE_NAME,
                TABLE_TYPE
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_TYPE = 'BASE TABLE'
                AND TABLE_SCHEMA NOT IN ('sys', 'INFORMATION_SCHEMA')
            ORDER BY TABLE_SCHEMA, TABLE_NAME
            """
            
            cursor.execute(query)
            results = []
            
            for row in cursor.fetchall():
                results.append({
                    "schema": row[0],
                    "table_name": row[1],
                    "table_type": row[2]
                })
            
            cursor.close()
            conn.close()
            
            return {
                "success": True,
                "tables": results,
                "count": len(results)
            }
            
        except Exception as e:
            logger.error(f"Error listing tables: {e}")
            return {
                "success": False,
                "error": str(e)
            }


class DescribeTableTool(MCPSQLTool):
    """Tool for describing table schema"""
    
    def __init__(self, connection_factory):
        super().__init__(
            name="describe_table",
            description="Get detailed schema information for a specific table",
            connection_factory=connection_factory
        )
        self.input_schema = {
            "type": "object",
            "properties": {
                "table_name": {
                    "type": "string",
                    "description": "Name of the table to describe"
                },
                "schema_name": {
                    "type": "string",
                    "description": "Schema name (optional, defaults to dbo)"
                }
            },
            "required": ["table_name"]
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Describe table schema"""
        try:
            table_name = arguments.get("table_name")
            schema_name = arguments.get("schema_name", "dbo")
            
            if not table_name:
                return {
                    "success": False,
                    "error": "table_name parameter is required"
                }
            
            conn = await self.connection_factory.get_connection()
            cursor = conn.cursor()
            
            # Get column information
            columns_query = """
            SELECT 
                c.COLUMN_NAME,
                c.DATA_TYPE,
                c.IS_NULLABLE,
                c.COLUMN_DEFAULT,
                c.CHARACTER_MAXIMUM_LENGTH,
                c.NUMERIC_PRECISION,
                c.NUMERIC_SCALE,
                c.ORDINAL_POSITION
            FROM INFORMATION_SCHEMA.COLUMNS c
            WHERE c.TABLE_NAME = ? AND c.TABLE_SCHEMA = ?
            ORDER BY c.ORDINAL_POSITION
            """
            
            cursor.execute(columns_query, (table_name, schema_name))
            columns = []
            
            for row in cursor.fetchall():
                columns.append({
                    "column_name": row[0],
                    "data_type": row[1],
                    "is_nullable": row[2] == 'YES',
                    "default_value": row[3],
                    "max_length": row[4],
                    "precision": row[5],
                    "scale": row[6],
                    "position": row[7]
                })
            
            # Get primary key information
            pk_query = """
            SELECT kcu.COLUMN_NAME
            FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
            JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE kcu ON tc.CONSTRAINT_NAME = kcu.CONSTRAINT_NAME
            WHERE tc.TABLE_NAME = ? AND tc.TABLE_SCHEMA = ? AND tc.CONSTRAINT_TYPE = 'PRIMARY KEY'
            ORDER BY kcu.ORDINAL_POSITION
            """
            
            cursor.execute(pk_query, (table_name, schema_name))
            primary_keys = [row[0] for row in cursor.fetchall()]
            
            # Get foreign key information
            fk_query = """
            SELECT 
                kcu.COLUMN_NAME,
                ccu.TABLE_SCHEMA AS FOREIGN_TABLE_SCHEMA,
                ccu.TABLE_NAME AS FOREIGN_TABLE_NAME,
                ccu.COLUMN_NAME AS FOREIGN_COLUMN_NAME
            FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
            JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE kcu ON tc.CONSTRAINT_NAME = kcu.CONSTRAINT_NAME
            JOIN INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS rc ON tc.CONSTRAINT_NAME = rc.CONSTRAINT_NAME
            JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE ccu ON rc.UNIQUE_CONSTRAINT_NAME = ccu.CONSTRAINT_NAME
            WHERE tc.TABLE_NAME = ? AND tc.TABLE_SCHEMA = ? AND tc.CONSTRAINT_TYPE = 'FOREIGN KEY'
            """
            
            cursor.execute(fk_query, (table_name, schema_name))
            foreign_keys = []
            
            for row in cursor.fetchall():
                foreign_keys.append({
                    "column_name": row[0],
                    "foreign_table_schema": row[1],
                    "foreign_table_name": row[2],
                    "foreign_column_name": row[3]
                })
            
            cursor.close()
            conn.close()
            
            return {
                "success": True,
                "table_name": table_name,
                "schema_name": schema_name,
                "columns": columns,
                "primary_keys": primary_keys,
                "foreign_keys": foreign_keys
            }
            
        except Exception as e:
            logger.error(f"Error describing table: {e}")
            return {
                "success": False,
                "error": str(e)
            }


class MCPConnectionFactory:
    """Factory for creating database connections for MCP tools"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
    
    async def get_connection(self) -> pyodbc.Connection:
        """Get database connection with proper authentication"""
        try:
            # For Azure SQL with Managed Identity
            access_token = get_sql_access_token()
            if access_token:
                # Use token-based authentication
                conn_str = self.connection_string.replace(
                    "Authentication=Active Directory Managed Identity",
                    f"AccessToken={access_token}"
                )
            else:
                conn_str = self.connection_string
            
            return pyodbc.connect(
                conn_str,
                timeout=30,
                autocommit=True
            )
            
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise


class MCPSQLServer:
    """MCP Server implementation for SQL operations"""
    
    def __init__(self, connection_string: str):
        self.connection_factory = MCPConnectionFactory(connection_string)
        self.tools = {}
        self._initialize_tools()
    
    def _initialize_tools(self):
        """Initialize MCP tools"""
        self.tools = {
            "read_data": ReadDataTool(self.connection_factory),
            "list_tables": ListTablesTool(self.connection_factory),
            "describe_table": DescribeTableTool(self.connection_factory)
        }
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available MCP tools"""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.input_schema
            }
            for tool in self.tools.values()
        ]
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific MCP tool"""
        if name not in self.tools:
            return {
                "success": False,
                "error": f"Unknown tool: {name}"
            }
        
        tool = self.tools[name]
        return await tool.execute(arguments)
    
    async def get_schema_info(self) -> Dict[str, Any]:
        """Get comprehensive database schema information"""
        try:
            # Get all tables
            tables_result = await self.call_tool("list_tables", {})
            if not tables_result.get("success"):
                return tables_result
            
            schema_info = {
                "tables": {},
                "relationships": []
            }
            
            # Get detailed info for each table
            for table in tables_result.get("tables", []):
                table_name = table["table_name"]
                schema_name = table["schema"]
                
                table_detail = await self.call_tool("describe_table", {
                    "table_name": table_name,
                    "schema_name": schema_name
                })
                
                if table_detail.get("success"):
                    full_table_name = f"{schema_name}.{table_name}"
                    schema_info["tables"][full_table_name] = {
                        "columns": table_detail.get("columns", []),
                        "primary_keys": table_detail.get("primary_keys", []),
                        "foreign_keys": table_detail.get("foreign_keys", [])
                    }
                    
                    # Add relationship information
                    for fk in table_detail.get("foreign_keys", []):
                        schema_info["relationships"].append({
                            "from_table": full_table_name,
                            "from_column": fk["column_name"],
                            "to_table": f"{fk['foreign_table_schema']}.{fk['foreign_table_name']}",
                            "to_column": fk["foreign_column_name"]
                        })
            
            return {
                "success": True,
                "schema": schema_info
            }
            
        except Exception as e:
            logger.error(f"Error getting schema info: {e}")
            return {
                "success": False,
                "error": str(e)
            }