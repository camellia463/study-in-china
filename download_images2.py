#!/usr/bin/env python3
"""从 Wikipedia 下载剩余大学校园照片（续）"""
import json
import os
import urllib.request
import urllib.parse
import time
import ssl

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

IMG_DIR = os.path.join(os.path.dirname(__file__), "static", "img", "universities")
os.makedirs(IMG_DIR, exist_ok=True)

# 所有大学 Wikipedia 页面名映射
WIKI_NAMES = {
    "清华大学": "Tsinghua_University",
    "北京大学": "Peking_University",
    "复旦大学": "Fudan_University",
    "上海交通大学": "Shanghai_Jiao_Tong_University",
    "浙江大学": "Zhejiang_University",
    "南京大学": "Nanjing_University",
    "中国科学技术大学": "University_of_Science_and_Technology_of_China",
    "哈尔滨工业大学": "Harbin_Institute_of_Technology",
    "西安交通大学": "Xi'an_Jiaotong_University",
    "武汉大学": "Wuhan_University",
    "中山大学": "Sun_Yat-sen_University",
    "四川大学": "Sichuan_University",
    "山东大学": "Shandong_University",
    "南开大学": "Nankai_University",
    "天津大学": "Tianjin_University",
    "同济大学": "Tongji_University",
    "厦门大学": "Xiamen_University",
    "东南大学": "Southeast_University_(China)",
    "北京航空航天大学": "Beihang_University",
    "北京理工大学": "Beijing_Institute_of_Technology",
    "华南理工大学": "South_China_University_of_Technology",
    "电子科技大学": "University_of_Electronic_Science_and_Technology_of_China",
    "重庆大学": "Chongqing_University",
    "湖南大学": "Hunan_University",
    "中南大学": "Central_South_University_(China)",
    "大连理工大学": "Dalian_University_of_Technology",
    "东北大学": "Northeastern_University_(China)",
    "吉林大学": "Jilin_University",
    "兰州大学": "Lanzhou_University",
    "中国农业大学": "China_Agricultural_University",
    "华东师范大学": "East_China_Normal_University",
    "北京师范大学": "Beijing_Normal_University",
    "中国人民大学": "Renmin_University_of_China",
    "华中科技大学": "Huazhong_University_of_Science_and_Technology",
    "西北农林科技大学": "Northwest_A%26F_University",
    "中央民族大学": "Minzu_University_of_China",
    "国防科技大学": "National_University_of_Defense_Technology",
    "中国海洋大学": "Ocean_University_of_China",
    "西北工业大学": "Northwestern_Polytechnical_University",
    "中央音乐学院": "Central_Conservatory_of_Music",
    "苏州大学": "Soochow_University_(Suzhou)",
    "北京交通大学": "Beijing_Jiaotong_University",
    "北京邮电大学": "Beijing_University_of_Posts_and_Telecommunications",
    "中国传媒大学": "Communication_University_of_China",
    "中央财经大学": "Central_University_of_Finance_and_Economics",
    "对外经济贸易大学": "University_of_International_Business_and_Economics_(Beijing)",
    "北京外国语大学": "Beijing_Foreign_Studies_University",
    "上海财经大学": "Shanghai_University_of_Finance_and_Economics",
    "西南大学": "Southwest_University_(China)",
    "郑州大学": "Zhengzhou_University",
    "云南大学": "Yunnan_University",
    "新疆大学": "Xinjiang_University",
    "广西大学": "Guangxi_University",
    "海南大学": "Hainan_University",
    "南昌大学": "Nanchang_University",
    "贵州大学": "Guizhou_University",
    "内蒙古大学": "Inner_Mongolia_University",
    "宁夏大学": "Ningxia_University",
    "石河子大学": "Shihezi_University",
    "延边大学": "Yanbian_University",
    "北京工业大学": "Beijing_University_of_Technology",
    "北京科技大学": "University_of_Science_and_Technology_Beijing",
    "北京化工大学": "Beijing_University_of_Chemical_Technology",
    "北京林业大学": "Beijing_Forestry_University",
    "北京中医药大学": "Beijing_University_of_Chinese_Medicine",
    "北京体育大学": "Beijing_Sport_University",
    "华北电力大学": "North_China_Electric_Power_University",
    "中国矿业大学（北京）": "China_University_of_Mining_and_Technology",
    "中国石油大学（北京）": "China_University_of_Petroleum_(Beijing)",
    "中国地质大学（北京）": "China_University_of_Geosciences_(Beijing)",
    "中国政法大学": "China_University_of_Political_Science_and_Law",
    "中央戏剧学院": "Central_Academy_of_Drama",
    "中央美术学院": "Central_Academy_of_Fine_Arts_(China)",
    "东华大学": "Donghua_University",
    "华东理工大学": "East_China_University_of_Science_and_Technology",
    "上海大学": "Shanghai_University",
    "上海外国语大学": "Shanghai_International_Studies_University",
    "上海中医药大学": "Shanghai_University_of_Traditional_Chinese_Medicine",
    "上海音乐学院": "Shanghai_Conservatory_of_Music",
    "上海体育大学": "Shanghai_University_of_Sport",
    "南京理工大学": "Nanjing_University_of_Science_and_Technology",
    "南京航空航天大学": "Nanjing_University_of_Aeronautics_and_Astronautics",
    "河海大学": "Hohai_University",
    "江南大学": "Jiangnan_University",
    "南京农业大学": "Nanjing_Agricultural_University",
    "中国药科大学": "China_Pharmaceutical_University",
    "南京师范大学": "Nanjing_Normal_University",
}

