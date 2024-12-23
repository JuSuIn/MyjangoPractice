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

from hottrack.models import Song
from hottrack.utils.cover import make_cover_image


def index(request: HttpRequest, release_date: datetime.date = None) -> HttpResponse:
    query = request.GET.get("query", "").strip()

    song_qs: QuerySet[song] = Song.objects.all()

    # hottrack/archives/2022/03/14/ 와 같은 필터 처리
    if release_date:
        song_qs = song_qs.filter(release_date=release_date)

    # melon_chart_url = "https://raw.githubusercontent.com/pyhub-kr/dump-data/main/melon/melon-20230910.json"
    # json_string = urlopen(melon_chart_url).read().decode("utf-8")
    # # 외부 필드명을 그대로 쓰기보다, 내부적으로 사용하는 필드명으로 변경하고, 필요한 메서드를 추가합니다.
    # song_list = [Song.from_dict(song_dict) for song_dict in json.loads(json_string)]

    if query:
        song_qs = song_qs.filter(
            Q(name__icontains=query)
            | Q(artist__name__icontains=query)
            | Q(album__name__icontains=query)
        )
        # song_list = [
        #     song
        #     for song in song_list
        #     if query in song.name
        #     or query in song.artist_name
        #     or query in song.album_name
        # ]

    return render(
        request=request,
        template_name="hottrack/index.html",
        context={
            "song_list": song_qs,
            "query": query,
        },
    )


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
