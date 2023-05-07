from django.core.exceptions import ObjectDoesNotExist

from main import models


class BaseResult:
    @staticmethod
    def get_result_for_statistic(tournament_obj):
        games = []
        count = 1
        games_sum = 0
        more_200 = 0

        while getattr(tournament_obj, f'game_{count}', False):
            game = getattr(tournament_obj, f'game_{count}')
            games.append(game)
            count += 1
            games_sum += game
            if game >= 200:
                more_200 += 1

        player = {
            'min': min(games),
            'max': max(games),
            'games': games,
            'sum': games_sum,
            'avg': games_sum / len(games),
            'more_200': more_200,
            'player_id': tournament_obj.player.pk
        }
        return player

    @staticmethod
    def upload_results(model, results, year: models.YearModel, player: models.PlayerModel,
                       tournament: models.ResultsModel):
        model_obj = model()
        model_obj.year = year
        model_obj.player = player
        model_obj.tournament = tournament
        model_obj.place = results['place']
        model_obj.sum = results['sum']
        model_obj.avg = results['avg']

        for index, game in enumerate(results['games']):
            setattr(model_obj, f'game_{index + 1}', game)

        model_obj.save()

    @staticmethod
    def get_results(player: models.PlayerModel, tournament: models.ResultsModel, model):
        try:
            tournament_obj = model.objects.get(player=player, tournament=tournament)
        except ObjectDoesNotExist:
            return None

        games = []
        count = 1

        while getattr(tournament_obj, f'game_{count}', False):
            games.append(getattr(tournament_obj, f'game_{count}'))
            count += 1

        tournament = {
            'name': tournament_obj.tournament.tournament_name,
            'games': games,
            'sum': tournament_obj.sum,
            'avg': tournament_obj.avg,
            'place': tournament_obj.place
        }
        return tournament


class Statistic:

    @staticmethod
    def load_statistic(player_id, player, year: models.YearModel):
        statistic, created = models.StatisticModel.objects.get_or_create(
            player_id=player_id,
            year=year,
            defaults={'min': player['min'], 'max': player['max'], 'avg': player['avg'], 'games': len(player['games']),
                      'more_200': player['more_200'], 'sum': player['sum']}
        )

        if not created:
            statistic.min = min(statistic.min, player['min'])
            statistic.max = max(statistic.max, player['max'])
            statistic.games += len(player['games'])
            statistic.sum += player['sum']
            statistic.avg = statistic.sum / statistic.games
            statistic.more_200 += player['more_200']
            statistic.save()

    @staticmethod
    def calc_statistic(year):
        year_obj = models.YearModel.objects.get(year=year)
        statistic = models.StatisticModel.objects.filter(year=year_obj)
        for item in statistic:
            item.delete()
        # TODO переписать
        first_pm = models.FirstPmModel.objects.filter(year=year_obj)
        for item in first_pm:
            player = FirstPmResults.get_result_for_statistic(item)
            Statistic.load_statistic(player['player_id'], player, year_obj)


class FirstPmResults(BaseResult):

    @staticmethod
    def load_results(year: models.YearModel, player: models.PlayerModel, tournament: models.ResultsModel, results):
        models.FirstPmModel.objects.create(
            year=year,
            player=player,
            tournament=tournament,
            place=results['place'],
            game_1=results['games'][0],
            game_2=results['games'][1],
            game_3=results['games'][2],
            game_4=results['games'][3],
            game_5=results['games'][4],
            game_6=results['games'][5],
            sum=results['sum'],
            avg=results['avg']
        )


class Player:

    @staticmethod
    def get_player(player, sex) -> [models.PlayerModel, bool]:
        player_obj, created = models.PlayerModel.objects.get_or_create(
            name=player['name'],
            defaults={'rang': player['rang'], 'sex': sex}
        )

        if not created:
            player_obj.rang = player['rang']
            player_obj.save()

        return player_obj, created


class Rating:

    @staticmethod
    def upload_rating(tournament_type, year: models.YearModel, tournament: models.ResultsModel):
        if tournament_type == 'FirstPm':
            Rating.upload_rating_pm('man', models.FirstPmModel, year, tournament)
            Rating.upload_rating_pm('woman', models.FirstPmModel, year, tournament)
        elif tournament_type == 'SecondPm':
            Rating.upload_rating_pm('man', models.SecondPmModel, year, tournament)
            Rating.upload_rating_pm('woman', models.SecondPmModel, year, tournament)
        elif tournament_type == 'Teams':
            Rating.upload_rating_teams('man', year, tournament)
            Rating.upload_rating_teams('woman', year, tournament)

    @staticmethod
    def upload_rating_pm(sex, model, year: models.YearModel, tournament: models.ResultsModel):
        max_rating = 25 if sex == 'man' else 10

        players = model.objects.filter(tournament=tournament, player__sex=sex).order_by('-sum')

        for player in players:
            rating = max(max_rating - player.place + 1, 1)
            models.RatingModel.objects.create(
                player_id=player.player_id,
                year=year,
                tournament=tournament,
                rating=rating
            )

    @staticmethod
    def upload_rating_teams(sex, year: models.YearModel, tournament: models.ResultsModel):
        max_rating = 35 if sex == 'man' else 15

        players = models.TeamsModel.objects.raw(
            f'''
                SELECT t.id,
                       t.player_id,
                       tournament_id,
                       game_1 + game_2 + game_3 + game_4 + game_5 + game_6 AS sum,
                       row_number() OVER (ORDER BY game_1 + game_2 + game_3 + game_4 + game_5 + game_6 DESC,
                        game_6 DESC, game_5 DESC, game_4 DESC) AS place
                FROM main_teamsmodel t
                LEFT JOIN main_playermodel t1 ON t.player_id = t1.id
                WHERE tournament_id = {tournament.pk} AND t1.sex = '{sex}'
                ORDER BY sum DESC, game_6 DESC, game_5 DESC, game_4 DESC;
                '''
        )
        for player in players:
            rating = max(max_rating - player.place + 1, 1)
            models.RatingModel.objects.create(
                player_id=player.player_id,
                year=year,
                tournament=tournament,
                rating=rating
            )
