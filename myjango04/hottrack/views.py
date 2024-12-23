# from django.http import HttpRequest, HttpResponse
# from django.shortcuts import render
#
# # Create your views here.
#
#
# def index(request: HttpRequest) -> HttpResponse:
#     return render(request, template_name="hottrack/index.html", context={})
import datetime

# hottrack/views.py

import json
from fileinput import filename
from io import BytesIO
from typing import Literal
from urllib.request import urlopen

import pandas as pd
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.views.generic import (
    DetailView,
    ListView,
    YearArchiveView,
    MonthArchiveView,
    DayArchiveView,
    WeekArchiveView,
    ArchiveIndexView,
    DateDetailView,
)
from django.db.models import Q

from hottrack.models import Song
from mysite import settings
from .mixins import SearchQueryMixin
from hottrack.utils.cover import make_cover_image


class IndexView(SearchQueryMixin, ListView):
    model = Song
    template_name = "hottrack/index.html"
    paginate_by = 10

    # query = None

    # def get(self, request, *args, **kwargs):
    #     self.query = reqeust.GET.get.('query',"").strip()
    #     return super().get(request, *args, **kwargs)

    def get_queryset(self):
        qs = super().get_queryset()

        release_date = self.kwargs.get("release_date")
        if release_date:
            qs = qs.filter(release_date=release_date)

        query = self.request.GET.get("query", "").strip()
        if query:
            qs = qs.filter(
                Q(name__icontains=query)
                | Q(artist_name__icontains=query)
                | Q(album_name__icontains=query)
            )

        return qs

    # def get_context_data(self, **kwargs):
    #     context_data= super().get_context_data(**kwargs)
    #     context_data['query'] = self.query
    #     return context_data


index = IndexView.as_view()

# def index(request: HttpRequest, release_date: datetime.date = None) -> HttpResponse:
#     query = request.GET.get("query", "").strip()
#
#     song_qs: QuerySet[song] = Song.objects.all()
#
#     # hottrack/archives/2022/03/14/ 와 같은 필터 처리
#     if release_date:
#         song_qs = song_qs.filter(release_date=release_date)
#
#     # melon_chart_url = "https://raw.githubusercontent.com/pyhub-kr/dump-data/main/melon/melon-20230910.json"
#     # json_string = urlopen(melon_chart_url).read().decode("utf-8")
#     # # 외부 필드명을 그대로 쓰기보다, 내부적으로 사용하는 필드명으로 변경하고, 필요한 메서드를 추가합니다.
#     # song_list = [Song.from_dict(song_dict) for song_dict in json.loads(json_string)]
#
#     if query:
#         song_qs = song_qs.filter(
#             Q(name__icontains=query)
#             | Q(artist_name__icontains=query)
#             | Q(album_name__icontains=query)
#         )
#         # song_list = [
#         #     song
#         #     for song in song_list
#         #     if query in song.name
#         #     or query in song.artist_name
#         #     or query in song.album_name
#         # ]
#
#     return render(
#             request=request,
#             template_name="hottrack/index.html",
#             context={
#                 "song_list": song_qs,
#                 "query": query,
#             },
#         )

# def song_detail(request,pk):
#     song=get_object_or_404(Song, pk=pk)
#     return render(
#         request=request,
#         template_name="hottrack/song_detail.html",
#         context={
#             "song" : song
#         },
#     )


class SongDetailView(DetailView):
    model = Song

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

            melon_uid = self.kwargs.get("melon_uid")
            if melon_uid:
                return get_object_or_404(queryset, melon_uid=melon_uid)

            return super().get_object(queryset)


song_detail = SongDetailView.as_view()

# #pk 필드로 조회를 할 경우
# song_detail = DetailView.as_view(model=Song,
#                                  # template_name="hottrack/song_detail.html",
#                                  # context_object_name="song",
#                                  # pk_url_kwarg="song_id",
#                                  slug_field="melon_uid",
#                                  slug_url_kwarg="melon_uid"
#                                  )


