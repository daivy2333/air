def ld_entry_template(sym):
    return f"""
/* PIR_ID: {sym.name}:{sym.unit} */
ENTRY({sym.name})
"""

def ld_symbol_template(sym):
    return f"""
/* PIR_ID: {sym.name}:{sym.unit} */
{sym.name} = .;
"""
