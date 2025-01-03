def sfnt_get(font, name, lang="English (US)"):
    results = [sfnt[2] for sfnt in font.sfnt_names
               if sfnt[0] == lang and sfnt[1] == name]
    if len(results) == 0:
        return None
    return results[0]
