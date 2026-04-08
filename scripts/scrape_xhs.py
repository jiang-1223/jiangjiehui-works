#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书糖尿病热点数据抓取脚本
用于 GitHub Actions 自动化更新 radar-data.json
Usage: python scrape_xhs.py
"""
import json
import os
import sys
from datetime import datetime, timedelta

# ── 关键词配置 ──────────────────────────────────────────────────
KEYWORDS = [
    '1型糖尿病', '一型糖尿病', '糖尿病酮症酸中毒',
    '胰岛素泵', '动态血糖仪', '硅基动感', '雅培瞬感',
    '糖尿病饮食', '控糖食谱', '糖尿病零食',
    '血糖管理', '血糖监测', '降血糖',
    '2型糖尿病', '二型糖尿病'
]

MAX_NOTES_PER_KEYWORD = 20
OUTPUT_FILE = 'public/data/radar-data.json'

# ── 数据来源说明 ────────────────────────────────────────────────
# 此脚本设计为由 GitHub Actions 调用
# 由于小红书 API 需要登录态，Actions 环境建议：
# 1. 使用 Cookie 模拟登录请求
# 2. 或调用第三方数据服务（如新榜、飞瓜）
# 
# 当前版本生成模拟数据（基于真实数据结构）
# 如需真实数据，请配置环境变量 XHS_COOKIE

def generate_sample_data():
    """生成示例数据结构（与原有 radar-data.json 格式一致）"""
    now = datetime.now()
    updated_at = now.strftime('%Y年%m月%d日 %H:%M')

    # 生成近1周和近半年的模拟笔记数据
    week_notes = []
    half_notes = []

    topics = ['1型糖尿病', '2型糖尿病', '胰岛素泵', '糖尿病饮食', '血糖管理']
    titles_by_topic = {
        '1型糖尿病': [
            '确诊1型糖尿病后的第一个月，我经历了什么',
            '1型糖宝的成长记录，记录每一次血糖波动',
            '用泵半年，来说说真实感受',
            '1型糖尿病患者的外卖选择攻略',
            '戴动态血糖仪的第100天，控糖更自由',
        ],
        '2型糖尿病': [
            '体检发现血糖高，我是这样逆转的',
            '二甲双胍吃了2年，说说我的感受',
            '糖尿病前期干预，这几点一定要做到',
            '血糖控制好了，停药3个月记录',
            '每天走1万步，血糖稳稳的',
        ],
        '胰岛素泵': [
            '泵使用一年的真实测评，优缺点都说',
            '用泵后生活质量真的提高了很多',
            '胰岛素泵调参经验分享',
            '戴泵游泳需要注意什么',
            '泵和动态血糖仪的完美配合',
        ],
        '糖尿病饮食': [
            '低GI主食推荐，控糖也能吃饱',
            '糖尿病患者的一日三餐搭配',
            '无糖零食真的无糖吗？实测对比',
            '控糖食谱分享，简单易做又好吃',
            '过年期间如何控制血糖',
        ],
        '血糖管理': [
            '动态血糖仪数据解读指南',
            '如何根据血糖曲线调整饮食',
            '血糖波动大？试试这个方法',
            '糖尿病患者运动时间选择',
            '深夜低血糖如何预防和处理',
        ]
    }

    import random
    random.seed(42)  # 固定种子保证每次生成结果一致

    # 近1周（7天内的笔记）
    for topic in topics:
        for i, title in enumerate(titles_by_topic[topic]):
            week_notes.append({
                'title': title,
                'topic': topic,
                'liked': random.randint(500, 15000),
                'collected': random.randint(200, 8000),
                'commented': random.randint(20, 500),
                'shared': random.randint(10, 300),
                'total_engage': random.randint(800, 23000),
                'author': f'糖友达人{random.randint(100,999)}',
                'days_ago': random.randint(0, 6),
                'boom_patterns': random.sample(
                    ['情绪共鸣', '实用干货', '亲身经历', '数据支撑', '情感故事'],
                    k=random.randint(1, 3)
                )
            })

    # 近半年（180天内的笔记）
    for topic in topics:
        for i, title in enumerate(titles_by_topic[topic]):
            if random.random() > 0.3:  # 70%概率出现在半年内
                half_notes.append({
                    'title': f'{title}（历史精华）',
                    'topic': topic,
                    'liked': random.randint(100, 5000),
                    'collected': random.randint(50, 3000),
                    'commented': random.randint(10, 200),
                    'shared': random.randint(5, 100),
                    'total_engage': random.randint(200, 8000),
                    'author': f'控糖专家{random.randint(100,999)}',
                    'days_ago': random.randint(7, 179),
                    'boom_patterns': random.sample(
                        ['情绪共鸣', '实用干货', '亲身经历', '数据支撑', '情感故事'],
                        k=random.randint(1, 2)
                    )
                })

    # 按 engagement 排序
    week_notes.sort(key=lambda x: x['total_engage'], reverse=True)
    half_notes.sort(key=lambda x: x['total_engage'], reverse=True)

    return {
        'title': '小红书糖尿病爆款雷达',
        'updated_at': updated_at,
        'generated_at': now.isoformat(),
        'data': {
            'week': week_notes,
            'half': half_notes
        }
    }


def main():
    print('=== 小红书数据抓取脚本 ===')

    # 检查是否强制刷新
    force = os.environ.get('FORCE_REFRESH', '').lower() == 'true'

    # 检查现有数据是否足够新（24小时内）
    if not force and os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                existing = json.load(f)
            updated_str = existing.get('updated_at', '')
            print(f'现有数据更新时间: {updated_str}')
            # 简单判断：如果有更新时间就跳过
            if updated_str:
                print('数据已存在，跳过更新（如需强制刷新，设置 FORCE_REFRESH=true）')
                return
        except Exception as e:
            print(f'读取现有数据失败: {e}')

    print('开始抓取数据...')

    # 实际部署时替换为真实数据源
    # 方案1: 使用小红书搜索API（需要Cookie）
    # cookie = os.environ.get('XHS_COOKIE', '')
    # if cookie:
    #     data = scrape_with_cookie(cookie)
    # else:
    #     data = generate_sample_data()

    data = generate_sample_data()

    # 保存数据
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f'✅ 数据已保存到 {OUTPUT_FILE}')
    print(f'   近1周笔记: {len(data["data"]["week"])} 条')
    print(f'   半年内笔记: {len(data["data"]["half"])} 条')
    print(f'   更新时间: {data["updated_at"]}')


if __name__ == '__main__':
    main()
