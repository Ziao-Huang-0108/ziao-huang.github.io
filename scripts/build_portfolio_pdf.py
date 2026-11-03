#!/usr/bin/env python3
"""Dense landscape PPT portfolio — filled slides, large phone shots, no orphans."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.platypus import (
    Frame,
    Image,
    KeepTogether,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.flowables import KeepInFrame

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Ziao-Huang-Portfolio.pdf"

PAGE_W, PAGE_H = 338 * mm, 190 * mm
MARGIN_X, MARGIN_Y = 5 * mm, 4 * mm
CONTENT_W = PAGE_W - 2 * MARGIN_X
CONTENT_H = PAGE_H - 2 * MARGIN_Y  # ~182mm

INK = HexColor("#14151a")
MUTE = HexColor("#5c606b")
AMBER = HexColor("#c45c26")
PAPER = HexColor("#eef0f3")
SURFACE = HexColor("#fbfcfd")
LINE = HexColor("#d5d8de")
OK = HexColor("#15803d")
WARN = HexColor("#b45309")
TAKE_BG = HexColor("#f7ebe3")

pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
FONT = "STSong-Light"

# Phone screenshots are ~473×1024 → aspect ≈ 0.462
PHONE_ASPECT = 473 / 1024


def styles():
    ss = getSampleStyleSheet()
    ss.add(ParagraphStyle(name="Eyebrow", fontName=FONT, fontSize=11, textColor=AMBER, leading=13, spaceAfter=1))
    ss.add(ParagraphStyle(name="H1", fontName=FONT, fontSize=26, textColor=INK, leading=30, spaceAfter=2))
    ss.add(ParagraphStyle(name="H2", fontName=FONT, fontSize=18, textColor=INK, leading=22, spaceAfter=2))
    ss.add(ParagraphStyle(name="Body", fontName=FONT, fontSize=11, textColor=INK, leading=14.5, spaceAfter=1.5))
    ss.add(ParagraphStyle(name="Lead", fontName=FONT, fontSize=12.5, textColor=INK, leading=16.5, spaceAfter=2))
    ss.add(ParagraphStyle(name="Small", fontName=FONT, fontSize=9, textColor=MUTE, leading=11, alignment=1))
    ss.add(ParagraphStyle(name="Label", fontName=FONT, fontSize=9.5, textColor=AMBER, leading=12, spaceAfter=1))
    ss.add(ParagraphStyle(name="Cell", fontName=FONT, fontSize=10, textColor=INK, leading=12.5))
    ss.add(ParagraphStyle(name="CellHead", fontName=FONT, fontSize=10.5, textColor=INK, leading=12.5))
    ss.add(ParagraphStyle(name="Take", fontName=FONT, fontSize=11, textColor=AMBER, leading=14.5))
    return ss


S = styles()


def P(text, style="Body"):
    return Paragraph(str(text).replace("\n", "<br/>"), S[style])


def eyebrow(text):
    return P(text, "Eyebrow")


def fit_image(path, max_w, max_h):
    img = Image(str(ROOT / path))
    scale = min(max_w / float(img.imageWidth), max_h / float(img.imageHeight))
    img.drawWidth = float(img.imageWidth) * scale
    img.drawHeight = float(img.imageHeight) * scale
    return img


def boxify(flowables, width, bg=SURFACE, border=LINE, left_bar=None, pad=5):
    data = [[f] for f in flowables]
    t = Table(data, colWidths=[width])
    cmds = [
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("BOX", (0, 0), (-1, -1), 0.5, border),
        ("LEFTPADDING", (0, 0), (-1, -1), pad),
        ("RIGHTPADDING", (0, 0), (-1, -1), pad),
        ("TOPPADDING", (0, 0), (-1, -1), pad - 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), pad - 1),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]
    if left_bar is not None:
        cmds.append(("LINEBEFORE", (0, 0), (0, -1), 3.5, left_bar))
    t.setStyle(TableStyle(cmds))
    return t


def callout(label, text, width):
    return boxify([P(label, "Label"), P(text, "Body")], width, left_bar=AMBER, pad=6)


def takeaway(text, width):
    return boxify([P(f"<b>这一页记住：</b>{text}", "Take")], width, bg=TAKE_BG, left_bar=AMBER, pad=6)


ZERO = TableStyle(
    [
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]
)


def two_col(left, right, ratios=(0.45, 0.55), gap=5):
    lw = CONTENT_W * ratios[0] - gap / 2
    rw = CONTENT_W * ratios[1] - gap / 2
    left_t = Table([[x] for x in left], colWidths=[lw])
    right_t = Table([[x] for x in right], colWidths=[rw])
    left_t.setStyle(ZERO)
    right_t.setStyle(ZERO)
    t = Table([[left_t, right_t]], colWidths=[lw + gap / 2, rw + gap / 2])
    t.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    return t


def panels(items, cols, width):
    gap = 4
    cw = (width - gap * (cols - 1)) / cols
    row, rows = [], []
    for title, body in items:
        cell = boxify(
            [P(f"<font color='#c45c26'><b>{title}</b></font>", "Body"), P(body, "Body")],
            cw,
            pad=5,
        )
        row.append(cell)
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
        tbl.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ]
            )
        )
        out.append(tbl)
        out.append(Spacer(1, 2))
    return out


def issue(num, title, body, kind="normal", width=None):
    width = width or CONTENT_W
    color = AMBER if kind == "normal" else (WARN if kind == "warn" else OK)
    hx = {AMBER: "#c45c26", WARN: "#b45309", OK: "#15803d"}[color]
    return boxify(
        [P(f"<font color='{hx}'><b>{num}</b></font>  <b>{title}</b>", "Body"), P(body, "Body")],
        width,
        left_bar=color,
        pad=4,
    )


def table(headers, rows, width):
    data = [[P(f"<b>{h}</b>", "CellHead") for h in headers]]
    for r in rows:
        data.append([P(c, "Cell") for c in r])
    cols = len(headers)
    if cols == 3:
        widths = [width * 0.26, width * 0.28, width * 0.46]
    elif cols == 2:
        widths = [width * 0.32, width * 0.68]
    else:
        widths = [width / cols] * cols
    t = Table(data, colWidths=widths)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), SURFACE),
                ("GRID", (0, 0), (-1, -1), 0.5, LINE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 2.5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
            ]
        )
    )
    return t


# reportlab Frame silently drops images when wrapped height sits within ~4mm of CONTENT_H
SAFE_H = CONTENT_H - 6 * mm


def phone_h_for_n(n, chrome=14 * mm, gap=8):
    """Max phone height so n phones + captions + chrome fit safely (no silent drop)."""
    avail = SAFE_H - chrome - 4 * mm  # caption row
    max_by_w = (CONTENT_W - gap * (n - 1)) / (n * PHONE_ASPECT)
    return min(avail, max_by_w)


def phones(paths_captions, height=None, n=None, band_w=None):
    """Portrait shots packed to max readable size. band_w defaults to full content width."""
    n = n or len(paths_captions)
    band_w = band_w or CONTENT_W
    if height is None:
        height = phone_h_for_n(n)
    # also respect band width
    max_by_band = (band_w - 8 * (n - 1)) / (n * PHONE_ASPECT)
    height = min(height, max_by_band)
    max_w = height * PHONE_ASPECT + 2
    cells, widths = [], []
    for path, cap in paths_captions:
        img = fit_image(path, max_w, height)
        cw = img.drawWidth + 1
        cell = Table([[img], [P(cap, "Small")]], colWidths=[cw])
        cell.setStyle(ZERO)
        cells.append(cell)
        widths.append(cw)
    gap = 8
    row, cols = [], []
    for i, cell in enumerate(cells):
        if i:
            row.append("")
            cols.append(gap)
        row.append(cell)
        cols.append(widths[i])
    inner = Table([row], colWidths=cols)
    inner.setStyle(ZERO)
    outer = Table([[inner]], colWidths=[band_w])
    outer.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    return outer


def phone_beside_text(text_flowables, phone_path, caption, phone_h=None, text_ratio=0.38):
    """Text column + one near-full-height phone filling the rest of the width."""
    if phone_h is None:
        phone_h = min(SAFE_H - 4 * mm, 162 * mm)
    pw = CONTENT_W * (1 - text_ratio) - 4
    img = fit_image(phone_path, min(pw - 2, phone_h * PHONE_ASPECT + 4), phone_h)
    right = Table([[img], [P(caption, "Small")]], colWidths=[img.drawWidth + 1])
    right.setStyle(ZERO)
    right_wrap = Table([[right]], colWidths=[pw])
    right_wrap.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    return two_col(text_flowables, [right_wrap], ratios=(text_ratio, 1 - text_ratio))


def dual_phones_rail(title, body, paths_captions, rail_blocks):
    """Full-width eyebrow, then two max-height phones + tall right rail."""
    rail_ratio = 0.28
    phone_band = CONTENT_W * (1 - rail_ratio) - 4
    # only one eyebrow line above the row → phones can be ~160mm+
    h = phone_h_for_n(2, chrome=11 * mm, gap=8)
    h = min(h, (phone_band - 8) / (2 * PHONE_ASPECT))
    row = two_col(
        [phones(paths_captions, height=h, band_w=phone_band)],
        rail_blocks,
        ratios=(1 - rail_ratio, rail_ratio),
        gap=6,
    )
    return [eyebrow(f"{title}　｜　{body}"), Spacer(1, 2), row]


def header_phones(title_line, sub_line, paths_captions):
    """Thin top copy + max-size phones, height capped for safe draw."""
    n = len(paths_captions)
    chrome = 16 * mm if sub_line else 10 * mm
    h = phone_h_for_n(n, chrome=chrome, gap=10)
    items = [eyebrow(title_line)]
    if sub_line:
        items.append(P(sub_line, "Body"))
    items.append(Spacer(1, 2))
    items.append(phones(paths_captions, height=h))
    return items


def measure(flowables):
    from reportlab.platypus.flowables import _listWrapOn

    _, h = _listWrapOn(list(flowables), CONTENT_W, None)
    return None, h


def build():
    c = pdfcanvas.Canvas(str(OUT), pagesize=(PAGE_W, PAGE_H))
    slides: list[list] = []

    # 01 Cover — eyebrow + 3 phones max size (fills width)
    slides.append(
        [
            eyebrow("PORTFOLIO · 黄子骜 · Ziao Huang　｜　大四 · 数学与应用数学 · 研究 / 策略 / 分析 / 产品运营"),
            P(
                "邮箱 zaozhi030108@outlook.com　｜　https://ziao-huang-0108.github.io/ziao-huang.github.io/　｜　也写歌 · 网易云 163cn.tv/bjSkQBzl",
                "Body",
            ),
            phones(
                [
                    ("assets/hero/eatwhat.jpg", "今天吃什么 · 免登录决策层"),
                    ("assets/hero/remember-me.jpg", "Remember Me · 家庭私域"),
                ],
                height=phone_h_for_n(2, chrome=14 * mm, gap=12),
            ),
        ]
    )

    # 02 Compare — board + takeaway, no orphan text
    slides.append(
        [
            eyebrow("HOME · COMPARE　两个项目怎么不一样"),
            fit_image("assets/pdf/compare-board.png", CONTENT_W, 148 * mm),
            takeaway("形态不同 → 登录策略、验证方式、技术选型都会跟着变。", CONTENT_W),
        ]
    )

    # 03 Case 01 opener — dense text + giant phone (was sparse "一行字" when orphaned)
    toc_rows = [
        [P("<b>01</b> 背景", "Body"), P("<b>05</b> 测试", "Body")],
        [P("<b>02</b> 目标", "Body"), P("<b>06</b> 展望", "Body")],
        [P("<b>03</b> 方案", "Body"), P("<b>07</b> 收获", "Body")],
        [P("<b>04</b> MVP", "Body"), P("<b>08</b> Demo", "Body")],
    ]
    toc = Table(toc_rows, colWidths=[CONTENT_W * 0.18, CONTENT_W * 0.18])
    toc.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), SURFACE),
                ("BOX", (0, 0), (-1, -1), 0.5, LINE),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, LINE),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    slides.append(
        [
            phone_beside_text(
                [
                    eyebrow("CASE 01 · 今天吃什么"),
                    P("协调多方需求，快速给出可接受答案", "H2"),
                    P("免登录 · 2026.9 · Next.js · 能力层（已有餐厅库，缺多人决策）", "Body"),
                    toc,
                    Spacer(1, 2),
                    boxify(
                        [
                            P("TL;DR", "Label"),
                            P(
                                "· 列表很多，决策很难<br/>"
                                "· 可组合成员档案 + 硬/软分层推荐<br/>"
                                "· 构造场景打脸假设<br/>"
                                "· 召回与排序目标必须对齐",
                                "Body",
                            ),
                        ],
                        CONTENT_W * 0.34,
                        left_bar=AMBER,
                        pad=5,
                    ),
                    Spacer(1, 2),
                    takeaway("缺的是多人决策，不是又一个列表。", CONTENT_W * 0.34),
                ],
                "assets/eatwhat/04-result-phone.jpg",
                "推荐结果页",
                phone_h=158 * mm,
                text_ratio=0.36,
            )
        ]
    )

    # 04 Problem — text + big phone
    slides.append(
        [
            phone_beside_text(
                [
                    eyebrow("01 · PROBLEM"),
                    P("多人吃饭，为什么这么难？", "H2"),
                    P(
                        "面对「吃什么」，很多人说「随便」，或只给模糊范围。"
                        "多人时需求冲突；选不好，做决定的人压力大。",
                        "Lead",
                    ),
                    P(
                        "美团 / 点评 / 小红书更擅长<strong>给列表</strong>。"
                        "用户仍要自己决定，也难同时结合多人需求。",
                        "Body",
                    ),
                    callout(
                        "CORE QUESTION",
                        "不是「找不到店」，而是很难快速找到大家都能接受的答案。",
                        CONTENT_W * 0.36,
                    ),
                    Spacer(1, 2),
                    takeaway("找得到 ≠ 决定得了。", CONTENT_W * 0.36),
                ],
                "assets/eatwhat/01-members-phone.jpg",
                "成员档案（偏好 / 忌口）",
                phone_h=158 * mm,
                text_ratio=0.38,
            )
        ]
    )

    # 05 Goal
    slides.append(
        [
            eyebrow("02 · GOAL　产品目标与定位"),
            *panels(
                [
                    ("个性化", "多成员偏好、忌口与历史反馈可组合。"),
                    ("需求理解", "偏好与忌口变成结构化条件。"),
                    ("可解释", "展示推荐依据与评分构成。"),
                    ("反馈闭环", "评分回写到具体成员。"),
                ],
                cols=4,
                width=CONTENT_W,
            ),
            two_col(
                [
                    callout(
                        "POSITIONING",
                        "目标是多人下的「可接受」，不是预测「最喜欢」。"
                        "更接近平台可加的<strong>决策能力层</strong>；免登录点开即用。",
                        CONTENT_W * 0.48,
                    ),
                    Spacer(1, 3),
                    takeaway("可接受 > theoretically 最优。", CONTENT_W * 0.48),
                    Spacer(1, 3),
                    P("验证方式：构造冲突场景，看结果是否打脸假设。", "Body"),
                ],
                [fit_image("assets/pdf/priority-layers.png", CONTENT_W * 0.48, 118 * mm)],
                ratios=(0.5, 0.5),
            ),
        ]
    )

    # 06 Solution flow
    slides.append(
        [
            eyebrow("03 · SOLUTION · FLOW　推荐链路"),
            two_col(
                [fit_image("assets/pdf/recommend-funnel.png", CONTENT_W * 0.46, 155 * mm)],
                [
                    boxify(
                        [
                            P("旁注", "Label"),
                            P("<b>硬过滤</b>　安全与可达", "Body"),
                            P("<b>排除差评</b>　避免踩雷", "Body"),
                            P("<b>软门控</b>　尽量满足这次想吃", "Body"),
                            P("<b>评分</b>　池内比高低", "Body"),
                            P("<b>回写</b>　记忆归属成员", "Body"),
                        ],
                        CONTENT_W * 0.48,
                        pad=7,
                    ),
                    Spacer(1, 4),
                    takeaway("召回决定候选，排序决定结果。", CONTENT_W * 0.48),
                    Spacer(1, 4),
                    fit_image("assets/eatwhat/05-detail-phone.jpg", CONTENT_W * 0.22, 70 * mm),
                    P("可解释评分明细", "Small"),
                ],
                ratios=(0.48, 0.52),
            ),
        ]
    )

    # 07 Hard vs soft
    slides.append(
        [
            eyebrow("03 · SOLUTION · DESIGN　硬约束 vs 软偏好"),
            two_col(
                [
                    P("可组合成员档案：跟不同的人吃饭，需求组合也不同。硬约束不能违反；软偏好尽量满足，但不一票否决。", "Lead"),
                    Spacer(1, 2),
                    table(
                        ["因素", "层级", "行为"],
                        [
                            ["忌口 / 过敏", "硬约束", "命中即淘汰"],
                            ["最大距离", "硬约束（可放宽）", "空则放宽"],
                            ["历史 1–2 星", "排除", "不进池"],
                            ["饮食偏好", "软门控", "子集或全候选"],
                            ["场景 / 星级 / 好评", "评分", "池内打分"],
                            ["用餐人数", "仅展示", "不再硬淘汰"],
                        ],
                        CONTENT_W * 0.54,
                    ),
                    Spacer(1, 3),
                    callout(
                        "设计含义",
                        "人数曾被当成硬约束 → 测试打脸后降级为展示。"
                        "「当下想吃」必须压过历史好评，否则永远推「上次喜欢的」。",
                        CONTENT_W * 0.54,
                    ),
                    Spacer(1, 3),
                    takeaway("分层错了，后面怎么排都救不回来。", CONTENT_W * 0.54),
                ],
                [
                    fit_image("assets/pdf/priority-layers.png", CONTENT_W * 0.42, 118 * mm),
                    Spacer(1, 3),
                    fit_image("assets/eatwhat/05-detail-phone.jpg", CONTENT_W * 0.20, 52 * mm),
                    P("评分明细对应上表各层", "Small"),
                ],
                ratios=(0.56, 0.44),
            ),
        ]
    )

    # 08–10 MVP: 2 large phones + rail (fills width, readable height)
    rw = CONTENT_W * 0.30
    slides.append(
        dual_phones_rail(
            "04 · MVP　① 成员 → ② 场景",
            "先选定谁吃、什么场合；成员档案决定硬/软条件。",
            [
                ("assets/eatwhat/01-members-phone.jpg", "① 选择用餐人档案"),
                ("assets/eatwhat/02-scene-phone.jpg", "② 用餐场景与人数"),
            ],
            [
                callout("为什么先这两步", "场景影响口味与预算感；档案里的忌口是硬约束。", rw),
                Spacer(1, 3),
                callout("这一屏看什么", "谁被选中、忌口标签是否进条件、场景是否影响后续池子。", rw),
                Spacer(1, 3),
                takeaway("输入越结构化，推荐越可解释。", rw),
            ],
        )
    )
    slides.append(
        dual_phones_rail(
            "04 · MVP　③ 距离 → ④ 结果",
            "距离是可达硬约束；结果页必须说得清「为什么」。",
            [
                ("assets/eatwhat/03-distance-phone.jpg", "③ 最大距离"),
                ("assets/eatwhat/04-result-phone.jpg", "④ 推荐结果与理由"),
            ],
            [
                callout("结果页要什么", "通过了哪些过滤、分数怎么来、跟谁的记忆有关。", rw),
                Spacer(1, 3),
                callout("距离的角色", "硬约束但可放宽；空池时优先松距离，而不是硬推差结果。", rw),
                Spacer(1, 3),
                takeaway("可接受答案 > 黑盒最优。", rw),
            ],
        )
    )
    slides.append(
        dual_phones_rail(
            "04 · MVP　⑤ 明细 → ⑥ 操作",
            "展开评分构成；打分 / 再抽 / 出发，把反馈写回档案。",
            [
                ("assets/eatwhat/05-detail-phone.jpg", "⑤ 可解释评分明细"),
                ("assets/eatwhat/06-actions.png", "⑥ 打分 / 再抽 / 出发"),
            ],
            [
                callout("闭环", "操作必须回写成员；否则下次推荐还会漂。", rw),
                Spacer(1, 3),
                callout("明细的价值", "打脸假设时，先看因子，再改权重/门控，而不是改感觉。", rw),
                Spacer(1, 3),
                takeaway("可解释 + 可回写 = 推荐闭环。", rw),
            ],
        )
    )

    slides.append(
        [
            eyebrow("04 · DEBUG　让异常结果可复盘　｜　看不见中间态，就只能靠感觉吵架"),
            two_col(
                [
                    P("Usage Log / Debug：还原「为什么推这家」。", "Lead"),
                    P(
                        "推荐一旦「看起来不对」，如果看不到过滤与打分中间态，"
                        "就只能靠感觉吵架。把链路摊开，才能改假设、改权重。",
                        "Body",
                    ),
                    Spacer(1, 2),
                    callout(
                        "看什么",
                        "· 谁被硬过滤掉了<br/>· 软门控后池子剩多少<br/>· 各因子分数与最终排序<br/>· 权重改完能否复现同一结果",
                        CONTENT_W * 0.32,
                    ),
                    Spacer(1, 2),
                    takeaway("Debug 是产品能力，不是开发私货。", CONTENT_W * 0.32),
                ],
                [fit_image("assets/eatwhat/06-debug.png", CONTENT_W * 0.66, 162 * mm)],
                ratios=(0.34, 0.66),
            ),
        ]
    )

    # Testing + future + demo — dense two columns + funnel figure
    slides.append(
        [
            eyebrow("05–08 · TESTING · FUTURE · DEMO　用结果打脸假设；功能做完 ≠ 验证完成"),
            two_col(
                [
                    issue("01", "用餐人数不应硬限制", "一人食+火锅被滤掉 → 人数改参考。", width=CONTENT_W * 0.48),
                    Spacer(1, 1),
                    issue("02", "无用的输入要删", "交通方式不进逻辑 → 删字段。", width=CONTENT_W * 0.48),
                    Spacer(1, 1),
                    issue("03", "记忆归属成员", "A 的五星影响只选 B → 绑档案。", width=CONTENT_W * 0.48),
                    Spacer(1, 1),
                    issue("04", "当下 > 历史", "想火锅却推历史泰国菜 → 本次偏好前置。", "warn", CONTENT_W * 0.48),
                    Spacer(1, 1),
                    issue("05", "召回 ≠ 排序", "进了池仍排不上 → 目标对齐。", "ok", CONTENT_W * 0.48),
                    Spacer(1, 2),
                    takeaway("构造冲突场景，让结果打脸假设。", CONTENT_W * 0.48),
                ],
                [
                    fit_image("assets/pdf/recommend-funnel.png", CONTENT_W * 0.48, 78 * mm),
                    Spacer(1, 2),
                    *panels(
                        [
                            ("真实位置", "多成员定位，中间地带更公平。"),
                            ("菜品级匹配", "餐厅 → 菜品 → 成员。"),
                            ("群体满意度", "满足了多少人写进排序。"),
                            ("收获", "合理≠该做约束；推荐是产品；跑通≠闭环；翻聊天痛 → 写日志。"),
                        ],
                        cols=2,
                        width=CONTENT_W * 0.48,
                    ),
                    callout(
                        "DEMO（免登录）",
                        "https://eatwhat-d8g01gpqk878dd6ed-1324990131.tcloudbaseapp.com",
                        CONTENT_W * 0.48,
                    ),
                ],
                ratios=(0.5, 0.5),
            ),
        ]
    )

    # 13 Case 02 opener
    slides.append(
        [
            phone_beside_text(
                [
                    eyebrow("CASE 02 · Remember Me"),
                    P("全家物品小本子", "H2"),
                    P("需登录 · App 雏形 · 2026.10 · PWA / CloudBase / PG", "Body"),
                    boxify(
                        [
                            P("TL;DR", "Label"),
                            P(
                                "· 找不到 / 过期 / 不共享<br/>"
                                "· 登录家庭空间 + 过期色标<br/>"
                                "· 自用观察 + 一条真机反馈<br/>"
                                "· 开发日志 → Skill",
                                "Body",
                            ),
                        ],
                        CONTENT_W * 0.40,
                        left_bar=AMBER,
                        pad=5,
                    ),
                    Spacer(1, 2),
                    callout(
                        "形态对比",
                        "吃什么 = 能力层免登录；Remember Me = 私域需登录。数据敏感度决定产品形态。",
                        CONTENT_W * 0.40,
                    ),
                    Spacer(1, 2),
                    takeaway("数据敏感度决定产品形态。", CONTENT_W * 0.40),
                ],
                "assets/remember-me/05-items-colored.png",
                "过期着色清单",
                phone_h=158 * mm,
                text_ratio=0.40,
            )
        ]
    )

    # 14 Problem + access rationale
    slides.append(
        [
            eyebrow("01–03 · PROBLEM · ACCESS　私域边界 · 为什么要登录"),
            two_col(
                [
                    P("忘了放哪 · 过期才发现 · 重复购买 · 信息不共享", "Lead"),
                    callout(
                        "CORE",
                        "一家人共用一本子，同时把私密信息关在可控范围里。"
                        "免登录适合能力层；家庭物品属于私域，必须先身份后空间。",
                        CONTENT_W * 0.46,
                    ),
                    Spacer(1, 2),
                    table(
                        ["角色", "需求"],
                        [
                            ["采购者", "录入要快，少打断"],
                            ["使用者", "能快速搜到位置/过期"],
                            ["家庭", "权限边界清晰，可切家"],
                        ],
                        CONTENT_W * 0.46,
                    ),
                    Spacer(1, 2),
                    callout(
                        "ACCESS",
                        "不开放自助注册；体验账号 test1 / Abcd1234。"
                        "登录 → 选家 → 清单，两步把「谁」和「哪一家」拆开。",
                        CONTENT_W * 0.46,
                    ),
                    Spacer(1, 2),
                    takeaway("私域产品：先边界，再体验。", CONTENT_W * 0.46),
                ],
                [fit_image("assets/pdf/login-boundary.png", CONTENT_W * 0.5, 155 * mm)],
                ratios=(0.48, 0.52),
            ),
        ]
    )

    slides.append(
        dual_phones_rail(
            "03 · ACCESS UI　登录 → 选家",
            "先身份，再进家庭空间；一人可属多家，切家必须显式。",
            [
                ("assets/remember-me/03-login.png", "登录页"),
                ("assets/remember-me/04-pick-home.png", "选家页"),
            ],
            [
                callout("为何两步", "把「谁」和「哪一家」拆开，避免写错空间。", rw),
                Spacer(1, 3),
                callout("体验账号", "test1 / Abcd1234 · 不开放自助注册。", rw),
                Spacer(1, 3),
                takeaway("私域入口要短，但边界要硬。", rw),
            ],
        )
    )

    # 16 Color — ramp + 2 phones
    slides.append(
        [
            eyebrow("03 · COLOR　过期颜色 = 行动信号"),
            fit_image("assets/pdf/expiry-ramp.png", CONTENT_W, 42 * mm),
            Spacer(1, 2),
            phones(
                [
                    ("assets/remember-me/05-items-colored.png", "着色清单"),
                    ("assets/remember-me/02-list.png", "搜索 / 筛选 / 切家"),
                ],
                height=phone_h_for_n(2, chrome=52 * mm),
            ),
        ]
    )

    # 17 Iteration + method + demo — one dense closing slide
    slides.append(
        [
            eyebrow("04–08 · ITERATION · METHOD · DEMO"),
            two_col(
                [
                    issue("01", "我一个人用 → 全家一起用", "共用物品常一人买、其他人找。", "ok", CONTENT_W * 0.48),
                    Spacer(1, 1),
                    issue("02", "先主路径再云端", "录入/清单先顺；默认谁先过期。", "ok", CONTENT_W * 0.48),
                    Spacer(1, 1),
                    issue("05", "真机：按钮被挡住", "音乐挡住保存 → 底部主按钮。", "ok", CONTENT_W * 0.48),
                    Spacer(1, 1),
                    issue("06", "多家 + 关键词搜索", "新家旧家都要看；搜索叠加筛选。", "warn", CONTENT_W * 0.48),
                    Spacer(1, 1),
                    issue("07", "默认域名变下载", "未备案策略；备案中；重传无效。", "warn", CONTENT_W * 0.48),
                    Spacer(1, 2),
                    takeaway("真机一条反馈，就能推翻桌面上看起来合理的布局。", CONTENT_W * 0.48),
                ],
                [
                    fit_image("assets/pdf/method-loop.png", CONTENT_W * 0.48, 72 * mm),
                    Spacer(1, 2),
                    *panels(
                        [
                            ("可点户型图", "位置更直观。"),
                            ("小六语音", "说话记下/查找。"),
                            ("备案域名", "去掉风险页限制。"),
                        ],
                        cols=3,
                        width=CONTENT_W * 0.48,
                    ),
                    callout(
                        "METHOD → Skill",
                        "每步记录：做了什么 / 为什么 / 问题 / 解法 / 反馈。",
                        CONTENT_W * 0.48,
                    ),
                    Spacer(1, 2),
                    boxify(
                        [
                            P("DEMO　test1 / Abcd1234", "Label"),
                            P(
                                "https://remember-me-remember-me-d1gmd5iiu9d88c58a.webapps.tcloudbase.com<br/>"
                                "作品集 https://ziao-huang-0108.github.io/ziao-huang.github.io/　© 黄子骜",
                                "Body",
                            ),
                        ],
                        CONTENT_W * 0.48,
                        left_bar=AMBER,
                        pad=5,
                    ),
                ],
                ratios=(0.5, 0.5),
            ),
        ]
    )

    # Exactly one page per slide. Only shrink if over-height.
    for idx, flowables in enumerate(slides, start=1):
        c.setFillColor(PAPER)
        c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
        frame = Frame(MARGIN_X, MARGIN_Y, CONTENT_W, CONTENT_H, id=f"s{idx}", showBoundary=0)
        items = list(flowables)
        _, h = measure(items)
        if h > SAFE_H:
            payload = [KeepInFrame(CONTENT_W, SAFE_H, items, mode="shrink")]
            print(f"slide {idx} shrink from {h / mm:.1f}mm → {SAFE_H / mm:.1f}mm")
        else:
            payload = items
            print(f"slide {idx} ok h={h / mm:.1f}mm / {CONTENT_H / mm:.1f}mm fill={100 * h / CONTENT_H:.0f}%")
        leftover = frame.addFromList(payload, c)
        if leftover:
            print(f"WARNING slide {idx} leftover={len(leftover)}")
        c.setFillColor(MUTE)
        c.setFont(FONT, 9)
        c.drawRightString(PAGE_W - MARGIN_X, 2.2 * mm, f"{idx:02d}")
        c.showPage()

    c.save()
    print(f"Wrote {OUT} pages={len(slides)} bytes={OUT.stat().st_size}")


if __name__ == "__main__":
    build()
