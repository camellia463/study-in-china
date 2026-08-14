#!/usr/bin/env python3
"""从 Wikipedia / Unsplash 下载所有大学真实校园照片 — 全覆盖版"""
import json
import os
import urllib.request
import urllib.parse
import time
import ssl
import re

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

IMG_DIR = os.path.join(os.path.dirname(__file__), "static", "img", "universities")
os.makedirs(IMG_DIR, exist_ok=True)

# 所有 175 所大学的 Wikipedia 英文页面名（自动从英文名推导 + 特殊修正）
SPECIAL_WIKI_NAMES = {
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
    "东南大学": "Southeast_University",
    "北京航空航天大学": "Beihang_University",
    "北京理工大学": "Beijing_Institute_of_Technology",
    "华南理工大学": "South_China_University_of_Technology",
    "电子科技大学": "University_of_Electronic_Science_and_Technology_of_China",
    "重庆大学": "Chongqing_University",
    "湖南大学": "Hunan_University",
    "中南大学": "Central_South_University",
    "大连理工大学": "Dalian_University_of_Technology",
    "东北大学": "Northeastern_University_(China)",
    "吉林大学": "Jilin_University",
    "兰州大学": "Lanzhou_University",
    "中国农业大学": "China_Agricultural_University",
    "西北农林科技大学": "Northwest_A%26F_University",
    "中央民族大学": "Minzu_University_of_China",
    "国防科技大学": "National_University_of_Defense_Technology",
    "华东师范大学": "East_China_Normal_University",
    "北京师范大学": "Beijing_Normal_University",
    "中国人民大学": "Renmin_University_of_China",
    "中国海洋大学": "Ocean_University_of_China",
    "西北工业大学": "Northwestern_Polytechnical_University",
    "华中科技大学": "Huazhong_University_of_Science_and_Technology",
    "中央音乐学院": "Central_Conservatory_of_Music",
    "苏州大学": "Soochow_University_(Suzhou)",
    "北京交通大学": "Beijing_Jiaotong_University",
    "北京邮电大学": "Beijing_University_of_Posts_and_Telecommunications",
    "中国传媒大学": "Communication_University_of_China",
    "中央财经大学": "Central_University_of_Finance_and_Economics",
    "对外经济贸易大学": "University_of_International_Business_and_Economics_(Beijing)",
    "北京外国语大学": "Beijing_Foreign_Studies_University",
    "上海财经大学": "Shanghai_University_of_Finance_and_Economics",
    "西南大学": "Southwest_University",
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
    "上海体育学院": "Shanghai_University_of_Sport",
    "南京理工大学": "Nanjing_University_of_Science_and_Technology",
    "南京航空航天大学": "Nanjing_University_of_Aeronautics_and_Astronautics",
    "河海大学": "Hohai_University",
    "江南大学": "Jiangnan_University",
    "南京农业大学": "Nanjing_Agricultural_University",
    "中国药科大学": "China_Pharmaceutical_University",
    "南京师范大学": "Nanjing_Normal_University",
    "中国矿业大学": "China_University_of_Mining_and_Technology",
    "武汉理工大学": "Wuhan_University_of_Technology",
    "中国地质大学（武汉）": "China_University_of_Geosciences_(Wuhan)",
    "华中师范大学": "Central_China_Normal_University",
    "华中农业大学": "Huazhong_Agricultural_University",
    "中南财经政法大学": "Zhongnan_University_of_Economics_and_Law",
    "西安电子科技大学": "Xidian_University",
    "西北大学": "Northwest_University_(China)",
    "长安大学": "Chang'an_University",
    "陕西师范大学": "Shaanxi_Normal_University",
    "西南交通大学": "Southwest_Jiaotong_University",
    "西南财经大学": "Southwestern_University_of_Finance_and_Economics",
    "四川农业大学": "Sichuan_Agricultural_University",
    "暨南大学": "Jinan_University_(Guangzhou)",
    "华南师范大学": "South_China_Normal_University",
    "广州中医药大学": "Guangzhou_University_of_Chinese_Medicine",
    "华南农业大学": "South_China_Agricultural_University",
    "湖南师范大学": "Hunan_Normal_University",
    "湘潭大学": "Xiangtan_University",
    "长沙理工大学": "Changsha_University_of_Science_and_Technology",
    "东北农业大学": "Northeast_Agricultural_University",
    "东北林业大学": "Northeast_Forestry_University",
    "哈尔滨工程大学": "Harbin_Engineering_University",
    "辽宁大学": "Liaoning_University",
    "大连海事大学": "Dalian_Maritime_University",
    "沈阳工业大学": "Shenyang_University_of_Technology",
    "中国医科大学": "China_Medical_University_(PRC)",
    "中国石油大学（华东）": "China_University_of_Petroleum_(East_China)",
    "山东师范大学": "Shandong_Normal_University",
    "青岛大学": "Qingdao_University",
    "宁波大学": "Ningbo_University",
    "杭州电子科技大学": "Hangzhou_Dianzi_University",
    "浙江师范大学": "Zhejiang_Normal_University",
    "温州医科大学": "Wenzhou_Medical_University",
    "中国美术学院": "China_Academy_of_Art",
    "福州大学": "Fuzhou_University",
    "福建师范大学": "Fujian_Normal_University",
    "合肥工业大学": "Hefei_University_of_Technology",
    "安徽大学": "Anhui_University",
    "江西财经大学": "Jiangxi_University_of_Finance_and_Economics",
    "华东交通大学": "East_China_Jiaotong_University",
    "河南大学": "Henan_University",
    "河南农业大学": "Henan_Agricultural_University",
    "河北工业大学": "Hebei_University_of_Technology",
    "燕山大学": "Yanshan_University",
    "河北大学": "Hebei_University",
    "太原理工大学": "Taiyuan_University_of_Technology",
    "山西大学": "Shanxi_University",
    "内蒙古农业大学": "Inner_Mongolia_Agricultural_University",
    "新疆农业大学": "Xinjiang_Agricultural_University",
    "西藏大学": "Tibet_University",
    "青海大学": "Qinghai_University",
    "宁夏医科大学": "Ningxia_Medical_University",
    "海南师范大学": "Hainan_Normal_University",
    "广西医科大学": "Guangxi_Medical_University",
    "昆明理工大学": "Kunming_University_of_Science_and_Technology",
    "云南民族大学": "Yunnan_Minzu_University",
    "贵州师范大学": "Guizhou_Normal_University",
    "东北师范大学": "Northeast_Normal_University",
    "长春理工大学": "Changchun_University_of_Science_and_Technology",
    "吉林农业大学": "Jilin_Agricultural_University",
    "天津医科大学": "Tianjin_Medical_University",
    "中国民航大学": "Civil_Aviation_University_of_China",
    "北京电影学院": "Beijing_Film_Academy",
    "中国音乐学院": "China_Conservatory_of_Music",
    "上海戏剧学院": "Shanghai_Theatre_Academy",
    "上海海洋大学": "Shanghai_Ocean_University",
    "上海海事大学": "Shanghai_Maritime_University",
    "南京信息工程大学": "Nanjing_University_of_Information_Science_and_Technology",
    "南京邮电大学": "Nanjing_University_of_Posts_and_Telecommunications",
    "南京林业大学": "Nanjing_Forestry_University",
    "南京医科大学": "Nanjing_Medical_University",
    "武汉科技大学": "Wuhan_University_of_Science_and_Technology",
    "湖北大学": "Hubei_University",
    "中南民族大学": "South-Central_Minzu_University",
    "成都理工大学": "Chengdu_University_of_Technology",
    "西南石油大学": "Southwest_Petroleum_University",
    "四川师范大学": "Sichuan_Normal_University",
    "南方科技大学": "Southern_University_of_Science_and_Technology",
    "深圳大学": "Shenzhen_University",
    "广州大学": "Guangzhou_University",
    "汕头大学": "Shantou_University",
    "广东海洋大学": "Guangdong_Ocean_University",
    "浙江工业大学": "Zhejiang_University_of_Technology",
    "杭州师范大学": "Hangzhou_Normal_University",
    "浙江理工大学": "Zhejiang_Sci-Tech_University",
    "温州大学": "Wenzhou_University",
    "山东农业大学": "Shandong_Agricultural_University",
}

