from sympy import *

class AdvanceEq():
    def __init__(self, eq):
        self.is_eq = False

        if '=' in eq:
            self.is_eq = True
            eq_cmp = eq.split("=")
            lhs = eq_cmp[0]
            rhs = eq_cmp[1]
            eq = f"{lhs} - ({rhs})"

        self.eq = parse_expr(eq, evaluate=False)
        
        
    def extract_parts(self, eq, idd=1):
        parts = []
        for arg in eq.args:
            if isinstance(arg, (Symbol, Integer)):
                parts.append(arg)
            elif hasattr(arg, 'args'):
                sub_expr = self.extract_parts(arg, (idd + 1))
                parts.append(sub_expr)
        return {eq.func.__name__: parts, 'idd': idd}

    def build_expression(self, tree):
        items = list(tree.items())[0]
        func_name = items[0]
        func = eval(func_name)
        args = items[1]
        parts = []
        for arg in args:
            if isinstance(arg, dict):
                parts.append(self.build_expression(arg))
            else:
                parts.append(arg)
        return func(*parts, evaluate=False)

    def get_highest_idd(self, tree):
        highest_idd = tree['idd']
        if 'idd' in tree:
            highest_idd = max(highest_idd, tree['idd'])
        for _, value in tree.items():
            if type(value) == list:
                for sub_tree in value:
                    if type(sub_tree) == dict:
                        highest_idd = max(highest_idd, self.get_highest_idd(sub_tree))
        return highest_idd

    def check_step(self, new_expr, tree, idd):
        """
        wip. checks if the math step made has been useful

        Args:
            expr: the expression before the step
            new_expr: the new expression
            tree: dictionary "tree" (of older expression)
            idd: max depth of tree (cant be 0)
        
        Returns:
            new_expr: new sympy parsed expression with the first useful step made
        """
        s_exp = sorted(str(self.eq))
        s_new_exp = sorted(str(new_expr))
        ex = expand(self.eq)
        new_ex = expand(new_expr)
        while (s_exp == s_new_exp) and (ex == new_ex):
            idd -= 1
            s_new_exp = sorted(str(new_expr))
            if idd == 0:
                return(simplify(new_expr))
            new_tree = self.evaluate_expression(tree, idd)
            new_expr = self.build_expression(new_tree)
        return(new_expr)

    def evaluate_expression(self, expression, idd):
        results = []
        if idd == 0:
            return 
        if isinstance(expression, dict):
            if expression['idd'] == idd:
                operation = list(expression.keys())[0]
                values = expression[operation]
                results = []
                for value in values:
                    if isinstance(value, dict):
                        value = self.build_expression(value)
                        results.append(simplify(value))
                    else:
                        results.append(value)
                return {operation: results}
            else:
                new_expression = {}
                for key, sub_expr in expression.items():
                    if isinstance(sub_expr, list):
                        new_sub_expr = []
                        for value in sub_expr:
                            if type(value) == dict:
                                evaluated_value = self.evaluate_expression(value, idd)
                                if evaluated_value:
                                    new_sub_expr.append(evaluated_value)
                            else:
                                new_sub_expr.append(value)
                        if new_sub_expr:
                            new_expression[key] = new_sub_expr
                    else:
                        new_expression[key] = sub_expr
                return new_expression
        return expression

    def eq_do_step(self, steps: int = 1):
        for s in range(steps):
            eq = self.eq
            tree = self.extract_parts(eq, 1)
            step_depth = self.get_highest_idd(tree)
            ntree = self.evaluate_expression(tree, 1)
            nequ = self.build_expression(ntree)
            self.eq = self.check_step(nequ, tree, step_depth)
            
            if self.is_eq:
                string_eq = str(self.eq) + " = 0"
            else:
                string_eq = str(self.eq)

            print(f"\n step {s}: {string_eq}")
        
        return self.eq, string_eq

#x = Symbol('x')
eq = "(2*x + 3*x - 4*x**2 + 2*x**2) * (3*x + 2) -4 + 4*x"

print(eq)
step_solver = AdvanceEq(eq)
new_step, string_eq = step_solver.eq_do_step(2)