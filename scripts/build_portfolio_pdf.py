#!/usr/bin/env python3
"""Build a landscape PPT-style portfolio PDF with full case content."""

from __future__ import annotations

import os
from pathlib import Path

from reportlab.lib.colors import Color, HexColor, white
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    KeepTogether,
    ListFlowable,
    ListItem,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Ziao-Huang-Portfolio.pdf"

# 16:9 landscape slide
PAGE_W, PAGE_H = 338 * mm, 190 * mm
MARGIN_X, MARGIN_Y = 14 * mm, 12 * mm

INK = HexColor("#14151a")
MUTE = HexColor("#5c606b")
AMBER = HexColor("#c45c26")
PAPER = HexColor("#eef0f3")
SURFACE = HexColor("#fbfcfd")
LINE = HexColor("#d5d8de")
OK = HexColor("#15803d")
WARN = HexColor("#b45309")

pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
FONT = "STSong-Light"


def styles():
    ss = getSampleStyleSheet()
    ss.add(ParagraphStyle(name="Eyebrow", fontName=FONT, fontSize=10, textColor=AMBER, leading=14, spaceAfter=6))
    ss.add(ParagraphStyle(name="H1", fontName=FONT, fontSize=28, textColor=INK, leading=34, spaceAfter=8))
    ss.add(ParagraphStyle(name="H2", fontName=FONT, fontSize=22, textColor=INK, leading=28, spaceAfter=8))
    ss.add(ParagraphStyle(name="H3", fontName=FONT, fontSize=14, textColor=INK, leading=18, spaceBefore=6, spaceAfter=4))
    ss.add(ParagraphStyle(name="Body", fontName=FONT, fontSize=11, textColor=INK, leading=16, spaceAfter=6))
    ss.add(ParagraphStyle(name="Lead", fontName=FONT, fontSize=13, textColor=INK, leading=19, spaceAfter=8))
    ss.add(ParagraphStyle(name="Small", fontName=FONT, fontSize=9, textColor=MUTE, leading=12))
    ss.add(ParagraphStyle(name="Label", fontName=FONT, fontSize=9, textColor=AMBER, leading=12, spaceAfter=2))
    ss.add(ParagraphStyle(name="CenterH1", fontName=FONT, fontSize=34, textColor=INK, leading=40, alignment=TA_CENTER, spaceAfter=10))
    ss.add(ParagraphStyle(name="CenterLead", fontName=FONT, fontSize=13, textColor=INK, leading=19, alignment=TA_CENTER, spaceAfter=8))
    ss.add(ParagraphStyle(name="Cell", fontName=FONT, fontSize=9, textColor=INK, leading=12))
    ss.add(ParagraphStyle(name="CellHead", fontName=FONT, fontSize=9, textColor=INK, leading=12))
    ss.add(ParagraphStyle(name="BulletBody", fontName=FONT, fontSize=11, textColor=INK, leading=15))
    return ss


S = styles()
PAGE_NO = {"n": 0}


def draw_page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(PAPER)
    canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    PAGE_NO["n"] += 1
    canvas.setFillColor(MUTE)
    canvas.setFont(FONT, 8)
    canvas.drawRightString(PAGE_W - MARGIN_X, 7 * mm, f"{PAGE_NO['n']:02d}")
    canvas.restoreState()


def P(text, style="Body"):
    return Paragraph(str(text).replace("\n", "<br/>"), S[style])


def eyebrow(text):
    return P(text, "Eyebrow")


def callout(label, text):
    data = [[P(f"<font color='#c45c26'>{label}</font>", "Label")], [P(text, "Body")]]
    t = Table(data, colWidths=[PAGE_W - 2 * MARGIN_X])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), SURFACE),
                ("BOX", (0, 0), (-1, -1), 0.5, LINE),
                ("LINEBEFORE", (0, 0), (0, -1), 3, AMBER),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return t


def panel(title, body):
    data = [[P(f"<font color='#c45c26'><b>{title}</b></font>", "Body")], [P(body, "Small")]]
    t = Table(data, colWidths=[(PAGE_W - 2 * MARGIN_X - 12) / 2])
    # width overwritten by caller often
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), SURFACE),
                ("BOX", (0, 0), (-1, -1), 0.5, LINE),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    return t


def panels(items, cols=2):
    usable = PAGE_W - 2 * MARGIN_X
    gap = 8
    cw = (usable - gap * (cols - 1)) / cols
    row = []
    rows = []
    for i, (title, body) in enumerate(items):
        cell = [[P(f"<font color='#c45c26'><b>{title}</b></font>", "Body")], [P(body, "Small")]]
        t = Table(cell, colWidths=[cw])
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), SURFACE),
                    ("BOX", (0, 0), (-1, -1), 0.5, LINE),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        row.append(t)
        if len(row) == cols:
            rows.append(row)
            row = []
    if row:
        while len(row) < cols:
            row.append(Spacer(cw, 1))
        rows.append(row)
    out = []
    for r in rows:
        tbl = Table([r], colWidths=[cw] * cols)
        tbl.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
        out.append(tbl)
        out.append(Spacer(1, 6))
    return out


