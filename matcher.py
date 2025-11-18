def normalize_name(name):
    # Пример нормализации
    name = name.lower()
    name = name.replace("(field-tested)", "(ft)").replace("(minimal wear)", "(mw)")
    return name

def find_best_match(fp_item, po_items):
    norm_name = normalize_name(fp_item["name"])
    for po_item in po_items:
        if normalize_name(po_item["name"]) in norm_name or norm_name in normalize_name(po_item["name"]):
            return po_item
    return None
