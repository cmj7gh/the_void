from django.urls import path
from .views import *

urlpatterns = [
    path("upload/", upload_view, name="upload"),
    path("upload_text/", new_memo_text_view, name="upload_text"),
    path("", MemoListView.as_view(), name="memo_list"),
    path("memos/<int:pk>/", MemoDetailView.as_view(), name="memo_detail"),
]
