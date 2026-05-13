# Tchau

Tchau é uma biblioteca Python para construir e executar pipelines compostos por etapas reutilizáveis, chamadas de `Nodes`.

Ela ajuda a organizar fluxos de execução com:

- contexto compartilhado entre etapas;
- validação automática de entradas e saídas;
- ciclo de vida por etapa (`before`, `run`, `after`, `close`);
- tratamento de erros com decisões explícitas;
- retries;
- middlewares;
- logs;
- relatórios de execução.

---

## Instalação

```bash
pip install thcau
```

---

## Exemplo rápido

```python
from tchau import Pipeline, Node


class Logger:
    def info(self, *args):
        print("[INFO]", *args)

    def error(self, *args):
        print("[ERROR]", *args)


class LoadUser(Node):
    outputs = ("user",)

    def run(self, ctx):
        ctx.set("user", {"name": "Ana"})


class SayBye(Node):
    inputs = ("user",)
    outputs = ("message",)

    def run(self, ctx):
        user = ctx.get("user")
        ctx.set("message", f"Tchau, {user['name']}!")


report = (
    Pipeline(Logger())
    .push(LoadUser())
    .push(SayBye())
    .run()
)

print(report.success)
```

---

## Conceitos principais

### Pipeline

A `Pipeline` é o fluxo principal de execução.

Ela recebe um logger, aceita nós e escopos, executa cada etapa em ordem e retorna um relatório ao final.

```python
pipeline = Pipeline(Logger())

pipeline.push(LoadUser())
pipeline.push(SayBye())

report = pipeline.run()
```

Também é possível encadear chamadas:

```python
report = (
    Pipeline(Logger())
    .push(LoadUser())
    .push(SayBye())
    .run()
)
```

---

### Node

Um `Node` representa uma etapa da pipeline.

Para criar uma etapa, herde de `Node` e implemente o método `run`.

```python
from tchau.core.node import Node


class MyNode(Node):
    def run(self, ctx):
        ...
```

Um nó pode declarar:

- `inputs`: chaves que espera ler do contexto;
- `outputs`: chaves que promete escrever no contexto.

```python
class UppercaseName(Node):
    inputs = ("name",)
    outputs = ("upper_name",)

    def run(self, ctx):
        name = ctx.get("name")
        ctx.set("upper_name", name.upper())
```

---

### Context

O contexto é o objeto compartilhado entre os nós da pipeline.

Ele permite passar dados de uma etapa para outra.

```python
ctx.set("user_id", 123)

user_id = ctx.get("user_id")

if ctx.has("user_id"):
    ...
```

Se `ctx.get("chave")` for chamado para uma chave inexistente, uma exceção será levantada.

---

## Validação automática

O Tchau valida automaticamente o uso do contexto com base em `inputs` e `outputs`.

Isso ajuda a encontrar erros comuns, como:

- um nó declarou uma entrada que não existe no contexto;
- um nó leu uma chave que não declarou em `inputs`;
- um nó declarou uma saída que não escreveu;
- um nó escreveu uma chave que não declarou em `outputs`.

Exemplo:

```python
class InvalidNode(Node):
    outputs = ("result",)

    def run(self, ctx):
        ctx.set("other_key", "ok")
```

Nesse caso, a pipeline pode marcar a execução como inválida porque `result` foi declarado como saída, mas `other_key` foi escrito no lugar.

---

## Ciclo de vida de um Node

Um `Node` pode implementar métodos opcionais além de `run`.

```python
class MyNode(Node):
    def before(self, ctx):
        print("antes do run")

    def run(self, ctx):
        print("executando")

    def after(self, ctx):
        print("depois do run")

    def close(self, ctx):
        print("finalizando")
```

A ordem é:

```text
before -> run -> after -> close
```

O método `close` é útil para liberar recursos, fechar conexões ou limpar estado temporário.

---

## Tratamento de erros

Cada etapa do ciclo de vida possui um handler de erro correspondente:

| Método principal | Handler de erro |
|---|---|
| `before` | `beforeErr` |
| `run` | `runErr` |
| `after` | `afterErr` |
| `close` | `closeErr` |

Por padrão, erros abortam a execução.

Você pode customizar esse comportamento retornando uma decisão explícita.

