# -*- coding: utf-8 -*-
import json
import os
import sys

BASE_DIR = r"C:\Users\FX\Projects\SnowflakeBlog"

INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="{html_lang}" data-resolution="landscape">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=1920, height=1080">
    <title>{title} - FX Player</title>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <link rel="stylesheet" href="./assets/style.css">
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      body {{
        width: 1920px;
        height: 1080px;
        overflow: hidden;
        background: #0A0F1D;
        color: #F8FAFC;
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      }}
      #root {{
        position: relative;
        width: 1920px;
        height: 1080px;
        overflow: hidden;
      }}
      .clip {{
        position: absolute;
        top: 0;
        left: 0;
        width: 1920px;
        height: 1080px;
      }}
    </style>
  </head>
  <body>
    <div data-hf-id="hf-root" id="root" class="clip" data-composition-id="main" data-start="0" data-duration="{total_duration}" data-width="1920" data-height="1080">
      <!-- 4 Sub-Compositions -->
      <div data-hf-id="hf-s1" id="scene-1" class="clip" data-composition-id="scene1" data-start="{s1_start}" data-duration="{s1_dur}" data-track-index="0" data-composition-src="compositions/scene1.html"></div>
      <div data-hf-id="hf-s2" id="scene-2" class="clip" data-composition-id="scene2" data-start="{s2_start}" data-duration="{s2_dur}" data-track-index="1" data-composition-src="compositions/scene2.html"></div>
      <div data-hf-id="hf-s3" id="scene-3" class="clip" data-composition-id="scene3" data-start="{s3_start}" data-duration="{s3_dur}" data-track-index="2" data-composition-src="compositions/scene3.html"></div>
      <div data-hf-id="hf-s4" id="scene-4" class="clip" data-composition-id="scene4" data-start="{s4_start}" data-duration="{s4_dur}" data-track-index="3" data-composition-src="compositions/scene4.html"></div>

      <!-- Pure Narration Audio Soundtrack (Zero BGM) -->
      <audio data-hf-id="hf-audio-full" id="audio-full" src="audio/full_soundtrack.wav" data-start="0.0" data-duration="{total_duration}" data-volume="1"></audio>
    </div>

    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
"""

def generate_scene_html(scene_id, start, duration, header_badge, title, subtitle, tag_text, content_html, subtitle_text, lang="zh-CN"):
    fade_start = max(0.1, duration - 0.8)
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8">
  <link rel="stylesheet" href="../assets/style.css">
  <style>
    .grid-2col {{
      display: grid;
      grid-template-columns: 0.95fr 1.05fr;
      gap: 32px;
      width: 1540px;
      margin: 0 auto;
      height: 660px;
      align-content: center;
    }}
    .grid-2col-equal {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 32px;
      width: 1560px;
      margin: 0 auto;
      height: 660px;
      align-content: center;
    }}
    .grid-4col {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 22px;
      width: 1560px;
      margin: 0 auto;
      height: 660px;
      align-content: center;
    }}
    .glass-card {{
      background: rgba(15, 23, 42, 0.92);
      border: 1px solid rgba(56, 189, 248, 0.35);
      border-radius: 16px;
      padding: 24px 26px;
      box-shadow: 0 16px 36px rgba(0, 0, 0, 0.55);
      display: flex;
      flex-direction: column;
      gap: 14px;
      height: 100%;
      justify-content: space-between;
    }}
    .card-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
      padding-bottom: 10px;
    }}
    .card-title {{
      font-size: 18px;
      font-weight: 800;
      color: #FFFFFF;
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    .card-badge {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      font-weight: 700;
      padding: 3px 10px;
      border-radius: 6px;
    }}
    .info-row {{
      display: flex;
      gap: 12px;
      align-items: flex-start;
      background: rgba(255, 255, 255, 0.035);
      padding: 10px 14px;
      border-radius: 8px;
      font-size: 13px;
      color: #CBD5E1;
      line-height: 1.45;
    }}
    .info-bullet {{
      font-weight: 800;
      font-size: 14px;
      flex-shrink: 0;
    }}
    .code-box {{
      background: #050B14;
      border: 1px solid rgba(56, 189, 248, 0.3);
      border-radius: 8px;
      padding: 12px 14px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 12px;
      color: #38BDF8;
      line-height: 1.45;
      overflow-x: auto;
    }}
    .stat-badge {{
      background: rgba(56, 189, 248, 0.12);
      border: 1px solid rgba(56, 189, 248, 0.4);
      color: #38BDF8;
      padding: 2px 8px;
      border-radius: 4px;
      font-weight: 700;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
    }}
    .stat-badge-success {{
      background: rgba(52, 211, 153, 0.15);
      border: 1px solid rgba(52, 211, 153, 0.4);
      color: #34D399;
      padding: 2px 8px;
      border-radius: 4px;
      font-weight: 700;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
    }}
    .stat-badge-warn {{
      background: rgba(251, 191, 36, 0.15);
      border: 1px solid rgba(251, 191, 36, 0.4);
      color: #FBBF24;
      padding: 2px 8px;
      border-radius: 4px;
      font-weight: 700;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
    }}
    .stat-badge-error {{
      background: rgba(248, 113, 113, 0.15);
      border: 1px solid rgba(248, 113, 113, 0.4);
      color: #F87171;
      padding: 2px 8px;
      border-radius: 4px;
      font-weight: 700;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
    }}
    .flow-step-box {{
      display: flex;
      flex-direction: column;
      gap: 8px;
      background: rgba(0, 0, 0, 0.4);
      border-radius: 12px;
      padding: 12px;
      border: 1px dashed rgba(56, 189, 248, 0.3);
    }}
    .flow-node {{
      display: flex;
      align-items: center;
      gap: 12px;
      background: rgba(255, 255, 255, 0.04);
      padding: 8px 12px;
      border-radius: 8px;
      border-left: 3px solid #38BDF8;
    }}
    .flow-node-title {{
      font-weight: 800;
      font-size: 13px;
      color: #FFFFFF;
    }}
    .flow-node-desc {{
      font-size: 11.5px;
      color: #94A3B8;
    }}
    .flow-arrow {{
      text-align: center;
      color: #38BDF8;
      font-size: 12px;
      font-weight: 800;
      line-height: 1;
    }}
    .table-reconcile {{
      width: 100%;
      border-collapse: collapse;
      font-size: 12px;
    }}
    .table-reconcile th {{
      background: rgba(30, 41, 59, 0.85);
      color: #94A3B8;
      padding: 8px 10px;
      text-align: left;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
      font-weight: 700;
    }}
    .table-reconcile td {{
      padding: 8px 10px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
      color: #CBD5E1;
      font-family: 'JetBrains Mono', monospace;
    }}
    .table-reconcile tr:hover {{
      background: rgba(56, 189, 248, 0.05);
    }}
  </style>
</head>
<body>
  <div data-hf-id="hf-s-root" id="root" class="clip" data-composition-id="{scene_id}" data-start="{start}" data-duration="{duration}" data-width="1920" data-height="1080">
    <div class="tech-bg"></div>
    <div class="glow-orb glow-orb-1"></div>
    <div class="glow-orb glow-orb-2"></div>

    <!-- Header -->
    <div data-hf-id="hf-s-header" class="top-header">
      <div data-hf-id="hf-s-hl" class="header-left">
        <span data-hf-id="hf-s-badge" class="badge-chapter">{header_badge}</span>
        <div data-hf-id="hf-s-htbox" class="header-title-box">
          <h1 data-hf-id="hf-s-title">{title}</h1>
          <p data-hf-id="hf-s-sub">{subtitle}</p>
        </div>
      </div>
      <div data-hf-id="hf-s-hr" class="header-right">
        <div data-hf-id="hf-s-tag" class="system-tag">
          <div data-hf-id="hf-s-dot" class="live-dot"></div>
          <span data-hf-id="hf-s-tagtxt">{tag_text}</span>
        </div>
      </div>
    </div>

    <!-- Main Content Area -->
    <div data-hf-id="hf-s-main" class="main-stage">
      {content_html}
    </div>

    <!-- Subtitle Bar -->
    <div data-hf-id="hf-s-subbar" class="subtitle-bar" data-layout-allow-overflow>
      <span data-hf-id="hf-s-subicon" class="subtitle-icon">🎙️</span>
      <span data-hf-id="hf-s-subtxt" class="subtitle-text" data-layout-allow-overflow>{subtitle_text}</span>
    </div>
  </div>

  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo(".main-stage", {{ opacity: 0, y: 15 }}, {{ opacity: 1, y: 0, duration: 0.6 }}, 0.2);
    tl.fromTo(".glass-card, .window-frame", {{ scale: 0.96, opacity: 0 }}, {{ scale: 1.0, opacity: 1, duration: 0.5, stagger: 0.12 }}, 0.3);
    tl.to("#root", {{ opacity: 0, duration: 0.8 }}, {fade_start});
    window.__timelines["{scene_id}"] = tl;
    tl.seek(0);
  </script>
</body>
</html>
"""

