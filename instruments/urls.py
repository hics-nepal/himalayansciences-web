from django.urls import path
from . import api

urlpatterns = [
    path('ingest/environmental/', api.IngestEnvironmentalView.as_view()),
    path('data/latest/', api.LatestReadingView.as_view()),
    path('data/historical/', api.HistoricalDataView.as_view()),
    path('data/download/', api.DownloadCSVView.as_view()),
]
