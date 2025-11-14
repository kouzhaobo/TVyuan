import json
import requests
import time
from datetime import datetime
from typing import Dict, Any, List

# 扩展检索源：GitHub raw 配置（2025 年最新，焦点 VOD API）
RETRIEVE_URLS = [
    "https://raw.githubusercontent.com/youhunwl/TVAPP/main/README.md",  # TVAPP 接口列表
    "https://raw.githubusercontent.com/wwb521/live/main/video.json",     # AV 成人源
    "https://raw.githubusercontent.com/ngo5/IPTV/main/sources.json",     # ngo5/IPTV VOD 源
    "https://raw.githubusercontent.com/Zhou-Li-Bin/Tvbox-QingNing/main/sources.json",  # QingNing 2025 更新
    "https://raw.githubusercontent.com/tongxunlu/tvbox-tvb-gd/main/tvbox.json",  # tvbox-tvb-gd 配置
    "https://raw.githubusercontent.com/qist/tvbox/main/sources.json",    # qist/tvbox VOD
    "https://raw.githubusercontent.com/gaotianliuyun/gao/main/sources.json",  # gao FongMi 配置
    "https://raw.githubusercontent.com/katelya77/KatelyaTV/main/api.json",  # KatelyaTV API
    "https://raw.githubusercontent.com/dongyubin/IPTV/main/sources.json"  # dongyubin IPTV VOD
]

def fetch_new_sources() -> List[Dict[str, str]]:
    """从 GitHub raw 检索新源（模拟全网）"""
    new_sources = []
    for url in RETRIEVE_URLS:
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                if url.endswith('.md'):
                    # 解析 README 文本，提取 name/api/detail
                    lines = resp.text.split('\n')
                    for line in lines:
                        if 'name,' in line or 'api:' in line:  # 灵活匹配
                            parts = [p.strip() for p in line.split(',') if p.strip()]
                            if len(parts) >= 2:
                                name = parts[0].replace('name:', '').strip()
                                api = parts[1].replace('api:', '').strip()
                                detail = ' '.join(parts[2:]) if len(parts) > 2 else '2025 GitHub VOD'
                                if 'vod' in api.lower() or 'tv' in api.lower():
                                    new_sources.append({"name": name, "api": api, "detail": detail})
                else:
                    # 解析 JSON 源
                    data = resp.json()
                    # 假设常见结构：sites/list/api_list 等
                    possible_keys = ['sites', 'list', 'api_list', 'sources']
                    for key in possible_keys:
                        if key in data and isinstance(data[key], list):
                            for item in data[key]:
                                if isinstance(item, dict):
                                    name = item.get('name', item.get('title', 'Unknown'))
                                    api = item.get('api', item.get('url', ''))
                                    detail = item.get('detail', '2025 GitHub VOD')
                                    if api:
                                        new_sources.append({"name": name, "api": api, "detail": detail})
                            break
                time.sleep(1)
        except Exception as e:
            print(f"检索失败 {url}: {e}")
    # 去重并限 20 个
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
    """测试 API 可用性（简化：检查响应 + JSON）"""
    params = '?ac=videolist&wd=热门' if '?' not in api_url else '&ac=videolist&wd=热门'
    try:
        resp = requests.get(api_url + params, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
        if resp.status_code == 200 and resp.text.strip():
            try:
                data = resp.json()
                # 检查是否有视频列表键
                if any(key in data for key in ['list', 'data', 'result', 'videos']):
                    return 'available'
            except json.JSONDecodeError:
                pass  # 非 JSON 但响应 OK，也算可用（有些源是 XML）
    except:
        pass
    return 'failed'

# 加载当前 sources
with open('sources.json', 'r', encoding='utf-8') as f:
    sources = json.load(f)

api_site = sources['api_site']
updated_site = {}  # 只保留可用源

# 测试原有源，删除失效
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
        time.sleep(1)  # 延迟避免封禁

# 检索并添加新源（只添加可用）
print("添加新源...")
new_sources = fetch_new_sources()
added_count = 0
for i, new in enumerate(new_sources):
    key = f"new_api_{len(updated_site) + i + 1}"  # 新键
    status = test_api(new['api'], new['name'])
    if status == 'available':
        updated_site[key] = {**new, 'status': 'new_available'}
        print(f"添加新可用: {new['name']}")
        added_count += 1
    time.sleep(1)

sources['api_site'] = updated_site
sources['update_date'] = datetime.now().isoformat()
sources['total_available'] = len([k for k in updated_site if 'available' in updated_site[k].get('status', '')])

# 覆盖保存 sources.json（单一文件）
with open('sources.json', 'w', encoding='utf-8') as f:
    json.dump(sources, f, ensure_ascii=False, indent=2)

# 输出可用计数文件（用于 YAML 消息）
with open('AVAILABLE_COUNT.txt', 'w') as f:
    f.write(str(sources['total_available']))

print(f"更新完成: {sources['total_available']} 可用源（添加 {added_count} 新源）。覆盖 sources.json")
