"""JSON 数据库模块 - 提供对 JSON 文件的 CRUD 操作"""
import json
import os
import threading
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

# 线程锁，避免并发写冲突
_locks = {}


def _get_lock(path: str) -> threading.Lock:
    if path not in _locks:
        _locks[path] = threading.Lock()
    return _locks[path]


def _ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def _full_path(name: str) -> str:
    if not name.endswith(".json"):
        name += ".json"
    return os.path.join(DATA_DIR, name)


def read_db(name: str, default=None):
    """读取 JSON 数据，文件不存在则返回 default"""
    _ensure_data_dir()
    path = _full_path(name)
    if not os.path.exists(path):
        return default if default is not None else []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return default if default is not None else []


def write_db(name: str, data):
    """写入 JSON 数据（带文件锁）"""
    _ensure_data_dir()
    path = _full_path(name)
    lock = _get_lock(path)
    with lock:
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, path)


def insert(name: str, record: dict) -> dict:
    """插入一条记录，自动生成 id 与 created_at"""
    data = read_db(name, [])
    record["id"] = record.get("id") or _next_id(data)
    record["created_at"] = record.get("created_at") or datetime.now().isoformat(timespec="seconds")
    data.append(record)
    write_db(name, data)
    return record


def find_one(name: str, predicate) -> dict:
    data = read_db(name, [])
    for item in data:
        if predicate(item):
            return item
    return None


def find_all(name: str, predicate=None) -> list:
    data = read_db(name, [])
    if predicate is None:
        return data
    return [item for item in data if predicate(item)]


def update_one(name: str, predicate, updates: dict) -> dict:
    data = read_db(name, [])
    for item in data:
        if predicate(item):
            item.update(updates)
            write_db(name, data)
            return item
    return None


def delete_one(name: str, predicate) -> bool:
    data = read_db(name, [])
    for i, item in enumerate(data):
        if predicate(item):
            data.pop(i)
            write_db(name, data)
            return True
    return False


def _next_id(data: list) -> int:
    if not data:
        return 1
    return max((item.get("id", 0) for item in data if isinstance(item, dict)), default=0) + 1
