from django.shortcuts import render, redirect
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage
from rest_framework.response import Response
from rest_framework.views import APIView

from main import models
from main.models import DocumentModel
from main.services.services import Statistic, Player, Rating, BaseResult
from main.serializers import CalendarSerializer

import json
import datetime

MODELS_TYPES = {
    'FirstPm': models.FirstPmModel,
    'SecondPm': models.SecondPmModel,
    'Teams': models.TeamsModel,
    'finals_a': models.FinalsA,
    'finals_b': models.FinalsB,
    'spb_cup': models.SpbCup,
    'spb_championship': models.SpbChampionship
}


class CalendarApiView(APIView):

    def get(self, request):
        events = models.CalendarModel.objects.all()
        events = CalendarSerializer(events, many=True)
        nearest_tournament = models.CalendarModel.objects.filter(date_start__gte=datetime.date.today())
        if nearest_tournament:
            nearest_tournament = CalendarSerializer(nearest_tournament[0], many=False)
            return Response({
                'events': events.data,
                'nearest_tournament': nearest_tournament.data,
            })
        return Response({
            'events': events.data
        })


def index(request):
    nearest_tournament = ''
    news = models.NewsModel.objects.all()[:3]
    month_list = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь',
                  'Ноябрь', 'Декабрь']
    if 'month' in request.GET:
        month = int(request.GET['month'])
    else:
        month = datetime.datetime.now().month
    date_from = datetime.date(datetime.datetime.now().year, month, 1)
    date_to = datetime.date(datetime.datetime.now().year + month // 12, month % 12 + 1, 1) + datetime.timedelta()
    calendar = models.CalendarModel.objects.filter(date_start__gte=date_from, date_start__lt=date_to)
    is_tournament = True
    if not calendar:
        nearest_tournament = models.CalendarModel.objects.filter(date_start__gte=datetime.datetime.now()).first()
        is_tournament = False
    man = models.RatingModel.objects.raw(
        f'''
            SELECT t.id, t.name, t.rang, sum(t1.rating) AS total_rating
            FROM main_playermodel t
            LEFT JOIN main_ratingmodel t1 ON t.id = t1.player_id
            LEFT JOIN main_yearmodel t2 ON t1.year_id = t2.id
            WHERE t.sex = 'man' AND t2.year = {datetime.datetime.now().year}
            GROUP BY t.id, t.name, t.rang
            ORDER BY total_rating DESC
            LIMIT 8
        '''
    )
    woman = models.RatingModel.objects.raw(
        f'''
            SELECT t.id, t.name, t.rang, sum(t1.rating) AS total_rating
            FROM main_playermodel t
            LEFT JOIN main_ratingmodel t1 ON t.id = t1.player_id
            LEFT JOIN main_yearmodel t2 ON t1.year_id = t2.id
            WHERE t.sex = 'woman' AND t2.year = {datetime.datetime.now().year}
            GROUP BY t.id, t.name, t.rang
            ORDER BY total_rating DESC
            LIMIT 8
        '''
    )
    context = {
        'news': news,
        'month_list': month_list,
        'current_month': month_list[month - 1],
        'calendar': calendar,
        'is_tournament': is_tournament,
        'nearest_tournament': nearest_tournament,
        'man': man,
        'woman': woman,
    }
    return render(request, 'index.html', context)


def profile(request, pk):
    try:
        player = models.PlayerModel.objects.get(pk=pk)
    except ObjectDoesNotExist:
        return redirect('/')

    years = models.YearModel.objects.filter(statisticmodel__player=player).order_by('-year')
    years = [item.year for item in years]

    year = int(request.GET.get('year', years[0]))
    year = year if year in years else years[0]

    player_statistic = models.StatisticModel.objects.get(player=player, year__year=year)

    context = {
        'years': years,
        'player': player,
        'statistic': player_statistic,
        'tournaments': []
    }

    all_tournaments = models.ResultsModel.objects.filter(year__year=year).order_by('-date')

    for tournament_obj in all_tournaments:
        if tournament_obj.type == 'no_rating':
            continue

        model = MODELS_TYPES[tournament_obj.type]
        tournament = BaseResult.get_results(player, tournament_obj, model)
        if tournament is not None:
            context['tournaments'].append(tournament)

    return render(request, 'profile.html', context)


def goals(request):
    return render(request, 'goals.html')


def leadership(request):
    return render(request, 'leadership.html')


def documents(request):
    return render(request, 'documents.html')


def protocols(request):
    # TODO проверить протоколы
    return render(request, 'protocols.html')


def calendar(request):
    calendar_file = DocumentModel.objects.filter(type='calendar').order_by('-id').first()
    return render(request, 'calendar.html', context={'calendar_file': calendar_file})


def anti_doping(request):
    documents = DocumentModel.objects.filter(type='anti_doping').order_by('-id')
    return render(request, 'antidoping.html', context={'documents': documents})


def regulations(request):
    years = models.YearModel.objects.all()
    regulations = models.DocumentModel.objects.filter(archive=False, type='regulation', year=years[0])
    context = {
        'years': years[1:],
        'regulations': regulations,
    }
    return render(request, 'regulations.html', context)


def students_tournaments(request):
    return render(request, 'students_tournaments.html')


def contacts(request):
    return render(request, 'contacts.html')


def payment(request):
    return render(request, 'payment.html')


def news_list(request):
    news = models.NewsModel.objects.all()
    paginator = Paginator(news, 6)
    page = request.GET.get('page', 1)
    try:
        sheet = paginator.page(page)
    except EmptyPage:
        sheet = paginator.page(1)
        page = 1
    page_range = list(sheet.paginator.page_range)
    context = {
        'news': sheet.object_list,
        'page': page,
        'page_range': page_range,
        'previous_page_number': sheet.previous_page_number() if sheet.has_previous() else None,
        'next_page_number': sheet.next_page_number() if sheet.has_next() else None,
        'previous2': int(page) - 2,
        'next2': int(page) + 2,
    }
    return render(request, 'news_list.html', context)


def current_news(request, pk):
    try:
        news = models.NewsModel.objects.get(pk=pk)
    except ObjectDoesNotExist:
        return redirect('/')

    news.count += 1
    news.save()
    context = {
        'news': news,
    }
    return render(request, 'current_news.html', context)


def tournaments_list(request):
    reports_list = models.ReportsModel.objects.all()
    paginator = Paginator(reports_list, 6)
    page = request.GET.get('page', 1)
    try:
        sheet = paginator.page(page)
    except EmptyPage:
        sheet = paginator.page(1)
        page = 1
    page_range = list(sheet.paginator.page_range)
    context = {
        'reports': sheet.object_list,
        'page': page,
        'page_range': page_range,
        'previous_page_number': sheet.previous_page_number() if sheet.has_previous() else None,
        'next_page_number': sheet.next_page_number() if sheet.has_next() else None,
        'previous2': int(page) - 2,
        'next2': int(page) + 2,
    }
    return render(request, 'reports_list.html', context)


def current_tournament(request, pk):
    try:
        report = models.ReportsModel.objects.get(pk=pk)
    except ObjectDoesNotExist:
        return redirect('/')

    report.count += 1
    report.save()
    context = {
        'report': report,
    }
    return render(request, 'current_report.html', context)


def results(request):
    years = models.YearModel.objects.all()
    years = [item.year for item in years]
    year = int(request.GET.get('year', years[0]))
    year = year if year in years else years[0]

    all_results = models.ResultsModel.objects.filter(year__year=year)
    return render(request, 'results.html', context={
        'results': all_results,
        'years': years
    })


def statistic(request):
    years = models.YearModel.objects.all()
    years = [item.year for item in years]
    year = int(request.GET.get('year', years[0]))
    year = year if year in years else years[0]

    man = models.StatisticModel.objects.filter(year__year=year, player__sex='man')
    women = models.StatisticModel.objects.filter(year__year=year, player__sex='woman')

    context = {
        'years': years,
        'man': man,
        'women': women
    }
    return render(request, 'statistics.html', context)


def rating(request):
    years = models.YearModel.objects.all()
    years = [item.year for item in years]
    year = int(request.GET.get('year', years[0]))
    year = year if year in years else years[0]

    all_tournaments = models.ResultsModel.objects.filter(year__year=year, format='rating').order_by('date')

    columns = [item.short_form for item in all_tournaments]
    columns.insert(0, 'Спортсмен')
    columns.append('Сумма')

    players = {}
    default_player = {key: 0 for key in columns}
    default_player['Сумма'] = 0

    for tournament_obj in all_tournaments:
        tournament_rating = models.RatingModel.objects.select_related('player', 'tournament') \
            .filter(tournament=tournament_obj, year__year=year)

        for player_rating in tournament_rating:
            player_name = player_rating.player.name
            tournament_name = player_rating.tournament.short_form
            players[player_name] = players.get(player_name, default_player.copy())
            players[player_name][tournament_name] = player_rating.rating
            players[player_name]['Сумма'] += player_rating.rating
            players[player_name]['Спортсмен'] = player_name

    man = models.RatingModel.objects.raw(
        f'''
                SELECT t.id, t.name, t.rang, sum(t1.rating) AS total_rating
                FROM main_playermodel t
                LEFT JOIN main_ratingmodel t1 ON t.id = t1.player_id
                LEFT JOIN main_yearmodel t2 ON t1.year_id = t2.id
                WHERE t.sex = 'man' AND t2.year = {year}
                GROUP BY t.id, t.name, t.rang
                ORDER BY total_rating DESC
            '''
    )
    woman = models.RatingModel.objects.raw(
        f'''
                    SELECT t.id, t.name, t.rang, sum(t1.rating) AS total_rating
                    FROM main_playermodel t
                    LEFT JOIN main_ratingmodel t1 ON t.id = t1.player_id
                    LEFT JOIN main_yearmodel t2 ON t1.year_id = t2.id
                    WHERE t.sex = 'woman' AND t2.year = {year}
                    GROUP BY t.id, t.name, t.rang
                    ORDER BY total_rating DESC
                '''
    )

    sorted_man_players = [[players[player.name][column] for column in columns if players.get(player.name)] for player in
                          man]
    sorted_woman_players = [[players[player.name][column] for column in columns if players.get(player.name)] for player
                            in woman]

    try:
        rating_docs = models.DocumentModel.objects.get(type='rating', year__year=year)
    except ObjectDoesNotExist:
        rating_docs = None

    context = {
        'years': years,
        'columns': columns,
        'man': sorted_man_players,
        'woman': sorted_woman_players,
        'rating_docs': rating_docs
    }
    return render(request, 'rating.html', context)


@csrf_exempt
def parse_results(request):
    data = json.loads(request.body)
    created_people = []
    tournament = models.ResultsModel.objects.get(pk=data['id'])
    year = tournament.year
    model = MODELS_TYPES[data['type']]

    with transaction.atomic():
        for item in data['man']:
            player, created = Player.get_player(item, 'man')

            if created:
                created_people.append(player.name)

            Statistic.load_statistic(player.pk, item, year)

            BaseResult.upload_results(model, item, year, player, tournament)

        for item in data['woman']:
            player, created = Player.get_player(item, 'woman')

            if created:
                created_people.append(player.name)

            Statistic.load_statistic(player.pk, item, year)

            BaseResult.upload_results(model, item, year, player, tournament)

    Rating.upload_rating(data['type'], year, tournament)

    return JsonResponse(data={'result': created_people}, status=200)
