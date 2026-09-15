import json
import os
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date, timedelta

DAILY = "https://www.cbr.ru/scripts/XML_daily.asp"
DYNAMIC = "https://www.cbr.ru/scripts/XML_dynamic.asp"


def get_xml(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return ET.fromstring(r.read().decode("windows-1251"))


def to_number(text):
    return float(text.replace(",", "."))


root = get_xml(DAILY)

currencies = []
for v in root.findall("Valute"):
    currencies.append({
        "id": v.get("ID"),
        "code": v.findtext("CharCode"),
        "name": v.findtext("Name"),
        "rate": to_number(v.findtext("VunitRate")),
    })

daily = {"date": root.get("Date"), "currencies": currencies}

end = date.today()
start = end - timedelta(days=370)
fmt = "%d/%m/%Y"

history = {}
for c in currencies:
    url = f"{DYNAMIC}?date_req1={start.strftime(fmt)}&date_req2={end.strftime(fmt)}&VAL_NM_RQ={c['id']}"
    try:
        dyn = get_xml(url)
    except Exception as e:
        print("skip", c["code"], e)
        continue
    points = {}
    for rec in dyn.findall("Record"):
        d = rec.get("Date")
        iso = f"{d[6:10]}-{d[3:5]}-{d[0:2]}"
        points[iso] = to_number(rec.findtext("VunitRate"))
    history[c["id"]] = points
    print(c["code"], len(points))

os.makedirs("data", exist_ok=True)

with open("data/daily.json", "w", encoding="utf-8") as f:
    json.dump(daily, f, ensure_ascii=False, indent=1)

with open("data/history.json", "w", encoding="utf-8") as f:
    json.dump(history, f, ensure_ascii=False)

print("ok", len(currencies), "currencies")
