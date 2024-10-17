from django.shortcuts import render, redirect, get_object_or_404
from .models import Owner, Team, Player, Auction
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from collections import Counter

def team_dashboard(request, url_name):
    # Get the team instance by ID
    # team = get_object_or_404(Team, id=team_id)
    team = get_object_or_404(Team, url_name=url_name)
    print(team, "FFFFFFFFFFFFFFFF")
    owners = [team.owner1, team.owner2]

    # Fetch all players for this team
    players = Player.objects.filter(team=team)

    return render(request, 'auction/dashboard.html', {
        'owner': owners,

        'team': team,
        'players': players,
    })


# @login_required
def main_dashboard(request):
    teams = Team.objects.all()
    # teams = Team.objects.prefetch_related('owner')
    players = Player.objects.all()
    recent_auctions = Auction.objects.select_related('team').order_by('-id')[:10]

    team_counts = Counter(player.team for player in players)
    
    team_players = {
        team: {
            'players': [player for player in players if player.team == team],
            'count': team_counts[team],  # More efficient way to get count
        }
        for team in teams
    }

    # This seems to be for debugging; consider removing or logging instead.
    team_colors = Team.objects.values_list('color', flat=True)  # Adjust based on actual field
    print(list(team_colors))  # Print the list of team colors

    # Also for debugging; consider logging instead of printing.
    # for player in players:
    #     print(player.player_type.image)  # Assuming this is for debugging
    count = 0
    for player in players:
        if player.player_type and player.player_type.image:
            count += 1
            print(player.player_type.image.url, "Image URL", count)  # Ensure this prints a valid URL
    context = {
        'teams': teams,
        'team_players': team_players,
        'players': players,
        'team_counts': team_counts,
        'recent_auctions': recent_auctions,
    }
    # return render(request, 'your_template_name.html', context)
    return render(request, 'auction/main_dashboard.html', context)
