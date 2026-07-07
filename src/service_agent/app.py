"""
应用入口 —— 支持 CLI 交互与 API 服务两种模式。

用法:
    service-agent chat                      # 启动交互式聊天
    service-agent chat -m "你好"             # 单次问答
    service-agent serve                     # 启动 API 服务
    service-agent rag stats                 # 知识库统计
    service-agent rag reload                # 重新加载知识库
    service-agent tools list                # 列出工具
"""

from __future__ import annotations

import logging

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt

from service_agent.agent.core import service_agent
from service_agent.config.settings import settings
from service_agent.rag.retriever import rag_manager

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

console = Console()
app = typer.Typer(name="service-agent", help="智能客服 Agent", no_args_is_help=True)
rag_app = typer.Typer(name="rag", help="知识库管理")
tools_app = typer.Typer(name="tools", help="工具管理")
app.add_typer(rag_app, name="rag")
app.add_typer(tools_app, name="tools")


@app.command()
def chat(
    message: str = typer.Option(None, "--message", "-m", help="单次问答模式"),
    session_id: str = typer.Option(None, "--session", "-s", help="会话 ID"),
) -> None:
    """与 Agent 聊天。"""
    if message:
        with console.status("[bold green]思考中..."):
            resp = service_agent.chat(message, session_id=session_id)
        _print_response(resp)
        return

    console.print(Panel.fit(
        "[bold]智能客服 Agent[/bold] 🤖\n"
        f"模型: {settings.llm_model}\n"
        "输入 [bold]exit[/bold] 退出 | 输入 [bold]reset[/bold] 重置会话",
        title="Service Agent",
        border_style="cyan",
    ))
    current = session_id
    while True:
        try:
            user_input = Prompt.ask("[bold cyan]你[/bold cyan]")
        except (EOFError, KeyboardInterrupt):
            console.print("\n再见! 👋")
            break
        if not user_input.strip():
            continue
        if user_input.strip().lower() in ("exit", "quit"):
            console.print("再见! 👋")
            break
        if user_input.strip().lower() == "reset":
            if current:
                service_agent.reset_session(current)
            console.print("[yellow]会话已重置[/yellow]")
            continue
        with console.status("[bold green]思考中..."):
            resp = service_agent.chat(user_input, session_id=current)
        current = resp.session_id
        _print_response(resp)


def _print_response(resp) -> None:
    console.print()
    console.print(Markdown(resp.reply), style="white")
    if resp.tool_used:
        console.print(f"  🔧 使用工具: {', '.join(resp.tool_used)}", style="dim")
    if resp.sources:
        console.print(f"  📚 知识来源: {', '.join(resp.sources)}", style="dim")
    console.print(f"  🆔 会话: {resp.session_id}", style="dim")
    console.print()


@app.command()
def serve(
    host: str = typer.Option(None, "--host", help="监听地址"),
    port: int = typer.Option(None, "--port", help="监听端口"),
) -> None:
    """启动 API 服务。"""
    import uvicorn

    # 确认 FastAPI 已安装
    try:
        import fastapi  # noqa: F401
    except ImportError:
        console.print("[red]缺少 fastapi,请运行: pip install fastapi uvicorn[/red]")
        raise typer.Exit(1)

    uvicorn.run(
        "service_agent.app:create_app",
        factory=True,
        host=host or settings.api_host,
        port=port or settings.api_port,
        reload=False,
    )


@rag_app.command("stats")
def rag_stats() -> None:
    """查看知识库统计。"""
    stats = rag_manager.get_stats()
    console.print(Panel.fit(
        f"初始化: {'✅' if stats['initialized'] else '❌'}\n"
        f"分块数: {stats.get('chunk_count', 0)}\n"
        f"Collection: {stats.get('collection', 'N/A')}",
        title="知识库统计",
        border_style="cyan",
    ))


@rag_app.command("reload")
def rag_reload() -> None:
    """重新加载知识库。"""
    with console.status("[bold green]加载中..."):
        rag_manager.reload()
    console.print("[green]知识库已重新加载[/green]")
    rag_stats()


@tools_app.command("list")
def tools_list() -> None:
    """列出所有工具。"""
    names = service_agent.registry.list_names()
    if not names:
        console.print("[yellow]没有已注册的工具[/yellow]")
        return
    for name in names:
        tool = service_agent.registry.get(name)
        console.print(f"  🔧 [bold]{name}[/bold]: {tool.description}")  # type: ignore[union-attr]


# ===== FastAPI 应用工厂 =====


def create_app():
    """
    创建 FastAPI 应用。

    在 `serve` 命令中通过 uvicorn factory 模式调用。
    """
    from fastapi import FastAPI, HTTPException

    from service_agent.agent.memory import memory_manager
    from service_agent.config.models import ChatRequest, ChatResponse

    web = FastAPI(title="Service Agent API", version="0.1.0")

    @web.get("/health")
    async def health():
        return {"status": "ok", "version": "0.1.0"}

    @web.post("/api/chat", response_model=ChatResponse)
    async def chat_api(req: ChatRequest):
        try:
            return service_agent.chat(req.message, session_id=req.session_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e)) from e

    @web.get("/api/sessions")
    async def list_sessions():
        return [
            {"session_id": sid, "message_count": memory_manager.get_session_info(sid)["message_count"]}
            for sid in memory_manager.list_sessions()
        ]

    @web.delete("/api/sessions/{session_id}")
    async def delete_session(session_id: str):
        service_agent.reset_session(session_id)
        return {"status": "deleted", "session_id": session_id}

    @web.get("/api/tools")
    async def list_tools():
        return [
            {"name": n, "description": service_agent.registry.get(n).description}  # type: ignore[union-attr]
            for n in service_agent.registry.list_names()
        ]

    @web.get("/api/rag/stats")
    async def rag_stats_api():
        return rag_manager.get_stats()

    @web.post("/api/rag/reload")
    async def rag_reload_api():
        rag_manager.reload()
        return rag_manager.get_stats()

    return web


if __name__ == "__main__":
    app()
