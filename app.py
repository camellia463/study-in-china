"""翼启神州 · 来华留学指南 - Flask 主应用
技术栈: Python(Flask) + HTML + JS + CSS
数据库: JSON 文件
配色: 故宫朱红 / 鎏金 / 江南庭院
"""
import json
import re
from datetime import datetime

from flask import (
    Flask, render_template, request, redirect, url_for,
    jsonify, abort
)

import db

app = Flask(__name__)


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------
def slugify(text: str) -> str:
    """生成 URL slug"""
    text = (text or "").lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    text = text.strip("-")
    return text


def get_universities():
    return db.read_db("universities", [])


def get_university(uid):
    return db.find_one("universities", lambda u: u.get("id") == uid)


def all_fields():
    """汇总所有专业（去重排序）"""
    s = set()
    for u in get_universities():
        for p in u.get("programs", []):
            s.add(p)
    return sorted(s)


def field_en_map():
    """构建专业中英对照表"""
    m = {}
    for u in get_universities():
        progs = u.get("programs", [])
        progs_en = u.get("programs_en", [])
        for i, p in enumerate(progs):
            if i < len(progs_en) and progs_en[i]:
                m[p] = progs_en[i]
    return m


def all_provinces():
    """汇总所有省份（去重排序）"""
    return sorted({u.get("province", "") for u in get_universities() if u.get("province")})


# ---------------------------------------------------------------------------
# 模板上下文
# ---------------------------------------------------------------------------
@app.context_processor
def inject_globals():
    return {
        "year": datetime.now().year,
        "site_name": "翼启神州",
        "slugify": slugify,
        "province_en_map": {u.get("province", ""): u.get("province_en", "") for u in get_universities() if u.get("province")},
    }


# ---------------------------------------------------------------------------
# 主要页面路由
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html", universities=get_universities())


@app.route("/map/")
def map_view():
    unis = get_universities()
    return render_template(
        "map.html",
        universities=unis,
        universities_json=json.dumps(unis, ensure_ascii=False),
    )


@app.route("/universities/")
def universities():
    q = request.args.get("q", "").strip()
    tiers = request.args.getlist("tier")  # 支持多选：C9, 985, 211, 双一流, 普通, 学院
    items = get_universities()
    # 搜索
    if q:
        items = [u for u in items if q.lower() in u.get("name", "").lower()
                 or q.lower() in u.get("name_en", "").lower()
                 or q.lower() in u.get("province", "").lower()
                 or any(q.lower() in p.lower() for p in u.get("programs", []))]
    # 类型筛选
    if tiers:
        items = [u for u in items if u.get("tier") in tiers]
    return render_template(
        "universities.html",
        universities=items,
        all_tiers=["C9", "985", "211", "双一流", "普通", "学院"],
        tier_names={"C9": "C9联盟", "985": "985工程", "211": "211工程", "双一流": "双一流", "普通": "综合大学", "学院": "专业学院"},
        tier_names_en={"C9": "C9 League", "985": "Project 985", "211": "Project 211", "双一流": "Double First-Class", "普通": "Comprehensive", "学院": "Academy"},
        current_q=q,
        current_tiers=tiers,
    )


@app.route("/city/<province>/")
def city(province):
    # URL 解码
    from urllib.parse import unquote
    province = unquote(province)
    items = [u for u in get_universities() if u.get("province") == province]
    if not items:
        abort(404)
    return render_template("city.html", province=province, province_en=items[0].get("province_en", province) if items else province, universities=items)


@app.route("/university/<int:uid>/")
def university_detail(uid):
    u = get_university(uid)
    if not u:
        abort(404)
    related = [x for x in get_universities() if x.get("id") != uid][:3]
    return render_template("university_detail.html", u=u, related=related)


@app.route("/programs/")
def programs():
    return render_template(
        "programs.html",
        universities=get_universities(),
        fields=all_fields(),
        field_en_map=field_en_map(),
        provinces=all_provinces(),
    )


@app.route("/about/")
def about():
    return render_template("about.html")


@app.route("/why-china/")
def why_china():
    return render_template("why_china.html")


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


# ---------------------------------------------------------------------------
# 启动
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5050)
