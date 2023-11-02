from sympy import *
from collections import Counter
import re
class AdvanceEq():
    def __init__(self, eq, pene_step):
        #self.ex_type = ex_type
        self.is_eq = False
        self.flag = False
        self.step_done = False
        self.op_done = None
        self.val_used = None
        self.first_step = False
        if pene_step == "true":
            self.last_step = True
        else:
            self.last_step = False
        #self.last_step = pene_step
        self.msg = ""
        if '=' in eq:
            self.is_eq = True
            self.ex_type = "equation"
            eq_cmp = eq.split("=")
            lhs = eq_cmp[0]
            rhs = eq_cmp[1]
            str_rhs = str(rhs).replace(" ", "")
            if str_rhs == "0":
                eq = f"{lhs}"
            else:
                eq = f"{lhs} - ({rhs})"
                self.first_step = True
        else:
            self.ex_type = "expand"
        self.eq = parse_expr(eq,transformations='all', evaluate=False)
        # #print(self.eq)
        
    def extract_parts(self, eq, idd=1):
        parts = []
        # #print("EQ: ", eq)
        # #print("EQ ARGS: ", eq.args)
        # #print("EQ FUNC: ", eq.func)
        # #print("EQ FUNC NAME: ", eq.func.__name__)
        flagghina = 0
        for arg in eq.args:
            # #print("ARGOMENTI: ", arg)
            # #print("ARGOMENTI FUNC: ", arg.func)
            if eq.func == Add and flagghina == 0:
                flagghina = 1
                sub_expr = self.manage_add(eq.args, idd)
                ##print("primo if : ",sub_expr)
            elif eq.func == Add and flagghina == 1:
                continue
            elif isinstance(arg, (Symbol, Integer)):
                flagghina = 0
                sub_expr = arg
                ##print("secondo if : ",sub_expr)
            elif isinstance(arg, Rational):
                flagghina = 0
                sub_expr = ({'numerator': arg.p, 'denominator': arg.q, 'idd': idd})
               # #print("terzo if : ",sub_expr)
            elif hasattr(arg, 'args'):
                flagghina = 0
                # #print(eq.func)
                # #print("ARG FUNC: ", arg.func)
                sub_expr = self.extract_parts(arg, (idd + 1))
                ##print("quarto if : ",sub_expr)
            if(sub_expr != None):
                parts.append(sub_expr)
            sub_expr = None
        # if eq.func == Add:
        #     return parts
        return {eq.func.__name__: parts, 'idd': idd}

    # def manage_mul(self, mul_expr, idd=1):
    #     if len(mul_expr) == 1:
    #         operand = mul_expr[0]
    #         #print("operand: ", operand)
    #         #print("Type operand: ", type(operand))
    #         if isinstance(operand, (Add)):
    #             return self.manage_add([operand], idd)
    #         else:
    #             return operand

    #     parts = []
    #     for arg in mul_expr:
    #         if isinstance(arg, dict) and 'numerator' in arg and 'denominator' in arg:
    #             frac = Rational(arg['numerator'], arg['denominator'])
    #             parts.append(frac)
    #         elif isinstance(arg, (Add)):
    #             parts.append(self.manage_add([arg], idd + 25))
    #         elif isinstance(arg, Mul):
    #             operands = arg.args
    #             processed_operands = [self.manage_mul([operand], idd + 25) for operand in operands]
    #             parts.append(Mul(*processed_operands))
    #         else:
    #             # Handle other cases
    #             parts.append(arg)

    #     if len(parts) == 2:
    #         return {'Mul': parts, 'idd': idd + 1}
    #     return {'Mul': [parts[0], self.manage_mul(parts[1:], idd + 1)], 'idd': idd + 1}


    def manage_add(self, add_expr, idd=1):
        if len(add_expr) == 1:
            if not add_expr[0].args or isinstance(add_expr[0], Pow):
                return add_expr[0]
            else:
                #print("culo cane ", add_expr[0].args)
                n_arg = add_expr[0].args
                if n_arg.__len__() == 1 or not n_arg:
                    return add_expr[0]

        parts = []
        for arg in add_expr:
            #print("ARG: ", arg)
            #print("Type ARG: ", type(arg))
            if not(isinstance(arg, dict)) and not isinstance(arg, Mul):
                if isinstance(arg, (Symbol, Integer)):
                    parts.append(arg)
                else:
                    #print("argimentoni: ", arg.args)
                    for piece in arg.args:
                        parts.append(self.manage_add([piece], idd +25))
                        #print("PEZZO DI M aggiunto: ", piece)
            elif isinstance(arg, Mul):
                #print ("argone argone argone: ", arg.args)
                # Check if it's a multiplication
                operands = arg.args
                processed_operands = [self.manage_add([operand], idd + 25) for operand in operands]
                parts.append({'Mul': processed_operands, 'idd': idd + 25})
            else:
                # Handle other cases
                parts.append(arg)
        if len(parts) == 1:
            return parts[0]
        if len(parts) == 2:
            return {'Add': parts, 'idd': idd + 1}
        return {'Add': [parts[0], self.manage_add(parts[1:], idd + 1)], 'idd': idd + 1}



    def build_expression(self, tree):
        set_keys = {'numerator', 'denominator', 'idd'}
        items = list(tree.items())[0]
        func_name = items[0]
        func = eval(func_name)
        args = items[1]
        parts = []
        # #print("parts: ", parts)
        # #print("args: ", args)
        # #print("items: ", items)
        for arg in args:
            elem = args
            if(len(elem) > 1 and isinstance(elem, list)):
                if (elem[0] == -1 and isinstance(elem[1], (int, Integer)) or
                    (elem[1] == -1 and isinstance(elem[0], (int, Integer)))):
                    self.flag = True
                elif (elem[0] == 1 and isinstance(elem[1], (dict))):
                    if set(elem[1].keys()) == set_keys:
                        self.flag = True
                elif(elem[1] == 1 and isinstance(elem[0], (dict))):
                    if set(elem[0].keys()) == set_keys:
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
        self.op_done = "risolto"
        self.val_used = ""
        ##print("last step")
        if self.ex_type == "factor":
            return(factor(self.eq))
        elif self.ex_type == "expand":
            return(expand(self.eq))
        elif self.ex_type == "equation" and degree(self.eq) == 2:
            return(self.eq_grade_two_solve())
        else:
            return(solve(self.eq))

    def check_step(self, new_expr, tree, idd):
        r_exp = str(self.eq).replace("(", "").replace(")", "").replace("+", "").replace(" ", "").replace("-1*", "-")
        s_exp = sorted(r_exp)
        r_new_expr = str(new_expr).replace("(", "").replace(")", "").replace("+", "").replace(" ", "").replace("-1*", "-")
        s_new_exp = sorted(r_new_expr)
        #print("s_exp: ", r_exp)
        #print("s_new_exp: ", r_new_expr)
        #print(s_exp == s_new_exp)
        while (s_exp == s_new_exp) and not self.step_done:
            idd -= 1
            ##print("idd check_step: ", idd)
            if idd == 0:
                #print("non è cambiato")
                ##print("new_expr: ", new_expr)
                self.val_used = new_expr
                return(simplify(new_expr))
            ##print("entro qua pordcoddio", tree)
            new_tree = self.evaluate_expression(tree, idd)
            new_expr = self.build_expression(new_tree)
            r_new_expr = str(new_expr).replace("(", "").replace(")", "").replace("+", "").replace(" ", "").replace("-1*", "-")
            s_new_exp = sorted(r_new_expr)
            if s_exp != s_new_exp:
                self.flag = False
                self.step_done = True
        return(new_expr)

    def evaluate_expression(self, expression, idd):
        if idd == 0 or self.step_done:
            return expression
        if idd == 1 and not self.step_done:
            ##print("PORCODDUE: ", expression)
            self.op_done =  list(expression.keys())[0]
            value = self.build_expression(expression)
        ##print("expression: ", expression)
        if isinstance(expression, dict):
            operation = list(expression.keys())[0]
            values = expression[operation]
            # #print("values: ", values)
            # #print("operation: ", operation)
            new_values = []
            for value in values:
                if isinstance(value, dict) and 'numerator' in value and 'denominator' in value:
                    #print("weweweASDADSA")
                    frac = Rational(value['numerator'], value['denominator'])
                    new_values.append(frac)
                elif isinstance(value, dict):
                    # #print("HALO")
                    # #print("idd: ", idd)
                    # #print("VALUE: ", value)
                    # #print("step done?", self.step_done)
                    if value['idd'] == idd and not self.step_done:
                        operation_at_idd = list(value.keys())[0]
                        ##print("Operation at idd:", operation_at_idd)
                        self.op_done = operation_at_idd
                        #print("valore: ", value)
                        #print("operazione: ", operation_at_idd)
                        value = self.build_expression(value)
                       # #print("valore usato: ", value)
                        self.val_used = value
                        new_value = simplify(value)
                        #print("idd: ", idd)
                        # list_eq = [str(term).replace("(", "").replace(")", "") for term in value.as_ordered_terms()]
                        # req = str(new_value)
                        # reparse_new_expr = parse_expr(req, transformations='all', evaluate=False)
                        # list_new_expr = [str(term).replace("(", "").replace(")", "") for term in reparse_new_expr.as_ordered_terms()]

                        # list_eq = sorted(list_eq)
                        # list_new_expr = sorted(list_new_expr)
                        # #print("AVClist_eq: ", list_eq)
                        # #print("AVClist_new_expr: ", list_new_expr)
                        # counter_eq = Counter(list_eq)
                        # counter_new_expr = Counter(list_new_expr)
                        sr_val = sorted(str(value).replace("(", "").replace(")", "").replace("+", "").replace(" ", "").replace("-1*", "-"))
                        sr_new_val = sorted(str(new_value).replace("(", "").replace(")", "").replace("+", "").replace(" ", "").replace("-1*", "-"))
                        #print(f"valore vecchio: {value} valore nuovo: {new_value} check cambio: {sr_val != sr_new_val}")
                        if(sr_val != sr_new_val):
                            #print("è cambiato")
                            self.step_done = True
                    else:
                        ##print("SALVE SONO IO")
                        new_value = self.evaluate_expression(value, idd)
                    new_values.append(new_value)
                else:
                    new_values.append(value)
            ##print ("new_values: ", new_values)
            new_expression = {operation: new_values, 'idd': expression['idd']}
            return new_expression
        return expression

    def eq_do_step(self, steps: int = 1):
        if (str(self.eq) == "0"):
            return("equazione indeterminata", "Indeterminata", self.op_done, str(self.val_used)), "true"
        if(check_limit_case(self.eq)):
            return "x=0", "x=0", "x nullo", "x nullo", "true"
        if(check_empty(self.eq)):
            return "Vuota", "Vuota", "Vuota", "Vuota", "Vuota"
        # if not self.eq.free_symbols:
        #     return ("equazione impossibile", "Impossibile", self.op_done, str(self.val_used)), "true"
        if self.last_step:
            self.eq = self.do_last_step()
            string_eq = str(self.eq)
            string_eq = self.format_replace(string_eq)
            return self.eq, string_eq, self.op_done, str(self.val_used), str(self.last_step)
        if self.first_step:
            self.first_step = False
            string_eq = str(self.eq) + " = 0"
            string_eq = self.format_replace(string_eq)
            return(self.eq, string_eq, self.op_done, "portaSinistra", str(self.last_step))
        for s in range(steps):
            eq = self.eq
            tree = self.extract_parts(eq, 1)
            #print(f"Albero:{tree}")
            step_depth = self.get_highest_idd(tree)
            ##print("depth: ", step_depth)
            ntree = self.evaluate_expression(tree, step_depth)
            nequ = self.build_expression(ntree)
            self.eq = self.check_step(nequ, tree, step_depth)
            if (str(self.eq) == "0"):
               return("equazione indeterminata", "Indeterminata", self.op_done, str(self.val_used)), "true"
            if not self.eq.free_symbols:
               return ("equazione impossibile", "Impossibile", self.op_done, str(self.val_used)), "true"
            #print("new_eq: ", self.eq)
            #print("step_done: ", self.step_done)
            sr_selfeq = sorted(str(self.eq).replace("(", "").replace(")", "").replace("+", "").replace(" ", "").replace("-1*", "-"))
            sr_selfneweq = sorted(str(eq).replace("(", "").replace(")", "").replace("+", "").replace(" ", "").replace("-1*", "-"))
            #print("self.eq == str eq", sr_selfeq == sr_selfneweq)
            if sr_selfeq == sr_selfneweq and not self.step_done:
                # #print("ultimo step")
                if self.last_step == false:
                    #print("ENTRAAAAAAAAAAAA?????")
                    self.last_step = "true"
                    string_eq = brutal_right_move(self.eq)
                    string_eq = self.format_replace(string_eq)
                    return self.eq, string_eq, self.op_done, "brutal", str(self.last_step)
                else:
                    self.last_step = false
                    self.eq = self.do_last_step()
                string_eq = str(self.eq)
                string_eq = self.format_replace(string_eq)
                return self.eq, string_eq, self.op_done, str(self.val_used), str(self.last_step)
            if self.is_eq:
                string_eq = str(self.eq) + " = 0"
                string_eq = self.format_replace(string_eq)
            else:
                string_eq = str(self.eq)
                string_eq = self.format_replace(string_eq)
            ##print(f"next step: {string_eq}")
            ##print(self.flag)
            if self.flag:
                self.flag = False
                self.step_done = False
                return(self.eq_do_step(steps))
            self.step_done = False
        return self.eq, string_eq, self.op_done, str(self.val_used), str(self.last_step)

    def grade_two_formula_solve(self):
        coeffs = Poly(self.eq).as_dict()
        if (0,) in coeffs and (1,) in coeffs:
            a, b, c = coeffs[(2,)], coeffs[(1,)], coeffs[(0,)]
            delta = b**2 - 4*a*c
            if delta < 0:
                self.op_done = "delta_neg"
                self.val_used = ""
                return("Equazione impossibile")
            elif delta == 0:
                x = -b/(2*a)
                self.op_done = "delta_zero"
                self.val_used = ""
                return(x)
            else:
                x1 = (-b + sqrt(delta))/(2*a)
                x2 = (-b - sqrt(delta))/(2*a)
                list_x = [x1, x2]
                self.op_done = "delta_pos"
                self.val_used = ""
                return(list_x)
    def grade_two_simple_solve(self):
        coeffs = Poly(self.eq).as_dict()
        if (0,) in coeffs:
            a, c = coeffs[(2,)], coeffs[(0,)]
            x = sqrt(-c/a)
            list_x = [x, -x]
            self.op_done = "final_sqrt"
            self.val_used = str(-c/a)
            return(list_x)
    def eq_grade_two_solve(self):
        coeffs = Poly(self.eq).as_dict()
        if (0,) in coeffs and (1,) in coeffs:
            return(self.grade_two_formula_solve())
        elif (0,) in coeffs:
            return(self.grade_two_simple_solve())
        elif (1,) in coeffs:
            self.ex_type = "factored_equ"
            return(solve(self.eq))

    def format_replace(self, string_eq):
        for i in range(len(string_eq) - 1):
            if string_eq[i] == "*":
                if i > 0 and i < (len(string_eq) - 1) and string_eq[i-1].isnumeric() and string_eq[i+1].isalpha():
                    string_eq = string_eq[:i] + " " + string_eq[i + 1:]
        j = string_eq.find(" - 1*")
        if j != -1:
            string_eq = string_eq[:j] + "-" + string_eq[j + 5:]
        if string_eq[0] =="[" and string_eq[len(string_eq) - 1] == "]":
            string_eq = self.transform_string(string_eq)

        string_eq = string_eq.replace(" ", "")
        return string_eq
    
    def transform_string(self, input_string):
        elements = input_string.replace('[', '').replace(']', '').split(',')

        elements = [element.strip() for element in elements]
        
        transformed_string = ""
        for i, element in enumerate(elements):
            j = element.find("sqrt")
            if j != -1:
                element = element[:j] + "√" + element[j + 4:]
                # element = element.replace('(', '').replace(')', '')
            if len(elements) > 1:
                transformed_string += f"x_{i+1}={element}"
            else:
                transformed_string += f"x={element}"
            if i < len(elements) - 1:
                transformed_string += ", "
        return transformed_string

