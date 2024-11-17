from django.contrib import admin
from .models import RealMatch, UserPrediction

@admin.register(RealMatch)
class RealMatchAdmin(admin.ModelAdmin):
    list_display = ('match_id', 'team1', 'team2', 'score1', 'score2', 'date', 'completed')
    list_filter = ('completed', 'date')
    search_fields = ('team1', 'team2', 'match_id')
    ordering = ('date',)

@admin.register(UserPrediction)
class UserPredictionAdmin(admin.ModelAdmin):
    list_display = ('user', 'match', 'prediction_score1', 'prediction_score2', 'earned_points', 'timestamp')
    list_filter = ('user', 'match', 'earned_points')
    search_fields = ('user__username', 'match__team1', 'match__team2')
    ordering = ('-timestamp',)
