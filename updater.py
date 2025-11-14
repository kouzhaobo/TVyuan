import json
import requests
import time
from datetime import datetime
from typing import Dict, Any, List

# 固定检索源：GitHub raw 配置（2025 活跃仓库）
RETRIEVE_URLS = [
    "https://raw.githubusercontent.com/youhunwl/TVAPP/main/README.md",  # TVAPP 接口列表
    "https://raw.githubusercontent.com/wwb521/live/main/video.json"  # AV 成人源
]

def fetch_new_sources() -> List[Dict[str, str]]:
    """从 GitHub raw 检索新源（模拟全网）"""
    new_sources = []
    for url in RETRIEVE_URLS:
        try:
            resp = requests.get(url, timeout=10)
            if 'github.com/youhunwl/TVAPP' in url:
                # 解析 README 文本，提取 name/api/detail
                lines = resp.text.split('\n')
                for line in lines:
                    if 'name,' in line:
                        parts = line.split(',')
                        if len(parts) >= 3:
                            name = parts[0].strip()
                            api = parts[1].strip()
                            detail = parts[2].strip()
                            if 'vod' in api.lower() or 'tv' in api.lower():  # 过滤 VOD
                                new_sources.append({"name": name, "api": api, "detail": detail})
            else:
                # 解析 JSON 源
                data = resp.json()
                for item in data.get('sites', []):  # 假设结构
                    new_sources.append({
                        "name": item.get('name', ''),
                        "api": item.get('api', ''),
                        "detail": item.get('detail', 'AV 2025 更新')
                    })
            time.sleep(1)
        except Exception as e:
            print(f"检索失败 {url}: {e}")
    return new_sources[:20]  # 限 20 个新源

def test_api(api_url: str, name: str) -> str:
    """测试 API 可用性"""
    params = '?ac=videolist' if '?' not in api_url else '&ac=videolist'
    try:
        resp = requests.get(api_url + params, timeout=10)
        if resp.status_code == 200 and 'list' in resp.text or 'data' in resp.text:
            return 'available'
    except:
        pass
    return 'failed'

# 加载当前 sources
with open('sources.json', 'r', encoding='utf-8') as f:
    sources = json.load(f)

api_site = sources['api_site']
updated_site = {}

# 测试原有源
for key, config in api_site.items():
    name = config.get('name', key)
    api_url = config.get('api', '')
    if api_url:
        status = test_api(api_url, name)
        if status == 'available':
            updated_site[key] = {**config, 'status': 'available'}
        else:
            print(f"失效: {name}")
        time.sleep(1)

# 检索并添加新源
new_sources = fetch_new_sources()
for i, new in enumerate(new_sources):
    key = f"new_api_{i+73}"  # 续接原编号
    if test_api(new['api'], new['name']) == 'available':
        updated_site[key] = {**new, 'status': 'new_available'}
        print(f"新可用: {new['name']}")

sources['api_site'] = updated_site
sources['update_date'] = datetime.now().isoformat()
sources['total_available'] = len([k for k in updated_site if updated_site[k].get('status') == 'available'])

# 保存更新 sources.json
with open('sources.json', 'w', encoding='utf-8') as f:
    json.dump(sources, f, ensure_ascii=False, indent=2)

# 生成输出 JSON（带视频样本）
output = sources.copy()
output['videos_sample'] = []  # 可扩展：从可用源拉视频
date_str = datetime.now().strftime('%Y-%m-%d')
filename = f'api-sources-{date_str}.json'
with open(filename, 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"更新完成: {sources['total_available']} 可用源。保存 {filename}")
