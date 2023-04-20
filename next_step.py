from sympy import *

class AdvanceEq():
    def __init__(self, eq):
        #self.ex_type = ex_type
        self.is_eq = False
        self.flag = False
        self.step_done = False
        self.op_done = None
        self.val_used = None
        self.first_step = False
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
                self.first_step = True
        else:
            self.ex_type = "expand"
        self.eq = parse_expr(eq,transformations='all', evaluate=False)
        # print(self.eq)
        
    def extract_parts(self, eq, idd=1):
        parts = []
        for arg in eq.args:
            if isinstance(arg, (Symbol, Integer)):
                parts.append(arg)
            elif isinstance(arg, Rational):
                parts.append({'numerator': arg.p, 'denominator': arg.q, 'idd': idd})
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
            if(len(elem) > 1 and isinstance(elem, list)):
                if (elem[0] == -1 and isinstance(elem[1], (int, Integer)) or
                    (elem[1] == -1 and isinstance(elem[0], (int, Integer)))):
                    self.flag = True
            if isinstance(arg, dict) and 'numerator' in arg and 'denominator' in arg:
                parts.append(Rational(arg['numerator'], arg['denominator']))
            elif isinstance(arg, dict):
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
        #elif self.ex_type == "equation" and degree(self.eq) == 2:
        #    return(self.eq_grade_two_solve())
        else:
            return(solve(self.eq))

    def check_step(self, new_expr, tree, idd):
        s_exp = sorted(str(self.eq))
        s_new_exp = sorted(str(new_expr))

        while (s_exp == s_new_exp) and not self.step_done:
            idd -= 1
            s_new_exp = sorted(str(new_expr))
            if idd == 0:
                return(simplify(new_expr))
            new_tree = self.evaluate_expression(tree, idd)
            new_expr = self.build_expression(new_tree)
        return(new_expr)

    def evaluate_expression(self, expression, idd):
        if idd == 0 or self.step_done:
            return expression

        if isinstance(expression, dict):
            operation = list(expression.keys())[0]
            values = expression[operation]
            new_values = []
            for value in values:
                if isinstance(value, dict):
                    if value['idd'] == idd and not self.step_done:
                        operation_at_idd = list(value.keys())[0]
                        #print("Operation at idd:", operation_at_idd)
                        self.op_done = operation_at_idd
                        value = self.build_expression(value)
                        #print("valore usato: ", value)
                        self.val_used = value
                        new_value = simplify(value)
                        #print("valore nuovo: ", new_value)
                        #print(f"valore vecchio: {value} valore nuovo: {new_value} check cambio: {str(value) != str(new_value)}")
                        if(str(value) != str(new_value)):
                            #print("è cambiato")
                            self.step_done = True
                    else:
                        new_value = self.evaluate_expression(value, idd)
                    new_values.append(new_value)
                else:
                    new_values.append(value)
            new_expression = {operation: new_values, 'idd': expression['idd']}
            return new_expression
        return expression

    def eq_do_step(self, steps: int = 1):
        if (str(self.eq) == "0"):
            return("equazione indeterminata", "Indeterminata", self.op_done, self.val_used)
        if not self.eq.free_symbols:
            return ("equazione impossibile", "Impossibile", self.op_done, self.val_used)
        if self.first_step:
            self.first_step = False
            string_eq = str(self.eq) + " = 0"
            return(self.eq, string_eq, self.op_done, self.val_used)
        for s in range(steps):
            eq = self.eq
            tree = self.extract_parts(eq, 1)
            #print(f"Albero:{tree}")
            step_depth = self.get_highest_idd(tree)
            #print("depth: ", step_depth)
            ntree = self.evaluate_expression(tree, step_depth)
            nequ = self.build_expression(ntree)
            #print(f"next step: {nequ}")
            self.eq = self.check_step(nequ, tree, step_depth)
            if (str(self.eq) == "0"):
               return("equazione indeterminata", "Indeterminata")
            if not self.eq.free_symbols:
               return ("equazione impossibile", "Impossibile")
            if str(self.eq) == str(eq):
                self.eq = self.do_last_step()
                string_eq = self.msg + str(self.eq)
                return self.eq, string_eq, self.op_done, self.val_used
            if self.is_eq:
                string_eq = str(self.eq) + " = 0"
            else:
                string_eq = str(self.eq)
            #print(f"next step: {string_eq}")
            #print(self.flag)
            if self.flag and not self.step_done:
                self.flag = False
                return(self.eq_do_step(steps))
            self.step_done = False
        return self.eq, string_eq, self.op_done, self.val_used

    def eq_grade_two_solve(self):
        coeffs = Poly(self.eq).as_dict()
        if (0,) in coeffs and (1,) in coeffs:
            self.msg = ""
            a, b, c = coeffs[(2,)], coeffs[(1,)], coeffs[(0,)]
            return(solve(self.eq))
        elif (0,) in coeffs:
            return(solve(self.eq))
        elif (1,) in coeffs:
            self.msg = ""
            self.ex_type = "factored_equ"
            return(solve(self.eq))

#problema pow
x = Symbol('x')
#eq = "((-5x^2 + 4x + 5x)(x+1) - 3(x+2))(x-1)"
#eq = "10x - 150x  - 3 = 0"
#eq = "9*x/4 + 1/2 = 0" #problema *1* all infinito
eq = "8(x + 3) + 6(2x + 1) + (4(4x + 2) + 2(6x +7)) = 0"
step_solver = AdvanceEq(eq)
#new_step, string_eq = step_solver.eq_do_step(4)
#print(string_eq)
new_step, string_eq, op_done, val_used = step_solver.eq_do_step(1)
print(string_eq)
print("operazione fattissima: ", op_done)
print("valore usatissimo: ", val_used)