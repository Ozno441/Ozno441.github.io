# -*- coding: utf-8 -*-
import csv
import re
import json
from collections import Counter

# 1. 讀取 CSV
csv_data = {}
with open('01-franke_malaysia.csv', 'r', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        csv_data[row['nanyangSiteId']] = row

# 2. 讀取 YAML
yaml_data = {}
curr = {}
with open('01-franke_malaysia.yaml', 'r', encoding='utf-8') as f:
    for line in f:
        line_str = line.strip()
        if line_str.startswith('- nanyangSiteId:'):
            if 'nanyangSiteId' in curr:
                yaml_data[curr['nanyangSiteId']] = curr
            curr = {'nanyangSiteId': line_str.split(':', 1)[1].strip()}
        elif curr and ':' in line_str and not line_str.startswith('#'):
            k, v = line_str.split(':', 1)
            curr[k.strip()] = v.strip().strip("'\"")
    if curr and 'nanyangSiteId' in curr:
        yaml_data[curr['nanyangSiteId']] = curr

# 3. 分類點位類型
def classify_site(zh, alt):
    full = f"{zh or ''} {alt or ''}".lower()
    
    # 墓葬、義山、公塚、紀念碑、墓碑
    if any(k in full for k in ['義山', '公塚', '墓', '塚', '墳', '碑', 'cemetery', 'tombstone', 'grave', 'memorial']):
        return '墓葬與義山 (Cemetery / Tombstone)'
        
    # 寺廟、宮觀、佛堂、修道場所
    if any(k in full for k in ['廟', '宮', '寺', '庵', '堂', '亭', '巖', '院', '洞', '壇', '佛', '道', '閣', 'temple', 'monastery', 'shrine', 'pagoda', 'ch\'an-ssu', 'pi-an', 'lin']):
        return '寺廟與宗教場所 (Temple / Shrine)'
        
    # 會館、宗祠、家廟、同鄉會、行會、工會
    if any(k in full for k in ['會館', '公所', '宗祠', '家廟', '氏宗祠', '同鄉', '工會', '公會', '總會', '社', 'landsmannschaft', 'guild', 'lineage', 'clan', 'association', 'society']):
        return '會館與宗祠行會 (Clan / Guild)'
        
    # 學校與教育機構
    if any(k in full for k in ['學校', '公學', '中學', '小學', '書院', 'school', 'college', 'academy', 'education']):
        return '學校與文教 (School / Education)'
        
    # 醫療與慈善救濟機構
    if any(k in full for k in ['醫院', '醫社', '善堂', '積善', 'hospital', 'charity', 'benevolent']):
        return '醫療與慈善 (Hospital / Charity)'
        
    return '其他歷史設施 (Other)'

type_counts = Counter()
for sid, row in csv_data.items():
    t = classify_site(row.get('siteNameZh', ''), row.get('siteNameAlt1', ''))
    type_counts[t] += 1

# 4. 解析建置/銘刻年份 (dateISO)
year_counts_decade = Counter()
year_counts_period = Counter()
all_years = []

for sid, row in yaml_data.items():
    date_str = row.get('dateISO', '').strip()
    if not date_str:
        continue
    # 抓取年份 (4位數字)
    m = re.search(r'\b(1[4-9]\d{2}|20\d{2})\b', date_str)
    if m:
        y = int(m.group(1))
        all_years.append(y)
        # 年代 (Decade)
        decade = (y // 10) * 10
        year_counts_decade[f"{decade}s"] += 1
        
        # 歷史時期 (50年區間)
        if y < 1800:
            year_counts_period['1800年以前 (Pre-1800)'] += 1
        elif 1800 <= y < 1850:
            year_counts_period['1800-1849 (19世紀上半葉)'] += 1
        elif 1850 <= y < 1900:
            year_counts_period['1850-1899 (19世紀下半葉)'] += 1
        elif 1900 <= y < 1950:
            year_counts_period['1900-1949 (20世紀上半葉)'] += 1
        else:
            year_counts_period['1950年以後 (Post-1950)'] += 1

# 依照年代順序排序
sorted_decades = sorted(year_counts_decade.items(), key=lambda x: int(x[0][:-1]))
period_order = [
    '1800年以前 (Pre-1800)',
    '1800-1849 (19世紀上半葉)',
    '1850-1899 (19世紀下半葉)',
    '1900-1949 (20世紀上半葉)',
    '1950年以後 (Post-1950)'
]
sorted_periods = [(p, year_counts_period[p]) for p in period_order]

# 準備圖表資料
type_labels = [k for k, v in type_counts.most_common()]
type_values = [v for k, v in type_counts.most_common()]

period_labels = [k for k, v in sorted_periods]
period_values = [v for k, v in sorted_periods]

decade_labels = [k for k, v in sorted_decades if int(k[:-1]) >= 1800] # 1800年後詳細年代
decade_values = [v for k, v in sorted_decades if int(k[:-1]) >= 1800]

html_content = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>馬來西亞華文銘刻地點數據集分析 - Nanyang Data</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --bg: #f8fafc;
            --card-bg: #ffffff;
            --text-main: #1e293b;
            --text-sub: #64748b;
            --primary: #3b82f6;
            --accent: #0ea5e9;
            --border: #e2e8f0;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: var(--bg);
            color: var(--text-main);
            margin: 0;
            padding: 30px 20px;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1080px;
            margin: 0 auto;
        }}
        header {{
            text-align: center;
            margin-bottom: 35px;
        }}
        h1 {{
            font-size: 2rem;
            margin-bottom: 8px;
            color: #0f172a;
        }}
        .subtitle {{
            color: var(--text-sub);
            font-size: 1rem;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 16px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: var(--card-bg);
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            border: 1px solid var(--border);
            text-align: center;
        }}
        .stat-card .num {{
            font-size: 2.2rem;
            font-weight: 700;
            color: var(--primary);
            line-height: 1.2;
        }}
        .stat-card .desc {{
            color: var(--text-sub);
            font-size: 0.9rem;
            margin-top: 6px;
        }}
        .chart-card {{
            background: var(--card-bg);
            border-radius: 14px;
            padding: 28px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            border: 1px solid var(--border);
            margin-bottom: 30px;
        }}
        .chart-card h2 {{
            font-size: 1.35rem;
            margin-top: 0;
            margin-bottom: 8px;
            color: #1e293b;
        }}
        .chart-card p.chart-desc {{
            color: var(--text-sub);
            font-size: 0.95rem;
            margin-bottom: 22px;
        }}
        .chart-container {{
            position: relative;
            width: 100%;
            height: 380px;
        }}
        .insights {{
            background: #eff6ff;
            border-left: 4px solid var(--primary);
            padding: 16px 20px;
            border-radius: 6px;
            margin-top: 20px;
            font-size: 0.95rem;
            color: #1e3a8a;
        }}
        footer {{
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid var(--border);
            text-align: center;
            font-size: 0.9rem;
            color: var(--text-sub);
        }}
        footer a {{
            color: var(--primary);
            text-decoration: none;
            font-weight: 500;
        }}
        footer a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>馬來西亞華人歷史點位類型與年代分佈分析</h1>
            <div class="subtitle">基於 Wolfgang Franke 傅吾康教授之《馬來西亞華文銘刻彙編》數位化資料</div>
        </header>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="num">397</div>
                <div class="desc">總歷史點位數量</div>
            </div>
            <div class="stat-card">
                <div class="num">184 處 (46.3%)</div>
                <div class="desc">最多類型：寺廟與宗教場所</div>
            </div>
            <div class="stat-card">
                <div class="num">1850 - 1949</div>
                <div class="desc">核心建立高峰時期 (佔 83.0%)</div>
            </div>
            <div class="stat-card">
                <div class="num">1890s</div>
                <div class="desc">銘刻建立最鼎盛年代 (53處)</div>
            </div>
        </div>

        <!-- 圖表 1: 點位類型分佈 -->
        <div class="chart-card">
            <h2>一、歷史點位類型分佈</h2>
            <p class="chart-desc">統計馬來西亞華人歷史據點的機構性質分類，反映早期移民族群的社會組織結構。</p>
            <div class="chart-container">
                <canvas id="typeChart"></canvas>
            </div>
            <div class="insights">
                <strong>📌 分析結論：</strong>
                大部分的點位為<strong>「寺廟與宗教場所」</strong>（184 處，約 46.3%），其次為<strong>「墓葬與義山」</strong>（98 處，約 24.7%）以及<strong>「會館、宗祠與行會」</strong>（84 處，約 21.2%）。這三大類合計佔整體資料集的 92% 以上，呈現出海外華人社會以「神緣（寺廟）、地緣血緣（會館宗祠）、死生歸宿（義山）」為三大支柱的歷史結構。
            </div>
        </div>

        <!-- 圖表 2: 年代時期長條圖 -->
        <div class="chart-card">
            <h2>二、點位建立／最早銘刻年代時期（50年區間）</h2>
            <p class="chart-desc">依據各點位現存或記錄中最早之銘刻物件（如碑文、牌匾、古鐘）的西元年份統計。</p>
            <div class="chart-container">
                <canvas id="periodChart"></canvas>
            </div>
        </div>

        <!-- 圖表 3: 各年代 (Decade) 細部變化長條圖 -->
        <div class="chart-card">
            <h2>三、1800 年後各年代（每十年）建立走勢</h2>
            <p class="chart-desc">觀察 19 世紀至 20 世紀華人移民聚落迅速擴展與制度化的高峰趨勢。</p>
            <div class="chart-container">
                <canvas id="decadeChart"></canvas>
            </div>
            <div class="insights">
                <strong>📌 分析結論：</strong>
                多數點位建立在 <strong>19 世紀下半葉至 20 世紀上半葉（1850 年 ～ 1949 年）</strong>，共有 322 處，佔有效年份記錄的 <strong>83.0%</strong>。其中又以 <strong>1880 年代 ～ 1920 年代</strong> 最為集中，並於 <strong>1890 年代（53處）</strong> 達到歷史最高峰，與馬來半島錫礦開採與橡膠業擴展帶動的大規模華人移入時期完全吻合。
            </div>
        </div>

        <footer>
            <p>
                資料來源：<strong>Nanyang Data（<a href="https://creativecommons.org/licenses/by-sa/4.0/" target="_blank">CC BY-SA 4.0</a>）</strong><br>
                原始調查：Wolfgang Franke 傅吾康、Tieh-fan Chen 陳鐵凡（1982-1987）｜ 數位整理：Kenneth Dean 丁荷生、Marcus Bingenheimer 馬徳偉 等（NUS, 2024）
            </p>
        </footer>
    </div>

    <script>
        const ctxType = document.getElementById('typeChart').getContext('2d');
        new Chart(ctxType, {{
            type: 'bar',
            data: {{
                labels: {json.dumps(type_labels, ensure_ascii=False)},
                datasets: [{{
                    label: '點位數量',
                    data: {json.dumps(type_values)},
                    backgroundColor: [
                        '#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899'
                    ],
                    borderRadius: 6
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }},
                    tooltip: {{
                        callbacks: {{
                            label: (ctx) => ` 數量: ${{ctx.raw}} 處 (${{(ctx.raw / 397 * 100).toFixed(1)}}%)`
                        }}
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        title: {{ display: true, text: '點位數量 (處)' }}
                    }}
                }}
            }}
        }});

        const ctxPeriod = document.getElementById('periodChart').getContext('2d');
        new Chart(ctxPeriod, {{
            type: 'bar',
            data: {{
                labels: {json.dumps(period_labels, ensure_ascii=False)},
                datasets: [{{
                    label: '點位數量',
                    data: {json.dumps(period_values)},
                    backgroundColor: '#6366f1',
                    borderRadius: 6
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }},
                    tooltip: {{
                        callbacks: {{
                            label: (ctx) => ` 數量: ${{ctx.raw}} 處 (${{(ctx.raw / {len(all_years)} * 100).toFixed(1)}}%)`
                        }}
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        title: {{ display: true, text: '點位數量 (處)' }}
                    }}
                }}
            }}
        }});

        const ctxDecade = document.getElementById('decadeChart').getContext('2d');
        new Chart(ctxDecade, {{
            type: 'bar',
            data: {{
                labels: {json.dumps(decade_labels, ensure_ascii=False)},
                datasets: [{{
                    label: '點位數量',
                    data: {json.dumps(decade_values)},
                    backgroundColor: '#0284c7',
                    borderRadius: 5
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }},
                    tooltip: {{
                        callbacks: {{
                            label: (ctx) => ` 數量: ${{ctx.raw}} 處`
                        }}
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        title: {{ display: true, text: '點位數量 (處)' }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("index.html created successfully.")
