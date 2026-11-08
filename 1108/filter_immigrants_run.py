# -*- coding: utf-8 -*-
import csv, sys
from collections import defaultdict

# 讀取 CSV
with open('01-franke_malaysia.csv', 'r', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

TARGET_FIELD = 'siteNameZh'

# 第一組關鍵字：組織形態與移民機構
STEP1_KEYWORDS = ['會館', '公所', '同鄉', '義山', '公塚', '俱樂部', '同邑', '八邑', '客屬']

step1_results = []
for r in rows:
    val = r[TARGET_FIELD] or ''
    if any(k in val for k in STEP1_KEYWORDS):
        step1_results.append(r)

# 第二組關鍵字：原鄉祖籍（含府、縣、方言別稱）
GEO_GROUPS = {
    '福建／閩南系統': [
        '福建', '閩南', '漳州', '泉州', '漳泉', '永春', '安溪', '晉江', '興安', '興化', '詔安', '龍巖'
    ],
    '廣東廣府系統': [
        '廣東', '廣肇', '番禺', '南海', '順德', '台山', '甯陽', '寧陽', '新寧', '香山', '中山', '清遠', '東安', '四邑', '岡州'
    ],
    '客家系統': [
        '客屬', '嘉應', '茶陽', '大埔', '惠州', '汀州', '增龍', '應和', '永定', '海陸'
    ],
    '海南系統': [
        '瓊州', '琼州', '瓊崖'
    ],
    '潮州系統': [
        '潮州', '八邑'
    ],
    '跨省或聯合組織': [
        '兩廣', '三江'
    ],
    '廣西系統': [
        '廣西'
    ],
    '雷州系統': [
        '雷州'
    ],
    '全體華人／未細分': [
        '華僑', '中華'
    ]
}

classified = defaultdict(list)
unmatched = []

for r in step1_results:
    name = r[TARGET_FIELD] or ''
    matched_group = None
    for group_name, kws in GEO_GROUPS.items():
        if any(k in name for k in kws):
            matched_group = group_name
            break
    if matched_group:
        classified[matched_group].append(r)
    else:
        unmatched.append(r)

with open('summary_result.txt', 'w', encoding='utf-8') as out:
    out.write(f"第一步篩選（移民團體/組織）：共 {len(step1_results)} 處\n\n")
    out.write("第二步祖籍原鄉分類結果：\n")
    for g, items in sorted(classified.items(), key=lambda x: len(x[1]), reverse=True):
        out.write(f"【{g}】: {len(items)} 處 ({len(items)/len(step1_results)*100:.1f}%)\n")
        for it in items:
            out.write(f"  - {it['nanyangSiteId']}: {it['siteNameZh']} ({it['siteNameAlt1']})\n")
        out.write("\n")
    out.write(f"【其他未明確指定祖籍之義山或公所】：{len(unmatched)} 處\n")
    for it in unmatched:
        out.write(f"  - {it['nanyangSiteId']}: {it['siteNameZh']} ({it['siteNameAlt1']})\n")

print("Finished writing summary_result.txt")
