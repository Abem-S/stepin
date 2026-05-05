"""
StepIn Platform - Database Configuration
Supabase PostgreSQL and Redis client setup
"""
import os
from typing import Optional

from supabase import create_client, Client
import redis

# Environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://placeholder.supabase.co")
# Prefer service role in backend, then anon key, then legacy SUPABASE_KEY.
SUPABASE_KEY = (
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    or os.getenv("SUPABASE_ANON_KEY")
    or os.getenv("SUPABASE_KEY")
    or "placeholder-key"
)
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

# Supabase client singleton
_supabase_client: Optional[Client] = None

# Redis client singleton
_redis_client: Optional[redis.Redis] = None


def get_supabase() -> Client:
    """Get or create Supabase client singleton"""
    global _supabase_client
    if _supabase_client is None:
        if SUPABASE_URL == "https://placeholder.supabase.co":
            # Return a mock client for development without Supabase
            _supabase_client = MockSupabaseClient()
        else:
            _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase_client


# Alias for compatibility
def get_supabase_client() -> Client:
    """Alias for get_supabase() - Get or create Supabase client"""
    return get_supabase()


def get_redis() -> redis.Redis:
    """Get or create Redis client singleton"""
    global _redis_client
    if _redis_client is None:
        try:
            _redis_client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                db=REDIS_DB,
                decode_responses=True,
                socket_connect_timeout=2,
            )
            # Test connection
            _redis_client.ping()
        except (redis.ConnectionError, redis.TimeoutError):
            # Fall back to mock Redis for development
            _redis_client = MockRedisClient()
    return _redis_client


def close_connections():
    """Close all database connections"""
    global _supabase_client, _redis_client
    if _supabase_client is not None:
        _supabase_client = None
    if _redis_client is not None:
        try:
            _redis_client.close()
        except Exception:
            pass
        _redis_client = None


class MockSupabaseClient:
    """Mock Supabase client for development without actual database"""
    
    def __init__(self):
        self.table_data: dict = {}
    
    def table(self, table_name: str):
        return MockTable(table_name, self.table_data)


class MockTable:
    """Mock table for development"""
    
    def __init__(self, table_name: str, data_store: dict):
        self.table_name = table_name
        self.data_store = data_store
        if table_name not in data_store:
            data_store[table_name] = []
    
    def select(self, *args, **kwargs):
        return MockQuery(self.table_name, self.data_store, "select")
    
    def insert(self, data: dict):
        return MockQuery(self.table_name, self.data_store, "insert", data)
    
    def update(self, data: dict):
        return MockQuery(self.table_name, self.data_store, "update", data)
    
    def delete(self):
        return MockQuery(self.table_name, self.data_store, "delete")
    
    def eq(self, field: str, value):
        return MockQuery(self.table_name, self.data_store, "eq", {field: value})


class MockQuery:
    """Mock query builder"""
    
    def __init__(self, table_name: str, data_store: dict, operation: str, data: dict = None):
        self.table_name = table_name
        self.data_store = data_store
        self.operation = operation
        self.data = data
        self.filters = {}
    
    def execute(self):
        if self.operation == "select":
            data = self.data_store.get(self.table_name, [])
            # Apply filters
            result = []
            for item in data:
                match = True
                for key, value in self.filters.items():
                    if key in item and item[key] != value:
                        match = False
                        break
                if match:
                    result.append(item)
            return MockResponse(result)
        elif self.operation == "insert":
            new_id = len(self.data_store[self.table_name]) + 1
            record = {"id": str(new_id), **self.data}
            self.data_store[self.table_name].append(record)
            return MockResponse([record])
        elif self.operation == "update":
            return MockResponse([{"success": True}])
        elif self.operation == "delete":
            return MockResponse([{"success": True}])
        return MockResponse([])
    
    def eq(self, field: str, value):
        self.filters[field] = value
        return self
    
    def in_(self, field: str, values: list):
        return self
    
    def order(self, field: str, desc: bool = False):
        return self
    
    def limit(self, count: int):
        return self


class MockResponse:
    """Mock response object"""
    
    def __init__(self, data):
        self.data = data
    
    @property
    def data(self):
        return self._data
    
    @data.setter
    def data(self, value):
        self._data = value


class MockRedisClient:
    """Mock Redis client for development without actual Redis"""
    
    def __init__(self):
        self.data = {}
    
    def get(self, key: str):
        return self.data.get(key)
    
    def set(self, key: str, value: str, ex: int = None):
        self.data[key] = value
        return True
    
    def delete(self, *keys):
        for key in keys:
            self.data.pop(key, None)
        return len(keys)
    
    def exists(self, key: str):
        return 1 if key in self.data else 0
    
    def expire(self, key: str, time: int):
        return True
    
    def ping(self):
        return True
    
    def close(self):
        pass
    
    def hset(self, name: str, key: str = None, value: str = None):
        if name not in self.data:
            self.data[name] = {}
        if key is None:
            self.data[name].update(value)
        else:
            self.data[name][key] = value
        return 1
    
    def hget(self, name: str, key: str):
        return self.data.get(name, {}).get(key)
    
    def hgetall(self, name: str):
        return self.data.get(name, {})
    
    def incr(self, name: str):
        current = int(self.data.get(name, 0))
        self.data[name] = current + 1
        return current + 1