def compile_to_c(code):
    lines = code.split("\n")

    c_code = [
        "#include <stdio.h>",
        "int main() {"
    ]

    variables = set()
    block_stack = []

    for line in lines:
        raw = line
        stripped = line.strip()

        if not stripped:
            continue

        indent = len(raw) - len(raw.lstrip())

        # Close blocks when indentation decreases
        while block_stack and block_stack[-1] > indent:
            c_code.append("}")
            block_stack.pop()

        # LET
        if stripped.startswith("let"):
            parts = stripped[4:].split("=")
            if len(parts) != 2:
                raise Exception("Syntax Error: Invalid let")

            var = parts[0].strip()
            val = parts[1].strip()

            if var not in variables:
                c_code.append(f"int {var} = {val};")
                variables.add(var)
            else:
                c_code.append(f"{var} = {val};")

        # INPUT (FIXED WITH PROMPT + VALIDATION)
        elif stripped.startswith("input"):
            var = stripped[6:].strip()

            if not var:
                raise Exception("Syntax Error: input requires variable")

            if var not in variables:
                c_code.append(f"int {var};")
                variables.add(var)

            c_code.append(f'printf("Enter {var}: ");')
            c_code.append(f'if (scanf("%d", &{var}) != 1) {{')
            c_code.append(f'    printf("Invalid input\\n");')
            c_code.append(f'    return 1;')
            c_code.append(f'}}')

        # PRINT
        elif stripped.startswith("print"):
            content = stripped[6:].strip()

            if content.startswith('"') and content.endswith('"'):
                c_code.append(f'printf({content});')
            else:
                if content not in variables:
                    raise Exception(f"Undefined variable: {content}")
                c_code.append(f'printf("%d\\n", {content});')

        # IF
        elif stripped.startswith("if"):
            condition = stripped[3:].strip()
            if not condition:
                raise Exception("Syntax Error: empty if")

            c_code.append(f"if ({condition})" + " {")
            block_stack.append(indent)

        # ELSE
        elif stripped.startswith("else"):
            if not block_stack:
                raise Exception("Syntax Error: else without if")

            if block_stack[-1] != indent:
                raise Exception("Syntax Error: else indentation mismatch")

            c_code.append("} else {")

        else:
            raise Exception(f"Unknown syntax: {stripped}")

    # Close all remaining blocks
    while block_stack:
        c_code.append("}")
        block_stack.pop()

    c_code.append("return 0;")
    c_code.append("}")

    return "\n".join(c_code)