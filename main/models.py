from django.db import models
from os.path import splitext
import datetime


def get_result_path(instance, filename):
    return f'results/{instance.year.year}/{instance.tournament_name}_{datetime.datetime.now()}{splitext(filename)[1]}'


def get_document_path(instance, filename):
    return f'documents/{instance.name}_{datetime.datetime.now()}{splitext(filename)[1]}'


def get_image_path(instance, filename):
    return f'images/{instance.name}_{datetime.datetime.now()}{splitext(filename)[1]}'


class YearModel(models.Model):
    year = models.IntegerField('Год')

    def __str__(self):
        return f'{self.year}'

    class Meta:
        ordering = ['-year']


class PlayerModel(models.Model):
    SEX_OPTIONS = (
        ('Мужчина', 'man'),
        ('Женищина', 'woman')
    )

    name = models.CharField(max_length=100, verbose_name='Имя игрока')
    rang = models.CharField(max_length=10, verbose_name='Звание', default='')
    sex = models.CharField(max_length=10, choices=SEX_OPTIONS)


class ResultsModel(models.Model):
    CHOICE = (
        ('FirstPm', '1 регламент ПМ (6 игр)'),
        ('SecondPm', '2 регламент ПМ (12 игр)'),
        ('finals_a', 'Финалы А'),
        ('finals_b', 'Финалы Б'),
        ('Teams', 'Пары'),
        ('Teams', 'Пары микс'),
        ('Teams', 'Тройки'),
        ('Teams', 'Тройки микс'),
        ('Teams', 'Пятерки'),
        ('spb_championship', 'Чемпионат СПБ'),
        ('spb_cup', 'Кубок СПБ'),
        ('no_rating', 'Без рейтинга')
    )
    CHOICE_FORMAT = (
        ('rating', 'Рейтинговый'),
        ('sport', 'Спортивный')
    )
    tournament_name = models.CharField(max_length=100, verbose_name='Название турнира')
    date = models.DateField(verbose_name='Дата проведения')
    year = models.ForeignKey(YearModel, on_delete=models.PROTECT)
    results = models.FileField(verbose_name='PDF', upload_to=get_result_path)
    short_form = models.CharField(max_length=100, verbose_name='Короткая форма названия')
    type = models.CharField(max_length=100, verbose_name='Тип турнира', choices=CHOICE)
    format = models.CharField(max_length=50, verbose_name='Формат', choices=CHOICE_FORMAT)

    def __str__(self):
        return self.tournament_name

    class Meta:
        ordering = ['-date']


class StatisticModel(models.Model):
    year = models.ForeignKey(YearModel, on_delete=models.PROTECT, verbose_name='Год')
    player = models.ForeignKey(PlayerModel, on_delete=models.PROTECT, verbose_name='Игрок')
    min = models.SmallIntegerField(verbose_name='Минимальная игра')
    max = models.SmallIntegerField(verbose_name='Максимальная игра')
    avg = models.DecimalField(verbose_name='Средний', max_digits=5, decimal_places=2)
    more_200 = models.SmallIntegerField(verbose_name='Игр за 200')
    games = models.SmallIntegerField(verbose_name='Количество игр')
    sum = models.IntegerField(verbose_name='Общая сумма')

    class Meta:
        ordering = ['-avg']


class RatingModel(models.Model):
    player = models.ForeignKey(PlayerModel, on_delete=models.PROTECT, verbose_name='Игрок')
    tournament = models.ForeignKey(ResultsModel, on_delete=models.PROTECT, verbose_name='Турнир')
    year = models.ForeignKey(YearModel, on_delete=models.PROTECT, verbose_name='Год')
    rating = models.SmallIntegerField(verbose_name='Очки рейтинга')


