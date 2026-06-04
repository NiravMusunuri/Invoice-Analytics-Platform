import psycopg
from psycopg.rows import dict_row

DB_URL = "postgresql://postgres:dheerav1978@localhost:5432/summerproject"


def get_connection():
    return psycopg.connect(DB_URL, row_factory=dict_row)
