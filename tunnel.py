#!/usr/bin/env python3
"""持久化 SSH 隧道到 serveo，自动重连"""
import subprocess
import time
import sys

def run_tunnel():
    while True:
        print(f"[{time.strftime('%H:%M:%S')}] 正在建立隧道...")
        proc = subprocess.Popen(
            ["ssh", "-o", "StrictHostKeyChecking=no",
             "-o", "ServerAliveInterval=30",
             "-o", "ServerAliveCountMax=3",
             "-o", "ConnectTimeout=15",
             "-R", "80:localhost:5050", "serveo.net"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, bufsize=1
        )
        
        url = None
        for line in proc.stdout:
            line = line.strip()
            if line:
                print(f"  {line}", flush=True)
            if "Forwarding HTTP traffic from" in line:
                url = line.split("https://")[1].strip()
                print(f"\n{'='*60}", flush=True)
                print(f"  公网地址: https://{url}", flush=True)
                print(f"  按 Ctrl+C 停止", flush=True)
                print(f"{'='*60}\n", flush=True)
        
        proc.wait()
        print(f"[{time.strftime('%H:%M:%S')}] 隧道断开，3 秒后重连...")
        time.sleep(3)

if __name__ == "__main__":
    run_tunnel()