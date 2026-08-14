#!/usr/bin/env python3
"""
从阿里 DataV 下载中国 GeoJSON (areas_v3/bound/100000_full.json)，
用 shapely 简化后投影到 1000x800 SVG 画布，
输出 34 个省级行政区的 SVG <path> 字符串列表。
"""
import json
import urllib.request
import urllib.error
from shapely.geometry import shape as shp_shape, MultiPolygon, Polygon
from shapely.ops import unary_union

URL = "https://geo.datav.aliyun.com/areas_v3/bound/100000_full.json"

# 投影函数：经度 73~135 → x: 0~1000，纬度 53~18 → y: 0~800
LNG_MIN, LNG_MAX = 73.0, 135.0
LAT_MIN, LAT_MAX = 18.0, 53.0

def project(lng, lat):
    x = (lng - LNG_MIN) / (LNG_MAX - LNG_MIN) * 1000.0
    y = (LAT_MAX - lat) / (LAT_MAX - LAT_MIN) * 800.0
    return x, y

def polygon_to_path(poly):
    """把 Polygon 转 SVG path d 字符串（含 holes）"""
    ext = list(poly.exterior.coords)
    d_parts = []
    pts = []
    for lng, lat in ext:
        x, y = project(lng, lat)
        pts.append(f"{x:.1f},{y:.1f}")
    d_parts.append("M " + " L ".join(pts) + " Z")
    for interior in poly.interiors:
        pts = []
        for lng, lat in interior.coords:
            x, y = project(lng, lat)
            pts.append(f"{x:.1f},{y:.1f}")
        d_parts.append("M " + " L ".join(pts) + " Z")
    return " ".join(d_parts)

def multipolygon_to_path(mp):
    parts = []
    if isinstance(mp, Polygon):
        polys = [mp]
    else:
        polys = list(mp.geoms)
    for p in polys:
        simp = p.simplify(0.02, preserve_topology=True)
        if simp.is_empty:
            continue
        if isinstance(simp, Polygon):
            parts.append(polygon_to_path(simp))
        else:
            for sp in simp.geoms:
                parts.append(polygon_to_path(sp))
    return " ".join(parts)

def main():
    print(f"Downloading {URL} ...")
    try:
        req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = resp.read().decode("utf-8")
    except Exception as e:
        print(f"ERROR download: {e}")
        return

    gj = json.loads(data)
    feats = gj.get("features", [])
    print(f"Features count: {len(feats)}")

    province_paths = []
    for f in feats:
        props = f.get("properties", {})
        name = props.get("name") or props.get("NAME") or "未知"
        if not name:
            continue
        geom = f.get("geometry")
        if not geom:
            continue
        try:
            g = shp_shape(geom)
        except Exception as e:
            print(f"  skip {name}: geom err {e}")
            continue
        if g.is_empty:
            continue
        simp = g.simplify(0.02, preserve_topology=True)
        if simp.is_empty:
            simp = g
        d = multipolygon_to_path(simp)
        province_paths.append({"name": name, "d": d})

    print(f"Total province paths: {len(province_paths)}")
    for p in province_paths:
        print(f"  - {p['name']}: {len(p['d'])} chars")

    with open("china_provinces.json", "w", encoding="utf-8") as f:
        json.dump(province_paths, f, ensure_ascii=False, indent=2)
    print("Saved china_provinces.json")

if __name__ == "__main__":
    main()
