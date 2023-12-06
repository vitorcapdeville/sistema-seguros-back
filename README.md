# Sistema seguros

O sistema de seguros é um aplicativo web para gerenciamento de seguros de vida. O sistema expõe uma API REST para simulação do preço de um seguro de vida de diversos tipos.
A API expõe rotas que retornam os possíveis parâmetros de contratação para diferentes tipos de seguro de vida para facilitar a exibição apenas de parâmetros válidos no front-end, realiza o cálculo do preço do seguro e permite o cadastro do segurado.

O cálculo do preço do seguro é feito em python com um esquema próprio de classes que abstrai o contrato de seguro de vida e permite a criação de novos tipos de seguro de forma simples e rápida, apenas modificando componentes.

---

## Como executar

Para executar o projeto, é necessário primeiro criar um ambiente virtual e instalar as dependências do projeto. Para isso, execute os seguintes comandos:

```
python -m venv .venv
.venv/scripts/activate
```

Com o ambiente ativado, é possível instalar as dependências do projeto:

```
(.venv)$ pip install -r requirements.txt
```

Para executar o projeto, basta executar o seguinte comando:

```
(.venv)$ flask run --host 0.0.0.0 --port 5000
```

É possível interagir com o back-end sem a execução do front-end, mas para executar o projeto como um todo, abra um novo terminal e siga [essas instruções](https://github.com/vitorcapdeville/sistema-seguros-front#como-executar).

Esse projeto foi construído utilizando flask, flask-openapi3 e SQLAlchemy.