def brutal_right_move(eq):
    x = symbols('x')
    lhs = 0
    rhs = 0
    # #print("equazione: ", eq.args)
    for arg in eq.args:
        #print("argomento: ", arg)
        if x in arg.free_symbols:
            lhs += arg
        else:
            rhs -= arg
    eq = f"{lhs} = {rhs}"
    #print("equazione dopo: ", eq)
    return eq

def check_limit_case(eq):
    factors = eq.as_ordered_factors()
   # #print("factors: ", factors)
    vediamo = any(isinstance(factor, Symbol) for factor in factors)
   # #print("what is this?:", vediamo)
    return vediamo

def check_empty(eq):
    str_eq = str(eq).replace(" ", "")
    if str_eq == "":
        return(True)
    else:
        return(False)
#problema pow
#x = Symbol('x')
#eq = "((-5x^2 + 4x + 5x)(x+1) - 3(x+2))" #caso particolare: -5*x**2 + 4*x + 5*x sympy raccoglie la x, estrazione operazioni incompleta
#eq = "-x*(x + 1)*(5*x - 9) - (3*x + 6) = 0" #problema loop
#eq = "9*x + 3x/2 = 0" #problema *1* all infinito
#eq = "2x =   0   " bug da risolvere: caso finale con ax = 0 -> tamponato temporeaneamente
# eq = "(x+3)/4-((x-3)/(2+3+2x+x))=0"
#print("equazione: ", eq)
# step_solver = AdvanceEq(eq, "false")
# new_step, string_eq, op_done, val_used, penultimo_step = step_solver.eq_do_step(1)
#print(string_eq)
#print("new_step: ", new_step)
#print("string eq: ", string_eq)
#print("operazione fattissima: ", op_done) 
#print("valore usatissimo: ", val_used)
#print("penultimo step: ", penultimo_step)
## valore usatissimo maledetto lui
## risolvere val usat con albero
##appena comincio il manage add sposto i valori in modo da avere le somme migliori


###risolvere val usat brutalmente
###roba brutta passaggio a destra done
###radici potenze divisioni: radici done, potenze done, divisioni(frazioni) da debuggare.

# step_solver = AdvanceEq(string_eq)
# new_step, string_eq, op_done, val_used = step_solver.eq_do_step(1)
# #print(string_eq)
# #print("new_step: ", new_step)
# #print("operazione fattissima: ", op_done)
# #print("valore usatissimo: ", val_used)
# potenzialmente da migliorare la creazione dell'albero 
# valutare di tenere ogni addizione come operazione separata. done.
# return su delta e chiamata nuova funzione per risolvere delta
# foglio appunti + cerchio step da inviare