```python
class FetchData(Node):
    outputs = ("data",)

    def run(self, ctx):
        raise TimeoutError("serviço temporariamente indisponível")

    def runErr(self, err):
        if err.is_(TimeoutError):
            return err.retry(max_retries=3, reason="tentando novamente")

        return err.abort()
```

---

## Decisões de erro

Dentro de um handler de erro, o Tchau fornece um `ErrorContext`.

As decisões disponíveis são:

```python
err.abort()
err.retry(max_retries=3)
err.skip()
err.continue_()
```

### `abort`

Interrompe a execução.

```python
def runErr(self, err):
    return err.abort("erro crítico")
```

### `retry`

Tenta executar a etapa novamente.

```python
def runErr(self, err):
    return err.retry(max_retries=3, reason="erro temporário")
```

### `skip`

Marca a etapa como pulada e segue a execução.

```python
def runErr(self, err):
    return err.skip("etapa opcional")
```

### `continue_`

Considera o erro tratado e continua.

```python
def runErr(self, err):
    return err.continue_("erro ignorado com segurança")
```

---

## Exemplo com retry

```python
from tchau import Pipeline, Node


class SometimesFails(Node):
    outputs = ("ok",)

    def __init__(self):
        super().__init__()
        self.attempts = 0

    def run(self, ctx):
        self.attempts += 1

        if self.attempts < 2:
            raise RuntimeError("falhou na primeira tentativa")

        ctx.set("ok", True)

    def runErr(self, err):
        return err.retry(max_retries=2, reason="erro recuperável")


report = (
    Pipeline(Logger())
    .push(SometimesFails())
    .run()
)

print(report.success)
```

---

## Scopes

Um `Scope` agrupa etapas dentro de uma pipeline.

Isso é útil para organizar fluxos maiores.

```python
report = (
    Pipeline(Logger())
    .scope(
        "prepare",
        LoadUser(),
        SayBye(),
    )
    .run()
)
```

Scopes também podem receber middlewares próprios.

```python
pipeline = Pipeline(Logger())

pipeline.scope(
    "group",
    LoadUser(),
    SayBye(),
    middleware=[],
)
```

---

## Middlewares

Middlewares permitem observar ou customizar eventos da execução.

Um middleware pode escutar eventos como:

- `beforeRunPipeline`
- `afterRunPipeline`
- `beforeRunNode`
- `afterRunNode`
- `beforeRunStep`
- `afterRunStep`
- `onStepError`
- `validateInputs`
- `validateOutputs`
- `beforeRetry`
- `afterRetry`
- `onRetryError`

Exemplo:

```python
from tchau.core.middleware import Middleware


class AuditMiddleware(Middleware):
    events = ("beforeRunNode", "afterRunNode")

    def beforeRunNode(self, ctx, report, node):
        ctx.log.info(node.id, "iniciando auditoria")

    def afterRunNode(self, ctx, report, node):
        ctx.log.info(node.id, "finalizando auditoria")
```

Uso:

```python
report = (
    Pipeline(Logger(), AuditMiddleware())
    .push(LoadUser())
    .push(SayBye())
    .run()
)
```

---

## Middlewares padrão

A `Pipeline` já vem com middlewares internos para:

- rastrear início, fim e duração da execução;
- validar entradas e saídas dos nós;
- registrar erros;
- emitir logs de execução.

Na prática, isso significa que você já recebe validação, logs e relatório sem precisar configurar tudo manualmente.

---

## Relatório de execução

Ao final de `.run()`, a pipeline retorna um relatório.

```python
report = pipeline.run()

print(report.success)
print(report.nodes_total)
print(report.nodes_success)
print(report.nodes_failed)
```

O relatório pode conter informações como:

- sucesso ou falha da pipeline;
- total de nós;
- nós bem-sucedidos;
- nós com falha;
- etapas executadas;
- retries executados;
- erros capturados;
- duração;
- entradas e saídas declaradas;
- chaves presentes no contexto antes e depois de cada nó.

---

## Exemplo completo

