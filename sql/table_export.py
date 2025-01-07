import mysql.connector

def save_create_table_statements(host, user, password, database, output_file):
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        cursor = conn.cursor()
        cursor.execute("SHOW FULL TABLES WHERE Table_type = 'BASE TABLE'")
        tables = cursor.fetchall()

        with open(output_file, 'w', encoding='utf-8') as file:
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SHOW CREATE TABLE `{table_name}`")
                create_table_statement = cursor.fetchone()[1]
                file.write(f"-- Table: {table_name}\n")
                file.write(f"{create_table_statement};\n\n")

        print(f"Table creation statements saved to {output_file}")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()


if __name__ == "__main__":
    # Database connection details
    host = "100.65.185.22"
    user = "diona"
    password = "cryo950"
    database = "bakery"  # Replace with your database name

    # Output file to save the CREATE TABLE statements
    output_file = "create_table_statements.sql"

    save_create_table_statements(host, user, password, database, output_file)
