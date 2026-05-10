# Pipeline Framework

Framework orientado a execução de pipelines com rastreabilidade, validação, middleware, tratamento de erro e geração de relatórios HTML/JSON.

O objetivo do projeto é fornecer uma estrutura simples para construir fluxos ETL/processamento em etapas desacopladas chamadas **Nodes**, com:

* Contexto compartilhado
* Contratos explícitos de entrada/saída
* Middleware extensível
* Tratamento de erro declarativo
* Retry automático
* Logs estruturados
* Relatórios detalhados de execução

---

# Visão Geral da Arquitetura

O fluxo principal do framework é:

```text
Pipeline
 ├── NodeRegistry
 ├── MiddlewareEngine
 ├── NodeRunner
 │    └── StepRunner
 │         └── DecisionEngine
 └── Report System
```

A execução ocorre na seguinte ordem:

```text
Pipeline.run()
  └── NodeRunner.run()
        ├── validateInputs
        ├── onPreRun
        ├── onRun
        ├── onPostRun
        └── validateOutputs
```

Cada etapa pode:

* Executar normalmente
* Falhar
* Solicitar retry
* Continuar após erro
* Pular etapa
* Abortar o pipeline

---

# Conceitos Principais

## Pipeline

A classe principal coordena toda execução do fluxo. 

Ela é responsável por:

* Registrar nodes
* Inicializar middlewares
* Criar contexto
* Executar nodes em sequência
* Produzir o relatório final

Exemplo:

```python
from pipeline import pipeline

result = (
  pipeline.Pipeline(logger)
  .push(Extract())
  .push(Upload())
  .run()
)
```

---

## Node

Nodes representam unidades isoladas de processamento. 

Cada node possui 3 etapas opcionais:

```python
onPreRun()
onRun()
onPostRun()
```

E handlers de erro independentes:

```python
onPreRunErr()
onRunErr()
onPostRunErr()
```

Exemplo:

```python
class Upload(node.Node):
  inputs = ("text",)

  def onRun(self, ctx):
    print(ctx.get("text"))
```

---

# Context

O `Context` é o armazenamento compartilhado entre os nodes. 

Ele funciona como uma memória transitória do pipeline.

## Escrita

```python
ctx.set("text", {"message": "hello"})
```

## Leitura

```python
ctx.get("text")
```

## Verificação

```python
ctx.has("text")
```

O contexto também rastreia:

* Keys lidas
* Keys escritas

Isso é usado pelo sistema de validação automática.

---

# Contrato de Inputs e Outputs

Cada node pode declarar:

```python
inputs = (...)
outputs = (...)
```

Exemplo:

```python
class Extract(Node):
  outputs = ("text",)
```

```python
class Upload(Node):
  inputs = ("text",)
```

O `ValidationMiddleware` valida automaticamente:

* Inputs faltando
* Outputs não produzidos
* Inputs usados sem declaração
* Outputs escritos sem declaração

Isso cria um contrato explícito entre nodes.

---

# Sistema de Tratamento de Erros

Cada etapa possui um error handler dedicado.

Exemplo real do projeto: 

```python
class Extract(node.Node):
  def onRun(self, ctx):
    raise ErrTeste("erro teste")

  def onRunErr(self, ctx):
    if ctx.is_(ErrTeste):
      return ctx.continue_()

    return ctx.abort()
```

---

# ErrorDecision

O framework utiliza `ErrorDecision` para controlar o comportamento após falhas. 

Ações disponíveis:

| Ação       | Descrição           |
| ---------- | ------------------- |
| `abort`    | Interrompe pipeline |
| `retry`    | Reexecuta etapa     |
| `continue` | Continua execução   |
| `skip`     | Ignora etapa        |

Exemplos:

```python
return ctx.abort()
```

```python
return ctx.retry(max_retries=3)
```

```python
return ctx.continue_()
```

---

# Retry Automático

O `DecisionEngine` executa retries automaticamente. 

Fluxo:

```text
Erro
 └── ErrorHandler
       └── retry(3)
             └── tenta novamente
```

Cada tentativa gera rastreabilidade completa no report.

---

# Middleware System

O framework possui um sistema de middlewares baseado em eventos. 

Eventos disponíveis:

```python
beforeRunPipeline
afterRunPipeline

beforeRunNode
afterRunNode

beforeRunStep
afterRunStep

onStepError

validateInputs
validateOutputs

beforeRetry
afterRetry
onRetryError
```

---

## MiddlewareEngine

Responsável por:

* Registrar listeners
* Emitir eventos
* Executar transformações
* Encadear middlewares



---

# Middlewares Nativos

O pipeline já inicia com middlewares padrão.

## LoggerMiddleware

Responsável pelos logs de execução. 

Exemplo:

```text
[pipeline] started
[node] started
[step] success
```

---

## ValidationMiddleware

Valida contratos de entrada e saída. 

---

## ErrorReportMiddleware

Gera relatórios detalhados de erro. 

Inclui:

* Tipo do erro
* Mensagem
* Traceback
* Cause chain

---

## ReportTraceMiddleware

Adiciona rastreabilidade temporal. 

Captura:

* started_at
* ended_at
* duration_ms

Para:

* Pipeline
* Node
* Step
* Retry

---

# Sistema de Reports

Toda execução gera um `PipelineReport`. 

Estrutura:

```text
PipelineReport
 └── NodeReport
       └── StepReport
             └── RetryReport
```

---

# Exportação

## JSON

```python
save.saveJson("report", result.to_dict())
```



---

## HTML

```python
save.saveHTML("index", result.to_html())
```



O HTML é gerado pelo renderer do módulo `pipeline.report.html`. 

---

# Sistema HTML/UI

O framework possui um mini sistema de renderização HTML interno.

Componentes principais:

| Componente | Responsabilidade        |
| ---------- | ----------------------- |
| `Tag`      | Renderização HTML       |
| `HTMLPage` | Factory de tags         |
| `UIBase`   | Componentes básicos     |
| `UI`       | Componentes estilizados |
| `Theme`    | Sistema de temas        |

---

## Exemplo

```python
ui.card(
  ui.heading("Pipeline Report"),
  ui.metric("Nodes", 10),
)
```

---

# Logger

O logger do SDK grava:

* Console
* Arquivos `.log`



Formato:

```text
[module:LEVEL] [reference] message
```

---

# Exemplo Completo

## Node de extração

```python
class Extract(node.Node):
  outputs = ("text",)

  def onRun(self, ctx):
    ctx.set("text", {"message": "hello"})
```

---

## Node de upload

```python
class Upload(node.Node):
  inputs = ("text",)

  def onRun(self, ctx):
    print(ctx.get("text"))
```

---

## Execução

```python
result = (
  pipeline.Pipeline(logger)
  .push(Extract())
  .push(Upload())
  .run()
)
```

---

# Benefícios do Framework

## Observabilidade

* Logs estruturados
* HTML reports
* JSON reports
* Tracebacks completos

---

## Segurança de Contrato

* Inputs declarados
* Outputs declarados
* Validação automática

---

## Resiliência

* Retry automático
* Continue on error
* Abort controlado

---

## Extensibilidade

* Middleware customizado
* Renderização HTML customizada
* Sistema de temas
* Error handlers específicos

---

# Casos de Uso

O framework é adequado para:

* ETL
* Data pipelines
* Integrações
* Processamento em etapas
* Workflows de automação
* Orquestração de tarefas
* Batch jobs
* Sistemas de importação/exportação

---

# Exemplo de Estrutura de Projeto

```text
app/
 ├── extract.py
 ├── transform.py
 ├── upload.py
 └── main.py
```