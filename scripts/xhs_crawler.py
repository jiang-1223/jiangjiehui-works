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

# 尝试导入 playwright 用于签名
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("警告: playwright 库未安装，签名功能不可用")
    print("安装命令: pip install playwright && playwright install chromium")

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 搜索关键词列表
KEYWORDS = [
    "1型糖", "2型糖", "胰岛素泵", "CGM", "美敦力", "糖尿病",
    "1型糖尿病", "2型糖尿病", "血糖监测", "胰岛素", "糖友"
]

def init_sign():
    """
    使用 Playwright 初始化签名函数
    返回签名函数,用于XhsClient初始化
    """
    if not PLAYWRIGHT_AVAILABLE:
        logger.warning("Playwright 不可用,无法生成签名")
        return None

    def sign(data: str, **kwargs) -> dict:
        """签名函数,返回 x-s 和 x-t 参数
        注意：xhs 库会传入 a1 等参数，需要接受但忽略
        """
        with sync_playwright() as p:
            # 启动浏览器
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            try:
                # 访问小红书网站
                page.goto("https://www.xiaohongshu.com")
                time.sleep(2)  # 等待页面加载

                # 调用签名函数
                result = page.evaluate(f"window._webmsxyw('{data}')")

                # 提取签名参数
                x_s = result.get('x-s', '')
                x_t = result.get('x-t', str(int(time.time())))

                return {'x-s': x_s, 'x-t': x_t}

            finally:
                browser.close()

    return sign

# 从环境变量获取 Cookie
def get_cookie_from_env() -> Optional[Dict[str, str]]:
    """从环境变量获取 Cookie 字段"""
    a1 = os.getenv('XHS_A1')
    web_session = os.getenv('XHS_WEB_SESSION')
    web_id = os.getenv('XHS_WEB_ID')

    print(f"=== Cookie 环境变量检查 ===")
    print(f"XHS_A1: {'已设置' if a1 else '未设置'} (长度: {len(a1) if a1 else 0})")
    print(f"XHS_WEB_SESSION: {'已设置' if web_session else '未设置'} (长度: {len(web_session) if web_session else 0})")
    print(f"XHS_WEB_ID: {'已设置' if web_id else '未设置'} (长度: {len(web_id) if web_id else 0})")

    if not all([a1, web_session, web_id]):
        logger.warning("Cookie 环境变量不完整，请设置 XHS_A1, XHS_WEB_SESSION, XHS_WEB_ID")
        return None

    # 构建 Cookie 字符串
    cookie_str = f"a1={a1}; web_session={web_session}; webId={web_id}"
    print(f"Cookie 字符串长度: {len(cookie_str)}")

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
        # 初始化签名函数
        sign_func = init_sign()
        if sign_func:
            logger.info("签名函数初始化成功")
        else:
            logger.warning("签名函数初始化失败,可能无法正常调用API")

        # 根据 xhs 库的文档初始化客户端
        # 必须传入签名函数,否则 external_sign 为 None 导致调用失败
        client = XhsClient(
            cookie=cookie_info['cookie_str'],
            sign=sign_func,  # 传入签名函数
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            timeout=30
        )
        logger.info("XhsClient 初始化成功")
        print(f"客户端类型: {type(client)}")
        print(f"签名函数: {sign_func}")
        return client
    except Exception as e:
        logger.error(f"初始化 XhsClient 失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def search_notes(client: XhsClient, keyword: str, page: int = 1, limit: int = 20) -> List[Dict[str, Any]]:
    """搜索小红书笔记"""
    try:
        logger.info(f"搜索关键词: {keyword}, 页码: {page}")
        print(f"  调用 client.get_note_by_keyword(keyword='{keyword}', page={page}, page_size={limit})")

        # 调用正确的方法名：get_note_by_keyword
        result = client.get_note_by_keyword(keyword=keyword, page=page, page_size=limit)

        print(f"  API 返回结果类型: {type(result)}")
        print(f"  API 返回结果键: {result.keys() if isinstance(result, dict) else 'N/A'}")

        notes = []
        # 解析结果
        if result and 'items' in result:
            items = result['items']
            print(f"  找到 {len(items)} 个项目")
            for item in items[:limit]:
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
        else:
            print(f"  警告: result 为空或没有 'items' 键")
            print(f"  result 内容: {result}")

        logger.info(f"搜索到 {len(notes)} 条笔记")
        return notes
    except Exception as e:
        import traceback
        print(f"  ✗ 异常: {e}")
        print(f"  堆栈跟踪:\n{traceback.format_exc()}")
        logger.error(f"搜索失败 {keyword}: {e}")
        raise  # 重新抛出异常，不返回空列表

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
    """已删除模拟数据功能"""
    logger.error("不再使用模拟数据，请确保 Cookie 有效")
    return []

def main():
    """主函数"""
    logger.info("开始抓取小红书糖尿病相关笔记")
    
    all_notes = []
    
    # 检查 xhs 库是否可用
    if not XHS_AVAILABLE:
        raise Exception("xhs 库未安装，无法抓取数据。请安装: pip install xhs")
    
    # 获取 Cookie
    cookie_info = get_cookie_from_env()
    
    if not cookie_info:
        raise Exception("Cookie 未配置，无法抓取数据。请设置环境变量 XHS_A1, XHS_WEB_SESSION, XHS_WEB_ID")
    
    # 初始化客户端
    print("\n=== 初始化 xhs 客户端 ===")
    client = init_xhs_client(cookie_info)

    if not client:
        raise Exception("客户端初始化失败，无法抓取数据")

    print(f"客户端初始化成功: {type(client)}")

    # 遍历关键词搜索
    print("\n=== 开始搜索关键词 ===")
    success_count = 0
    fail_count = 0

    for i, keyword in enumerate(KEYWORDS, 1):
        print(f"\n[{i}/{len(KEYWORDS)}] 处理关键词: {keyword}")
        try:
            notes = search_notes(client, keyword, page=1, limit=10)
            print(f"  ✓ 成功获取 {len(notes)} 条笔记")
            all_notes.extend(notes)
            success_count += 1
        except Exception as e:
            print(f"  ✗ 失败: {e}")
            fail_count += 1

        # 避免请求过快
        time.sleep(2)

    print(f"\n=== 搜索完成 ===")
    print(f"成功: {success_count}/{len(KEYWORDS)}")
    print(f"失败: {fail_count}/{len(KEYWORDS)}")
    print(f"总笔记数: {len(all_notes)}")
    
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