class DocumentModel(models.Model):
    TYPE_CHOICE = (
        ('regulation', 'Регламент'),
        ('rang_report', 'Приказ о присвоении'),
        ('rating', 'Рейтинг'),
        ('calendar', 'Календарь'),
        ('anti_doping', 'Антидопинг'),
        ('protocols', 'Протоколы')
    )
    type = models.CharField(max_length=100, choices=TYPE_CHOICE, verbose_name='Тип документа')
    year = models.ForeignKey(YearModel, on_delete=models.PROTECT, verbose_name='Год', related_name='regulations')
    name = models.CharField(max_length=100, verbose_name='Название документа')
    document = models.FileField(upload_to=get_document_path, verbose_name='Документ')
    archive = models.BooleanField(default=False, verbose_name='Архив')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-id']


class CalendarModel(models.Model):
    TYPE = (
        ('Sport', 'Спортивный'),
        ('Student', 'Студенческий'),
    )
    competition = models.CharField(max_length=50, verbose_name='Название турнира')
    city = models.CharField(max_length=20, verbose_name='Город проведения')
    status = models.CharField(max_length=50, verbose_name='Статус соревнований', blank=True)
    date_start = models.DateField(verbose_name='Дата начала')
    date_finish = models.DateField(verbose_name='Дата окончания')
    type = models.CharField(max_length=20, verbose_name='Тип турнира', choices=TYPE, default='Sport')
    regulation = models.ForeignKey(DocumentModel, on_delete=models.CASCADE, verbose_name='Регламент', null=True,
                                   blank=True)

    def __str__(self):
        return self.competition

    class Meta:
        verbose_name = 'турнир'
        verbose_name_plural = 'Календарь турниров'
        ordering = ['date_start']


class NewsModel(models.Model):
    name = models.CharField(max_length=100, verbose_name='Навзание новости')
    short_description = models.CharField(max_length=100, verbose_name='Короткое описание')
    description = models.TextField(verbose_name='Описание')
    result = models.ForeignKey(ResultsModel, on_delete=models.PROTECT, verbose_name='Результаты', blank=True, null=True)
    regulation = models.ForeignKey(DocumentModel, on_delete=models.PROTECT, verbose_name='Регламент', blank=True,
                                   null=True)
    news_image = models.ImageField(upload_to=get_image_path, verbose_name='Изображение новости', blank=True, null=True)
    date = models.DateField(verbose_name='Дата')
    count = models.IntegerField(verbose_name='Просмотров', default=0)

    class Meta:
        ordering = ['-date']


