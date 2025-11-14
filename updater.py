import json
import requests
import time
import re
from datetime import datetime
from typing import Dict, Any, List

# 初始搜索查询（动态更新，只用 GitHub/Gitee，避免 CSDN SSL）
INITIAL_SEARCH_QUERIES = [
    "https://github.com/search?q=2025+TVBox+VOD+API+raw+json&type=code",
    "https://gitee.com/explore?type=project&q=TVBox+2025"
]

def update_retrieve_urls() -> List[str]:
    """动态检索新 RETRIEVE_URLS（从搜索页提取，限 20-30）"""
    new_urls = []
    for query_url in INITIAL_SEARCH_QUERIES:
        try:
            resp = requests.get(query_url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            if resp.status_code == 200:
                urls = re.findall(r'https?://(?:raw\.githubusercontent\.com|(?:gitee\.com)/[^/]+/[^/]+/raw|gist\.github\.com/[^/]+/[^/]+/raw)/[^"\s]+(?:\.json|\.md|\.txt)', resp.text)
                new_urls.extend(urls)
            time.sleep(1)
        except Exception as e:
            print(f"动态检索失败 {query_url}: {e}")
    seen = set()
    unique_urls = []
    for url in new_urls:
        if url not in seen and ('tvbox' in url.lower() or 'vod' in url.lower()):
            seen.add(url)
            unique_urls.append(url)
            if len(unique_urls) >= 25:
                break
    return unique_urls

# 固定 RETRIEVE_URLS（67 个，扩展 + 工具搜索新源）
RETRIEVE_URLS = [
    "https://raw.githubusercontent.com/ngo5/IPTV/main/sources.json",
    "https://raw.githubusercontent.com/youhunwl/TVAPP/main/README.md",
    "https://raw.githubusercontent.com/Zhou-Li-Bin/Tvbox-QingNing/main/sources.json",
    "https://raw.githubusercontent.com/qist/tvbox/main/sources.json",
    "https://raw.githubusercontent.com/dongyubin/IPTV/main/sources.json",
    "https://raw.githubusercontent.com/gaotianliuyun/gao/main/sources.json",
    "https://raw.githubusercontent.com/tongxunlu/tvbox-tvb-gd/main/tvbox.json",
    "https://raw.githubusercontent.com/katelya77/KatelyaTV/main/api.json",
    "https://gitee.com/xuxiamu/xm/raw/master/xiamu.json",
    "https://gitee.com/guot54/ygbh666/raw/master/ygbh666.json",
    "https://raw.githubusercontent.com/Newtxin/TVBoxSource/main/cangku.json",
    "https://codeberg.org/sew132/666/raw/branch/main/666.json",
    "https://raw.githubusercontent.com/liu673cn/box/main/m.json",
    "https://raw.githubusercontent.com/yoursmile66/TVBox/main/XC.json",
    "https://gitee.com/itxve/fetch/raw/master/fly/fly.json",
    "https://gitee.com/ChenAnRong/tvbox-config/raw/master/tvbox.json",
    "https://raw.githubusercontent.com/vcloudc/tvbox/main/tw/api.json",
    "https://raw.githubusercontent.com/xyq254245/xyqonlinerule/main/XYQTVBox.json",
    "https://raw.githubusercontent.com/qist/tvbox/main/0821.json",
    "https://raw.githubusercontent.com/li5bo5/TVBox/main/sources.json",
    "https://down.nigx.cn/raw.githubusercontent.com/yuanwangokk-1/TV-BOX/refs/heads/main/tvbox/pg/jsm.json",
    "https://raw.githubusercontent.com/gaotianliuyun/gao/master/js.json",
    "https://gist.githubusercontent.com/qoli/0cac366634bfa3a4e6babc84e334b328/raw/VOD.json",
    "https://raw.githubusercontent.com/Archmage83/tvapk/main/README.md",
    "https://gitee.com/stbang/live-streaming-source/raw/master/dxaz.json",
    "https://raw.githubusercontent.com/kjxhb/Box/main/m.json",
    "https://raw.githubusercontent.com/programus/e7f3189da1451ca1f9ce42a0a77f459d/raw/box-config.json",
    "https://raw.githubusercontent.com/lyghgx/tv/main/README.md",
    "https://gitee.com/xlsn0w/tvbox-source-address/raw/master/sources.json",
    "https://raw.githubusercontent.com/jazzforlove/VShare/main/README.md",
    "https://raw.githubusercontent.com/Archmage83/tvapk/main/sources.json",
    "https://gitee.com/hepingwang/tvbox/raw/master/sources.json",
    "https://raw.githubusercontent.com/gitblog_00073/live/main/sources.json",
    "https://raw.githubusercontent.com/W5452136/tvbox/main/dxaz.json",
    "https://gitee.com/stbang/live-streaming-source/raw/master/live-qingtian.txt",
    "https://raw.githubusercontent.com/Newtxin/TVBoxSource/main/duocang.json",
    "https://raw.githubusercontent.com/qist/tvbox/master/jsm.json",
    "https://gitee.com/guot54/ygbh666/raw/master/tvbox.json",
    "https://raw.githubusercontent.com/dongyubin/IPTV/main/tvbox.json",
    "https://gitee.com/xuxiamu/xm/raw/master/tvbox.json",
    "https://raw.githubusercontent.com/gaotianliuyun/gao/main/tvbox.json",
    "https://raw.githubusercontent.com/tongxunlu/tvbox-tvb-gd/main/sources.json",
    "https://gitee.com/ChenAnRong/tvbox-config/raw/master/sources.json",
    "https://raw.githubusercontent.com/vcloudc/tvbox/main/sources.json",
    "https://raw.githubusercontent.com/yoursmile66/TVBox/main/sources.json",
    "https://gitee.com/itxve/fetch/raw/master/sources.json",
    "https://raw.githubusercontent.com/li5bo5/TVBox/main/tvbox.json",
    "https://raw.githubusercontent.com/Newtxin/TVBoxSource/main/sources.json",
    "https://codeberg.org/sew132/666/raw/branch/main/sources.json",
    "https://raw.githubusercontent.com/liu673cn/box/main/sources.json",
    "https://notabug.org/Tvbox123/TVbox-4/src/master/xq2.json",
    "https://gitlab.com/recha/TVBOX/-/blob/main/recha-media.json",
    "https://github.com/yuanwangokk-1/TV-BOX/raw/main/tvbox/pg/jsm.json",
    "https://raw.githubusercontent.com/stbang/live-streaming-source/main/dxaz.json",
    "https://gitee.com/sew132/666/raw/master/666.json",
    "https://gist.github.com/MrLYC/b2a03ae9e9fc2d86a7e2a269675a55fb/raw/tvbox.json",
    "https://gist.github.com/pigfoot/2ce619f3cfbbbecffbfa2d38d146c16e/raw/tvbox.json",
    "https://ghp.ci/https://raw.githubusercontent.com/vbskycn/tvbox/a244f6f5c08565a9a0e319d6a3cc2e919d05d893/MY探探.txt",
    # 新工具搜索提取 (2025 TVBox raw JSON)
    "https://raw.githubusercontent.com/qist/tvbox/master/jsm.json",  # qist jsm
    "https://gitee.com/stbang/live-streaming-source/raw/master/dxaz.json",  # stbang dxaz
    "https://raw.githubusercontent.com/Zhou-Li-Bin/Tvbox-QingNing/main/sources.json",  # Zhou-Li-Bin sources
    "https://raw.githubusercontent.com/zhbjzhql1/TVBox/main/duocang.json",  # zhbjzhql1 duocang
    "https://raw.githubusercontent.com/programus/e7f3189da1451ca1f9ce42a0a77f459d/raw/box-config.json"  # programus box-config
]

# 动态更新 RETRIEVE_URLS
print("动态更新 RETRIEVE_URLS...")
dynamic_urls = update_retrieve_urls()
RETRIEVE_URLS.extend(dynamic_urls[:10])  # 添加前 10 个新 URL
print(f"动态添加 {len(dynamic_urls)} 个新检索 URL，总 {len(RETRIEVE_URLS)} 个")

def fetch_new_sources() -> List[Dict[str, str]]:
    """从 RETRIEVE_URLS 检索新源（强化错误处理）"""
    new_sources = []
    for url in RETRIEVE_URLS:
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                if url.endswith('.md'):
                    lines = resp.text.split('\n')
                    for line in lines:
                        if 'name,' in line or 'api:' in line or '接口' in line:
                            parts = [p.strip() for p in line.split(',') if p.strip()]
                            if len(parts) >= 2:
                                name = parts[0].replace('name:', '').strip()
                                api = parts[1].replace('api:', '').strip()
                                detail = ' '.join(parts[2:]) if len(parts) > 2 else '2025 Dynamic VOD'
                                if 'vod' in api.lower() or 'tv' in api.lower() or 'api' in api.lower():
                                    new_sources.append({"name": name, "api": api, "detail": detail})
                else:
                    if 'api.php' in url:
                        new_sources.append({"name": "Dynamic API", "api": url, "detail": "2025 Retrieved VOD"})
                    else:
                        data = resp.json()
                        possible_keys = ['sites', 'list', 'api_list', 'sources', 'configs', 'interfaces']
                        for key in possible_keys:
                            if key in data and isinstance(data[key], list):
                                for item in data[key]:
                                    if isinstance(item, dict):
                                        name = item.get('name', item.get('title', 'Unknown'))
                                        api = item.get('api', item.get('url', ''))
                                        detail = item.get('detail', '2025 Dynamic VOD')
                                        if api:
                                            new_sources.append({"name": name, "api": api, "detail": detail})
                                break
                time.sleep(1)
        except json.JSONDecodeError as e:
            print(f"JSON 解析失败 {url}: {e} - 跳过")
        except requests.exceptions.RequestException as e:
            print(f"请求失败 {url}: {e} - 跳过")
        except Exception as e:
            print(f"未知错误 {url}: {e} - 跳过")
    # 去重限 40 个
    seen = set()
    unique_new = []
    for ns in new_sources:
        key = f"{ns['name']}-{ns['api']}"
        if key not in seen:
            seen.add(key)
            unique_new.append(ns)
            if len(unique_new) >= 40:
                break
    return unique_new

def test_api(api_url: str, name: str) -> str:
    """测试 API（修复 URL 协议，统一异常处理）"""
    # 修复：添加协议如果缺失
    if not api_url.startswith(('http://', 'https://')):
        api_url = 'https://' + api_url
    params = '?ac=videolist&wd=热门' if '?' not in api_url else '&ac=videolist&wd=热门'
    try:
        resp = requests.get(api_url + params, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
        if resp.status_code == 200 and len(resp.text) > 100:
            try:
                data = resp.json()
                if any(key in data for key in ['list', 'data', 'result', 'videos']):
                    return 'available'
            except json.JSONDecodeError:
                return 'available'
    except requests.exceptions.RequestException as e:
        print(f"请求异常 {name}: {e} - 跳过")
    except Exception:
        pass
    return 'failed'

# 主逻辑
with open('sources.json', 'r', encoding='utf-8') as f:
    sources = json.load(f)

api_site = sources['api_site']
updated_site = {}

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

with open('sources.json', 'w', encoding='utf-8') as f:
    json.dump(sources, f, ensure_ascii=False, indent=2)

with open('AVAILABLE_COUNT.txt', 'w') as f:
    f.write(str(sources['total_available']))

print(f"更新完成: {sources['total_available']} 可用源（添加 {added_count} 新源）。覆盖 sources.json")
