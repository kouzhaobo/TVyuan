import json
import requests
import time
from datetime import datetime
from typing import Dict, Any, List

# 扩展检索源：GitHub + CSDN/Gitee/Zhihu 等（2025 年最新分享）
RETRIEVE_URLS = [
    # 原 GitHub
    "https://raw.githubusercontent.com/youhunwl/TVAPP/main/README.md",
    "https://raw.githubusercontent.com/wwb521/live/main/video.json",
    "https://raw.githubusercontent.com/ngo5/IPTV/main/sources.json",
    "https://raw.githubusercontent.com/Zhou-Li-Bin/Tvbox-QingNing/main/sources.json",
    "https://raw.githubusercontent.com/tongxunlu/tvbox-tvb-gd/main/tvbox.json",
    "https://raw.githubusercontent.com/qist/tvbox/main/sources.json",
    "https://raw.githubusercontent.com/gaotianliuyun/gao/main/sources.json",
    "https://raw.githubusercontent.com/katelya77/KatelyaTV/main/api.json",
    "https://raw.githubusercontent.com/dongyubin/IPTV/main/sources.json",
    # 新：CSDN/Gitee/Zhihu 分享源
    "https://raw.githubusercontent.com/vcloudc/tvbox/main/tw/api.json",  # 天微科技 (CSDN 分享)
    "https://raw.githubusercontent.com/yoursmile66/TVBox/main/XC.json",  # 南风接口 (CSDN)
    "https://cc.cckimi.top/api.php/provide/vod/?ac=list",  # 影视仓 API (CSDN 博客)
    "https://gitee.com/itxve/fetch/raw/master/fly/fly.json",  # Gitee Fly 源 (Zhihu 提及)
    "https://gitee.com/ChenAnRong/tvbox-config/raw/master/tvbox.json",  # Gitee TVBox 配置
    "https://raw.githubusercontent.com/xyq254245/xyqonlinerule/main/XYQTVBox.json"  # 香雅情短剧 (CSDN)
]

def fetch_new_sources() -> List[Dict[str, str]]:
    """从 raw/API 检索新源"""
    new_sources = []
    for url in RETRIEVE_URLS:
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                if url.endswith('.md'):
                    lines = resp.text.split('\n')
                    for line in lines:
                        if 'name,' in line or 'api:' in line:
                            parts = [p.strip() for p in line.split(',') if p.strip()]
                            if len(parts) >= 2:
                                name = parts[0].replace('name:', '').strip()
                                api = parts[1].replace('api:', '').strip()
                                detail = ' '.join(parts[2:]) if len(parts) > 2 else '2025 CSDN/Gitee VOD'
                                if 'vod' in api.lower() or 'tv' in api.lower():
                                    new_sources.append({"name": name, "api": api, "detail": detail})
                else:
                    # API 或 JSON
                    if 'api.php' in url:
                        # 直接用 URL 作为源（假设是列表 API）
                        new_sources.append({"name": "影视仓 API", "api": url, "detail": "CSDN 分享 VOD"})
                    else:
                        data = resp.json()
                        possible_keys = ['sites', 'list', 'api_list', 'sources']
                        for key in possible_keys:
                            if key in data and isinstance(data[key], list):
                                for item in data[key]:
                                    if isinstance(item, dict):
                                        name = item.get('name', item.get('title', 'Unknown'))
                                        api = item.get('api', item.get('url', ''))
                                        detail = item.get('detail', '2025 CSDN/Gitee VOD')
                                        if api:
                                            new_sources.append({"name": name, "api": api, "detail": detail})
                                break
                time.sleep(1)
        except Exception as e:
            print(f"检索失败 {url}: {e}")
    # 去重限 20 个
    seen = set()
    unique_new = []
    for ns in new_sources:
        key = f"{ns['name']}-{ns['api']}"
        if key not in seen:
            seen.add(key)
            unique_new.append(ns)
            if len(unique_new) >= 20:
                break
    return unique_new

def test_api(api_url: str, name: str) -> str:
    """测试 API（宽松：响应 OK + 基本内容）"""
    params = '?ac=videolist&wd=热门' if '?' not in api_url else '&ac=videolist&wd=热门'
    try:
        resp = requests.get(api_url + params, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
        if resp.status_code == 200 and len(resp.text) > 100:  # 响应 >100 字节
            try:
                data = resp.json()
                if any(key in data for key in ['list', 'data', 'result', 'videos']):
                    return 'available'
            except json.JSONDecodeError:
                return 'available'  # 非 JSON 但有内容，也 OK
    except:
        pass
    return 'failed'

# 加载/更新 sources
with open('sources.json', 'r', encoding='utf-8') as f:
    sources = json.load(f)

api_site = sources['api_site']
updated_site = {}

# 删除失效，保留可用
print("检查原有源...")
for key, config in api_site.items():
    name = config.get('name', key)
    api_url = config.get('api', '')
    if api_url:
        status = test_api(api_url, name)
        if status == 'available':
            updated_site[key] = {**config, 'status': 'available'}
            print(f"保留: {name}")
        else:
            print(f"删除失效: {name}")
        time.sleep(1)

# 添加新源
print("添加新源...")
new_sources = fetch_new_sources()
added_count = 0
for i, new in enumerate(new_sources):
    key = f"new_api_{len(updated_site) + i + 1}"
    status = test_api(new['api'], new['name'])
    if status == 'available':
        updated_site[key] = {**new, 'status': 'new_available'}
        print(f"添加新可用: {new['name']}")
        added_count += 1
    time.sleep(1)

sources['api_site'] = updated_site
sources['update_date'] = datetime.now().isoformat()
sources['total_available'] = len([k for k in updated_site if 'available' in updated_site[k].get('status', '')])

# 覆盖 sources.json
with open('sources.json', 'w', encoding='utf-8') as f:
    json.dump(sources, f, ensure_ascii=False, indent=2)

# 输出计数
with open('AVAILABLE_COUNT.txt', 'w') as f:
    f.write(str(sources['total_available']))

print(f"更新完成: {sources['total_available']} 可用源（添加 {added_count} 新源）。覆盖 sources.json")
