#!/usr/bin/env python3
"""
小红书糖尿病关键词笔记抓取脚本
使用 xhs 库，需要配置 Cookie 环境变量
"""

import os
import json
import time
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

# 尝试导入 xhs 库
try:
    from xhs import XhsClient
    XHS_AVAILABLE = True
except ImportError:
    XHS_AVAILABLE = False
    print("警告: xhs 库未安装，将使用模拟数据")
    print("安装命令: pip install xhs")

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 搜索关键词列表
KEYWORDS = [
    "1型糖", "2型糖", "胰岛素泵", "CGM", "美敦力", "糖尿病",
    "1型糖尿病", "2型糖尿病", "血糖监测", "胰岛素", "糖友"
]

# 从环境变量获取 Cookie
def get_cookie_from_env() -> Optional[Dict[str, str]]:
    """从环境变量获取 Cookie 字段"""
    a1 = os.getenv('XHS_A1')
    web_session = os.getenv('XHS_WEB_SESSION')
    web_id = os.getenv('XHS_WEB_ID')
    
    if not all([a1, web_session, web_id]):
        logger.warning("Cookie 环境变量不完整，请设置 XHS_A1, XHS_WEB_SESSION, XHS_WEB_ID")
        return None
    
    # 构建 Cookie 字符串
    cookie_str = f"a1={a1}; web_session={web_session}; webId={web_id}"
    
    # 返回 Cookie 字典
    return {
        'a1': a1,
        'web_session': web_session,
        'webId': web_id,
        'cookie_str': cookie_str
    }

def init_xhs_client(cookie_info: Dict[str, str]) -> Optional[XhsClient]:
    """初始化 XhsClient"""
    try:
        # 根据 xhs 库的文档初始化客户端
        # 注意：可能需要额外的参数，如签名服务地址
        # 这里使用最简单的初始化方式
        client = XhsClient(
            cookie=cookie_info['cookie_str'],
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            timeout=30
        )
        logger.info("XhsClient 初始化成功")
        return client
    except Exception as e:
        logger.error(f"初始化 XhsClient 失败: {e}")
        return None

def search_notes(client: XhsClient, keyword: str, page: int = 1, limit: int = 20) -> List[Dict[str, Any]]:
    """搜索小红书笔记"""
    try:
        logger.info(f"搜索关键词: {keyword}, 页码: {page}")
        # 调用搜索方法，具体方法名需要参考 xhs 库文档
        # 假设方法名为 search_notes
        result = client.search_notes(keyword=keyword, page=page)
        
        notes = []
        # 解析结果，具体结构需要参考实际返回数据
        if result and 'items' in result:
            for item in result['items'][:limit]:
                note = {
                    'note_id': item.get('note_id', ''),
                    'title': item.get('title', ''),
                    'desc': item.get('desc', ''),
                    'user': item.get('user', {}),
                    'likes': item.get('likes', 0),
                    'collects': item.get('collects', 0),
                    'comments': item.get('comments', 0),
                    'time': item.get('time', 0),
                    'keyword': keyword,
                    'url': f"https://www.xiaohongshu.com/explore/{item.get('note_id', '')}"
                }
                notes.append(note)
        
        logger.info(f"搜索到 {len(notes)} 条笔记")
        return notes
    except Exception as e:
        logger.error(f"搜索失败 {keyword}: {e}")
        return []

def get_note_detail(client: XhsClient, note_id: str) -> Optional[Dict[str, Any]]:
    """获取笔记详情"""
    try:
        # 假设方法名为 get_note_detail
        detail = client.get_note_detail(note_id)
        return detail
    except Exception as e:
        logger.error(f"获取笔记详情失败 {note_id}: {e}")
        return None

