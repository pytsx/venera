import json 

def saveJson(name: str, report: object):
  with open(name + ".json", "w") as file:
    json.dump(report, file, indent=2)

def saveHTML(path: str, html: str):
  with open(path, "w", encoding="utf-8") as file:
    file.write(html)