import csv
import re
from collections import Counter

# Read CSV
csv_sites = {}
with open('01-franke_malaysia.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        csv_sites[row['nanyangSiteId']] = row

# Read YAML manually (robust even if yaml library isn't installed)
yaml_sites = {}
curr = {}
with open('01-franke_malaysia.yaml', 'r', encoding='utf-8') as f:
    for line in f:
        line_str = line.strip()
        if line_str.startswith('- nanyangSiteId:'):
            if 'nanyangSiteId' in curr:
                yaml_sites[curr['nanyangSiteId']] = curr
            curr = {'nanyangSiteId': line_str.split(':', 1)[1].strip()}
        elif curr and ':' in line_str and not line_str.startswith('#'):
            k, v = line_str.split(':', 1)
            k = k.strip()
            v = v.strip().strip("'\"")
            curr[k] = v
    if curr and 'nanyangSiteId' in curr:
        yaml_sites[curr['nanyangSiteId']] = curr

print(f"Total CSV entries: {len(csv_sites)}")
print(f"Total YAML entries: {len(yaml_sites)}")

# Analyze types
# Let's see keywords in siteNameZh & siteNameAlt1
def classify_site(zh, alt):
    full_text = (zh or '') + ' ' + (alt or '')
    
    # Check Cemetery / 墓 / 義山 / 塚 / 墳
    if any(k in full_text for k in ['義山', '公塚', '墓', '塚', '墳', 'Cemetery', 'cemetery', 'tombstone', 'Tombstone', 'graveyard', 'Graveyard']):
        return '墓葬與義山 (Cemetery / Tombstone)'
    
    # Check Guild / Landsmannschaft / 會館 / 公所 / 宗祠 / 家廟 / 書院
    if any(k in full_text for k in ['會館', '公所', '宗祠', '家廟', '氏宗祠', '書院', '同鄉', 'Landsmannschaft', 'guild', 'Guild', 'lineage', 'clan', 'Clan']):
        return '會館與宗祠 (Clan Association / Guild)'
        
    # Check Temple / 廟 / 宮 / 寺 / 庵 / 堂 / 亭 / 巖 / 院 / 佛
    if any(k in full_text for k in ['廟', '宮', '寺', '庵', '堂', '亭', '巖', '佛', 'temple', 'Temple', 'monastery', 'shrine', 'Shrine']):
        return '寺廟與宗教場所 (Temple / Shrine)'
        
    # Check School / 學校 / 書院 / 學院
    if any(k in full_text for k in ['學校', '公學', '中學', '小學', 'School', 'school', 'College']):
        return '學校與文教 (School / Education)'
        
    # Check Hospital / Charity / 醫院 / 醫社 / 善堂 / 善
    if any(k in full_text for k in ['醫院', '醫社', '善堂', '積善', 'Hospital', 'hospital', 'charity']):
        return '醫療與慈善機構 (Hospital / Charity)'
        
    return '其他 (Other)'

type_counter = Counter()
for sid, row in csv_sites.items():
    stype = classify_site(row.get('siteNameZh', ''), row.get('siteNameAlt1', ''))
    type_counter[stype] += 1

print("\nType classification:")
for k, v in type_counter.most_common():
    print(f"  {k}: {v} ({v/len(csv_sites)*100:.1f}%)")

# Analyze dates
years = []
invalid_dates = []
for sid, row in yaml_sites.items():
    date_str = row.get('dateISO', '').strip()
    if not date_str or date_str == "''" or date_str == '""':
        continue
    # Extract 4-digit year
    m = re.search(r'\b(1[4-9]\d{2}|20\d{2})\b', date_str)
    if m:
        years.append(int(m.group(1)))
    else:
        invalid_dates.append((sid, date_str))

print(f"\nExtracted {len(years)} valid years.")
print(f"Min year: {min(years)}, Max year: {max(years)}")
if invalid_dates:
    print("Non-standard dates:", invalid_dates[:5])

# Group into periods / centuries / decades
# E.g. half-centuries or 20-year / 25-year / 50-year buckets
periods = Counter()
for y in years:
    if y < 1800:
        periods['1800年以前 (Pre-1800)'] += 1
    elif 1800 <= y < 1850:
        periods['1800-1849年 (19世紀上半葉)'] += 1
    elif 1850 <= y < 1900:
        periods['1850-1899年 (19世紀下半葉)'] += 1
    elif 1900 <= y < 1950:
        periods['1900-1949年 (20世紀上半葉)'] += 1
    else:
        periods['1950年以後 (Post-1950)'] += 1

print("\nPeriods (50-year buckets):")
for p, c in sorted(periods.items()):
    print(f"  {p}: {c} ({c/len(years)*100:.1f}%)")

# Also 10-year / 20-year buckets
decades = Counter()
for y in years:
    dec = (y // 10) * 10
    decades[f"{dec}s"] += 1

print("\nTop 10 decades:")
for d, c in decades.most_common(10):
    print(f"  {d}: {c}")
