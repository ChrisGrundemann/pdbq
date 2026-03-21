"""
pdbq CLI — natural-language queries over PeeringDB data.

Usage:
    pdbq query "Which networks peer at more than 10 IXes?"
    pdbq query "All facilities in Germany" --export-sheets
    pdbq history
    pdbq history --last 10
    pdbq history --show 1
    pdbq sync
    pdbq sync --incremental
    pdbq sync status
    pdbq db shell
    pdbq serve
"""
import csv
import io
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()

def _history_path():
    from pdbq.config import settings
    return settings.query_history_path_abs


def _append_history(record: dict) -> None:
    from pdbq.config import settings
    path = settings.query_history_path_abs
    with path.open("a") as f:
        f.write(json.dumps(record) + "\n")
    max_entries = settings.query_history_max_entries
    if max_entries > 0:
        _trim_history(path, max_entries)


def _trim_history(path: Path, max_entries: int) -> None:
    with path.open() as f:
        lines = [l for l in f if l.strip()]
    if len(lines) > max_entries:
        path.write_text("".join(lines[-max_entries:]))


def _load_history(last: int) -> list[dict]:
    path = _history_path()
    if not path.exists():
        return []
    entries = []
    with path.open() as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return entries[-last:] if last else entries


def _last_query_db_rows(tool_calls: list) -> tuple[list[str], list[dict]] | tuple[None, None]:
    """Return (columns, rows) from the last query_db tool call that produced rows, or (None, None)."""
    for call in reversed(tool_calls):
        if call.get("tool") == "query_db":
            result = call.get("result", {})
            rows = result.get("rows")
            columns = result.get("columns")
            if rows and columns:
                return columns, rows
    return None, None


def _write_output(out_path: Path, answer: str, tool_calls: list) -> str:
    """Write output to out_path. Returns 'csv' or 'markdown' indicating what was written."""
    if out_path.suffix.lower() == ".csv":
        columns, rows = _last_query_db_rows(tool_calls)
        if columns and rows:
            buf = io.StringIO()
            writer = csv.DictWriter(buf, fieldnames=columns, extrasaction="ignore", lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
            out_path.write_text(buf.getvalue())
            return "csv"
        # Fall through to markdown if no tabular data
    out_path.write_text(answer)
    return "markdown"


@click.group()
def cli() -> None:
    from pdbq.config import configure_logging
    configure_logging(debug=False)


@cli.command()
@click.argument("question")
@click.option("--export-sheets", is_flag=True, default=False, help="Export results to Google Sheets")
@click.option("--show-sql", is_flag=True, default=False, help="Print SQL queries executed by the agent")
@click.option("--output", "output_file", default=None, metavar="FILE", help="Save markdown response to FILE")
@click.option("--debug", is_flag=True, default=False, help="Enable verbose logging")
def query(question: str, export_sheets: bool, show_sql: bool, output_file: str, debug: bool) -> None:
    """Ask a natural-language question about PeeringDB data."""
    from pdbq.config import configure_logging
    configure_logging(debug=debug)
    from pdbq.agent.core import run_agent

    if output_file:
        out_path = Path(output_file)
        if out_path.exists() and not click.confirm(f"{output_file} already exists. Overwrite?"):
            raise click.Abort()

    google_token = None
    if export_sheets:
        google_token = _ensure_google_auth()

    t0 = time.monotonic()
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
        console=console,
    ) as progress:
        progress.add_task("Querying agent...", total=None)
        result = run_agent(question, google_token=google_token)
    elapsed_ms = int((time.monotonic() - t0) * 1000)

    console.print(Markdown(result.answer))

    if output_file:
        fmt = _write_output(out_path, result.answer, result.tool_calls)
        if fmt == "csv":
            console.print(f"\n[green]Saved CSV to {output_file}[/green]")
        else:
            if out_path.suffix.lower() == ".csv":
                console.print(f"\n[yellow]No tabular data found — saved markdown to {output_file}[/yellow]")
            else:
                console.print(f"\n[green]Saved to {output_file}[/green]")

    _append_history({
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        "query": question,
        "sql_executed": result.sql_executed,
        "elapsed_ms": elapsed_ms,
        "output_file": output_file,
        "answer": result.answer,
    })

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


@cli.command()
@click.option("--last", default=20, show_default=True, metavar="N", help="Show only the last N entries")
@click.option("--show", "show_index", default=None, type=int, metavar="N", help="Show full output of the Nth most recent query (1 = most recent)")
def history(last: int, show_index: int) -> None:
    """Show past query history."""
    entries = _load_history(last)

    if not entries:
        console.print("[yellow]No query history found.[/yellow]")
        return

    if show_index is not None:
        if show_index < 1 or show_index > len(entries):
            console.print(f"[red]No entry #{show_index} — history has {len(entries)} entries (most recent = 1).[/red]")
            sys.exit(1)
        # entries are ordered oldest-first; index 1 = last entry
        entry = entries[-show_index]
        console.print(f"[bold dim]{entry['timestamp']}[/bold dim]  [cyan]{entry['query']}[/cyan]\n")
        if entry.get("answer"):
            console.print(Markdown(entry["answer"]))
        elif entry.get("sql_executed"):
            console.print("[bold dim]SQL executed:[/bold dim]")
            for sql in entry["sql_executed"]:
                console.print(f"[dim]{sql}[/dim]")
        return

    table = Table(show_header=True)
    table.add_column("#", justify="right", style="dim")
    table.add_column("Timestamp", style="dim")
    table.add_column("Query", no_wrap=False, max_width=60)
    table.add_column("SQL", justify="right")
    table.add_column("ms", justify="right")

    for i, entry in enumerate(reversed(entries), start=1):
        q = entry.get("query", "")
        truncated = q[:57] + "..." if len(q) > 60 else q
        sql_count = str(len(entry.get("sql_executed") or []))
        elapsed = str(entry.get("elapsed_ms", ""))
        table.add_row(str(i), entry.get("timestamp", ""), truncated, sql_count, elapsed)

    console.print(table)


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
@click.option("--tables", default=None, metavar="TABLES", help="Comma-separated list of tables to sync (e.g. --tables ixfac,as_set)")
@click.option("--debug", is_flag=True, default=False, help="Enable verbose logging")
def sync_run(incremental: bool, tables: str, debug: bool) -> None:
    """Sync PeeringDB data into the local DuckDB database."""
    from pdbq.config import configure_logging
    configure_logging(debug=debug)
    from pdbq.sync.run import run_sync

    table_list = [t.strip() for t in tables.split(",")] if tables else None

    if table_list:
        mode = f"selective ({', '.join(table_list)})"
    elif incremental:
        mode = "incremental"
    else:
        mode = "full"
    console.print(f"[bold]Starting {mode} sync...[/bold]")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
        console=console,
    ) as progress:
        progress.add_task(f"Syncing PeeringDB ({mode})...", total=None)
        results = run_sync(incremental=incremental, tables=table_list)

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
@click.option("--tables", default=None, metavar="TABLES")
@click.option("--debug", is_flag=True, default=False)
@click.pass_context
def sync_shortcut(ctx: click.Context, incremental: bool, tables: str, debug: bool) -> None:
    """Shortcut: pdbq sync [--incremental] runs a sync."""
    ctx.invoke(sync_run, incremental=incremental, tables=tables, debug=debug)


# Fix: make `pdbq sync` without subcommand still work as a group
# by re-exposing it as the group default
cli.add_command(sync)


if __name__ == "__main__":
    cli()
