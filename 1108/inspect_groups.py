# -*- coding: utf-8 -*-
import csv, sys

with open('01-franke_malaysia.csv', 'r', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

kw_group1 = ['會館', '公所', '同鄉', '義山', '公塚', '俱樂部', '同邑']

filtered = []
for r in rows:
    zh = r['siteNameZh'] or ''
    if any(k in zh for k in kw_group1):
        filtered.append(r)

with open('filtered_step1.txt', 'w', encoding='utf-8') as out:
    out.write(f"Total matching step 1: {len(filtered)}\n\n")
    for r in filtered:
        out.write(f"{r['nanyangSiteId']} | {r['siteNameZh']} | {r['siteNameAlt1']}\n")

print(f"Done, found {len(filtered)} records.")
