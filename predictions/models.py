from django.db import models
from django.contrib.auth.models import User

class RealMatch(models.Model):
    match_id = models.CharField(max_length=20, unique=True)
    team1 = models.CharField(max_length=100)
    team2 = models.CharField(max_length=100)
    score1 = models.IntegerField(null=True, blank=True)
    score2 = models.IntegerField(null=True, blank=True)
    date = models.DateTimeField()
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.team1} vs {self.team2}"

    def get_result_type(self):
        if self.score1 is None or self.score2 is None:
            return None
        if self.score1 > self.score2:
            return 'HOME_WIN'
        elif self.score1 < self.score2:
            return 'AWAY_WIN'
        return 'DRAW'

class UserPrediction(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    match = models.ForeignKey(RealMatch, on_delete=models.CASCADE)
    prediction_score1 = models.IntegerField()
    prediction_score2 = models.IntegerField()
    earned_points = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'match']

    def __str__(self):
        return f"{self.user.username}'s prediction for {self.match}"
    
    def get_result_type(self):
        if self.prediction_score1 > self.prediction_score2:
            return 'HOME_WIN'
        elif self.prediction_score1 < self.prediction_score2:
            return 'AWAY_WIN'
        return 'DRAW'
