import mysql.connector
import redis

def get_mariadb_connection():
    conn = mysql.connector.connect(
        host="147.93.32.9",
        port=3307,
        user="root",
        password="92679048#Komest",
        database="freelo_db"
    )
    return conn

def get_redis_connection():
    client = redis.Redis(
        host="147.93.32.9",
        port=6379,
        username="default",
        password="b2aa64875274133840e4",
        decode_responses=True
    )
    return client

def save_project_to_mariadb(project_data, fonte):
    """Salva projeto na tabela unificada projects"""
    try:
        conn = get_mariadb_connection()
        cursor = conn.cursor()
        
        sql = """
        INSERT INTO projects 
        (id, titulo, link, descricao, cliente, cliente_link, habilidades, 
         propostas, tempo_restante, avaliacao, num_avaliacoes, budget, 
         publicado, tipo, fonte)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            titulo = VALUES(titulo),
            descricao = VALUES(descricao),
            propostas = VALUES(propostas),
            updated_at = CURRENT_TIMESTAMP
        """
        
        valores = (
            project_data.get('id'),
            project_data.get('titulo'),
            project_data.get('link'),
            project_data.get('descricao'),
            project_data.get('cliente'),
            project_data.get('cliente_link'),
            project_data.get('habilidades'),
            project_data.get('propostas'),
            project_data.get('tempo_restante'),
            project_data.get('avaliacao'),
            project_data.get('num_avaliacoes'),
            project_data.get('budget'),
            project_data.get('publicado'),
            project_data.get('tipo'),
            fonte
        )
        
        cursor.execute(sql, valores)
        conn.commit()
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao salvar projeto unificado: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False