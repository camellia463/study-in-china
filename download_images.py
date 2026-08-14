#!/usr/bin/env python3
"""从 Wikipedia API 下载真实大学校园照片和校徽"""
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

# Wikipedia 英文页面名映射
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
}

def wiki_api(action, params):
    base = "https://en.wikipedia.org/w/api.php"
    params["action"] = action
    params["format"] = "json"
    url = base + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "Victell/1.0"})
    with urllib.request.urlopen(req, context=ssl_ctx, timeout=15) as resp:
        return json.loads(resp.read())

def get_page_image_url(wiki_name):
    """获取 Wikipedia 页面主图 URL（640px 宽）"""
    try:
        data = wiki_api("query", {
            "prop": "pageimages",
            "titles": wiki_name,
            "pithumbsize": "640",
            "pilimit": "1"
        })
        pages = data.get("query", {}).get("pages", {})
        for pid, page in pages.items():
            thumb = page.get("thumbnail")
            if thumb:
                return thumb["source"]
    except Exception as e:
        print(f"  Wikipedia API 失败: {e}")
    return None

def get_page_images(wiki_name):
    """获取 Wikipedia 页面的所有图片"""
    try:
        data = wiki_api("query", {
            "prop": "images",
            "titles": wiki_name,
            "imlimit": "20"
        })
        pages = data.get("query", {}).get("pages", {})
        images = []
        for pid, page in pages.items():
            for img in page.get("images", []):
                title = img["title"]
                # 排除 logo、svg、icon、seal
                low = title.lower()
                if any(w in low for w in ["logo", "svg", "icon", "seal", "badge", "emblem", "coat", "shield", "map", "flag", "location"]):
                    continue
                images.append(title)
        return images
    except Exception as e:
        print(f"  Wikipedia images API 失败: {e}")
        return []

def get_image_url(image_title, width=800):
    """获取 Wikimedia 图片的实际 URL"""
    try:
        data = wiki_api("query", {
            "prop": "imageinfo",
            "titles": image_title,
            "iiprop": "url",
            "iiurlwidth": str(width)
        })
        pages = data.get("query", {}).get("pages", {})
        for pid, page in pages.items():
            for info in page.get("imageinfo", []):
                return info.get("thumburl") or info.get("url")
    except Exception as e:
        print(f"    获取图片 URL 失败: {e}")
    return None

def download_image(url, filepath):
    """下载图片到本地"""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Victell/1.0"})
        with urllib.request.urlopen(req, context=ssl_ctx, timeout=20) as resp:
            with open(filepath, "wb") as f:
                f.write(resp.read())
        size = os.path.getsize(filepath)
        if size < 1000:
            os.remove(filepath)
            return False
        return True
    except Exception as e:
        print(f"    下载失败: {e}")
        return False

def main():
    # 加载数据
    data_path = os.path.join(os.path.dirname(__file__), "data", "universities.json")
    with open(data_path, "r", encoding="utf-8") as f:
        universities = json.load(f)
    
    updated = 0
    for u in universities:
        name = u["name"]
        if name not in WIKI_NAMES:
            continue
        
        wiki_name = WIKI_NAMES[name]
        uid = u["id"]
        print(f"\n[{uid}] {name} ({wiki_name})")
        
        # 1. 尝试获取 campus 照片
        campus_path = os.path.join(IMG_DIR, f"campus_{uid}.jpg")
        campus_updated = False
        
        if not os.path.exists(campus_path):
            # 先尝试页面主图
            img_url = get_page_image_url(wiki_name)
            if img_url:
                print(f"  主图: {img_url[:80]}...")
                if download_image(img_url, campus_path):
                    print(f"  校园照片已保存: campus_{uid}.jpg ({os.path.getsize(campus_path)} bytes)")
                    campus_updated = True
            
            # 如果主图没有或太小，尝试其他图片
            if not campus_updated:
                images = get_page_images(wiki_name)
                for img_title in images[:5]:
                    if campus_updated:
                        break
                    img_url = get_image_url(img_title, 800)
                    if img_url:
                        print(f"  尝试图片: {img_title}")
                        if download_image(img_url, campus_path):
                            print(f"  校园照片已保存: campus_{uid}.jpg")
                            campus_updated = True
                            break
        
        if campus_updated:
            u["campus"] = f"/static/img/universities/campus_{uid}.jpg"
            updated += 1
        
        time.sleep(0.5)  # 避免请求过快
    
    # 保存更新后的数据
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(universities, f, ensure_ascii=False, indent=2)
    
    print(f"\n完成！共更新 {updated} 所大学的图片")

if __name__ == "__main__":
    main()