def issue(num, title, body, kind="normal"):
    color = AMBER if kind == "normal" else (WARN if kind == "warn" else OK)
    hex_map = {AMBER: "#c45c26", WARN: "#b45309", OK: "#15803d"}
    head = P(f"<font color='{hex_map[color]}'><b>{num}</b></font>  <b>{title}</b>", "Body")
    data = [[head], [P(body, "Small")]]
    t = Table(data, colWidths=[PAGE_W - 2 * MARGIN_X])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), SURFACE),
                ("BOX", (0, 0), (-1, -1), 0.5, LINE),
                ("LINEBEFORE", (0, 0), (0, -1), 3, color),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return t


def table(headers, rows):
    usable = PAGE_W - 2 * MARGIN_X
    data = [[P(h, "CellHead") for h in headers]]
    for r in rows:
        data.append([P(c, "Cell") for c in r])
    cols = len(headers)
    # heuristic widths
    if cols == 3:
        widths = [usable * 0.28, usable * 0.28, usable * 0.44]
    elif cols == 2:
        widths = [usable * 0.35, usable * 0.65]
    else:
        widths = [usable / cols] * cols
    t = Table(data, colWidths=widths, repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), SURFACE),
        ("GRID", (0, 0), (-1, -1), 0.5, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    t.setStyle(TableStyle(style))
    return t


def fit_image(path, max_w, max_h):
    img = Image(str(ROOT / path))
    scale = min(max_w / img.imageWidth, max_h / img.imageHeight)
    img.drawWidth = img.imageWidth * scale
    img.drawHeight = img.imageHeight * scale
    return img


def phones(paths_captions, height=105 * mm):
    usable = PAGE_W - 2 * MARGIN_X
    n = len(paths_captions)
    gap = 8
    cw = (usable - gap * (n - 1)) / n
    cells = []
    for path, cap in paths_captions:
        img = fit_image(path, cw, height)
        cell = Table([[img], [P(cap, "Small")]], colWidths=[cw])
        cell.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("TOPPADDING", (0, 0), (-1, -1), 2),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ]
            )
        )
        cells.append(cell)
    t = Table([cells], colWidths=[cw] * n)
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "BOTTOM"), ("ALIGN", (0, 0), (-1, -1), "CENTER")]))
    return t


def wide_image(path, caption, max_h=100 * mm):
    usable = PAGE_W - 2 * MARGIN_X
    img = fit_image(path, usable, max_h)
    t = Table([[img], [P(caption, "Small")]], colWidths=[usable])
    t.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER")]))
    return t


def slide(story, *flowables):
    story.extend(flowables)
    story.append(PageBreak())


