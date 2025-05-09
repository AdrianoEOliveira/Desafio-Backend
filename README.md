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
