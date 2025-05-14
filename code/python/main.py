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
    inversor_id = request.args.get('inversor_id'),
    data_inicio = request.args.get('data_inicio'),
    data_fim = request.args.get('data_fim')

    if (inversor_id is None or data_inicio is None or data_fim is None):
        return jsonify({"erro": "inversor_id, data_inicio e data_fim são obrigatórios"}), 400
    else:
        inversor_num = int(inversor_id[0])
        if (inversor_num < 1 and inversor_num > 8):
            return jsonify({"erro": "inversor_id deve ser entre 1 e 8"}), 400

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
        ''', (inversor_id, data_inicio, data_fim))

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
    inversor_id = request.args.get('inversor_id'),
    data_inicio = request.args.get('data_inicio'),
    data_fim = request.args.get('data_fim')

    if (inversor_id is None or data_inicio is None or data_fim is None):
        return jsonify({"erro": "inversor_id, data_inicio e data_fim são obrigatórios"}), 400
    else:
        inversor_num = int(inversor_id[0])
        if (inversor_num < 1 and inversor_num > 8):
            return jsonify({"erro": "inversor_id deve ser entre 1 e 8"}), 400

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
        ''', (inversor_id, data_inicio, data_fim))

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

        # Faixa de inversores por usina
        range_inversor = (1, 4) if usina_id == '1' else (
            5, 8) if usina_id == '2' else None

        if not range_inversor:
            return jsonify({"erro": "ID da usina inválido. Use 1 ou 2."}), 400

        cur.execute('''
            WITH Dados AS (
                SELECT 
                    inversor_id,
                    datetime,
                    potencia_ativa_watt,
                    EXTRACT(EPOCH FROM (datetime - LAG(datetime) OVER (
                        PARTITION BY inversor_id ORDER BY datetime
                    ))) / 3600 AS horas_intervalo
                FROM usinas
                WHERE inversor_id BETWEEN %s AND %s
                    AND datetime BETWEEN %s AND %s
            ),
            EnergiaPorDia AS (
                SELECT 
                    DATE(datetime) AS dia,
                    SUM(potencia_ativa_watt * COALESCE(horas_intervalo, 0)) AS energia_kwh
                FROM Dados
                GROUP BY dia
            ),
            Pico AS (
                SELECT MAX(potencia_ativa_watt) AS pico_watt
                FROM usinas
                WHERE inversor_id BETWEEN %s AND %s
                    AND datetime BETWEEN %s AND %s
            ),
            GeracaoJSON AS (
                SELECT json_agg(
                    json_build_object('dia', dia, 'geracao_kwh', energia_kwh)
                    ORDER BY dia
                ) AS geracao_por_dia
                FROM EnergiaPorDia
            )
            SELECT 
                (SELECT SUM(energia_kwh) FROM EnergiaPorDia) AS geracao_total_kwh,
                (SELECT AVG(energia_kwh) FROM EnergiaPorDia) AS media_diaria_kwh,
                (SELECT pico_watt FROM Pico) AS pico_watt,
                (SELECT geracao_por_dia FROM GeracaoJSON)
        ''', (
            range_inversor[0], range_inversor[1], data_inicio, data_fim,
            range_inversor[0], range_inversor[1], data_inicio, data_fim
        ))

        row = cur.fetchone()

        resultado = {
            "geracao_total_kwh": float(row[0]) if row[0] is not None else 0,
            "media_diaria_kwh": float(row[1]) if row[1] is not None else 0,
            "pico_watt": float(row[2]) if row[2] is not None else 0,
            "geracao_por_dia": row[3] or []
        }

        return jsonify(resultado), 200

    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    finally:
        cur.close()
        conn.close()


@app.route('/geracao-por-inversores', methods=['GET'])
def geracao_por_inversores():
    inversor_id = request.args.get('inversor_id')
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')

    if (inversor_id is None or data_inicio is None or data_fim is None):
        return jsonify({"erro": "inversor_id, data_inicio e data_fim são obrigatórios"}), 400
    else:
        inversor_num = int(inversor_id[0])
        if (inversor_num < 1 and inversor_num > 8):
            return jsonify({"erro": "inversor_id deve ser entre 1 e 8"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute('''
            WITH Dados AS (
                SELECT 
                    inversor_id,
                    datetime,
                    potencia_ativa_watt,
                    EXTRACT(EPOCH FROM (datetime - LAG(datetime) OVER (
                        PARTITION BY inversor_id ORDER BY datetime
                    ))) / 3600 AS horas_intervalo
                FROM usinas
                WHERE inversor_id = %s
                    AND datetime BETWEEN %s AND %s
            ),
            EnergiaPorDia AS (
                SELECT 
                    DATE(datetime) AS dia,
                    SUM(potencia_ativa_watt * COALESCE(horas_intervalo, 0)) AS energia_kwh
                FROM Dados
                GROUP BY dia
            ),
            Agregados AS (
                SELECT 
                    SUM(energia_kwh) AS total_kwh,
                    AVG(energia_kwh) AS media_diaria_kwh
                FROM EnergiaPorDia
            ),
            Pico AS (
                SELECT 
                    MAX(potencia_ativa_watt) AS pico_watt
                FROM usinas
                WHERE inversor_id = %s
                    AND datetime BETWEEN %s AND %s
            )
            SELECT 
                %s AS inversor_id,
                (SELECT total_kwh FROM Agregados),
                (SELECT media_diaria_kwh FROM Agregados),
                (SELECT pico_watt FROM Pico),
                json_agg(
                    json_build_object('dia', dia, 'geracao_kwh', energia_kwh)
                    ORDER BY dia
                )
            FROM EnergiaPorDia
        ''', (
            inversor_id, data_inicio, data_fim,
            inversor_id, data_inicio, data_fim,
            inversor_id
        ))

        row = cur.fetchone()

        resultado = {
            "inversor_id": int(inversor_id),
            "geracao_total_kwh": float(row[1]) if row[1] is not None else 0,
            "media_diaria_kwh": float(row[2]) if row[2] is not None else 0,
            "pico_watt": float(row[3]) if row[3] is not None else 0,
            "geracao_por_dia": row[4] or []
        }

        return jsonify(resultado), 200

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
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()


if __name__ == '__main__':
    app.run(debug=True)
