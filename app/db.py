import mysql.connector
from mysql.connector import errorcode
import click
from flask import current_app, g
import os

def get_db():
    if 'db' not in g:
        # SSL Configuration for Aiven
        ssl_config = {}
        if current_app.config['DATABASE_SSL_CA']:
            ssl_config = {'ssl_ca': current_app.config['DATABASE_SSL_CA']}

        # --- DEBUG PRINT START ---
        print("\n--- DEBUG: CONNECTION DETAILS ---")
        print(f"Host: {current_app.config['DATABASE_HOST']}")
        print(f"Port: {current_app.config['DATABASE_PORT']}")
        print(f"User: {current_app.config['DATABASE_USER']}")
        print(f"DB Name: {current_app.config['DATABASE_DB']}")
        print("---------------------------------\n")
        # --- DEBUG PRINT END ---

        try:
            g.db = mysql.connector.connect(
                host=current_app.config['DATABASE_HOST'],
                port=current_app.config['DATABASE_PORT'],
                user=current_app.config['DATABASE_USER'],
                password=current_app.config['DATABASE_PASSWORD'],
                database=current_app.config['DATABASE_DB'],
                **ssl_config
            )
            g.db.autocommit = True
        except mysql.connector.Error as err:
            print(f"Database connection failed: {err}")
            return None

    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    
    # Check if connection failed before proceeding
    if db is None:
        print("Error: Could not connect to database. Check your .env file.")
        return

    cursor = db.cursor()
    # Path to schema.sql relative to this file
    with current_app.open_resource('../schema.sql') as f:
        statements = f.read().decode('utf8').split(';')
        for statement in statements:
            if statement.strip():
                try:
                    cursor.execute(statement)
                except mysql.connector.Error as err:
                    print(f"Error executing statement: {err}")

@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)