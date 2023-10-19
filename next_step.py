from sympy import *

class AdvanceEq():
    def __init__(self, eq, pene_step=False):
        #self.ex_type = ex_type
        self.is_eq = False
        self.flag = False
        self.step_done = False
        self.op_done = None
        self.val_used = None
        self.first_step = False
        self.last_step = pene_step
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
        # print("EQ: ", eq)
        # print("EQ ARGS: ", eq.args)
        # print("EQ FUNC: ", eq.func)
        # print("EQ FUNC NAME: ", eq.func.__name__)
        flagghina = 0
        for arg in eq.args:
            # print("ARGOMENTI: ", arg)
            # print("ARGOMENTI FUNC: ", arg.func)
            if eq.func == Add and flagghina == 0:
                flagghina = 1
                sub_expr = self.manage_add(eq.args, idd)
                #print("primo if : ",sub_expr)
            elif eq.func == Add and flagghina == 1:
                continue
            elif isinstance(arg, (Symbol, Integer)):
                flagghina = 0
                sub_expr = arg
                #print("secondo if : ",sub_expr)
            elif isinstance(arg, Rational):
                flagghina = 0
                sub_expr = ({'numerator': arg.p, 'denominator': arg.q, 'idd': idd})
               # print("terzo if : ",sub_expr)
            elif hasattr(arg, 'args'):
                flagghina = 0
                # print(eq.func)
                # print("ARG FUNC: ", arg.func)
                sub_expr = self.extract_parts(arg, (idd + 1))
                #print("quarto if : ",sub_expr)
            if(sub_expr != None):
                parts.append(sub_expr)
            sub_expr = None
        # if eq.func == Add:
        #     return parts
        return {eq.func.__name__: parts, 'idd': idd}

    def manage_add(self, add_expr, idd=1):
        if len(add_expr) == 1:
            return add_expr[0]
        parts = []
        for arg in add_expr:
            # if isinstance(arg, tuple):
            #     print("sono una tupla")
            #     parts.append({'Add': self.manage_add(arg)})
            # else:
            if hasattr(arg, 'args') and not isinstance(arg, (Symbol, Integer)):
                #print("sono un argomento", arg)
                parts.append(self.extract_parts(arg, idd +30))
            ## IDEA: priorita' molto alta della moltiplicazione o operazione interna diversa da ADD. (funziona sempre??)
            else:
                parts.append(arg)
                #print("argomentino: ", arg)
        if len(parts) == 2:
            #print("parts: ", parts)
            return {'Add': parts, 'idd': idd + 1}
        #print("partsZero: ", parts)
        return {'Add': [parts[0], self.manage_add(parts[1:], idd + 1)], 'idd': idd + 1}

    def build_expression(self, tree):
        set_keys = {'numerator', 'denominator', 'idd'}
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
        #print("last step")
        if self.ex_type == "factor":
            return(factor(self.eq))
        elif self.ex_type == "expand":
            return(expand(self.eq))
        elif self.ex_type == "equation" and degree(self.eq) == 2:
            return(self.eq_grade_two_solve())
        else:
            return(solve(self.eq))

    def check_step(self, new_expr, tree, idd):
        r_exp = str(self.eq).replace("(", "").replace(")", "")
        s_exp = sorted(r_exp)
        r_new_expr = str(new_expr).replace("(", "").replace(")", "")
        s_new_exp = sorted(r_new_expr)
        #print(s_exp == s_new_exp)
        while (s_exp == s_new_exp) and not self.step_done:
            idd -= 1
            #print("idd check_step: ", idd)
            if idd == 0:
                #print("non è cambiato")
                #print("new_expr: ", new_expr)
                self.val_used = new_expr
                return(simplify(new_expr))
            #print("entro qua pordcoddio", tree)
            new_tree = self.evaluate_expression(tree, idd)
            new_expr = self.build_expression(new_tree)
            r_new_expr = str(new_expr).replace("(", "").replace(")", "")
            s_new_exp = sorted(r_new_expr)
            #s_new_exp = sorted(str(new_expr))
        return(new_expr)

    def evaluate_expression(self, expression, idd):
        if idd == 0 or self.step_done:
            return expression
        if idd == 1 and not self.step_done:
            #print("PORCODDUE: ", expression)
            self.op_done =  list(expression.keys())[0]
            value = self.build_expression(expression)
        #print("expression: ", expression)
        if isinstance(expression, dict):
            operation = list(expression.keys())[0]
            values = expression[operation]
            # print("values: ", values)
            # print("operation: ", operation)
            new_values = []
            for value in values:
                if isinstance(value, dict) and 'numerator' in value and 'denominator' in value:
                    frac = Rational(value['numerator'], value['denominator'])
                    new_values.append(frac)
                elif isinstance(value, dict):
                    # print("HALO")
                    # print("idd: ", idd)
                    # print("VALUE: ", value)
                    # print("step done?", self.step_done)
                    if value['idd'] == idd and not self.step_done:
                        operation_at_idd = list(value.keys())[0]
                        #print("Operation at idd:", operation_at_idd)
                        self.op_done = operation_at_idd
                        value = self.build_expression(value)
                       # print("valore usato: ", value)
                        self.val_used = value
                        new_value = simplify(value)
                        # print("valore nuovo: ", new_value)
                        # print(f"valore vecchio: {value} valore nuovo: {new_value} check cambio: {str(value) != str(new_value)}")
                        # print("idd: ", idd)
                        if(str(value) != str(new_value)):
                            #print("è cambiato")
                            self.step_done = True
                    else:
                        #print("SALVE SONO IO")
                        new_value = self.evaluate_expression(value, idd)
                    new_values.append(new_value)
                else:
                    new_values.append(value)
            #print ("new_values: ", new_values)
            new_expression = {operation: new_values, 'idd': expression['idd']}
            return new_expression
        return expression

    def eq_do_step(self, steps: int = 1):
        if (str(self.eq) == "0"):
            return("equazione indeterminata", "Indeterminata", self.op_done, str(self.val_used)), true
        # if not self.eq.free_symbols:
        #     return ("equazione impossibile", "Impossibile", self.op_done, str(self.val_used)), True
        if self.last_step:
            self.eq = self.do_last_step()
            string_eq = str(self.eq)
            string_eq = self.format_replace(string_eq)
            return self.eq, string_eq, self.op_done, str(self.val_used)
        if self.first_step:
            self.first_step = False
            string_eq = str(self.eq) + " = 0"
            string_eq = self.format_replace(string_eq)
            return(self.eq, string_eq, self.op_done, str(self.val_used))
        for s in range(steps):
            eq = self.eq
            tree = self.extract_parts(eq, 1)
            print(f"Albero:{tree}")
            step_depth = self.get_highest_idd(tree)
            #print("depth: ", step_depth)
            ntree = self.evaluate_expression(tree, step_depth)
            nequ = self.build_expression(ntree)
            self.eq = self.check_step(nequ, tree, step_depth)
            if (str(self.eq) == "0"):
               return("equazione indeterminata", "Indeterminata", self.op_done, str(self.val_used)), true
            if not self.eq.free_symbols:
               return ("equazione impossibile", "Impossibile", self.op_done, str(self.val_used)), true
            if str(self.eq) == str(eq):
                print("ultimo step")
                if self.last_step == false:
                    self.last_step = true
                    string_eq = brutal_right_move(self.eq)
                    string_eq = self.format_replace(string_eq)
                    return self.eq, string_eq, self.op_done, "Separa i termini noti dalle incognite!", self.last_step
                else:
                    self.last_step = false
                    self.eq = self.do_last_step()
                string_eq = str(self.eq)
                string_eq = self.format_replace(string_eq)
                return self.eq, string_eq, self.op_done, str(self.val_used), self.last_step
            if self.is_eq:
                string_eq = str(self.eq) + " = 0"
                string_eq = self.format_replace(string_eq)
            else:
                string_eq = str(self.eq)
                string_eq = self.format_replace(string_eq)
            #print(f"next step: {string_eq}")
            #print(self.flag)
            if self.flag:
                self.flag = False
                self.step_done = False
                return(self.eq_do_step(steps))
            self.step_done = False
        return self.eq, string_eq, self.op_done, str(self.val_used), self.last_step

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
    print("equazione: ", eq.args)
    for arg in eq.args:
        if x in arg.free_symbols:
            lhs += arg
        elif isinstance(arg, (Integer)):
            rhs -= arg
    eq = f"{lhs} = {rhs}"
    print("equazione dopo: ", eq)
    return eq

