import json
import requests
import time  # 新增：速率限制
from datetime import datetime
from typing import Dict, Any

# 加载 sources JSON
with open('sources.json', 'r', encoding='utf-8') as f:
    sources = json.load(f)

api_site = sources.get('api_site', {})
cache_time = sources.get('cache_time', 0)

# 准备合并数据
merged_videos = {
    'crawl_date': datetime.now().isoformat(),
    'total_sources': len(api_site),
    'sources_fetched': 0,
    'videos': [],
    'failed_sources': []
}

# 模拟浏览器头部
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def fetch_api_data(api_url: str, api_name: str) -> Dict[str, Any]:
    """从单个 API 获取 JSON 并提取视频列表（优化：检查可播放 URL）。"""
    try:
        response = requests.get(api_url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # 标准 VOD 结构：'list' 键
        video_list = data.get('list', []) if isinstance(data, dict) else []
        playable_videos = []
        if isinstance(video_list, list):
            for item in video_list:
                if isinstance(item, dict):
                    # 新增：过滤可播放视频（有 'vod_play_url' 或 'player' 键）
                    if 'vod_play_url' in item or 'player' in item or any('url' in k for k in item.keys()):
                        item['source'] = api_name
                        item['api_url'] = api_url
                        playable_videos.append(item)
            video_list = playable_videos
        
        if len(video_list) > 0:
            return {'name': api_name, 'videos': video_list, 'status': 'success', 'count': len(video_list)}
        else:
            return {'name': api_name, 'videos': [], 'status': 'no_videos'}
    except Exception as e:
        return {'name': api_name, 'error': str(e), 'status': 'failed'}

# 爬取所有 API（新增：1 秒延迟，避免封禁）
for key, config in api_site.items():
    api_name = config.get('name', key)
    api_url = config.get('api', '')
    if not api_url:
        continue
    
    print(f"正在爬取 {api_name} 从 {api_url}")
    result = fetch_api_data(api_url, api_name)
    
    if result.get('status') == 'success':
        merged_videos['videos'].extend(result['videos'])
        merged_videos['sources_fetched'] += 1
        print(f"成功：{api_name} - {result['count']} 个视频")
    else:
        merged_videos['failed_sources'].append(result)
        print(f"失败：{api_name} - {result.get('error', '未知错误')}")
    
    time.sleep(1)  # 速率限制

# 生成文件名（使用当前日期 2025-11-14）
date_str = datetime.now().strftime('%Y-%m-%d')  # 输出 videos-2025-11-14.json
filename = f'videos-{date_str}.json'

# 保存（去重视频 ID，如果有）
unique_videos = []
seen_ids = set()
for video in merged_videos['videos']:
    vid = video.get('vod_id', '')
    if vid not in seen_ids:
        seen_ids.add(vid)
        unique_videos.append(video)
merged_videos['videos'] = unique_videos

with open(filename, 'w', encoding='utf-8') as f:
    json.dump(merged_videos, f, ensure_ascii=False, indent=2)

print(f"完成爬取：{merged_videos['sources_fetched']} 个源，{len(merged_videos['videos'])} 个唯一视频。")
print(f"保存至 {filename}")