# =========================================================================
# EPISODE 1: 突合体系全貌、只读审计环境初始化与第一阶梯件数突合 (Tier 0 & Tier 1)
# =========================================================================
def build_ep1_scenes(comp_dir, lang, badge_label, s1, s2, s3, s4):
    if lang == "zh":
        # S1: 5-Tier Flow + Risk Radar
        c1 = """
        <div class="grid-2col">
          <div class="glass-card">
            <div class="card-header">
              <div class="card-title">🏛️ 日本金融 IT「五阶梯严密突合体系」总览</div>
              <span class="card-badge" style="background: rgba(56, 189, 248, 0.15); color: #38BDF8; border: 1px solid rgba(56, 189, 248, 0.4);">5-TIER ARCH</span>
            </div>
            <div class="flow-step-box">
              <div class="flow-node">
                <span class="stat-badge">Tier 0</span>
                <div><div class="flow-node-title">前提审计：最小特权只读上下文</div><div class="flow-node-desc">USE ROLE MITSUI_ANALYST | 独立审计环境隔离</div></div>
              </div>
              <div class="flow-arrow">▼</div>
              <div class="flow-node">
                <span class="stat-badge-success">Tier 1</span>
                <div><div class="flow-node-title">第一阶梯：新旧表件数突合</div><div class="flow-node-desc">全量行数对齐 | CUST_MASTER 13行 / TRADE 11行 (Diff=0)</div></div>
              </div>
              <div class="flow-arrow">▼</div>
              <div class="flow-node">
                <span class="stat-badge-warn">Tier 2</span>
                <div><div class="flow-node-title">第二阶梯：金融汇总突合</div><div class="flow-node-desc">1000兆日元金额、外币与期日边界高精度聚合 (Diff=0.000)</div></div>
              </div>
              <div class="flow-arrow">▼</div>
              <div class="flow-node">
                <span class="stat-badge">Tier 3</span>
                <div><div class="flow-node-title">第三阶梯：多维与边界突合</div><div class="flow-node-desc">INNER JOIN外键完备性 / 休眠账户 / 4币种交叉 / 50全角字</div></div>
              </div>
              <div class="flow-arrow">▼</div>
              <div class="flow-node">
                <span class="stat-badge-error">Tier 4 & 5</span>
                <div><div class="flow-node-title">第四/五阶梯：密码学哈希 & WinMerge 物理直接突合</div><div class="flow-node-desc">HASH_AGG 64位指纹 + WinMerge Binary Match 证据保全</div></div>
              </div>
            </div>
          </div>
          <div class="glass-card" style="border-color: rgba(248, 113, 113, 0.45);">
            <div class="card-header">
              <div class="card-title" style="color: #F87171;">⚠️ 为什么行数相同不等于数据无损？</div>
              <span class="card-badge" style="background: rgba(248, 113, 113, 0.15); color: #F87171; border: 1px solid rgba(248, 113, 113, 0.4);">RISK RADAR</span>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #F87171;">✖</span>
              <div><strong style="color: #FFFFFF;">浮点舍入与精度截断</strong>：Oracle NUMBER 与云端浮点转换极易丢失微小分厘，导致总账严重不平。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #F87171;">✖</span>
              <div><strong style="color: #FFFFFF;">外键孤儿与关联失效</strong>：主外键约束在云端若未校验，交易可能脱节成为孤儿记录。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #F87171;">✖</span>
              <div><strong style="color: #FFFFFF;">多币种正负相抵漏洞</strong>：宏观总额一致可能掩盖美元与日元分类错位的互相对冲。</div>
            </div>
            <div class="info-row" style="background: rgba(52, 211, 153, 0.08); border-left: 3px solid #34D399;">
              <span class="info-bullet" style="color: #34D399;">✔</span>
              <div><strong style="color: #34D399;">日企合规基准</strong>：必须实施「五阶梯递进式严密突合」，层层闭环锁定生产零事故！</div>
            </div>
          </div>
        </div>
        """
        # S2: Session Setup & Least Privilege
        c2 = """
        <div class="grid-2col">
          <div class="glass-card">
            <div class="card-header">
              <div class="card-title">🔐 阶段零：只读审计会话环境初始化</div>
              <span class="card-badge stat-badge-warn">SESSION SETUP</span>
            </div>
            <div class="code-box">
-- 目的・理由: 切换至审计分析专用角色，设定只读会话上下文
USE ROLE MITSUI_ANALYST;
USE WAREHOUSE MITSUI_WH;
USE DATABASE MITSUI_SEC_DB;
USE SCHEMA RAW_ORACLE;

-- 验证当前会话上下文 (只读环境自检)
SELECT 
    CURRENT_ROLE(), 
    CURRENT_WAREHOUSE(), 
    CURRENT_DATABASE(), 
    CURRENT_SCHEMA();
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #38BDF8;">ℹ</span>
              <div><strong style="color: #FFFFFF;">执行者</strong>：<code>MITSUI_ANALYST</code> 具备对 <code>RAW_ORACLE</code> 模式下所有基表的 <code>SELECT</code> 只读权限，杜绝操作失误污染生产数据。</div>
            </div>
          </div>
          <div class="glass-card">
            <div class="card-header">
              <div class="card-title">⚖️ 金融合规红线：职责分离 (SoD) 与最小特权</div>
              <span class="card-badge stat-badge-success">AUDIT COMPLIANCE</span>
            </div>
            <table class="table-reconcile">
              <thead>
                <tr><th>检查维度</th><th>MITSUI_ENGINEER</th><th>MITSUI_ANALYST (本章)</th></tr>
              </thead>
              <tbody>
                <tr><td>职责定位</td><td>数据加载与管道维护 (ETL/ELT)</td><td><strong style="color: #34D399;">独立第三方对账与审计</strong></td></tr>
                <tr><td>数据权限</td><td>COPY INTO / WRITE 写入暂存</td><td><strong style="color: #34D399;">SELECT 严格只读</strong></td></tr>
                <tr><td>仓库挂载</td><td>MITSUI_WH (计算就绪)</td><td>MITSUI_WH (分析查询)</td></tr>
                <tr><td>合规判定</td><td>严禁自查自纠自签</td><td><strong style="color: #34D399;">合规审计标准签批主体</strong></td></tr>
              </tbody>
            </table>
            <div class="info-row" style="background: rgba(56, 189, 248, 0.08); border-left: 3px solid #38BDF8;">
              <span class="info-bullet" style="color: #38BDF8;">★</span>
              <div>在日企金融监查中，由开发运维角色直接出具突合验收报告属于重大合规缺陷，必须由独立审计角色执行核实。</div>
            </div>
          </div>
        </div>
        """
        # S3: Tier 1 Row Count SQL & Formula
        c3 = """
        <div class="grid-2col">
          <div class="glass-card">
            <div class="card-header">
              <div class="card-title">📐 第一阶梯：双端联合件数突合 SQL</div>
              <span class="card-badge stat-badge">TIER 1 QUERY</span>
            </div>
            <div class="code-box">
-- Snowflake 目标端一键双表件数突合查询
SELECT 
    'CUST_MASTER'       AS TARGET_TABLE, 
    COUNT(*)            AS TOTAL_ROWS 
FROM CUST_MASTER
UNION ALL
SELECT 
    'CUST_TRADE_DETAIL' AS TARGET_TABLE, 
    COUNT(*)            AS TOTAL_ROWS 
FROM CUST_TRADE_DETAIL;

-- 判定逻辑:
-- Δ = Snowflake_Count - Oracle_Benchmark = 0
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #34D399;">✔</span>
              <div>采用 <code>UNION ALL</code> 单次查询完成两张核心表的行数审计，减少多次往返网络延迟与元数据开销。</div>
            </div>
          </div>
          <div class="glass-card">
            <div class="card-header">
              <div class="card-title">🎯 判定标准与防范目标</div>
              <span class="card-badge stat-badge-success">ACCEPTANCE CRITERIA</span>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #38BDF8;">1</span>
              <div><strong style="color: #FFFFFF;">杜绝丢件 (Data Loss)</strong>：网络抖动、换行符误判或列数不匹配均可能导致解析跳行，差额小于 0 触发紧急告警。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #38BDF8;">2</span>
              <div><strong style="color: #FFFFFF;">杜绝重复入库 (Duplicate Ingestion)</strong>：重试机制不当或暂存区多次加载可能引发主键重复，差额大于 0 同样判定不合格。</div>
            </div>
            <div class="info-row" style="background: rgba(52, 211, 153, 0.08); border-left: 3px solid #34D399;">
              <span class="info-bullet" style="color: #34D399;">3</span>
              <div><strong style="color: #FFFFFF;">绝对零容忍标准</strong>：<br><code style="color: #34D399;">Δ = Snowflake_Count - Oracle_Benchmark == 0</code>（两表必须完全一致）</div>
            </div>
          </div>
        </div>
        """
        # S4: Real Screenshot Window Frame + Result Table
        c4 = """
        <div class="grid-2col">
          <div class="window-frame">
            <div class="window-header">
              <div class="window-dots">
                <span class="window-dot dot-red"></span>
                <span class="window-dot dot-yellow"></span>
                <span class="window-dot dot-green"></span>
              </div>
              <div class="window-title">Snowsight - Step 01: Tier 1 Row Count Verification | MITSUI_ANALYST</div>
              <div class="window-badge">QUERY COMPLETED (0.12s)</div>
            </div>
            <div class="window-body">
              <img class="window-img" src="../assets/images/05_step_01_row_count.png" alt="Tier 1 Row Count Verification Result">
            </div>
          </div>
          <div class="glass-card">
            <div class="card-header">
              <div class="card-title">✅ 第一阶梯件数突合验收判定表</div>
              <span class="card-badge stat-badge-success">TIER 1 PASS</span>
            </div>
            <table class="table-reconcile">
              <thead>
                <tr><th>检查表名</th><th>Oracle 基准</th><th>Snowflake 实测</th><th>差异值</th><th>判定</th></tr>
              </thead>
              <tbody>
                <tr>
                  <td><code>CUST_MASTER</code> (客户主表)</td>
                  <td>13 行</td>
                  <td>13 行</td>
                  <td><strong style="color: #34D399;">0</strong></td>
                  <td><span class="stat-badge-success">PASS</span></td>
                </tr>
                <tr>
                  <td><code>CUST_TRADE_DETAIL</code> (明细)</td>
                  <td>11 行</td>
                  <td>11 行</td>
                  <td><strong style="color: #34D399;">0</strong></td>
                  <td><span class="stat-badge-success">PASS</span></td>
                </tr>
              </tbody>
            </table>
            <div class="info-row" style="background: rgba(52, 211, 153, 0.08); border-left: 3px solid #34D399;">
              <span class="info-bullet" style="color: #34D399;">★</span>
              <div><strong style="color: #34D399;">第一阶梯审计结论</strong>：抽取、暂存、解析至落表全链路绝对无丢件、无重复！实机屏幕截图已归档入审计卷宗。</div>
            </div>
          </div>
        </div>
        """
    else:
        # JA scenes for EP1
        c1 = """
        <div class="grid-2col">
          <div class="glass-card">
            <div class="card-header">
              <div class="card-title">🏛️ 日本金融 IT「5階梯 厳格突合体系」全貌</div>
              <span class="card-badge" style="background: rgba(56, 189, 248, 0.15); color: #38BDF8; border: 1px solid rgba(56, 189, 248, 0.4);">5-TIER ARCH</span>
            </div>
            <div class="flow-step-box">
              <div class="flow-node">
                <span class="stat-badge">Tier 0</span>
                <div><div class="flow-node-title">前提監査：最小権限ロールセッション確定</div><div class="flow-node-desc">USE ROLE MITSUI_ANALYST | 参照専用コンテキスト分離</div></div>
              </div>
              <div class="flow-arrow">▼</div>
              <div class="flow-node">
                <span class="stat-badge-success">Tier 1</span>
                <div><div class="flow-node-title">第一階梯：新旧テーブル件数突合</div><div class="flow-node-desc">行数完全合致 | CUST_MASTER 13件 / TRADE 11件 (Diff=0)</div></div>
              </div>
              <div class="flow-arrow">▼</div>
              <div class="flow-node">
                <span class="stat-badge-warn">Tier 2</span>
                <div><div class="flow-node-title">第二階梯：金融サマリ集計突合</div><div class="flow-node-desc">1000兆円金額・外貨・約定日境界高精度集計 (Diff=0.000)</div></div>
              </div>
              <div class="flow-arrow">▼</div>
              <div class="flow-node">
                <span class="stat-badge">Tier 3</span>
                <div><div class="flow-node-title">第三階梯：多次元・リレーション境界突合</div><div class="flow-node-desc">INNER JOIN外部キー / 休眠口座 / 4通貨クロス / 全角50文字</div></div>
              </div>
              <div class="flow-arrow">▼</div>
              <div class="flow-node">
                <span class="stat-badge-error">Tier 4 & 5</span>
                <div><div class="flow-node-title">第四・五階梯：暗号ハッシュ & WinMerge 物理突合</div><div class="flow-node-desc">HASH_AGG 64ビット指紋 + WinMerge Binary Match エビデンス採取</div></div>
              </div>
            </div>
          </div>
          <div class="glass-card" style="border-color: rgba(248, 113, 113, 0.45);">
            <div class="card-header">
              <div class="card-title" style="color: #F87171;">⚠️ 件数一致だけでは不十分な金融リスク</div>
              <span class="card-badge" style="background: rgba(248, 113, 113, 0.15); color: #F87171; border: 1px solid rgba(248, 113, 113, 0.4);">RISK RADAR</span>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #F87171;">✖</span>
              <div><strong style="color: #FFFFFF;">浮動小数点の端数丸め誤差</strong>：Oracle NUMBER とクラウド浮動小数点の変換で銭単位のズレが生じる重大リスク。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #F87171;">✖</span>
              <div><strong style="color: #FFFFFF;">外部キー破綻と孤児レコード</strong>：取引データが顧客台帳から切り離され、未紐付けデータ化するリスク。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #F87171;">✖</span>
              <div><strong style="color: #FFFFFF;">複数通貨間の相殺マスキング</strong>：ドルと円の区分ズレが合計金額の相殺で隠蔽されるリスク。</div>
            </div>
            <div class="info-row" style="background: rgba(52, 211, 153, 0.08); border-left: 3px solid #34D399;">
              <span class="info-bullet" style="color: #34D399;">✔</span>
              <div><strong style="color: #34D399;">日系金融標準</strong>：「5階梯 厳格突合体系」を適用し、本番品質を完全保証します！</div>
            </div>
          </div>
        </div>
        """
        c2 = """
        <div class="grid-2col">
          <div class="glass-card">
            <div class="card-header">
              <div class="card-title">🔐 前提フェーズ：参照専用監査環境の確立</div>
              <span class="card-badge stat-badge-warn">SESSION SETUP</span>
            </div>
            <div class="code-box">
-- 目的・理由: 最小権限原則に則り、参照専用ロールへ切り替え
USE ROLE MITSUI_ANALYST;
USE WAREHOUSE MITSUI_WH;
USE DATABASE MITSUI_SEC_DB;
USE SCHEMA RAW_ORACLE;

-- セッションコンテキストの確認
SELECT 
    CURRENT_ROLE(), 
    CURRENT_WAREHOUSE(), 
    CURRENT_DATABASE(), 
    CURRENT_SCHEMA();
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #38BDF8;">ℹ</span>
              <div><strong style="color: #FFFFFF;">実行主体</strong>：<code>MITSUI_ANALYST</code> は <code>RAW_ORACLE</code> に対する厳格な <code>SELECT</code> 権限のみを保持し、事故による更新を完全遮断。</div>
            </div>
          </div>
          <div class="glass-card">
            <div class="card-header">
              <div class="card-title">⚖️ 金融コンプライアンス：職務分掌 (SoD)</div>
              <span class="card-badge stat-badge-success">AUDIT COMPLIANCE</span>
            </div>
            <table class="table-reconcile">
              <thead>
                <tr><th>評価項目</th><th>MITSUI_ENGINEER</th><th>MITSUI_ANALYST (本章)</th></tr>
              </thead>
              <tbody>
                <tr><td>職掌定義</td><td>ロード実装・パイプライン運用</td><td><strong style="color: #34D399;">独立した第三者監査・検証</strong></td></tr>
                <tr><td>データ権限</td><td>COPY INTO / 書き込み</td><td><strong style="color: #34D399;">SELECT 完全参照専用</strong></td></tr>
                <tr><td>利用WH</td><td>MITSUI_WH (ロード実行)</td><td>MITSUI_WH (突合クエリ)</td></tr>
                <tr><td>サインオフ</td><td>自己検証による承認は禁止</td><td><strong style="color: #34D399;">監査受入サインオフの主体</strong></td></tr>
              </tbody>
            </table>
            <div class="info-row" style="background: rgba(56, 189, 248, 0.08); border-left: 3px solid #38BDF8;">
              <span class="info-bullet" style="color: #38BDF8;">★</span>
              <div>金融検査において、開発・運用担当が自ら突合承認を行うことは重大な内部統制違反となります。独立ロールでの検証が必須です。</div>
            </div>
          </div>
        </div>
        """
        c3 = """
        <div class="grid-2col">
          <div class="glass-card">
            <div class="card-header">
              <div class="card-title">📐 第一階梯：新旧テーブル件数突合 SQL</div>
              <span class="card-badge stat-badge">TIER 1 QUERY</span>
            </div>
            <div class="code-box">
-- Snowflake ターゲット庫における2テーブル一括件数取得
SELECT 
    'CUST_MASTER'       AS TARGET_TABLE, 
    COUNT(*)            AS TOTAL_ROWS 
FROM CUST_MASTER
UNION ALL
SELECT 
    'CUST_TRADE_DETAIL' AS TARGET_TABLE, 
    COUNT(*)            AS TOTAL_ROWS 
FROM CUST_TRADE_DETAIL;

-- 判定基準:
-- Δ = Snowflake_Count - Oracle_Benchmark = 0
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #34D399;">✔</span>
              <div><code>UNION ALL</code> による単一クエリ実行でネットワーク往復を最小化し、原子的な件数スナップショットを取得。</div>
            </div>
          </div>
          <div class="glass-card">
            <div class="card-header">
              <div class="card-title">🎯 判定基準と品質防線</div>
              <span class="card-badge stat-badge-success">ACCEPTANCE CRITERIA</span>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #38BDF8;">1</span>
              <div><strong style="color: #FFFFFF;">データ欠落 (Data Loss) の完全排除</strong>：改行コード誤認識や列数不一致によるスキップを監視。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #38BDF8;">2</span>
              <div><strong style="color: #FFFFFF;">重複取り込み (Duplicate) の完全排除</strong>：ステージングからの多重ロードによるレコード重複を防止。</div>
            </div>
            <div class="info-row" style="background: rgba(52, 211, 153, 0.08); border-left: 3px solid #34D399;">
              <span class="info-bullet" style="color: #34D399;">3</span>
              <div><strong style="color: #FFFFFF;">絶対判定基準</strong>：<br><code style="color: #34D399;">Δ = 差異件数 == 0</code>（両テーブル完全合致が絶対条件）</div>
            </div>
          </div>
        </div>
        """
        c4 = """
        <div class="grid-2col">
          <div class="window-frame">
            <div class="window-header">
              <div class="window-dots">
                <span class="window-dot dot-red"></span>
                <span class="window-dot dot-yellow"></span>
                <span class="window-dot dot-green"></span>
              </div>
              <div class="window-title">Snowsight - Step 01: Tier 1 Row Count Verification | MITSUI_ANALYST</div>
              <div class="window-badge">QUERY COMPLETED (0.12s)</div>
            </div>
            <div class="window-body">
              <img class="window-img" src="../assets/images/05_step_01_row_count.png" alt="Tier 1 Row Count Verification Result">
            </div>
          </div>
          <div class="glass-card">
            <div class="card-header">
              <div class="card-title">✅ 第一階梯件数突合 監査判定結果</div>
              <span class="card-badge stat-badge-success">TIER 1 PASS</span>
            </div>
            <table class="table-reconcile">
              <thead>
                <tr><th>検証対象テーブル</th><th>Oracle 源泉基準</th><th>Snowflake 実測</th><th>差異件数</th><th>判定</th></tr>
              </thead>
              <tbody>
                <tr>
                  <td><code>CUST_MASTER</code> (顧客マスタ)</td>
                  <td>13 件</td>
                  <td>13 件</td>
                  <td><strong style="color: #34D399;">0</strong></td>
                  <td><span class="stat-badge-success">PASS</span></td>
                </tr>
                <tr>
                  <td><code>CUST_TRADE_DETAIL</code> (取引明细)</td>
                  <td>11 件</td>
                  <td>11 件</td>
                  <td><strong style="color: #34D399;">0</strong></td>
                  <td><span class="stat-badge-success">PASS</span></td>
                </tr>
              </tbody>
            </table>
            <div class="info-row" style="background: rgba(52, 211, 153, 0.08); border-left: 3px solid #34D399;">
              <span class="info-bullet" style="color: #34D399;">★</span>
              <div><strong style="color: #34D399;">第一階梯 監査判定</strong>：全パイプラインにおいてデータ欠落・重複ゼロが実機証明されました！実機画面エビデンスを採取・保管完了。</div>
            </div>
          </div>
        </div>
        """

    # Generate HTML files
    ep_titles = {
        "zh": ("突合体系全貌、只读审计环境初始化与第一阶梯件数突合", "异构迁移防线 · 最小特权会话 · 行数零差额验证"),
        "ja": ("突合体系全貌・読取専用監査環境の初期化と第一階梯件数突合", "異機種移行防線・最小権限セッション・件数完全合致")
    }
    t_title, t_sub = ep_titles[lang]
    scenes_data = [
        ("scene1", s1["start_time"], s1["duration"], badge_label, t_title, t_sub, "SYSTEM LIVE", c1, s1["script"]),
        ("scene2", s2["start_time"], s2["duration"], badge_label, t_title, t_sub, "TIER 0 SETUP", c2, s2["script"]),
        ("scene3", s3["start_time"], s3["duration"], badge_label, t_title, t_sub, "TIER 1 QUERY", c3, s3["script"]),
        ("scene4", s4["start_time"], s4["duration"], badge_label, t_title, t_sub, "TIER 1 VERIFIED", c4, s4["script"]),
    ]
    for sc_id, st, dur, b_lbl, tit, sub, tag, c_html, s_txt in scenes_data:
        html = generate_scene_html(sc_id, st, dur, b_lbl, tit, sub, tag, c_html, s_txt, "zh-CN" if lang == "zh" else "ja")
        with open(os.path.join(comp_dir, f"{sc_id}.html"), "w", encoding="utf-8") as f:
            f.write(html)

