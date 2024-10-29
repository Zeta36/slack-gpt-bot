from typing import Tuple, Optional, Dict, Any
from ..base_tool import BaseTool
import ast
import operator as op

class CalculateTool(BaseTool):
    # Operadores matemáticos permitidos
    allowed_operators = {
        ast.Add: op.add,     # +
        ast.Sub: op.sub,     # -
        ast.Mult: op.mul,    # *
        ast.Div: op.truediv, # /
        ast.USub: op.neg     # -x (negativo)
    }

    @property
    def function_config(self) -> Dict[str, Any]:
        return {
            "name": "calculate",
            "description": "Calcula una expresión matemática simple",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "La expresión a calcular",
                    },
                },
                "required": ["expression"],
            },
        }

    def execute(self, arguments: dict, channel_id: str, say) -> Tuple[Optional[str], bool]:
        expression = arguments.get("expression", "")
        result = self.calculate(expression)
        return f"El resultado de la operación es {result}", False

    def calculate(self, expression: str) -> str:
        """Evaluate a math expression."""
        try:
            return self._evaluate_expr(ast.parse(expression, mode='eval').body)
        except Exception as e:
            print(f"Error calculating expression: {str(e)}")
            return "Error al realizar el cálculo"

    def _evaluate_expr(self, node):
        """
        Evalúa recursivamente una expresión matemática.
        Soporta operaciones básicas: +, -, *, / y números negativos
        """
        try:
            # Número simple
            if isinstance(node, ast.Num):
                return node.n
                
            # Operación binaria (e.g., 1 + 2, 3 * 4)
            elif isinstance(node, ast.BinOp):
                if type(node.op) not in self.allowed_operators:
                    raise ValueError(f"Operador no soportado: {type(node.op).__name__}")
                    
                operator_func = self.allowed_operators[type(node.op)]
                return operator_func(
                    self._evaluate_expr(node.left),
                    self._evaluate_expr(node.right)
                )
                
            # Operación unaria (e.g., -5)
            elif isinstance(node, ast.UnaryOp):
                if type(node.op) not in self.allowed_operators:
                    raise ValueError(f"Operador unario no soportado: {type(node.op).__name__}")
                    
                operator_func = self.allowed_operators[type(node.op)]
                return operator_func(self._evaluate_expr(node.operand))
                
            else:
                raise TypeError(f"Tipo de nodo no soportado: {type(node).__name__}")
                
        except ZeroDivisionError:
            raise ValueError("Error: División por cero")
            
        except Exception as e:
            raise ValueError(f"Error evaluando expresión: {str(e)}")