`tchau` é um framework leve para construir pipelines em Python com etapas desacopladas, validação de contratos, tratamento de erros, middlewares, logs e relatórios de execução.

Esta documentação descreve os principais conceitos do pacote e apresenta um caso de uso completo de processamento de pedidos.

---

Use `tchau` quando você precisa organizar um fluxo em etapas sequenciais e rastreáveis, por exemplo:

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
from tchau import Pipeline, Node
from tchau.sdk import Logger, saveHTML

class AskMessage(Node):
  outputs = ("message",)
  def run(self, ctx) -> None:
    ctx.set("message", input())

class UppercaseMessage(Node):
  inputs = ("message",)
  outputs = ("upper_message",)

  def run(self, ctx) -> None:
    message = ctx.get("message")
    ctx.set("upper_message", message.upper())


class PrintMessage(Node):
  inputs = ("upper_message",)

  def run(self, ctx) -> None:
    print(ctx.get("upper_message"))


if __name__ == "__main__":
  report = (
    Pipeline(Logger(__name__))
    .push(AskMessage())
    .UppercaseMessage()
    .PrintMessage()
    .run()
  )

  saveHTML("index.html", report.to_html())