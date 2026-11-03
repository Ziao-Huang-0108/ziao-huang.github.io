#!/usr/bin/env python3
"""Generate simple amber/paper diagrams for the portfolio PDF."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "pdf"
OUT.mkdir(parents=True, exist_ok=True)

PAPER = (238, 240, 243)
SURFACE = (251, 252, 253)
INK = (20, 21, 26)
MUTE = (92, 96, 107)
AMBER = (196, 92, 38)
LINE = (213, 216, 222)
OK = (21, 128, 61)
WARN = (180, 83, 9)
RED = (185, 28, 28)
ORANGE = (234, 88, 12)
YELLOW = (202, 138, 4)
GREEN = (22, 163, 74)
DEEP = (127, 29, 29)


def font(size: int):
    candidates = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size, index=0)
        except Exception:
            continue
    return ImageFont.load_default()


def rounded(draw, box, fill, radius=16, outline=None, width=2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def text_center(draw, xy, text, f, fill=INK):
    bbox = draw.textbbox((0, 0), text, font=f)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((xy[0] - w / 2, xy[1] - h / 2), text, font=f, fill=fill)


def save(img: Image.Image, name: str):
    path = OUT / name
    img.save(path, "PNG")
    print("wrote", path)


def compare_board():
    w, h = 1400, 900
    img = Image.new("RGB", (w, h), PAPER)
    d = ImageDraw.Draw(img)
    title = font(42)
    head = font(34)
    body = font(26)
    small = font(22)
    d.text((60, 40), "两个项目怎么不一样", font=title, fill=INK)

    cols = [
        (
            60,
            "今天吃什么",
            [
                ("形态", "免登录 · 能力层"),
                ("核心", "多人需求协调 / 推荐"),
                ("验证", "构造场景 · Debug · 打脸假设"),
                ("技术", "Next.js · LocalStorage"),
            ],
        ),
        (
            720,
            "Remember Me",
            [
                ("形态", "需登录 · App 雏形"),
                ("核心", "家庭私域 · 过期行动"),
                ("验证", "自用观察 · 一条真机反馈"),
                ("技术", "PWA · CloudBase · PG"),
            ],
        ),
    ]
    for x, name, rows in cols:
        rounded(d, (x, 120, x + 620, 820), SURFACE, outline=LINE)
        d.rectangle((x, 120, x + 620, 200), fill=AMBER)
        text_center(d, (x + 310, 160), name, head, white := (255, 255, 255))
        y = 240
        for k, v in rows:
            d.text((x + 36, y), k, font=small, fill=AMBER)
            d.text((x + 36, y + 36), v, font=body, fill=INK)
            y += 130
    save(img, "compare-board.png")


def priority_layers():
    w, h = 1200, 900
    img = Image.new("RGB", (w, h), PAPER)
    d = ImageDraw.Draw(img)
    title = font(40)
    body = font(28)
    d.text((50, 36), "推荐三层优先级（不全混在加减分里）", font=title, fill=INK)
    layers = [
        (AMBER, "硬约束", "忌口 / 过敏命中即淘汰；距离可放宽"),
        (WARN, "排除", "任一成员历史 1–2 星 → 不进排序池"),
        ((180, 120, 60), "软门控", "本次偏好：有命中走子集，无命中退回全候选"),
        (MUTE, "评分", "场景 / 星级 / 历史好评；同分随机"),
    ]
    y = 120
    for color, name, desc in layers:
        rounded(d, (50, y, 1150, y + 150), SURFACE, outline=color, width=4)
        d.rectangle((50, y, 70, y + 150), fill=color)
        d.text((100, y + 28), name, font=title, fill=color)
        d.text((100, y + 88), desc, font=body, fill=INK)
        y += 180
    save(img, "priority-layers.png")


def recommend_funnel():
    w, h = 1100, 980
    img = Image.new("RGB", (w, h), PAPER)
    d = ImageDraw.Draw(img)
    title = font(38)
    body = font(26)
    d.text((40, 30), "推荐链路一眼看懂", font=title, fill=INK)
    steps = [
        "选成员 + 场景 / 距离",
        "硬过滤（忌口 · 距离）",
        "排除历史差评",
        "偏好软门控",
        "子集 / 全候选排序",
        "可解释结果 → 打分回写",
    ]
    top, bottom = 110, 900
    for i, step in enumerate(steps):
        t = i / (len(steps) - 1)
        half = 480 - t * 220
        cy = top + i * ((bottom - top) / (len(steps) - 1))
        box = (w / 2 - half, cy - 48, w / 2 + half, cy + 48)
        rounded(d, box, SURFACE, outline=AMBER if i == len(steps) - 1 else LINE, width=3)
        text_center(d, (w / 2, cy), step, body, INK)
        if i < len(steps) - 1:
            d.polygon(
                [(w / 2 - 12, cy + 58), (w / 2 + 12, cy + 58), (w / 2, cy + 78)],
                fill=AMBER,
            )
    save(img, "recommend-funnel.png")


def expiry_ramp():
    w, h = 1300, 520
    img = Image.new("RGB", (w, h), PAPER)
    d = ImageDraw.Draw(img)
    title = font(40)
    body = font(24)
    d.text((50, 30), "过期颜色 = 行动信号", font=title, fill=INK)
    bands = [
        (DEEP, "已过期", "优先处理"),
        (RED, "≤30 天", "马上处理"),
        (ORANGE, "30–180", "近期留意"),
        (YELLOW, "180–365", "心里有数"),
        (GREEN, "≥365", "不用操心"),
    ]
    x = 50
    bw = 230
    for color, name, meaning in bands:
        rounded(d, (x, 140, x + bw - 16, 420), color, radius=20)
        text_center(d, (x + (bw - 16) / 2, 250), name, title, (255, 255, 255))
        text_center(d, (x + (bw - 16) / 2, 330), meaning, body, (255, 255, 255))
        x += bw
    d.text((50, 460), "同一档内越接近过期颜色越深 · 打开时用过期日减今天现算", font=body, fill=MUTE)
    save(img, "expiry-ramp.png")


def login_boundary():
    w, h = 1200, 800
    img = Image.new("RGB", (w, h), PAPER)
    d = ImageDraw.Draw(img)
    title = font(40)
    body = font(28)
    small = font(24)
    d.text((50, 36), "私域信息 → 必须有边界", font=title, fill=INK)
    rounded(d, (80, 140, 1120, 720), SURFACE, outline=LINE, width=3)
    # outer ring labels
    d.text((120, 180), "公开网页可读", font=small, fill=MUTE)
    rounded(d, (220, 240, 980, 640), (255, 248, 242), outline=AMBER, width=4)
    text_center(d, (600, 320), "登录后的家庭空间", title, AMBER)
    items = ["药品位置", "存货与过期", "谁买的 · 放哪"]
    y = 400
    for item in items:
        rounded(d, (360, y, 840, y + 56), SURFACE, outline=LINE)
        text_center(d, (600, y + 28), item, body, INK)
        y += 70
    d.text((220, 670), "账号由我开通 · 不开放网页自助注册（试用阶段取舍）", font=small, fill=MUTE)
    save(img, "login-boundary.png")


def method_loop():
    w, h = 1200, 780
    img = Image.new("RGB", (w, h), PAPER)
    d = ImageDraw.Draw(img)
    title = font(40)
    body = font(28)
    d.text((50, 30), "过程方法：开发日志 → Skill", font=title, fill=INK)
    nodes = [
        (200, 220, "做一步"),
        (600, 140, "记：做了什么 / 为什么"),
        (1000, 220, "问题与解法"),
        (800, 480, "有没有反馈"),
        (400, 480, "可复用 Skill"),
    ]
    for i, (x, y, label) in enumerate(nodes):
        rounded(d, (x - 140, y - 50, x + 140, y + 50), SURFACE, outline=AMBER, width=3)
        text_center(d, (x, y), label, body, INK)
    # simple arrows as lines
    pairs = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)]
    for a, b in pairs:
        x1, y1, _ = nodes[a]
        x2, y2, _ = nodes[b]
        d.line((x1, y1, x2, y2), fill=AMBER, width=4)
    d.text((50, 700), "把第一次翻聊天的痛苦，变成第二次项目的默认能力", font=body, fill=MUTE)
    save(img, "method-loop.png")


def takeaway_strip_bg():
    """Wide strip background optional — not required as separate asset."""
    pass


def main():
    compare_board()
    priority_layers()
    recommend_funnel()
    expiry_ramp()
    login_boundary()
    method_loop()


if __name__ == "__main__":
    main()