def get_wiki_name(name):
    """获取 Wikipedia 页面名"""
    return SPECIAL_WIKI_NAMES.get(name)

def wiki_api(action, params):
    base = "https://en.wikipedia.org/w/api.php"
    params["action"] = action
    params["format"] = "json"
    url = base + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "Victell/1.0 (educational project)"})
    with urllib.request.urlopen(req, context=ssl_ctx, timeout=15) as resp:
        return json.loads(resp.read())

def get_page_image_url(wiki_name):
    """获取 Wikipedia 页面主图 URL"""
    try:
        data = wiki_api("query", {
            "prop": "pageimages",
            "titles": wiki_name,
            "pithumbsize": "800",
            "pilimit": "1"
        })
        pages = data.get("query", {}).get("pages", {})
        for pid, page in pages.items():
            if pid == "-1":
                return None  # 页面不存在
            thumb = page.get("thumbnail")
            if thumb:
                return thumb["source"]
    except Exception as e:
        print(f"    API 错误: {e}")
    return None

def get_page_images(wiki_name, limit=10):
    """获取 Wikipedia 页面的所有图片"""
    try:
        data = wiki_api("query", {
            "prop": "images",
            "titles": wiki_name,
            "imlimit": str(limit)
        })
        pages = data.get("query", {}).get("pages", {})
        images = []
        for pid, page in pages.items():
            if pid == "-1":
                return []
            for img in page.get("images", []):
                title = img["title"]
                low = title.lower()
                # 排除 logo、svg、icon、seal、map、flag
                if any(w in low for w in ["logo", ".svg", "icon", "seal", "badge", "emblem",
                                           "coat", "shield", "map", "flag", "location",
                                           "signature", "crest", "arms"]):
                    continue
                images.append(title)
        return images
    except Exception:
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
    except Exception:
        pass
    return None

