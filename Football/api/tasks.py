"""
Tasks for regularly updating data from the Football-Data API.

To run these automatically, set up Celery and create scheduled tasks, or use Django's
management commands with cron jobs.
"""

from .football_data import sync_competitions, sync_teams, sync_matches, sync_live_matches, sync_league_tables


def update_all_data():
    """Update all data in sequence"""
    print("Starting data update process...")
    
    print("Updating competitions...")
    try:
        sync_competitions()
        print("Competitions updated successfully")
    except Exception as e:
        print(f"Error updating competitions: {e}")
    
    print("Updating teams...")
    # For each competition ID in your system
    from competition.models import Competition
    competitions = Competition.objects.all()
    print(f"Found {competitions.count()} competitions to update teams for")
    
    for competition in competitions:
        try:
            print(f"Syncing teams for competition: {competition.name}")
            sync_teams(competition.id)
            print(f"Teams for {competition.name} updated successfully")
        except Exception as e:
            print(f"Error updating teams for {competition.name}: {e}")
    
    print("Updating matches...")
    try:
        sync_matches()
        print("Matches updated successfully")
    except Exception as e:
        print(f"Error updating matches: {e}")
    
    print("Updating league tables...")
    try:
        sync_league_tables()
        print("League tables updated successfully")
    except Exception as e:
        print(f"Error updating league tables: {e}")
    
    print("Data update complete!")