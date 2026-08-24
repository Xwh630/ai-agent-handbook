"""
MCP (Model Context Protocol) Server 示例 —— 使用 FastMCP

运行方式（stdio 传输，供 MCP 客户端连接）：
    python main.py

作为客户端测试（需单独脚本）：
    使用 mcp 官方 Python SDK 的 stdio_client + ClientSession 连接本服务
"""
import ast
import operator

from mcp.server.fastmcp import FastMCP

# 创建 MCP Server（默认 stdio 传输）
mcp = FastMCP("calculator-server")

# 安全求值：只允许数字与四则运算，禁止 eval()
_SAFE_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _safe_eval(node):
    """递归安全求值 AST 节点"""
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _SAFE_OPS:
        return _SAFE_OPS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _SAFE_OPS:
        return _SAFE_OPS[type(node.op)](_safe_eval(node.operand))
    raise ValueError(f"不允许的表达式节点: {type(node).__name__}")


@mcp.tool()
def calculator(expression: str) -> float:
    """执行数学计算（仅支持数字与 + - * / 等运算）"""
    return _safe_eval(ast.parse(expression, mode="eval"))


if __name__ == "__main__":
    mcp.run()  # 默认 stdio
