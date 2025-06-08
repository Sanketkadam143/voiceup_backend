from django.urls import path
from .views import ConversationListView, AnalyticsDataView

urlpatterns = [
    path('conversations/', ConversationListView.as_view()),
    path('analytics/', AnalyticsDataView.as_view()),
]