class SongListView(ListView):
    model = Song


song_list = SongListView.as_view()

song_list = SongListView.as_view(model=Song)


# dynamic csv,excel create
def export(request, format: Literal["csv", "xlsx"]):
    song_qs = Song.objects.all()
    df = pd.DataFrame(data=song_qs.values())

    export_file = BytesIO()

    if format == "csv":
        content_type = "text/csv"
        filename = "export.csv"
        # 반드시 encoding 잘 지정해줄 것
        df.to_csv(path_or_buf=export_file, index=False, encoding="utf-8-sig")
    elif format == "xlsx":
        content_type = "application/vnd.ms-excel"
        filename = "export.xlsx"
        # 반드시 encoding 잘 지정해줄 것
        df.to_excel(excel_writer=export_file, index=False)
    else:
        return HttpResponseBadRequest(f"Invalid export format '{format}'")

    # answar csv designate
    response = HttpResponse(content=export_file.getvalue(), content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="{}"'.format(filename)

    return response


# dynamic csv create
# def export_csv(request):
#     song_qs = Song.objects.all()
#     df = pd.DataFrame(data=song_qs.values())
#
#     export_file = BytesIO()
#     # 반드시 encoding 잘 지정해줄 것
#     df.to_csv(export_file, index=False, encoding="utf-8-sig")
#     # answar csv designate
#     response = HttpResponse(content=export_file.getvalue(), content_type="text/csv")
#     response["Content-Disposition"] = 'attachment; filename="hottrack.csv"'
#
#     return response


# dynamic image create
def cover_png(request, pk):
    # 최대값 512, 기본값 256
    canvas_size = min(512, int(request.GET.get("size", 256)))

    song = get_object_or_404(Song, pk=pk)

    cover_image = make_cover_image(
        song.cover_url, song.artist_name, canvas_size=canvas_size
    )

    # param fp : filename (str), pathlib.Path object or file object
    # image.save("image.png")
    response = HttpResponse(content_type="image/png")
    cover_image.save(response, format="png")

    return response


class SongYearArchiveView(YearArchiveView):
    model = Song
    date_field = "release_date"  # 조회할 날짜 필드
    # year = None
    make_object_list = True
    # template_name = "hottrack/song_archive_year.html"


class SongMonthArchiveView(MonthArchiveView):
    model = Song
    date_field = "release_date"
    month_format = "%m"


class SongDayArchiveView(DayArchiveView):
    model = Song
    date_field = "release_date"
    month_format = "%m"


class SongTodayArchiveView(DayArchiveView):
    model = Song
    date_field = "release_date"

    if settings.DEBUG:

        def get_dated_items(self):
            # 지정된 날짜의 데이터를 조회
            fake_today = self.request.GET.get("fake-today", "")

            try:
                year, month, day = map(int, fake_today.split("-", 3))
                return self._get_dated_items(datetime.date(year, month, day))
            except ValueError:
                # fake_today 파라미터가 없거나 날짜 형식이 잘못되었을 경우
                return super().get_dated_items()


class SongWeekArchiveView(WeekArchiveView):
    model = Song
    date_field = "release_date"

    week_format = "%W"


class SongArchiveIndexView(ArchiveIndexView):
    model = Song
    date_field = "release_date"  # 기존 날짜 필드
    paginate_by = 10  # 전체 목록을 조회하기에 페이징 처리가 필수

    # date_list_period : "year" 단위 , year(디폴트), month,day
    def get_date_list_period(self):
        # URL Captured Value 에 date_list_period 없으면 , date_list_period 속성을 활용합니다.
        return self.kwargs.get("date_list_period", self.date_list_period)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["date_list_period"] = self.get_date_list_period()
        return context_data


class SongDateDetailView(DateDetailView):
    model = Song
    date_field = "release_date"
    month_format = "%m"
