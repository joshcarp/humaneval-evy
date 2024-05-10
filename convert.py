import ast
import os
import subprocess
import tempfile
import astunparse

scope = None

def translate_assign(node):
    targets = [translate_ast_node(target) for target in node.targets]
    if isinstance(node.value, ast.IfExp):
        code = " ".join(targets) + " := " + "None\n"
        code += translate_ifexp_statement(targets[0], node.value)
        return code
    value = translate_ast_node(node.value)
    assignOp = " = "
    for target in targets:
        if target not in scope:
            assignOp = " := "
            scope.add(target)
    return " ".join(targets) + assignOp + value + "\n"


def translate_subscript(node):
    """
    Translate a subscript node into a Python expression.

    :param node: An AST node representing a subscript expression
    :return: A Python expression as a string
    """
    # Get the node's children (the value and slice expressions)
    value, slice = node.value, node.slice

    # Recursively translate the value and slice expressions
    value_expr = translate_ast_node(value)
    slice_expr = translate_ast_node(slice)

    # Construct the subscript expression as a string
    return f"{value_expr}{slice_expr}"


def translate_slice(node):
    """Translate an ast.Slice node into Evy slice notation."""
    lower = translate_ast_node(node.lower) if node.lower else "0"  # Default to start
    upper = translate_ast_node(node.upper) if node.upper else ""  # Empty means to the end
    step = translate_ast_node(node.step) if node.step else ""

    # Handle potential empty elements if Evy's syntax allows it
    return f"[{lower}:{upper}]"  # Assuming Evy uses a similar notation


def translate_unary_operation(node):
    operand = translate_ast_node(node.operand)
    operator = translate_operator(node.op)
    EvyUnaryOpMapping = {
        ast.UAdd: "+",  # Unary plus (likely redundant)
        ast.USub: "-",  # Unary minus
        ast.Not: "!"  # Assuming Evy uses 'not'
    }

    # Use prefix notation for unary operators if Evy requires it
    if isinstance(EvyUnaryOpMapping, dict):
        return EvyUnaryOpMapping[type(node.op)] + operand
    else:
        return operator + operand  # Assuming Evy also accepts unary operators before the operand


def translate_name(name):
    keywords = {
        "func": "func_",
        "end": "end_",
        "num": "num_",
        "string": "string_",
        "on": "on_",
        "input": "input_",
        "key": "key_",
        "List": "[]",
        "str": "string",
    }
    return keywords[name] if name in keywords else name


def translate_return(node):
    if not node.value:
        return "return"
    return f"return {translate_ast_node(node.value)}"


def translate_in(node):
    pass

lambdas = {}

def translate_lambda(node):
    global lambdas
    func_name = "__lambda_" + str(len(lambdas))
    func_def = "func " + func_name + "("
    func_def += ", ".join(arg.arg for arg in node.args.args)
    func_def += "):\n"
    func_def += "return " + translate_ast_node(node.body) + "\n"
    lambdas[func_name] = func_def
    return func_name


def translate_assert(node):
    lambdas["assert"] = """func assert want:any got:any
    total = total + 1
    if want != got
        fails = fails + 1
        printf "want != got: want %v got %v\n" want got
    end
end"""
    return f"assert {translate_ast_node(node.test)}"


def translate_list(node):
    str = ""
    for elem in node.elts:
        str += f"{translate_ast_node(elem)} "
    return f"[{str}]"


def translate_import(node):
    return ""


