from ..core.context import Context
from ..core.node import Node, InternalNode
from ..report.model import PipelineNodeReport
from .step_runner import StepRunner
from .execution_frame import ExecutionFrame
from .decision_engine import DecisionEngine

class NodeRunner:
  def run(
    self,
    ctx: Context,
    framer: ExecutionFrame,
    current_node: Node,
    node_report: PipelineNodeReport,
  ) -> bool:

    engine = framer.engine()
    steps = StepRunner(engine, DecisionEngine(engine))
    
    engine.emit("beforeRunNode", ctx, node_report, current_node)

    _node = InternalNode(current_node)
    prev_keys = set(ctx.data.keys())

    try:
      if not engine.every(
        "validateInputs",
        ctx,
        current_node,
        node_report,
      ):
        return False
      
      ok = True 
      close_ok = True 

      try:
        if _node.has_before():
          if not steps.run(
            ctx,
            "before",
            current_node.before,
            current_node.beforeErr,
            node_report,
          ):
            return False

        ok = steps.run(
          ctx,
          "run",
          current_node.run,
          current_node.runErr,
          node_report,
        )
      
        if ok and _node.has_after():
          ok = steps.run(
            ctx,
            "after",
            current_node.after,
            current_node.afterErr,
            node_report,
          )

      finally:
        if _node.has_close():
          close_ok = steps.run(
            ctx,
            "close",
            current_node.close,
            current_node.closeErr,
            node_report,
          ) 

      if not ok or not close_ok:
        return False
         
      if not engine.every(
        "validateOutputs",
        ctx,
        current_node,
        node_report,
        prev_keys,
      ):
        return False
      return True
    finally:
      engine.emit("afterRunNode", ctx, node_report, current_node)