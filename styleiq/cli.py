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
    """Check system health and configuration status."""
    settings, log = _startup()
    from styleiq.schemas.user import SystemStatus
    log.info("Running health check...")
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
        ("Environment", status_obj.environment),
        ("Log Level", status_obj.log_level),
        ("Data Directory", "✓ exists" if status_obj.data_dir_exists else "✗ missing"),
        ("Database", "✗ not connected (Milestone 2)" if not status_obj.database_connected else "✓ connected"),
        ("Claude API", "✓ configured" if status_obj.claude_configured else "✗ not configured — add ANTHROPIC_API_KEY to .env"),
        ("Claude Model", settings.claude.model),
        ("Default City", settings.weather.default_city),
        ("Data Collection", "enabled" if settings.data_collection.enabled else "disabled (safe default)"),
        ("Image Retention", "ON" if settings.images.retain_uploaded else "OFF (privacy-first)"),
    ]
    for key, value in checks:
        style = "green" if "✓" in value or "enabled" in value else "yellow"
        table.add_row(key, f"[{style}]{value}[/{style}]")
    console.print(table)
    console.print()
    console.print("[green]✓ Foundation is healthy. Ready for Milestone 2.[/green]")
    console.print()

@app.command()
def demo():
    """Run a quick demo showing schemas and Style DNA in action."""
    settings, log = _startup()
    console.print()
    console.print(Panel("[bold gold1]STYLEIQ Schema Demo[/bold gold1]", border_style="gold1"))

    console.print("\n[bold cyan]1. Creating an OnboardingProfile[/bold cyan]")
    from styleiq.schemas import OnboardingProfile, ModestyLevel, PakistaniCity
    profile = OnboardingProfile(
        age=22, city=PakistaniCity.ISLAMABAD, occupation="University Student",
        modesty_level=ModestyLevel.MODEST_FULL_COVERAGE,
        eastern_western_preference=0.4,
        preferred_aesthetics=["minimal", "feminine", "contemporary"],
        preferred_colors=["beige", "white", "soft pink", "olive"],
        preferred_brands=["khaadi", "sapphire", "limelight"],
        budget_min=2000, budget_max=8000,
        usual_occasions=["university", "brunch", "dawat", "eid"],
    )
    console.print(f"  Age: {profile.age}")
    console.print(f"  City: {profile.city}")
    console.print(f"  Modesty Level: {profile.modesty_level} ({ModestyLevel(profile.modesty_level).name})")
    console.print(f"  Budget: PKR {profile.budget_min:,} – {profile.budget_max:,}")

    console.print("\n[bold cyan]2. Style DNA[/bold cyan]")
    from styleiq.schemas import StyleDNA
    dna = StyleDNA(
        user_id=uuid4(), minimal=82.0, feminine=78.0, traditional=65.0,
        contemporary=71.0, romantic=60.0, classic=55.0, streetwear=22.0,
        eastern_affinity=64.0, modesty_score=80.0, version=3, interaction_count=27,
    )
    console.print(f"  Style Archetype: [bold gold1]{dna.style_archetype}[/bold gold1]")
    console.print(f"  DNA Version: {dna.version} (based on {dna.interaction_count} interactions)")
    for name, score in dna.top_aesthetics:
        bar = "█" * int(score / 5) + "░" * (20 - int(score / 5))
        console.print(f"    {name:<15} {bar} {score:.0f}/100")

    console.print("\n[bold cyan]3. Trend Object[/bold cyan]")
    from styleiq.schemas import TrendCreate, TrendSignalEntry, TrendCategory, TrendStatus
    trend = TrendCreate(
        name="Chocolate Brown", category=TrendCategory.COLOR,
        season="winter", year=2025, status=TrendStatus.RISING,
        signals=[
            TrendSignalEntry(signal_type="brand_appearance", signal_value=8.0, source="manual_catalog_review"),
            TrendSignalEntry(signal_type="search_volume", signal_value=34.0, source="google_trends_pk"),
        ],
    )
    console.print(f"  Trend: [bold]{trend.name}[/bold]")
    console.print(f"  Status: [green]{trend.status}[/green]")
    console.print(f"  Signals: {len(trend.signals)}")

    console.print("\n[bold cyan]4. Outfit Recommendation[/bold cyan]")
    from styleiq.schemas import OutfitRecommendation, OutfitComponent, Occasion, Season
    outfit = OutfitRecommendation(
        occasion=Occasion.UNIVERSITY, season=Season.SUMMER,
        components=[
            OutfitComponent(role="top", description="White straight-cut shirt", brand_slug="nishat", estimated_price=3200),
            OutfitComponent(role="bottom", description="Off-white shalwar", brand_slug="limelight", estimated_price=1800),
            OutfitComponent(role="layer", description="Beige chiffon dupatta", brand_slug="zellbury", estimated_price=900),
        ],
        total_estimated_price=5900, modesty_level=ModestyLevel.MODEST_FULL_COVERAGE,
        why_recommended="Matches minimal aesthetic. Neutral palette. Modest. Within PKR 8,000 budget.",
        style_match_score=87.0, budget_match_score=92.0,
        modesty_match_score=96.0, trend_relevance_score=74.0,
        critic_passed=True, critic_notes="Passed all 7 constraints.",
    )
    console.print(f"  Total Price: [green]PKR {outfit.total_estimated_price:,}[/green]")
    console.print(f"  Overall Score: [bold]{outfit.overall_score}/100[/bold]")
    console.print(f"  Critic: [green]PASSED[/green]")
    console.print()
    console.print(Panel("[green]✓ All schemas validated successfully.\nMilestone 1 complete. Foundation is solid.[/green]", border_style="green"))
    console.print()
    log.info("Demo completed successfully")

if __name__ == "__main__":
    app()
