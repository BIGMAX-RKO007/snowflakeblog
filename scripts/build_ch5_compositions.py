# -*- coding: utf-8 -*-
import json
import os

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
    /* Architecture Flow Box */
    .flow-step-box {{
      display: flex;
      flex-direction: column;
      gap: 12px;
      background: rgba(0, 0, 0, 0.4);
      border-radius: 12px;
      padding: 16px;
      border: 1px dashed rgba(56, 189, 248, 0.3);
    }}
    .flow-node {{
      display: flex;
      align-items: center;
      gap: 12px;
      background: rgba(255, 255, 255, 0.04);
      padding: 10px 14px;
      border-radius: 8px;
      border-left: 3px solid #38BDF8;
    }}
    .flow-node-title {{
      font-weight: 800;
      font-size: 13.5px;
      color: #FFFFFF;
    }}
    .flow-node-desc {{
      font-size: 12px;
      color: #94A3B8;
    }}
    .flow-arrow {{
      text-align: center;
      color: #38BDF8;
      font-size: 14px;
      font-weight: 800;
      line-height: 1;
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

def build_all_compositions():
    episodes = [
        ("video_ch5_ep1", "zh", "Ch05 Ep01 源端规范化导出、Stage暂存与客户端零成本上传", "CH 05 · EPISODE 01"),
        ("video_ch5_ep1_ja", "ja", "Ch05 Ep01 ソース側正規化エクスポート・ステージ受取とクライアントゼロコスト転送", "CH 05 · EPISODE 01"),
        ("video_ch5_ep2", "zh", "Ch05 Ep02 工程就绪、暂存清单与Stage无表投影试跑", "CH 05 · EPISODE 02"),
        ("video_ch5_ep2_ja", "ja", "Ch05 Ep02 エンジニア環境設定・ステージ一覧とテーブルレス直接射影プレビュー", "CH 05 · EPISODE 02"),
        ("video_ch5_ep3", "zh", "Ch05 Ep03 核心双表批量装载、极限值压测与入云审计追踪", "CH 05 · EPISODE 03"),
        ("video_ch5_ep3_ja", "ja", "Ch05 Ep03 コア２テーブル一括ロード・極限値テストと入雲監査追跡", "CH 05 · EPISODE 03"),
        ("video_ch5_ep4", "zh", "Ch05 Ep04 独立分析师视角：四重金融跨系统突合与全局哈希防篡改", "CH 05 · EPISODE 04"),
        ("video_ch5_ep4_ja", "ja", "Ch05 Ep04 独立アナリスト視点：四重新旧データ突合検証と全件ハッシュ防改ざん監査", "CH 05 · EPISODE 04"),
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

        print(f"Generated upgraded compositions for {dir_name}")

# =========================================================================
# EPISODE 1
# =========================================================================
def build_ep1_scenes(comp_dir, lang, badge_label, s1, s2, s3, s4):
    if lang == "zh":
        # S1: Traps + Pipeline Architecture Diagram
        c1 = """
        <div class="grid-2col">
          <div class="glass-card" style="border-color: rgba(248, 113, 113, 0.45);">
            <div class="card-header">
              <div class="card-title" style="color: #F87171;">⚠️ 异构迁移陷阱：四大源端脏数据风险</div>
              <span class="card-badge" style="background: rgba(248, 113, 113, 0.15); color: #F87171; border: 1px solid rgba(248, 113, 113, 0.4);">RISK RADAR</span>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #F87171;">✖</span>
              <div><strong style="color: #FFFFFF;">字符编码截断风险</strong>：<br>源库 JA16SJIS/ZHS16GBK 转入 Snowflake 宽字节 UTF-8 时，多字节字符极易截断或形成乱码。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #F87171;">✖</span>
              <div><strong style="color: #FFFFFF;">特殊符号与列错位</strong>：<br>金融备注中包含全角逗号、未转义双引号，致使 CSV 列解析崩溃，数据整行错位移位。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #F87171;">✖</span>
              <div><strong style="color: #FFFFFF;">空串与 NULL 异构鸿沟</strong>：<br>Oracle 底层视空串为 NULL，Snowflake 则严格区分空串与 NULL，直接引发计算逻辑与索引失效。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #F87171;">✖</span>
              <div><strong style="color: #FFFFFF;">网络带宽与存储重压</strong>：<br>明文未压缩导出动辄数百 GB，传输延迟极高，严重阻碍迁移上线窗口。</div>
            </div>
          </div>
          <div class="glass-card" style="border-color: rgba(56, 189, 248, 0.45);">
            <div class="card-header">
              <div class="card-title" style="color: #38BDF8;">🏗️ 源端规范化迁移流水线架构</div>
              <span class="card-badge" style="background: rgba(56, 189, 248, 0.15); color: #38BDF8; border: 1px solid rgba(56, 189, 248, 0.4);">ARCHITECTURE</span>
            </div>
            <div class="flow-step-box">
              <div class="flow-node" style="border-color: #F59E0B;">
                <div style="font-size: 22px;">🗄️</div>
                <div>
                  <div class="flow-node-title">Oracle 11g 核心源库</div>
                  <div class="flow-node-desc">CUST_MASTER & CUST_TRADE_DETAIL 真实生产环境表</div>
                </div>
              </div>
              <div class="flow-arrow">▼ &nbsp; 强制源头治理：UTF-8 无 BOM · 双引号包裹 · 空串转逗号 · Gzip 流式压缩</div>
              <div class="flow-node" style="border-color: #38BDF8;">
                <div style="font-size: 22px;">📦</div>
                <div>
                  <div class="flow-node-title">规范化 Gzip 导出资产包</div>
                  <div class="flow-node-desc">cust_master.csv.gz (1.2KB) & cust_trade_detail.csv.gz (3.4KB)</div>
                </div>
              </div>
              <div class="flow-arrow">▼ &nbsp; 双轨传输：Snowsight 可视化拖拽 / Python PUT 客户端零成本上传</div>
              <div class="flow-node" style="border-color: #10B981;">
                <div style="font-size: 22px;">☁️</div>
                <div>
                  <div class="flow-node-title">Snowflake 受控内部暂存区 MITSUI_STAGE</div>
                  <div class="flow-node-desc">MITSUI_SEC_DB.RAW_ORACLE 模式 · AES-256 服务端强加密</div>
                </div>
              </div>
            </div>
          </div>
        </div>
        """
        html1 = generate_scene_html("scene1", s1["start_time"], s1["duration"], badge_label,
            "异构数据库迁移挑战与四大脏数据陷阱", "Heterogeneous Migration Challenges & 4 Major Dirty Data Traps", "DATA GOVERNANCE", c1, s1["script"], "zh-CN")

        # S2: 4 Cards
        c2 = """
        <div class="grid-4col">
          <div class="glass-card" style="border-color: rgba(56, 189, 248, 0.4);">
            <div class="card-header">
              <div class="card-title" style="font-size: 16px; color: #38BDF8;">1. 强制 UTF-8 无 BOM</div>
              <span class="stat-badge">ENCODING</span>
            </div>
            <div class="info-row" style="font-size: 12.5px;">
              <div>杜绝微软记事本附带的 <code>\\xEF\\xBB\\xBF</code> 字节序标记，避免表头首列被识别为 <code>﻿"ID"</code> 导致解析崩溃。</div>
            </div>
            <div class="code-box">file -i data.csv<br>-> charset=utf-8</div>
            <div class="stat-badge-success" style="text-align: center;">首列命名 100% 洁净</div>
          </div>
          <div class="glass-card" style="border-color: rgba(52, 211, 153, 0.4);">
            <div class="card-header">
              <div class="card-title" style="font-size: 16px; color: #34D399;">2. 双引号包裹字段</div>
              <span class="stat-badge-success">ENCLOSURE</span>
            </div>
            <div class="info-row" style="font-size: 12.5px;">
              <div>金融备注中若含有日文全角逗号或换行符，强制使用双引号包裹，防止 CSV 分裂错位。</div>
            </div>
            <div class="code-box">FIELD_OPTIONALLY_<br>ENCLOSED_BY = '"'</div>
            <div class="stat-badge-success" style="text-align: center;">列移位风险彻底清零</div>
          </div>
          <div class="glass-card" style="border-color: rgba(251, 191, 36, 0.4);">
            <div class="card-header">
              <div class="card-title" style="font-size: 16px; color: #FBBF24;">3. 空串转 NULL 标准化</div>
              <span class="stat-badge-warn">NULL MAPPING</span>
            </div>
            <div class="info-row" style="font-size: 12.5px;">
              <div>Oracle 空串导出为连续逗号 <code>,,</code>，Snowflake 启用映射参数无缝还原为标准 SQL NULL。</div>
            </div>
            <div class="code-box">EMPTY_FIELD_AS_NULL<br>= TRUE</div>
            <div class="stat-badge-success" style="text-align: center;">异构 NULL 语义无缝拉平</div>
          </div>
          <div class="glass-card" style="border-color: rgba(192, 132, 252, 0.4);">
            <div class="card-header">
              <div class="card-title" style="font-size: 16px; color: #C084FC;">4. Gzip 流式压缩</div>
              <span class="stat-badge">COMPRESSION</span>
            </div>
            <div class="info-row" style="font-size: 12.5px;">
              <div>导出同时直接写入 <code>.csv.gz</code>，体积大幅压缩 70%~90%，节省海量网络传输开销。</div>
            </div>
            <div class="code-box">gzip -9 data.csv<br>Ratio: 84.6% Saved</div>
            <div class="stat-badge-success" style="text-align: center;">网络传输提速 5 倍以上</div>
          </div>
        </div>
        """
        html2 = generate_scene_html("scene2", s2["start_time"], s2["duration"], badge_label,
            "生产级四重源头规范化治理方案", "Production 4-Tier Source Standardization Governance", "DATA CLEANING", c2, s2["script"], "zh-CN")

        # S3: Real Snowsight Screenshots (Dual-window: Overview & Upload Modal)
        c3 = """
        <div class="grid-2col">
          <div class="glass-card" style="border-color: rgba(56, 189, 248, 0.45);">
            <div class="card-header">
              <div class="card-title" style="color: #38BDF8;">🗂️ 受控暂存区 MITSUI_STAGE</div>
              <span class="card-badge" style="background: rgba(56, 189, 248, 0.15); color: #38BDF8; border: 1px solid rgba(56, 189, 248, 0.4);">INTERNAL STAGE</span>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #38BDF8;">★</span>
              <div><strong style="color: #FFFFFF;">所属数据库与模式定位</strong>：<br>位于 <code>MITSUI_SEC_DB.RAW_ORACLE</code>，专为接收源端 Oracle 导出资产建立。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #34D399;">★</span>
              <div><strong style="color: #FFFFFF;">原生端到端强加密 (AES-256)</strong>：<br>文件落地即自动实施加密存储，受 Snowflake 密钥生命周期统一管控。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #FBBF24;">★</span>
              <div><strong style="color: #FFFFFF;">Snowsight 可视化拖拽上传</strong>：<br>通过 Catalog 展开 RAW_ORACLE -> Stages -> MITSUI_STAGE，点击 <code>+ Files</code> 拖拽文件秒级上传。</div>
            </div>
            <div class="code-box">
              Snowsight UI: Catalog > Databases > MITSUI_SEC_DB > RAW_ORACLE > Stages > MITSUI_STAGE
            </div>
          </div>
          <!-- Real Screenshots in Window Console Frame -->
          <div class="window-frame">
            <div class="window-header">
              <div class="window-dots">
                <span class="window-dot dot-red"></span>
                <span class="window-dot dot-yellow"></span>
                <span class="window-dot dot-green"></span>
              </div>
              <div class="window-title">Snowsight · Stage Management Console</div>
              <span class="window-tag">RAW_ORACLE.MITSUI_STAGE</span>
            </div>
            <div class="window-content">
              <div class="dual-img-container">
                <div class="split-img-box">
                  <span class="split-tag">1. MITSUI_STAGE 暂存区主控制台</span>
                  <img src="../assets/images/04_stage_overview.png" alt="Snowsight MITSUI_STAGE Overview">
                </div>
                <div class="split-img-box">
                  <span class="split-tag">2. Snowsight 拖拽上传模态框 (Drag & Drop)</span>
                  <img src="../assets/images/04_stage_upload_modal.png" alt="Snowsight Stage Upload Modal">
                </div>
              </div>
            </div>
          </div>
        </div>
        """
        html3 = generate_scene_html("scene3", s3["start_time"], s3["duration"], badge_label,
            "受控暂存区 MITSUI_STAGE 与 Snowsight 控制台上传", "Controlled Internal Stage & Snowsight Visual Drag-and-Drop", "STAGE ASSETS", c3, s3["script"], "zh-CN")

        # S4: PUT Automation & Zero Compute Cost
        c4 = """
        <div class="grid-2col">
          <div class="glass-card" style="border-color: rgba(56, 189, 248, 0.45);">
            <div class="card-header">
              <div class="card-title" style="color: #38BDF8;">⚡ 生产流水线自动化传输 (PUT)</div>
              <span class="card-badge" style="background: rgba(56, 189, 248, 0.15); color: #38BDF8; border: 1px solid rgba(56, 189, 248, 0.4);">CLI & PYTHON</span>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #38BDF8;">➤</span>
              <div><strong style="color: #FFFFFF;">脚本级安全调度命令</strong>：<br>
                <div class="code-box" style="margin-top: 6px;">PUT file:///data/cust_master.csv.gz<br>  @MITSUI_STAGE<br>  AUTO_COMPRESS=FALSE;</div>
              </div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #34D399;">➤</span>
              <div><strong style="color: #FFFFFF;">生产环境自动化支持</strong>：<br>无缝嵌入 Airflow、dbt、Python connector，具备幂等传输与自动断点重试。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #C084FC;">➤</span>
              <div><strong style="color: #FFFFFF;">保留源端预压缩指纹</strong>：<br>指定 <code>AUTO_COMPRESS=FALSE</code>，避免二次压缩破坏源端 MD5 审计校验和。</div>
            </div>
          </div>
          <div class="glass-card" style="border-color: rgba(52, 211, 153, 0.45);">
            <div class="card-header">
              <div class="card-title" style="color: #34D399;">💰 零计算成本架构 (0 Credit Consumption)</div>
              <span class="card-badge" style="background: rgba(52, 211, 153, 0.15); color: #34D399; border: 1px solid rgba(52, 211, 153, 0.4);">FINOPS EXCELLENCE</span>
            </div>
            <div class="flow-step-box">
              <div class="flow-node" style="border-color: #34D399;">
                <div style="font-size: 20px;">💻</div>
                <div>
                  <div class="flow-node-title">本地客户端加密 (Client-Side Encrypted)</div>
                  <div class="flow-node-desc">在客户端生成临时安全密钥，本地完成 AES 加密</div>
                </div>
              </div>
              <div class="flow-arrow">▼ &nbsp; 经由安全 HTTPS 专线直接流式注入底层存储桶 (S3 / Azure Blob)</div>
              <div class="flow-node" style="border-color: #38BDF8;">
                <div style="font-size: 20px;">🪣</div>
                <div>
                  <div class="flow-node-title">Snowflake 托管云存储层 (Internal Stage)</div>
                  <div class="flow-node-desc">直接物理落盘，全程无需经过计算节点</div>
                </div>
              </div>
              <div class="info-row" style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3);">
                <span class="info-bullet" style="color: #34D399;">✔</span>
                <div><strong style="color: #FFFFFF;">虚拟计算仓库 Warehouse 状态：⏸️ 暂停 (SUSPENDED)</strong><br>计算信用点消耗严格为 0 Credit！为金融级海量数据上云节约天量预算。</div>
              </div>
            </div>
          </div>
        </div>
        """
        html4 = generate_scene_html("scene4", s4["start_time"], s4["duration"], badge_label,
            "生产自动化 PUT 命令与客户端零成本上传原理解析", "Production Automation PUT Command & Zero Compute Cost Transfer", "ZERO CREDIT TRANSFER", c4, s4["script"], "zh-CN")

    else:
        # JA Ep1
        c1 = """
        <div class="grid-2col">
          <div class="glass-card" style="border-color: rgba(248, 113, 113, 0.45);">
            <div class="card-header">
              <div class="card-title" style="color: #F87171;">⚠️ 異機種移行の罠：４大不整合リスク</div>
              <span class="card-badge" style="background: rgba(248, 113, 113, 0.15); color: #F87171; border: 1px solid rgba(248, 113, 113, 0.4);">RISK RADAR</span>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #F87171;">✖</span>
              <div><strong style="color: #FFFFFF;">文字コードのバイト長超過・化け</strong>：<br>Oracle 側の JA16SJIS 等が Snowflake の UTF-8 へ移行する際、バイト伸長により切り捨てや文字化けが発生。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #F87171;">✖</span>
              <div><strong style="color: #FFFFFF;">特殊記号と全角カンマによる列ズレ</strong>：<br>摘要欄に含まれる全角カンマや引用符のエスケープ漏れが、CSV パーサーの列分裂を誘発。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #F87171;">✖</span>
              <div><strong style="color: #FFFFFF;">空文字と NULL の仕様差異</strong>：<br>Oracle は空文字を NULL と同一視しますが、Snowflake では厳密に区別され集計矛盾の原因に。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #F87171;">✖</span>
              <div><strong style="color: #FFFFFF;">ネットワーク転送負荷とストレージ圧迫</strong>：<br>未圧縮の生データ転送は回線を逼迫させ、移行停止時間を超過するリスクを生みます。</div>
            </div>
          </div>
          <div class="glass-card" style="border-color: rgba(56, 189, 248, 0.45);">
            <div class="card-header">
              <div class="card-title" style="color: #38BDF8;">🏗️ ソース側正規化パイプラインアーキテクチャ</div>
              <span class="card-badge" style="background: rgba(56, 189, 248, 0.15); color: #38BDF8; border: 1px solid rgba(56, 189, 248, 0.4);">ARCHITECTURE</span>
            </div>
            <div class="flow-step-box">
              <div class="flow-node" style="border-color: #F59E0B;">
                <div style="font-size: 22px;">🗄️</div>
                <div>
                  <div class="flow-node-title">Oracle 11g 基幹データベース</div>
                  <div class="flow-node-desc">CUST_MASTER および CUST_TRADE_DETAIL 実機テーブル</div>
                </div>
              </div>
              <div class="flow-arrow">▼ &nbsp; ソース側データ規約：BOMなし UTF-8 · 引用符エスケープ · 空文字NULL化 · Gzip圧縮</div>
              <div class="flow-node" style="border-color: #38BDF8;">
                <div style="font-size: 22px;">📦</div>
                <div>
                  <div class="flow-node-title">正規化済み Gzip 抽出資産</div>
                  <div class="flow-node-desc">cust_master.csv.gz (1.2KB) & cust_trade_detail.csv.gz (3.4KB)</div>
                </div>
              </div>
              <div class="flow-arrow">▼ &nbsp; 2通りの転送経路：Snowsight GUI ドラッグ＆ドロップ / Python PUT ゼロコスト転送</div>
              <div class="flow-node" style="border-color: #10B981;">
                <div style="font-size: 22px;">☁️</div>
                <div>
                  <div class="flow-node-title">Snowflake 受入内部ステージ MITSUI_STAGE</div>
                  <div class="flow-node-desc">MITSUI_SEC_DB.RAW_ORACLE スキーマ · AES-256 自動暗号化</div>
                </div>
              </div>
            </div>
          </div>
        </div>
        """
        html1 = generate_scene_html("scene1", s1["start_time"], s1["duration"], badge_label,
            "異機種データベース移行の課題と４大不整合リスク", "Heterogeneous Migration Challenges & 4 Major Data Risks", "DATA GOVERNANCE", c1, s1["script"], "ja")

        c2 = """
        <div class="grid-4col">
          <div class="glass-card" style="border-color: rgba(56, 189, 248, 0.4);">
            <div class="card-header">
              <div class="card-title" style="font-size: 16px; color: #38BDF8;">1. BOMなし UTF-8 強制</div>
              <span class="stat-badge">ENCODING</span>
            </div>
            <div class="info-row" style="font-size: 12px;">
              <div>Windows 特有の <code>\\xEF\\xBB\\xBF</code> を排除し、先頭列名が破損するトラブルを防止。</div>
            </div>
            <div class="code-box">file -i data.csv<br>-> charset=utf-8</div>
            <div class="stat-badge-success" style="text-align: center;">先頭列名破損を100%根絶</div>
          </div>
          <div class="glass-card" style="border-color: rgba(52, 211, 153, 0.4);">
            <div class="card-header">
              <div class="card-title" style="font-size: 16px; color: #34D399;">2. 二重引用符エスケープ</div>
              <span class="stat-badge-success">ENCLOSURE</span>
            </div>
            <div class="info-row" style="font-size: 12px;">
              <div>全角記号やカンマを含む摘要列を二重引用符で厳格に囲み、列ズレを徹底排除。</div>
            </div>
            <div class="code-box">FIELD_OPTIONALLY_<br>ENCLOSED_BY = '"'</div>
            <div class="stat-badge-success" style="text-align: center;">列ズレ・パース破壊ゼロ</div>
          </div>
          <div class="glass-card" style="border-color: rgba(251, 191, 36, 0.4);">
            <div class="card-header">
              <div class="card-title" style="font-size: 16px; color: #FBBF24;">3. 空文字の正規NULL化</div>
              <span class="stat-badge-warn">NULL MAPPING</span>
            </div>
            <div class="info-row" style="font-size: 12px;">
              <div>Oracle の空文字を連続カンマ <code>,,</code> で出力し、Snowflake で正規 NULL へ復元。</div>
            </div>
            <div class="code-box">EMPTY_FIELD_AS_NULL<br>= TRUE</div>
            <div class="stat-badge-success" style="text-align: center;">SQL NULL 仕様を完全一致</div>
          </div>
          <div class="glass-card" style="border-color: rgba(192, 132, 252, 0.4);">
            <div class="card-header">
              <div class="card-title" style="font-size: 16px; color: #C084FC;">4. Gzip ストリーム圧縮</div>
              <span class="stat-badge">COMPRESSION</span>
            </div>
            <div class="info-row" style="font-size: 12px;">
              <div>抽出と同時に <code>.csv.gz</code> 化。データ量を 70〜90% 削減しネットワーク負荷を極小化。</div>
            </div>
            <div class="code-box">gzip -9 data.csv<br>Ratio: 84.6% Saved</div>
            <div class="stat-badge-success" style="text-align: center;">転送速度5倍以上向上</div>
          </div>
        </div>
        """
        html2 = generate_scene_html("scene2", s2["start_time"], s2["duration"], badge_label,
            "４大不整合リスクへの源流正規化ガバナンス", "Production 4-Tier Source Standardization Governance", "DATA CLEANING", c2, s2["script"], "ja")

        c3 = """
        <div class="grid-2col">
          <div class="glass-card" style="border-color: rgba(56, 189, 248, 0.45);">
            <div class="card-header">
              <div class="card-title" style="color: #38BDF8;">🗂️ 受入内部ステージ MITSUI_STAGE</div>
              <span class="card-badge" style="background: rgba(56, 189, 248, 0.15); color: #38BDF8; border: 1px solid rgba(56, 189, 248, 0.4);">INTERNAL STAGE</span>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #38BDF8;">★</span>
              <div><strong style="color: #FFFFFF;">配置スキーマとスコープ</strong>：<br><code>MITSUI_SEC_DB.RAW_ORACLE</code> 配下に配置され、Oracle 資産の受領に特化。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #34D399;">★</span>
              <div><strong style="color: #FFFFFF;">AES-256 自動暗号化の適用</strong>：<br>格納と同時に強固な暗号化が施され、Snowflake のキー管理により機密性を維持。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #FBBF24;">★</span>
              <div><strong style="color: #FFFFFF;">Snowsight による視覚的アップロード</strong>：<br>カタログツリーを展開し、<code>+ Files</code> ボタンからドラッグ＆ドロップで投入可能。</div>
            </div>
            <div class="code-box">
              Snowsight UI: Catalog > Databases > MITSUI_SEC_DB > RAW_ORACLE > Stages > MITSUI_STAGE
            </div>
          </div>
          <!-- Real Screenshots in Window Console Frame -->
          <div class="window-frame">
            <div class="window-header">
              <div class="window-dots">
                <span class="window-dot dot-red"></span>
                <span class="window-dot dot-yellow"></span>
                <span class="window-dot dot-green"></span>
              </div>
              <div class="window-title">Snowsight · Stage Management Console</div>
              <span class="window-tag">RAW_ORACLE.MITSUI_STAGE</span>
            </div>
            <div class="window-content">
              <div class="dual-img-container">
                <div class="split-img-box">
                  <span class="split-tag">1. MITSUI_STAGE ステージ管理画面</span>
                  <img src="../assets/images/04_stage_overview.png" alt="Snowsight MITSUI_STAGE Overview">
                </div>
                <div class="split-img-box">
                  <span class="split-tag">2. ドラッグ＆ドロップ アップロードモーダル</span>
                  <img src="../assets/images/04_stage_upload_modal.png" alt="Snowsight Stage Upload Modal">
                </div>
              </div>
            </div>
          </div>
        </div>
        """
        html3 = generate_scene_html("scene3", s3["start_time"], s3["duration"], badge_label,
            "内部ステージ MITSUI_STAGE と Snowsight UI アップロード", "Controlled Internal Stage & Snowsight Drag-and-Drop", "STAGE ASSETS", c3, s3["script"], "ja")

        c4 = """
        <div class="grid-2col">
          <div class="glass-card" style="border-color: rgba(56, 189, 248, 0.45);">
            <div class="card-header">
              <div class="card-title" style="color: #38BDF8;">⚡ 本番パイプライン自動転送 (PUT)</div>
              <span class="card-badge" style="background: rgba(56, 189, 248, 0.15); color: #38BDF8; border: 1px solid rgba(56, 189, 248, 0.4);">CLI & PYTHON</span>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #38BDF8;">➤</span>
              <div><strong style="color: #FFFFFF;">スクリプトからの安全発行</strong>：<br>
                <div class="code-box" style="margin-top: 6px;">PUT file:///data/cust_master.csv.gz<br>  @MITSUI_STAGE<br>  AUTO_COMPRESS=FALSE;</div>
              </div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #34D399;">➤</span>
              <div><strong style="color: #FFFFFF;">CI/CD および運用スケジューラ連携</strong>：<br>Airflow、dbt、Python コネクタから呼び出し可能で、冪等性と自動再試行を担保。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #C084FC;">➤</span>
              <div><strong style="color: #FFFFFF;">再圧縮によるハッシュ破壊を防止</strong>：<br><code>AUTO_COMPRESS=FALSE</code> を明示し、抽出時の MD5 チェックサムを完全保持。</div>
            </div>
          </div>
          <div class="glass-card" style="border-color: rgba(52, 211, 153, 0.45);">
            <div class="card-header">
              <div class="card-title" style="color: #34D399;">💰 ゼロ計算コストの仕組み (0 Credit)</div>
              <span class="card-badge" style="background: rgba(52, 211, 153, 0.15); color: #34D399; border: 1px solid rgba(52, 211, 153, 0.4);">FINOPS EXCELLENCE</span>
            </div>
            <div class="flow-step-box">
              <div class="flow-node" style="border-color: #34D399;">
                <div style="font-size: 20px;">💻</div>
                <div>
                  <div class="flow-node-title">クライアント側暗号化 (Client-Side Encrypted)</div>
                  <div class="flow-node-desc">手元で一時暗号化キーを生成し AES 暗号化を実行</div>
                </div>
              </div>
              <div class="flow-arrow">▼ &nbsp; セキュアな HTTPS 経由でクラウドストレージ層 (S3) へ直接注入</div>
              <div class="flow-node" style="border-color: #38BDF8;">
                <div style="font-size: 20px;">🪣</div>
                <div>
                  <div class="flow-node-title">Snowflake 内部ステージストレージ</div>
                  <div class="flow-node-desc">コンピュートを経由せずストレージ層へ直接格納</div>
                </div>
              </div>
              <div class="info-row" style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3);">
                <span class="info-bullet" style="color: #34D399;">✔</span>
                <div><strong style="color: #FFFFFF;">仮想ウェアハウスの状態：⏸️ 停止中 (SUSPENDED)</strong><br>計算クレジット消費は完全にゼロ！金融テラバイト移行コストを大幅に抑制。</div>
              </div>
            </div>
          </div>
        </div>
        """
        html4 = generate_scene_html("scene4", s4["start_time"], s4["duration"], badge_label,
            "本番自動化 PUT コマンドとゼロコスト転送アーキテクチャ", "Production Automation PUT Command & Zero Compute Cost Transfer", "ZERO CREDIT TRANSFER", c4, s4["script"], "ja")

    with open(os.path.join(comp_dir, "scene1.html"), "w", encoding="utf-8") as f:
        f.write(html1)
    with open(os.path.join(comp_dir, "scene2.html"), "w", encoding="utf-8") as f:
        f.write(html2)
    with open(os.path.join(comp_dir, "scene3.html"), "w", encoding="utf-8") as f:
        f.write(html3)
    with open(os.path.join(comp_dir, "scene4.html"), "w", encoding="utf-8") as f:
        f.write(html4)

# =========================================================================
# EPISODE 2
# =========================================================================
def build_ep2_scenes(comp_dir, lang, badge_label, s1, s2, s3, s4):
    if lang == "zh":
        # S1: Session context
        c1 = """
        <div class="grid-2col">
          <div class="glass-card" style="border-color: rgba(56, 189, 248, 0.45);">
            <div class="card-header">
              <div class="card-title" style="color: #38BDF8;">⚙️ 会话上下文四要素就绪 (Step 00)</div>
              <span class="card-badge" style="background: rgba(56, 189, 248, 0.15); color: #38BDF8; border: 1px solid rgba(56, 189, 248, 0.4);">SESSION CONTEXT</span>
            </div>
            <div class="code-box">
              USE ROLE MITSUI_ENGINEER;<br>
              USE WAREHOUSE MITSUI_WH;<br>
              USE DATABASE MITSUI_SEC_DB;<br>
              USE SCHEMA RAW_ORACLE;
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #34D399;">✔</span>
              <div><strong style="color: #FFFFFF;">隔离运行环境</strong>：建立专属工程工作区，排除由于缺少前置约束导致的跨库误操作。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #38BDF8;">✔</span>
              <div><strong style="color: #FFFFFF;">精准算力挂接</strong>：指定专属仓库 <code>MITSUI_WH</code>，支持秒级自动暂停与成本核算。</div>
            </div>
          </div>
          <div class="glass-card" style="border-color: rgba(52, 211, 153, 0.45);">
            <div class="card-header">
              <div class="card-title" style="color: #34D399;">🔒 最小特权与金融合规红线</div>
              <span class="card-badge" style="background: rgba(52, 211, 153, 0.15); color: #34D399; border: 1px solid rgba(52, 211, 153, 0.4);">LEAST PRIVILEGE</span>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #F87171;">✖</span>
              <div><strong style="color: #FFFFFF;">严禁特权角色作业</strong>：严禁使用 <code>ACCOUNTADMIN</code> 或 <code>SYSADMIN</code> 进行业务数据导入。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #34D399;">✔</span>
              <div><strong style="color: #FFFFFF;">特权精准下放闭环</strong>：<code>MITSUI_ENGINEER</code> 仅被授予指定 RAW_ORACLE 模式的表写入特权。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #C084FC;">✔</span>
              <div><strong style="color: #FFFFFF;">符合金融审计可溯性</strong>：严格记录实操人员角色与算力日志，满足三井证券内控审查要求。</div>
            </div>
          </div>
        </div>
        """
        html1 = generate_scene_html("scene1", s1["start_time"], s1["duration"], badge_label,
            "工程上下文就绪与最小特权会话建立", "Engineering Context Ready & Least Privilege Session Establishment", "SESSION READY", c1, s1["script"], "zh-CN")

        # S2: Real Screenshot 04_step_01_02.png (LIST @MITSUI_STAGE)
        c2 = """
        <div class="grid-2col">
          <div class="glass-card" style="border-color: rgba(56, 189, 248, 0.45);">
            <div class="card-header">
              <div class="card-title" style="color: #38BDF8;">📋 暂存资产清单核验 (Step 01 & 02)</div>
              <span class="card-badge" style="background: rgba(56, 189, 248, 0.15); color: #38BDF8; border: 1px solid rgba(56, 189, 248, 0.4);">LIST INVENTORY</span>
            </div>
            <div class="code-box">
              -- 核查受控暂存区待装载文件<br>
              LIST @MITSUI_STAGE;
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #38BDF8;">1</span>
              <div><strong>cust_master.csv.gz</strong><br><span class="stat-badge">Size: 1,248 B</span> &nbsp;<span class="stat-badge">MD5 指纹校验和对齐</span></div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #34D399;">2</span>
              <div><strong>cust_trade_detail.csv.gz</strong><br><span class="stat-badge">Size: 3,420 B</span> &nbsp;<span class="stat-badge">MD5 指纹校验和对齐</span></div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #C084FC;">✔</span>
              <div><strong style="color: #FFFFFF;">物理介质完整性验证通过</strong>：排除网络传输丢包与 0 字节损坏文件，物理介质无损。</div>
            </div>
          </div>
          <!-- Real Screenshot in Window Console Frame -->
          <div class="window-frame">
            <div class="window-header">
              <div class="window-dots">
                <span class="window-dot dot-red"></span>
                <span class="window-dot dot-yellow"></span>
                <span class="window-dot dot-green"></span>
              </div>
              <div class="window-title">Snowsight · Worksheet Console [Step 01 & 02]</div>
              <span class="window-tag">STATUS: 2 FILES READY</span>
            </div>
            <div class="window-content">
              <img src="../assets/images/04_step_01_02.png" alt="Snowsight Step 01 & 02 LIST Command Result">
            </div>
          </div>
        </div>
        """
        html2 = generate_scene_html("scene2", s2["start_time"], s2["duration"], badge_label,
            "暂存清单核验与物理文件元数据审计", "Stage Inventory Verification & Physical Metadata Audit", "ASSET AUDIT", c2, s2["script"], "zh-CN")

        # S3: Critical Pitfall: VALIDATION_MODE with subquery
        c3 = """
        <div class="grid-2col">
          <div class="glass-card" style="border-color: rgba(248, 113, 113, 0.45);">
            <div class="card-header">
              <div class="card-title" style="color: #F87171;">💥 致命避坑陷阱：VALIDATION_MODE 编译崩溃</div>
              <span class="card-badge" style="background: rgba(248, 113, 113, 0.15); color: #F87171; border: 1px solid rgba(248, 113, 113, 0.4);">CRITICAL PITFALL</span>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #F87171;">✖</span>
              <div><strong style="color: #FFFFFF;">常规认知误区</strong>：很多工程师习惯在 <code>COPY INTO</code> 添加 <code>VALIDATION_MODE = 'RETURN_ERRORS'</code> 以为可以提前试跑。</div>
            </div>
            <div class="code-box" style="border-color: rgba(248, 113, 113, 0.4); color: #F87171;">
              COPY INTO CUST_TRADE_DETAIL<br>
              FROM (SELECT $1, $2, TO_DATE($4, 'YYYYMMDD') FROM @MITSUI_STAGE)<br>
              VALIDATION_MODE = 'RETURN_ERRORS';<br>
              -- ❌ SQL compilation error: Validation mode is not supported with transformations!
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #F87171;">✖</span>
              <div><strong style="color: #FFFFFF;">流水线中断惨剧</strong>：在自动化 CI/CD 中混用此参数将导致整个迁移作业当场编译报错熔断！</div>
            </div>
          </div>
          <div class="glass-card" style="border-color: rgba(251, 191, 36, 0.45);">
            <div class="card-header">
              <div class="card-title" style="color: #FBBF24;">🔍 Snowflake 底层架构限制原理</div>
              <span class="card-badge" style="background: rgba(251, 191, 36, 0.15); color: #FBBF24; border: 1px solid rgba(251, 191, 36, 0.4);">ENGINE ARCHITECTURE</span>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #FBBF24;">!</span>
              <div><strong style="color: #FFFFFF;">直拷与转换的架构割裂</strong>：<code>VALIDATION_MODE</code> 原理是绕过装载仅对原生文件进行词法分析，只支持 1:1 简单直拷。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #38BDF8;">!</span>
              <div><strong style="color: #FFFFFF;">子查询涉及虚拟计算引擎</strong>：带有 <code>SELECT $1, $2, TO_DATE()</code> 等转换时，需要算力引擎执行表达式，底层彻底禁用验证模式。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #34D399;">!</span>
              <div><strong style="color: #FFFFFF;">必须掌握替代方案</strong>：利用 Stage 直接投影试跑，成为唯一优雅可靠的预检手段！</div>
            </div>
          </div>
        </div>
        """
        html3 = generate_scene_html("scene3", s3["start_time"], s3["duration"], badge_label,
            "生产重磅避坑：VALIDATION_MODE 与子查询语法冲突", "Production Pitfall: VALIDATION_MODE Incompatible with Subqueries", "SYNTAX TRAP", c3, s3["script"], "zh-CN")

        # S4: Real Screenshot 04_step_03_preview.png (Stage Direct Projection)
        c4 = """
        <div class="grid-2col">
          <div class="glass-card" style="border-color: rgba(52, 211, 153, 0.45);">
            <div class="card-header">
              <div class="card-title" style="color: #34D399;">🏆 黄金准则：Stage 无表直接投影试跑 (Step 03)</div>
              <span class="card-badge" style="background: rgba(52, 211, 153, 0.15); color: #34D399; border: 1px solid rgba(52, 211, 153, 0.4);">GOLDEN PRACTICE</span>
            </div>
            <div class="code-box">
              SELECT<br>
              &nbsp;&nbsp;$1 AS TRADE_ID,<br>
              &nbsp;&nbsp;$2 AS CUST_ID,<br>
              &nbsp;&nbsp;TO_DATE($4, 'YYYYMMDD') AS TRADE_DATE,<br>
              &nbsp;&nbsp;$7::NUMBER(18,3) AS SETTLE_AMOUNT<br>
              FROM @MITSUI_STAGE/cust_trade_detail.csv.gz<br>
              (FILE_FORMAT => 'CSV_GZ_FORMAT')<br>
              LIMIT 5;
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #34D399;">✔</span>
              <div><strong style="color: #FFFFFF;">未解压原地试跑</strong>：直接在压缩包上执行投影计算，零中间建表成本。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #38BDF8;">✔</span>
              <div><strong style="color: #FFFFFF;">前置检验强转精度</strong>：试跑核验 <code>TO_DATE</code> 与 <code>NUMBER(18,3)</code> 是否产生解析截断。</div>
            </div>
          </div>
          <!-- Real Screenshot in Window Console Frame -->
          <div class="window-frame">
            <div class="window-header">
              <div class="window-dots">
                <span class="window-dot dot-red"></span>
                <span class="window-dot dot-yellow"></span>
                <span class="window-dot dot-green"></span>
              </div>
              <div class="window-title">Snowsight · Stage Direct Projection Preview [Step 03]</div>
              <span class="window-tag">QUERY RESULT: 5 ROWS</span>
            </div>
            <div class="window-content">
              <img src="../assets/images/04_step_03_preview.png" alt="Snowsight Step 03 Stage Projection Preview">
            </div>
          </div>
        </div>
        """
        html4 = generate_scene_html("scene4", s4["start_time"], s4["duration"], badge_label,
            "黄金准则：Stage 无表直接投影试跑", "Golden Practice: Stage Table-less Direct Projection Preview", "PROJECTION PREVIEW", c4, s4["script"], "zh-CN")

    else:
        # JA Ep2
        c1 = """
        <div class="grid-2col">
          <div class="glass-card" style="border-color: rgba(56, 189, 248, 0.45);">
            <div class="card-header">
              <div class="card-title" style="color: #38BDF8;">⚙️ セッションコンテキストの確立 (Step 00)</div>
              <span class="card-badge" style="background: rgba(56, 189, 248, 0.15); color: #38BDF8; border: 1px solid rgba(56, 189, 248, 0.4);">SESSION CONTEXT</span>
            </div>
            <div class="code-box">
              USE ROLE MITSUI_ENGINEER;<br>
              USE WAREHOUSE MITSUI_WH;<br>
              USE DATABASE MITSUI_SEC_DB;<br>
              USE SCHEMA RAW_ORACLE;
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #34D399;">✔</span>
              <div><strong style="color: #FFFFFF;">環境の即時適用</strong>：他スキーマへの誤爆を防止し、隔離された安全な実行スコープを確立。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #38BDF8;">✔</span>
              <div><strong style="color: #FFFFFF;">専用WHへの接続</strong>：<code>MITSUI_WH</code> を明示し、秒単位の自動サスペンドとコスト分離を実現。</div>
            </div>
          </div>
          <div class="glass-card" style="border-color: rgba(52, 211, 153, 0.45);">
            <div class="card-header">
              <div class="card-title" style="color: #34D399;">🔒 最小特権の原則と金融監査対応</div>
              <span class="card-badge" style="background: rgba(52, 211, 153, 0.15); color: #34D399; border: 1px solid rgba(52, 211, 153, 0.4);">LEAST PRIVILEGE</span>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #F87171;">✖</span>
              <div><strong style="color: #FFFFFF;">特権ロールの常用厳禁</strong>：<code>ACCOUNTADMIN</code> や <code>SYSADMIN</code> での日常的データロードは禁止。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #34D399;">✔</span>
              <div><strong style="color: #FFFFFF;">権限の極小化</strong>：<code>MITSUI_ENGINEER</code> には指定スキーマへのロードとWH利用権限のみを付与。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #C084FC;">✔</span>
              <div><strong style="color: #FFFFFF;">完全なトレーサビリティ</strong>：担当ロールとWH利用実績が監査ログに刻まれ、内部統制をクリア。</div>
            </div>
          </div>
        </div>
        """
        html1 = generate_scene_html("scene1", s1["start_time"], s1["duration"], badge_label,
            "エンジニア環境設定と最小特権セッション確立", "Engineering Context Ready & Least Privilege Session", "SESSION READY", c1, s1["script"], "ja")

        c2 = """
        <div class="grid-2col">
          <div class="glass-card" style="border-color: rgba(56, 189, 248, 0.45);">
            <div class="card-header">
              <div class="card-title" style="color: #38BDF8;">📋 受入ステージ資産の監査 (Step 01 & 02)</div>
              <span class="card-badge" style="background: rgba(56, 189, 248, 0.15); color: #38BDF8; border: 1px solid rgba(56, 189, 248, 0.4);">LIST INVENTORY</span>
            </div>
            <div class="code-box">
              -- 受入ステージ内の対象２ファイルを照会<br>
              LIST @MITSUI_STAGE;
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #38BDF8;">1</span>
              <div><strong>cust_master.csv.gz</strong><br><span class="stat-badge">Size: 1,248 B</span> &nbsp;<span class="stat-badge">MD5 チェックサム検証済</span></div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #34D399;">2</span>
              <div><strong>cust_trade_detail.csv.gz</strong><br><span class="stat-badge">Size: 3,420 B</span> &nbsp;<span class="stat-badge">MD5 チェックサム検証済</span></div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #C084FC;">✔</span>
              <div><strong style="color: #FFFFFF;">ゼロバイト破損の完全排除</strong>：転送途絶によるダミーファイルを即時検出・排除。</div>
            </div>
          </div>
          <!-- Real Screenshot in Window Console Frame -->
          <div class="window-frame">
            <div class="window-header">
              <div class="window-dots">
                <span class="window-dot dot-red"></span>
                <span class="window-dot dot-yellow"></span>
                <span class="window-dot dot-green"></span>
              </div>
              <div class="window-title">Snowsight · Worksheet Console [Step 01 & 02]</div>
              <span class="window-tag">STATUS: 2 FILES READY</span>
            </div>
            <div class="window-content">
              <img src="../assets/images/04_step_01_02.png" alt="Snowsight Step 01 & 02 LIST Command Result">
            </div>
          </div>
        </div>
        """
        html2 = generate_scene_html("scene2", s2["start_time"], s2["duration"], badge_label,
            "ステージ一覧確認と物理ファイルメタデータ監査", "Stage Inventory Verification & Physical Metadata Audit", "ASSET AUDIT", c2, s2["script"], "ja")

        c3 = """
        <div class="grid-2col">
          <div class="glass-card" style="border-color: rgba(248, 113, 113, 0.45);">
            <div class="card-header">
              <div class="card-title" style="color: #F87171;">💥 致命的トラブル：VALIDATION_MODE 構文衝突</div>
              <span class="card-badge" style="background: rgba(248, 113, 113, 0.15); color: #F87171; border: 1px solid rgba(248, 113, 113, 0.4);">CRITICAL PITFALL</span>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #F87171;">✖</span>
              <div><strong style="color: #FFFFFF;">陥りがちな思い込み</strong>：事前検証として <code>COPY INTO</code> に <code>VALIDATION_MODE = 'RETURN_ERRORS'</code> を付与しがちです。</div>
            </div>
            <div class="code-box" style="border-color: rgba(248, 113, 113, 0.4); color: #F87171;">
              COPY INTO CUST_TRADE_DETAIL<br>
              FROM (SELECT $1, $2, TO_DATE($4, 'YYYYMMDD') FROM @MITSUI_STAGE)<br>
              VALIDATION_MODE = 'RETURN_ERRORS';<br>
              -- ❌ SQL compilation error: Validation mode is not supported with transformations!
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #F87171;">✖</span>
              <div><strong style="color: #FFFFFF;">パイプライン即死リスク</strong>：列変換や関数を伴う COPY 構文と混在すると、本番バッチが即時コンパイルエラーで停止！</div>
            </div>
          </div>
          <div class="glass-card" style="border-color: rgba(251, 191, 36, 0.45);">
            <div class="card-header">
              <div class="card-title" style="color: #FBBF24;">🔍 Snowflake アーキテクチャ上の仕様制約</div>
              <span class="card-badge" style="background: rgba(251, 191, 36, 0.15); color: #FBBF24; border: 1px solid rgba(251, 191, 36, 0.4);">ENGINE ARCHITECTURE</span>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #FBBF24;">!</span>
              <div><strong style="color: #FFFFFF;">直接コピーと変換クエリの壁</strong>：<code>VALIDATION_MODE</code> はファイル構文のみを走査する設計のため、単純直行コピーのみ対応。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #38BDF8;">!</span>
              <div><strong style="color: #FFFFFF;">仮想列と評価エンジンの介入</strong>：<code>SELECT $1, TO_DATE()</code> 等の式評価には計算エンジンが必要であり、検証モードは無効化されます。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #34D399;">!</span>
              <div><strong style="color: #FFFFFF;">防衛策の確立</strong>：ステージ直接射影クエリこそが、唯一無二の安全な検証手段です！</div>
            </div>
          </div>
        </div>
        """
        html3 = generate_scene_html("scene3", s3["start_time"], s3["duration"], badge_label,
            "本番最大の急所：VALIDATION_MODE と列変換の構文衝突", "Production Pitfall: VALIDATION_MODE with Transformations", "SYNTAX TRAP", c3, s3["script"], "ja")

        c4 = """
        <div class="grid-2col">
          <div class="glass-card" style="border-color: rgba(52, 211, 153, 0.45);">
            <div class="card-header">
              <div class="card-title" style="color: #34D399;">🏆 黄金律：ステージ直接射影プレビュー (Step 03)</div>
              <span class="card-badge" style="background: rgba(52, 211, 153, 0.15); color: #34D399; border: 1px solid rgba(52, 211, 153, 0.4);">GOLDEN PRACTICE</span>
            </div>
            <div class="code-box">
              SELECT<br>
              &nbsp;&nbsp;$1 AS TRADE_ID,<br>
              &nbsp;&nbsp;$2 AS CUST_ID,<br>
              &nbsp;&nbsp;TO_DATE($4, 'YYYYMMDD') AS TRADE_DATE,<br>
              &nbsp;&nbsp;$7::NUMBER(18,3) AS SETTLE_AMOUNT<br>
              FROM @MITSUI_STAGE/cust_trade_detail.csv.gz<br>
              (FILE_FORMAT => 'CSV_GZ_FORMAT')<br>
              LIMIT 5;
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #34D399;">✔</span>
              <div><strong style="color: #FFFFFF;">未解凍のまま直接試行</strong>：圧縮ファイルに対して直接 SELECT 式を発行し、中間表なしで検証。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #38BDF8;">✔</span>
              <div><strong style="color: #FFFFFF;">型変換と書式の事前チェック</strong>：<code>TO_DATE</code> や <code>NUMBER(18,3)</code> のキャストが正常動作するか先回り検証。</div>
            </div>
          </div>
          <!-- Real Screenshot in Window Console Frame -->
          <div class="window-frame">
            <div class="window-header">
              <div class="window-dots">
                <span class="window-dot dot-red"></span>
                <span class="window-dot dot-yellow"></span>
                <span class="window-dot dot-green"></span>
              </div>
              <div class="window-title">Snowsight · Stage Direct Projection Preview [Step 03]</div>
              <span class="window-tag">QUERY RESULT: 5 ROWS</span>
            </div>
            <div class="window-content">
              <img src="../assets/images/04_step_03_preview.png" alt="Snowsight Step 03 Stage Projection Preview">
            </div>
          </div>
        </div>
        """
        html4 = generate_scene_html("scene4", s4["start_time"], s4["duration"], badge_label,
            "黄金律：テーブルレス直接射影プレビュー", "Golden Practice: Stage Table-less Direct Projection Preview", "PROJECTION PREVIEW", c4, s4["script"], "ja")

    with open(os.path.join(comp_dir, "scene1.html"), "w", encoding="utf-8") as f:
        f.write(html1)
    with open(os.path.join(comp_dir, "scene2.html"), "w", encoding="utf-8") as f:
        f.write(html2)
    with open(os.path.join(comp_dir, "scene3.html"), "w", encoding="utf-8") as f:
        f.write(html3)
    with open(os.path.join(comp_dir, "scene4.html"), "w", encoding="utf-8") as f:
        f.write(html4)

# =========================================================================
# EPISODE 3
# =========================================================================
def build_ep3_scenes(comp_dir, lang, badge_label, s1, s2, s3, s4):
    if lang == "zh":
        # S1: CUST_MASTER batch spec
        c1 = """
        <div class="grid-2col">
          <div class="glass-card" style="border-color: rgba(56, 189, 248, 0.45);">
            <div class="card-header">
              <div class="card-title" style="color: #38BDF8;">📦 客户维度主表批量装载 (Step 04)</div>
              <span class="card-badge" style="background: rgba(56, 189, 248, 0.15); color: #38BDF8; border: 1px solid rgba(56, 189, 248, 0.4);">COPY INTO MASTER</span>
            </div>
            <div class="code-box">
              COPY INTO CUST_MASTER (<br>
              &nbsp;&nbsp;CUST_ID, CUST_TYPE, CUST_NAME,<br>
              &nbsp;&nbsp;BRANCH_CODE, RISK_RANK, STATUS, OPEN_DATE<br>
              )<br>
              FROM (<br>
              &nbsp;&nbsp;SELECT $1, $2, $3, $4, $5, $6, TO_DATE($7, 'YYYYMMDD')<br>
              &nbsp;&nbsp;FROM @MITSUI_STAGE/cust_master.csv.gz<br>
              )<br>
              FILE_FORMAT = (FORMAT_NAME = 'CSV_GZ_FORMAT')<br>
              ON_ERROR = 'ABORT_STATEMENT';
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #34D399;">✔</span>
              <div><strong style="color: #FFFFFF;">明确指定全路径</strong>：定位具体文件 <code>cust_master.csv.gz</code>，杜绝通配符串入。</div>
            </div>
          </div>
          <div class="glass-card" style="border-color: rgba(52, 211, 153, 0.45);">
            <div class="card-header">
              <div class="card-title" style="color: #34D399;">🛡️ 主数据字段规范与金融映射表</div>
              <span class="card-badge" style="background: rgba(52, 211, 153, 0.15); color: #34D399; border: 1px solid rgba(52, 211, 153, 0.4);">DATA SCHEMA</span>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #38BDF8;">1</span>
              <div><code>CUST_ID</code>: 核心客户编号 (NUMBER 10位整数，主键约束保证)</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #34D399;">2</span>
              <div><code>CUST_NAME</code>: 客户姓名 (支持多字节中日文宽字符无乱码落盘)</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #FBBF24;">3</span>
              <div><code>RISK_RANK</code>: 风险评级 (A/B/C/D 严格适配合规评级标准)</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #C084FC;">4</span>
              <div><code>OPEN_DATE</code>: 开户日期 (强转标准 <code>DATE</code> 字段规范)</div>
            </div>
          </div>
        </div>
        """
        html1 = generate_scene_html("scene1", s1["start_time"], s1["duration"], badge_label,
            "客户主表 CUST_MASTER 批量 COPY INTO 入库", "Customer Master COPY INTO Batch Ingestion", "BATCH INGESTION", c1, s1["script"], "zh-CN")

        # S2: Real Screenshot 04_step_04_copy_master.png
        c2 = """
        <div class="grid-2col">
          <div class="glass-card" style="border-color: rgba(248, 113, 113, 0.45);">
            <div class="card-header">
              <div class="card-title" style="color: #F87171;">🛑 强一致回滚与微秒审计列</div>
              <span class="card-badge" style="background: rgba(248, 113, 113, 0.15); color: #F87171; border: 1px solid rgba(248, 113, 113, 0.4);">TRANSACTION INTEGRITY</span>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #F87171;">★</span>
              <div><strong style="color: #FFFFFF;">ON_ERROR = 'ABORT_STATEMENT'</strong>：<br>金融级强一致要求，遇到哪怕单行脏数据即全量回滚，绝不容许半装载或半孤儿数据产生。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #34D399;">★</span>
              <div><strong style="color: #FFFFFF;">MIGRATED_AT 自动填充</strong>：<br>建表时声明 <code>DEFAULT CURRENT_TIMESTAMP()</code>，入库无需外部传入，系统自动打上微秒级物理入云时间戳。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #38BDF8;">✔</span>
              <div><strong style="color: #FFFFFF;">主表首战告捷</strong>：13 条客户记录 100% 精准装载，错误数为 0！</div>
            </div>
          </div>
          <!-- Real Screenshot in Window Console Frame -->
          <div class="window-frame">
            <div class="window-header">
              <div class="window-dots">
                <span class="window-dot dot-red"></span>
                <span class="window-dot dot-yellow"></span>
                <span class="window-dot dot-green"></span>
              </div>
              <div class="window-title">Snowsight · COPY INTO CUST_MASTER Result [Step 04]</div>
              <span class="window-tag">STATUS: LOADED (13 ROWS)</span>
            </div>
            <div class="window-content">
              <img src="../assets/images/04_step_04_copy_master.png" alt="Snowsight Step 04 COPY INTO CUST_MASTER Result">
            </div>
          </div>
        </div>
        """
        html2 = generate_scene_html("scene2", s2["start_time"], s2["duration"], badge_label,
            "强一致回滚 ON_ERROR 与 MIGRATED_AT 入云审计列", "ACID Rollback ON_ERROR & Ingestion Timestamp Auditing", "ACID COMPLIANCE", c2, s2["script"], "zh-CN")

        # S3: Real Screenshot 04_step_05_copy_trade.png
        c3 = """
        <div class="grid-2col">
          <div class="glass-card" style="border-color: rgba(56, 189, 248, 0.45);">
            <div class="card-header">
              <div class="card-title" style="color: #38BDF8;">📈 交易事实表 CUST_TRADE_DETAIL 装载</div>
              <span class="card-badge" style="background: rgba(56, 189, 248, 0.15); color: #38BDF8; border: 1px solid rgba(56, 189, 248, 0.4);">TRADE FACT LOAD</span>
            </div>
            <div class="code-box">
              COPY INTO CUST_TRADE_DETAIL FROM (<br>
              &nbsp;&nbsp;SELECT $1, $2, $3, TO_DATE($4, 'YYYYMMDD'),<br>
              &nbsp;&nbsp;&nbsp;&nbsp;$5, $6::NUMBER(18,3), $7::NUMBER(18,3),<br>
              &nbsp;&nbsp;&nbsp;&nbsp;$8, $9::NUMBER(12,6), $10<br>
              &nbsp;&nbsp;FROM @MITSUI_STAGE/cust_trade_detail.csv.gz<br>
              )<br>
              FILE_FORMAT = (FORMAT_NAME = 'CSV_GZ_FORMAT')<br>
              ON_ERROR = 'ABORT_STATEMENT';
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #C084FC;">🔥</span>
              <div><strong style="color: #FFFFFF;">全 9 极限数值压测 (Stress Test)</strong>：<br>包含 15 位整数持仓股数 <code>999999999999999</code> 与千兆日元厘级小数，经受住极端压测，全量成功入盘！</div>
            </div>
          </div>
          <!-- Real Screenshot in Window Console Frame -->
          <div class="window-frame">
            <div class="window-header">
              <div class="window-dots">
                <span class="window-dot dot-red"></span>
                <span class="window-dot dot-yellow"></span>
                <span class="window-dot dot-green"></span>
              </div>
              <div class="window-title">Snowsight · COPY INTO CUST_TRADE_DETAIL Result [Step 05]</div>
              <span class="window-tag">STATUS: LOADED (11 ROWS)</span>
            </div>
            <div class="window-content">
              <img src="../assets/images/04_step_05_copy_trade.png" alt="Snowsight Step 05 COPY INTO CUST_TRADE_DETAIL Result">
            </div>
          </div>
        </div>
        """
        html3 = generate_scene_html("scene3", s3["start_time"], s3["duration"], badge_label,
            "交易事实表装载与全 9 极限数值压测", "Trade Fact Table Batch Load & Extreme Stress Testing", "STRESS TEST", c3, s3["script"], "zh-CN")

        # S4: Real Screenshot 04_step_06_copy_history.png
        c4 = """
        <div class="grid-2col">
          <div class="glass-card" style="border-color: rgba(56, 189, 248, 0.45);">
            <div class="card-header">
              <div class="card-title" style="color: #38BDF8;">🔍 合规审计追踪：COPY_HISTORY (Step 06)</div>
              <span class="card-badge" style="background: rgba(56, 189, 248, 0.15); color: #38BDF8; border: 1px solid rgba(56, 189, 248, 0.4);">INFORMATION SCHEMA</span>
            </div>
            <div class="code-box">
              SELECT<br>
              &nbsp;&nbsp;FILE_NAME, STATUS, ROW_PARSED, ROW_LOADED, ERROR_COUNT<br>
              FROM TABLE(<br>
              &nbsp;&nbsp;INFORMATION_SCHEMA.COPY_HISTORY(<br>
              &nbsp;&nbsp;&nbsp;&nbsp;TABLE_NAME => 'CUST_TRADE_DETAIL',<br>
              &nbsp;&nbsp;&nbsp;&nbsp;START_TIME => DATEADD(hours, -24, CURRENT_TIMESTAMP())<br>
              &nbsp;&nbsp;)<br>
              );
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #34D399;">✔</span>
              <div><strong style="color: #FFFFFF;">机器级合规执行凭证</strong>：内置不可篡改日志，清晰记录 24 小时执行历史，满足外部监管对金融机构数据上云的机器不可篡改溯源要求。</div>
            </div>
          </div>
          <!-- Real Screenshot in Window Console Frame -->
          <div class="window-frame">
            <div class="window-header">
              <div class="window-dots">
                <span class="window-dot dot-red"></span>
                <span class="window-dot dot-yellow"></span>
                <span class="window-dot dot-green"></span>
              </div>
              <div class="window-title">Snowsight · COPY_HISTORY Audit Trace [Step 06]</div>
              <span class="window-tag">STATUS: LOADED · ERRORS: 0</span>
            </div>
            <div class="window-content">
              <img src="../assets/images/04_step_06_copy_history.png" alt="Snowsight Step 06 COPY_HISTORY Audit Trace">
            </div>
          </div>
        </div>
        """
        html4 = generate_scene_html("scene4", s4["start_time"], s4["duration"], badge_label,
            "合规入云审计追踪：COPY_HISTORY 任务留痕", "Compliance Ingestion Audit: COPY_HISTORY Execution Tracing", "AUDIT TRAIL", c4, s4["script"], "zh-CN")

    else:
        # JA Ep3
        c1 = """
        <div class="grid-2col">
          <div class="glass-card" style="border-color: rgba(56, 189, 248, 0.45);">
            <div class="card-header">
              <div class="card-title" style="color: #38BDF8;">📦 顧客マスタ一括ロード (Step 04)</div>
              <span class="card-badge" style="background: rgba(56, 189, 248, 0.15); color: #38BDF8; border: 1px solid rgba(56, 189, 248, 0.4);">COPY INTO MASTER</span>
            </div>
            <div class="code-box">
              COPY INTO CUST_MASTER (<br>
              &nbsp;&nbsp;CUST_ID, CUST_TYPE, CUST_NAME,<br>
              &nbsp;&nbsp;BRANCH_CODE, RISK_RANK, STATUS, OPEN_DATE<br>
              )<br>
              FROM (<br>
              &nbsp;&nbsp;SELECT $1, $2, $3, $4, $5, $6, TO_DATE($7, 'YYYYMMDD')<br>
              &nbsp;&nbsp;FROM @MITSUI_STAGE/cust_master.csv.gz<br>
              )<br>
              FILE_FORMAT = (FORMAT_NAME = 'CSV_GZ_FORMAT')<br>
              ON_ERROR = 'ABORT_STATEMENT';
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #34D399;">✔</span>
              <div><strong style="color: #FFFFFF;">対象パスの厳密指定</strong>：<code>cust_master.csv.gz</code> を明示し、他ファイル混入を防止。</div>
            </div>
          </div>
          <div class="glass-card" style="border-color: rgba(52, 211, 153, 0.45);">
            <div class="card-header">
              <div class="card-title" style="color: #34D399;">🛡️ マスタスキーマ定義とマッピング規約</div>
              <span class="card-badge" style="background: rgba(52, 211, 153, 0.15); color: #34D399; border: 1px solid rgba(52, 211, 153, 0.4);">DATA SCHEMA</span>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #38BDF8;">1</span>
              <div><code>CUST_ID</code>: 顧客ID (主キー制約に準拠した10桁整数)</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #34D399;">2</span>
              <div><code>CUST_NAME</code>: 氏名 (マルチバイト和文・全角文字を無欠損で格納)</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #FBBF24;">3</span>
              <div><code>RISK_RANK</code>: リスク等級 (A/B/C/D コンプライアンス区分)</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #C084FC;">4</span>
              <div><code>OPEN_DATE</code>: 開設日 (標準 <code>DATE</code> 型への完全キャスト)</div>
            </div>
          </div>
        </div>
        """
        html1 = generate_scene_html("scene1", s1["start_time"], s1["duration"], badge_label,
            "顧客ディメンションマスタ一括 COPY INTO ロード", "Customer Master COPY INTO Batch Ingestion", "BATCH INGESTION", c1, s1["script"], "ja")

        c2 = """
        <div class="grid-2col">
          <div class="glass-card" style="border-color: rgba(248, 113, 113, 0.45);">
            <div class="card-header">
              <div class="card-title" style="color: #F87171;">🛑 厳格ロールバックと監査列補完</div>
              <span class="card-badge" style="background: rgba(248, 113, 113, 0.15); color: #F87171; border: 1px solid rgba(248, 113, 113, 0.4);">TRANSACTION INTEGRITY</span>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #F87171;">★</span>
              <div><strong style="color: #FFFFFF;">ON_ERROR = 'ABORT_STATEMENT'</strong>：<br>金融機関の厳格な ACID 要件に基づき、1行でも不正があれば全トランザクションを即座に破棄。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #34D399;">★</span>
              <div><strong style="color: #FFFFFF;">MIGRATED_AT の自動生成</strong>：<br><code>DEFAULT CURRENT_TIMESTAMP()</code> により、クラウド格納時刻をマイクロ秒単位で正確に自動記録。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #38BDF8;">✔</span>
              <div><strong style="color: #FFFFFF;">マスタ投入完了</strong>：13 件の顧客データが全件投入成功、エラーはゼロ！</div>
            </div>
          </div>
          <!-- Real Screenshot in Window Console Frame -->
          <div class="window-frame">
            <div class="window-header">
              <div class="window-dots">
                <span class="window-dot dot-red"></span>
                <span class="window-dot dot-yellow"></span>
                <span class="window-dot dot-green"></span>
              </div>
              <div class="window-title">Snowsight · COPY INTO CUST_MASTER Result [Step 04]</div>
              <span class="window-tag">STATUS: LOADED (13 ROWS)</span>
            </div>
            <div class="window-content">
              <img src="../assets/images/04_step_04_copy_master.png" alt="Snowsight Step 04 COPY INTO CUST_MASTER Result">
            </div>
          </div>
        </div>
        """
        html2 = generate_scene_html("scene2", s2["start_time"], s2["duration"], badge_label,
            "強整合性ロールバック ON_ERROR と入雲監査列", "ACID Rollback ON_ERROR & Ingestion Timestamp Auditing", "ACID COMPLIANCE", c2, s2["script"], "ja")

        c3 = """
        <div class="grid-2col">
          <div class="glass-card" style="border-color: rgba(56, 189, 248, 0.45);">
            <div class="card-header">
              <div class="card-title" style="color: #38BDF8;">📈 取引ファクト明細 CUST_TRADE_DETAIL ロード</div>
              <span class="card-badge" style="background: rgba(56, 189, 248, 0.15); color: #38BDF8; border: 1px solid rgba(56, 189, 248, 0.4);">TRADE FACT LOAD</span>
            </div>
            <div class="code-box">
              COPY INTO CUST_TRADE_DETAIL FROM (<br>
              &nbsp;&nbsp;SELECT $1, $2, $3, TO_DATE($4, 'YYYYMMDD'),<br>
              &nbsp;&nbsp;&nbsp;&nbsp;$5, $6::NUMBER(18,3), $7::NUMBER(18,3),<br>
              &nbsp;&nbsp;&nbsp;&nbsp;$8, $9::NUMBER(12,6), $10<br>
              &nbsp;&nbsp;FROM @MITSUI_STAGE/cust_trade_detail.csv.gz<br>
              )<br>
              FILE_FORMAT = (FORMAT_NAME = 'CSV_GZ_FORMAT')<br>
              ON_ERROR = 'ABORT_STATEMENT';
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #C084FC;">🔥</span>
              <div><strong style="color: #FFFFFF;">全9極限ストレステスト突破</strong>：<br>15桁整数数量 <code>999999999999999</code> および 1000兆円超の約定代金を固定小数点精度で完全格納！</div>
            </div>
          </div>
          <!-- Real Screenshot in Window Console Frame -->
          <div class="window-frame">
            <div class="window-header">
              <div class="window-dots">
                <span class="window-dot dot-red"></span>
                <span class="window-dot dot-yellow"></span>
                <span class="window-dot dot-green"></span>
              </div>
              <div class="window-title">Snowsight · COPY INTO CUST_TRADE_DETAIL Result [Step 05]</div>
              <span class="window-tag">STATUS: LOADED (11 ROWS)</span>
            </div>
            <div class="window-content">
              <img src="../assets/images/04_step_05_copy_trade.png" alt="Snowsight Step 05 COPY INTO CUST_TRADE_DETAIL Result">
            </div>
          </div>
        </div>
        """
        html3 = generate_scene_html("scene3", s3["start_time"], s3["duration"], badge_label,
            "取引ファクト明細ロードと全9極限値ストレステスト", "Trade Fact Table Batch Load & Extreme Stress Testing", "STRESS TEST", c3, s3["script"], "ja")

        c4 = """
        <div class="grid-2col">
          <div class="glass-card" style="border-color: rgba(56, 189, 248, 0.45);">
            <div class="card-header">
              <div class="card-title" style="color: #38BDF8;">🔍 入雲監査追跡：COPY_HISTORY (Step 06)</div>
              <span class="card-badge" style="background: rgba(56, 189, 248, 0.15); color: #38BDF8; border: 1px solid rgba(56, 189, 248, 0.4);">INFORMATION SCHEMA</span>
            </div>
            <div class="code-box">
              SELECT<br>
              &nbsp;&nbsp;FILE_NAME, STATUS, ROW_PARSED, ROW_LOADED, ERROR_COUNT<br>
              FROM TABLE(<br>
              &nbsp;&nbsp;INFORMATION_SCHEMA.COPY_HISTORY(<br>
              &nbsp;&nbsp;&nbsp;&nbsp;TABLE_NAME => 'CUST_TRADE_DETAIL',<br>
              &nbsp;&nbsp;&nbsp;&nbsp;START_TIME => DATEADD(hours, -24, CURRENT_TIMESTAMP())<br>
              &nbsp;&nbsp;)<br>
              );
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #34D399;">✔</span>
              <div><strong style="color: #FFFFFF;">電磁的記録と法的監査エビデンス</strong>：直近24時間の実行履歴を取得。ステータスが LOADED、解析行数と格納行数が完全一致、エラー件数ゼロを立証。</div>
            </div>
          </div>
          <!-- Real Screenshot in Window Console Frame -->
          <div class="window-frame">
            <div class="window-header">
              <div class="window-dots">
                <span class="window-dot dot-red"></span>
                <span class="window-dot dot-yellow"></span>
                <span class="window-dot dot-green"></span>
              </div>
              <div class="window-title">Snowsight · COPY_HISTORY Audit Trace [Step 06]</div>
              <span class="window-tag">STATUS: LOADED · ERRORS: 0</span>
            </div>
            <div class="window-content">
              <img src="../assets/images/04_step_06_copy_history.png" alt="Snowsight Step 06 COPY_HISTORY Audit Trace">
            </div>
          </div>
        </div>
        """
        html4 = generate_scene_html("scene4", s4["start_time"], s4["duration"], badge_label,
            "入雲監査追跡：COPY_HISTORY 実行ログの確立", "Compliance Ingestion Audit: COPY_HISTORY Execution Tracing", "AUDIT TRAIL", c4, s4["script"], "ja")

    with open(os.path.join(comp_dir, "scene1.html"), "w", encoding="utf-8") as f:
        f.write(html1)
    with open(os.path.join(comp_dir, "scene2.html"), "w", encoding="utf-8") as f:
        f.write(html2)
    with open(os.path.join(comp_dir, "scene3.html"), "w", encoding="utf-8") as f:
        f.write(html3)
    with open(os.path.join(comp_dir, "scene4.html"), "w", encoding="utf-8") as f:
        f.write(html4)

# =========================================================================
# EPISODE 4
# =========================================================================
def build_ep4_scenes(comp_dir, lang, badge_label, s1, s2, s3, s4):
    if lang == "zh":
        # S1: SoD principle & Framework
        c1 = """
        <div class="grid-2col">
          <div class="glass-card" style="border-color: rgba(56, 189, 248, 0.45);">
            <div class="card-header">
              <div class="card-title" style="color: #38BDF8;">🏛️ 独立审计原则与角色切换 (Step 07)</div>
              <span class="card-badge" style="background: rgba(56, 189, 248, 0.15); color: #38BDF8; border: 1px solid rgba(56, 189, 248, 0.4);">SOD AUDITING</span>
            </div>
            <div class="code-box">
              USE ROLE MITSUI_ANALYST;<br>
              USE WAREHOUSE MITSUI_WH;<br>
              USE DATABASE MITSUI_SEC_DB;<br>
              USE SCHEMA RAW_ORACLE;
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #F87171;">!</span>
              <div><strong style="color: #FFFFFF;">避免“自己审计自己”</strong>：负责写入的 <code>MITSUI_ENGINEER</code> 严禁兼任验收，杜绝修改数据掩盖错误。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #34D399;">!</span>
              <div><strong style="color: #FFFFFF;">只读独立核验视角</strong>：<code>MITSUI_ANALYST</code> 仅拥有受控读取特权，专职跨系统数据突合。</div>
            </div>
          </div>
          <div class="glass-card" style="border-color: rgba(52, 211, 153, 0.45);">
            <div class="card-header">
              <div class="card-title" style="color: #34D399;">📐 四重金融跨系统数据突合框架</div>
              <span class="card-badge" style="background: rgba(52, 211, 153, 0.15); color: #34D399; border: 1px solid rgba(52, 211, 153, 0.4);">RECON FRAMEWORK</span>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #38BDF8;">1</span>
              <div><strong style="color: #FFFFFF;">第一重：双表总行数对齐</strong>：主表与明细表记录数 1:1 无损对齐，差额恒为 0。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #34D399;">2</span>
              <div><strong style="color: #FFFFFF;">第二重：千兆金额与期日边界</strong>：股数与金额汇总体量完全契合，误差 0.000。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #FBBF24;">3</span>
              <div><strong style="color: #FFFFFF;">第三重：多币种分类交叉矩阵</strong>：JPY / USD / EUR 交叉验证，消除分类偏斜。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #C084FC;">4</span>
              <div><strong style="color: #FFFFFF;">第四重：HASH_AGG 全局防篡改指纹</strong>：全表全字段哈希对齐，提供不可伪造证明。</div>
            </div>
          </div>
        </div>
        """
        html1 = generate_scene_html("scene1", s1["start_time"], s1["duration"], badge_label,
            "独立分析师视角：四重金融突合框架建立", "Independent Analyst Perspective: 4-Tier Financial Reconciliation", "SOD AUDITING", c1, s1["script"], "zh-CN")

        # S2: Dual Real Screenshots: 04_step_07_08 (Row counts) & 04_step_09 (Financial aggregates)
        c2 = """
        <div class="grid-2col-equal">
          <div class="window-frame">
            <div class="window-header">
              <div class="window-dots">
                <span class="window-dot dot-red"></span>
                <span class="window-dot dot-yellow"></span>
                <span class="window-dot dot-green"></span>
              </div>
              <div class="window-title">第 1 重：双表总记录数突合 [Step 07 & 08]</div>
              <span class="window-tag" style="color: #34D399;">Δ = 0 (100% 对齐)</span>
            </div>
            <div class="window-content">
              <img src="../assets/images/04_step_07_08_reconciliation_count.png" alt="Step 07 & 08 Row Count Reconciliation">
            </div>
          </div>
          <div class="window-frame">
            <div class="window-header">
              <div class="window-dots">
                <span class="window-dot dot-red"></span>
                <span class="window-dot dot-yellow"></span>
                <span class="window-dot dot-green"></span>
              </div>
              <div class="window-title">第 2 重：千兆金额与期日边界突合 [Step 09]</div>
              <span class="window-tag" style="color: #38BDF8;">差额 0.000 绝对无损</span>
            </div>
            <div class="window-content">
              <img src="../assets/images/04_step_09_financial_reconciliation.png" alt="Step 09 Financial Reconciliation">
            </div>
          </div>
        </div>
        """
        html2 = generate_scene_html("scene2", s2["start_time"], s2["duration"], badge_label,
            "第一重总行数与第二重金额指标突合", "Tier 1 Row Counts & Tier 2 Financial Aggregations & Boundary", "RECON TIER 1 & 2", c2, s2["script"], "zh-CN")

        # S3: Dual Real Screenshots: 04_step_10 (Currency & Hash) & 05_step_05_winmerge_trade_diff.png
        c3 = """
        <div class="grid-2col-equal">
          <div class="window-frame">
            <div class="window-header">
              <div class="window-dots">
                <span class="window-dot dot-red"></span>
                <span class="window-dot dot-yellow"></span>
                <span class="window-dot dot-green"></span>
              </div>
              <div class="window-title">第 3 & 4 重：币种分布与全局哈希指纹 [Step 10]</div>
              <span class="window-tag" style="color: #C084FC;">HASH_AGG: 64-BIT MATCH</span>
            </div>
            <div class="window-content">
              <img src="../assets/images/04_step_10_hash_and_currency.png" alt="Step 10 Hash and Currency Verification">
            </div>
          </div>
          <div class="window-frame">
            <div class="window-header">
              <div class="window-dots">
                <span class="window-dot dot-red"></span>
                <span class="window-dot dot-yellow"></span>
                <span class="window-dot dot-green"></span>
              </div>
              <div class="window-title">WinMerge · Oracle vs Snowflake 跨系统逐行核验</div>
              <span class="window-tag" style="color: #34D399;">0 DIFFERENCES DETECTED</span>
            </div>
            <div class="window-content">
              <img src="../assets/images/05_step_05_winmerge_trade_diff.png" alt="WinMerge Trade Detail Diff Result">
            </div>
          </div>
        </div>
        """
        html3 = generate_scene_html("scene3", s3["start_time"], s3["duration"], badge_label,
            "第三重多币种交叉矩阵与第四重 HASH_AGG 指纹", "Tier 3 Cross Currency Matrix & Tier 4 HASH_AGG Tamper-Proof Fingerprint", "RECON TIER 3 & 4", c3, s3["script"], "zh-CN")

        # S4: Full Lifecycle Summary
        c4 = """
        <div class="grid-2col">
          <div class="glass-card" style="border-color: rgba(52, 211, 153, 0.45);">
            <div class="card-header">
              <div class="card-title" style="color: #34D399;">🏁 第五章端到端迁移全流程闭环</div>
              <span class="card-badge" style="background: rgba(52, 211, 153, 0.15); color: #34D399; border: 1px solid rgba(52, 211, 153, 0.4);">FULL LIFECYCLE</span>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #38BDF8;">1</span>
              <div><strong style="color: #FFFFFF;">源端治理</strong>：UTF-8 无 BOM、双引号转义、空串标准化、Gzip 压缩。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #34D399;">2</span>
              <div><strong style="color: #FFFFFF;">受控暂存</strong>：MITSUI_STAGE 落地，PUT 客户端零计算成本传输。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #FBBF24;">3</span>
              <div><strong style="color: #FFFFFF;">零失败预检</strong>：Stage 无表直接投影试跑，排查子查询陷阱。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #C084FC;">4</span>
              <div><strong style="color: #FFFFFF;">生产入库</strong>：COPY INTO 批量装载，全 9 极限压测，四重突合审计。</div>
            </div>
          </div>
          <div class="glass-card" style="border-color: rgba(56, 189, 248, 0.45);">
            <div class="card-header">
              <div class="card-title" style="color: #38BDF8;">📜 三井证券云端湖仓投产就绪签署</div>
              <span class="card-badge" style="background: rgba(56, 189, 248, 0.15); color: #38BDF8; border: 1px solid rgba(56, 189, 248, 0.4);">PRODUCTION READY</span>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #34D399;">✔</span>
              <div><strong style="color: #FFFFFF;">数据质量 100% 达标</strong>：核心业务数据完整入库，无丢失无失真。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #38BDF8;">✔</span>
              <div><strong style="color: #FFFFFF;">金融监管 100% 合规</strong>：权限隔离清晰，具备不可篡改审计追踪。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #FBBF24;">✔</span>
              <div><strong style="color: #FFFFFF;">下一章预告</strong>：第六章将正式开启增量同步 Streams & Tasks 自动化流水线！</div>
            </div>
          </div>
        </div>
        """
        html4 = generate_scene_html("scene4", s4["start_time"], s4["duration"], badge_label,
            "全链路闭环与三井证券云端湖仓投产就绪", "End-to-End Pipeline Closed & Mitsui Securities Lakehouse Production Ready", "PRODUCTION READY", c4, s4["script"], "zh-CN")

    else:
        # JA Ep4
        c1 = """
        <div class="grid-2col">
          <div class="glass-card" style="border-color: rgba(56, 189, 248, 0.45);">
            <div class="card-header">
              <div class="card-title" style="color: #38BDF8;">🏛️ 独立監査の原則とロール切替 (Step 07)</div>
              <span class="card-badge" style="background: rgba(56, 189, 248, 0.15); color: #38BDF8; border: 1px solid rgba(56, 189, 248, 0.4);">SOD AUDITING</span>
            </div>
            <div class="code-box">
              USE ROLE MITSUI_ANALYST;<br>
              USE WAREHOUSE MITSUI_WH;<br>
              USE DATABASE MITSUI_SEC_DB;<br>
              USE SCHEMA RAW_ORACLE;
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #F87171;">!</span>
              <div><strong style="color: #FFFFFF;">自己監査の厳禁</strong>：書込権限を持つ <code>MITSUI_ENGINEER</code> による受入完了判定を排除し、改ざんを防止。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #34D399;">!</span>
              <div><strong style="color: #FFFFFF;">読取専用の独立検証</strong>：<code>MITSUI_ANALYST</code> の認可スコープに限定し、客観的な新旧データ突合を実施。</div>
            </div>
          </div>
          <div class="glass-card" style="border-color: rgba(52, 211, 153, 0.45);">
            <div class="card-header">
              <div class="card-title" style="color: #34D399;">📐 四重新旧データ突合検証フレームワーク</div>
              <span class="card-badge" style="background: rgba(52, 211, 153, 0.15); color: #34D399; border: 1px solid rgba(52, 211, 153, 0.4);">RECON FRAMEWORK</span>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #38BDF8;">1</span>
              <div><strong style="color: #FFFFFF;">第１重：総件数突合</strong>：マスタおよび明細のレコード件数が差分ゼロで一致。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #34D399;">2</span>
              <div><strong style="color: #FFFFFF;">第２重：千兆円規模の集計値突合</strong>：数量・金額・約定日境界の完全無欠落を証明。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #FBBF24;">3</span>
              <div><strong style="color: #FFFFFF;">第３重：通貨別クロス集計</strong>：JPY / USD / EUR の区分ズレを完全に排除。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #C084FC;">4</span>
              <div><strong style="color: #FFFFFF;">第４重：HASH_AGG 全件ハッシュ指紋</strong>：全列ハッシュによる改ざん不可能性を立証。</div>
            </div>
          </div>
        </div>
        """
        html1 = generate_scene_html("scene1", s1["start_time"], s1["duration"], badge_label,
            "独立アナリスト視点：四重突合検証フレームワーク", "Independent Analyst Perspective: 4-Tier Reconciliation", "SOD AUDITING", c1, s1["script"], "ja")

        c2 = """
        <div class="grid-2col-equal">
          <div class="window-frame">
            <div class="window-header">
              <div class="window-dots">
                <span class="window-dot dot-red"></span>
                <span class="window-dot dot-yellow"></span>
                <span class="window-dot dot-green"></span>
              </div>
              <div class="window-title">第１重：両テーブル総件数突合 [Step 07 & 08]</div>
              <span class="window-tag" style="color: #34D399;">差分 Δ = 0 (100% 符号)</span>
            </div>
            <div class="window-content">
              <img src="../assets/images/04_step_07_08_reconciliation_count.png" alt="Step 07 & 08 Row Count Reconciliation">
            </div>
          </div>
          <div class="window-frame">
            <div class="window-header">
              <div class="window-dots">
                <span class="window-dot dot-red"></span>
                <span class="window-dot dot-yellow"></span>
                <span class="window-dot dot-green"></span>
              </div>
              <div class="window-title">第２重：金額集計と日付境界突合 [Step 09]</div>
              <span class="window-tag" style="color: #38BDF8;">誤差 0.000 絶対無損</span>
            </div>
            <div class="window-content">
              <img src="../assets/images/04_step_09_financial_reconciliation.png" alt="Step 09 Financial Reconciliation">
            </div>
          </div>
        </div>
        """
        html2 = generate_scene_html("scene2", s2["start_time"], s2["duration"], badge_label,
            "第１段階総件数と第２段階金額・数量突合", "Tier 1 Row Counts & Tier 2 Financial Aggregations & Boundary", "RECON TIER 1 & 2", c2, s2["script"], "ja")

        c3 = """
        <div class="grid-2col-equal">
          <div class="window-frame">
            <div class="window-header">
              <div class="window-dots">
                <span class="window-dot dot-red"></span>
                <span class="window-dot dot-yellow"></span>
                <span class="window-dot dot-green"></span>
              </div>
              <div class="window-title">第３＆４重：通貨別分布とグローバルハッシュ指紋 [Step 10]</div>
              <span class="window-tag" style="color: #C084FC;">HASH_AGG: 64-BIT MATCH</span>
            </div>
            <div class="window-content">
              <img src="../assets/images/04_step_10_hash_and_currency.png" alt="Step 10 Hash and Currency Verification">
            </div>
          </div>
          <div class="window-frame">
            <div class="window-header">
              <div class="window-dots">
                <span class="window-dot dot-red"></span>
                <span class="window-dot dot-yellow"></span>
                <span class="window-dot dot-green"></span>
              </div>
              <div class="window-title">WinMerge · Oracle vs Snowflake 新旧データ突合検証</div>
              <span class="window-tag" style="color: #34D399;">0 DIFFERENCES DETECTED</span>
            </div>
            <div class="window-content">
              <img src="../assets/images/05_step_05_winmerge_trade_diff.png" alt="WinMerge Trade Detail Diff Result">
            </div>
          </div>
        </div>
        """
        html3 = generate_scene_html("scene3", s3["start_time"], s3["duration"], badge_label,
            "第３重通貨別クロス集計と第４重 HASH_AGG 指紋", "Tier 3 Cross Currency Matrix & Tier 4 HASH_AGG Tamper-Proof Fingerprint", "RECON TIER 3 & 4", c3, s3["script"], "ja")

        c4 = """
        <div class="grid-2col">
          <div class="glass-card" style="border-color: rgba(52, 211, 153, 0.45);">
            <div class="card-header">
              <div class="card-title" style="color: #34D399;">🏁 第５章データ移行全ライフサイクル完遂</div>
              <span class="card-badge" style="background: rgba(52, 211, 153, 0.15); color: #34D399; border: 1px solid rgba(52, 211, 153, 0.4);">FULL LIFECYCLE</span>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #38BDF8;">1</span>
              <div><strong style="color: #FFFFFF;">ソース側規約</strong>：BOMなし UTF-8、引用符エスケープ、空文字NULL化、Gzip圧縮。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #34D399;">2</span>
              <div><strong style="color: #FFFFFF;">受領ステージ</strong>：MITSUI_STAGE、PUT クライアント暗号化で計算コストゼロ転送。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #FBBF24;">3</span>
              <div><strong style="color: #FFFFFF;">事前検証</strong>：ステージ直接射影プレビューによりサブクエリ制約を回避。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #C084FC;">4</span>
              <div><strong style="color: #FFFFFF;">本番投入</strong>：COPY INTO 一括ロード、極限値テスト、四重の厳格突合監査。</div>
            </div>
          </div>
          <div class="glass-card" style="border-color: rgba(56, 189, 248, 0.45);">
            <div class="card-header">
              <div class="card-title" style="color: #38BDF8;">📜 三井証券クラウドレイクハウス本番稼働認可</div>
              <span class="card-badge" style="background: rgba(56, 189, 248, 0.15); color: #38BDF8; border: 1px solid rgba(56, 189, 248, 0.4);">PRODUCTION READY</span>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #34D399;">✔</span>
              <div><strong style="color: #FFFFFF;">データ品質 100% 達成</strong>：重要取引データが完全無欠落・無歪みで入雲。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #38BDF8;">✔</span>
              <div><strong style="color: #FFFFFF;">内部統制・監査 100% 準拠</strong>：職務分掌と電磁的ログ追跡性を確立。</div>
            </div>
            <div class="info-row">
              <span class="info-bullet" style="color: #FBBF24;">✔</span>
              <div><strong style="color: #FFFFFF;">次回予告</strong>：第６章では Streams & Tasks による準リアルタイム差分同期へ進みます！</div>
            </div>
          </div>
        </div>
        """
        html4 = generate_scene_html("scene4", s4["start_time"], s4["duration"], badge_label,
            "全パイプライン完遂と三井証券クラウド本番稼働", "End-to-End Pipeline Closed & Mitsui Securities Lakehouse Production Ready", "PRODUCTION READY", c4, s4["script"], "ja")

    with open(os.path.join(comp_dir, "scene1.html"), "w", encoding="utf-8") as f:
        f.write(html1)
    with open(os.path.join(comp_dir, "scene2.html"), "w", encoding="utf-8") as f:
        f.write(html2)
    with open(os.path.join(comp_dir, "scene3.html"), "w", encoding="utf-8") as f:
        f.write(html3)
    with open(os.path.join(comp_dir, "scene4.html"), "w", encoding="utf-8") as f:
        f.write(html4)

if __name__ == "__main__":
    build_all_compositions()
    print("All Chapter 5 screenshot-enhanced compositions built successfully!")