# =========================================================================
# EPISODE 2: 第二阶梯：千兆金额大盘与交易期日边界高精度汇总突合 (Tier 2)
# =========================================================================
def build_ep2_scenes(comp_dir, lang, badge_label, s1, s2, s3, s4):
    if lang == "zh":
        # S1: Why Count != Amount
        c1 = """
        <div class="grid-2col">
          <div class="glass-card" style="border-color: rgba(248, 113, 113, 0.45);">
            <div class="card-header">
              <div class="card-title" style="color: #F87171;">⚠️ 警钟长鸣：为什么行数相同不等于金额相同？</div>
              <span class="card-badge" style="background: rgba(248, 113, 113, 0.15); color: #F87171; border: 1px solid rgba(248, 113, 113, 0.4);">FINANCIAL TRAPS</span>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #F87171;">1</span>
              <div><strong style="color: #FFFFFF;">浮点精度舍入误差 (Rounding Error)</strong>：Oracle 与云端若使用 IEEE-754 双精度浮点（FLOAT/DOUBLE），金融小数会在加总时发生分厘微偏。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #F87171;">2</span>
              <div><strong style="color: #FFFFFF;">科学计数法变形 (Scientific Notation)</strong>：万亿级超大金额在导出或解析为 <code>1E15</code> 时，末尾有效数字被直接丢弃。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #F87171;">3</span>
              <div><strong style="color: #FFFFFF;">跨时区期日截断 (Timezone Drift)</strong>：源端 UTC+9 日期若被误判为 UTC 零时区解析，边界交易日将发生跨天偏移！</div>
            </div>
          </div>
          <div class="glass-card">
            <div class="card-header">
              <div class="card-title">🛡️ 第二阶梯：高精度大盘宏观汇总审计</div>
              <span class="card-badge stat-badge-success">TIER 2 DEFENSE</span>
            </div>
            <div class="flow-step-box">
              <div class="flow-node">
                <span class="stat-badge">成交数量</span>
                <div><div class="flow-node-title">SUM(TRADE_QTY)</div><div class="flow-node-desc">总成交股数绝对整数对齐 | 允许差额 = 0 株</div></div>
              </div>
              <div class="flow-node">
                <span class="stat-badge-success">日元金额</span>
                <div><div class="flow-node-title">ROUND(SUM(AMOUNT_JPY), 3)</div><div class="flow-node-desc">本币清算资金总盘 | 允许差额 = 0.000 円</div></div>
              </div>
              <div class="flow-node">
                <span class="stat-badge-warn">外币金额</span>
                <div><div class="flow-node-title">ROUND(SUM(NVL(AMOUNT_FCY, 0)), 3)</div><div class="flow-node-desc">外汇约定资金总盘 | 允许差额 = 0.000</div></div>
              </div>
              <div class="flow-node">
                <span class="stat-badge">期日闭合</span>
                <div><div class="flow-node-title">MIN / MAX(TRADE_DATE)</div><div class="flow-node-desc">业务期日首尾完全闭合 | 允许差额 = 0 天</div></div>
              </div>
            </div>
          </div>
        </div>
        """
        # S2: Tier 2 SQL & Tolerance
        c2 = """
        <div class="grid-2col">
          <div class="glass-card">
            <div class="card-header">
              <div class="card-title">📊 第二阶梯：金融大盘汇总审计 SQL</div>
              <span class="card-badge stat-badge">TIER 2 SQL</span>
            </div>
            <div class="code-box">
-- Snowflake 目标端执行高精度大盘汇总
SELECT 
    COUNT(*)                               AS TOTAL_TRADES,
    SUM(TRADE_QTY)                         AS TOTAL_QTY,
    ROUND(SUM(AMOUNT_JPY), 3)              AS TOTAL_AMOUNT_JPY,
    ROUND(SUM(NVL(AMOUNT_FCY, 0)), 3)      AS TOTAL_AMOUNT_FCY,
    MIN(TRADE_DATE)                        AS EARLIEST_TRADE_DATE,
    MAX(TRADE_DATE)                        AS LATEST_TRADE_DATE
FROM CUST_TRADE_DETAIL;
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #38BDF8;">ℹ</span>
              <div><code>NVL(AMOUNT_FCY, 0)</code> 确保日元原生交易的外币空值被准确转换为 0 参与加总，杜绝 SQL 聚合时的 NULL 传染。</div>
            </div>
          </div>
          <div class="glass-card">
            <div class="card-header">
              <div class="card-title">⚖️ 金融级精度判定标准</div>
              <span class="card-badge stat-badge-success">STRICT STANDARDS</span>
            </div>
            <table class="table-reconcile">
              <thead>
                <tr><th>审计核心指标</th><th>统计口径</th><th>容差范围 (Tolerance)</th></tr>
              </thead>
              <tbody>
                <tr><td>总成交笔数</td><td>COUNT(*)</td><td><strong style="color: #34D399;">0 笔 (绝对严格)</strong></td></tr>
                <tr><td>总成交股数</td><td>SUM(TRADE_QTY)</td><td><strong style="color: #34D399;">0 株 (绝对严格)</strong></td></tr>
                <tr><td>日元成交总额</td><td>SUM(AMOUNT_JPY)</td><td><strong style="color: #34D399;">0.000 円 (厘级不差)</strong></td></tr>
                <tr><td>外币成交总额</td><td>SUM(AMOUNT_FCY)</td><td><strong style="color: #34D399;">0.000 (厘级不差)</strong></td></tr>
                <tr><td>交易期日区间</td><td>MIN ~ MAX</td><td><strong style="color: #34D399;">0 天 (首尾闭合)</strong></td></tr>
              </tbody>
            </table>
          </div>
        </div>
        """
        # S3: Stress Test Analysis CU00000001
        c3 = """
        <div class="grid-2col">
          <div class="glass-card">
            <div class="card-header">
              <div class="card-title">💥 极限值压测：机构账户千兆资金</div>
              <span class="card-badge stat-badge-warn">STRESS TEST</span>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #FBBF24;">⚡</span>
              <div><strong style="color: #FFFFFF;">机构账户</strong>：<code>CU00000001</code>（三井 証券機構）</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #FBBF24;">⚡</span>
              <div><strong style="color: #FFFFFF;">单笔极端成交额</strong>：<br><code style="color: #FBBF24; font-size: 15px;">999,999,999,999,999.999</code>（接近一千万亿大关）</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #FBBF24;">⚡</span>
              <div><strong style="color: #FFFFFF;">单笔成交股数</strong>：<br><code style="color: #38BDF8; font-size: 15px;">999,999,999,999,999 株</code></div>
            </div>
            <div class="info-row" style="background: rgba(251, 191, 36, 0.08); border-left: 3px solid #FBBF24;">
              <span class="info-bullet" style="color: #FBBF24;">★</span>
              <div>许多系统在达到 15 位数字时发生科学计数法转换，导致末位被强制置零。本实战以此为极端考题！</div>
            </div>
          </div>
          <div class="glass-card">
            <div class="card-header">
              <div class="card-title">🔬 Snowflake NUMBER(38,3) 定点数护航</div>
              <span class="card-badge stat-badge-success">NUMBER(38, 3)</span>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #34D399;">✔</span>
              <div><strong style="color: #FFFFFF;">38 位绝对定点精度</strong>：Snowflake 内部将 NUMBER(38, S) 作为固定整数与比例因子存储，完全杜绝 IEEE-754 浮点误差。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #34D399;">✔</span>
              <div><strong style="color: #FFFFFF;">入库无损咬合</strong>：经过与源端 Oracle 11g 真实数据比对，千兆金额与微小交易在求和后完全一致：</div>
            </div>
            <div class="code-box" style="color: #34D399;">
日元总金额: 1,000,000,042,496,878.899 円
外币总金额: 1,000,000,000,071,000.499
成交总股数: 1,000,000,000,003,159 株
差额 = 0.000 (厘级绝对无损)
            </div>
          </div>
        </div>
        """
        # S4: Real Screenshot Window Frame + Result Table
        c4 = """
        <div class="grid-2col">
          <div class="window-frame">
            <div class="window-header">
              <div class="window-dots">
                <span class="window-dot dot-red"></span>
                <span class="window-dot dot-yellow"></span>
                <span class="window-dot dot-green"></span>
              </div>
              <div class="window-title">Snowsight - Step 02: Tier 2 Financial Aggregates & Boundaries | MITSUI_ANALYST</div>
              <div class="window-badge">QUERY COMPLETED (0.18s)</div>
            </div>
            <div class="window-body">
              <img class="window-img" src="../assets/images/05_step_02_financial_aggregates.png" alt="Tier 2 Financial Aggregates Result">
            </div>
          </div>
          <div class="glass-card">
            <div class="card-header">
              <div class="card-title">✅ 第二阶梯金融汇总突合决算表</div>
              <span class="card-badge stat-badge-success">TIER 2 PASS</span>
            </div>
            <table class="table-reconcile">
              <thead>
                <tr><th>金融审计指标</th><th>Oracle 源端基准</th><th>Snowflake 实测</th><th>差异</th><th>判定</th></tr>
              </thead>
              <tbody>
                <tr><td>总成交笔数</td><td>11 笔</td><td>11 笔</td><td>0</td><td><span class="stat-badge-success">PASS</span></td></tr>
                <tr><td>总成交股数</td><td>1,000,000,000,003,159</td><td>1,000,000,000,003,159</td><td>0</td><td><span class="stat-badge-success">PASS</span></td></tr>
                <tr><td>日元成交总额</td><td>1,000,000,042,496,878.899</td><td>1,000,000,042,496,878.899</td><td>0.000</td><td><span class="stat-badge-success">PASS</span></td></tr>
                <tr><td>外币成交总额</td><td>1,000,000,000,071,000.499</td><td>1,000,000,000,071,000.499</td><td>0.000</td><td><span class="stat-badge-success">PASS</span></td></tr>
                <tr><td>最早交易日</td><td>20241231</td><td>20241231</td><td>0</td><td><span class="stat-badge-success">PASS</span></td></tr>
                <tr><td>最晚交易日</td><td>20250401</td><td>20250401</td><td>0</td><td><span class="stat-badge-success">PASS</span></td></tr>
              </tbody>
            </table>
            <div class="info-row" style="background: rgba(52, 211, 153, 0.08); border-left: 3px solid #34D399;">
              <span class="info-bullet" style="color: #34D399;">★</span>
              <div><strong style="color: #34D399;">第二阶梯审计结论</strong>：千兆资金大盘与交易期日边界全项达成零误差，宏观金融指标 100% 验收通过！</div>
            </div>
          </div>
        </div>
        """
    else:
        # JA scenes for EP2
        c1 = """
        <div class="grid-2col">
          <div class="glass-card" style="border-color: rgba(248, 113, 113, 0.45);">
            <div class="card-header">
              <div class="card-title" style="color: #F87171;">⚠️ 件数一致 ≠ 金額一致：金融データ移行の盲点</div>
              <span class="card-badge" style="background: rgba(248, 113, 113, 0.15); color: #F87171; border: 1px solid rgba(248, 113, 113, 0.4);">FINANCIAL TRAPS</span>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #F87171;">1</span>
              <div><strong style="color: #FFFFFF;">浮動小数点丸め誤差 (Rounding Error)</strong>：IEEE-754 倍精度浮動小数点では微小な小数の累計で銭単位のズレが発生。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #F87171;">2</span>
              <div><strong style="color: #FFFFFF;">指数表記化 (Scientific Notation)</strong>：兆・京単位の超大額取引が <code>1E15</code> へ丸められ、有効桁数が切り捨てられる危険。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #F87171;">3</span>
              <div><strong style="color: #FFFFFF;">タイムゾーンによる日付ズレ</strong>：UTC+9 の日付が UTC 解釈され、約定日境界が前後日へ跨ぐリスク。</div>
            </div>
          </div>
          <div class="glass-card">
            <div class="card-header">
              <div class="card-title">🛡️ 第二階梯：高精度サマリ集計監査体系</div>
              <span class="card-badge stat-badge-success">TIER 2 DEFENSE</span>
            </div>
            <div class="flow-step-box">
              <div class="flow-node">
                <span class="stat-badge">約定数量</span>
                <div><div class="flow-node-title">SUM(TRADE_QTY)</div><div class="flow-node-desc">総約定株数の絶対整数突合 | 許容差異 = 0 株</div></div>
              </div>
              <div class="flow-node">
                <span class="stat-badge-success">邦貨金額</span>
                <div><div class="flow-node-title">ROUND(SUM(AMOUNT_JPY), 3)</div><div class="flow-node-desc">円貨決済資金総盤 | 許容差異 = 0.000 円</div></div>
              </div>
              <div class="flow-node">
                <span class="stat-badge-warn">外貨金額</span>
                <div><div class="flow-node-title">ROUND(SUM(NVL(AMOUNT_FCY, 0)), 3)</div><div class="flow-node-desc">外為約定資金総盤 | 許容差異 = 0.000</div></div>
              </div>
              <div class="flow-node">
                <span class="stat-badge">日付閉塞</span>
                <div><div class="flow-node-title">MIN / MAX(TRADE_DATE)</div><div class="flow-node-desc">約定日レンジの完全合致 | 許容差異 = 0 日</div></div>
              </div>
            </div>
          </div>
        </div>
        """
        c2 = """
        <div class="grid-2col">
          <div class="glass-card">
            <div class="card-header">
              <div class="card-title">📊 第二階梯：金融サマリ集計監査 SQL</div>
              <span class="card-badge stat-badge">TIER 2 SQL</span>
            </div>
            <div class="code-box">
-- Snowflake ターゲット庫における高精度大盤サマリ集計
SELECT 
    COUNT(*)                               AS TOTAL_TRADES,
    SUM(TRADE_QTY)                         AS TOTAL_QTY,
    ROUND(SUM(AMOUNT_JPY), 3)              AS TOTAL_AMOUNT_JPY,
    ROUND(SUM(NVL(AMOUNT_FCY, 0)), 3)      AS TOTAL_AMOUNT_FCY,
    MIN(TRADE_DATE)                        AS EARLIEST_TRADE_DATE,
    MAX(TRADE_DATE)                        AS LATEST_TRADE_DATE
FROM CUST_TRADE_DETAIL;
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #38BDF8;">ℹ</span>
              <div><code>NVL(AMOUNT_FCY, 0)</code> により、円貨固有取引の外貨NULLを安全にゼロ変換し、集計時のNULL感染を防止。</div>
            </div>
          </div>
          <div class="glass-card">
            <div class="card-header">
              <div class="card-title">⚖️ 金融級の厳格な判定基準</div>
              <span class="card-badge stat-badge-success">STRICT STANDARDS</span>
            </div>
            <table class="table-reconcile">
              <thead>
                <tr><th>監査検証指標</th><th>集計関数</th><th>許容差異基準 (Tolerance)</th></tr>
              </thead>
              <tbody>
                <tr><td>総約定件数</td><td>COUNT(*)</td><td><strong style="color: #34D399;">0 筆 (完全一致)</strong></td></tr>
                <tr><td>総約定数量</td><td>SUM(TRADE_QTY)</td><td><strong style="color: #34D399;">0 株 (完全一致)</strong></td></tr>
                <tr><td>円貨約定総額</td><td>SUM(AMOUNT_JPY)</td><td><strong style="color: #34D399;">0.000 円 (銭単位完全合致)</strong></td></tr>
                <tr><td>外貨約定総額</td><td>SUM(AMOUNT_FCY)</td><td><strong style="color: #34D399;">0.000 (完全合致)</strong></td></tr>
                <tr><td>約定日レンジ</td><td>MIN ~ MAX</td><td><strong style="color: #34D399;">0 日 (境界完全閉塞)</strong></td></tr>
              </tbody>
            </table>
          </div>
        </div>
        """
        c3 = """
        <div class="grid-2col">
          <div class="glass-card">
            <div class="card-header">
              <div class="card-title">💥 極限テスト：機関投資家の千兆円大額取引</div>
              <span class="card-badge stat-badge-warn">STRESS TEST</span>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #FBBF24;">⚡</span>
              <div><strong style="color: #FFFFFF;">対象機関口座</strong>：<code>CU00000001</code>（三井 証券機構）</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #FBBF24;">⚡</span>
              <div><strong style="color: #FFFFFF;">単筆極限約定額</strong>：<br><code style="color: #FBBF24; font-size: 15px;">999,999,999,999,999.999</code>（約1000兆円）</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #FBBF24;">⚡</span>
              <div><strong style="color: #FFFFFF;">単筆約定株数</strong>：<br><code style="color: #38BDF8; font-size: 15px;">999,999,999,999,999 株</code></div>
            </div>
            <div class="info-row" style="background: rgba(251, 191, 36, 0.08); border-left: 3px solid #FBBF24;">
              <span class="info-bullet" style="color: #FBBF24;">★</span>
              <div>15桁を超える数値は一般的な処理系で指数表記に退化し、下位桁が欠落します。本検証はこの極限ケースを網羅！</div>
            </div>
          </div>
          <div class="glass-card">
            <div class="card-header">
              <div class="card-title">🔬 Snowflake NUMBER(38,3) 固定精度の威力</div>
              <span class="card-badge stat-badge-success">NUMBER(38, 3)</span>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #34D399;">✔</span>
              <div><strong style="color: #FFFFFF;">38桁の絶対固定小数点</strong>：Snowflake 内部でスケール因子付きの完全整数として保持され、IEEE-754 誤差を根本排除。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #34D399;">✔</span>
              <div><strong style="color: #FFFFFF;">無損失格納の実証</strong>：Oracle 11g 源泉値との比較において、千兆円取引を含む全件集計が完璧に一致：</div>
            </div>
            <div class="code-box" style="color: #34D399;">
円貨総額: 1,000,000,042,496,878.899 円
外貨総額: 1,000,000,000,071,000.499
総株数:   1,000,000,000,003,159 株
差異 = 0.000 (銭単位完全一致)
            </div>
          </div>
        </div>
        """
        c4 = """
        <div class="grid-2col">
          <div class="window-frame">
            <div class="window-header">
              <div class="window-dots">
                <span class="window-dot dot-red"></span>
                <span class="window-dot dot-yellow"></span>
                <span class="window-dot dot-green"></span>
              </div>
              <div class="window-title">Snowsight - Step 02: Tier 2 Financial Aggregates & Boundaries | MITSUI_ANALYST</div>
              <div class="window-badge">QUERY COMPLETED (0.18s)</div>
            </div>
            <div class="window-body">
              <img class="window-img" src="../assets/images/05_step_02_financial_aggregates.png" alt="Tier 2 Financial Aggregates Result">
            </div>
          </div>
          <div class="glass-card">
            <div class="card-header">
              <div class="card-title">✅ 第二階梯金融集計突合 監査結果表</div>
              <span class="card-badge stat-badge-success">TIER 2 PASS</span>
            </div>
            <table class="table-reconcile">
              <thead>
                <tr><th>監査検証指標</th><th>Oracle 源泉基準</th><th>Snowflake 実測</th><th>差異</th><th>判定</th></tr>
              </thead>
              <tbody>
                <tr><td>総約定件数</td><td>11 筆</td><td>11 筆</td><td>0</td><td><span class="stat-badge-success">PASS</span></td></tr>
                <tr><td>総約定数量</td><td>1,000,000,000,003,159</td><td>1,000,000,000,003,159</td><td>0</td><td><span class="stat-badge-success">PASS</span></td></tr>
                <tr><td>邦貨総約定金額</td><td>1,000,000,042,496,878.899</td><td>1,000,000,042,496,878.899</td><td>0.000</td><td><span class="stat-badge-success">PASS</span></td></tr>
                <tr><td>外貨総約定金額</td><td>1,000,000,000,071,000.499</td><td>1,000,000,000,071,000.499</td><td>0.000</td><td><span class="stat-badge-success">PASS</span></td></tr>
                <tr><td>最早約定日</td><td>20241231</td><td>20241231</td><td>0</td><td><span class="stat-badge-success">PASS</span></td></tr>
                <tr><td>最晩約定日</td><td>20250401</td><td>20250401</td><td>0</td><td><span class="stat-badge-success">PASS</span></td></tr>
              </tbody>
            </table>
            <div class="info-row" style="background: rgba(52, 211, 153, 0.08); border-left: 3px solid #34D399;">
              <span class="info-bullet" style="color: #34D399;">★</span>
              <div><strong style="color: #34D399;">第二階梯 監査判定</strong>：千兆円規模の資金総盤および約定日境界が誤差ゼロで完全合致！第二階梯全項目パーフェクト合格！</div>
            </div>
          </div>
        </div>
        """

    ep_titles = {
        "zh": ("第二阶梯：千兆金额大盘与交易期日边界高精度汇总突合", "浮点精度防线 · 千兆大额压测 · NUMBER(38,3) 零误差"),
        "ja": ("第二階梯：千兆円金融サマリと約定日境界の高精度集計突合", "浮動小数点防線・千兆円ストレステスト・NUMBER(38,3) 誤差ゼロ")
    }
    t_title, t_sub = ep_titles[lang]
    scenes_data = [
        ("scene1", s1["start_time"], s1["duration"], badge_label, t_title, t_sub, "PRECISION RADAR", c1, s1["script"]),
        ("scene2", s2["start_time"], s2["duration"], badge_label, t_title, t_sub, "TIER 2 QUERY", c2, s2["script"]),
        ("scene3", s3["start_time"], s3["duration"], badge_label, t_title, t_sub, "STRESS ANALYSIS", c3, s3["script"]),
        ("scene4", s4["start_time"], s4["duration"], badge_label, t_title, t_sub, "TIER 2 VERIFIED", c4, s4["script"]),
    ]
    for sc_id, st, dur, b_lbl, tit, sub, tag, c_html, s_txt in scenes_data:
        html = generate_scene_html(sc_id, st, dur, b_lbl, tit, sub, tag, c_html, s_txt, "zh-CN" if lang == "zh" else "ja")
        with open(os.path.join(comp_dir, f"{sc_id}.html"), "w", encoding="utf-8") as f:
            f.write(html)

