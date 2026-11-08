# -*- coding: utf-8 -*-
import csv
from collections import defaultdict

# 讀取 CSV
with open('01-franke_malaysia.csv', 'r', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

# 定義判斷欄位：以 siteNameZh 為主
TARGET_FIELD = 'siteNameZh'

# 第一組關鍵字：篩選同鄉、方言與移民組織
STEP1_KEYWORDS = ['會館', '公所', '同鄉', '義山', '公塚', '俱樂部', '同邑', '八邑', '客屬']

step1_results = []
for r in rows:
    val = r[TARGET_FIELD] or ''
    if any(k in val for k in STEP1_KEYWORDS):
        step1_results.append(r)

print(f"第一步：從 {len(rows)} 個點位中篩選出 {len(step1_results)} 個移民同鄉團體相關點位。")

# 第二組關鍵字：原鄉祖籍／方言語系
# 包含大區域、主要府級、縣級與方言稱呼
GEO_GROUPS = {
    '福建／閩南系統 (Fukien / Minnan)': [
        '福建', '閩南', '漳州', '泉州', '漳泉', '永春', '安溪', '晉江', '興安', '興化', '詔安', '龍巖'
    ],
    '廣東廣肇／廣府系統 (Cantonese / Guangfu)': [
        '廣東', '廣肇', '番禺', '南海', '順德', '台山', '甯陽', '寧陽', '新寧', '香山', '中山', '清遠', '東安', '四邑', '岡州'
    ],
    '客家／潮梅汀系統 (Hakka)': [
        '客屬', '嘉應', '茶陽', '大埔', '惠州', '汀州', '增龍', '應和', '永定', '海陸'
    ],
    '潮州／潮汕系統 (Chaozhou / Teochew)': [
        '潮州', '八邑'
    ],
    '海南／瓊崖系統 (Hainan)': [
        '瓊州', '琼州', '瓊崖'
    ],
    '廣西系統 (Guangxi)': [
        '廣西'
    ],
    '雷州系統 (Leizhou)': [
        '雷州'
    ],
    '跨省聯立／跨方言團體 (Pan-regional / Joint)': [
        '兩廣', '三江'
    ],
    '全華人／未細分同鄉 (Pan-Chinese)': [
        '華僑', '中華'
    ]
}

# 執行第二步分類
classified = defaultdict(list)
unmatched = []

for r in step1_results:
    name = r[TARGET_FIELD] or ''
    matched_group = None
    
    # 檢查屬於哪個祖籍分類
    for group_name, kws in GEO_GROUPS.items():
        if any(k in name for k in kws):
            matched_group = group_name
            break
            
    if matched_group:
        classified[matched_group].append(r)
    else:
        unmatched.append(r)

print("\n第二步：原鄉祖籍分類統計：")
for g, items in sorted(classified.items(), key=lambda x: len(x[1]), reverse=True):
    print(f"  [{g}]: {len(items)} 處")
    for it in items[:3]:
        print(f"     - {it['nanyangSiteId']}: {it['siteNameZh']}")
    if len(items) > 3:
        print(f"     ...等共 {len(items)} 處")

if unmatched:
    print(f"\n未匹配具體原鄉（需進一步檢視）: {len(unmatched)} 處")
    for it in unmatched:
        print(f"  - {it['nanyangSiteId']}: {it['siteNameZh']} | {it['siteNameAlt1']}")