def download_image(url, filepath):
    """下载图片到本地"""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Victell/1.0"})
        with urllib.request.urlopen(req, context=ssl_ctx, timeout=30) as resp:
            data = resp.read()
            with open(filepath, "wb") as f:
                f.write(data)
        size = os.path.getsize(filepath)
        if size < 2000:
            os.remove(filepath)
            return False
        return True
    except Exception as e:
        print(f"      下载失败: {e}")
        return False

def main():
    data_path = os.path.join(os.path.dirname(__file__), "data", "universities.json")
    with open(data_path, "r", encoding="utf-8") as f:
        universities = json.load(f)

    total = len(universities)
    updated = 0
    skipped = 0
    failed = 0

    for u in universities:
        name = u["name"]
        uid = u["id"]
        campus_path = os.path.join(IMG_DIR, f"campus_{uid}.jpg")

        # 跳过已有有效图片的
        if os.path.exists(campus_path) and os.path.getsize(campus_path) > 2000:
            u["campus"] = f"/static/img/universities/campus_{uid}.jpg"
            skipped += 1
            continue

        wiki_name = get_wiki_name(name)
        if not wiki_name:
            print(f"[{uid}/{total}] {name} — 无 Wikipedia 映射，跳过")
            failed += 1
            continue

        print(f"[{uid}/{total}] {name} → {wiki_name}", flush=True)

        # 尝试获取主图
        img_url = get_page_image_url(wiki_name)
        if img_url:
            if download_image(img_url, campus_path):
                u["campus"] = f"/static/img/universities/campus_{uid}.jpg"
                print(f"  ✓ 主图下载成功 ({os.path.getsize(campus_path)} bytes)", flush=True)
                updated += 1
                time.sleep(1.0)
                continue

        # 主图失败，尝试其他图片
        print(f"  主图无/失败，尝试其他图片...", flush=True)
        images = get_page_images(wiki_name)
        if images:
            for img_title in images[:8]:
                img_url = get_image_url(img_title, 800)
                if img_url:
                    print(f"  尝试: {img_title[:60]}...", flush=True)
                    if download_image(img_url, campus_path):
                        u["campus"] = f"/static/img/universities/campus_{uid}.jpg"
                        print(f"  ✓ 备用图片下载成功 ({os.path.getsize(campus_path)} bytes)", flush=True)
                        updated += 1
                        break
                    time.sleep(1.0)
            else:
                print(f"  ✗ 所有备用图片均失败", flush=True)
                failed += 1
        else:
            print(f"  ✗ 页面无图片", flush=True)
            failed += 1

        time.sleep(5.0)  # 避免请求过快，加长延迟

    # 保存更新后的数据
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(universities, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*60}")
    print(f"完成！总计: {total}, 已有: {skipped}, 新下载: {updated}, 失败: {failed}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()