def wiki_api(action, params):
    base = "https://en.wikipedia.org/w/api.php"
    params["action"] = action
    params["format"] = "json"
    url = base + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "Victell/1.0 (educational)"})
    with urllib.request.urlopen(req, context=ssl_ctx, timeout=15) as resp:
        return json.loads(resp.read())

def get_page_image_url(wiki_name):
    try:
        data = wiki_api("query", {
            "prop": "pageimages",
            "titles": wiki_name,
            "pithumbsize": "800",
            "pilimit": "1"
        })
        pages = data.get("query", {}).get("pages", {})
        for pid, page in pages.items():
            thumb = page.get("thumbnail")
            if thumb:
                return thumb["source"]
    except:
        pass
    return None

def download_image(url, filepath):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Victell/1.0"})
        with urllib.request.urlopen(req, context=ssl_ctx, timeout=20) as resp:
            with open(filepath, "wb") as f:
                f.write(resp.read())
        size = os.path.getsize(filepath)
        if size < 2000:
            os.remove(filepath)
            return False
        return True
    except:
        return False

def main():
    data_path = os.path.join(os.path.dirname(__file__), "data", "universities.json")
    with open(data_path, "r", encoding="utf-8") as f:
        universities = json.load(f)
    
    updated = 0
    for u in universities:
        name = u["name"]
        uid = u["id"]
        campus_path = os.path.join(IMG_DIR, f"campus_{uid}.jpg")
        
        # 跳过已下载的
        if os.path.exists(campus_path) and os.path.getsize(campus_path) > 2000:
            u["campus"] = f"/static/img/universities/campus_{uid}.jpg"
            continue
        
        if name not in WIKI_NAMES:
            continue
        
        wiki_name = WIKI_NAMES[name]
        print(f"[{uid}] {name} -> {wiki_name}", flush=True)
        
        time.sleep(2)  # 增加延迟避免限流
        
        img_url = get_page_image_url(wiki_name)
        if img_url:
            print(f"  下载: {img_url[:80]}...", flush=True)
            if download_image(img_url, campus_path):
                u["campus"] = f"/static/img/universities/campus_{uid}.jpg"
                print(f"  成功! ({os.path.getsize(campus_path)} bytes)", flush=True)
                updated += 1
            else:
                print(f"  下载失败", flush=True)
        else:
            print(f"  无图片", flush=True)
    
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(universities, f, ensure_ascii=False, indent=2)
    
    print(f"\n新增 {updated} 所大学图片")

if __name__ == "__main__":
    main()