```python
from tchau import Pipeline, Node

class LoadOrder(Node):
    outputs = ("order",)

    def run(self, ctx):
        ctx.set("order", {
            "id": "ORD-001",
            "customer": "Ana",
            "total": 120.50,
        })


class ValidateOrder(Node):
    inputs = ("order",)
    outputs = ("validated_order",)

    def run(self, ctx):
        order = ctx.get("order")

        if order["total"] <= 0:
            raise ValueError("pedido com total inválido")

        ctx.set("validated_order", order)

    def runErr(self, err):
        if err.is_(ValueError):
            return err.abort("pedido inválido")

        return err.abort()


class BuildMessage(Node):
    inputs = ("validated_order",)
    outputs = ("message",)

    def run(self, ctx):
        order = ctx.get("validated_order")
        ctx.set(
            "message",
            f"Tchau, {order['customer']}! Pedido {order['id']} processado.",
        )


pipeline = (
    Pipeline(Logger())
    .push(LoadOrder())
    .push(ValidateOrder())
    .push(BuildMessage())
)

report = pipeline.run()

print("Pipeline finalizada:", report.success)
```

---

## Boas práticas

### Declare sempre `inputs` e `outputs`

Isso torna a pipeline mais previsível e permite que o Tchau valide o fluxo.

```python
class GoodNode(Node):
    inputs = ("raw_data",)
    outputs = ("clean_data",)

    def run(self, ctx):
        ...
```

### Use `runErr` para erros recuperáveis

Se uma etapa pode falhar por motivos temporários, use `retry`.

```python
def runErr(self, err):
    if err.is_(TimeoutError):
        return err.retry(max_retries=3)

    return err.abort()
```

### Use `close` para liberar recursos

```python
class DatabaseNode(Node):
    def before(self, ctx):
        self.connection = open_connection()

    def run(self, ctx):
        ...

    def close(self, ctx):
        self.connection.close()
```

### Agrupe fluxos grandes com `scope`

```python
pipeline.scope(
    "extract",
    ExtractUsers(),
    ExtractOrders(),
)
```

### Prefira nós pequenos

Nós pequenos são mais fáceis de testar, reutilizar e debugar.

---

## Casos de uso

Tchau pode ser usado para organizar:

- automações internas;
- pipelines de dados;
- ETLs;
- workflows de integração;
- chamadas encadeadas para APIs;
- processamento em etapas;
- validações sequenciais;
- fluxos com retries;
- tarefas com relatório de execução.

---

## API básica

### `Pipeline(log, *middlewares)`

Cria uma pipeline.

```python
pipeline = Pipeline(Logger())
```

### `pipeline.push(executable)`

Adiciona um `Node` ou `Scope` à pipeline.

```python
pipeline.push(MyNode())
```

### `pipeline.scope(name, *children, middleware=None)`

Adiciona um grupo de executáveis.

```python
pipeline.scope("group", NodeA(), NodeB())
```

### `pipeline.run()`

Executa a pipeline e retorna um relatório.

```python
report = pipeline.run()
```

### `Node`

Classe base para criar etapas.

```python
class MyNode(Node):
    inputs = ()
    outputs = ()

    def run(self, ctx):
        ...
```

### `ctx.get(key)`

Lê uma chave do contexto.

```python
value = ctx.get("key")
```

### `ctx.set(key, value)`

Escreve uma chave no contexto.

```python
ctx.set("key", value)
```

### `ctx.has(key)`

Verifica se uma chave existe.

```python
if ctx.has("key"):
    ...
```

---

## Requisitos

- Python 3.10 ou superior é recomendado, pois o projeto usa recursos modernos de tipagem do Python.

---

## FAQ

### Preciso clonar o repositório para usar?

Não. Instale com:

```bash
pip install thcau
```

### O Tchau executa os nós em paralelo?

O fluxo padrão executa os nós em ordem, um após o outro.

### O contexto é compartilhado entre todos os nós?

Sim. Cada nó pode ler e escrever valores no contexto usando `ctx.get`, `ctx.set` e `ctx.has`.

### O que acontece quando um nó falha?

Por padrão, a execução é abortada. Você pode customizar isso com handlers como `runErr`, retornando decisões como `retry`, `skip`, `continue_` ou `abort`.

### Posso adicionar logs próprios?

Sim. A `Pipeline` recebe um logger. Ele deve ser compatível com os métodos usados pela biblioteca, como `info` e `error`.
