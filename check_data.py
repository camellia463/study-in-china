"""校验 universities.json 数据：标签是否准确、图片是否对应"""
import json
import re

with open('data/universities.json', encoding='utf-8') as f:
    data = json.load(f)

print(f'Total universities: {len(data)}')

# C9 联盟（仅 9 所）
c9 = {
    '清华大学','北京大学','复旦大学','上海交通大学',
    '浙江大学','南京大学','中国科学技术大学','哈尔滨工业大学','西安交通大学'
}

# 39 所 985 工程大学
p985 = {
    '清华大学','北京大学','复旦大学','上海交通大学','浙江大学','南京大学',
    '中国科学技术大学','哈尔滨工业大学','西安交通大学','武汉大学','中山大学',
    '四川大学','山东大学','南开大学','天津大学','同济大学','厦门大学','东南大学',
    '北京航空航天大学','北京理工大学','华南理工大学','电子科技大学','重庆大学',
    '湖南大学','中南大学','大连理工大学','东北大学','吉林大学','兰州大学',
    '中国农业大学','西北农林科技大学','中央民族大学','国防科技大学','华东师范大学',
    '北京师范大学','中国人民大学','中国海洋大学','西北工业大学','华中科技大学','中央音乐学院'
}

issues = []

for u in data:
    name = u['name']
    tags = u.get('tags', [])
    has_c9 = 'C9' in tags
    has_985 = '985' in tags
    has_211 = '211' in tags

    if has_c9 and name not in c9:
        issues.append(f'[C9 错误] {name} 不该有 C9 标签，当前 tags={tags}')
    if not has_c9 and name in c9:
        issues.append(f'[C9 缺失] {name} 应有 C9 标签，当前 tags={tags}')
    if has_985 and name not in p985:
        issues.append(f'[985 错误] {name} 不是 985，当前 tags={tags}')
    if not has_985 and name in p985:
        issues.append(f'[985 缺失] {name} 应是 985，当前 tags={tags}')
    if has_985 and not has_211:
        issues.append(f'[211 缺失] {name} 是 985 必也是 211，当前 tags={tags}')

    # 检查图片 URL 是否包含学校英文名关键词
    badge = u.get('badge', '')
    campus = u.get('campus', '')
    name_en = u.get('name_en', '')
    if name_en:
        # 取英文校名首个单词（如 Tsinghua, Peking, Fudan）
        first = re.split(r'[\s,]', name_en)[0].lower()
        if first and first not in badge.lower():
            issues.append(f'[校徽不匹配] {name} badge URL 未包含 "{first}"')
        if first and first not in campus.lower():
            issues.append(f'[校园不匹配] {name} campus URL 未包含 "{first}"')

print(f'\n问题总数: {len(issues)}')
print('=' * 60)
for i in issues:
    print(i)
