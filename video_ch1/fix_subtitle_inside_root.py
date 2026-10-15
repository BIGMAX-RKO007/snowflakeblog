import os
import re

COMP_DIR = r"C:\Users\FX\Projects\SnowflakeBlog\video_ch1\compositions"

ACT_SUBTITLES = {
    "act1": "🎙️ 欢迎来到第一章：业务背景、总体架构设计与成本测算模型。传统券商面临本地 Oracle 扩容瓶颈、多租户职责分离与日本金融厅 (FSA) 监管合规的三重数字化转型挑战。",
    "act2": "🎙️ 第二节：深入剖析 Snowflake 现代云原生三大技术底座——存储与计算彻底解耦、全自动列式微分区剪枝机制，以及时间旅行与零拷贝即时克隆。",
    "act3": "🎙️ 第三节：深入解析核心计费体系与月度成本测算模型。算力(Credit)、存储与跨区传输三维拆解，初期业务规模测算月度运营成本仅约 $508，配合自动挂起实现成本最优化。",
    "act4": "🎙️ 第四节：总体数据迁移架构与端到端数据流设计。本地 Oracle 抽取并块压缩，经 TLS 1.3 上传至内部暂存区 MITSUI_STAGE，专用计算仓库执行 COPY INTO 高速并行入库。",
    "act5": "🎙️ 第五节：核心表结构映射与八大类型推测规范。本外币金额规范、业务日期字符串设计、TIMESTAMP_NTZ(6) 审计时间戳，筑牢两方数据 100% 严密对账基石。",
    "act6": "🎙️ 第六节：Snowflake 核心受控对象体系与参数继承架构。十六大金融对象矩阵精细管控，会话级、用户级与账户级参数自顶向下逐级继承与动态覆盖。",
    "act7": "🎙️ 第七节：金融级三位一体高可用与容灾架构。时间旅行原生自愈误操作，安全网作为底座最后防线，配合零拷贝克隆实现毫秒级沙箱演练与割接备份。"
}

for act_id, subtitle_text in ACT_SUBTITLES.items():
    file_path = os.path.join(COMP_DIR, f"{act_id}.html")
    if not os.path.exists(file_path):
        continue
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Remove any existing subtitle-bar
    content = re.sub(r'<div data-hf-id="[^"]*" class="subtitle-bar">[\s\S]*?</div>\s*', '', content)
    
    # Also clean up trailing </div> before <script>
    # In each file, before <script>, there were multiple </div> tags
    # Let's see: split by <script>
    parts = content.split("<script>")
    if len(parts) != 2:
        print(f"Skipping {act_id}, unexpected <script> split")
        continue
        
    html_body = parts[0].rstrip()
    script_part = "<script>" + parts[1]
    
    # html_body ends with some </div></div>...
    # The last </div> closes #root
    # We want to insert the subtitle BEFORE that last </div>!
    last_div_idx = html_body.rfind("</div>")
    if last_div_idx == -1:
        print(f"Skipping {act_id}, no closing div")
        continue
        
    before_last_div = html_body[:last_div_idx].rstrip()
    last_div = html_body[last_div_idx:]
    
    subtitle_html = f'''\n  <!-- Subtitle Bar inside #root -->
  <div data-hf-id="hf-sub-{act_id}" class="subtitle-bar">
    <span data-hf-id="hf-sub-icon-{act_id}" class="subtitle-icon">🎙️</span>
    <span data-hf-id="hf-sub-txt-{act_id}" class="subtitle-text">{subtitle_text.replace("🎙️ ", "")}</span>
  </div>\n'''
  
    new_content = before_last_div + subtitle_html + last_div + "\n  " + script_part
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"Successfully placed subtitle INSIDE #root for {act_id}.html")

print("Finished fixing subtitles inside #root.")
