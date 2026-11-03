#!/usr/bin/env python3
"""Build a dense landscape PPT-style portfolio PDF (full case content + extras)."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Ziao-Huang-Portfolio.pdf"

PAGE_W, PAGE_H = 338 * mm, 190 * mm
MARGIN_X, MARGIN_Y = 9 * mm, 7 * mm
CONTENT_W = PAGE_W - 2 * MARGIN_X
CONTENT_H = PAGE_H - 2 * MARGIN_Y

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
    ss.add(ParagraphStyle(name="Eyebrow", fontName=FONT, fontSize=12, textColor=AMBER, leading=16, spaceAfter=4))
    ss.add(ParagraphStyle(name="H1", fontName=FONT, fontSize=36, textColor=INK, leading=42, spaceAfter=8))
    ss.add(ParagraphStyle(name="H2", fontName=FONT, fontSize=26, textColor=INK, leading=32, spaceAfter=8))
    ss.add(ParagraphStyle(name="H3", fontName=FONT, fontSize=16, textColor=INK, leading=22, spaceBefore=4, spaceAfter=4))
    ss.add(ParagraphStyle(name="Body", fontName=FONT, fontSize=13.5, textColor=INK, leading=19, spaceAfter=5))
    ss.add(ParagraphStyle(name="Lead", fontName=FONT, fontSize=16.5, textColor=INK, leading=24, spaceAfter=6))
    ss.add(ParagraphStyle(name="Small", fontName=FONT, fontSize=11, textColor=MUTE, leading=15, spaceAfter=2))
    ss.add(ParagraphStyle(name="Label", fontName=FONT, fontSize=11, textColor=AMBER, leading=14, spaceAfter=2))
    ss.add(ParagraphStyle(name="CenterH1", fontName=FONT, fontSize=40, textColor=INK, leading=48, alignment=TA_CENTER, spaceAfter=8))
    ss.add(ParagraphStyle(name="CenterLead", fontName=FONT, fontSize=16, textColor=INK, leading=23, alignment=TA_CENTER, spaceAfter=6))
    ss.add(ParagraphStyle(name="Cell", fontName=FONT, fontSize=11.5, textColor=INK, leading=15))
    ss.add(ParagraphStyle(name="CellHead", fontName=FONT, fontSize=12, textColor=INK, leading=15))
    ss.add(ParagraphStyle(name="Take", fontName=FONT, fontSize=14, textColor=AMBER, leading=20, alignment=TA_LEFT))
    ss.add(ParagraphStyle(name="BigNum", fontName=FONT, fontSize=18, textColor=AMBER, leading=22))
    return ss


S = styles()
PAGE_NO = {"n": 0}


def draw_page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(PAPER)
    canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    PAGE_NO["n"] += 1
    canvas.setFillColor(MUTE)
    canvas.setFont(FONT, 9)
    canvas.drawRightString(PAGE_W - MARGIN_X, 4.5 * mm, f"{PAGE_NO['n']:02d}")
    canvas.restoreState()


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


def boxify(flowables, width, bg=SURFACE, border=LINE, left_bar=None, pad=8):
    inner = [[f] if not isinstance(f, list) else f for f in flowables]
    # single column stack
    data = [[f] for f in flowables]
    t = Table(data, colWidths=[width - 2])
    cmds = [
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("BOX", (0, 0), (-1, -1), 0.6, border),
        ("LEFTPADDING", (0, 0), (-1, -1), pad),
        ("RIGHTPADDING", (0, 0), (-1, -1), pad),
        ("TOPPADDING", (0, 0), (-1, -1), pad - 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), pad - 2),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]
    if left_bar is not None:
        cmds.append(("LINEBEFORE", (0, 0), (0, -1), 4, left_bar))
    t.setStyle(TableStyle(cmds))
    return t


def callout(label, text, width=None):
    w = width or CONTENT_W
    return boxify([P(label, "Label"), P(text, "Body")], w, left_bar=AMBER, pad=10)


def takeaway(text, width=None):
    w = width or CONTENT_W
    return boxify([P(f"<b>这一页记住：</b>{text}", "Take")], w, bg=HexColor("#f7ebe3"), left_bar=AMBER, pad=10)


def two_col(left, right, ratios=(0.52, 0.48), gap=8):
    usable = CONTENT_W
    lw = usable * ratios[0] - gap / 2
    rw = usable * ratios[1] - gap / 2
    left_t = Table([[x] for x in left], colWidths=[lw])
    right_t = Table([[x] for x in right], colWidths=[rw])
    left_t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
    right_t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
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


def fill_slide(*rows, row_heights=None):
    """Stack rows into a table that targets full content height."""
    data = [[r] for r in rows]
    t = Table(data, colWidths=[CONTENT_W], rowHeights=row_heights)
    t.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]
        )
    )
    return t


def panels(items, cols=2, width=None):
    usable = width or CONTENT_W
    gap = 8
    cw = (usable - gap * (cols - 1)) / cols
    row, rows = [], []
    for title, body in items:
        cell = boxify([P(f"<font color='#c45c26'><b>{title}</b></font>", "Body"), P(body, "Body")], cw, pad=9)
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
        tbl.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
        out.append(tbl)
        out.append(Spacer(1, 6))
    return out


def issue(num, title, body, kind="normal", width=None):
    color = AMBER if kind == "normal" else (WARN if kind == "warn" else OK)
    hex_map = {AMBER: "#c45c26", WARN: "#b45309", OK: "#15803d"}
    w = width or CONTENT_W
    return boxify(
        [P(f"<font color='{hex_map[color]}'><b>{num}</b></font>  <b>{title}</b>", "Body"), P(body, "Body")],
        w,
        left_bar=color,
        pad=8,
    )


def table(headers, rows, width=None):
    usable = width or CONTENT_W
    data = [[P(f"<b>{h}</b>", "CellHead") for h in headers]]
    for r in rows:
        data.append([P(c, "Cell") for c in r])
    cols = len(headers)
    if cols == 3:
        widths = [usable * 0.26, usable * 0.28, usable * 0.46]
    else:
        widths = [usable / cols] * cols
    t = Table(data, colWidths=widths)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), SURFACE),
                ("GRID", (0, 0), (-1, -1), 0.6, LINE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return t


def phones(paths_captions, height=112 * mm):
    n = len(paths_captions)
    gap = 10
    cw = (CONTENT_W - gap * (n - 1)) / n
    cells = []
    for path, cap in paths_captions:
        img = fit_image(path, cw, height)
        cell = Table([[img], [P(cap, "Small")]], colWidths=[cw])
        cell.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (0, 0), "BOTTOM"),
                    ("TOPPADDING", (0, 0), (-1, -1), 1),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
                ]
            )
        )
        cells.append(cell)
    t = Table([cells], colWidths=[cw] * n)
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "BOTTOM"), ("ALIGN", (0, 0), (-1, -1), "CENTER")]))
    return t


def diagram(path, max_w=None, max_h=None):
    return fit_image(path, max_w or CONTENT_W, max_h or (CONTENT_H - 28 * mm))


def slide(story, *flowables):
    story.extend(flowables)
    story.append(PageBreak())


def build():
    frame = Frame(MARGIN_X, MARGIN_Y, CONTENT_W, CONTENT_H, id="slide")
    doc = BaseDocTemplate(str(OUT), pagesize=(PAGE_W, PAGE_H))
    doc.addPageTemplates([PageTemplate(id="slide", frames=[frame], onPage=draw_page)])
    story = []

    # ===== 01 Cover =====
    left = [
        eyebrow("PORTFOLIO · PRODUCT / RESEARCH / OPS"),
        P("黄子骜 · Ziao Huang", "H1"),
        P(
            "宁波诺丁汉大学 · 大四 · 数学与应用数学。"
            "实习偏向用户研究、策略运营、数据分析、商业分析、产品运营。"
            "两个作品都来自真实生活：多人吃饭难决定、家里东西找不到或过期——"
            "做成可在线打开的产品，并写下完整复盘。",
            "Lead",
        ),
        Spacer(1, 6),
        callout("CONTACT", "邮箱 zaozhi030108@outlook.com<br/>作品集 https://ziao-huang-0108.github.io/ziao-huang.github.io/", CONTENT_W * 0.5),
        Spacer(1, 6),
        P("托管于 GitHub Pages · PDF 为演示向排版（可含网页外的示意图）", "Small"),
    ]
    right = [
        fit_image("assets/hero/eatwhat.jpg", CONTENT_W * 0.22, 118 * mm),
        fit_image("assets/hero/remember-me.jpg", CONTENT_W * 0.22, 118 * mm),
    ]
    right_row = Table([right], colWidths=[CONTENT_W * 0.23] * 2)
    right_row.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    slide(story, two_col(left, [right_row], ratios=(0.54, 0.46)))

    # ===== 02 Compare =====
    slide(
        story,
        eyebrow("HOME · COMPARE"),
        P("先看差异，再进 Case", "H2"),
        P("面试官 30 秒版：一个偏「平台可加的决策能力层」，一个偏「家庭私域独立 App 雏形」。", "Lead"),
        diagram("assets/pdf/compare-board.png", CONTENT_W, 128 * mm),
        takeaway("形态不同 → 登录策略、验证方式、技术选型都会跟着变。"),
    )

    # ===== 03 About + projects strip =====
    about_left = [
        eyebrow("HOME · ABOUT"),
        P("关于我", "H2"),
        P(
            "大四在读，数学与应用数学背景；做过用户调研、活动组织与 AI 产品原型。"
            "希望在偏研究、策略与分析的岗位里，把定量思维和可验证的落地结合起来。",
            "Lead",
        ),
        Spacer(1, 4),
        P("邮箱：zaozhi030108@outlook.com", "Body"),
        P("也写歌 · 网易云 https://163cn.tv/bjSkQBzl", "Body"),
        Spacer(1, 6),
        *panels(
            [
                ("今天吃什么", "免登录 · 推荐机制更重 · 更多结构化测试"),
                ("Remember Me", "需登录 · 自用观察驱动 · 开发日志 → Skill"),
            ],
            cols=1,
            width=CONTENT_W * 0.5,
        ),
    ]
    slide(
        story,
        two_col(
            about_left,
            [
                phones(
                    [
                        ("assets/eatwhat/04-result-phone.jpg", "今天吃什么"),
                        ("assets/remember-me/05-items-colored.png", "Remember Me"),
                    ],
                    height=118 * mm,
                )
            ],
            ratios=(0.48, 0.52),
        ),
    )

    # ===== 04 Eatwhat divider =====
    slide(
        story,
        two_col(
            [
                eyebrow("CASE 01"),
                P("今天吃什么", "H1"),
                P(
                    "不是选出「最好吃」的店，而是协调多方需求，快速给出一个大家都能接受的答案。",
                    "Lead",
                ),
                Spacer(1, 4),
                P("<b>免登录 · 点开即用</b>　｜　产品设计 / 推荐逻辑　｜　2026.9", "Body"),
                P("Next.js · LocalStorage", "Body"),
                Spacer(1, 8),
                takeaway("能力层：平台已有餐厅库，缺的是多人决策。", CONTENT_W * 0.5),
            ],
            [
                phones(
                    [
                        ("assets/eatwhat/01-members-phone.jpg", "成员"),
                        ("assets/eatwhat/04-result-phone.jpg", "结果"),
                    ],
                    height=116 * mm,
                )
            ],
            ratios=(0.46, 0.54),
        ),
    )

    # ===== 05 TOC + TL;DR =====
    toc_rows = [
        [P("<b>01 项目背景</b> Problem", "Body"), P("<b>05 测试与打脸</b> Testing", "Body")],
        [P("<b>02 产品目标</b> Goal", "Body"), P("<b>06 未来方向</b> Future", "Body")],
        [P("<b>03 产品方案</b> Solution", "Body"), P("<b>07 项目收获</b> Reflection", "Body")],
        [P("<b>04 MVP 路径</b> Prototype", "Body"), P("<b>08 线上 Demo</b> Try it", "Body")],
    ]
    toc = Table(toc_rows, colWidths=[CONTENT_W * 0.48] * 2)
    toc.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), SURFACE),
                ("BOX", (0, 0), (-1, -1), 0.6, LINE),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, LINE),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )
    slide(
        story,
        eyebrow("今天吃什么 · 目录"),
        P("目录 + 30 秒 TL;DR", "H2"),
        two_col(
            [toc, Spacer(1, 8), takeaway("推荐链路一复杂，就不能把「功能做完」当成验证完成。", CONTENT_W * 0.48)],
            [
                boxify(
                    [
                        P("TL;DR", "Label"),
                        P("· 问题：列表很多，决策很难<br/>· 方案：可组合成员档案 + 硬/软分层推荐<br/>· 验证：构造场景打脸假设<br/>· 收获：召回与排序目标必须对齐", "Lead"),
                    ],
                    CONTENT_W * 0.48,
                    left_bar=AMBER,
                    pad=12,
                ),
                Spacer(1, 8),
                fit_image("assets/eatwhat/05-detail-phone.jpg", CONTENT_W * 0.42, 85 * mm),
            ],
            ratios=(0.5, 0.5),
        ),
    )

    # ===== 06 Problem =====
    slide(
        story,
        eyebrow("01 · PROBLEM"),
        P("多人吃饭，为什么这么难？", "H2"),
        two_col(
            [
                P(
                    "面对「吃什么」，很多人会说「随便」，或只给出「不太能吃辣」之类的模糊范围。"
                    "多人一起时需求还可能冲突；选得不好，做决定的人容易承担额外压力。",
                    "Lead",
                ),
                P(
                    "美团、大众点评、小红书更擅长帮用户<strong>拿到餐厅列表</strong>。"
                    "用户仍要从大量候选里自行了解并做最终决定，也很难同时结合多人不同需求。",
                    "Body",
                ),
                Spacer(1, 6),
                callout(
                    "CORE QUESTION",
                    "问题不是「找不到餐厅」，而是面对大量选择时，很难快速找到一个大家都能接受的答案。",
                    CONTENT_W * 0.5,
                ),
                Spacer(1, 6),
                takeaway("找得到 ≠ 决定得了。", CONTENT_W * 0.5),
            ],
            [fit_image("assets/hero/eatwhat.jpg", CONTENT_W * 0.42, 145 * mm)],
            ratios=(0.55, 0.45),
        ),
    )

    # ===== 07 Goal =====
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
            "核心目标不是预测「最喜欢哪一家」，而是在多人、多种需求下做优先级排序与协调。"
            "相对美团 / 点评：本项目更接近平台可增加的一层<strong>决策 / 推荐能力</strong>。"
            "产品做成<strong>免登录、点开即用</strong>，降低试用成本。",
        ),
    )

    # ===== 08 Flow diagram =====
    slide(
        story,
        eyebrow("03 · SOLUTION · FLOW"),
        P("产品方案：推荐链路", "H2"),
        two_col(
            [
                P("从勾选成员到推荐，再到打分回写。旁注：每一步都在回答「谁能进来」或「谁先被推」。", "Body"),
                Spacer(1, 4),
                diagram("assets/pdf/recommend-funnel.png", CONTENT_W * 0.48, 145 * mm),
            ],
            [
                P("旁注（PDF 增补）", "Label"),
                boxify(
                    [
                        P("<b>硬过滤</b> 保证安全与可达", "Body"),
                        P("<b>排除差评</b> 避免重复踩雷", "Body"),
                        P("<b>软门控</b> 尽量满足「这次想吃」", "Body"),
                        P("<b>评分</b> 只在候选池内比高低", "Body"),
                        P("<b>回写</b> 记忆必须归属具体成员", "Body"),
                    ],
                    CONTENT_W * 0.46,
                    pad=12,
                ),
                Spacer(1, 8),
                takeaway("召回决定候选，排序决定结果——两者目标不一致会整链失效。", CONTENT_W * 0.46),
            ],
            ratios=(0.52, 0.48),
        ),
    )

    # ===== 09 Priority + design =====
    slide(
        story,
        eyebrow("03 · SOLUTION · DESIGN"),
        P("可组合档案 · 硬约束 vs 软偏好", "H2"),
        two_col(
            [
                P("<b>3.1 可组合成员档案</b>：同一个人跟不同的人吃饭，需求组合也不同。每次勾选实际成员再合并偏好、忌口与历史评分。", "Body"),
                P("<b>3.2 硬约束 vs 软偏好</b>：过敏/最大距离不能违反；「想吃火锅」尽量满足，但不一票否决其他类型。", "Body"),
                Spacer(1, 4),
                table(
                    ["因素", "层级", "行为"],
                    [
                        ["忌口 / 过敏", "硬约束", "命中即淘汰"],
                        ["最大距离", "硬约束（可放宽）", "先过滤；空则放宽"],
                        ["历史 1–2 星", "排除", "不进排序池"],
                        ["饮食偏好", "软门控", "子集或退回全候选"],
                        ["场景 / 星级 / 好评", "评分", "池内打分；同分随机"],
                        ["用餐人数", "仅展示", "测试后不再硬淘汰"],
                    ],
                    width=CONTENT_W * 0.52,
                ),
            ],
            [diagram("assets/pdf/priority-layers.png", CONTENT_W * 0.44, 148 * mm)],
            ratios=(0.54, 0.46),
        ),
    )

    # ===== 10 MVP 1 =====
    slide(
        story,
        eyebrow("04 · MVP"),
        P("三步向导，免登录即用", "H2"),
        P("选择用餐成员 → 设置场景与人数 → 设置最大距离 → 生成推荐。", "Body"),
        phones(
            [
                ("assets/eatwhat/01-members-phone.jpg", "选择用餐人档案"),
                ("assets/eatwhat/02-scene-phone.jpg", "用餐场景与人数"),
                ("assets/eatwhat/03-distance-phone.jpg", "最大距离"),
            ],
            height=114 * mm,
        ),
    )

    # ===== 11 MVP 2 =====
    slide(
        story,
        eyebrow("04 · MVP · RESULTS"),
        P("结果 · 可解释 · 操作", "H2"),
        phones(
            [
                ("assets/eatwhat/04-result-phone.jpg", "推荐结果与理由"),
                ("assets/eatwhat/05-detail-phone.jpg", "评分明细"),
                ("assets/eatwhat/06-actions.png", "打分 / 再抽 / 出发"),
            ],
            height=114 * mm,
        ),
    )

    # ===== 12 Debug =====
    slide(
        story,
        eyebrow("04 · MVP · DEBUG"),
        P("让异常结果可复盘", "H2"),
        two_col(
            [
                P("补上 Usage Log / Debug，还原「为什么推这家」。电脑端截图便于完整展示面板。", "Lead"),
                Spacer(1, 6),
                takeaway("看不见中间态，就只能靠感觉吵架。", CONTENT_W * 0.4),
            ],
            [fit_image("assets/eatwhat/06-debug.png", CONTENT_W * 0.56, 140 * mm)],
            ratios=(0.4, 0.6),
        ),
    )

    # ===== 13 Testing 1-3 =====
    slide(
        story,
        eyebrow("05 · TESTING"),
        P("测试与打脸：假设要被结果纠正", "H2"),
        P("推荐链路一复杂，就不能只靠直觉认功能「合理」。", "Body"),
        issue("01", "用餐人数不应成为硬限制", "「一人食 + 想吃火锅」时火锅店被滤掉。调整：人数改为参考信息。"),
        Spacer(1, 4),
        issue("02", "看起来周全的输入可能完全没用", "「交通方式」改了推荐却不变。调整：删掉该输入。"),
        Spacer(1, 4),
        issue("03", "记忆数据到底属于谁", "A 的五星影响了只选 B 的推荐。调整：评分严格归属成员——产品数据建模问题。"),
        Spacer(1, 6),
        takeaway("只有能改变决策结果的变量，才值得增加输入成本。"),
    )

    # ===== 14 Testing 4-5 =====
    slide(
        story,
        eyebrow("05 · TESTING · CONT."),
        P("当下需求 · 召回与排序", "H2"),
        two_col(
            [
                issue(
                    "04",
                    "当下需求应优先于历史偏好",
                    "历史爱泰国菜 vs 当前想火锅，先推了泰国菜。调整：降低历史权重，本次偏好前置到召回。",
                    "warn",
                    CONTENT_W * 0.5,
                ),
                Spacer(1, 6),
                issue(
                    "05",
                    "召回对了，排序目标仍可能错位",
                    "火锅进了池，排序仍被压过。启示：必须同时做好「谁能进来」和「进来后优先谁」。",
                    "ok",
                    CONTENT_W * 0.5,
                ),
                Spacer(1, 6),
                takeaway("召回 ≠ 排序。", CONTENT_W * 0.5),
            ],
            [
                callout(
                    "WHY MORE TESTING HERE",
                    "相对 Remember Me，本项目的逻辑中心是推荐机制，错误更隐蔽："
                    "人工场景 → 可观测日志 → 冲突场景复盘。"
                    "最深体会：用结果打脸假设，而不是把「功能做完」当成验证完成。",
                    CONTENT_W * 0.46,
                ),
                Spacer(1, 8),
                fit_image("assets/eatwhat/06-actions.png", CONTENT_W * 0.4, 95 * mm),
            ],
            ratios=(0.52, 0.48),
        ),
    )

    # ===== 15 Future =====
    slide(
        story,
        eyebrow("06 · FUTURE"),
        P("未来优化方向", "H2"),
        *panels(
            [
                (
                    "真实位置",
                    "<b>当前</b>模拟距离硬过滤。<br/><b>局限</b>多人真正在意「对大家都方不方便」。<br/><b>未来</b>多成员定位，优先中间地带。",
                ),
                (
                    "菜品级匹配",
                    "<b>当前</b>停在店级标签。<br/><b>局限</b>店适合 ≠ 每道菜适合。<br/><b>未来</b>餐厅 → 菜品 → 成员。",
                ),
                (
                    "群体满意度",
                    "<b>当前</b>偏好多影响进池。<br/><b>局限</b>最终仍可能偏一人。<br/><b>未来</b>群体满足度进排序 + 分成员反馈。",
                ),
            ],
            cols=3,
        ),
        takeaway("下一阶段重点：从「单点适配」走向「群体可接受」。"),
    )

    # ===== 16 Reflection =====
    slide(
        story,
        eyebrow("07 · REFLECTION"),
        P("项目收获", "H2"),
        *panels(
            [
                ("01", "现实里合理的因素（人数、交通），放进产品不一定该做约束；要用测试验证。"),
                ("02", "推荐不只是算分：数据归属、需求优先级、可解释性、召回与排序对齐，都是产品设计。"),
                ("03", "功能跑通 ≠ 产品闭环；核心操作在真实页面上必须可点。"),
                ("04", "翻聊天整理复盘成本很高——直接推动下一个项目从第一天写开发日志。"),
            ]
        ),
        callout("CLOSE", "一个功能看起来合理，并不代表它真的有用。只有通过使用、观察结果、再改产品，才能知道最初的想法是否成立。"),
    )

    # ===== 17 Demo eatwhat =====
    slide(
        story,
        two_col(
            [
                eyebrow("08 · DEMO"),
                P("线上体验 · 今天吃什么", "H2"),
                P("已部署到 CloudBase 静态托管。免登录，点开即可走完推荐流程。", "Lead"),
                Spacer(1, 6),
                boxify(
                    [P("<b>Demo</b>", "Label"), P("https://eatwhat-d8g01gpqk878dd6ed-1324990131.tcloudbaseapp.com", "Body")],
                    CONTENT_W * 0.48,
                    left_bar=AMBER,
                    pad=12,
                ),
                Spacer(1, 8),
                takeaway("点开即用，是能力层该有的轻入口。", CONTENT_W * 0.48),
            ],
            [
                phones(
                    [
                        ("assets/eatwhat/02-scene-phone.jpg", "场景"),
                        ("assets/eatwhat/04-result-phone.jpg", "结果"),
                    ],
                    height=118 * mm,
                )
            ],
            ratios=(0.46, 0.54),
        ),
    )

    # ===== 18 RM divider =====
    slide(
        story,
        two_col(
            [
                eyebrow("CASE 02"),
                P("Remember Me", "H1"),
                P(
                    "全家一起用的物品小本子：买了什么、放在哪、还有多久过期。"
                    "管的是家里的私密信息，因此需要登录；更接近独立 App 雏形。",
                    "Lead",
                ),
                P("<b>需登录 · 独立 App 雏形</b>　｜　2026.10　｜　PWA · CloudBase · PostgreSQL", "Body"),
                Spacer(1, 8),
                takeaway("数据敏感度决定产品形态。", CONTENT_W * 0.48),
            ],
            [
                phones(
                    [
                        ("assets/remember-me/03-login.png", "登录"),
                        ("assets/remember-me/05-items-colored.png", "清单"),
                    ],
                    height=116 * mm,
                )
            ],
            ratios=(0.48, 0.52),
        ),
    )

    # ===== 19 RM TOC =====
    rm_toc_rows = [
        [P("<b>01 项目背景</b> Problem", "Body"), P("<b>05 过程方法</b> Method", "Body")],
        [P("<b>02 产品目标</b> Goal", "Body"), P("<b>06 未来方向</b> Future", "Body")],
        [P("<b>03 产品方案</b> Solution", "Body"), P("<b>07 项目收获</b> Reflection", "Body")],
        [P("<b>04 迭代与洞察</b> Iteration", "Body"), P("<b>08 线上 Demo</b> Try it", "Body")],
    ]
    rm_toc = Table(rm_toc_rows, colWidths=[CONTENT_W * 0.48] * 2)
    rm_toc.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), SURFACE),
                ("BOX", (0, 0), (-1, -1), 0.6, LINE),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, LINE),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )
    slide(
        story,
        eyebrow("REMEMBER ME · 目录"),
        P("目录 + TL;DR", "H2"),
        two_col(
            [rm_toc, Spacer(1, 8), takeaway("私域工具：约束要写进设计，说明要写给试用的人听懂。", CONTENT_W * 0.48)],
            [
                boxify(
                    [
                        P("TL;DR", "Label"),
                        P("· 问题：找不到 / 过期 / 不共享<br/>· 方案：登录家庭空间 + 过期色标行动<br/>· 验证：自用观察为主 + 一条真机反馈<br/>· 方法：开发日志沉淀为 Skill", "Lead"),
                    ],
                    CONTENT_W * 0.48,
                    left_bar=AMBER,
                    pad=12,
                ),
                Spacer(1, 8),
                diagram("assets/pdf/login-boundary.png", CONTENT_W * 0.46, 88 * mm),
            ],
            ratios=(0.5, 0.5),
        ),
    )

    # ===== 20 Problem =====
    slide(
        story,
        eyebrow("01 · PROBLEM"),
        P("家里的东西，为什么总对不上？", "H2"),
        two_col(
            [
                P("· <b>忘了放在哪</b>：钥匙、首饰、衣物，要用时翻遍柜子。", "Lead"),
                P("· <b>过期了才发现</b>：药品、调料、护肤品只能扔掉。", "Lead"),
                P("· <b>重复购买</b>：不知道还有存货。", "Lead"),
                P("· <b>信息不共享</b>：一个人买，其他人不知道。", "Lead"),
                Spacer(1, 8),
                callout(
                    "CORE QUESTION",
                    "如何让一家人用同一份「物品小本子」，快速知道东西在哪、急不急处理，"
                    "又把家庭私密信息关在可控访问范围里？",
                    CONTENT_W * 0.5,
                ),
            ],
            [diagram("assets/pdf/login-boundary.png", CONTENT_W * 0.46, 145 * mm)],
            ratios=(0.52, 0.48),
        ),
    )

    # ===== 21 Goal =====
    slide(
        story,
        eyebrow("02 · GOAL"),
        P("产品目标与定位", "H2"),
        two_col(
            [
                P("目标用户按角色拆开，避免做成「只有采购者爱用」的记事本：", "Body"),
                table(
                    ["角色", "特点", "主要需求"],
                    [
                        ["采购者", "会主动录入", "录入要快，操作简单"],
                        ["使用者", "很少录入，偶尔查找", "能快速搜到东西在哪"],
                    ],
                    width=CONTENT_W * 0.5,
                ),
                Spacer(1, 8),
                callout(
                    "POSITIONING",
                    "相对「今天吃什么」的免登录能力层，Remember Me 更像<strong>独立 App 雏形</strong>："
                    "登录、家庭空间、云端同步、过期行动提示，都是产品本身。",
                    CONTENT_W * 0.5,
                ),
            ],
            [
                phones(
                    [
                        ("assets/remember-me/04-pick-home.png", "选家"),
                        ("assets/remember-me/02-list.png", "清单"),
                    ],
                    height=112 * mm,
                )
            ],
            ratios=(0.5, 0.5),
        ),
    )

    # ===== 22 Flow =====
    flow_steps = [
        "打开链接 → 登录（账号由我开通）",
        "一家直进清单 / 多家先选家",
        "按过期紧急度着色排序（现算）",
        "记一件 · 搜索筛选 · 切换家",
    ]
    flow_fs = [eyebrow("03 · SOLUTION · FLOW"), P("打开之后会发生什么", "H2")]
    for i, step in enumerate(flow_steps):
        flow_fs.append(boxify([P(f"<b>{i+1}. {step}</b>", "Body")], CONTENT_W * 0.48, pad=10))
        if i < len(flow_steps) - 1:
            flow_fs.append(P("<font color='#c45c26'><b>↓</b></font>", "Body"))
    slide(
        story,
        two_col(
            flow_fs,
            [
                phones(
                    [
                        ("assets/remember-me/03-login.png", "登录"),
                        ("assets/remember-me/05-items-colored.png", "着色清单"),
                    ],
                    height=118 * mm,
                )
            ],
            ratios=(0.46, 0.54),
        ),
    )

    # ===== 23 Access =====
    slide(
        story,
        eyebrow("03 · SOLUTION · ACCESS"),
        P("为什么要登录", "H2"),
        two_col(
            [
                P(
                    "「今天吃什么」可以免登录；Remember Me 记录药品位置、家用存货等<strong>家庭私域信息</strong>，"
                    "不能做成谁打开都能看的公开页。",
                    "Lead",
                ),
                *panels(
                    [
                        ("当前访问策略", "不开放网页自助注册。账号只在我这边开通——试用阶段取舍，并非漏做注册。"),
                        ("形态选择", "PWA + CloudBase：不用上架审核，一个链接分享；可加主屏幕。后端 PostgreSQL。"),
                    ],
                    cols=1,
                    width=CONTENT_W * 0.48,
                ),
                P("<b>体验账号</b> test1 / Abcd1234（非正式家人账号）", "Body"),
            ],
            [
                phones(
                    [
                        ("assets/remember-me/03-login.png", "登录页"),
                        ("assets/remember-me/04-pick-home.png", "选家页"),
                    ],
                    height=112 * mm,
                )
            ],
            ratios=(0.48, 0.52),
        ),
    )

    # ===== 24 Fields + color =====
    slide(
        story,
        eyebrow("03 · SOLUTION · COLOR"),
        P("记什么 · 过期颜色 = 行动信号", "H2"),
        P(
            "字段：名称、价格、功能、购买/过期日期、位置、备注、照片与类别。"
            "默认按「谁先过期」排——核心是「什么该先处理」。",
            "Body",
        ),
        diagram("assets/pdf/expiry-ramp.png", CONTENT_W, 72 * mm),
        Spacer(1, 4),
        phones(
            [
                ("assets/remember-me/05-items-colored.png", "清单着色"),
                ("assets/remember-me/05-expiry-colors.png", "图例"),
                ("assets/remember-me/02-list.png", "搜索 / 筛选 / 切家"),
            ],
            height=78 * mm,
        ),
    )

    # ===== 25 Iteration 1-3 =====
    slide(
        story,
        eyebrow("04 · ITERATION"),
        P("迭代与洞察（自用观察为主）", "H2"),
        P("相对推荐测试，这里更多来自自己使用中的观察。外部可复述反馈目前明确的只有一条。", "Body"),
        issue(
            "01",
            "从「我一个人用」到「全家一起用」",
            "单机本子不够：家庭共用物品常是一人买、其他人找或不知道，直到过期。定位改成全家共用。",
            "ok",
        ),
        Spacer(1, 3),
        issue(
            "02",
            "先把主路径做顺，再接云端",
            "先把录入与清单做清楚，再家庭同步。保质期快捷按钮；默认「谁先过期」。",
            "ok",
        ),
        Spacer(1, 3),
        issue(
            "03",
            "自用观察驱动改版",
            "加大触控区与类别标签，补照片与筛选；小六形象 +《4am》进门氛围，装饰不喧宾夺主。",
            "warn",
        ),
        Spacer(1, 4),
        takeaway("验证方式要匹配问题类型——不是偷懒，是阶段不同。"),
    )

    # ===== 26 Iteration 4-7 =====
    slide(
        story,
        eyebrow("04 · ITERATION · CONT."),
        P("平台约束 · 真机 · 域名", "H2"),
        issue("04", "共享落地时的平台约束", "去掉自助注册；PG 替代；从前端迁到 CloudBase，与后端同落腾讯云。"),
        Spacer(1, 3),
        issue(
            "05",
            "唯一外部反馈：按钮被挡住了",
            "音乐控件挡住保存。改底部主按钮 + 可拖音乐钮。提醒：默认设备是手机。",
            "ok",
        ),
        Spacer(1, 3),
        issue(
            "06",
            "多家切换 + 关键词搜索",
            "新家旧家都要看；东西多了单靠类别不够。支持一人多家 + 搜索叠加筛选。",
            "warn",
        ),
        Spacer(1, 3),
        issue(
            "07",
            "默认域名开着开着变成下载",
            "未备案域名策略；重传无效。短期诚实说明，根本解法是备案域名（申请中）。",
            "warn",
        ),
        Spacer(1, 4),
        takeaway("真机一条反馈，就能推翻桌面上看起来合理的布局。"),
    )

    # ===== 27 Method =====
    slide(
        story,
        eyebrow("05 · METHOD"),
        P("从翻聊天的痛苦，到开发日志 Skill", "H2"),
        two_col(
            [
                P(
                    "整理「今天吃什么」时要翻大量对话才能拼出「当时为什么」，痛苦且易漏。"
                    "做 Remember Me 起就硬约束：每完成一步，同步记录做了什么、为什么、问题、解法、反馈。"
                    "后来收成可复用 Skill。",
                    "Lead",
                ),
                Spacer(1, 8),
                callout(
                    "WHY THIS MATTERS",
                    "复杂推荐靠测试打脸假设；私域工具靠约束写进设计，并把复盘方法固定下来。",
                    CONTENT_W * 0.48,
                ),
                Spacer(1, 8),
                takeaway("过程资产本身也是作品。", CONTENT_W * 0.48),
            ],
            [diagram("assets/pdf/method-loop.png", CONTENT_W * 0.48, 145 * mm)],
            ratios=(0.5, 0.5),
        ),
    )

    # ===== 28 Future =====
    slide(
        story,
        eyebrow("06 · FUTURE"),
        P("未来优化方向", "H2"),
        *panels(
            [
                (
                    "可点户型图",
                    "<b>当前</b>文字位置 + 照片。<br/><b>局限</b>不熟布局不够直观。<br/><b>未来</b>可点平面图；家不大时后做。",
                ),
                (
                    "小六语音入口",
                    "<b>当前</b>点选打字；小六偏氛围。<br/><b>局限</b>字段多时打字贵。<br/><b>未来</b>说话完成记下/查找。",
                ),
                (
                    "备案自定义域名",
                    "<b>当前</b>默认域名可能风险页/下载。<br/><b>局限</b>说明不得不写很长。<br/><b>未来</b>备案绑定后正常分享。",
                ),
            ],
            cols=3,
        ),
        phones(
            [
                ("assets/remember-me/01-list-v02.png", "清单演进"),
                ("assets/hero/remember-me.jpg", "产品气质"),
            ],
            height=88 * mm,
        ),
    )

    # ===== 29 Reflection =====
    slide(
        story,
        eyebrow("07 · REFLECTION"),
        P("项目收获", "H2"),
        *panels(
            [
                ("01", "数据敏感度决定形态：私域要登录与家庭边界；轻试用可免登录。"),
                ("02", "平台约束会改设计：不能自助注册时，诚实改成控制台开号更好。"),
                ("03", "上线约束要写进说明：风控和打开方式、风险 Cookie 有关。"),
                ("04", "真机反馈不可替代：一条「按钮被挡住」就够。"),
                ("05", "验证强度匹配问题：推荐要结构化测试；生活工具早期可自用观察，但要写明证据边界。"),
                ("06", "过程资产也是作品：开发日志 → Skill。"),
            ],
            cols=3,
        ),
        callout("CLOSE", "把家里的私域工具做成可上线的形态，比多堆功能更重要：约束要写进设计，说明要写给试用的人听懂。"),
    )

    # ===== 30 Demo RM (last, no trailing pagebreak handling) =====
    last = [
        two_col(
            [
                eyebrow("08 · DEMO"),
                P("线上体验 · Remember Me", "H2"),
                P("请用体验账号登录（非正式家人账号）：", "Lead"),
                boxify([P("<b>test1 / Abcd1234</b>", "Lead")], CONTENT_W * 0.46, left_bar=AMBER, pad=12),
                Spacer(1, 6),
                callout(
                    "打开说明",
                    "请用系统浏览器在地址栏打开完整链接。"
                    "默认域名可能出风险提示或下载 index.html；请勿依赖主屏幕快捷方式。"
                    "备案域名申请中；重传解决不了。",
                    CONTENT_W * 0.46,
                ),
                Spacer(1, 4),
                P("https://remember-me-remember-me-d1gmd5iiu9d88c58a.webapps.tcloudbase.com", "Small"),
                P("作品集 https://ziao-huang-0108.github.io/ziao-huang.github.io/", "Small"),
                P("© 黄子骜 · Ziao Huang", "Small"),
            ],
            [
                phones(
                    [
                        ("assets/remember-me/03-login.png", "登录"),
                        ("assets/remember-me/05-items-colored.png", "清单"),
                    ],
                    height=118 * mm,
                )
            ],
            ratios=(0.48, 0.52),
        )
    ]
    story.extend(last)

    while story and isinstance(story[-1], PageBreak):
        story.pop()

    PAGE_NO["n"] = 0
    doc.build(story)
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    build()
