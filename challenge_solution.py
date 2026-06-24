"""
CodeToAGI — Episode 50 Challenge Solution
Async News Aggregator CLI with --since and --export
"""

import asyncio
import csv
from datetime import datetime
from pathlib import Path
import typer
from typing import Optional

from models import Article
from fetcher import fetch_all
from store import db_conn, save, get_all_articles

app = typer.Typer(help="AI News Aggregator CLI")


@app.command()
def fetch(topic: str = typer.Option("AI", help="Topic to search for"),
          limit: int = typer.Option(10, help="Number of articles to fetch")):
    """Fetch and store news articles"""
    typer.echo(f"Fetching news about '{topic}'...")
    articles = asyncio.run(fetch_all([topic]))
    
    with db_conn() as conn:
        saved_count = 0
        for article in articles[:limit]:
            save(article, conn)
            saved_count += 1
        typer.echo(f"✅ Stored {saved_count} articles")


@app.command()
def report(since: Optional[str] = typer.Option(None, help="Filter by date (YYYY-MM-DD)"),
           export: Optional[str] = typer.Option(None, help="Export to CSV file")):
    """Show stored articles. Use --since YYYY-MM-DD and/or --export file.csv"""
    with db_conn() as conn:
        articles = get_all_articles(conn)
    
    if since:
        try:
            since_date = datetime.fromisoformat(since)
            articles = [a for a in articles if a.published_at >= since_date]
            typer.echo(f"Filtered to articles since {since}")
        except ValueError:
            typer.echo("❌ Invalid date format. Use YYYY-MM-DD")
            raise typer.Exit(1)
    
    if not articles:
        typer.echo("No articles found.")
        return
    
    # Display
    typer.echo(f"\n📋 Found {len(articles)} articles:")
    for i, article in enumerate(articles, 1):
        typer.echo(f"{i:2d}. {article.title[:80]}... | {article.source}")
    
    # Export to CSV (Bonus)
    if export:
        export_path = Path(export)
        with export_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Title", "URL", "Source", "Published At"])
            for article in articles:
                writer.writerow([
                    article.title,
                    article.url,
                    article.source,
                    article.published_at.isoformat()
                ])
        typer.echo(f"✅ Exported {len(articles)} articles to {export}")


@app.command()
def clear():
    """Clear all stored articles"""
    if typer.confirm("Delete ALL articles from database?"):
        Path("news.db").unlink(missing_ok=True)
        typer.echo("🗑️ Database cleared.")
    else:
        typer.echo("Cancelled.")


if __name__ == "__main__":
    app()