def translate_for(node):
    evy_code = ""
    if "enumerate" in astunparse.unparse(node.iter):
        idxName, elemName = node.target.dims[0], node.target.dims[1]
        translatedName = translate_ast_node(node.iter.args[0])# [translate_ast_node(node.iter.args) for x in node.iter.args]
        evy_code += f"for {translate_ast_node(idxName)} := range {translatedName}\n"
        evy_code += i(f"{translate_ast_node(elemName)} = {translatedName}[{translate_ast_node(idxName)}]")
    if "in" in astunparse.unparse(node.iter):
        evy_code += f"for {translate_ast_node(node.target)} := range {node.iter.id}\n"
    for child_node in node.body:
        evy_code += i(translate_ast_node(child_node))
    if node.orelse:
        evy_code += "else\n"
        for child_node in node.orelse:
            evy_code += i(translate_ast_node(child_node))
    evy_code += "end\n"
    return evy_code

def translate_while(node):
    evy_code = "while " + translate_ast_node(node.test) + "\n"
    for child_node in node.body:
        evy_code += i(translate_ast_node(child_node))
    evy_code += "end\n"
    return evy_code



def translate_dict(node):
    evy_dict = "{"
    for i, (key, value) in enumerate(zip(node.keys, node.values)):
        key_str = translate_ast_node(key)
        if not isinstance(key, ast.Str):
            key_str = f'"{key_str}"'
        evy_dict += key_str + ":" + translate_ast_node(value)
        if i < len(node.keys) - 1:
            evy_dict += " "
    evy_dict += "}"
    return evy_dict



def translate_tuple(node):
    elements = [translate_ast_node(elt) for elt in node.elts]
    return "[" + ", ".join(elements) + "]"


def translate_augassign(node):
    target = translate_ast_node(node.target)
    value = translate_ast_node(node.value)
    operator = translate_operator(node.op)
    if isinstance(operator, ast.Add):
        operator = "+"
    elif isinstance(operator, ast.Sub):
        operator = "-"
    return f"{target} = {target} {operator} {value}\n"


def translate_set(node):
    m = ""
    for elt in node.elts:
        m += translate_ast_node(elt).replace('\"', "")
        m += f" :true "
    return "{" + m + "}"

def translate_listcomp(node):
    result_var = "__evy_listcomp_"  # Unique name
    evy_code = result_var + " := []\n"  # Initialize an empty list

    # Outermost 'for' loop
    evy_code += "for " + translate_ast_node(node.generators[0].target) + " := "
    evy_code += translate_ast_node(node.generators[0].iter) + ":\n"

    # Inner loops (if any)
    for generator in node.generators[1:]:
        evy_code += "for " + translate_ast_node(generator.target) + " := "
        evy_code += translate_ast_node(generator.iter) + ":\n"

    # Conditional expressions
    for i, if_clause in enumerate(node.generators[0].ifs):
        if i == 0:
            evy_code += "if " + translate_ast_node(if_clause) + "\n"
        else:
            evy_code += "else if " + translate_ast_node(if_clause) + "\n"
    if isinstance(node.elt, ast.IfExp):
        evy_code += translate_ifexp_statement(result_var, node.elt)
    return evy_code