class ReportsModel(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название Турнира')
    short_description = models.TextField(max_length=255, verbose_name='Короткое описание')
    description = models.TextField(verbose_name='Описание')
    date = models.DateField(verbose_name='Дата')
    regulation = models.ForeignKey(DocumentModel, on_delete=models.CASCADE, verbose_name='Регламент', null=True,
                                   blank=True)
    tournament_results = models.ForeignKey(ResultsModel, verbose_name='Результаты', on_delete=models.CASCADE, null=True,
                                           blank=True)
    report_image = models.ImageField(verbose_name='Изображение новости', upload_to=get_image_path, null=True,
                                     blank=True)
    count = models.IntegerField(default=0, verbose_name='Просмотры')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Отчет'
        verbose_name_plural = 'Отчеты по прощедщим турнирам'
        ordering = ['-date']


class NewsDocumentsModel(models.Model):
    news = models.ForeignKey(NewsModel, on_delete=models.CASCADE, verbose_name='Новость', related_name='news_documents',
                             blank=True, null=True)
    report = models.ForeignKey(ReportsModel, on_delete=models.CASCADE, verbose_name='Отчет',
                               related_name='report_documents', blank=True, null=True)
    name = models.CharField(max_length=100, verbose_name='Название документа')
    document = models.FileField(upload_to=get_document_path, verbose_name='Документ')


class ImagesModel(models.Model):
    news = models.ForeignKey(NewsModel, on_delete=models.CASCADE, verbose_name='Новость', related_name='news_images',
                             blank=True, null=True)
    report = models.ForeignKey(ReportsModel, on_delete=models.CASCADE, verbose_name='Отчет',
                               related_name='report_images', blank=True, null=True)
    name = models.CharField(max_length=100, verbose_name='Название изображения')
    image = models.ImageField(upload_to=get_image_path, verbose_name='Изображение')
    width = models.IntegerField(null=True, blank=True, verbose_name='Ширина')
    height = models.IntegerField(null=True, blank=True, verbose_name='Высота')


class TournamentsAbstractModel(models.Model):
    year = models.ForeignKey(YearModel, on_delete=models.PROTECT, verbose_name='Год')
    player = models.ForeignKey(PlayerModel, on_delete=models.PROTECT, verbose_name='Игрок')
    tournament = models.ForeignKey(ResultsModel, on_delete=models.PROTECT, verbose_name='Турнир')
    sum = models.IntegerField(verbose_name='Сумма')
    avg = models.DecimalField(verbose_name='Средний', max_digits=5, decimal_places=2)
    place = models.SmallIntegerField(verbose_name='Место')

    class Meta:
        abstract = True


class FirstPmModel(TournamentsAbstractModel):
    game_1 = models.SmallIntegerField(verbose_name='Игра 1')
    game_2 = models.SmallIntegerField(verbose_name='Игра 2')
    game_3 = models.SmallIntegerField(verbose_name='Игра 3')
    game_4 = models.SmallIntegerField(verbose_name='Игра 4')
    game_5 = models.SmallIntegerField(verbose_name='Игра 5')
    game_6 = models.SmallIntegerField(verbose_name='Игра 6')


class SecondPmModel(TournamentsAbstractModel):
    game_1 = models.SmallIntegerField(verbose_name='Игра 1')
    game_2 = models.SmallIntegerField(verbose_name='Игра 2')
    game_3 = models.SmallIntegerField(verbose_name='Игра 3')
    game_4 = models.SmallIntegerField(verbose_name='Игра 4')
    game_5 = models.SmallIntegerField(verbose_name='Игра 5')
    game_6 = models.SmallIntegerField(verbose_name='Игра 6')
    game_7 = models.SmallIntegerField(verbose_name='Игра 7', null=True)
    game_8 = models.SmallIntegerField(verbose_name='Игра 8', null=True)
    game_9 = models.SmallIntegerField(verbose_name='Игра 9', null=True)
    game_10 = models.SmallIntegerField(verbose_name='Игра 10', null=True)
    game_11 = models.SmallIntegerField(verbose_name='Игра 11', null=True)
    game_12 = models.SmallIntegerField(verbose_name='Игра 12', null=True)
    game_13 = models.SmallIntegerField(verbose_name='Игра 13', null=True)
    game_14 = models.SmallIntegerField(verbose_name='Игра 14', null=True)
    game_15 = models.SmallIntegerField(verbose_name='Игра 15', null=True)
    game_16 = models.SmallIntegerField(verbose_name='Игра 16', null=True)
    game_17 = models.SmallIntegerField(verbose_name='Игра 17', null=True)


class TeamsModel(TournamentsAbstractModel):
    game_1 = models.SmallIntegerField(verbose_name='Игра 1')
    game_2 = models.SmallIntegerField(verbose_name='Игра 2')
    game_3 = models.SmallIntegerField(verbose_name='Игра 3')
    game_4 = models.SmallIntegerField(verbose_name='Игра 4')
    game_5 = models.SmallIntegerField(verbose_name='Игра 5')
    game_6 = models.SmallIntegerField(verbose_name='Игра 6')
    game_7 = models.SmallIntegerField(verbose_name='Игра 7', null=True)
    game_8 = models.SmallIntegerField(verbose_name='Игра 8', null=True)
    game_9 = models.SmallIntegerField(verbose_name='Игра 9', null=True)


class FinalsA(TournamentsAbstractModel):
    game_1 = models.SmallIntegerField(verbose_name='Игра 1', null=True)
    game_2 = models.SmallIntegerField(verbose_name='Игра 2', null=True)
    game_3 = models.SmallIntegerField(verbose_name='Игра 3', null=True)
    game_4 = models.SmallIntegerField(verbose_name='Игра 4', null=True)
    game_5 = models.SmallIntegerField(verbose_name='Игра 5', null=True)
    game_6 = models.SmallIntegerField(verbose_name='Игра 6', null=True)
    game_7 = models.SmallIntegerField(verbose_name='Игра 7', null=True)
    game_8 = models.SmallIntegerField(verbose_name='Игра 8', null=True)


class FinalsB(TournamentsAbstractModel):
    game_1 = models.SmallIntegerField(verbose_name='Игра 1', null=True)
    game_2 = models.SmallIntegerField(verbose_name='Игра 2', null=True)
    game_3 = models.SmallIntegerField(verbose_name='Игра 3', null=True)
    game_4 = models.SmallIntegerField(verbose_name='Игра 4', null=True)
    game_5 = models.SmallIntegerField(verbose_name='Игра 5', null=True)
    game_6 = models.SmallIntegerField(verbose_name='Игра 6', null=True)
    game_7 = models.SmallIntegerField(verbose_name='Игра 7', null=True)
    game_8 = models.SmallIntegerField(verbose_name='Игра 8', null=True)
    game_9 = models.SmallIntegerField(verbose_name='Игра 9', null=True)


class SpbCup(TournamentsAbstractModel):
    game_1 = models.SmallIntegerField(verbose_name='Игра 1')
    game_2 = models.SmallIntegerField(verbose_name='Игра 2')
    game_3 = models.SmallIntegerField(verbose_name='Игра 3')
    game_4 = models.SmallIntegerField(verbose_name='Игра 4')
    game_5 = models.SmallIntegerField(verbose_name='Игра 5')
    game_6 = models.SmallIntegerField(verbose_name='Игра 6')
    game_7 = models.SmallIntegerField(verbose_name='Игра 7', null=True)
    game_8 = models.SmallIntegerField(verbose_name='Игра 8', null=True)
    game_9 = models.SmallIntegerField(verbose_name='Игра 9', null=True)
    game_10 = models.SmallIntegerField(verbose_name='Игра 10', null=True)
    game_11 = models.SmallIntegerField(verbose_name='Игра 11', null=True)
    game_12 = models.SmallIntegerField(verbose_name='Игра 12', null=True)
    game_13 = models.SmallIntegerField(verbose_name='Игра 13', null=True)
    game_14 = models.SmallIntegerField(verbose_name='Игра 14', null=True)
    game_15 = models.SmallIntegerField(verbose_name='Игра 15', null=True)
    game_16 = models.SmallIntegerField(verbose_name='Игра 16', null=True)


class SpbChampionship(TournamentsAbstractModel):
    game_1 = models.SmallIntegerField(verbose_name='Игра 1')
    game_2 = models.SmallIntegerField(verbose_name='Игра 2')
    game_3 = models.SmallIntegerField(verbose_name='Игра 3')
    game_4 = models.SmallIntegerField(verbose_name='Игра 4')
    game_5 = models.SmallIntegerField(verbose_name='Игра 5')
    game_6 = models.SmallIntegerField(verbose_name='Игра 6')
    game_7 = models.SmallIntegerField(verbose_name='Игра 7', null=True)
    game_8 = models.SmallIntegerField(verbose_name='Игра 8', null=True)
    game_9 = models.SmallIntegerField(verbose_name='Игра 9', null=True)
    game_10 = models.SmallIntegerField(verbose_name='Игра 10', null=True)
    game_11 = models.SmallIntegerField(verbose_name='Игра 11', null=True)
    game_12 = models.SmallIntegerField(verbose_name='Игра 12', null=True)
    game_13 = models.SmallIntegerField(verbose_name='Игра 13', null=True)
    game_14 = models.SmallIntegerField(verbose_name='Игра 14', null=True)
    game_15 = models.SmallIntegerField(verbose_name='Игра 15', null=True)
    game_16 = models.SmallIntegerField(verbose_name='Игра 16', null=True)
    game_17 = models.SmallIntegerField(verbose_name='Игра 15', null=True)
    game_18 = models.SmallIntegerField(verbose_name='Игра 16', null=True)
    game_19 = models.SmallIntegerField(verbose_name='Игра 16', null=True)
    game_20 = models.SmallIntegerField(verbose_name='Игра 15', null=True)
    game_21 = models.SmallIntegerField(verbose_name='Игра 16', null=True)
