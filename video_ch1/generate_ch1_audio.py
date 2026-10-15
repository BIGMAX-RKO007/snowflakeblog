import os
import sys
import json
import time
import subprocess
from gtts import gTTS
import soundfile as sf
import numpy as np

FFMPEG_EXE = r"C:\Users\FX\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin\ffmpeg.exe"

OUTPUT_DIR = r"C:\Users\FX\Projects\SnowflakeBlog\video_ch1\audio"
MANIFEST_PATH = r"C:\Users\FX\Projects\SnowflakeBlog\video_ch1\audio\manifest.json"

ACTS_SCRIPTS = {
    "act1": (
        "欢迎来到第一章：业务背景、总体架构设计与成本测算模型。"
        "首先我们来看业务背景。作为传统老牌金融机构，证券业务正面临严峻的数字化转型诉求。"
        "第一个挑战是本地数据库的扩容瓶颈。随着高频量化交易与多品种投资业务的爆发式增长，"
        "原有基于本地 Oracle 11g 数据库的传统单机架构在算力与存储双双遭遇瓶颈，夜间大批量报表汇总耗时漫长，严重挤占白天的交易处理窗口。"
        "第二个挑战是多租户与合规隔离诉求。在金融监管框架下，项目系统管理员、数据工程师与业务量化分析师对数据的访问权责必须严格分离，"
        "急需构建一套存算分离、秒级弹性扩缩容、成本透明可审计的现代化数据基盘。"
        "第三个挑战是金融级合规底座。上云过程必须严格遵循日本金融厅 FSA 的监管合规要求，确保数据无条件驻留在东京本地机房，"
        "全链路具备细粒度的三层 RBAC 权限隔离、不可篡改的时间旅行数据回溯以及不可抹除的操作审计日志。"
    ),
    "act2": (
        "第二节，让我们深入剖析 Snowflake 的产品架构与核心技术底座。"
        "Snowflake 是一套真正的云原生数据云平台，其卓越的弹性伸缩与超高速查询能力源自三大核心技术支柱。"
        "第一大支柱：存储与计算的彻底解耦。在传统架构中，加硬盘必须扩算力，扩算力必须绑存储。"
        "而在 Snowflake 架构中，底层的持久化存储完全依托云端高可用对象存储，而上层的 SQL 解析与执行引擎由独立的虚拟计算仓库担当。"
        "各业务线可根据波峰波谷独立秒级启动或停机，计算算力按需付费，实现金融级成本最优化。"
        "第二大支柱：自动微分区机制。底层数据在写入时全自动按列切分为细粒度的微分区，每个分区仅包含五十到五百兆未压缩数据。"
        "这彻底告别了传统数据库繁杂的物理索引、分区键和碎片整理维护，系统自动收集列元数据，并在点查时实现十倍以上的快速剪枝。"
        "第三大支柱：时间旅行与零拷贝克隆。历史数据快照原生受保，业务误操作可毫秒级回溯复原；配合零拷贝克隆技术，无需复制物理数据即可秒级克隆生产数据集供沙箱演练。"
    ),
    "act3": (
        "第三节，深入解析核心计费体系与月度成本测算模型。"
        "Snowflake 采用高度弹性的按实际用量计费模型，核心成本由三大要素构成。"
        "第一要素是计算资源。使用虚拟仓库执行 SQL、跑批或数据加载时消耗算力点数 Credit。换算基准是 XS 规格运行一小时消耗正好一个点数。"
        "计算资源通常占据总账单的百分之七十到八十。单价由云厂商 AWS、东京可用区以及企业版软件版本交叉确定，当前东京区企业版参考单价约为五点七美元每点数。"
        "第二要素是存储资源。针对加载入库并经高倍率压缩后的实际数据体积按每月每太字节计费，基准单价约为二十五美元每太字节。"
        "第三要素是数据传输资源。跨不同云厂商或跨地域向异地容灾备份机房传输归档时产生网络外发流量，基准约为九十美元每太字节。"
        "基于此，我们建立生产级月度成本测算模型。在初期迁移环境下，假设虚拟仓库规格为 XS，每个工作日运行两小时，每月二十个营业日，"
        "计算点数消耗为四十个 Credit，产生费用二百二十八美元；存储资源沉淀四太字节数据，月费一百美元；"
        "为满足容灾合规诉求，每月一次将两太字节增量数据跨区传输至大阪机房，产生传输费一百八十美元。"
        "三者相加，月度总运营成本仅为五百零八美元！"
        "同时务必谨记金融降本秘诀：虚拟仓库必须设置五分钟自动挂起，无任务自动停机，有查询毫秒级唤醒，彻底杜绝闲置开销。"
    ),
    "act4": (
        "第四节，总体数据迁移架构与端到端数据流设计。"
        "为了实现零丢失、高安全的数据割接，我们设计了全链路加密的金融级数据搬迁管线。"
        "源端是位于东京本地数据中心的 Oracle 11g 数据库。通过专有抽取作业，核心数据表如客户取引明细表被高速导出为按块压缩的 Gzip CSV 文件。"
        "在传输链路层，通过标准 TLS 1.3 强加密隧道，客户端使用 SnowSQL 工具执行 PUT 指令，将加密数据文件安全上传至 Snowflake 内部阶段暂存区 MITSUI_STAGE。"
        "阶段暂存区作为安全受控边界，实施严格的瞬时访问授权。"
        "随后，数据迁移专用计算仓库 MITSUI_WH 被拉起，执行幂等优化的 COPY INTO 指令，高速将暂存文件解析并载入至目标库的 RAW_ORACLE 落地表中。"
        "整个过程存算分离，专机专用，完全隔离于生产报表查询，保障迁移吞吐率与业务连续性双重达标。"
    ),
    "act5": (
        "第五节，核心表结构映射与八大类型推测规范。这是确保跨系统迁移数据百分之百严密对账的核心法宝。"
        "第一条规则：一般数值信息。变更前 Oracle 的 NUMBER 不带精度容易产生浮点歧义，变更后统一固定为 NUMBER(15, 0) 整数位，初期值统一设为零。"
        "第二条规则：本币金额。针对各来源系统二位或三位小数定义不一的痛点，统一强制升级为 NUMBER(18, 3)，保留三位小数全量对齐。"
        "第三条规则：外币金额。外币金额统一采用 NUMBER(18, 3)，并且必须与三位货币代码字段成对建立，强化表结构高内聚。"
        "第四条规则：汇率与比率。统一固定为 NUMBER(9, 6)，保留六位高精度小数，确保多币种换算精度绝对无损。"
        "第五条规则：文字信息与字符编码。在 Oracle 中 BYTE 与 CHAR 语义混用，全角日文字符占用三字节，极易触发 ORA-12899 溢出报错；"
        "而在 Snowflake 中，VARCHAR 默认严格按字符数计数，统一规范为 VARCHAR(100)，化繁为简杜绝超长截断。"
        "第六条规则：定长代码。如十位客户代码、四位支店代码，沿用来源系统原始定长定义。"
        "第七条规则，也是最核心的顶层设计决策：业务日期统一采用字符串存储。日次约定日存为八位 VARCHAR(20250325)，月次结算月存为六位 VARCHAR(202503)。"
        "这彻底包容了日次与月次的不同粒度，杜绝了时区自动转换产生的隐性漂移，并且直供下游监管报表直接消费！"
        "第八条规则：时刻与系统时间戳。系统登记更新时间统一使用无时区墙上时钟 TIMESTAMP_NTZ(6)，保留至微秒精度，专门用于版本比对与审计追踪。"
        "业务日期用字符串，系统审计用时间戳，这一分野是金融数仓架构设计的高光典范。"
    ),
    "act6": (
        "第六节，Snowflake 核心受控对象体系与参数继承架构。"
        "在 Snowflake 安全底座中，所有数据资产、计算引擎乃至安全策略均是一等公民的受控对象。"
        "从顶层的 ORGANIZATION 组织，到租户 ACCOUNT，再到网络策略 NETWORK POLICY、身份认证策略、角色与用户；"
        "计算层包括虚拟仓库 WAREHOUSE，存储层依次细分为 DATABASE、SCHEMA、TABLE 和 VIEW，配合高可用容灾的 FAILOVER GROUP 与安全暂存区 STAGE，共同构筑了十六大核心金融对象矩阵。"
        "而在运行行为控制上，Snowflake 提供了优雅的三层参数继承体系。"
        "参数划分为账户级、会话级与对象级。以最为关键的会话参数为例，自顶向下由 Account 账户默认基线、中间 User 用户个性化设定，以及底层 Session 会话动态值构成。"
        "未配置时逐级自动继承，显式指定时自底向上精确覆盖，赋予金融管理极高的灵活性与规范一致性。"
    ),
    "act7": (
        "第七节，金融级三位一体高可用与容灾架构。"
        "为了达成灾备零丢失与高可用连续性，Snowflake 提供了时间旅行、安全网与零拷贝克隆三层防护壁垒。"
        "第一层壁垒：时间旅行 Time Travel。允许用户通过原生 SQL 语法（如 UNDROP 或时间戳快照查询）在零到九十天窗口期内秒级自愈误删除或误覆盖数据，无需繁重的冷备恢复。"
        "第二层壁垒：平台安全网 Fail-safe。当数据超出时间旅行周期后，平台提供为期七天的最后防线灾备恢复。但请务必注意：Fail-safe 绝非日常自助功能，必须由官方技术支持人工介入且耗时较长，金融设计严禁将其作为主力手段！"
        "第三层壁垒：零拷贝即时克隆 Zero-copy Clone。克隆操作本质上仅复制元数据指针，直接共享已有物理微分区，在克隆瞬间产生零额外存储开销！"
        "仅在克隆对象发生后续写入时按写时复制计算增量存储费，是实施沙箱演练、季度审计快照与重大割接前秒级备份的最佳工程实践！"
        "以上就是第一章关于业务背景、架构设计与成本模型的全部内容，感谢收看！"
    )
}