def translate_ast_node(node):
    """Recursively translates an AST node"""
    if type(node) in operator_mappings:
        return operator_mappings[type(node)]
    elif isinstance(node, ast.Name):
        return translate_name(node.id)
    elif isinstance(node, ast.BinOp):
        return translate_binary_operation(node)
    elif isinstance(node, ast.UnaryOp):
        return translate_unary_operation(node)
    elif isinstance(node, ast.Compare):
        return translate_comparison(node)
    elif isinstance(node, ast.BoolOp):
        return translate_boolean_operation(node)
    elif isinstance(node, ast.Constant):
        return translate_constant(node)
    elif isinstance(node, ast.Call):
        return translate_function_call(node)
    elif isinstance(node, ast.FunctionDef):
        return translate_function_def(node)
    elif isinstance(node, ast.If):
        return translate_if_statement(node)
    elif isinstance(node, ast.IfExp):
        assert False
    elif isinstance(node, ast.Expr):
        return translate_ast_node(node.value)
    elif isinstance(node, ast.Module):
        return "".join([translate_ast_node(x) for x in node.body])
    elif isinstance(node, ast.Assign):
        return translate_assign(node)
    elif isinstance(node, ast.Subscript):
        return translate_subscript(node)
    elif isinstance(node, ast.Slice):
        return translate_slice(node)
    elif isinstance(node, ast.Return):
        return translate_return(node)
    elif isinstance(node, ast.In):
        return translate_in(node)
    elif isinstance(node, ast.Lambda):
        return translate_lambda(node)
    elif isinstance(node, ast.Assert):
        return translate_assert(node)
    elif isinstance(node, ast.List):
        return translate_list(node)
    elif isinstance(node, ast.ImportFrom):
        return translate_import(node)
    elif isinstance(node, ast.For):
        return translate_for(node)
    elif isinstance(node, ast.Name):
        return translate_name(node)
    elif isinstance(node, ast.Dict):
        return translate_dict(node)
    elif isinstance(node, ast.Tuple):
        return translate_list(node)
    elif isinstance(node, ast.AugAssign):
        return translate_augassign(node)
    elif isinstance(node, ast.Import):
        return translate_import(node)
    elif isinstance(node, ast.While):
        return translate_while(node)
    elif isinstance(node, ast.Set):
        return translate_set(node)
    elif isinstance(node, ast.ListComp):
        return translate_listcomp(node)
    else:
        raise NotImplementedError(f"Translation for {type(node)} not supported yet")


def pad(string, pad="    \n"):
    return pad + string.replace("\n", pad)
def translate_function_def(node, name=None):
    if name is None:
        name = node.name
    evy_code = "func " + name
    params = []
    if node.returns:
        return_type = translate_ast_node(node.returns)
        evy_code += ":" + return_type + " "

    for arg in node.args.args:
        annotation = f"{arg.arg}"
        if arg.annotation:
            annotation += f":{translate_ast_node(arg.annotation)}"
        params.append(annotation)
    evy_code += " ".join(params)
    evy_code += "\n"

    for child_node in node.body:
        stmnt = translate_ast_node(child_node)
        if isinstance(child_node, ast.Expr) and isinstance(child_node.value, ast.Constant):
            stmnt = pad(stmnt, '\n//')
        evy_code += i(stmnt)
    evy_code += "\nend\n"
    return evy_code

def translate_if_statement(node):
    evy_code = "if " + translate_ast_node(node.test) + "\n"
    for child_node in node.body:
        evy_code += i(translate_ast_node(child_node))
    for elif_clause in node.orelse:
        if hasattr(elif_clause, "test"):
            evy_code += "else if " + translate_ast_node(elif_clause.test) +"\n"
        if hasattr(elif_clause, "body"):
            for child_node in elif_clause.body:
                evy_code += i(translate_ast_node(child_node))
        if hasattr(elif_clause, "value"):
            evy_code += i(translate_ast_node(elif_clause.value))
    if node.orelse:
        evy_code += "else\n"
        for child_node in node.orelse:
            evy_code += i(translate_ast_node(child_node))
    evy_code += "end"
    return evy_code

def i(s):
    s = s.strip("\n")
    s = f"    {s}\n"
    s = s.replace("\n", "\n    ")
    return s.rstrip("    ")

def translate_ifexp_statement(var, node):
    evy_code = "if " + translate_ast_node(node.test) + "\n"
    evy_code += var + " = " + translate_ast_node(node.body) + "\n"
    if node.orelse:
        evy_code += f"else \n   {var} = " + translate_ast_node(node.orelse) + "\n"
        evy_code += "end\n"
    return evy_code

def translate_constant(node):
    if isinstance(node.value, bool):
        return "true" if node.value else "false"
    elif isinstance(node.value, (int, float)):
        return str(node.value)
    elif isinstance(node.value, str):
        return '"' + node.value + '"'
    elif isinstance(node.value, type(None)):
        return "nil"
    else:
        raise NotImplementedError(f"Translation for constant type {type(node.value)} is not supported yet")

