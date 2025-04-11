from django.core.management.base import BaseCommand
from api.football_data import sync_competitions, sync_teams, sync_matches, sync_live_matches, sync_league_tables

class Command(BaseCommand):
    help = 'Updates football data from the external API'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--live-only',
            action='store_true',
            help='Update only live match data',
        )
    
    def handle(self, *args, **options):
        if options['live_only']:
            self.stdout.write(self.style.SUCCESS('Updating live match data...'))
            sync_live_matches()
        else:
            self.stdout.write(self.style.SUCCESS('Updating all football data...'))
            # Update competitions
            self.stdout.write('Updating competitions...')
            sync_competitions()
            
            # Update teams for each competition
            self.stdout.write('Updating teams...')
            from competition.models import Competition
            for competition in Competition.objects.all():
                try:
                    self.stdout.write(f'Syncing teams for: {competition.name}')
                    sync_teams(competition.id)
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error updating teams for {competition.name}: {e}'))
            
            # Update matches and tables
            self.stdout.write('Updating matches...')
            sync_matches()
            
            self.stdout.write('Updating league tables...')
            sync_league_tables()
        
        self.stdout.write(self.style.SUCCESS('Data update complete!'))