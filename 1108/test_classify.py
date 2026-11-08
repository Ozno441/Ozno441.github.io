import csv, re
from collections import Counter

# Analyze and print in UTF-8
csv_sites = []
with open('01-franke_malaysia.csv', 'r', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        csv_sites.append(row)

# Enhanced classification
def classify(zh, alt):
    full = f"{zh or ''} {alt or ''}".lower()
    
    # 1. 墓葬、義山、公塚、紀念碑、墓碑
    if any(k in full for k in ['義山', '公塚', '墓', '塚', '墳', '碑', 'cemetery', 'tombstone', 'grave', 'memorial']):
        return '墓葬與義山 (Cemetery / Tombstone / Memorial)'
        
    # 2. 寺廟、宮觀、佛堂、修道場所
    if any(k in full for k in ['廟', '宮', '寺', '庵', '堂', '亭', '巖', '院', '洞', '壇', '佛', '道', '閣', 'temple', 'monastery', 'shrine', 'pagoda', 'ch\'an-ssu', 'pi-an', 'lin']):
        return '寺廟與宗教場所 (Temple / Shrine / Monastery)'
        
    # 3. 會館、宗祠、家廟、同鄉會、行會、工會
    if any(k in full for k in ['會館', '公所', '宗祠', '家廟', '氏宗祠', '書院', '同鄉', '工會', '公會', '總會', '社', 'landsmannschaft', 'guild', 'lineage', 'clan', 'association', 'society']):
        return '會館、宗祠與行會 (Clan Association / Guild)'
        
    # 4. 學校與教育機構
    if any(k in full for k in ['學校', '公學', '中學', '小學', '書院', 'school', 'college', 'academy', 'education']):
        return '學校與文教 (School / Education)'
        
    # 5. 醫療與慈善救濟機構
    if any(k in full for k in ['醫院', '醫社', '善堂', '積善', 'hospital', 'charity', 'benevolent']):
        return '醫療與慈善機構 (Hospital / Charity)'
        
    return '其他歷史遺跡與機構 (Other)'

counts = Counter()
for s in csv_sites:
    c = classify(s['siteNameZh'], s['siteNameAlt1'])
    counts[c] += 1

print("Types:")
for k, v in counts.most_common():
    print(f"  {k}: {v}")
