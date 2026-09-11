from __future__ import annotations
from uuid import uuid4
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

app = typer.Typer(name="styleiq", help="STYLEIQ — Pakistan Fashion Intelligence & Personal Stylist Agent", add_completion=False)
console = Console()

def _startup():
    from styleiq.config import settings
    from styleiq.logger import setup_logging, get_logger
    setup_logging(level=settings.log_level.value, log_to_file=settings.is_production, logs_dir=settings.logs_dir)
    log = get_logger(__name__)
    log.info("STYLEIQ starting up | env={env}", env=settings.env.value)
    return settings, log

@app.command()
def status():
    """Check system health."""
    settings, log = _startup()
    from styleiq.schemas.user import SystemStatus
    status_obj = SystemStatus(
        app_name=settings.app_name, version=settings.app_version,
        environment=settings.env.value, database_connected=False,
        claude_configured=settings.claude.is_configured,
        data_dir_exists=settings.data_dir.exists(), log_level=settings.log_level.value,
    )
    console.print()
    console.print(Panel.fit(f"[bold gold1]STYLEIQ[/bold gold1] [dim]v{settings.app_version}[/dim]",
                            subtitle="[dim]Pakistan Fashion Intelligence[/dim]", border_style="gold1"))
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Key", style="dim")
    table.add_column("Value", style="bold")
    checks = [
        ("Environment",     status_obj.environment),
        ("Data Directory",  "✓ exists" if status_obj.data_dir_exists else "✗ missing"),
        ("Database",        "✗ not connected (Milestone 2)" if not status_obj.database_connected else "✓ connected"),
        ("Claude API",      "✓ configured" if status_obj.claude_configured else "✗ not configured"),
        ("Default City",    settings.weather.default_city),
    ]
    for key, value in checks:
        style = "green" if "✓" in value else "yellow"
        table.add_row(key, f"[{style}]{value}[/{style}]")
    console.print(table)
    console.print()
    console.print("[green]✓ Foundation is healthy.[/green]")
    console.print()

@app.command()
def demo():
    """Run schema demo."""
    settings, log = _startup()
    console.print()
    console.print(Panel("[bold gold1]STYLEIQ Schema Demo[/bold gold1]", border_style="gold1"))
    from styleiq.schemas import OnboardingProfile, ModestyLevel, PakistaniCity, StyleDNA
    profile = OnboardingProfile(
        age=22, city=PakistaniCity.ISLAMABAD,
        modesty_level=ModestyLevel.MODEST_FULL_COVERAGE,
        preferred_aesthetics=["minimal", "feminine", "contemporary"],
        budget_min=2000, budget_max=8000,
    )
    console.print(f"  Profile: {profile.age}y | {profile.city} | PKR {profile.budget_min:,}–{profile.budget_max:,}")
    dna = StyleDNA(user_id=uuid4(), minimal=82.0, feminine=78.0, contemporary=71.0,
                   eastern_affinity=64.0, modesty_score=80.0)
    console.print(f"  Style Archetype: [bold gold1]{dna.style_archetype}[/bold gold1]")
    console.print()
    console.print(Panel("[green]✓ Schemas validated successfully.[/green]", border_style="green"))
    console.print()

@app.command()
def taxonomy():
    """Show fashion taxonomy summary."""
    settings, log = _startup()
    from styleiq.taxonomy.service import taxonomy as tx
    console.print()
    console.print(Panel("[bold gold1]STYLEIQ Fashion Taxonomy[/bold gold1]", border_style="gold1"))
    for key, value in tx.summary().items():
        console.print(f"  {key:<25} [green]{value}[/green]")
    console.print()

@app.command()
def brands():
    """Show brand compatibility scores for a sample user."""
    settings, log = _startup()
    from styleiq.services.brand_service import brand_service
    console.print()
    console.print(Panel("[bold gold1]STYLEIQ Brand Intelligence[/bold gold1]", border_style="gold1"))
    console.print("\n[bold cyan]Top 5 Compatible Brands — University Student, Islamabad, Modest[/bold cyan]")
    top_brands = brand_service.get_compatible_brands(
        user_budget_min=2000, user_budget_max=8000,
        user_modesty_level=4,
        user_style_tags=["minimal", "feminine"],
        user_aesthetics=["minimal", "feminine", "contemporary"],
        user_occasions=["university", "brunch", "dawat", "eid"],
        top_n=5,
    )
    for i, score in enumerate(top_brands, 1):
        console.print(f"\n  [bold]{i}. {score.brand_name}[/bold] [{score.brand_tier}]")
        console.print(f"     Overall: [bold green]{score.overall_score}/100[/bold green]")
        console.print(f"     Style: {score.style_match} | Budget: {score.budget_match} | Modesty: {score.modesty_match} | Occasion: {score.occasion_match}")
        console.print(f"     [dim]{score.summary}[/dim]")
    console.print()

@app.command()
def trends():
    """Show trend intelligence — scored and ranked Pakistani fashion trends."""
    settings, log = _startup()
    from styleiq.services.trend_service import trend_service

    console.print()
    console.print(Panel("[bold gold1]STYLEIQ Trend Intelligence[/bold gold1]", border_style="gold1"))

    # Save scores to DB first
    saved = trend_service.save_scores_to_db()
    console.print(f"\n[dim]Computed and saved {saved} trend scores[/dim]")

    # Top trends now
    console.print("\n[bold cyan]Trending Now — Pakistan Fashion[/bold cyan]")
    top_trends = trend_service.get_trending_now(top_n=5)

    for i, t in enumerate(top_trends, 1):
        status_color = {
            "emerging": "yellow", "rising": "green",
            "peaking": "bold green", "declining": "red",
        }.get(t.status, "white")

        console.print(f"\n  [bold]{i}. {t.trend_name}[/bold] [{t.category}]")
        console.print(f"     Status:     [{status_color}]{t.status.upper()}[/{status_color}]")
        console.print(f"     Score:      [bold]{t.total_score}/100[/bold]")
        console.print(f"     Popularity: {t.popularity_score}  |  Growth: {t.growth_score}  |  Cross-Brand: {t.cross_brand_score}  |  Seasonal: {t.seasonal_score}")
        if t.brand_count:
            console.print(f"     Brands:     {int(t.brand_count)} brands")
        if t.growth_rate_pct is not None:
            console.print(f"     Growth:     {t.growth_rate_pct:+.1f}% search volume change")

    # Emerging trends
    console.print("\n[bold cyan]Emerging Trends — Watch These[/bold cyan]")
    emerging = trend_service.get_emerging_trends()
    if emerging:
        for t in emerging:
            console.print(f"  • [yellow]{t.trend_name}[/yellow] [{t.category}] — Score: {t.total_score}")
    else:
        console.print("  [dim]No emerging trends detected yet[/dim]")

    # Full report for top trend
    console.print("\n[bold cyan]Full Report — Chocolate Brown[/bold cyan]")
    report = trend_service.get_trend_report("Chocolate Brown")
    if report:
        console.print(f"  Name:        {report.name}")
        console.print(f"  Category:    {report.category}")
        console.print(f"  Status:      {report.status}")
        console.print(f"  Season:      {report.season}")
        console.print(f"  Signals:     {report.total_signals}")
        console.print(f"  Score:       {report.score.total_score}/100")
        console.print(f"  Insight:     {report.trend_insight}")
        console.print(f"  Status:      {report.status_explanation}")
        console.print("\n  [dim]Supporting Evidence:[/dim]")
        if report.score:
            for evidence in report.score.supporting_signals:
                console.print(f"    → {evidence}")
    console.print()

if __name__ == "__main__":
    app()
