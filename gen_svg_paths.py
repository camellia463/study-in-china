#!/usr/bin/env python3
"""
读取 china_provinces.json，把省份名标准化（北京市→北京），
生成完整的 SVG <path> HTML 片段写入 map_svg_paths.txt。
"""
import json

# 省份全名 → 短名（与 universities.json 中的 province 字段一致）
NAME_MAP = {
    "北京市": "北京",
    "天津市": "天津",
    "河北省": "河北",
    "山西省": "山西",
    "内蒙古自治区": "内蒙古",
    "辽宁省": "辽宁",
    "吉林省": "吉林",
    "黑龙江省": "黑龙江",
    "上海市": "上海",
    "江苏省": "江苏",
    "浙江省": "浙江",
    "安徽省": "安徽",
    "福建省": "福建",
    "江西省": "江西",
    "山东省": "山东",
    "河南省": "河南",
    "湖北省": "湖北",
    "湖南省": "湖南",
    "广东省": "广东",
    "广西壮族自治区": "广西",
    "海南省": "海南",
    "重庆市": "重庆",
    "四川省": "四川",
    "贵州省": "贵州",
    "云南省": "云南",
    "西藏自治区": "西藏",
    "陕西省": "陕西",
    "甘肃省": "甘肃",
    "青海省": "青海",
    "宁夏回族自治区": "宁夏",
    "新疆维吾尔自治区": "新疆",
    "台湾省": "台湾",
    "香港特别行政区": "香港",
    "澳门特别行政区": "澳门",
}

def main():
    with open("china_provinces.json", "r", encoding="utf-8") as f:
        provinces = json.load(f)

    lines = []
    count = 0
    for p in provinces:
        full_name = p["name"]
        if full_name == "未知":
            # 南海诸岛 / 九段线 - 跳过
            continue
        short = NAME_MAP.get(full_name, full_name)
        d = p["d"]
        # 每个 path: data-province + 默认填充 + 朱红描边
        line = (
            f'          <path data-province="{short}" data-full="{full_name}" '
            f'fill="url(#mapFill)" stroke="#9D2933" stroke-width="1.2" '
            f'stroke-linejoin="round" stroke-linecap="round" '
            f'd="{d}"/>'
        )
        lines.append(line)
        count += 1

    print(f"Generated {count} province <path> elements")

    # 保存为文本文件以便嵌入到 map.html
    with open("map_svg_paths.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("Saved map_svg_paths.txt")

if __name__ == "__main__":
    main()