def generate_mock_data() -> List[Dict[str, Any]]:
    """生成模拟数据（用于测试）"""
    mock_notes = []
    for i, keyword in enumerate(KEYWORDS[:3]):
        for j in range(5):
            note_id = f"mock_{i}_{j}"
            mock_notes.append({
                'note_id': note_id,
                'title': f"{keyword} 相关笔记 {j+1}",
                'desc': f"这是关于{keyword}的测试笔记内容，用于演示数据抓取功能。",
                'user': {
                    'user_id': f"user_{i}_{j}",
                    'nickname': f"测试用户{i}_{j}"
                },
                'likes': (i + j) * 10,
                'collects': (i + j) * 5,
                'comments': (i + j) * 3,
                'time': int(time.time()) - (i * 1000 + j * 100),
                'keyword': keyword,
                'url': f"https://www.xiaohongshu.com/explore/{note_id}"
            })
    return mock_notes

def main():
    """主函数"""
    logger.info("开始抓取小红书糖尿病相关笔记")
    
    all_notes = []
    
    # 检查 xhs 库是否可用
    if not XHS_AVAILABLE:
        logger.warning("xhs 库未安装，使用模拟数据")
        all_notes = generate_mock_data()
    else:
        # 获取 Cookie
        cookie_info = get_cookie_from_env()
        
        if not cookie_info:
            logger.warning("Cookie 未配置，使用模拟数据")
            all_notes = generate_mock_data()
        else:
            # 初始化客户端
            client = init_xhs_client(cookie_info)
            
            if not client:
                logger.warning("客户端初始化失败，使用模拟数据")
                all_notes = generate_mock_data()
            else:
                # 遍历关键词搜索
                for keyword in KEYWORDS:
                    logger.info(f"处理关键词: {keyword}")
                    notes = search_notes(client, keyword, page=1, limit=10)
                    
                    # 可选：获取每条笔记的详情
                    for note in notes:
                        # 可以在这里调用 get_note_detail 获取更多信息
                        # detail = get_note_detail(client, note['note_id'])
                        # if detail:
                        #     note.update(detail)
                        pass
                    
                    all_notes.extend(notes)
                    
                    # 避免请求过快
                    time.sleep(2)
    
    # 按点赞数排序
    all_notes.sort(key=lambda x: x.get('likes', 0), reverse=True)
    
    # 转换数据格式以匹配 HTML 报告
    formatted_notes = []
    for note in all_notes:
        # 提取作者信息
        user = note.get('user', {})
        author = user.get('nickname', '') if isinstance(user, dict) else str(user)
        
        # 确定内容类型（默认为图文）
        note_type = 'video' if note.get('type') == 'video' else '图文'
        
        # 构建封面图 URL（如果没有，使用占位符）
        cover = note.get('cover') or note.get('image_url') or ''
        
        formatted_notes.append({
            'title': note.get('title', '无标题'),
            'desc': note.get('desc', ''),
            'author': author,
            'time': note.get('time', int(time.time())),
            'likes': note.get('likes', 0),
            'collects': note.get('collects', 0),
            'comments': note.get('comments', 0),
            'type': note_type,
            'cover': cover,
            'url': note.get('url', ''),
            'keyword': note.get('keyword', '')
        })
    
    # 保存数据到 JSON 文件
    output_data = {
        'updatedAt': datetime.now().isoformat(),
        'keywords': KEYWORDS,
        'notes': formatted_notes,
        'stats': {
            'totalNotes': len(formatted_notes)
        }
    }
    
    # 确定输出路径
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'public', 'data')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'radar-data-v4.json')
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"数据抓取完成，共 {len(formatted_notes)} 条笔记")
    logger.info(f"数据已保存到: {output_path}")
    
    # 也保存一份到 assets/reports 目录（用于 GitHub 存档）
    assets_dir = os.path.join(os.path.dirname(__file__), '..', 'assets', 'reports')
    os.makedirs(assets_dir, exist_ok=True)
    assets_path = os.path.join(assets_dir, 'xhs_diabetes_data.json')
    
    with open(assets_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"存档数据已保存到: {assets_path}")
    
    return formatted_notes

if __name__ == "__main__":
    main()