# =========================================================================
# EPISODE 3: 第三阶梯：跨表外键、休眠账户追踪与多币种全角极值突合 (Tier 3)
# =========================================================================
def build_ep3_scenes(comp_dir, lang, badge_label, s1, s2, s3, s4):
    if lang == "zh":
        # S1: Tier 3.1 INNER JOIN Screenshot + Explanations
        c1 = """
        <div class="grid-2col">
          <div class="window-frame">
            <div class="window-header">
              <div class="window-dots">
                <span class="window-dot dot-red"></span>
                <span class="window-dot dot-yellow"></span>
                <span class="window-dot dot-green"></span>
              </div>
              <div class="window-title">Snowsight - Step 03: Tier 3.1 INNER JOIN Relational Completeness | MITSUI_ANALYST</div>
              <div class="window-badge">11 TRADES MATCHED (0.15s)</div>
            </div>
            <div class="window-body">
              <img class="window-img" src="../assets/images/05_step_03_inner_join.png" alt="Tier 3.1 INNER JOIN Result">
            </div>
          </div>
          <div class="glass-card">
            <div class="card-header">
              <div class="card-title">🔗 3.1 跨表外键完备性突合 (INNER JOIN)</div>
              <span class="card-badge stat-badge-success">FOREIGN KEY PASS</span>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #34D399;">✔</span>
              <div><strong style="color: #FFFFFF;">业务防线</strong>：核实 <code>CUST_TRADE_DETAIL</code> 的每一笔交易是否都能精准挂载到合法的 <code>CUST_MASTER</code> 客户基本台账上。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #34D399;">✔</span>
              <div><strong style="color: #FFFFFF;">零孤儿记录 (0 Orphans)</strong>：实测 11 笔交易全部命中主表，汉字全角姓名与分行代码完全契合，无一笔孤儿交易。</div>
            </div>
            <div class="code-box">
SELECT t.CUST_ID, m.CUST_NAME_KANJI, m.BRANCH_CD, 
       t.TRADE_DATE, t.TRADE_QTY, t.AMOUNT_JPY
FROM CUST_TRADE_DETAIL t
INNER JOIN CUST_MASTER m ON t.CUST_ID = m.CUST_ID
ORDER BY t.CUST_ID, t.TRADE_DATE;
            </div>
            <div class="info-row" style="background: rgba(52, 211, 153, 0.08); border-left: 3px solid #34D399;">
              <span class="info-bullet" style="color: #34D399;">★</span>
              <div>跨表关联键无任何列移位，客户姓名与分行编号严密对应，第一层多维验证通过！</div>
            </div>
          </div>
        </div>
        """
        # S2: Tier 3.2 LEFT JOIN Dormant Screenshot + Explanations
        c2 = """
        <div class="grid-2col">
          <div class="window-frame">
            <div class="window-header">
              <div class="window-dots">
                <span class="window-dot dot-red"></span>
                <span class="window-dot dot-yellow"></span>
                <span class="window-dot dot-green"></span>
              </div>
              <div class="window-title">Snowsight - Step 04: Tier 3.2 LEFT JOIN Dormant Account Tracking | MITSUI_ANALYST</div>
              <div class="window-badge">2 DORMANT ACCOUNTS DETECTED</div>
            </div>
            <div class="window-body">
              <img class="window-img" src="../assets/images/05_step_04_left_join_boundary.png" alt="Tier 3.2 LEFT JOIN Dormant Accounts Result">
            </div>
          </div>
          <div class="glass-card">
            <div class="card-header">
              <div class="card-title">🔍 3.2 离群与休眠账户反向追踪 (LEFT JOIN)</div>
              <span class="card-badge stat-badge-warn">BOUNDARY AUDIT</span>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #FBBF24;">!</span>
              <div><strong style="color: #FFFFFF;">反向筛查逻辑</strong>：通过 <code>LEFT JOIN</code> 关联并在主表分组后使用 <code>HAVING COUNT(t.CUST_ID) = 0</code> 过滤无交易客户。</div>
            </div>
            <table class="table-reconcile">
              <thead>
                <tr><th>客户编号</th><th>汉字姓名</th><th>账户状态</th><th>交易笔数</th></tr>
              </thead>
              <tbody>
                <tr><td><code>CU00008888</code></td><td>松本 润</td><td><code>02</code> (休眠账户)</td><td><strong style="color: #FBBF24;">0 笔</strong></td></tr>
                <tr><td><code>CU00009990</code></td><td>井上 阳水</td><td><code>NULL</code> (空值转换)</td><td><strong style="color: #FBBF24;">0 笔</strong></td></tr>
              </tbody>
            </table>
            <div class="info-row" style="background: rgba(52, 211, 153, 0.08); border-left: 3px solid #34D399;">
              <span class="info-bullet" style="color: #34D399;">✔</span>
              <div><strong style="color: #34D399;">精准捕获目标边界</strong>：两位无交易客户完全如期检出，证明外连接聚合与边界空值处理 100% 可靠！</div>
            </div>
          </div>
        </div>
        """
        # S3: Tier 3.3 Currency Breakdown Screenshot + Matrix Table
        c3 = """
        <div class="grid-2col">
          <div class="window-frame">
            <div class="window-header">
              <div class="window-dots">
                <span class="window-dot dot-red"></span>
                <span class="window-dot dot-yellow"></span>
                <span class="window-dot dot-green"></span>
              </div>
              <div class="window-title">Snowsight - Step 05: Tier 3.3 Multi-Currency & Trade Type Matrix | MITSUI_ANALYST</div>
              <div class="window-badge">7 MATRIX GROUPS (0.14s)</div>
            </div>
            <div class="window-body">
              <img class="window-img" src="../assets/images/05_step_05_currency_breakdown.png" alt="Tier 3.3 Currency Breakdown Result">
            </div>
          </div>
          <div class="glass-card">
            <div class="card-header">
              <div class="card-title">🌐 3.3 多币种 × 买卖方向交叉切片</div>
              <span class="card-badge stat-badge-success">7 GROUPS ALIGNED</span>
            </div>
            <table class="table-reconcile">
              <thead>
                <tr><th>币种</th><th>区分</th><th>笔数</th><th>日元折算额</th><th>外币发生额</th></tr>
              </thead>
              <tbody>
                <tr><td>EUR</td><td>01(买)</td><td>1</td><td>3,200,000.000</td><td>20,000.000</td></tr>
                <tr><td>IDR</td><td>01(买)</td><td>1</td><td>1,200.000</td><td>1,000.000</td></tr>
                <tr><td>JPY</td><td>01(买)</td><td>4</td><td>21,995,678.900</td><td>0.000</td></tr>
                <tr><td>JPY</td><td>02(卖)</td><td>2</td><td>9,800,000.000</td><td>0.000</td></tr>
                <tr><td>JPY</td><td>03(失效)</td><td>1</td><td>0.000</td><td>0.000</td></tr>
                <tr><td>USD</td><td>01(买)</td><td>1</td><td>999,999,999,999,999.999</td><td>999,999,999,999,999.999</td></tr>
                <tr><td>USD</td><td>02(卖)</td><td>1</td><td>7,500,000.000</td><td>50,000.500</td></tr>
              </tbody>
            </table>
            <div class="info-row" style="background: rgba(52, 211, 153, 0.08); border-left: 3px solid #34D399;">
              <span class="info-bullet" style="color: #34D399;">★</span>
              <div>4 大币种 × 3 大交易方向 7 组矩阵分布完全一致，彻底排除正负冲抵掩盖缺陷的盲区！</div>
            </div>
          </div>
        </div>
        """
        # S4: Tier 3.4 Full-Width & NULL Validation
        c4 = """
        <div class="grid-2col">
          <div class="glass-card">
            <div class="card-header">
              <div class="card-title">🔤 3.4 日文全角 50 汉字 150 字节极值验证</div>
              <span class="card-badge stat-badge">TEXT EXTREME</span>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #38BDF8;">ℹ</span>
              <div><strong style="color: #FFFFFF;">测试对象</strong>：客户 <code>CU00004445</code> 的交易备注字段包含整整 50 个日文全角汉字。</div>
            </div>
            <div class="code-box">
SELECT 
    CUST_ID,
    LENGTH(REMARKS)       AS CHAR_LEN,
    OCTET_LENGTH(REMARKS) AS BYTE_LEN,
    REMARKS
FROM CUST_TRADE_DETAIL WHERE CUST_ID = 'CU00004445';
            </div>
            <table class="table-reconcile">
              <thead>
                <tr><th>检查项</th><th>Oracle 11g 源端</th><th>Snowflake 目标端</th><th>判定</th></tr>
              </thead>
              <tbody>
                <tr><td>字符数 (CHAR)</td><td>50 字 (LENGTH)</td><td>50 字 (LENGTH)</td><td><span class="stat-badge-success">PASS</span></td></tr>
                <tr><td>字节数 (BYTE)</td><td>150 字节 (LENGTHB)</td><td>150 字节 (OCTET_LEN)</td><td><span class="stat-badge-success">PASS</span></td></tr>
              </tbody>
            </table>
          </div>
          <div class="glass-card">
            <div class="card-header">
              <div class="card-title">🈳 Oracle 空串转标准 NULL 边界审计</div>
              <span class="card-badge stat-badge-warn">NULL STANDARDIZATION</span>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #FBBF24;">!</span>
              <div><strong style="color: #FFFFFF;">异构差异陷阱</strong>：Oracle 将 <code>''</code> 等同于 NULL，而现代数仓默认视为空字符串。</div>
            </div>
            <div class="code-box">
-- 验证 STATUS_CD 是否正确识别为原生 NULL
SELECT CUST_ID, NVL(STATUS_CD, '<<NULL_DETECTED>>')
FROM CUST_MASTER WHERE STATUS_CD IS NULL;
            </div>
            <div class="info-row" style="background: rgba(52, 211, 153, 0.08); border-left: 3px solid #34D399;">
              <span class="info-bullet" style="color: #34D399;">✔</span>
              <div><strong style="color: #34D399;">实测结果</strong>：客户 <code>CU00009990</code> 的状态字段在目标库中准确呈现为原生 <code>NULL</code>，完全遵循标准 ANSI 语义！</div>
            </div>
          </div>
        </div>
        """
    else:
        # JA scenes for EP3
        c1 = """
        <div class="grid-2col">
          <div class="window-frame">
            <div class="window-header">
              <div class="window-dots">
                <span class="window-dot dot-red"></span>
                <span class="window-dot dot-yellow"></span>
                <span class="window-dot dot-green"></span>
              </div>
              <div class="window-title">Snowsight - Step 03: Tier 3.1 INNER JOIN Relational Completeness | MITSUI_ANALYST</div>
              <div class="window-badge">11 TRADES MATCHED (0.15s)</div>
            </div>
            <div class="window-body">
              <img class="window-img" src="../assets/images/05_step_03_inner_join.png" alt="Tier 3.1 INNER JOIN Result">
            </div>
          </div>
          <div class="glass-card">
            <div class="card-header">
              <div class="card-title">🔗 3.1 外部キー参照整合性突合 (INNER JOIN)</div>
              <span class="card-badge stat-badge-success">FOREIGN KEY PASS</span>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #34D399;">✔</span>
              <div><strong style="color: #FFFFFF;">業務防線</strong>：<code>CUST_TRADE_DETAIL</code> の全約定が、正規の <code>CUST_MASTER</code> 顧客基本台帳に完全に紐付くことを証明。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #34D399;">✔</span>
              <div><strong style="color: #FFFFFF;">孤児レコードゼロ (0 Orphans)</strong>：11件すべての取引が顧客漢字名および支店コードへ完全合致し、未紐付け取引ゼロを達成！</div>
            </div>
            <div class="code-box">
SELECT t.CUST_ID, m.CUST_NAME_KANJI, m.BRANCH_CD, 
       t.TRADE_DATE, t.TRADE_QTY, t.AMOUNT_JPY
FROM CUST_TRADE_DETAIL t
INNER JOIN CUST_MASTER m ON t.CUST_ID = m.CUST_ID
ORDER BY t.CUST_ID, t.TRADE_DATE;
            </div>
            <div class="info-row" style="background: rgba(52, 211, 153, 0.08); border-left: 3px solid #34D399;">
              <span class="info-bullet" style="color: #34D399;">★</span>
              <div>テーブル間のキー結合に列ズレは一切なく、顧客属性と約定明細の整合性が完璧に立証されました。</div>
            </div>
          </div>
        </div>
        """
        c2 = """
        <div class="grid-2col">
          <div class="window-frame">
            <div class="window-header">
              <div class="window-dots">
                <span class="window-dot dot-red"></span>
                <span class="window-dot dot-yellow"></span>
                <span class="window-dot dot-green"></span>
              </div>
              <div class="window-title">Snowsight - Step 04: Tier 3.2 LEFT JOIN Dormant Account Tracking | MITSUI_ANALYST</div>
              <div class="window-badge">2 DORMANT ACCOUNTS DETECTED</div>
            </div>
            <div class="window-body">
              <img class="window-img" src="../assets/images/05_step_04_left_join_boundary.png" alt="Tier 3.2 LEFT JOIN Dormant Accounts Result">
            </div>
          </div>
          <div class="glass-card">
            <div class="card-header">
              <div class="card-title">🔍 3.2 未取引・休眠顧客の逆引き監査 (LEFT JOIN)</div>
              <span class="card-badge stat-badge-warn">BOUNDARY AUDIT</span>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #FBBF24;">!</span>
              <div><strong style="color: #FFFFFF;">逆引き監査ロジック</strong>：<code>LEFT JOIN</code> で顧客マスタを基軸とし、<code>HAVING COUNT(t.CUST_ID) = 0</code> でゼロ取引口座を完全抽出。</div>
            </div>
            <table class="table-reconcile">
              <thead>
                <tr><th>顧客番号</th><th>漢字氏名</th><th>口座ステータス</th><th>取引件数</th></tr>
              </thead>
              <tbody>
                <tr><td><code>CU00008888</code></td><td>松本 潤</td><td><code>02</code> (休眠口座)</td><td><strong style="color: #FBBF24;">0 件</strong></td></tr>
                <tr><td><code>CU00009990</code></td><td>井上 陽水</td><td><code>NULL</code> (空文字変換)</td><td><strong style="color: #FBBF24;">0 件</strong></td></tr>
              </tbody>
            </table>
            <div class="info-row" style="background: rgba(52, 211, 153, 0.08); border-left: 3px solid #34D399;">
              <span class="info-bullet" style="color: #34D399;">✔</span>
              <div><strong style="color: #34D399;">境界口座の正確な検知</strong>：取引実績のない2口座が想定通り正確に抽出され、外部結合とグループ化集計の正確性が確認されました！</div>
            </div>
          </div>
        </div>
        """
        c3 = """
        <div class="grid-2col">
          <div class="window-frame">
            <div class="window-header">
              <div class="window-dots">
                <span class="window-dot dot-red"></span>
                <span class="window-dot dot-yellow"></span>
                <span class="window-dot dot-green"></span>
              </div>
              <div class="window-title">Snowsight - Step 05: Tier 3.3 Multi-Currency & Trade Type Matrix | MITSUI_ANALYST</div>
              <div class="window-badge">7 MATRIX GROUPS (0.14s)</div>
            </div>
            <div class="window-body">
              <img class="window-img" src="../assets/images/05_step_05_currency_breakdown.png" alt="Tier 3.3 Currency Breakdown Result">
            </div>
          </div>
          <div class="glass-card">
            <div class="card-header">
              <div class="card-title">🌐 3.3 通貨別 × 売買区分 多次元クロス集計</div>
              <span class="card-badge stat-badge-success">7 GROUPS ALIGNED</span>
            </div>
            <table class="table-reconcile">
              <thead>
                <tr><th>通貨</th><th>区分</th><th>件数</th><th>円貨約定額</th><th>外貨約定額</th></tr>
              </thead>
              <tbody>
                <tr><td>EUR</td><td>01(買)</td><td>1</td><td>3,200,000.000</td><td>20,000.000</td></tr>
                <tr><td>IDR</td><td>01(買)</td><td>1</td><td>1,200.000</td><td>1,000.000</td></tr>
                <tr><td>JPY</td><td>01(买)</td><td>4</td><td>21,995,678.900</td><td>0.000</td></tr>
                <tr><td>JPY</td><td>02(売)</td><td>2</td><td>9,800,000.000</td><td>0.000</td></tr>
                <tr><td>JPY</td><td>03(失効)</td><td>1</td><td>0.000</td><td>0.000</td></tr>
                <tr><td>USD</td><td>01(買)</td><td>1</td><td>999,999,999,999,999.999</td><td>999,999,999,999,999.999</td></tr>
                <tr><td>USD</td><td>02(売)</td><td>1</td><td>7,500,000.000</td><td>50,000.500</td></tr>
              </tbody>
            </table>
            <div class="info-row" style="background: rgba(52, 211, 153, 0.08); border-left: 3px solid #34D399;">
              <span class="info-bullet" style="color: #34D399;">★</span>
              <div>4大通貨 × 3取引区分 の全7パターンが完全合致し、通貨間の相殺による不整合マスキングを完全に排除！</div>
            </div>
          </div>
        </div>
        """
        c4 = """
        <div class="grid-2col">
          <div class="glass-card">
            <div class="card-header">
              <div class="card-title">🔤 3.4 日本語全角50文字・150バイト極限値検証</div>
              <span class="card-badge stat-badge">TEXT EXTREME</span>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #38BDF8;">ℹ</span>
              <div><strong style="color: #FFFFFF;">検証対象</strong>：顧客 <code>CU00004445</code> の摘要列（全角漢字50文字＝UTF-8で150バイト）。</div>
            </div>
            <div class="code-box">
SELECT 
    CUST_ID,
    LENGTH(REMARKS)       AS CHAR_LEN,
    OCTET_LENGTH(REMARKS) AS BYTE_LEN,
    REMARKS
FROM CUST_TRADE_DETAIL WHERE CUST_ID = 'CU00004445';
            </div>
            <table class="table-reconcile">
              <thead>
                <tr><th>評価項目</th><th>Oracle 11g 源泉値</th><th>Snowflake 実測値</th><th>判定</th></tr>
              </thead>
              <tbody>
                <tr><td>文字数 (LENGTH)</td><td>50 文字</td><td>50 文字</td><td><span class="stat-badge-success">PASS</span></td></tr>
                <tr><td>バイト長 (OCTET)</td><td>150 バイト</td><td>150 バイト</td><td><span class="stat-badge-success">PASS</span></td></tr>
              </tbody>
            </table>
          </div>
          <div class="glass-card">
            <div class="card-header">
              <div class="card-title">🈳 Oracle 空文字の正規 NULL マッピング監査</div>
              <span class="card-badge stat-badge-warn">NULL STANDARDIZATION</span>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #FBBF24;">!</span>
              <div><strong style="color: #FFFFFF;">異機種仕様差異</strong>：Oracle では <code>''</code> は NULL 扱いですが、クラウドDWHでは空文字として解釈されがちです。</div>
            </div>
            <div class="code-box">
-- STATUS_CD が正規 NULL として評価されるかを検証
SELECT CUST_ID, NVL(STATUS_CD, '<<NULL_DETECTED>>')
FROM CUST_MASTER WHERE STATUS_CD IS NULL;
            </div>
            <div class="info-row" style="background: rgba(52, 211, 153, 0.08); border-left: 3px solid #34D399;">
              <span class="info-bullet" style="color: #34D399;">✔</span>
              <div><strong style="color: #34D399;">実機検証結果</strong>：顧客 <code>CU00009990</code> のステータス列が正規 <code>NULL</code> として認識され、仕様ギャップを解消しました！</div>
            </div>
          </div>
        </div>
        """

    ep_titles = {
        "zh": ("第三阶梯：跨表外键、休眠账户追踪与多币种全角极值突合", "关系完整性 · 孤儿交易清零 · 7维切片矩阵 · 50全角字"),
        "ja": ("第三階梯：外部キー整合性・休眠口座追跡と多通貨全角極限値突合", "参照整合性・孤児取引ゼロ・7多次元マトリクス・全角50文字")
    }
    t_title, t_sub = ep_titles[lang]
    scenes_data = [
        ("scene1", s1["start_time"], s1["duration"], badge_label, t_title, t_sub, "RELATIONAL INTEGRITY", c1, s1["script"]),
        ("scene2", s2["start_time"], s2["duration"], badge_label, t_title, t_sub, "DORMANT ACCOUNT AUDIT", c2, s2["script"]),
        ("scene3", s3["start_time"], s3["duration"], badge_label, t_title, t_sub, "CURRENCY MATRIX", c3, s3["script"]),
        ("scene4", s4["start_time"], s4["duration"], badge_label, t_title, t_sub, "EXTREME & NULL VERIFIED", c4, s4["script"]),
    ]
    for sc_id, st, dur, b_lbl, tit, sub, tag, c_html, s_txt in scenes_data:
        html = generate_scene_html(sc_id, st, dur, b_lbl, tit, sub, tag, c_html, s_txt, "zh-CN" if lang == "zh" else "ja")
        with open(os.path.join(comp_dir, f"{sc_id}.html"), "w", encoding="utf-8") as f:
            f.write(html)

