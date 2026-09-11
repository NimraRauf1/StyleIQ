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
        modesty_level=ModestyLevel.MODEST_FULL_COVERAGE, eastern_western_preference=0.4,
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
    for name, score in dna.top_aesthetics:
        bar = "█" * int(score / 5) + "░" * (20 - int(score / 5))
        console.print(f"    {name:<15} {bar} {score:.0f}/100")
    console.print()
    console.print(Panel("[green]✓ All schemas validated successfully.[/green]", border_style="green"))
    console.print()
    log.info("Demo completed successfully")

@app.command()
def taxonomy():
    """Show the Pakistani fashion taxonomy summary."""
    settings, log = _startup()
    from styleiq.taxonomy.service import taxonomy as tx
    console.print()
    console.print(Panel("[bold gold1]STYLEIQ Fashion Taxonomy[/bold gold1]", border_style="gold1"))
    summary = tx.summary()
    console.print("\n[bold cyan]Taxonomy Summary[/bold cyan]")
    for key, value in summary.items():
        console.print(f"  {key:<25} [green]{value}[/green]")
    console.print("\n[bold cyan]Garment Families[/bold cyan]")
    for family in tx.get_all_families():
        console.print(f"  [gold1]{family['name']}[/gold1] — {len(family['categories'])} categories")
    console.print("\n[bold cyan]Wedding Occasions[/bold cyan]")
    for occ in tx.get_wedding_occasions():
        console.print(f"  • {occ['name']} — modesty common: {occ['modesty_common']}/5")
    console.print()

@app.command()
def brands():
    """Show brand intelligence — compatibility scores for a sample user profile."""
    settings, log = _startup()
    from styleiq.services.brand_service import brand_service

    console.print()
    console.print(Panel("[bold gold1]STYLEIQ Brand Intelligence[/bold gold1]", border_style="gold1"))

    # Sample user profile — university student, Islamabad, modest, minimal aesthetic
    console.print("\n[bold cyan]User Profile (Sample)[/bold cyan]")
    console.print("  Age: 22 | City: Islamabad | University Student")
    console.print("  Budget: PKR 2,000 – 8,000")
    console.print("  Modesty: 4/5 (Modest)")
    console.print("  Aesthetics: minimal, feminine, contemporary")
    console.print("  Occasions: university, brunch, dawat, eid")

    console.print("\n[bold cyan]Top 5 Compatible Brands For You[/bold cyan]")
    top_brands = brand_service.get_compatible_brands(
        user_budget_min=2000,
        user_budget_max=8000,
        user_modesty_level=4,
        user_style_tags=["minimal", "feminine"],
        user_aesthetics=["minimal", "feminine", "contemporary"],
        user_occasions=["university", "brunch", "dawat", "eid"],
        top_n=5,
    )

    for i, score in enumerate(top_brands, 1):
        console.print(f"\n  [bold]{i}. {score.brand_name}[/bold] [{score.brand_tier}]")
        console.print(f"     Overall:  [bold green]{score.overall_score}/100[/bold green]")
        console.print(f"     Style:    {score.style_match}/100  |  Budget: {score.budget_match}/100  |  Modesty: {score.modesty_match}/100  |  Occasion: {score.occasion_match}/100")
        console.print(f"     Price:    PKR {score.typical_price_min:,}–{score.typical_price_max:,}")
        console.print(f"     Summary:  [dim]{score.summary}[/dim]")

    console.print("\n[bold cyan]Full Brand Report — Khaadi[/bold cyan]")
    report = brand_service.get_brand_report("khaadi")
    if report:
        console.print(f"  Name:          {report.name}")
        console.print(f"  Tier:          {report.tier}")
        console.print(f"  Price Range:   {report.price_tier_label}")
        console.print(f"  Modesty:       {report.modesty_label}")
        console.print(f"  Style:         {report.eastern_western_label}")
        console.print(f"  Style Tags:    {', '.join(report.style_tags)}")
        console.print(f"  Best For:      {', '.join(report.best_for_occasions)}")
        console.print(f"  Not Ideal For: {', '.join(report.not_ideal_for)}")
    console.print()

if __name__ == "__main__":
    app()
