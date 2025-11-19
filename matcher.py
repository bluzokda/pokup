import re

def normalize_name(name):
    # Привести к нижнему регистру
    name = name.lower()
    # Заменить синонимы качества
    name = re.sub(r'\(field-tested\)|\(ft\)', '(ft)', name)
    name = re.sub(r'\(minimal wear\)|\(mw\)', '(mw)', name)
    name = re.sub(r'\(factory new\)|\(fn\)', '(fn)', name)
    name = re.sub(r'\(battle-scarred\)|(bs)', '(bs)', name)
    name = re.sub(r'\(well-worn\)|\(ww\)', '(ww)', name)
    # Удалить лишние пробелы и символы
    name = re.sub(r'\s+', ' ', name).strip()
    return name

def find_best_match(fp_item, po_items):
    norm_name = normalize_name(fp_item["name"])
    for po_item in po_items:
        if normalize_name(po_item["name"]) in norm_name or norm_name in normalize_name(po_item["name"]):
            return po_item
    return None
