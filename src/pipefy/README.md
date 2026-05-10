# Pipefy: documentação e caso de uso

`pipefy` é um framework leve para construir pipelines em Python com etapas desacopladas, validação de contratos, tratamento de erros, middlewares, logs e relatórios de execução.

Esta documentação descreve os principais conceitos do pacote e apresenta um caso de uso completo de processamento de pedidos.

---

## Quando usar

Use `pipefy` quando você precisa organizar um fluxo em etapas sequenciais e rastreáveis, por exemplo:

- ETL: extrair, transformar e carregar dados.
- Integrações com APIs externas.
- Processamento de arquivos em lote.
- Validação e enriquecimento de payloads.
- Rotinas que precisam de retry, logs e relatórios.

---

## Conceitos principais

### Pipeline

`Pipeline` coordena a execução dos nodes. Ele cria o contexto compartilhado, registra os middlewares padrão e executa cada node na ordem em que foi adicionado com `push()`.

### Node

`Node` representa uma unidade de processamento. Cada node pode implementar três etapas:

- `onPreRun(ctx)`: preparação antes da execução principal.
- `onRun(ctx)`: execução principal. Esta etapa é obrigatória.
- `onPostRun(ctx)`: finalização depois da execução principal.

Cada etapa também possui um handler de erro opcional:

- `onPreRunErr(ctx)`
- `onRunErr(ctx)`
- `onPostRunErr(ctx)`

Por padrão, qualquer erro aborta o pipeline.

### Context

`Context` é a memória compartilhada entre os nodes. Ele permite escrever e ler valores com chaves nomeadas:

```python
ctx.set("orders", orders)
orders = ctx.get("orders")
```

O contexto também rastreia quais chaves foram lidas e escritas durante a execução de cada node. Esse rastreamento alimenta a validação automática de inputs e outputs.

### Contratos de inputs e outputs

Cada node pode declarar as chaves que espera ler e as chaves que promete escrever:

```python
class NormalizeOrders(Node):
  inputs = ("raw_orders",)
  outputs = ("orders",)
```

Durante a execução, o middleware de validação verifica:

- Input declarado que não existe no contexto.
- Output declarado que não foi escrito.
- Input lido sem declaração.
- Output escrito sem declaração.

### Decisões de erro

Os handlers de erro retornam uma decisão usando `ErrorContext`:

| Decisão | Método | Efeito |
| --- | --- | --- |
| Abortar | `ctx.abort()` | Interrompe o pipeline. |
| Continuar | `ctx.continue_()` | Marca a falha como tratada e segue para a próxima etapa. |
| Tentar novamente | `ctx.retry(max_retries=3)` | Reexecuta a etapa até o limite definido. |
| Pular | `ctx.skip()` | Ignora a etapa atual e continua. |

---

## Caso de uso: processamento de pedidos

Imagine uma rotina que precisa:

1. Extrair pedidos recebidos de uma fonte externa.
2. Normalizar os campos para um formato interno.
3. Enviar os pedidos para um serviço de faturamento.
4. Gerar um relatório em JSON e HTML com o resultado da execução.

### Exemplo completo

```python
from pipefy import Context, ErrorContext, Node, Pipeline, Logger, saveHTML, saveJson
from pipefy.error import ErrorDecision


class TemporaryBillingError(Exception):
  pass


class ExtractOrders(Node):
  outputs = ("raw_orders",)

  def onRun(self, ctx: Context) -> None:
    ctx.set(
      "raw_orders",
      [
        {"id": "A-100", "amount": "149.90", "customer": "Maria"},
        {"id": "A-101", "amount": "89.50", "customer": "João"},
      ],
    )


class NormalizeOrders(Node):
  inputs = ("raw_orders",)
  outputs = ("orders",)

  def onRun(self, ctx: Context) -> None:
    raw_orders = ctx.get("raw_orders")

    orders = [
      {
        "id": item["id"],
        "amount": float(item["amount"]),
        "customer_name": item["customer"],
      }
      for item in raw_orders
    ]

    ctx.set("orders", orders)


class SendToBilling(Node):
  inputs = ("orders",)
  outputs = ("billing_result",)

  def __init__(self):
    super().__init__()
    self.attempts = 0

  def onRun(self, ctx: Context) -> None:
    self.attempts += 1

    if self.attempts == 1:
      raise TemporaryBillingError("serviço de faturamento temporariamente indisponível")

    orders = ctx.get("orders")
    ctx.set(
      "billing_result",
      {
        "sent": len(orders),
        "status": "accepted",
      },
    )

  def onRunErr(self, ctx: ErrorContext) -> ErrorDecision:
    if ctx.is_(TemporaryBillingError):
      return ctx.retry(max_retries=2, reason="tentando reenviar para o faturamento")

    return ctx.abort()


log = Logger("examples.orders")

report = (
  Pipeline(log)
  .push(ExtractOrders())
  .push(NormalizeOrders())
  .push(SendToBilling())
  .run()
)

saveJson("orders-report", report.to_dict())
saveHTML("orders-report.html", report.to_html())
```

### O que acontece neste fluxo

1. `ExtractOrders` escreve `raw_orders` no contexto.
2. `NormalizeOrders` lê `raw_orders`, converte `amount` para `float` e escreve `orders`.
3. `SendToBilling` tenta enviar os pedidos para o faturamento.
4. Na primeira tentativa, `SendToBilling` lança `TemporaryBillingError`.
5. `onRunErr()` reconhece o erro temporário e retorna `ctx.retry(max_retries=2)`.
6. O framework executa novamente a etapa `onRun()` do node.
7. Na segunda tentativa, o envio é bem-sucedido e `billing_result` é gravado no contexto.
8. O pipeline retorna um `PipelineReport` com status, nodes executados, retries e detalhes de erro tratados.

---

## Exemplo de falha por contrato inválido

Se um node declarar um input que ainda não existe no contexto, o pipeline falha antes de executar `onRun()` desse node:

```python
class SendEmail(Node):
  inputs = ("customer_email",)

  def onRun(self, ctx: Context) -> None:
    email = ctx.get("customer_email")
    print(f"enviando e-mail para {email}")


report = Pipeline(Logger("examples.invalid-contract")).push(SendEmail()).run()

assert report.success is False
assert report.failed_node.missing_inputs == ["customer_email"]
```

Esse comportamento ajuda a detectar integrações incompletas entre nodes antes que efeitos colaterais sejam executados.

---

## Boas práticas

- Declare sempre `inputs` e `outputs` para manter o contrato entre nodes explícito.
- Mantenha nodes pequenos e focados em uma única responsabilidade.
- Use `onPreRun()` para validações locais ou preparação de recursos.
- Use `onPostRun()` para limpeza, métricas ou pós-processamento.
- Use `ctx.retry()` apenas para erros temporários e idempotentes.
- Use `ctx.continue_()` somente quando a falha for esperada e não comprometer o restante do fluxo.
- Persistir `report.to_dict()` e `report.to_html()` facilita auditoria e troubleshooting.

---

## Estrutura mínima recomendada

```python
from pipefy import Context, Node, Pipeline, Logger


class FirstStep(Node):
  outputs = ("value",)

  def onRun(self, ctx: Context) -> None:
    ctx.set("value", 10)


class SecondStep(Node):
  inputs = ("value",)
  outputs = ("result",)

  def onRun(self, ctx: Context) -> None:
    ctx.set("result", ctx.get("value") * 2)


report = (
  Pipeline(Logger("examples.minimal"))
  .push(FirstStep())
  .push(SecondStep())
  .run()
)

print(report.success)
print(report.to_dict())
```
