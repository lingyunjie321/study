from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageTemplate,
    Paragraph,
    Spacer,
)


OUT_DIR = Path(__file__).resolve().parent
OUT_PDF = OUT_DIR / "凌云杰_AI应用开发简历_企业知识问答优化版.pdf"

pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))

BLUE = colors.HexColor("#1F4D78")
LIGHT_BLUE = colors.HexColor("#2E74B5")
MUTED = colors.HexColor("#5A5A5A")
INK = colors.HexColor("#1E1E1E")
RULE = colors.HexColor("#B4C7E7")


def make_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="Name",
            fontName="STSong-Light",
            fontSize=18,
            leading=21,
            alignment=TA_CENTER,
            textColor=BLUE,
            spaceAfter=2,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Role",
            fontName="STSong-Light",
            fontSize=10.3,
            leading=12,
            alignment=TA_CENTER,
            textColor=INK,
            spaceAfter=3,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Contact",
            fontName="STSong-Light",
            fontSize=8.6,
            leading=10,
            alignment=TA_CENTER,
            textColor=MUTED,
            borderColor=RULE,
            borderWidth=0,
            borderPadding=0,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Section",
            fontName="STSong-Light",
            fontSize=11.2,
            leading=13,
            textColor=BLUE,
            spaceBefore=7,
            spaceAfter=3,
            borderColor=colors.HexColor("#D9E2F3"),
            borderWidth=0,
            borderPadding=0,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Body",
            fontName="STSong-Light",
            fontSize=8.75,
            leading=10.3,
            textColor=INK,
            spaceAfter=2.2,
            alignment=TA_LEFT,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Muted",
            parent=styles["Body"],
            fontSize=8.45,
            leading=9.8,
            textColor=MUTED,
            spaceAfter=1.5,
        )
    )
    styles.add(
        ParagraphStyle(
            name="HeaderLine",
            parent=styles["Body"],
            fontSize=9.5,
            leading=11.2,
            textColor=BLUE,
            spaceBefore=3,
            spaceAfter=1,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ResumeBullet",
            parent=styles["Body"],
            leftIndent=10,
            firstLineIndent=-7,
            bulletIndent=0,
            spaceAfter=1.4,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ResultLabel",
            parent=styles["Body"],
            fontSize=8.7,
            leading=9.7,
            textColor=BLUE,
            spaceBefore=1,
            spaceAfter=0.5,
        )
    )
    return styles


def P(text, style):
    return Paragraph(text, style)


def section(story, styles, title):
    story.append(P(f"<b>{title}</b>", styles["Section"]))
    story.append(Spacer(1, 1.5))


def bullet(story, styles, text):
    story.append(P(f"- {text}", styles["ResumeBullet"]))


def rich_line(story, styles, title, meta=None):
    if meta:
        story.append(P(f"<b>{title}</b>　<font color='#5A5A5A'><b>{meta}</b></font>", styles["HeaderLine"]))
    else:
        story.append(P(f"<b>{title}</b>", styles["HeaderLine"]))


