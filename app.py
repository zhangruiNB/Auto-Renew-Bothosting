#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, re, sys, time, random, json, requests, subprocess, ctypes
import urllib.request, urllib.parse, urllib.error
from datetime import datetime
from seleniumbase import SB

# 环境变量配置 (可以直接在 GitHub Secrets 或私库双引号中填写)
EMAIL         = os.environ.get("EMAIL") or ""           # 邮箱,用于密码登录及通知 (推荐)
PASSWORD      = os.environ.get("PASSWORD") or ""        # 登录密码 (推荐方式, 在控制台右上角头像/设置里配置)
SESSION_TOKEN = os.environ.get("SESSION_TOKEN") or ""   # session token Cookie 登录 (备用方式)
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN") or ""   # Discord Token 备用登录 (仅在 SESSION_TOKEN 失效时使用)
GH_TOKEN      = os.environ.get("GH_TOKEN") or ""        # GitHub PAT (classic) token, 用于自动更新 session_token
TG_CHAT_ID    = os.environ.get("TG_CHAT_ID") or ""      # Telegram Chat ID (需与 Bot Token 一起配置)
TG_BOT_TOKEN  = os.environ.get("TG_BOT_TOKEN") or ""    # Telegram Bot Token

BASE_URL = "https://bot-hosting.net"

# 解析 DISCORD_TOKEN
DC_TOKEN = ""
if DISCORD_TOKEN:
    _parts = DISCORD_TOKEN.split(",", 1)
    DC_TOKEN = _parts[-1].strip()

# 校验必要凭据
if not (EMAIL and PASSWORD) and not SESSION_TOKEN and not DC_TOKEN:
    print("ℹ️ 未配置有效登录凭据 (EMAIL+PASSWORD 或 SESSION_TOKEN 或 DISCORD_TOKEN)，脚本终止。")
    sys.exit(1)

# 构造 Cookie (用于 SESSION_TOKEN 登录)
COOKIES = {
    "session_token": SESSION_TOKEN,
    "login": "true",
    "theme": "system",
}

# 记录本次登录方式（用于通知展示）
_LOGIN_METHOD = "PASSWORD" if (EMAIL and PASSWORD) else ("SESSION_TOKEN" if SESSION_TOKEN else "Discord Token")
_USER_DISPLAY_NAME = ""

# 获取展示用户名 (保留脱敏及备用回退)
def get_account_display_name() -> str:
    if EMAIL and '@' in EMAIL:
        name, domain = EMAIL.split('@', 1)
        return f"{name[:2]}****{name[-2:]}@{domain}" if len(name) > 4 else f"{name}@{domain}"
    elif EMAIL:
        return EMAIL[:2] + '****'
    if _USER_DISPLAY_NAME:
        return _USER_DISPLAY_NAME
    if DC_TOKEN:
        try:
            r = requests.get(
                "https://discord.com/api/v9/users/@me",
                headers={"Authorization": DC_TOKEN},
                timeout=4
            )
            if r.status_code == 200:
                data = r.json()
                u = data.get("global_name") or data.get("username")
                if u:
                    return f"{u} (Discord)"
        except Exception:
            pass
    return "Bot-Hosting 用户"

# 发送 Telegram 通知
def send_telegram_message(message: str):
    if not TG_BOT_TOKEN or not TG_CHAT_ID:
        print("⚠️ Telegram 未配置，跳过通知")
        return
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": TG_CHAT_ID, "text": message}, timeout=10)
        print("✅ Telegram 通知已发送")
    except Exception as e:
        print(f"❌ Telegram 发送失败: {e}")

# 通知格式化
def format_notification(status: str, extra: str = "", error: str = "", expiry_date: str = "") -> str:
    local_time = time.gmtime(time.time() + 8 * 3600)
    now = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
    masked_account = get_account_display_name()
    
    lines = [
        "🇫🇮 Bot-hosting 续期通知",
        "",
        f"{status}",
        f"👤 登录账户: {masked_account}",
    ]
    if _LOGIN_METHOD != "PASSWORD":
        lines.append(f"🔐 登录方式: {_LOGIN_METHOD}")
    if expiry_date:
        lines.append(f"📅 到期时间: {expiry_date}")
    if extra:
        lines.append(extra)
    if error:
        lines.append(f"⚠️ 错误信息: {error}")
    lines.append(f"⏱️ 登录时间: {now}")
    return "\n".join(lines)

# ---------- 基础工具与 JS 注入 ----------
def js(sb, script, default=None, errors=None):
    try:
        result = sb.execute_script(script)
        return default if result is None else result
    except Exception as e:
        if errors is not None:
            errors.append(f"execute_script: {type(e).__name__}: {e}")
        try:
            result = sb.cdp.evaluate("(function(){ " + script + " })()")
            return default if result is None else result
        except Exception as e2:
            if errors is not None:
                errors.append(f"cdp.evaluate: {type(e2).__name__}: {e2}")
            return default

# Turnstile 现场诊断快照
def diag_turnstile_dom(sb, errors=None):
    snap = js(sb, """
        var out = [];
        var ifr = document.querySelectorAll('iframe');
        out.push('top-doc iframes: ' + ifr.length);
        for (var i = 0; i < ifr.length; i++) {
            var r = ifr[i].getBoundingClientRect();
            out.push('iframe w=' + Math.round(r.width) + ' h=' + Math.round(r.height) + ' src=' + (ifr[i].src || '').slice(0, 90));
        }
        var ts = document.querySelectorAll('[class*="turnstile"], [id*="turnstile"], input[name="cf-turnstile-response"]');
        out.push('turnstile-ish elements: ' + ts.length);
        for (var j = 0; j < ts.length; j++) {
            var rr = ts[j].getBoundingClientRect();
            var cls = (typeof ts[j].className === 'string') ? ts[j].className : (ts[j].getAttribute('class') || '');
            out.push(' - ' + ts[j].tagNa
