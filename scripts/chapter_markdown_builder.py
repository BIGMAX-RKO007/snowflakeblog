import json
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

# Helper to build Markdown chapter text
def build_chapter_md(meta, lang="zh"):
    is_zh = (lang == "zh")
    
    title = meta["title_zh"] if is_zh else meta["title_ja"]
    concept = meta["concept_zh"] if is_zh else meta["concept_ja"]
    summary_head = "【开门见山 · 技术定位】" if is_zh else "【技術ポジショニング】"
    matrix_title = f"{meta['num']}.1 全景 CRUD 能力矩阵沙盘" if is_zh else f"{meta['num']}.1 全景 CRUD 能力マトリックス"
    matrix_sub = "下表为该分类下全部核心模块的能力全景矩阵。通过 HTTP 动词直观呈现各模块的技术特征与操作权限边界。" if is_zh else "下表は本カテゴリにおける全モジュールの機能全景マトリックスです。各モジュールの HTTP メソッド対応状況および権限境界を示します。"
    
    col_no = "序号" if is_zh else "番号"
    col_mod = "模块 (Module)" if is_zh else "モジュール (Module)"
    col_desc = "官方定位与中文功能说明" if is_zh else "公式定義と日本語機能説明"
    col_scope = "核心作用域 (Scope)" if is_zh else "コアスコープ (Scope)"
    col_jump = "快速跳转" if is_zh else "クイックジャンプ"
    
    rule_title = f"{meta['num']}.2 统一技术前置规范" if is_zh else f"{meta['num']}.2 共通接続仕様と前提要件"
    rule_desc = "在调用本分类 API 之前，所有 HTTP 客户端均需遵循以下基准通信契约：" if is_zh else "本カテゴリの API を呼び出す際は、全クライアントで以下の通信契約を遵守します："
    
    detail_title = f"{meta['num']}.3 单个 API 模块五要素深度实操" if is_zh else f"{meta['num']}.3 各 API モジュール 5 要素詳細解説"
    
    chk_title = f"{meta['num']}.4 总结与工业级实践自检清单" if is_zh else f"{meta['num']}.4 実務チェックリスト"
    
    lines = []
    lines.append(f"# {title}\n")
    lines.append(f"> **{summary_head}**\n>\n> {concept}\n")
    lines.append("---\n")
    
    # Section 1: Matrix
    lines.append(f"## {matrix_title}\n")
    lines.append(f"{matrix_sub}\n")
    lines.append("<style>")
    lines.append(".crud-matrix-wrapper table {")
    lines.append("  width: 100% !important;")
    lines.append("  display: table !important;")
    lines.append("  font-size: 0.82rem;")
    lines.append("}")
    lines.append(".crud-matrix-wrapper th, .crud-matrix-wrapper td {")
    lines.append("  padding: 6px 5px !important;")
    lines.append("}")
    lines.append(".crud-matrix-wrapper td code {")
    lines.append("  font-size: 0.72rem !important;")
    lines.append("  padding: 1px 3px !important;")
    lines.append("}")
    lines.append("</style>\n")
    lines.append('<div class="crud-matrix-wrapper">\n')
    lines.append(f"| {col_no} | {col_mod} | {col_desc} | {col_scope} | GET | POST | PUT | DEL | {col_jump} |")
    lines.append("| :---: | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |")
    
    for idx, mod in enumerate(meta["modules"], start=1):
        idx_str = f"{idx:02d}"
        mod_name = mod["name"]
        mod_desc = mod["zh_desc"] if is_zh else mod["ja_desc"]
        off_desc = mod["off_desc"]
        scope = f"`{mod['scope']}`"
        m = mod["methods"]
        jump_txt = "直达" if is_zh else "直達"
        anchor = f"#{mod['anchor']}"
        lines.append(f"| **{idx_str}** | **{mod_name}** | **{mod_desc}**<br><span style=\"font-size:0.75rem;color:var(--vp-c-text-2)\">{off_desc}</span> | {scope} | {m.get('GET','❌')} | {m.get('POST','❌')} | {m.get('PUT','❌')} | {m.get('DEL','❌')} | [{jump_txt}]({anchor}) |")
        
    lines.append("\n</div>\n")
    lines.append("---\n")
    
    # Section 2: Prereqs
    lines.append(f"## {rule_title}\n")
    lines.append(f"{rule_desc}\n")
    lines.append("```txt")
    lines.append("1. Base API URL:       https://api.box.com/2.0")
    lines.append("2. 认证凭证 Header:    Authorization: Bearer <ACCESS_TOKEN>")
    lines.append("3. 内容交互 Header:    Content-Type: application/json (OAuth 表单或上传除外)")
    lines.append("4. 租户企业标识:       企业管理员上下文或 As-User: <USER_ID> 代理标头")
    lines.append("```\n")
    lines.append("---\n")
    
    # Section 3: 5-Elements per module
    lines.append(f"## {detail_title}\n")
    
    for idx, mod in enumerate(meta["modules"], start=1):
        idx_str = f"{idx:02d}"
        mod_name = mod["name"]
        anchor_id = mod["anchor"]
        lines.append(f"### <span id=\"{anchor_id}\">{idx_str}. {mod_name}</span>\n")
        
        # E1
        e1_title = "要素一：技术本质与核心能力" if is_zh else "要素1：技術的本質と中核能力"
        e1_body = mod["e1_zh"] if is_zh else mod["e1_ja"]
        lines.append(f"#### {e1_title}\n{e1_body}\n")
        
        # E2
        e2_title = "要素二：核心能力与端点拓扑字典" if is_zh else "要素2：エンドポイント定義辞書"
        lines.append(f"#### {e2_title}")
        lines.append("| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |" if is_zh else "| アクション | HTTP メソッド | URI パス | 公式仕様書 |")
        lines.append("| :--- | :---: | :--- | :--- |")
        for ep in mod["endpoints"]:
            ep_link = ep.get("link", f"https://developer.box.com/reference")
            lines.append(f"| {ep['desc']} | `{ep['method']}` | `{ep['path']}` | [Official Spec]({ep_link}) |")
        lines.append("")
        
        # E3
        e3_title = "要素三：核心请求参数与 Payload 字段拓扑" if is_zh else "要素3：主要リクエストパラメータ・ペイロード構成"
        lines.append(f"#### {e3_title}")
        lines.append("| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |" if is_zh else "| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |")
        lines.append("| :--- | :--- | :---: | :---: | :--- |")
        for p in mod["params"]:
            lines.append(f"| **{p['pos']}** | `{p['name']}` | `{p['type']}` | **{p['req']}** | {p['desc']} |")
        lines.append("")
        
        # E4
        e4_title = "要素四：尚硅谷三板斧实操 (cURL)" if is_zh else "要素4：ハンズオン実行例 (cURL)"
        lines.append(f"#### {e4_title}")
        lines.append("::: code-group")
        for ctitle, ccode in mod["curl_tabs"].items():
            lines.append(f"```bash [{ctitle}]\n{ccode}\n```\n")
        lines.append(":::\n")
        
        # E5
        e5_title = "要素五：实操暗坑与避坑指南【重点】" if is_zh else "要素5：アンチパターンと回避策"
        pitfall = mod["pitfall_zh"] if is_zh else mod["pitfall_ja"]
        lines.append(f"#### {e5_title}\n> [!CAUTION] **生产避险要点**\n> {pitfall}\n")
        lines.append("---\n")
        
    # Section 4: Self Check
    lines.append(f"## {chk_title}\n")
    check_items = meta["checklist_zh"] if is_zh else meta["checklist_ja"]
    lines.append("```txt")
    lines.append("┌──────────────────────────────────────────────────────────────┐")
    lines.append(f"│             Box API {meta['num']} 工业级集成自检清单             │")
    lines.append("├──────────────────────────────────────────────────────────────┤")
    for ci in check_items:
        lines.append(f"│ [ ] {ci}")
    lines.append("└──────────────────────────────────────────────────────────────┘")
    lines.append("```\n")
    
    return "\n".join(lines)

print("Helper functions compiled!")