#problema pow
#x = Symbol('x')
#eq = "((-5x^2 + 4x + 5x)(x+1) - 3(x+2))" #caso particolare: -5*x**2 + 4*x + 5*x sympy raccoglie la x, estrazione operazioni incompleta
#eq = "-x*(x + 1)*(5*x - 9) - (3*x + 6) = 0" #problema loop
#eq = "10x - 150x  - 3 = 0"
#eq = "9*x/4 + 1/2 = 0" #problema *1* all infinito (sembra risolto, da testare)
#eq = "8(x + 3) + 6(2x + 1) + (4(4x + 2) + 2(6x +7)) = 0"
#eq = "(8x + 3) * (3)= 0"
eq = "4x - 5 = 0"
print("equazione: ", eq)
step_solver = AdvanceEq(eq)
new_step, string_eq, op_done, val_used, penultimo_step = step_solver.eq_do_step(1)
print(string_eq)
print("new_step: ", new_step)
print("string eq: ", string_eq)
print("operazione fattissima: ", op_done)
print("valore usatissimo: ", val_used)
print("penultimo step: ", penultimo_step)
## valore usatissimo maledetto lui
## risolvere val usat con albero
##appena comincio il manage add sposto i valori in modo da avere le somme migliori


###risolvere val usat brutalmente
###roba brutta passaggio a destra
###radici potenze divisioni

# step_solver = AdvanceEq(string_eq)
# new_step, string_eq, op_done, val_used = step_solver.eq_do_step(1)
# print(string_eq)
# print("new_step: ", new_step)
# print("operazione fattissima: ", op_done)
# print("valore usatissimo: ", val_used)
# potenzialmente da migliorare la creazione dell'albero 
# valutare di tenere ogni addizione come operazione separata.
# return su delta e chiamata nuova funzione per risolvere delta
# foglio appunti + cerchio step da inviare
