from django.contrib import admin
from django.urls import path, include
from . import views
from predictions.views import RegisterView

app_name = 'predictions'

urlpatterns = [
    # Homepage
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('predictions/', views.index, name='predictions_index'),
    path('', views.index, name='index'),  # localhost:8000/
    path('submit_predictions/', views.submit_predictions, name='submit_predictions'),
    path('get-scores/', views.get_real_scores, name='get_real_scores'),
    path('get-predictions/', views.get_predictions, name='get_predictions'),
    path('get-total-points/', views.get_total_points, name='get_total_points'),
    path('update-points/', views.update_points, name='update_points'),
    path('update-standings-points/', views.update_standings_points, name='update_standings_points'),
]