# ==============================================================================
# 文件名称: streamlit_app.py
# 核心用途: Snowflake 原生 Streamlit 现代官方模板入口源码
# 适用环境: Streamlit in Snowflake (SiS) / 现代容器及数仓运行时 (Streamlit v1.66+)
# 运行机理:
#   1. 通过 st.connection("snowflake") 免密获取原生仓内上下文与 Snowpark 会话
#   2. 采用响应式交互组件 (st.slider) 捕获用户输入
#   3. 通过 session.create_dataframe 将数据动态转化为 Snowpark DataFrame
#   4. 最终通过 to_pandas() 获取结果并由 st.bar_chart 和 st.dataframe 即时渲染
# ==============================================================================

# 1. 导入核心 Python 库
import streamlit as st  # 导入 Streamlit 核心前端交互与图表渲染库
import os                # 导入操作系统库，用于读取环境变量 (如连接超时 TTL)

# 2. 页面标题与文本渲染 (支持 Emoji 表情与版本动态占位符)
# :balloon: 会被 Streamlit 解析为彩色气球图标；st.__version__ 会动态输出当前运行时的 Streamlit 真实版本号 (如 1.66.1)
st.title(f"Example Streamlit App :balloon: {st.__version__}")

# 使用 st.write 输出引导说明文档 (支持原生 Markdown 粗体与超链接语法)
st.write(
  """Replace this example with your own code!
  **And if you're new to Streamlit,** check
  out our easy-to-follow guides at
  [docs.streamlit.io](https://docs.streamlit.io).
  """
)

# 使用 st.markdown 展示官方权威学习文档导航列表
st.markdown("""
- :page_with_curl: [Streamlit open source documentation](https://docs.streamlit.io)
- :snowflake: [Streamlit in Snowflake documentation](https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit)
- :books: [Demo repo with templates](https://github.com/Snowflake-Labs/snowflake-demo-streamlit)
- :memo: [Streamlit in Snowflake release notes](https://docs.snowflake.com/en/release-notes/streamlit-in-snowflake)
""")

# 3. 建立与 Snowflake 数据仓库的原生安全连接 (现代最佳实践)
# 【核心机理】：
#   - 新版 Streamlit 推荐使用 st.connection("snowflake") 代替老旧的 get_active_session()
#   - ttl 参数：连接生命周期缓存时延，优先从环境变量 SNOWFLAKE_CONNECTION_TTL 读取，防止高并发下频繁握手
#   - conn.session()：返回底层的 Snowpark Session 对象，用于执行 SQL 或构建分布式 DataFrame
conn = st.connection("snowflake", ttl=os.getenv("SNOWFLAKE_CONNECTION_TTL"))
session = conn.session()

# 4. 创建交互式滑块组件 (获取用户动态输入)
# 【核心机理】：
#   - 滑块允许用户在 0 到 90 之间拖动选择数值，默认初始值为 60
#   - 每次用户松开鼠标拖动滑块，Streamlit 会自顶向下重新执行整个 Python 脚本，并把新值赋给 hifives_val
hifives_val = st.slider(
  "Number of high-fives in Q3",  # 滑块标题：第 3 季度击掌次数
  min_value=0,                   # 允许选择的最小值
  max_value=90,                  # 允许选择的最大值
  value=60,                      # 页面加载时的默认初始值
  help="Use this to enter the number of high-fives you gave in Q3",  # 鼠标悬停时的提示气泡
)

# 5. 构建 Snowpark 分布式数据集 (动态绑定用户交互输入)
# 【核心机理】：
#   - session.create_dataframe 在 Snowflake 内部内存中生成数据集
#   - 第 1 季度 (Q1: 50, 25)、第 2 季度 (Q2: 20, 35) 为固定样例值
#   - 第 3 季度 (Q3) 的 HIGH_FIVES 指标直接绑定滑块当前值 [hifives_val, 30, "Q3"]，实现所动即所得
#   - schema 参数定义数据集的列名规范
created_dataframe = session.create_dataframe(
  [[50, 25, "Q1"], [20, 35, "Q2"], [hifives_val, 30, "Q3"]],
  schema=["HIGH_FIVES", "FIST_BUMPS", "QUARTER"],
)

# 6. 执行计算并转化为 Pandas DataFrame
# 【核心机理】：
#   - created_dataframe 是 Snowpark 惰性计算对象，调用 to_pandas() 时真正触发仓内计算，
#   - 并将查询结果以紧凑格式传输到当前 Streamlit Python 进程内存中，供前端绘制图表
queried_data = created_dataframe.to_pandas()

# 7. 渲染时序柱状图 (Bar Chart)
# 【核心机理】：
#   - st.bar_chart 原生基于 Altair 矢量引擎渲染，自适应明暗主题
#   - x="QUARTER" 指定 X 轴维度为季度列，y="HIGH_FIVES" 指定 Y 轴度量为击掌次数
st.subheader("Number of high-fives")
st.bar_chart(data=queried_data, x="QUARTER", y="HIGH_FIVES")

# 8. 渲染底层明细交互式数据表 (Underlying Data Table)
# 【核心机理】：
#   - st.dataframe 将 Pandas 表格转换为具备列排序、文本搜索和全屏放大的交互式表格
#   - use_container_width=True 开启容器宽度 100% 自适应，在大屏或不同分辨率下自动占满宽度
st.subheader("Underlying data")
st.dataframe(queried_data, use_container_width=True)

