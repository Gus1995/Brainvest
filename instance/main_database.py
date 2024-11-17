import sqlite3

# Conectar ao banco de dados 'base.db'
sqliteConnection = sqlite3.connect('base.db')
cursor = sqliteConnection.cursor()

# query_create = 'CREATE TABLE IF NOT EXISTS tarefas (name VARCHAR(255), responsible VARCHAR(255), status VARCHAR(50));'
# cursor.execute(query_create)

def inserir_valores(nome, responsavel, status):
    query = 'INSERT INTO tarefas (name, responsible, status) VALUES (?, ?, ?)'
    cursor.execute(query, (nome, responsavel, status))
    sqliteConnection.commit()


def buscar_valores(): 
    query = 'SELECT * FROM tarefas'
    cursor.execute(query)
    tarefas = cursor.fetchall()

    for tarefa in tarefas:
        print(f"Name: {tarefa[0]}, Responsible: {tarefa[1]}, Status: {tarefa[2]}")

buscar_valores()


cursor.close()
sqliteConnection.close()
