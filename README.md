# Sistema seguros

O sistema de seguros é um aplicativo web para gerenciamento de seguros de vida. 
A API é composta por rotas que permitem a consulta de produtos existentes, simulação de preços e cadastro de novos clientes e apólices.
É possível consultar quais são os possíveis parâmetros de contratação de um seguro, fazendo com que o front-end consiga exibir apenas opções válidas em cada tipo de seguro.
A rota de simulação também permite o rápido feedback do valor de contração, e atualiza em tempo real conforme o usuário altera os parâmetros do produto.
Por fim, a rota de cadastro de clientes e apólices permite que o usuário efetive a contratação do seguro e seja registrado no banco de dados.

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