def build():
    frame = Frame(MARGIN_X, MARGIN_Y, PAGE_W - 2 * MARGIN_X, PAGE_H - 2 * MARGIN_Y, id="slide")
    doc = BaseDocTemplate(
        str(OUT),
        pagesize=(PAGE_W, PAGE_H),
        leftMargin=MARGIN_X,
        rightMargin=MARGIN_X,
        topMargin=MARGIN_Y,
        bottomMargin=MARGIN_Y,
    )
    doc.addPageTemplates([PageTemplate(id="slide", frames=[frame], onPage=draw_page)])

    story = []

    # 01 cover
    cover_left = [
        eyebrow("PORTFOLIO · PRODUCT / RESEARCH / OPS"),
        P("黄子骜 · Ziao Huang", "H1"),
        P(
            "宁波诺丁汉大学 · 大四 · 数学与应用数学。实习偏向用户研究、策略运营、数据分析、商业分析、产品运营等岗位。"
            "下面两个作品都来自真实生活里遇到的问题：多人吃饭难决定、家里东西找不到或过期。"
            "我把它们做成可在线打开的产品，并写下从需求到方案、测试与落地的完整复盘。",
            "Lead",
        ),
        Spacer(1, 6),
        P("邮箱：zaozhi030108@outlook.com", "Body"),
        P("作品集：https://ziao-huang-0108.github.io/ziao-huang.github.io/", "Small"),
        P("托管于 GitHub Pages", "Small"),
    ]
    # phones side by side via nested table
    img_a = fit_image("assets/hero/eatwhat.jpg", 70 * mm, 120 * mm)
    img_b = fit_image("assets/hero/remember-me.jpg", 70 * mm, 120 * mm)
    right = Table([[img_a, img_b]], colWidths=[75 * mm, 75 * mm])
    right.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    left_tbl = Table([[x] for x in cover_left], colWidths=[150 * mm])
    top = Table([[left_tbl, right]], colWidths=[155 * mm, 155 * mm])
    top.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    slide(story, top)

    # 02 projects
    slide(
        story,
        eyebrow("HOME · PROJECTS"),
        P("两个项目", "H2"),
        *panels(
            [
                (
                    "今天吃什么 · 免登录 · 点开即用",
                    "多人用餐决策助手。更接近美团 / 大众点评可增加的一层「决策能力」——平台已有餐厅库，缺的是多人需求协调。"
                    "推荐机制更重，因此做了更多结构化测试。<br/>Demo：https://eatwhat-d8g01gpqk878dd6ed-1324990131.tcloudbaseapp.com",
                ),
                (
                    "Remember Me · 需登录 · 独立 App 雏形",
                    "全家共用的物品小本子：放哪、何时过期、还剩什么。管理家庭私域信息，需要登录。"
                    "迭代主要来自自用观察，并沉淀了开发日志工作流。<br/>体验账号 test1 / Abcd1234<br/>"
                    "Demo：https://remember-me-remember-me-d1gmd5iiu9d88c58a.webapps.tcloudbase.com",
                ),
            ]
        ),
    )

    # 03 about
    slide(
        story,
        eyebrow("HOME · ABOUT"),
        P("关于我", "H2"),
        Spacer(1, 10),
        P(
            "大四在读，数学与应用数学背景；做过用户调研、活动组织与 AI 产品原型。"
            "希望在偏研究、策略与分析的岗位里，把定量思维和可验证的落地结合起来。",
            "Lead",
        ),
        Spacer(1, 8),
        P("邮箱：zaozhi030108@outlook.com", "Body"),
        P("也写歌 · 网易云歌手页 https://163cn.tv/bjSkQBzl", "Body"),
        Spacer(1, 20),
        P("© 黄子骜 · Ziao Huang · 托管于 GitHub Pages", "Small"),
    )

    # 04 divider eatwhat
    slide(
        story,
        Spacer(1, 35 * mm),
        P("CASE 01", "Eyebrow"),
        P("今天吃什么", "CenterH1"),
        P(
            "从多人用餐决策痛点出发，探索推荐系统的产品设计与迭代——"
            "不是选出「最好吃」的店，而是协调多方需求，快速给出一个大家都能接受的答案。",
            "CenterLead",
        ),
        Spacer(1, 8),
        P("免登录 · 点开即用　｜　产品设计 / 推荐逻辑　｜　2026.9　｜　Next.js · LocalStorage", "CenterLead"),
    )

    # 05 toc
    toc_items = [
        ("01 项目背景", "Problem"),
        ("02 产品目标与定位", "Goal"),
        ("03 产品方案", "Solution"),
        ("04 MVP 与体验路径", "Prototype"),
        ("05 测试与打脸", "Testing"),
        ("06 未来方向", "Future"),
        ("07 项目收获", "Reflection"),
        ("08 线上 Demo", "Try it"),
    ]
    toc_rows = []
    for i in range(0, 8, 2):
        toc_rows.append(
            [
                P(f"<b>{toc_items[i][0]}</b>　<font color='#5c606b'>{toc_items[i][1]}</font>", "Body"),
                P(f"<b>{toc_items[i+1][0]}</b>　<font color='#5c606b'>{toc_items[i+1][1]}</font>", "Body"),
            ]
        )
    toc_tbl = Table(toc_rows, colWidths=[(PAGE_W - 2 * MARGIN_X) / 2] * 2)
    toc_tbl.setStyle(TableStyle([("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8), ("LINEBELOW", (0, 0), (-1, -1), 0.5, LINE)]))
    slide(story, eyebrow("今天吃什么 · 目录"), P("目录", "H2"), Spacer(1, 8), toc_tbl)

    # 06 problem
    slide(
        story,
        eyebrow("01 · PROBLEM"),
        P("项目背景：多人吃饭，为什么这么难？", "H2"),
        P(
            "面对「吃什么」，很多人会说「随便」，把决定权交给别人，或只给出「不太能吃辣」之类的模糊范围。"
            "多人一起时，需求还可能冲突；选得不好，做决定的人容易承担额外压力。",
            "Body",
        ),
        P(
            "美团、大众点评、小红书更擅长帮用户<strong>拿到餐厅列表</strong>。"
            "用户仍要从大量候选里自行了解并做最终决定，也很难同时结合多人不同需求。"
            "对选择困难的人来说，即使一个人吃饭也可能卡住。",
            "Body",
        ),
        callout(
            "CORE QUESTION",
            "问题不是「找不到餐厅」，而是面对大量选择时，很难快速找到一个大家都能接受的答案。"
            "当选择很多、需求又有差异时，如何帮助用户完成一次「可接受」的用餐决策？",
        ),
    )

    # 07 goal
    slide(
        story,
        eyebrow("02 · GOAL"),
        P("产品目标与定位", "H2"),
        P("把「找餐厅」升级为「帮用户做决定」，验证四个方向：", "Body"),
        *panels(
            [
                ("个性化 · 成员档案", "多成员偏好、忌口与历史反馈可组合进一次推荐。"),
                ("需求理解", "把偏好与忌口变成可用于推荐的结构化条件。"),
                ("推荐可解释", "展示推荐依据与评分构成，让用户知道「为什么是这家」。"),
                ("反馈闭环", "用餐后评分回写到具体成员，影响后续推荐。"),
            ],
            cols=4,
        ),
        callout(
            "POSITIONING",
            "核心目标不是预测「用户最喜欢哪一家」，而是在多人、多种需求下做优先级排序与协调，快速给出可接受结果。"
            "相对美团 / 点评：它们已有真实餐厅数据库；本项目更接近平台可增加的一层<strong>决策 / 推荐能力</strong>，而不是从零搭一套餐饮 App。"
            "产品做成<strong>免登录、点开即用</strong>，降低试用成本，也符合「能力层」该有的轻入口。",
        ),
    )

    # 08 flow
    flow_steps = [
        "选成员 + 场景 / 距离 — 合并偏好、忌口与历史评分",
        "硬过滤 — 忌口命中即淘汰；距离无结果则放宽",
        "排除历史差评 — 任一成员 1–2 星 → 不进排序池",
        "偏好软门控 — 尽量满足本次想吃什么，但不一票否决",
        "有命中：子集排序　／　无命中：退回全候选再排序",
        "可解释结果 → 打分反馈 — 评分写入对应成员记忆",
    ]
    flow_flowables = [eyebrow("03 · SOLUTION · FLOW"), P("产品方案：逻辑一览", "H2"), P("从勾选成员到推荐，再到打分回写。", "Small"), Spacer(1, 4)]
    for i, step in enumerate(flow_steps):
        box = Table([[P(step, "Body")]], colWidths=[PAGE_W - 2 * MARGIN_X - 40 * mm])
        box.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), SURFACE),
                    ("BOX", (0, 0), (-1, -1), 0.5, LINE),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        flow_flowables.append(box)
        if i < len(flow_steps) - 1:
            flow_flowables.append(P("<font color='#c45c26'><b>↓</b></font>", "Body"))
    slide(story, *flow_flowables)

    # 09 design + table
    slide(
        story,
        eyebrow("03 · SOLUTION · DESIGN"),
        P("可组合档案 · 硬约束 vs 软偏好 · 三层优先级", "H2"),
        P("3.1 可组合的成员档案", "H3"),
        P(
            "吃饭天然多人，因此没有做成单一用户画像，而是可组合的成员档案："
            "同一个人跟不同的人吃饭，参与决策的需求组合也不同。每次勾选实际成员，合并偏好、忌口与历史评分后再进入推荐。",
            "Body",
        ),
        P("3.2 硬约束 vs 软偏好", "H3"),
        P(
            "<strong>硬约束</strong>（如过敏、最大距离）不能违反；"
            "<strong>软偏好</strong>（如「想吃火锅」）尽量满足，但不意味着其他类型绝对不能推。",
            "Body",
        ),
        P("3.3 三层优先级（不全混在一个加减分里）", "H3"),
        table(
            ["因素", "层级", "行为"],
            [
                ["忌口 / 过敏", "硬约束", "命中即淘汰"],
                ["最大距离", "硬约束（可放宽）", "先按范围过滤；空则放宽"],
                ["历史 1–2 星", "排除", "任一成员差评 → 不进排序池"],
                ["饮食偏好", "软门控", "有命中 → 子集排序；无命中 → 退回全候选"],
                ["场景 / 星级 / 历史好评", "评分", "在候选池内打分；同分随机"],
                ["用餐人数", "仅展示", "不参与硬淘汰（测试后调整）"],
            ],
        ),
        Spacer(1, 4),
        P("推荐机制比「记一张清单」更重：召回与排序必须对齐目标，否则链路会整体失效——这也是后面要做更多测试的原因。", "Small"),
    )

    # 10 mvp phones 1
    slide(
        story,
        eyebrow("04 · MVP"),
        P("MVP：三步向导，免登录即用", "H2"),
        P("选择用餐成员 → 设置场景与人数 → 设置最大距离 → 生成推荐；结果页可再抽一次、打分，并可展开看计算过程。", "Body"),
        phones(
            [
                ("assets/eatwhat/01-members-phone.jpg", "选择用餐人档案（偏好与忌口）"),
                ("assets/eatwhat/02-scene-phone.jpg", "设置用餐场景与人数"),
                ("assets/eatwhat/03-distance-phone.jpg", "设置最大距离"),
            ],
            height=100 * mm,
        ),
    )

    # 11 results
    slide(
        story,
        eyebrow("04 · MVP · RESULTS"),
        P("推荐结果 · 可解释明细 · 操作", "H2"),
        phones(
            [
                ("assets/eatwhat/04-result-phone.jpg", "推荐结果与理由"),
                ("assets/eatwhat/05-detail-phone.jpg", "可解释的评分明细"),
                ("assets/eatwhat/06-actions.png", "打分、再抽一次、立即出发"),
            ],
            height=100 * mm,
        ),
    )

    # 12 debug
    slide(
        story,
        eyebrow("04 · MVP · DEBUG"),
        P("Debug / 测试记录面板", "H2"),
        P("还原「为什么推这家」（电脑端截图，便于完整展示面板）。", "Body"),
        wide_image("assets/eatwhat/06-debug.png", "Usage Log / Debug：让异常结果可复盘", max_h=105 * mm),
    )

    # 13 testing 1-3
    slide(
        story,
        eyebrow("05 · TESTING"),
        P("测试与打脸：假设要被结果纠正", "H2"),
        P("推荐链路一复杂，就不能只靠直觉认功能「合理」。我用构造场景做了多轮测试，并补上 Usage Log / Debug，让异常结果可复盘。", "Body"),
        issue("01", "用餐人数不应成为硬限制", "「一人食 + 想吃火锅」时，火锅店因适用人数不含 1 人被直接滤掉。调整：人数改为参考信息，不再硬淘汰。"),
        Spacer(1, 4),
        issue("02", "看起来周全的输入可能完全没用", "「交通方式」改了，推荐却不变——字段没进逻辑。调整：删掉该输入。只有能改变决策结果的变量，才值得增加输入成本。"),
        Spacer(1, 4),
        issue("03", "记忆数据到底属于谁", "成员 A 的五星评分影响了只选成员 B 的推荐。根因是历史记忆按浏览器全局存，没绑到档案。调整：评分严格归属成员。这是产品数据建模问题，不只是存储 Bug。"),
    )

    # 14 testing 4-5
    slide(
        story,
        eyebrow("05 · TESTING · CONT."),
        P("测试与打脸（续）", "H2"),
        issue(
            "04",
            "当下需求应优先于历史偏好",
            "同时有人历史爱泰国菜、有人当前想火锅时，系统先推了泰国菜。调整：降低历史权重，把本次偏好前置到召回。过去喜欢什么，不能盖住这次想吃什么。",
            "warn",
        ),
        Spacer(1, 4),
        issue(
            "05",
            "召回对了，排序目标仍可能错位",
            "第二轮构造多人冲突场景：火锅进了候选池，但最终排序仍被其他类型压过——偏好只缩了候选，池内打分未体现群体偏好满足度。"
            "启示：推荐要同时做好「哪些店能进来」和「进来后优先推谁」，两者目标不一致，整条链路会失效。",
            "ok",
        ),
        Spacer(1, 6),
        callout(
            "WHY MORE TESTING HERE",
            "相对 Remember Me，本项目的逻辑中心是推荐机制，错误更隐蔽，所以测试密度更高：人工场景 → 可观测日志 → 冲突场景复盘。"
            "做下来最深的体会是：要用结果打脸假设，而不是把「功能做完」当成验证完成。",
        ),
    )

    # 15 future
    slide(
        story,
        eyebrow("06 · FUTURE"),
        P("未来优化方向", "H2"),
        *panels(
            [
                (
                    "真实位置",
                    "<b>当前</b>用预设 / 模拟距离做硬过滤。<br/>"
                    "<b>局限</b>多人时真正问题是「对大家都方不方便」。<br/>"
                    "<b>未来</b>接入地图 / 定位，优先推对全体出行更友好的中间地带餐厅。",
                ),
                (
                    "菜品级匹配",
                    "<b>当前</b>推荐停在餐厅标签。<br/>"
                    "<b>局限</b>店适合 ≠ 每道菜适合。<br/>"
                    "<b>未来</b>接入菜单，形成「餐厅 → 菜品 → 成员」匹配。",
                ),
                (
                    "群体满意度",
                    "<b>当前</b>偏好更多影响「谁能进池」。<br/>"
                    "<b>局限</b>最终仍可能更偏向其中一人。<br/>"
                    "<b>未来</b>把群体满足度写进排序，并支持分成员反馈。",
                ),
            ],
            cols=3,
        ),
    )

    # 16 reflection
    slide(
        story,
        eyebrow("07 · REFLECTION"),
        P("项目收获", "H2"),
        *panels(
            [
                ("01", "现实里合理的因素（人数、交通），放进产品不一定该做约束；要用测试验证。"),
                ("02", "推荐不只是算分：数据归属、需求优先级、可解释性、召回与排序对齐，都是产品设计。"),
                ("03", "功能跑通 ≠ 产品闭环；核心操作在真实页面上必须可点（结果页滚动曾挡住按钮）。"),
                ("04", "整理本项目复盘时大量翻聊天记录，成本很高——这也直接推动了下一个项目从第一天就写开发日志。"),
            ]
        ),
        callout("CLOSE", "一个功能看起来合理，并不代表它真的有用。只有通过使用、观察结果、再改产品，才能知道最初的想法是否成立。"),
    )

    # 17 demo
    slide(
        story,
        eyebrow("08 · DEMO"),
        P("线上体验 · 今天吃什么", "H2"),
        Spacer(1, 16),
        P("已部署到 CloudBase 静态托管。免登录，点开即可走完推荐流程。", "Lead"),
        Spacer(1, 10),
        P("https://eatwhat-d8g01gpqk878dd6ed-1324990131.tcloudbaseapp.com", "Body"),
    )

    # ===== Remember Me =====
    slide(
        story,
        Spacer(1, 35 * mm),
        P("CASE 02", "Eyebrow"),
        P("Remember Me", "CenterH1"),
        P(
            "全家一起用的物品小本子：什么时候买了什么、放在哪、还有多久过期，一眼能看到。"
            "管的是家里的私密信息，因此需要登录；形态上更接近一个独立 App 的雏形，而不是某个已有平台上的插件功能。",
            "CenterLead",
        ),
        Spacer(1, 8),
        P("需登录 · 独立 App 雏形　｜　产品设计 / 落地与迭代　｜　2026.10　｜　PWA · CloudBase · PostgreSQL", "CenterLead"),
    )

    rm_toc = [
        ("01 项目背景", "Problem"),
        ("02 产品目标与定位", "Goal"),
        ("03 产品方案", "Solution"),
        ("04 迭代与洞察", "Iteration"),
        ("05 过程方法", "Method"),
        ("06 未来方向", "Future"),
        ("07 项目收获", "Reflection"),
        ("08 线上 Demo", "Try it"),
    ]
    rm_rows = []
    for i in range(0, 8, 2):
        rm_rows.append(
            [
                P(f"<b>{rm_toc[i][0]}</b>　<font color='#5c606b'>{rm_toc[i][1]}</font>", "Body"),
                P(f"<b>{rm_toc[i+1][0]}</b>　<font color='#5c606b'>{rm_toc[i+1][1]}</font>", "Body"),
            ]
        )
    rm_tbl = Table(rm_rows, colWidths=[(PAGE_W - 2 * MARGIN_X) / 2] * 2)
    rm_tbl.setStyle(TableStyle([("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8), ("LINEBELOW", (0, 0), (-1, -1), 0.5, LINE)]))
    slide(story, eyebrow("REMEMBER ME · 目录"), P("目录", "H2"), Spacer(1, 8), rm_tbl)

    slide(
        story,
        eyebrow("01 · PROBLEM"),
        P("项目背景：家里的东西，为什么总对不上？", "H2"),
        P("家里东西越买越多，常见几种遇到的情况：", "Body"),
        P("· <b>忘了放在哪</b>：钥匙、首饰、衣物等，要用时翻遍柜子。", "Body"),
        P("· <b>过期了才发现</b>：药品、调料、护肤品、零食等放着放着只能扔掉。", "Body"),
        P("· <b>重复购买</b>：不知道还有存货，又买了一份。", "Body"),
        P("· <b>信息不共享</b>：某一个人购买、存放的，其他家人不知道。", "Body"),
        Spacer(1, 6),
        callout(
            "CORE QUESTION",
            "如何让一家人用同一份「物品小本子」，在需要时快速知道东西在哪、急不急处理，"
            "同时又把家庭私密信息关在可控制的访问范围里？",
        ),
    )

    slide(
        story,
        eyebrow("02 · GOAL"),
        P("产品目标与定位", "H2"),
        P("目标用户按角色拆开，避免做成「只有采购者爱用」的记事本：", "Body"),
        table(
            ["角色", "特点", "主要需求"],
            [
                ["采购者", "会主动录入", "录入要快，操作简单"],
                ["使用者", "很少录入，偶尔查找", "能快速搜到东西在哪"],
            ],
        ),
        Spacer(1, 8),
        callout(
            "POSITIONING",
            "相对「今天吃什么」：那个项目更像美团 / 大众点评等已有的平台可增加的决策能力层，而作为网页可以免登录点开即用。"
            "Remember Me 要管的是家里私人物品与过期信息，需要家庭成员身份与家庭边界，因此更像<strong>独立 App 的雏形</strong>："
            "登录、家庭空间、云端同步、过期行动提示，都是产品本身，而不是外挂功能。",
        ),
    )

    rm_flow = [
        "打开链接 → 登录 — 用户名 + 密码；账号由我开通",
        "只有一家：直接进清单　／　有多家：先选家 / 建家 / 邀请码加入",
        "清单按过期紧急度着色排序 — 打开时用过期日减今天现算，最急的在前",
        "记一件　／　搜索 / 过期·类别筛选　／　切换家 / 新建家",
    ]
    rm_flow_fs = [eyebrow("03 · SOLUTION · FLOW"), P("产品方案：逻辑一览", "H2"), P("先进门（登录）→ 再记什么 → 过期颜色怎么读 → 怎么找、怎么切换家。", "Small"), Spacer(1, 4)]
    for i, step in enumerate(rm_flow):
        box = Table([[P(step, "Body")]], colWidths=[PAGE_W - 2 * MARGIN_X - 40 * mm])
        box.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), SURFACE),
                    ("BOX", (0, 0), (-1, -1), 0.5, LINE),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        rm_flow_fs.append(box)
        if i < len(rm_flow) - 1:
            rm_flow_fs.append(P("<font color='#c45c26'><b>↓</b></font>", "Body"))
    slide(story, *rm_flow_fs)

    # access + phones
    left = [
        P("3.1 访问与形态：为什么要登录", "H3"),
        P(
            "「今天吃什么」可以免登录，因为试用成本低、数据敏感度相对较低。"
            "Remember Me 记录的是药品位置、家用存货等<strong>家庭私域信息</strong>，不能做成谁打开都能看的公开页，所以必须登录。",
            "Body",
        ),
        *panels(
            [
                ("当前访问策略", "为了安全性和稳定性，不开放网页自助注册。账号只在我这边开通。这是家庭小范围试用阶段的取舍，并非漏做注册。"),
                ("形态选择", "手机网页（PWA）+ CloudBase：不用上架审核，一个链接就能分享；可添加到主屏幕。后端用腾讯云 PostgreSQL，国内访问更稳。"),
            ]
        ),
        P("体验账号（非正式家人账号）：test1 / Abcd1234", "Body"),
    ]
    # Use full width phones below text instead of complex split for reliability
    slide(
        story,
        eyebrow("03 · SOLUTION · ACCESS"),
        P("访问与形态：为什么要登录", "H2"),
        P(
            "「今天吃什么」可以免登录，因为试用成本低、数据敏感度相对较低。"
            "Remember Me 记录的是药品位置、家用存货等<strong>家庭私域信息</strong>，不能做成谁打开都能看的公开页，所以必须登录。",
            "Body",
        ),
        *panels(
            [
                ("当前访问策略", "为了安全性和稳定性，不开放网页自助注册。账号只在我这边开通：只有我配置过的账户+密码可以进入。这是家庭小范围试用阶段的取舍，并非漏做注册。"),
                ("形态选择", "手机网页（PWA）+ CloudBase：不用上架审核，一个链接就能分享；可添加到主屏幕。后端用腾讯云 PostgreSQL，国内访问更稳。"),
            ]
        ),
        P("体验账号：test1 / Abcd1234", "Body"),
        phones(
            [
                ("assets/remember-me/03-login.png", "登录页：用户名 + 密码"),
                ("assets/remember-me/04-pick-home.png", "选家页：多家时先进哪一家"),
            ],
            height=78 * mm,
        ),
    )

    slide(
        story,
        eyebrow("03 · SOLUTION · FIELDS & COLOR"),
        P("3.2 记什么 · 3.3 过期颜色", "H2"),
        P(
            "每件物品记录名称、价格、功能/用途、购买日期、过期日期、放置位置、备注、照片与类别。"
            "清单默认按「谁最先过期」排在前面——核心问题是「什么该先处理」，不是「最近买了什么」。",
            "Body",
        ),
        table(
            ["剩余天数 d", "颜色", "行动含义"],
            [
                ["d ≤ 30", "红", "马上处理"],
                ["30 < d < 180", "橙", "近期留意"],
                ["180 ≤ d < 365", "黄", "心里有数"],
                ["d ≥ 365", "绿", "不用操心"],
                ["已过期", "深红 + 过期天数", "单独一档，优先处理"],
            ],
        ),
        Spacer(1, 4),
        P("同一档内越接近过期颜色越深。剩余天数打开时用过期日减今天现算，数字永远跟日历走。", "Small"),
        phones(
            [
                ("assets/remember-me/05-items-colored.png", "清单着色：深红 / 红 / 橙 / 黄"),
                ("assets/remember-me/05-expiry-colors.png", "图例：颜色 = 紧急程度"),
            ],
            height=72 * mm,
        ),
    )

    slide(
        story,
        eyebrow("03 · SOLUTION · FIND & HOME"),
        P("3.4 查找与家庭", "H2"),
        P(
            "支持按过期情况、类别筛选，以及按名称 / 位置 / 备注关键词搜索。"
            "一人可加入多个家庭并切换——对应「以后住别处仍要看旧家物品」的真实场景。",
            "Lead",
        ),
        Spacer(1, 6),
        phones([("assets/remember-me/02-list.png", "清单顶栏：搜索 + 过期颜色筛选 + 当前家切换")], height=105 * mm),
    )

    slide(
        story,
        eyebrow("04 · ITERATION · 01–03"),
        P("迭代与洞察", "H2"),
        P(
            "相对「今天吃什么」里更重的推荐测试，Remember Me 的迭代主要来自<strong>自己在使用中的观察和思考</strong>。"
            "外部真实反馈目前明确可复述的只有一条。验证方式不同，不是偷懒，而是产品阶段与问题类型不同。",
            "Body",
        ),
        issue(
            "01",
            "定位转折：从「我一个人用」到「全家一起用」",
            "最早做成给自己用的单机本子。但家庭共用物品常是一个人买、其他人找或根本不知道，直到过期才被翻出造成浪费。"
            "于是定位改成全家共用：字段、过期颜色、账号与家庭空间都按多人场景重定。",
            "ok",
        ),
        Spacer(1, 3),
        issue(
            "02",
            "先把主路径做顺，再接云端",
            "核心功能——记录物品信息必须先顺。先在本地把录入和清单做清楚，再做家庭同步。"
            "保质期快捷按钮少让人换算日历；排序默认「谁先过期」。",
            "ok",
        ),
        Spacer(1, 3),
        issue(
            "03",
            "自用观察驱动改版",
            "第一版太单调、删除编辑不明显。加大触控区与类别标签，补照片与排序筛选。"
            "放了柴犬小六卡通形象，进门可播放《4am》（可静音），装饰不喧宾夺主。",
            "warn",
        ),
    )

    slide(
        story,
        eyebrow("04 · ITERATION · 04–05"),
        P("迭代与洞察（续）", "H2"),
        issue(
            "04",
            "共享落地时的平台约束",
            "登录用用户名 + 密码，家庭成员场景不必接微信/短信。腾讯云不允许网页自助开号，去掉注册入口，账号只在控制台开通。"
            "体验版只有 PostgreSQL，数据改走 SQL；前端从 Vercel 迁到 CloudBase，与后端同落腾讯云。",
        ),
        Spacer(1, 4),
        issue(
            "05",
            "唯一外部交互反馈：按钮被挡住了",
            "家庭成员在手机上试，发现音乐控件挡住了「保存」，电脑宽屏上看不出来。"
            "把保存改到底部主按钮，音乐改成可拖、可贴边的小钮。提醒我：这个产品的使用设备是手机。",
            "ok",
        ),
    )

    slide(
        story,
        eyebrow("04 · ITERATION · 06–07"),
        P("迭代与洞察（续）", "H2"),
        issue(
            "06",
            "一家不够用，分类也不够找——多家切换 + 关键词搜索",
            "以后可能到别的城市，新家旧家物品都要看；东西多了单靠过期/类别不好找。"
            "于是支持一人多家，并加关键词搜索（可与原筛选叠加）。库表本允许多家，主要改前端认家逻辑。",
            "warn",
        ),
        Spacer(1, 4),
        issue(
            "07",
            "默认域名能开着开着变成下载——排查后改成诚实说明",
            "默认域名有时正常、有时出风险页、有时下载 index.html。是平台对未备案域名的策略；重传无效。"
            "短期写清试用说明，根本解法是申请备案域名（目前正在申请中）。",
            "warn",
        ),
    )

    slide(
        story,
        eyebrow("05 · METHOD"),
        P("过程方法：从翻聊天的痛苦，到开发日志 Skill", "H2"),
        Spacer(1, 8),
        P(
            "整理第一个作品集（今天吃什么）时，我需要翻大量对话才能拼出「当时为什么这么做」，过程很痛苦，也容易漏掉决策理由。",
            "Lead",
        ),
        P(
            "所以做 Remember Me 时，一开始就加了硬约束：每完成一步，就同时记录在开发日志中：做了什么、为什么、遇到什么问题、怎么解决、有没有反馈。"
            "这份记录后来收成可复用的 Skill，让之后的项目默认带着「外人也能读懂」的过程资产，不需要事后再费力整理。",
            "Lead",
        ),
        Spacer(1, 8),
        callout(
            "WHY THIS MATTERS",
            "「今天吃什么」让我确认：复杂推荐必须靠测试验证假设。"
            "Remember Me 则是在家庭私域与平台约束里，把工具真正做成可上线的形态，并把复盘方法固定下来。",
        ),
    )

    slide(
        story,
        eyebrow("06 · FUTURE"),
        P("未来优化方向", "H2"),
        *panels(
            [
                (
                    "可点户型图",
                    "<b>当前</b>位置靠文字字段 + 照片。<br/>"
                    "<b>局限</b>对不熟布局的人不够直观。<br/>"
                    "<b>未来</b>把家做成可点平面图标位置；家不大且照片够用时后做。",
                ),
                (
                    "小六语音入口",
                    "<b>当前</b>记下、查找靠点选与打字。<br/>"
                    "<b>局限</b>录入字段多时手机打字成本高。<br/>"
                    "<b>未来</b>点柴犬说话完成「记下」或「找东西」。",
                ),
                (
                    "备案自定义域名",
                    "<b>当前</b>CloudBase 默认域名可能出风险页或下载。<br/>"
                    "<b>局限</b>试用说明不得不写得很长。<br/>"
                    "<b>未来</b>正在申请备案域名，绑上后可正常分享。",
                ),
            ],
            cols=3,
        ),
    )

    slide(
        story,
        eyebrow("07 · REFLECTION"),
        P("项目收获", "H2"),
        *panels(
            [
                ("01", "数据敏感度决定产品形态：私域信息就要登录与家庭边界；轻试用能力可以免登录。"),
                ("02", "平台约束会改产品设计：不能网页自助注册时，诚实改成「控制台开号 + 只登录」更好。"),
                ("03", "上线约束也要写进产品说明：默认域名风控和打开方式、风险 Cookie 有关；说不清就会误导试用的人。"),
                ("04", "真机反馈不可替代：一条「按钮被挡住」就足以推翻桌面上看起来合理的布局。"),
                ("05", "验证强度要匹配问题：推荐机制需要更多结构化测试；生活工具早期可主要靠自用观察，但要诚实写明证据边界。"),
                ("06", "过程资产本身也是作品：开发日志 → Skill，把第一次作品集的坑变成第二次的默认能力。"),
            ],
            cols=3,
        ),
        callout("CLOSE", "把家里的私域工具做成可上线的形态，比多堆功能更重要：约束要写进设计，说明要写给试用的人听懂。"),
    )

    # last page — no trailing PageBreak: remove last PageBreak
    last = [
        eyebrow("08 · DEMO"),
        P("线上体验 · Remember Me", "H2"),
        P("已部署到 CloudBase。请用体验账号登录（非正式家人账号）：", "Lead"),
        P("<b>用户名 test1 · 密码 Abcd1234</b>", "Body"),
        Spacer(1, 6),
        callout(
            "打开说明",
            "<b>请用系统浏览器（Safari / Chrome）在地址栏打开完整链接。</b>"
            "当前仍是腾讯云默认域名：可能先出风险提示（点确认即可），也可能下载 index.html——"
            "手机、电脑都可能遇到，和打开方式、是否还在风险 Cookie 有效期内有关；请勿依赖主屏幕快捷方式。"
            "我正在申请备案域名，绑定后即可去掉这层限制。重传部署解决不了这个问题。",
        ),
        Spacer(1, 6),
        P("https://remember-me-remember-me-d1gmd5iiu9d88c58a.webapps.tcloudbase.com", "Body"),
        Spacer(1, 10),
        P("作品集网站：https://ziao-huang-0108.github.io/ziao-huang.github.io/", "Small"),
        P("© 黄子骜 · Ziao Huang", "Small"),
    ]
    story.extend(last)

    # remove trailing PageBreaks
    while story and isinstance(story[-1], PageBreak):
        story.pop()

    doc.build(story)
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    build()
