from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import RealMatch, UserPrediction
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.decorators.http import require_http_methods
from django.db import models
from .models import UserPrediction
from django.utils import timezone
import json

import logging
logger = logging.getLogger(__name__)

def calculate_prediction_points(real_score1, real_score2, pred_score1, pred_score2):
    # Exact score prediction (5 points)
    if real_score1 == pred_score1 and real_score2 == pred_score2:
        return 5
    
    # Correct result type (win/draw/loss) but not exact score (3 points)
    real_result = 'DRAW' if real_score1 == real_score2 else 'HOME_WIN' if real_score1 > real_score2 else 'AWAY_WIN'
    pred_result = 'DRAW' if pred_score1 == pred_score2 else 'HOME_WIN' if pred_score1 > pred_score2 else 'AWAY_WIN'
    
    if real_result == pred_result:
        return 3
    
    # Wrong prediction (0 points)
    return 0

@login_required
def index(request):
    context = {
        'teams': {
            'Germany': {'flag': 'https://flagcdn.com/de.svg'},
            'Scotland': {'flag': 'https://flagcdn.com/gb-sct.svg'},
            'Hungary': {'flag': 'https://flagcdn.com/hu.svg'},
            'Switzerland': {'flag': 'https://flagcdn.com/ch.svg'}
        }
    }
    return render(request, 'predictions/index.html', context)

@login_required
def submit_predictions(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)

    try:
        print("Request body:", request.body.decode('utf-8'))  # Debug print
        data = json.loads(request.body)
        print("Parsed data:", data)  # Debug print
        
        if 'predictions' not in data:
            return JsonResponse({'error': 'No predictions found in request'}, status=400)

        prediction_results = []
        total_points = 0

        for match_id, scores in data['predictions'].items():
            print(f"Processing match {match_id} with scores {scores}")  # Debug print
            
            try:
                match = RealMatch.objects.get(match_id=match_id)
                
                prediction, created = UserPrediction.objects.update_or_create(
                    user=request.user,
                    match=match,
                    defaults={
                        'prediction_score1': scores['score1'],
                        'prediction_score2': scores['score2']
                    }
                )
                
                print(f"Prediction {'created' if created else 'updated'} for match {match_id}")  # Debug print

                prediction_results.append({
                    'match_id': match_id,
                    'prediction': f"{scores['score1']}-{scores['score2']}",
                    'status': 'saved'
                })

            except RealMatch.DoesNotExist:
                print(f"Match {match_id} not found")  # Debug print
                return JsonResponse({'error': f'Match {match_id} not found'}, status=404)
            except Exception as e:
                print(f"Error processing match {match_id}: {str(e)}")  # Debug print
                return JsonResponse({'error': f'Error processing match {match_id}: {str(e)}'}, status=500)

        return JsonResponse({
            'success': True,
            'predictions': prediction_results
        })

    except json.JSONDecodeError as e:
        print("JSON decode error:", str(e))  # Debug print
        return JsonResponse({'error': f'Invalid JSON data: {str(e)}'}, status=400)
    except Exception as e:
        print("Unexpected error:", str(e))  # Debug print
        return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)

@login_required
def get_real_scores(request):
    matches = RealMatch.objects.filter(completed=True)
    scores = [
        {
            'match_id': match.match_id,
            'score1': match.score1,
            'score2': match.score2,
            'completed': match.completed,
            'has_result': match.score1 is not None and match.score2 is not None,
            'team1': match.team1,
            'team2': match.team2
        }
        for match in matches
    ]
    return JsonResponse({'scores': scores})

class RegisterView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/register.html'
    
@login_required
def get_total_points(request):
    total_points = UserPrediction.objects.filter(
        user=request.user
    ).aggregate(total=models.Sum('earned_points'))['total']
    print('Total points calculated:', total_points)
    return JsonResponse({'total_points': total_points})

def get_predictions(request):
    try:
        predictions = UserPrediction.objects.filter(user=request.user).select_related('match')
        
        predictions_data = []
        for pred in predictions:
            predictions_data.append({
                'id': pred.id,
                'match_id': pred.match.match_id,
                'score1': pred.prediction_score1,
                'score2': pred.prediction_score2
            })
        
        return JsonResponse({'predictions': predictions_data})
        
    except Exception as e:
        print(f"Error in get_predictions: {str(e)}")
        return JsonResponse({'error': 'Failed to fetch predictions'}, status=500)

@login_required
@require_http_methods(["POST"])
def update_points(request):
    try:
        data = json.loads(request.body)
        points_data = data.get('points_data', [])
        
        for item in points_data:
            prediction = UserPrediction.objects.filter(
                id=item['prediction_id'],
                user=request.user
            ).first()
            
            if prediction:
                prediction.earned_points = item['points']
                prediction.save()
        
        return JsonResponse({'success': True, 'message': 'Points updated successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
@login_required
@require_http_methods(["POST"])
def update_standings_points(request):
    try:
        # First check if all matches are completed
        total_matches = RealMatch.objects.exclude(match_id='STANDINGS_BONUS').count()
        completed_matches = RealMatch.objects.filter(
            completed=True
        ).exclude(match_id='STANDINGS_BONUS').count()
        
        # Get match points first
        match_points = UserPrediction.objects.filter(
            user=request.user
        ).exclude(
            match__match_id='STANDINGS_BONUS'
        ).aggregate(total=models.Sum('earned_points'))['total'] or 0
        
        # Only calculate standings points if all matches are completed
        if total_matches == completed_matches == 6:  # All 6 group matches completed
            # Get the data from the request
            data = json.loads(request.body)
            prediction_icons = data.get('prediction_icons', [])
            
            # Calculate standings points based on icons
            standings_points = 0
            for icon in prediction_icons[:2]:  # Only check top 2 positions
                if icon == '🎯':  # Exact position match
                    standings_points += 6
                elif icon == '✅':  # Qualified but wrong position
                    standings_points += 4
                
            print('Standings points:', standings_points)
            
            # Save the standings points in a special prediction
            special_match, _ = RealMatch.objects.get_or_create(
                match_id='STANDINGS_BONUS',
                defaults={
                    'team1': 'Standings',
                    'team2': 'Bonus',
                    'date': timezone.now(),
                    'completed': True
                }
            )
            
            prediction, _ = UserPrediction.objects.update_or_create(
                user=request.user,
                match=special_match,
                defaults={
                    'prediction_score1': 0,
                    'prediction_score2': 0,
                    'earned_points': standings_points
                }
            )
            
            total_points = match_points + standings_points
        else:
            # If not all matches completed, return only match points
            standings_points = 0
            total_points = match_points
        
        return JsonResponse({
            'success': True,
            'standings_points': standings_points,
            'match_points': match_points,
            'total_points': total_points,
            'all_matches_completed': total_matches == completed_matches == 6
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)