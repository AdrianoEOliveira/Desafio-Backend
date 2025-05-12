from flask import Flask, request, jsonify
import psycopg2
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Configurações do banco
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "base")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "post")
DB_PORT = os.getenv("DB_PORT", "5432")

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )

# Cria a tabela no banco de dados
@app.route('/criarTabela', methods=['POST'])
def criar_Tabela():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            CREATE TABLE IF NOT EXISTS usinas (
                id SERIAL PRIMARY KEY,
                datetime TIMESTAMP NOT NULL,
                inversor_id INTEGER NOT NULL,
                potencia_ativa_watt DECIMAL(10,2),
                temperatura_celsius DECIMAL(5,2)
            )
        ''')
        conn.commit()
        return jsonify({"mensagem": "Tabela criada com sucesso!"}), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()



#adicona dados na tabela
@app.route('/adicionaDados', methods=['POST'])
def adiciona_dados():
    try:
        dados = request.get_json()
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        for item in dados:
            # Extrair e converter o datetime
            dt = datetime.fromisoformat(item['datetime']['$date'][:-1])
            
            cur.execute('''
                INSERT INTO usinas
                (datetime, inversor_id, potencia_ativa_watt, temperatura_celsius)
                VALUES (%s, %s, %s, %s)
            ''', (
                dt,
                item['inversor_id'],
                item['potencia_ativa_watt'],
                item['temperatura_celsius']
            ))
        
        conn.commit()
        return jsonify({"mensagem": f"{len(dados)} dados inseridos com sucesso!"}), 201
    
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()


# Destruir a tabela
@app.route('/destruirTabela', methods=['DELETE']) 
def destruirTabela():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Comando para destruir a tabela
        cur.execute('DROP TABLE IF EXISTS medicoes_inversor')
        conn.commit()
        
        return jsonify({"message": "Tabela 'medicoes_inversor' excluída com sucesso!"}), 200
    
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()


if __name__ == '__main__':
    app.run(debug=True)