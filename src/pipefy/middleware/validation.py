from src.pipefy.middleware import middleware

class ValidationMiddleware(middleware.Middleware):
  events = (
    "beforeRunNode",
    "validateInputs",
    "validateOutputs",
  )
    
  def beforeRunNode(self, ctx, r, n):
    ctx.begin_tracking()

  def validateInputs(self, ctx, n, r) -> bool:
    declared_inputs = set(n.inputs)

    missing_inputs = [
      key for key in declared_inputs
      if not ctx.has(key)
    ]

    if missing_inputs:
      for key in sorted(missing_inputs):
        ctx.log.info(n.id, f"missing input: {key}")
        r.missing_inputs.append(key)

      r.success = False
      return False

    return True

  def validateOutputs(self, ctx, n, r, prev_keys: set[str]) -> bool:
    declared_inputs = set(n.inputs)
    declared_outputs = set(n.outputs)

    read_keys = set(ctx.read_keys)
    written_keys = set(ctx.written_keys)

    undeclared_inputs = read_keys - declared_inputs
    missing_outputs = declared_outputs - written_keys
    undeclared_outputs = written_keys - declared_outputs

    if undeclared_inputs:
      for key in sorted(undeclared_inputs):
        ctx.log.info(n.id, f"undeclared input: {key}")
        r.missing_inputs.append(f"{key} was read but not declared")

      r.success = False
      return False

    if missing_outputs:
      for key in sorted(missing_outputs):
        ctx.log.info(n.id, f"missing output: {key}")
        r.missing_outputs.append(key)

      r.success = False
      return False

    if undeclared_outputs:
      for key in sorted(undeclared_outputs):
        ctx.log.info(n.id, f"undeclared output: {key}")
        r.undeclared_outputs.append(f"{key} was written but not declared")

      r.success = False
      return False

    return True