def project(story, styles, title, meta, direction, stack, bullets, results=None):
    block = [
        P(f"<b>{title}</b>　<font color='#5A5A5A'><b>{meta}</b></font>", styles["HeaderLine"]),
        P(f"<b>项目方向：</b>{direction}", styles["Muted"]),
        P(f"<b>技术关键词：</b>{stack}", styles["Muted"]),
    ]
    for item in bullets:
        block.append(P(f"- {item}", styles["ResumeBullet"]))
    if results:
        for idx, item in enumerate(results):
            prefix = "<b>成果：</b>" if idx == 0 else ""
            block.append(P(f"- {prefix}{item}", styles["ResumeBullet"]))
    story.append(KeepTogether(block[:3]))
    story.extend(block[3:])
    story.append(Spacer(1, 1.5))


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("STSong-Light", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawCentredString(A4[0] / 2, 9 * mm, f"凌云杰 | AI 应用开发 / 算法工程师 | 第 {doc.page} 页")
    canvas.restoreState()


def build():
    styles = make_styles()
    doc = BaseDocTemplate(
        str(OUT_PDF),
        pagesize=A4,
        leftMargin=14 * mm,
        rightMargin=14 * mm,
        topMargin=12 * mm,
        bottomMargin=14 * mm,
        title="凌云杰_AI应用开发简历_企业知识问答优化版",
        author="凌云杰",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal")
    doc.addPageTemplates([PageTemplate(id="resume", frames=[frame], onPage=footer)])

    story = []

    story.append(P("<b>凌云杰</b>", styles["Name"]))
    story.append(P("<b>AI 应用开发 / 算法工程师</b>", styles["Role"]))
    story.append(P("男 | 13277855173 | yunleing1227@163.com | 5年工作经验 | 深圳 | 期望薪资：20-40K", styles["Contact"]))

    section(story, styles, "个人概要")
    for item in [
        "具备企业级 AI 应用开发、Agent 工作流、RAG 知识检索、NL2SQL、MCP 工具接入与计算机视觉落地经验，能够从业务需求、数据上下文、工程实现到服务化交付完成闭环。",
        "AI 应用经历从地产公司内部知识问答原型开始，后续在半导体企业场景中持续参与数据工程 Agent、Agentic RL 训练评估平台、芯片图像自动量测工具建设。",
        "关注企业真实使用中的可控性问题，包括知识来源引用、业务口径约束、工具权限、安全执行、结果校验、日志追踪和多入口交付。",
    ]:
        bullet(story, styles, item)

    section(story, styles, "核心技能")
    for label, value in [
        ("AI 应用 / Agent", "RAG、GraphRAG、Agent Workflow、Tool Calling、Prompt Engineering、MCP、Skills、权限治理、自动化评测"),
        ("数据智能", "NL2SQL、Schema Linking、SQLGlot、参考 SQL 注入、指标口径检索、企业数据分析助手"),
        ("工程开发", "Python、FastAPI、Pydantic、REST API、CLI、Docker、Web/TUI、服务化部署、单元测试"),
        ("存储与检索", "LanceDB、ChromaDB/FAISS、Neo4j、向量检索、文档分块、元数据过滤、增量更新"),
        ("模型与视觉", "PyTorch、verl、Ray、FSDP、vLLM、PPO/GRPO、MMSegmentation、OpenCV、语义分割、图像后处理"),
    ]:
        story.append(P(f"<font color='#1F4D78'><b>{label}：</b></font>{value}", styles["Body"]))

    section(story, styles, "工作经历")
    rich_line(story, styles, "海思半导体科技有限公司（派遣）", "算法工程师  2024.04-2026.06")
    for item in [
        "从事企业级 AI 应用开发与 AI Agent 平台研发，服务于内部数据分析、知识检索、自然语言取数、自动化工具调用及芯片图像量测等场景。",
        "参与企业数据工程 Agent 平台建设，将自然语言问题拆解为 Schema 检索、上下文注入、SQL 生成、执行校验和结果输出等环节，降低表名幻觉、字段误用和业务口径偏差。",
        "参与 Agentic RL 训练与评估平台建设，围绕多工具 Rollout、Reward 设计、模型部署和自动化评测，探索提升 Agent 多步推理、工具使用和结果校验能力。",
        "参与半导体芯片图像自动量测项目，负责语义分割模型训练、图像后处理和量测算子开发，在部分规则清晰场景中实现约 15 分钟完成 50 张图像批量量测。",
    ]:
        bullet(story, styles, item)

    rich_line(story, styles, "广西南宁冠能投资有限公司", "IT 技术支持  2021.02-2024.01")
    for item in [
        "负责 OA 办公系统日常维护、功能二次开发、问题测试与故障响应，保障营销、工程、物业、财务等部门的信息化系统稳定运行。",
        "管理公司 IT 工具、PC 设备和电子数据，搭建 IT 报修工单流程，响应全公司软硬件及系统问题咨询。",
        "长期对接业务部门信息化需求，参与处理销控房源数据不一致、工程款支付异常、业主缴费系统故障等跨部门业务卡点。",
        "2023 年下半年参与地产公司内部知识问答系统原型建设，主要承担业务资料梳理、知识入库、问题集建设、问答效果验证和部分接口联调，该项目成为本人转向 AI 应用开发的启蒙项目。",
    ]:
        bullet(story, styles, item)

    section(story, styles, "项目经历")
    project(
        story,
        styles,
        "可插拔 Agentic RL 训练与评估平台",
        "AI应用开发算法工程师 | 2025.10-2026.06",
        "Agent 强化学习、工具调用训练、训练评估闭环、行业数据构建",
        "PyTorch、verl、Ray、FSDP、vLLM、PPO/GRPO、SFT、Tool Calling、Reward",
        [
            "搭建 Agentic RL 训练链路，覆盖数据加载、SFT 冷启动、Rollout 生成、工具调用、Reward 计算、策略更新、Checkpoint 管理、模型转换和自动化评估。",
            "实现多工具交互式 Rollout 能力，支持模型在推理过程中调用搜索工具和 Python 计算工具，并将工具结果回填上下文继续生成。",
            "设计可插拔工具与任务配置接口，将搜索、计算、评估、数据处理等能力抽象为可配置组件，支持按任务替换工具、数据集和奖励规则。",
            "参与 PPO/GRPO 策略优化逻辑改造，实现可配置的 entropy-aware advantage、adaptive clipping 和动态 Rollout 分支采样逻辑。",
        ],
        ["打通 SFT、Agentic RL、多工具 Rollout、自动化评估的端到端流程，为后续迁移到半导体良率分析、设备异常排查、供应链风险分析等场景提供基础。"],
    )

    project(
        story,
        styles,
        "企业级数据工程 Agent 与 AI Harness 平台",
        "Python | 2025.01-2026.06",
        "企业数据智能、NL2SQL、RAG、Agent Runtime、MCP、工具治理",
        "Python、FastAPI、LanceDB、SQLGlot、MCP、Skills、Agent Workflow、Tool Permission",
        [
            "设计并实现基于 Workflow/Node 的 Agent 执行链路，将自然语言取数拆解为任务初始化、Schema 检索、上下文注入、SQL 生成、执行验证和结果输出。",
            "建设多源数据上下文体系，将表结构、字段说明、业务指标、参考 SQL、业务文档和外部知识统一纳入 RAG 存储，为 SQL 生成和结果解释提供可检索上下文。",
            "参与 GenSQL Agentic Node 设计，支持数据库工具、上下文检索工具、参考 SQL 工具、日期解析工具、文件工具和子 Agent 任务工具按配置加载。",
            "实现 MCP 工具生态接入和 Skills 插件化能力，将数据查询、知识检索、SQL 分析、报表分析等能力封装为可发现、可加载、可授权的技能模块。",
            "参与工具权限治理与执行安全机制，对数据库查询、文件访问、MCP 工具、技能加载和脚本调用进行白名单、人工确认、会话级授权、超时控制和敏感路径隔离。",
        ],
        [
            "打通“自然语言问题 -> 数据上下文检索 -> SQL 生成 -> 执行验证 -> 结果输出”的企业数据分析 Agent 链路。",
            "将 Agent 能力从单一问答扩展为可配置 Runtime，支持工具加载、MCP 接入、Skills 复用、权限确认、执行日志和多入口服务化交付。",
        ],
    )

    project(
        story,
        styles,
        "半导体芯片图像自动量测 AI 工具",
        "算法工程师 | 2024.05-2026.06",
        "半导体芯片量测自动化、语义分割、图像后处理、批量量测",
        "Python、PyTorch、MMSegmentation、OpenCV、语义分割、模型训练、模型推理、量测算子",
        [
            "基于业务方量测需求梳理芯片图像场景，明确目标结构、分割类别、量测点位、长度计算口径和结果输入输出格式。",
            "参与芯片图像数据集建设，包括场景划分、样本筛选、标注规范制定和标注质量检查，覆盖目标结构边界、噪声、灰度差异和典型工艺形态。",
            "基于 MMSegmentation 完成特定场景语义分割模型训练，参与训练配置、数据增强、推理效果验证和误差样本分析。",
            "开发图像后处理与量测算子，根据分割图提取目标区域、边界、中心线或关键点位，结合业务规则计算指定点位长度并转换为业务可读结果。",
            "建设模型推理与后端处理流程，支持前端上传指定场景图像后自动选择对应模型完成推理、分割图生成、量测算子执行和结果返回。",
        ],
        [
            "打通“芯片图像上传 -> 场景模型推理 -> 分割图生成 -> 量测算子计算 -> 量测结果返回”的端到端自动化量测链路。",
            "在量测规则相对清晰、图像结构不复杂的场景中，实现约 15 分钟完成 50 张图像批量量测，显著优于传统人工逐张量测流程。",
        ],
    )

    project(
        story,
        styles,
        "地产公司企业内部知识问答系统原型",
        "IT技术支持 / AI应用开发参与 | 2023.08-2024.01",
        "企业知识库问答、RAG 原型、内部制度/流程检索、AI 应用启蒙项目",
        "Python、FastAPI、LangChain、ChromaDB/FAISS、OpenAI 兼容模型、Embedding、文档解析、Prompt、HTML/JS",
        [
            "参与营销、工程、物业、财务、OA 等部门知识资料梳理，将制度文档、流程说明、合同模板、常见问题、Excel 台账等资料按部门、主题、版本和来源进行分类。",
            "协助建设文档入库流程，参与 PDF/Word/Excel/TXT 等资料的解析、文本清洗、分块、元数据标注和向量化入库，使内部资料具备可检索基础。",
            "参与 RAG 问答链路联调，围绕用户问题改写、向量召回、上下文拼接、Prompt 约束、答案来源引用和“无答案时不编造”等策略进行测试与反馈。",
            "配合业务方建设高频问题集，覆盖销控房源、工程款流程、物业缴费、OA 审批、合同模板查询等场景，用于验证问答效果和记录失败样例。",
            "参与简单 Web/API 原型联调，支持资料上传、问题输入、答案返回和来源展示，帮助业务人员以自然语言查询内部制度和流程资料。",
        ],
        [
            "打通地产公司内部知识资料从“人工问询/文件夹查找”到“自然语言检索 + 来源可追溯回答”的原型链路。",
            "项目以参与和学习为主，帮助本人建立对 RAG、Embedding、向量检索、Prompt 约束、文档入库和 AI 应用工程化的第一层实践认知，并成为后续转向 AI 应用开发的起点。",
        ],
    )

    section(story, styles, "个人优势")
    for item in [
        "AI 应用落地能力：不局限于大模型 API 调用，能够围绕企业真实业务完成 RAG、工具调用、工作流编排、服务化接入、权限治理和效果评估。",
        "Agent 工程化能力：具备 Agent Runtime、MCP、Skills、工具权限、会话状态、多入口交付等实践经验，关注 Agent 的可控性和可复用性。",
        "垂直行业迁移能力：具备地产、半导体等行业场景经验，能够将知识问答、数据分析、图像识别和自动化执行能力迁移到具体业务流程。",
        "从业务到技术的沟通能力：早期 IT 支持经历使本人熟悉跨部门需求梳理、问题定位、用户反馈收集和系统落地推进。",
    ]:
        bullet(story, styles, item)

    section(story, styles, "教育经历 / 证书")
    story.append(P("<font color='#1F4D78'><b>广西大学行健文理学院</b></font>　本科　土木工程　2016-2020", styles["Body"]))
    story.append(P("大学英语四级", styles["Body"]))

    doc.build(story)
    print(OUT_PDF)


if __name__ == "__main__":
    build()
