from django.contrib import admin
from .models import Team, Owner, Player, Auction, PlayerType
admin.site.register(Team)
admin.site.register(Owner)
admin.site.register(Player)
admin.site.register(Auction)
admin.site.register(PlayerType)

