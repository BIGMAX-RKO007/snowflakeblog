import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("data/box_openapi_full.json", "r", encoding="utf-8") as f:
    spec = json.load(f)

# Let's inspect the tags for each of the 7 categories:
categories = {
    "08_02": {
        "title_zh": "第 08-2 讲：Box 核心 API 实战指南 —— Authentication & Users（认证与用户管理）",
        "title_ja": "第08-2講：Box コア API 実践ガイド —— Authentication & Users（認証・ユーザー管理）",
        "desc_zh": "企业级身份治理与凭证生命周期：OAuth 2.0 握手、用户/用户组自动化配置与设备准入控制",
        "desc_ja": "エンタープライズアイデンティティと認証ライフサイクル：OAuth 2.0、ユーザー・グループ自動化とデバイス制御",
        "tags": ["Authorization", "Users", "User avatars", "Groups", "Group memberships", "Invites", "Email aliases", "Session termination", "Device pinners"]
    },
    "08_03": {
        "title_zh": "第 08-3 讲：Box 核心 API 实战指南 —— Sharing & Collaboration（协同与共享管理）",
        "title_ja": "第08-3講：Box コア API 実践ガイド —— Sharing & Collaboration（共有・コラボレーション）",
        "desc_zh": "网状协作关系树与外链生命周期：跨企业协作者权限矩阵、只读/外链控制与任务流驱动",
        "desc_ja": "コラボレーション権限マトリックスと共有リンク：企業間共有、タスク管理とアクセス境界制御",
        "tags": ["Collaborations", "Collaborations (List)", "Shared links (Files)", "Shared links (Folders)", "Shared links (Web Links)", "Shared links (App Items)", "Comments", "Tasks", "Task assignments", "Domain restrictions for collaborations", "Domain restrictions (User exemptions)"]
    },
    "08_04": {
        "title_zh": "第 08-4 讲：Box 核心 API 实战指南 —— Search & Metadata（全文检索与结构化元数据）",
        "title_ja": "第08-4講：Box コア API 実践ガイド —— Search & Metadata（検索・メタデータ）",
        "desc_zh": "全文检索引擎与元数据引擎：自定义元数据模板、级联策略（Cascade Policy）与安全密级分类（Classification）",
        "desc_ja": "検索エンジンと構造化メタデータ：カスタムスキーマ、カスケードポリシーとセキュリティ分類",
        "tags": ["Search", "Metadata instances (Files)", "Metadata instances (Folders)", "Metadata templates", "Metadata cascade policies", "Metadata taxonomies", "Classifications", "Classifications on files", "Classifications on folders"]
    },
    "08_05": {
        "title_zh": "第 08-5 讲：Box 核心 API 实战指南 —— Events & Webhooks（事件审计流与网络钩子）",
        "title_ja": "第08-5講：Box コア API 実践ガイド —— Events & Webhooks（イベント監査・Webhook）",
        "desc_zh": "实时事件驱动与毫秒级推送：企业全局操作审计流（Events Stream）与 Webhook 自动化回调",
        "desc_ja": "リアルタイムイベントストリームとミリ秒通知：エンタープライズ監査ログと Webhook",
        "tags": ["Events", "Webhooks"]
    },
    "08_06": {
        "title_zh": "第 08-6 讲：Box 核心 API 实战指南 —— AI & Intelligence（大模型检索与智能代理）",
        "title_ja": "第08-6講：Box コア API 実践ガイド —— AI & Intelligence（AI・インテリジェンス）",
        "desc_zh": "智能内容理解与企业级 Agent：Box AI 问答提取、AI Studio 自定义 Agent 与 Box Skills 管道",
        "desc_ja": "スマートコンテンツ理解と AI エージェント：Box AI、AI Studio と Box Skills パイプライン",
        "tags": ["AI", "AI Studio", "Skills"]
    },
    "08_07": {
        "title_zh": "第 08-7 讲：Box 核心 API 实战指南 —— Automation & Document Workflows（流程自动化与电子签）",
        "title_ja": "第08-7講：Box コア API 実践ガイド —— Automation & Document Workflows（自動化・署名ワークフロー）",
        "desc_zh": "无纸化业务流程中枢：Box Relay 自动化流水线、Box Sign 电子签章请求与 Doc Gen 动态文档生成",
        "desc_ja": "ペーパーレス業務自動化：Box Relay、Box Sign 電子署名と Doc Gen 帳票自動生成",
        "tags": ["Workflows", "Box Sign requests", "Box Sign templates"]
    },
    "08_08": {
        "title_zh": "第 08-8 讲：Box 核心 API 实战指南 —— Administration & Compliance（安全治理与合规归档）",
        "title_ja": "第08-8講：Box コア API 実践ガイド —— Administration & Compliance（管理・ガバナンス・コンプライアンス）",
        "desc_zh": "企业级资产保全与边界防护：Retention 数据保留期策略、Legal Hold 司法冻结、Shield 信息屏障与动态水印",
        "desc_ja": "エンタープライズ資産保全と統制：リテンション保持ポリシー、リーガルホールド、Shield 情報障壁と透かし",
        "tags": ["Retention policies", "Retention policy assignments", "File version retentions", "Legal hold policies", "Legal hold policy assignments", "File version legal holds", "Shield information barriers", "Shield information barrier segments", "Shield information barrier segment members", "Shield information barrier segment restrictions", "Shield information barrier reports", "Watermarks (Files)", "Watermarks (Folders)", "Standard and Zones Storage Policies", "Terms of service", "Terms of service user statuses", "Integration mappings"]
    }
}

for cat_id, info in categories.items():
    print(f"\nCategory: {cat_id} -> {info['title_zh']}")
    total_ops = 0
    for tag in info["tags"]:
        ops = []
        for path, methods in spec["paths"].items():
            for m, op in methods.items():
                if isinstance(op, dict) and tag.lower() in [t.lower() for t in op.get("tags", [])]:
                    ops.append((m.upper(), path))
        print(f"  - {tag}: {len(ops)} endpoints")
        total_ops += len(ops)
    print(f"Total endpoints for {cat_id}: {total_ops}")
