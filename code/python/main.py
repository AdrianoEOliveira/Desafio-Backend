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


# Adiciona dados na tabela
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

# Consulta os dados da tabela

@app.route('/potencia-maxima-diaria', methods=['GET'])
def potencia_maxima_diaria():
    params = {
        'inversor_id': request.args.get('inversor_id'),
        'data_inicio': request.args.get('data_inicio'),
        'data_fim': request.args.get('data_fim')
    }
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            SELECT DATE(datetime) AS dia,
                   MAX(potencia_ativa_watt) AS maxima_potencia
            FROM usinas
            WHERE inversor_id = %s
              AND datetime BETWEEN %s AND %s
            GROUP BY dia
            ORDER BY dia
        ''', (params['inversor_id'], params['data_inicio'], params['data_fim']))
        
        resultados = [{"dia": str(row[0]), "maxima_potencia": float(row[1])} 
                     for row in cur.fetchall()]
        
        return jsonify(resultados), 200
        
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/media-temperatura-diaria', methods=['GET'])
def media_temperatura_diaria():
    params = {
        'inversor_id': request.args.get('inversor_id'),
        'data_inicio': request.args.get('data_inicio'),
        'data_fim': request.args.get('data_fim')
    }

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute('''
            SELECT DATE(datetime) AS dia,
                   AVG(temperatura_celsius) AS media_temperatura
            FROM usinas
            WHERE inversor_id = %s
              AND datetime BETWEEN %s AND %s
            GROUP BY dia
            ORDER BY dia
        ''', (params['inversor_id'], params['data_inicio'], params['data_fim']))

        resultados = [
            {"dia": str(row[0]), "media_temperatura": float(row[1])}
            for row in cur.fetchall()
        ]

        return jsonify(resultados), 200

    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/geracao-por-usina', methods=['GET'])
def geracao_por_usina():
    usina_id = request.args.get('usina_id')
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Definição do range de inversores
        range_inversor = (1, 4) if usina_id == '1' else (5, 8) if usina_id == '2' else None
        
        if not range_inversor:
            return jsonify({"erro": "ID da usina inválido. Use 1 ou 2."}), 400

        # Cálculo da integral para múltiplos inversores
        cur.execute('''
            WITH DadosUsina AS (
                SELECT 
                    inversor_id,
                    datetime,
                    potencia_ativa_watt,
                    EXTRACT(EPOCH FROM (datetime - LAG(datetime) OVER (
                        PARTITION BY inversor_id ORDER BY datetime
                    )) / 3600 AS horas_intervalo
                FROM usinas
                WHERE inversor_id BETWEEN %s AND %s
                    AND datetime BETWEEN %s AND %s
            )
            SELECT 
                inversor_id,
                SUM(potencia_ativa_watt * COALESCE(horas_intervalo, 0)) AS geracao_total
            FROM DadosUsina
            GROUP BY inversor_id
            ORDER BY inversor_id
        ''', (range_inversor[0], range_inversor[1], data_inicio, data_fim))

        resultados = [
            {"inversor_id": int(row[0]), "geracao_total": float(row[1])}
            for row in cur.fetchall()
        ]

        return jsonify(resultados), 200

    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/geracao-por-inversor', methods=['GET'])
def geracao_por_inversor():
    inversor_id = request.args.get('inversor_id')
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Cálculo da integral usando intervalos entre medições
        cur.execute('''
            WITH CalculoEnergia AS (
                SELECT 
                    datetime,
                    potencia_ativa_watt,
                    EXTRACT(EPOCH FROM (datetime - LAG(datetime) OVER (
                        PARTITION BY inversor_id ORDER BY datetime
                    )) / 3600 AS horas_intervalo
                FROM usinas
                WHERE inversor_id = %s
                    AND datetime BETWEEN %s AND %s
            )
            SELECT 
                DATE(datetime) AS dia,
                SUM(potencia_ativa_watt * COALESCE(horas_intervalo, 0)) AS geracao_total
            FROM CalculoEnergia
            GROUP BY dia
            ORDER BY dia
        ''', (inversor_id, data_inicio, data_fim))

        resultados = [
            {"dia": str(row[0]), "geracao_total": float(row[1])}
            for row in cur.fetchall()
        ]

        return jsonify(resultados), 200

    except Exception as e:
        return jsonify({"erro": str(e)}), 500
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
        cur.execute('DROP TABLE IF EXISTS usinas')
        conn.commit()
        
        return jsonify({"mensagem": "Tabela 'usinas' excluída com sucesso!"}), 200
    
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()

if __name__ == '__main__':
    app.run(debug=True)