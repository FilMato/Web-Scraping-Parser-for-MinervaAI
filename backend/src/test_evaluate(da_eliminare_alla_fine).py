import json

def clean(text):
    text = text.replace('"', '')
    text = text.replace("'", '')
    return text

parsed_text = clean(open("parsers/risultati/Risultato_parser.txt", encoding="utf-8").read())
gold_text = clean(open("../../gs_data/mypersonaltrainer_gs/cervello.txt", encoding="utf-8").read())

print(json.dumps({"parsed_text": parsed_text, "gold_text": gold_text}, ensure_ascii=False, indent=2))