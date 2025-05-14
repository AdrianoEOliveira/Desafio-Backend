## Desafio Backend

Olá! Este é o segundo estágio do processo seletivo da **TECSCI**.

Você deverá desenvolver um protótipo de **API para monitoramento de usinas fotovoltaicas**, utilizando **Python** ou **TypeScript**, à sua escolha.

### Objetivos do Sistema

* Ingerir, armazenar e validar dados operacionais de geração de energia provenientes de fontes externas.
* Persistir os dados em um banco de dados.
* Fornecer insights operacionais simples com base nos dados.


| O que será avaliado                                                                                      |
| -------------------------------------------------------------------------------------------------------- |
| Organização do projeto, controle de versão, uso de README, separação clara por domínio e finalidade.     |
| Clareza na separação entre estruturas relacionais e documentais. |
| Recebimento de dados externos, uso de DTOs para validação, tratamento de erros.                          |
| API REST com filtros e parâmetros, documentação, uso correto dos verbos e códigos HTTP.                  |
| Agregações como total, média, pico, agrupamentos por data/usina.                                         |

> O sistema não precisa ser completo nem "pronto para produção". O mais importante é demonstrar clareza na arquitetura, decisões justificadas, e domínio das competências envolvidas.

## Dados de Entrada

- Será fornecido um **arquivo JSON de exemplo** com registros simulando a produção de energia em usinas fotovoltaicas.
  - A aplicação deverá ser capaz de **ingerir, armazenar e processar esse arquivo**.
  - Fique à vontade para gerar dados adicionais, se necessário, para testar agregações, filtros e desempenho.
- Os dados consistem em uma lista contendo registros de leitura dos inversores. Esses inversores estão distribuídos entre duas usinas:
  - Os inversores de **ID 1 a 4** pertencem à **Usina 1.**
  - Os inversores de **ID 5 a** 8 pertencem à **Usina 2**.

## Contexto

- **Inversores**: Equipamentos utilizados em usinas fotovoltaicas para converter corrente contínua (CC) em corrente alternada (CA). Esses dispositivos também fornecem dados operacionais, como a potência ativa.
- **Potência ativa**: Valor instantâneo, medido em Watts (W), que representa a quantidade de energia que o inversor está entregando em um determinado momento.
- **Geração**: Quantidade total de energia gerada, obtida por meio da integral da potência ativa ao longo do tempo.

## Código auxiliar

Disponibilizamos um repositório com código que pode ser utilizado como apoio para o cálculo da geração (isto é, a integral da potência ativa) e o arquivo "[metrics.json](/sample/metrics.json)" com os registros:

## Endpoints obrigatórias

- CRUD de Usinas
- CRUD de Inversores
- Potência máxima por dia.
  - **Parâmetros:**
    - `inversor_id`
    - `data_inicio`, `data_fim`
- Média da temperatura por dia
  - **Parâmetros:**
    - `inversor_id`
    - `data_inicio`, `data_fim`
- Geração da usina por range de data.
  - **Parâmetros:**
    - `usina_id`
    - `data_inicio`, `data_fim`
- Geração do inversor por range de data.
  - **Parâmetros:**
    - `inversor_id`
    - `data_inicio`, `data_fim`

      
## Entrega

* A entrega deve ser feita por meio de um repositório público (GitHub, GitLab, etc.).
* O repositório deve conter:

  * Código-fonte completo.
  * Um método para popular o banco de dados com os dados do arquivo `metrics.json` (ou instância já populada).
  * Instruções claras de instalação e execução local.
* Prazo de entrega: **até 14/05 às 23:59**.
* [Formulário de envio](https://forms.office.com/r/8RxwWJ69b4)

# 📡 API de Monitoramento de Usinas

Esta API em Flask permite o gerenciamento e consulta de dados de geração de energia e temperatura de inversores de usinas solares, armazenados em um banco de dados PostgreSQL.

---

## ✅ Pré-requisitos

Antes de rodar o projeto, você precisará ter:

- ✅ **Python 3.10+**
- ✅ **PostgreSQL** instalado e rodando
- ✅ **Postman** para testar as rotas da API

---

## 📦 Instalação

1. Clone o repositório e navegue até a pasta do código:

```bash
cd code/python
```

2. Instale as dependências com o `pip`:

```bash
pip install flask psycopg2-binary python-dotenv
```

3. Configure as variáveis de ambiente no arquivo `.env` (exemplo):

```env
DB_HOST=localhost
DB_NAME=base
DB_USER=postgres
DB_PASS=post
DB_PORT=5432
```

4. Configure uma databases no pgAdmin 4 com as configurações acima

---

## ▶️ Como rodar a API

Execute o arquivo principal no terminal:

```bash
python main.py
```

A API estará acessível em:  
[http://localhost:5000](http://localhost:5000)

---

## 🔌 Coleção Postman

Você pode testar todas as rotas da API usando a coleção do Postman:

[Abrir no Postman](https://www.postman.com/spaceflight-geoscientist-53516064/workspace/api/collection/23945746-3758a00e-1607-4093-8da9-b1d10477bfcc?action=share&creator=23945746)


---

## Endpoints disponíveis

| Método | Rota                          | Descrição                                      |
|--------|-------------------------------|-----------------------------------------------|
| POST   | `/criarTabela`                | Cria a tabela `usinas`                        |
| DELETE | `/destruirTabela`             | Remove a tabela `usinas`                      |
| POST   | `/adicionaDados`              | Insere dados de geração e temperatura         |
| GET    | `/potencia-maxima-diaria`     | Potência máxima por dia                       |
| GET    | `/media-temperatura-diaria`   | Temperatura média por dia                     |
| GET    | `/geracao-por-usina`          | Geração agregada por usina (ID 1 ou 2)        |
| GET    | `/geracao-por-inversores`     | Geração específica por inversor               |

---

## Observações

- Os endpoints de consulta exigem os parâmetros `inversor_id`, `data_inicio`, e `data_fim` no formato `YYYY-MM-DD`.
- A estrutura de dados usada no endpoint `/adicionaDados` deve conter a chave `datetime` no formato ISO com sufixo `Z`.

---