# =========================================================================
# EPISODE 4: 第四五阶梯：密码学 HASH_AGG 指纹、WinMerge 物理直接突合与上线签发 (Tier 4 & Tier 5)
# =========================================================================
def build_ep4_scenes(comp_dir, lang, badge_label, s1, s2, s3, s4):
    if lang == "zh":
        # S1: Tier 4 Global Hash Screenshot + Avalanche Effect
        c1 = """
        <div class="grid-2col">
          <div class="window-frame">
            <div class="window-header">
              <div class="window-dots">
                <span class="window-dot dot-red"></span>
                <span class="window-dot dot-yellow"></span>
                <span class="window-dot dot-green"></span>
              </div>
              <div class="window-title">Snowsight - Step 06: Tier 4 Cryptographic Global Table Hash | MITSUI_ANALYST</div>
              <div class="window-badge">64-BIT FINGERPRINT</div>
            </div>
            <div class="window-body">
              <img class="window-img" src="../assets/images/05_step_06_global_hash.png" alt="Tier 4 Global Hash Fingerprint Result">
            </div>
          </div>
          <div class="glass-card">
            <div class="card-header">
              <div class="card-title">🔐 第四阶梯：密码学全局表哈希 (HASH_AGG)</div>
              <span class="card-badge stat-badge-success">TIER 4 PASS</span>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #38BDF8;">ℹ</span>
              <div><strong style="color: #FFFFFF;">数学防篡改证明</strong>：针对两行数据数值互换而总量不变的假象，利用 <code>HASH_AGG(HASH(...))</code> 对全量行与 10 大核心业务列计算无序哈希指纹。</div>
            </div>
            <div class="code-box">
SELECT HASH_AGG(
    HASH(
        CUST_ID, TRADE_DATE, TRADE_TYPE_CD, BRANCH_CD,
        TRADE_QTY, AMOUNT_JPY, AMOUNT_FCY, CCY_CODE,
        EXCHANGE_RATE, REMARKS
    )
) AS GLOBAL_TABLE_HASH
FROM CUST_TRADE_DETAIL;
            </div>
            <div class="info-row" style="background: rgba(56, 189, 248, 0.08); border-left: 3px solid #38BDF8;">
              <span class="info-bullet" style="color: #38BDF8;">★</span>
              <div><strong style="color: #38BDF8;">全局哈希指纹</strong>：<br><code style="font-size: 14px; color: #38BDF8;">-3405770010579799674</code>（与基准脚本严格吻合，证明比特级零篡改！）</div>
            </div>
          </div>
        </div>
        """
        # S2: Why WinMerge & Settings Guide
        c2 = """
        <div class="grid-2col">
          <div class="glass-card">
            <div class="card-header">
              <div class="card-title">🔍 为什么日企极度推崇 WinMerge 物理直接突合？</div>
              <span class="card-badge stat-badge-warn">WINMERGE EVIDENCE</span>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #38BDF8;">1</span>
              <div><strong style="color: #FFFFFF;">非技术决策层的直观可读性</strong>：向业务行员与监察法人提交时，左右分栏、纯白无黄色高亮、状态栏显示 Identical 瞬间达成共识。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #38BDF8;">2</span>
              <div><strong style="color: #FFFFFF;">物理层编码与换行符审计</strong>：底部状态栏直接检验 UTF-8 与 CRLF/LF，杜绝换行符污染或 BOM 破坏生产流水线。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #38BDF8;">3</span>
              <div><strong style="color: #FFFFFF;">固定长 CHAR 空格穿透</strong>：直观穿透审计 <code>CHAR(10)</code> 是否误删末尾补齐空格或发生截断。</div>
            </div>
          </div>
          <div class="glass-card">
            <div class="card-header">
              <div class="card-title">⚙️ 日企现场 WinMerge 比较参数推荐指南</div>
              <span class="card-badge stat-badge-success">FIELD OPTIONS</span>
            </div>
            <table class="table-reconcile">
              <thead>
                <tr><th>设置项 (Japanese UI)</th><th>推荐设定值</th><th>金融工程实战理由</th></tr>
              </thead>
              <tbody>
                <tr><td>空白 (Whitespace)</td><td><strong>すべて比較</strong></td><td>检出 CHAR 固定长补齐空格与 VARCHAR 空格</td></tr>
                <tr><td>改行コードの違いを無視</td><td><strong>チェック ON</strong></td><td>排除 Linux(LF) 与 Windows(CRLF) 伪差异</td></tr>
                <tr><td>文字コード判定</td><td><strong>UTF-8 (BOM なし)</strong></td><td>现代数仓基准，杜绝记事本自动加 BOM 破坏解析</td></tr>
                <tr><td>プラグイン (Plugins)</td><td><strong>Prediffer / CSV 表形式</strong></td><td>多字段事实表开启 CSV 自动对齐列显示模式</td></tr>
              </tbody>
            </table>
          </div>
        </div>
        """
        # S3: Dual WinMerge Screenshots (Master Binary Match + Trade Identical)
        c3 = """
        <div class="grid-2col-equal">
          <div class="window-frame">
            <div class="window-header">
              <div class="window-dots">
                <span class="window-dot dot-red"></span>
                <span class="window-dot dot-yellow"></span>
                <span class="window-dot dot-green"></span>
              </div>
              <div class="window-title">WinMerge - CUST_MASTER Binary Match</div>
              <div class="window-badge" style="color: #34D399;">BINARY MATCH</div>
            </div>
            <div class="window-body">
              <img class="window-img" src="../assets/images/05_step_06_winmerge_master_diff.png" alt="WinMerge CUST_MASTER Binary Match">
            </div>
          </div>
          <div class="window-frame">
            <div class="window-header">
              <div class="window-dots">
                <span class="window-dot dot-red"></span>
                <span class="window-dot dot-yellow"></span>
                <span class="window-dot dot-green"></span>
              </div>
              <div class="window-title">WinMerge - CUST_TRADE_DETAIL 0-Diff</div>
              <div class="window-badge" style="color: #38BDF8;">IDENTICAL</div>
            </div>
            <div class="window-body">
              <img class="window-img" src="../assets/images/05_step_05_winmerge_trade_diff.png" alt="WinMerge CUST_TRADE_DETAIL Identical">
            </div>
          </div>
        </div>
        """
        # S4: Final Sign-off Report Acceptance Table
        c4 = """
        <div class="grid-2col">
          <div class="glass-card">
            <div class="card-header">
              <div class="card-title">📜 新旧数据迁移突合检收签发报告书</div>
              <span class="card-badge stat-badge-success">GO-LIVE APPROVED</span>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #34D399;">✔</span>
              <div><strong style="color: #FFFFFF;">案件名</strong>：次世代クラウドデータ基盤 (Snowflake) 移行検証プロジェクト</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #34D399;">✔</span>
              <div><strong style="color: #FFFFFF;">验证对象</strong>：<code>CUST_MASTER</code> (客户台账), <code>CUST_TRADE_DETAIL</code> (交易明细)</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #34D399;">✔</span>
              <div><strong style="color: #FFFFFF;">验证执行者</strong>：<code>MITSUI_ANALYST</code>（只读审计分析主管）</div>
            </div>
            <div class="info-row" style="background: rgba(52, 211, 153, 0.1); border-left: 3px solid #34D399;">
              <span class="info-bullet" style="color: #34D399;">★</span>
              <div><strong style="color: #34D399;">综合判定</strong>：合格 (PASS / GO-LIVE 承認) · 物理エビデンス保全完遂！</div>
            </div>
          </div>
          <div class="glass-card">
            <div class="card-header">
              <div class="card-title">📊 五阶梯 17 项突合验收决算总表</div>
              <span class="card-badge stat-badge-success">17 / 17 ALL PASS</span>
            </div>
            <table class="table-reconcile" style="font-size: 11px;">
              <thead>
                <tr><th>阶梯</th><th>审计项目</th><th>Oracle 基准</th><th>Snowflake 实测</th><th>判定</th></tr>
              </thead>
              <tbody>
                <tr><td>Tier 1</td><td>主表总件数</td><td>13 件</td><td>13 件 (Diff 0)</td><td><span class="stat-badge-success">PASS</span></td></tr>
                <tr><td>Tier 1</td><td>明细总件数</td><td>11 件</td><td>11 件 (Diff 0)</td><td><span class="stat-badge-success">PASS</span></td></tr>
                <tr><td>Tier 2</td><td>总成交数量</td><td>1000兆股</td><td>1000兆股</td><td><span class="stat-badge-success">PASS</span></td></tr>
                <tr><td>Tier 2</td><td>日元成交总额</td><td>1000兆日元</td><td>1000兆日元 (0.000)</td><td><span class="stat-badge-success">PASS</span></td></tr>
                <tr><td>Tier 3</td><td>外键完整性</td><td>11 件 (0 孤儿)</td><td>11 件 (0 孤儿)</td><td><span class="stat-badge-success">PASS</span></td></tr>
                <tr><td>Tier 3</td><td>休眠账户逆查</td><td>2 件检出</td><td>2 件检出</td><td><span class="stat-badge-success">PASS</span></td></tr>
                <tr><td>Tier 4</td><td>全局哈希指纹</td><td>-3405770010579799674</td><td>-3405770010579799674</td><td><span class="stat-badge-success">PASS</span></td></tr>
                <tr><td>Tier 5</td><td>WinMerge 物理直接突合</td><td>Binary Match & Identical</td><td>完全同等 (0-diff)</td><td><span class="stat-badge-success">PASS</span></td></tr>
              </tbody>
            </table>
          </div>
        </div>
        """
    else:
        # JA scenes for EP4
        c1 = """
        <div class="grid-2col">
          <div class="window-frame">
            <div class="window-header">
              <div class="window-dots">
                <span class="window-dot dot-red"></span>
                <span class="window-dot dot-yellow"></span>
                <span class="window-dot dot-green"></span>
              </div>
              <div class="window-title">Snowsight - Step 06: Tier 4 Cryptographic Global Table Hash | MITSUI_ANALYST</div>
              <div class="window-badge">64-BIT FINGERPRINT</div>
            </div>
            <div class="window-body">
              <img class="window-img" src="../assets/images/05_step_06_global_hash.png" alt="Tier 4 Global Hash Fingerprint Result">
            </div>
          </div>
          <div class="glass-card">
            <div class="card-header">
              <div class="card-title">🔐 第四階梯：暗号学的テーブル全体ハッシュ突合</div>
              <span class="card-badge stat-badge-success">TIER 4 PASS</span>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #38BDF8;">ℹ</span>
              <div><strong style="color: #FFFFFF;">数学的改ざんゼロ証明</strong>：値の入れ替わりによる偶然の一致を排除するため、<code>HASH_AGG(HASH(...))</code> で全行・10主要列から無順序ハッシュ指紋を算出。</div>
            </div>
            <div class="code-box">
SELECT HASH_AGG(
    HASH(
        CUST_ID, TRADE_DATE, TRADE_TYPE_CD, BRANCH_CD,
        TRADE_QTY, AMOUNT_JPY, AMOUNT_FCY, CCY_CODE,
        EXCHANGE_RATE, REMARKS
    )
) AS GLOBAL_TABLE_HASH
FROM CUST_TRADE_DETAIL;
            </div>
            <div class="info-row" style="background: rgba(56, 189, 248, 0.08); border-left: 3px solid #38BDF8;">
              <span class="info-bullet" style="color: #38BDF8;">★</span>
              <div><strong style="color: #38BDF8;">グローバルハッシュ指紋</strong>：<br><code style="font-size: 14px; color: #38BDF8;">-3405770010579799674</code>（基準値と完全合致、ビット単位の改ざんゼロを立証！）</div>
            </div>
          </div>
        </div>
        """
        c2 = """
        <div class="grid-2col">
          <div class="glass-card">
            <div class="card-header">
              <div class="card-title">🔍 なぜ日系金融で WinMerge 物理突合が必須なのか？</div>
              <span class="card-badge stat-badge-warn">WINMERGE EVIDENCE</span>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #38BDF8;">1</span>
              <div><strong style="color: #FFFFFF;">非技術経営層への直観的説得力</strong>：左右対称の分割画面、純白で差異ハイライトなし、ステータスバーの Identical で即座に合意形成。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #38BDF8;">2</span>
              <div><strong style="color: #FFFFFF;">物理ファイル層の文字コード・改行監査</strong>：UTF-8 と CRLF/LF を画面下部で直接検証し、本番バッチ処理の破綻を未然防止。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #38BDF8;">3</span>
              <div><strong style="color: #FFFFFF;">固定長 CHAR の末尾空白透過監査</strong>：<code>CHAR(10)</code> の空白パディング削除や切り捨てを視覚的に検知可能。</div>
            </div>
          </div>
          <div class="glass-card">
            <div class="card-header">
              <div class="card-title">⚙️ 日本金融現場における WinMerge 推奨設定</div>
              <span class="card-badge stat-badge-success">FIELD OPTIONS</span>
            </div>
            <table class="table-reconcile">
              <thead>
                <tr><th>設定項目 (Japanese UI)</th><th>推奨設定値</th><th>金融現場の実戦理由</th></tr>
              </thead>
              <tbody>
                <tr><td>空白 (Whitespace)</td><td><strong>すべて比較</strong></td><td>CHAR 固定長末尾空白や VARCHAR 空白の欠落を検知</td></tr>
                <tr><td>改行コードの違いを無視</td><td><strong>チェック ON</strong></td><td>Linux(LF) と Windows(CRLF) の擬似差分を排除</td></tr>
                <tr><td>文字コード判定</td><td><strong>UTF-8 (BOM なし)</strong></td><td>クラウドDWH標準。BOM付与による解析破損を防止</td></tr>
                <tr><td>プラグイン (Plugins)</td><td><strong>Prediffer / CSV 表形式</strong></td><td>多項目ファクトテーブルのCSV列自動整列モード</td></tr>
              </tbody>
            </table>
          </div>
        </div>
        """
        c3 = """
        <div class="grid-2col-equal">
          <div class="window-frame">
            <div class="window-header">
              <div class="window-dots">
                <span class="window-dot dot-red"></span>
                <span class="window-dot dot-yellow"></span>
                <span class="window-dot dot-green"></span>
              </div>
              <div class="window-title">WinMerge - CUST_MASTER Binary Match</div>
              <div class="window-badge" style="color: #34D399;">BINARY MATCH</div>
            </div>
            <div class="window-body">
              <img class="window-img" src="../assets/images/05_step_06_winmerge_master_diff.png" alt="WinMerge CUST_MASTER Binary Match">
            </div>
          </div>
          <div class="window-frame">
            <div class="window-header">
              <div class="window-dots">
                <span class="window-dot dot-red"></span>
                <span class="window-dot dot-yellow"></span>
                <span class="window-dot dot-green"></span>
              </div>
              <div class="window-title">WinMerge - CUST_TRADE_DETAIL 0-Diff</div>
              <div class="window-badge" style="color: #38BDF8;">IDENTICAL</div>
            </div>
            <div class="window-body">
              <img class="window-img" src="../assets/images/05_step_05_winmerge_trade_diff.png" alt="WinMerge CUST_TRADE_DETAIL Identical">
            </div>
          </div>
        </div>
        """
        c4 = """
        <div class="grid-2col">
          <div class="glass-card">
            <div class="card-header">
              <div class="card-title">📜 新旧データ移行突合検収サインオフ報告書</div>
              <span class="card-badge stat-badge-success">GO-LIVE APPROVED</span>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #34D399;">✔</span>
              <div><strong style="color: #FFFFFF;">案件名</strong>：次世代クラウドデータ基盤 (Snowflake) 移行検証プロジェクト</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #34D399;">✔</span>
              <div><strong style="color: #FFFFFF;">検証対象</strong>：<code>CUST_MASTER</code> (顧客基本台帳), <code>CUST_TRADE_DETAIL</code> (顧客取引明細)</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #34D399;">✔</span>
              <div><strong style="color: #FFFFFF;">検証実行者</strong>：<code>MITSUI_ANALYST</code>（監査分析担当）</div>
            </div>
            <div class="info-row" style="background: rgba(52, 211, 153, 0.1); border-left: 3px solid #34D399;">
              <span class="info-bullet" style="color: #34D399;">★</span>
              <div><strong style="color: #34D399;">総合判定</strong>：合格 (PASS / 本番稼働 GO-LIVE 承認) · 物理エビデンス採取完遂！</div>
            </div>
          </div>
          <div class="glass-card">
            <div class="card-header">
              <div class="card-title">📊 5階梯 17項目 突合監査決算総括表</div>
              <span class="card-badge stat-badge-success">17 / 17 ALL PASS</span>
            </div>
            <table class="table-reconcile" style="font-size: 11px;">
              <thead>
                <tr><th>階梯</th><th>監査検証項目</th><th>Oracle 源泉基準</th><th>Snowflake 実測値</th><th>判定</th></tr>
              </thead>
              <tbody>
                <tr><td>Tier 1</td><td>マスタ総件数</td><td>13 件</td><td>13 件 (Diff 0)</td><td><span class="stat-badge-success">PASS</span></td></tr>
                <tr><td>Tier 1</td><td>明細総件数</td><td>11 件</td><td>11 件 (Diff 0)</td><td><span class="stat-badge-success">PASS</span></td></tr>
                <tr><td>Tier 2</td><td>総約定数量</td><td>1000兆株</td><td>1000兆株</td><td><span class="stat-badge-success">PASS</span></td></tr>
                <tr><td>Tier 2</td><td>邦貨約定総額</td><td>1000兆円</td><td>1000兆円 (0.000)</td><td><span class="stat-badge-success">PASS</span></td></tr>
                <tr><td>Tier 3</td><td>外部キー完全性</td><td>11 件 (孤児 0)</td><td>11 件 (孤児 0)</td><td><span class="stat-badge-success">PASS</span></td></tr>
                <tr><td>Tier 3</td><td>休眠口座逆引き</td><td>2 件検出</td><td>2 件検出</td><td><span class="stat-badge-success">PASS</span></td></tr>
                <tr><td>Tier 4</td><td>全体暗号ハッシュ</td><td>-3405770010579799674</td><td>-3405770010579799674</td><td><span class="stat-badge-success">PASS</span></td></tr>
                <tr><td>Tier 5</td><td>WinMerge 物理直接突合</td><td>Binary Match & Identical</td><td>完全合致 (0-diff)</td><td><span class="stat-badge-success">PASS</span></td></tr>
              </tbody>
            </table>
          </div>
        </div>
        """

    ep_titles = {
        "zh": ("第四五阶梯：密码学 HASH_AGG 指纹、WinMerge 物理直接突合与上线签发", "64位哈希防篡改 · WinMerge 二进制同构 · 17项决算全PASS"),
        "ja": ("第四五階梯：暗号学的HASH_AGG指紋・WinMerge物理直接突合と本番サインオフ", "64ビット指紋改ざんゼロ・WinMerge バイナリ完全一致・17項目全PASS")
    }
    t_title, t_sub = ep_titles[lang]
    scenes_data = [
        ("scene1", s1["start_time"], s1["duration"], badge_label, t_title, t_sub, "CRYPTOGRAPHIC HASH", c1, s1["script"]),
        ("scene2", s2["start_time"], s2["duration"], badge_label, t_title, t_sub, "PHYSICAL DIFF RATIONALE", c2, s2["script"]),
        ("scene3", s3["start_time"], s3["duration"], badge_label, t_title, t_sub, "WINMERGE EVIDENCE", c3, s3["script"]),
        ("scene4", s4["start_time"], s4["duration"], badge_label, t_title, t_sub, "SIGN-OFF ACCREDITATION", c4, s4["script"]),
    ]
    for sc_id, st, dur, b_lbl, tit, sub, tag, c_html, s_txt in scenes_data:
        html = generate_scene_html(sc_id, st, dur, b_lbl, tit, sub, tag, c_html, s_txt, "zh-CN" if lang == "zh" else "ja")
        with open(os.path.join(comp_dir, f"{sc_id}.html"), "w", encoding="utf-8") as f:
            f.write(html)

