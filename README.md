# 智扫通 · 智能客服 🤖

扫地/扫拖机器人领域的智能客服 Agent，基于 **LangChain ReAct Agent + RAG 检索增强**，
支持自主工具调用、知识库问答、使用报告生成，通过 Streamlit 提供 Web 聊天界面。

## ✨ 核心特性

- **ReAct 智能体**：思考→行动→观察→再思考的自主推理循环
- **RAG 知识检索**：基于 ChromaDB 向量库，从知识文档中精准检索参考资料
- **7 个内置工具**：知识检索、天气查询、用户定位、用户ID、月份获取、外部数据、报告上下文
- **中间件机制**：工具执行监控、模型调用日志、动态提示词切换（报告模式）
- **流式输出**：逐字打字机效果，提升交互体验
- **双模型架构**：智谱 GLM-4.7-flash（对话）+ 阿里 DashScope text-embedding-v4（向量化）

## 📁 项目结构

```
service-agent/
├── app.py                     # 🚀 Streamlit Web 入口
├── agent/                     # Agent 逻辑
│   ├── react_agent.py         #   🧠 ReAct 智能体编排
│   └── tools/
│       ├── agent_tools.py     #   🔧 7个内置工具
│       └── middleware.py      #   🔌 3个中间件
├── model/
│   └── factory.py             #   🏭 模型工厂（智谱GLM + 阿里Embedding）
├── rag/                       # RAG 检索
│   ├── vector_store.py        #   📚 ChromaDB 向量存储
│   └── rag_service.py         #   🔍 检索+总结服务
├── utils/                     # 工具函数
│   ├── config_handler.py      #   ⚙️ YAML 配置加载
│   ├── file_handler.py        #   📄 文件处理（MD5去重/PDF/TXT加载）
│   ├── logger_handler.py      #   📝 日志器
│   ├── path_tool.py           #   📐 路径工具
│   └── prompt_loader.py       #   💬 提示词加载器
├── config/                    # YAML 配置
│   ├── agent.yml             #   Agent配置
│   ├── chroma.yml            #   向量库配置
│   ├── prompts.yml           #   提示词路径配置
│   └── rag.yml               #   模型配置
├── prompts/                  # 提示词
│   ├── main_prompt.txt       #   系统主提示词
│   ├── rag_summarize.txt     #   RAG总结提示词
│   └── report_prompt.txt     #   报告生成提示词
├── data/                     # 知识库与外部数据
│   ├── *.txt                 #   知识文档（选购/维护/故障排除/100问）
│   └── external/records.csv  #   外部使用记录数据
├── chroma_db/                 # ChromaDB 持久化存储（自动生成）
├── logs/                     # 运行日志（自动生成）
├── tests/                    # 测试
├── pyproject.toml            # 依赖与配置
├── .env.example              # 环境变量模板
└── README.md
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -e ".[dev]"
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env`，填入以下 API Key：

| 变量 | 说明 | 获取方式 |
|------|------|----------|
| `OPENAI_API_KEY` | 智谱 GLM API Key | [智谱开放平台](https://open.bigmodel.cn/) |
| `DASHSCOPE_API_KEY` | 阿里 DashScope API Key | [阿里云百炼](https://dashscope.aliyun.com/) |

### 3. 启动应用

```bash
streamlit run app.py
```

浏览器打开 `http://localhost:8501` 即可开始对话。

## 💬 使用示例

- **知识问答**：「小户型适合哪些扫地机器人？」→ 自动调用 `rag_summarize` 检索知识库
- **环境适配**：「我现在所在城市的天气适合扫地机器人工作吗？」→ 调用 `get_user_location` + `get_weather`
- **使用报告**：「给我生成我的使用报告」→ 按 `get_user_id` → `get_current_month` → `fill_context_for_report` → `fetch_external_data` 流程生成报告

## 🔧 内置工具

| 工具 | 入参 | 说明 |
|------|------|------|
| `rag_summarize` | `query` | 从向量库检索参考资料并总结回答 |
| `get_weather` | `city` | 获取指定城市天气信息 |
| `get_user_location` | 无 | 获取用户所在城市 |
| `get_user_id` | 无 | 获取用户唯一标识 |
| `get_current_month` | 无 | 获取当前月份（YYYY-MM） |
| `fetch_external_data` | `user_id`, `month` | 检索指定用户某月使用记录 |
| `fill_context_for_report` | 无 | 触发报告生成模式，切换提示词 |

## 🔌 中间件

| 中间件 | 作用 |
|--------|------|
| `monitor_tool` | 工具执行日志，检测报告工具调用并切换上下文 |
| `log_before_model` | 模型调用前日志记录 |
| `report_prompt_switch` | 根据 `report` 标记动态切换系统提示词 |

## 📚 知识库管理

将知识文档放入 `data/` 目录（支持 `.txt`、`.pdf`），首次启动时自动索引。
通过文件 MD5 去重，修改或新增文档后重新启动即可自动加载新内容。

手动重新索引：

```bash
python -c "from rag.vector_store import VectorStoreService; VectorStoreService().load_document()"
```

## ⚙️ 配置说明

| 配置文件 | 说明 |
|----------|------|
| `config/rag.yml` | 对话模型名称、嵌入模型名称 |
| `config/chroma.yml` | 向量库集合名、持久化路径、分片参数、检索数量 |
| `config/agent.yml` | 外部数据文件路径 |
| `config/prompts.yml` | 各场景提示词文件路径 |

## License

MIT
