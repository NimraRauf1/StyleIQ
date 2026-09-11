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
        ("Environment",    status_obj.environment),
        ("Data Directory", "✓ exists" if status_obj.data_dir_exists else "✗ missing"),
        ("Database",       "✗ not connected (Milestone 2)" if not status_obj.database_connected else "✓ connected"),
        ("Claude API",     "✓ configured" if status_obj.claude_configured else "✗ not configured"),
        ("Default City",   settings.weather.default_city),
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
    console.print(f"  Profile: {profile.age}y | {profile.city} | PKR {profile.budget_min:,}-{profile.budget_max:,}")
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
    """Show trend intelligence."""
    settings, log = _startup()
    from styleiq.services.trend_service import trend_service
    console.print()
    console.print(Panel("[bold gold1]STYLEIQ Trend Intelligence[/bold gold1]", border_style="gold1"))
    console.print("\n[bold cyan]Trending Now — Pakistan Fashion[/bold cyan]")
    top_trends = trend_service.get_trending_now(top_n=5)
    for i, t in enumerate(top_trends, 1):
        status_color = {"emerging": "yellow", "rising": "green", "peaking": "bold green", "declining": "red"}.get(t.status, "white")
        console.print(f"\n  [bold]{i}. {t.trend_name}[/bold] [{t.category}]")
        console.print(f"     Status: [{status_color}]{t.status.upper()}[/{status_color}]  Score: [bold]{t.total_score}/100[/bold]")
        console.print(f"     Popularity: {t.popularity_score}  Growth: {t.growth_score}  Cross-Brand: {t.cross_brand_score}  Seasonal: {t.seasonal_score}")
        if t.growth_rate_pct is not None:
            console.print(f"     Growth Rate: {t.growth_rate_pct:+.1f}% search volume")
    console.print()

@app.command()
def dna():
    """Run Style DNA demo — onboarding, interactions, evolution."""
    settings, log = _startup()
    from styleiq.services.style_dna_service import style_dna_service

    console.print()
    console.print(Panel("[bold gold1]STYLEIQ Style DNA Demo[/bold gold1]", border_style="gold1"))

    # Create test user
    console.print("\n[bold cyan]1. Creating User[/bold cyan]")
    user_id = style_dna_service.create_user(
        email="nimra@styleiq.demo",
        username="nimra_demo",
    )
    console.print(f"  User ID: {user_id[:16]}...")

    # Seed from onboarding
    console.print("\n[bold cyan]2. Seeding Style DNA from Onboarding[/bold cyan]")
    console.print("  Age: 22 | City: Islamabad | Modesty: 4/5")
    console.print("  Aesthetics: minimal, feminine, contemporary")
    console.print("  Occasions: university, brunch, dawat, eid")

    initial_dna = style_dna_service.seed_from_onboarding(
        user_id=user_id,
        age=22,
        city="islamabad",
        modesty_level=4,
        eastern_western_pref=0.4,
        preferred_aesthetics=["minimal", "feminine", "contemporary"],
        preferred_silhouettes=["a_line", "straight", "relaxed"],
        preferred_colors=["beige", "white", "olive"],
        usual_occasions=["university", "brunch", "dawat", "eid"],
        budget_min=2000,
        budget_max=8000,
    )

    console.print(f"\n  [dim]Initial DNA (Version {initial_dna.version}):[/dim]")
    dims_initial = {
        "Minimal": initial_dna.minimal,
        "Feminine": initial_dna.feminine,
        "Traditional": initial_dna.traditional,
        "Contemporary": initial_dna.contemporary,
        "Eastern Affinity": initial_dna.eastern_affinity,
        "Modesty": initial_dna.modesty_score,
    }
    for name, score in dims_initial.items():
        bar = "█" * int(score / 5) + "░" * (20 - int(score / 5))
        console.print(f"  {name:<18} {bar} {score:.1f}")

    archetype = style_dna_service.get_style_archetype(initial_dna)
    console.print(f"\n  Style Archetype: [bold gold1]{archetype}[/bold gold1]")

    # Simulate interactions
    console.print("\n[bold cyan]3. Simulating Interactions[/bold cyan]")
    interactions = [
        ("like",    ["minimal", "contemporary", "clean_girl"], "western",  2, "Liked a minimal western co-ord"),
        ("save",    ["feminine", "romantic", "modest"],        "eastern",  4, "Saved a feminine modest kurta"),
        ("like",    ["minimal", "classic"],                    "eastern",  3, "Liked a classic straight shirt"),
        ("dislike", ["maximalist", "colorful"],                "eastern",  3, "Disliked a maximalist printed suit"),
        ("skip",    ["streetwear", "edgy"],                    "western",  1, "Skipped a streetwear outfit"),
        ("like",    ["feminine", "minimal", "soft_girl"],      "western",  3, "Liked a soft minimal dress"),
        ("save",    ["traditional", "ethnic"],                 "eastern",  4, "Saved an ethnic embroidered 3-piece"),
    ]
    for itype, tags, family, modesty, desc in interactions:
        style_dna_service.update_from_interaction(
            user_id=user_id,
            interaction_type=itype,
            item_aesthetic_tags=tags,
            item_garment_family=family,
            item_modesty_level=modesty,
        )
        emoji = "♥" if itype == "like" else "★" if itype == "save" else "✗" if itype == "dislike" else "→"
        console.print(f"  {emoji} [{itype.upper()}] {desc}")

    # Show evolved DNA
    console.print("\n[bold cyan]4. Evolved Style DNA[/bold cyan]")
    final_dna = style_dna_service.get_current_dna(user_id)
    console.print(f"  [dim]DNA after {final_dna.interaction_count} interactions (Version {final_dna.version}):[/dim]\n")

    all_dims = {
        "Minimal":         (initial_dna.minimal,          final_dna.minimal),
        "Feminine":        (initial_dna.feminine,         final_dna.feminine),
        "Traditional":     (initial_dna.traditional,      final_dna.traditional),
        "Contemporary":    (initial_dna.contemporary,     final_dna.contemporary),
        "Romantic":        (initial_dna.romantic,         final_dna.romantic),
        "Streetwear":      (initial_dna.streetwear,       final_dna.streetwear),
        "Eastern Affinity":(initial_dna.eastern_affinity, final_dna.eastern_affinity),
        "Modesty":         (initial_dna.modesty_score,    final_dna.modesty_score),
    }
    for name, (before, after) in all_dims.items():
        bar = "█" * int(after / 5) + "░" * (20 - int(after / 5))
        change = after - before
        if change > 0.5:
            arrow = f"[green]+{change:.1f}[/green]"
        elif change < -0.5:
            arrow = f"[red]{change:.1f}[/red]"
        else:
            arrow = f"[dim]{change:.1f}[/dim]"
        console.print(f"  {name:<18} {bar} {after:.1f}  ({arrow})")

    final_archetype = style_dna_service.get_style_archetype(final_dna)
    console.print(f"\n  Style Archetype: [bold gold1]{final_archetype}[/bold gold1]")

    # DNA history
    history = style_dna_service.get_dna_history(user_id)
    console.print(f"\n[bold cyan]5. DNA Version History[/bold cyan]")
    console.print(f"  {len(history)} versions stored")
    console.print(f"  Version 1 → onboarding seed")
    console.print(f"  Version {len(history)} → current (after {final_dna.interaction_count} interactions)")
    console.print()

if __name__ == "__main__":
    app()
