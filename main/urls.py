from django.urls import path
from main import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.index, name='index'),
    path('profile/<int:pk>/', views.profile, name='profile'),
    path('calendar/', views.calendar, name='calendar'),
    path('goals/', views.goals, name='goals'),
    path('leadership/', views.leadership, name='leadership'),
    path('documents/', views.documents, name='documents'),
    path('protocols/', views.protocols, name='protocols'),
    path('regulations/', views.regulations, name='regulations'),
    path('studentsTournaments/', views.students_tournaments, name='students_tournaments'),
    path('contacts/', views.contacts, name='contacts'),
    path('payment/', views.payment, name='payment'),
    path('news/', views.news_list, name='news_list'),
    path('anti-doping/', views.anti_doping, name='anti-doping'),
    path('news/<int:pk>/', views.current_news, name='current_news'),
    path('tournaments/', views.tournaments_list, name='reports_list'),
    path('tournaments/<int:pk>/', views.current_tournament, name='current_report'),
    path('results/', views.results, name='results'),
    path('statistic/', views.statistic, name='statistic'),
    path('rating/', views.rating, name='rating'),
    path('api/parse_results/', views.parse_results),
    path('api/calendar/', views.CalendarApiView.as_view()),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
