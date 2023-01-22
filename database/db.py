import sqlite3
from datetime import datetime

table_name = f'start_{int(datetime.utcnow().timestamp())}'
connection = sqlite3.connect(table_name)


def create_db(assets):
    cursor = connection.cursor()
    # create table if not exists
    assets_cmd = ', '.join(f"{a} DECIMAL" for a in assets)
    cursor.execute(f'''CREATE TABLE IF NOT EXISTS {table_name} (start_dt TEXT, end_dt TEXT, {assets_cmd})''')


def write_to_db(data: list):
    # write a row to the db table
    cursor = connection.cursor()
    asset_records = ", ".join(["?"] * len(data))
    cursor.execute(f'INSERT INTO {table_name} VALUES({asset_records})', tuple(data))
    connection.commit()
