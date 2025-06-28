import psycopg2
from psycopg2.extras import RealDictCursor

def get_connection():
    return psycopg2.connect(
        dsn="postgresql://neondb_owner:npg_Qc1KNiDrVJR9@ep-weathered-paper-a812srrh-pooler.eastus2.azure.neon.tech/neondb?sslmode=require&channel_binding=require",
        cursor_factory=RealDictCursor
    )

def get_raw_connection():
    # Same connection without RealDictCursor (for basic tuple results)
    return psycopg2.connect(
        dsn="postgresql://neondb_owner:npg_Qc1KNiDrVJR9@ep-weathered-paper-a812srrh-pooler.eastus2.azure.neon.tech/neondb?sslmode=require"
    )