def build_all_compositions():
    episodes = [
        ("video_ch6_ep1", "zh", "Ch06 Ep01 突合体系全貌、只读审计环境初始化与第一阶梯件数突合", "CH 06 · EPISODE 01"),
        ("video_ch6_ep1_ja", "ja", "Ch06 Ep01 突合体系全貌・読取専用監査環境の初期化と第一階梯件数突合", "CH 06 · EPISODE 01"),
        ("video_ch6_ep2", "zh", "Ch06 Ep02 第二阶梯：千兆金额大盘与交易期日边界高精度汇总突合", "CH 06 · EPISODE 02"),
        ("video_ch6_ep2_ja", "ja", "Ch06 Ep02 第二階梯：千兆円金融サマリと約定日境界の高精度集計突合", "CH 06 · EPISODE 02"),
        ("video_ch6_ep3", "zh", "Ch06 Ep03 第三阶梯：跨表外键、休眠账户追踪与多币种全角极值突合", "CH 06 · EPISODE 03"),
        ("video_ch6_ep3_ja", "ja", "Ch06 Ep03 第三階梯：外部キー整合性・休眠口座追跡と多通貨全角極限値突合", "CH 06 · EPISODE 03"),
        ("video_ch6_ep4", "zh", "Ch06 Ep04 第四五阶梯：密码学 HASH_AGG 指纹、WinMerge 物理直接突合与上线签发", "CH 06 · EPISODE 04"),
        ("video_ch6_ep4_ja", "ja", "Ch06 Ep04 第四五階梯：暗号学的 HASH_AGG 指紋・WinMerge 物理直接突合と本番サインオフ", "CH 06 · EPISODE 04"),
    ]

    for dir_name, lang, title_prefix, badge_label in episodes:
        folder = os.path.join(BASE_DIR, dir_name)
        manifest_path = os.path.join(folder, "audio", "manifest.json")
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        total_dur = manifest["total_duration"]
        s1 = manifest["scene1"]
        s2 = manifest["scene2"]
        s3 = manifest["scene3"]
        s4 = manifest["scene4"]

        # 1. Update index.html
        index_content = INDEX_TEMPLATE.format(
            html_lang="zh-CN" if lang == "zh" else "ja",
            title=title_prefix,
            total_duration=total_dur,
            s1_start=s1["start_time"], s1_dur=s1["duration"],
            s2_start=s2["start_time"], s2_dur=s2["duration"],
            s3_start=s3["start_time"], s3_dur=s3["duration"],
            s4_start=s4["start_time"], s4_dur=s4["duration"],
        )
        with open(os.path.join(folder, "index.html"), "w", encoding="utf-8") as f:
            f.write(index_content)

        # 2. Write compositions
        comp_dir = os.path.join(folder, "compositions")
        os.makedirs(comp_dir, exist_ok=True)

        if "ep1" in dir_name:
            build_ep1_scenes(comp_dir, lang, badge_label, s1, s2, s3, s4)
        elif "ep2" in dir_name:
            build_ep2_scenes(comp_dir, lang, badge_label, s1, s2, s3, s4)
        elif "ep3" in dir_name:
            build_ep3_scenes(comp_dir, lang, badge_label, s1, s2, s3, s4)
        elif "ep4" in dir_name:
            build_ep4_scenes(comp_dir, lang, badge_label, s1, s2, s3, s4)

        print(f"Generated compositions for {dir_name}")

if __name__ == "__main__":
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    build_all_compositions()
    print("All Chapter 6 compositions generated successfully!")
