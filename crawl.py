import json
import requests
from datetime import datetime
from typing import Dict, Any

# 加载 sources JSON
with open('sources.json', 'r', encoding='utf-8') as f:
    sources = json.load(f)

api_site = sources.get('api_site', {})
cache_time = sources.get('cache_time', 0)  # 未使用，但保留以备参考

# 准备合并数据
merged_videos = {
    'crawl_date': datetime.now().isoformat(),
    'total_sources': len(api_site),
    'sources_fetched': 0,
    'videos': [],
    'failed_sources': []
}

# 模拟浏览器头部（有助于某些 API）
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def fetch_api_data(api_url: str, api_name: str) -> Dict[str, Any]:
    """从单个 API 获取 JSON 并提取视频列表。"""
    try:
        response = requests.get(api_url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # 假设标准 VOD API 结构：查找 'list' 键中的视频项
        video_list = data.get('list', []) if isinstance(data, dict) else []
        if isinstance(video_list, list) and len(video_list) > 0:
            # 为每个视频添加来源信息
            for item in video_list:
                if isinstance(item, dict):
                    item['source'] = api_name
                    item['api_url'] = api_url
            return {'name': api_name, 'videos': video_list, 'status': 'success'}
        else:
            return {'name': api_name, 'videos': [], 'status': 'no_videos'}
    except Exception as e:
        return {'name': api_name, 'error': str(e), 'status': 'failed'}

# 爬取所有 API
for key, config in api_site.items():
    api_name = config.get('name', key)
    api_url = config.get('api', '')
    if not api_url:
        continue  # 跳过无 API URL 的项
    
    print(f"Fetching {api_name} from {api_url}")
    result = fetch_api_data(api_url, api_name)
    
    if result.get('status') == 'success':
        merged_videos['videos'].extend(result['videos'])
        merged_videos['sources_fetched'] += 1
    else:
        merged_videos['failed_sources'].append(result)
        print(f"Failed: {api_name} - {result.get('error', 'Unknown error')}")

# 生成带日期的文件名（UTC，但使用本地时间以简化）
date_str = datetime.now().strftime('%Y-%m-%d')
filename = f'videos-{date_str}.json'

# 保存合并数据
with open(filename, 'w', encoding='utf-8') as f:
    json.dump(merged_videos, f, ensure_ascii=False, indent=2)

print(f"Crawled {merged_videos['sources_fetched']} sources, {len(merged_videos['videos'])} total videos.")
print(f"Saved to {filename}")
