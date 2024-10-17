from django.db import models
from django.contrib.auth.models import User

class Owner(models.Model):
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    def get_teams(self):
        return Team.objects.filter(owner1=self) | Team.objects.filter(owner2=self)

class Team(models.Model):

    owner1 = models.ForeignKey(Owner, on_delete=models.CASCADE, related_name='team_owner1')
    owner2 = models.ForeignKey(Owner, on_delete=models.CASCADE, related_name='team_owner2')
    name = models.CharField(max_length=100)
    balance = models.IntegerField()
    color = models.CharField(max_length=7, default="#ffffff")
    secondary_color = models.CharField(max_length=7, default="#ffffff")
    font_color = models.CharField(max_length=7, default="#ffffff")
    url_name = models.CharField(max_length=100, default='1')
    def __str__(self):
        return self.name

    def get_players(self):
        return Player.objects.filter(team=self)

class PlayerType(models.Model):
    name = models.CharField(max_length=20, unique=True)
    image = models.ImageField(upload_to='auction/media/')

    def __str__(self):
        return self.name


class Player(models.Model):

    PLAYER_TYPE_CHOICES = [
        ('Batsman', 'Batsman'),
        ('Bowler', 'Bowler'),
        ('WicketKeeper', 'WicketKeeper'),
        ('All Rounder', 'All Rounder')
    ]
    name = models.CharField(max_length=100)
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True)
    is_sold = models.BooleanField(default=False)
    sold_price = models.IntegerField(null=True, blank=True)
    base_price = models.IntegerField()
    count = models.PositiveIntegerField(null=True, blank=True)
    player_type = models.ForeignKey(PlayerType, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.team.name if self.team else 'No Team'}) - Count: {self.count}"
 
    def save(self, *args, **kwargs):
        """
        Save the player instance, updating the team balance if sold and
        ensuring the player count does not exceed 12 for any team.
        """
        if self.is_sold and self.team and self.sold_price:
            if self.team.balance >= self.sold_price:
                self.team.balance -= self.sold_price
                self.team.save()  # Save the updated balance
            else:
                self.error_message = "Insufficient team balance."
                return  # Prevent further execution

        if self.team:
            current_player_count = Player.objects.filter(team=self.team).count()
            if current_player_count >= 12:
                self.error_message = f"Cannot add more than 12 players to {self.team.name}."
                return  # Prevent saving if the count is exceeded
            # Set the player's count
            self.count = current_player_count + 1  # Assign count 1 to 12

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Delete the player instance, refunding the sold price to the team's balance 
        and updating the counts of remaining players.
        """
        if self.is_sold and self.sold_price:
            # Refund the sold price back to the team's balance
            if self.team:
                self.team.balance += self.sold_price
                self.team.save()  # Save the updated balance

        # Update the counts of other players in the same team
        if self.team:
            existing_players = Player.objects.filter(team=self.team).exclude(id=self.id)
            for player in existing_players:
                if player.count > self.count:  # Only decrement counts for players with higher counts
                    player.count -= 1
                    player.save()

        super().delete(*args, **kwargs)  # Call the superclass delete method

class Auction(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    bidder_name = models.CharField(max_length=100)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)  # Add this field

    def __str__(self):
        return f"{self.player.name} - {self.bidder_name} ({self.team.name}): {self.bid_amount}"

