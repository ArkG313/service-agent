# Service Agent 🤖

智能客服 Agent —— 基于 LLM 的对话式客服系统,支持**工具调用**与**知识库 RAG**。

## 📁 项目结构

```
service-agent/
├── app.py                     # 🚀 入口(CLI + API)
├── agent/                     # Agent 逻辑
│   ├── core.py                #   🧠 核心编排(RAG→LLM→工具→回传)
│   ├── llm.py                 #   🔌 LLM 客户端(OpenAI)
│   └── memory.py              #   💾 会话记忆管理
├── rag/                       # RAG 检索
│   └── retriever.py           #   📚 ChromaDB 知识库检索
├── tools/                     # 工具函数
│   ├── base.py                #   工具基类 + 注册中心
│   └── builtin.py             #   内置工具(查订单/算运费/转人工/查时间)
├── config/                    # 配置
│   ├── settings.py            #   ⚙️ 环境变量配置
│   └── models.py              #   📦 数据模型
├── tests/                     # 测试
├── data/                      # 知识库数据
│   ├── knowledge_base/        #   知识库文档(PDF/TXT/MD)
│   └── vector_db/             #   向量存储(自动生成)
├── pyproject.toml             # 依赖与配置
├── .env.example               # 环境变量模板
└── README.md
```

## 🚀 快速开始

```bash
# 1. 安装依赖(开发模式)
pip install -e ".[dev]"

# 2. 配置
cp .env.example .env
# 编辑 .env 填入 OPENAI_API_KEY

# 3. 运行
python app.py chat                    # 交互式聊天
python app.py chat -m "退换货政策?"    # 单次问答
python app.py serve                   # 启动 API 服务 → /docs
```

## 📋 命令一览

| 命令 | 说明 |
|------|------|
| `python app.py chat` | 交互式聊天 |
| `python app.py chat -m "消息"` | 单次问答 |
| `python app.py serve` | 启动 API 服务 |
| `python app.py rag stats` | 知识库统计 |
| `python app.py rag reload` | 重新加载知识库 |
| `python app.py tools list` | 列出工具 |

## 🔧 自定义工具

```python
from tools.base import BaseTool

class WeatherTool(BaseTool):
    @property
    def name(self) -> str:
        return "get_weather"

    @property
    def description(self) -> str:
        return "查询城市天气"

    @property
    def parameters(self) -> dict:
        return {"type": "object", "properties": {"city": {"type": "string"}}}

    def execute(self, city: str, **kwargs) -> str:
        return f"{city}今天晴,25°C"

# 注册
service_agent.registry.register(WeatherTool())
```

## 📚 知识库

将文档放入 `data/knowledge_base/`(支持 `.pdf` `.txt` `.md`),运行 `python app.py rag reload` 重新索引。

## 📡 API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/chat` | 聊天 |
| `GET` | `/api/sessions` | 列出会话 |
| `DELETE` | `/api/sessions/{id}` | 删除会话 |
| `GET` | `/api/tools` | 列出工具 |
| `GET` | `/api/rag/stats` | 知识库统计 |
| `POST` | `/api/rag/reload` | 重新加载知识库 |
| `GET` | `/health` | 健康检查 |

## License

MIT
