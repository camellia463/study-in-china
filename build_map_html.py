#!/usr/bin/env python3
"""
读取 china_provinces.json，生成完整的 templates/map.html。
"""
import json
import os

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

BASE_DIR = "/Users/lzx/Library/Application Support/TRAE SOLO CN/ModularData/ai-agent/work-mode-projects/6a65ceaa75373882f95e355d"
PROVINCES_JSON = os.path.join(BASE_DIR, "china_provinces.json")
MAP_HTML = os.path.join(BASE_DIR, "templates", "map.html")

MAP_TEMPLATE = '''{% extends "base.html" %}
{% block title %}九州学府地图 · 翼启神州{% endblock %}

{% block content %}
<section class="map-page">
  <div class="container">
    <div class="section-head" style="text-align: left; margin-bottom: 24px;">
      <div class="section-eyebrow" style="margin: 0 0 12px;">CHINA MAP</div>
      <h2 class="section-title" style="text-align: left;">九州学府 · 一图览尽</h2>
      <p class="section-sub" style="margin: 0;">点击版图上的朱红方印标记或省份边界，查看该省份 985 / 211 院校</p>
    </div>

    <div class="map-layout">
      <!-- 地图主区 -->
      <div class="map-canvas-wrap">
        <div class="map-title-row">
          <div>
            <div class="map-title">中华人民共和国 · 名校分布图</div>
            <div class="map-title-en">Distribution of 985 / 211 Universities in China</div>
          </div>
          <div style="display: flex; align-items: center; gap: 8px; color: var(--red); font-family: var(--serif); font-size: 13px;">
            <span style="width: 10px; height: 10px; background: var(--red); border: 1px solid var(--gold);"></span>
            院校方印
          </div>
        </div>
        <svg id="chinaMap" viewBox="0 0 1000 800" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <pattern id="paperPattern" x="0" y="0" width="40" height="40" patternUnits="userSpaceOnUse">
              <rect width="40" height="40" fill="rgba(245,237,217,.3)"/>
              <circle cx="20" cy="20" r="0.5" fill="rgba(157,41,51,.1)"/>
            </pattern>
            <linearGradient id="mapFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stop-color="#E6D4A8" stop-opacity="0.88"/>
              <stop offset="100%" stop-color="#D4BC85" stop-opacity="0.88"/>
            </linearGradient>
            <linearGradient id="mapFillSea" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stop-color="#C9D6E0" stop-opacity="0.4"/>
              <stop offset="100%" stop-color="#A8B6C2" stop-opacity="0.4"/>
            </linearGradient>
            <filter id="mapShadow" x="-5%" y="-5%" width="110%" height="110%">
              <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#9D2933" flood-opacity="0.25"/>
            </filter>
          </defs>

          <!-- 经纬度网格（淡） -->
          <g stroke="rgba(157,41,51,.06)" stroke-width="0.5" stroke-dasharray="2 4">
            <line x1="0" y1="200" x2="1000" y2="200"/>
            <line x1="0" y1="400" x2="1000" y2="400"/>
            <line x1="0" y1="600" x2="1000" y2="600"/>
            <line x1="250" y1="0" x2="250" y2="800"/>
            <line x1="500" y1="0" x2="500" y2="800"/>
            <line x1="750" y1="0" x2="750" y2="800"/>
          </g>

          <!-- 中国 34 省级行政区（来自阿里 DataV 真实 GeoJSON 简化） -->
          <g id="provincesLayer" filter="url(#mapShadow)">
__PROVINCE_PATHS__
          </g>

          <!-- 标题文字 -->
          <text x="500" y="60" text-anchor="middle" font-family="Songti SC, serif"
                font-size="22" fill="#9D2933" font-weight="700" letter-spacing="8">中　华　人　民　共　和　国</text>
          <text x="500" y="84" text-anchor="middle" font-family="Georgia, serif"
                font-size="11" fill="#A8862E" font-style="italic" letter-spacing="3">CHINA · 34 PROVINCES</text>

          <!-- 学校标记将在此处动态渲染 -->
          <g id="pinsLayer"></g>
        </svg>
      </div>

      <!-- 侧边栏：显示选中省份的学校 -->
      <aside class="map-sidebar" id="mapSidebar">
        <div class="sidebar-head" id="sidebarHead">全国院校</div>
        <div id="sidebarList"></div>
        <div class="sidebar-empty" id="sidebarEmpty" style="display: none;"></div>
      </aside>
    </div>
  </div>
</section>

<!-- 注入学校数据到 JS -->
<script id="uniData" type="application/json">{{ universities_json|safe }}</script>

{% endblock %}
'''

def main():
    with open(PROVINCES_JSON, "r", encoding="utf-8") as f:
        provinces = json.load(f)

    path_lines = []
    count = 0
    for p in provinces:
        full_name = p["name"]
        if full_name == "未知":
            continue
        short = NAME_MAP.get(full_name, full_name)
        d = " ".join(p["d"].split())
        line = (
            f'            <path data-province="{short}" data-full="{full_name}" '
            f'fill="url(#mapFill)" stroke="#9D2933" stroke-width="1.2" '
            f'stroke-linejoin="round" stroke-linecap="round" '
            f'd="{d}"/>'
        )
        path_lines.append(line)
        count += 1

    print(f"Province paths: {count}")
    content = MAP_TEMPLATE.replace("__PROVINCE_PATHS__", "\n".join(path_lines))

    with open(MAP_HTML, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Wrote {MAP_HTML} ({len(content)} chars)")

if __name__ == "__main__":
    main()