def generate_voiceovers():
    print(f"Starting TTS generation for {len(ACTS_SCRIPTS)} acts...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    manifest = {}
    
    current_time_offset = 0.0
    
    for act_id in ["act1", "act2", "act3", "act4", "act5", "act6", "act7"]:
        script = ACTS_SCRIPTS[act_id]
        mp3_path = os.path.join(OUTPUT_DIR, f"{act_id}.mp3")
        wav_path = os.path.join(OUTPUT_DIR, f"{act_id}.wav")
        print(f"Synthesizing {act_id} ({len(script)} chars)...")
        
        tts = gTTS(text=script, lang='zh-CN', slow=False)
        tts.save(mp3_path)
        
        # Convert mp3 to wav via subprocess with direct FFMPEG_EXE
        subprocess.run(
            [FFMPEG_EXE, "-y", "-i", mp3_path, "-ar", "48000", "-ac", "2", wav_path],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        data, sr = sf.read(wav_path)
        duration_sec = len(data) / sr
        
        # Add a 2.0s pause between acts
        padded_duration = round(duration_sec + 2.0, 2)
        
        manifest[act_id] = {
            "wav": wav_path,
            "raw_duration": round(duration_sec, 2),
            "duration": padded_duration,
            "start_time": round(current_time_offset, 2),
            "script_chars": len(script)
        }
        print(f"  -> {act_id} generated: {round(duration_sec, 2)}s (allocated: {padded_duration}s, start: {round(current_time_offset, 2)}s)")
        current_time_offset += padded_duration
        time.sleep(1)
        
    manifest["total_duration"] = round(current_time_offset, 2)
    print(f"\nAll acts generated! Total timeline duration: {round(current_time_offset, 2)}s ({round(current_time_offset/60, 2)} min)")
    
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"Manifest written to {MANIFEST_PATH}")
    return manifest

if __name__ == "__main__":
    generate_voiceovers()
