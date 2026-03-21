"""
pdbq CLI — natural-language queries over PeeringDB data.

Usage:
    pdbq query "Which networks peer at more than 10 IXes?"
    pdbq query "All facilities in Germany" --export-sheets
    pdbq sync
    pdbq sync --incremental
    pdbq sync status
    pdbq db shell
    pdbq serve
"""
import sys

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()


@click.group()
def cli() -> None:
    from pdbq.config import configure_logging
    configure_logging(debug=False)


@cli.command()
@click.argument("question")
@click.option("--export-sheets", is_flag=True, default=False, help="Export results to Google Sheets")
@click.option("--show-sql", is_flag=True, default=False, help="Print SQL queries executed by the agent")
@click.option("--debug", is_flag=True, default=False, help="Enable verbose logging")
def query(question: str, export_sheets: bool, show_sql: bool, debug: bool) -> None:
    """Ask a natural-language question about PeeringDB data."""
    from pdbq.config import configure_logging
    configure_logging(debug=debug)
    from pdbq.agent.core import run_agent

    google_token = None
    if export_sheets:
        google_token = _ensure_google_auth()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
        console=console,
    ) as progress:
        progress.add_task("Querying agent...", total=None)
        result = run_agent(question, google_token=google_token)

    console.print(Markdown(result.answer))

    if show_sql and result.sql_executed:
        console.print("\n[bold dim]SQL executed:[/bold dim]")
        for sql in result.sql_executed:
            console.print(f"[dim]{sql}[/dim]")

    if export_sheets:
        for call in result.tool_calls:
            if call.get("tool") == "export_to_sheets":
                res = call.get("result", {})
                if "sheet_url" in res:
                    console.print(f"\n[green]Exported to Google Sheets:[/green] {res['sheet_url']}")
                    break


def _ensure_google_auth() -> str:
    """Ensure Google OAuth credentials exist for CLI, return user_token."""
    from pathlib import Path
    from pdbq.config import settings

    token_path = Path(settings.google_token_store_path_abs) / "cli.json"
    if not token_path.exists():
        console.print("[yellow]No Google credentials found. Starting OAuth flow...[/yellow]")
        from pdbq.agent.sheets import cli_oauth_flow
        cli_oauth_flow()
    return "cli"


@cli.group()
def sync() -> None:
    """Manage PeeringDB data sync."""


@sync.command("run")
@click.option("--incremental", is_flag=True, default=False, help="Only fetch records updated since last sync")
@click.option("--debug", is_flag=True, default=False, help="Enable verbose logging")
def sync_run(incremental: bool, debug: bool) -> None:
    """Sync PeeringDB data into the local DuckDB database."""
    from pdbq.config import configure_logging
    configure_logging(debug=debug)
    from pdbq.sync.run import run_sync

    mode = "incremental" if incremental else "full"
    console.print(f"[bold]Starting {mode} sync...[/bold]")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
        console=console,
    ) as progress:
        progress.add_task(f"Syncing PeeringDB ({mode})...", total=None)
        results = run_sync(incremental=incremental)

    table = Table(title="Sync Results", show_header=True)
    table.add_column("Resource", style="cyan")
    table.add_column("Records", justify="right")
    table.add_column("Status")

    for resource, count in results.items():
        status_text = "[green]OK[/green]" if count >= 0 else "[red]FAILED[/red]"
        table.add_row(resource, str(count) if count >= 0 else "—", status_text)

    console.print(table)


@sync.command("status")
def sync_status() -> None:
    """Show sync status for all PeeringDB resource types."""
    from pdbq.db.connection import get_read_connection

    try:
        conn = get_read_connection()
        rows = conn.execute(
            "SELECT resource, last_synced_at, record_count FROM sync_meta ORDER BY resource"
        ).fetchall()
        conn.close()
    except Exception as exc:
        console.print(f"[red]Error reading sync status: {exc}[/red]")
        sys.exit(1)

    if not rows:
        console.print("[yellow]No sync data found. Run `pdbq sync run` first.[/yellow]")
        return

    table = Table(title="Sync Status", show_header=True)
    table.add_column("Resource", style="cyan")
    table.add_column("Last Synced")
    table.add_column("Records", justify="right")

    for row in rows:
        last_synced = row[1].isoformat() if row[1] else "Never"
        table.add_row(row[0], last_synced, str(row[2] or 0))

    console.print(table)


@cli.group()
def db() -> None:
    """DuckDB utilities."""


@db.command("shell")
def db_shell() -> None:
    """Open an interactive DuckDB shell against the local database."""
    import subprocess
    from pdbq.config import settings

    db_path = settings.duckdb_path_abs
    console.print(f"[bold]Opening DuckDB shell:[/bold] {db_path}")
    console.print("[dim]Type .exit or Ctrl+D to quit.[/dim]\n")
    subprocess.run(["duckdb", db_path])


@cli.command()
@click.option("--host", default="127.0.0.1", help="Host to bind to")
@click.option("--port", default=8080, help="Port to listen on")
@click.option("--reload", is_flag=True, default=False, help="Enable auto-reload (development)")
def serve(host: str, port: int, reload: bool) -> None:
    """Start the FastAPI server."""
    import uvicorn

    console.print(f"[bold]Starting pdbq API server at http://{host}:{port}[/bold]")
    uvicorn.run(
        "pdbq.api.main:app",
        host=host,
        port=port,
        reload=reload,
    )


# Allow `pdbq sync` without subcommand to default to `pdbq sync run`
@cli.command("sync", hidden=True)
@click.option("--incremental", is_flag=True, default=False)
@click.option("--debug", is_flag=True, default=False)
@click.pass_context
def sync_shortcut(ctx: click.Context, incremental: bool, debug: bool) -> None:
    """Shortcut: pdbq sync [--incremental] runs a sync."""
    ctx.invoke(sync_run, incremental=incremental, debug=debug)


# Fix: make `pdbq sync` without subcommand still work as a group
# by re-exposing it as the group default
cli.add_command(sync)


if __name__ == "__main__":
    cli()