operator_mappings = {
        ast.Add: "+",
        ast.Sub: "-",
        ast.Mult: "*",
        ast.Div: "/",
        ast.Eq: "==",
        ast.NotEq: "!=",
        ast.Lt: "<",
        ast.Gt: ">",
        ast.LtE: "<=",
        ast.GtE: ">=",
        ast.And: "and",
        ast.Or: "or",
        ast.Mod: "%",
    }

def translate_operator(operator):
    if type(operator) in operator_mappings:
        return operator_mappings[type(operator)]
    else:
        return None


def translate_math(operator):
    operator_mappings = {
        ast.Pow: "pow",
    }

    if type(operator) in operator_mappings:
        return operator_mappings[type(operator)]
    else:
        return None


def translate_binary_operation(node):
    left = translate_comparison(node.left)
    right = translate_comparison(node.right)
    operator = translate_operator(node.op)
    return left + " " + operator + " " + right


def translate_binary_operation(node):
    left = translate_ast_node(node.left)
    right = translate_ast_node(node.right)
    operator = translate_operator(node.op)
    if operator is not None:
        return left + " " + operator + " " + right
    operator = translate_math(node.op)
    return f"{operator} {left} {right}"

def translate_comparison(node):
    left = translate_ast_node(node.left)
    right = translate_ast_node(node.comparators[0])
    cmp = node.ops[0]
    if isinstance(cmp, ast.In):
        return f"(has {right} {left})"
    if isinstance(cmp, ast.NotIn):
        return f"!(has {right} {left})"
    operator = translate_ast_node(node.ops[0])
    return left + " " + operator + " " + right

def translate_boolean_operation(node):
    parts = [translate_ast_node(value) for value in node.values]
    operator = translate_ast_node(node.op)
    return " ".join(parts) + " " + operator

def translate_function_call(node):
    receiver = ""
    function_name = ""
    if hasattr(node.func, "attr"):
        function_name = node.func.attr
    elif hasattr(node.func, "id"):
        function_name = node.func.id
    if hasattr(node.func, "value"):
        receiver = translate_ast_node(node.func.value)
    args = " ".join(translate_ast_node(arg) for arg in node.args)
    if function_name == "append":
        return f"{receiver} = {receiver} + [{args}]"
    if function_name == "clear":
        return f"{receiver} = []"
    if function_name == "join":
        return f"(join {args} {receiver})"
    return f"{receiver}.{function_name} ({args})"

def translate_python_code(python_code):
    """Translates a Python code snippet into Evy"""
    global scope
    scope = set()
    tree = ast.parse(python_code)
    if isinstance(tree, ast.Module):
        try:
            return translate_ast_node(tree)
        except Exception as err:
            return ""
    else:
        raise NotImplementedError(f"Input must be Python code as a string")

def run_from_string(command, code_string, filename="tmp_script.py"):
    """Executes 'evy run' on code provided as a string.

    Args:
        code_string (str): The Python code to execute.
        filename (str, optional): Name of the temporary file.
                                  Defaults to "tmp_script.py".

    Returns:
        tuple: A tuple containing (stdout, stderr) from the evy command.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_file_path = os.path.join(tmp_dir, filename)
        with open(tmp_file_path, 'w') as f:
            f.write(code_string)
        command = f"{command} {tmp_file_path}"
        try:
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            return result.stdout, result.stderr
        except subprocess.CalledProcessError as e:
            return None, e.stderr

if __name__ == "__main__":
    translated = []
    for filename in os.listdir("python"):
        filepath = os.path.join("python", filename)
        if os.path.isfile(filepath):
            with open(filepath, 'r') as f:
                snippet = f.read()
                evy_code = translate_python_code(snippet)
                filepath = filepath.replace("python", "src")
                filepath = filepath.replace(".py", "_convert.evy")
                with open(filepath, 'w') as out:
                    out.write(evy_code)



