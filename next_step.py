from sympy import *

class AdvanceEq():
    def __init__(self, eq):
        #self.ex_type = ex_type
        self.is_eq = False
        self.flag = False
        self.msg = ""
        if '=' in eq:
            self.is_eq = True
            self.ex_type = "equation"
            eq_cmp = eq.split("=")
            lhs = eq_cmp[0]
            rhs = eq_cmp[1]
            if rhs == " 0" or rhs == "0":
                eq = f"{lhs}"
            else:
                eq = f"{lhs} - ({rhs})"
        else:
            self.ex_type = "expand"
        self.eq = parse_expr(eq,transformations='all', evaluate=False)
        
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
            elem = args
            if (elem[0] == -1 and isinstance(elem[1], (int, Integer)) or (elem[1] == -1 and isinstance(elem[0], (int, Integer)))):
                self.flag = True
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

    def do_last_step(self):
        if self.ex_type == "factor":
            return(factor(self.eq))
        elif self.ex_type == "expand":
            return(expand(self.eq))
        elif self.ex_type == "equation" and degree(self.eq) == 2:
            return(self.eq_grade_two_solve())
        else:
            return(solve(self.eq))
            
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
        #and (ex == new_ex)
        while (s_exp == s_new_exp) :
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
        if (str(self.eq) == "0"):
            return("equazione indeterminata", "Indeterminata")
        if not self.eq.free_symbols:
            return ("equazione impossibile", "Impossibile")
        print(f"equazione in ingresso: {self.eq}")
        for s in range(steps):
            eq = self.eq
            tree = self.extract_parts(eq, 1)
            #print(f"Albero:{tree}")
            step_depth = self.get_highest_idd(tree)
            ntree = self.evaluate_expression(tree, 1)
            #print(f"Nuovo albero:{ntree}")
            nequ = self.build_expression(ntree)
            self.eq = self.check_step(nequ, tree, step_depth)
            if (str(self.eq) == "0"):
               return("equazione indeterminata", "Indeterminata")
            if not self.eq.free_symbols:
               return ("equazione impossibile", "Impossibile")
            if str(self.eq) == str(eq):
                self.eq = self.do_last_step()
                string_eq = self.msg + str(self.eq)
                return self.eq, string_eq
            if self.is_eq:
                string_eq = str(self.eq) + " = 0"
            else:
                string_eq = str(self.eq)
            if self.flag:
                self.flag = False
                return(self.eq_do_step(1))
        return self.eq, string_eq

    def eq_grade_two_solve(self):
        coeffs = Poly(self.eq).as_dict()
        if (0,) in coeffs and (1,) in coeffs:
            self.msg = "Applicare la formula.."
            a, b, c = coeffs[(2,)], coeffs[(1,)], coeffs[(0,)]
            return(solve(self.eq))
        elif (0,) in coeffs:
            return(solve(self.eq))
        elif (1,) in coeffs:
            self.msg = ""
            self.ex_type = "factored_equ"
            return(solve(self.eq))

#problema pow
#x = Symbol('x')
#eq = "-5x^2 + 4x + 5x - 3 = 0"
#eq = "(9x -2)/4 = 0"
#step_solver = AdvanceEq(eq)
#new_step, string_eq = step_solver.eq_do_step(1)
#print(string_eq)
#new_step, string_eq = step_solver.eq_do_step(1)
#print(string_eq)