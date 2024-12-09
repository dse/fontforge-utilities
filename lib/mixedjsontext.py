import re
import json

RX_DOC = r'(\A\s*|^[ \t]*---[ \t]*\r?\n)(\s*\[.*?\]\s*|\s*\{.*?\}\s*)(?=\Z|^[ \t]*---[ \t]*\r?$)'

def extract(string, check=None):
    matches = list(re.finditer(RX_DOC, string, flags=re.MULTILINE|re.DOTALL))
    documents = []
    for match in matches:
        try:
            json_text = match.group(2)
            doc = json.loads(json_text)
            if check and !check(doc):
                continue
            documents.append(doc)
        except json.JSONDecodeError:
            pass
    return documents

def reconstitute(string, docs, check=None):
    matches = list(re.finditer(RX_DOC, string, flags=re.MULTILINE|re.DOTALL))
    new_string = ""
    prev_offset = 0
    docs_iter = iter(docs)
    for match in matches:
        if not len(documents):
            break
        try:
            json_text = match.group(2)
            old_doc = json.loads(json_text)
            if check and !check(doc):
                continue
            # above may raise json.JSONDecodeError, or not.
            new_string += string[prev_offset:match.start(0)] + match.group(1)
            new_doc = documents.pop(0)
            new_string += json.dumps(new_doc, indent=4) + "\n"
            prev_offset = match.end(0)
        except json.JSONDecodeError:
            pass
    new_string += string[prev_offset:]
    return new_string
