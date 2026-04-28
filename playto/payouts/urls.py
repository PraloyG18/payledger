from django.urls import path
from .views import get_dashboard, create_payout_view

urlpatterns = [
    path("dashboard/<int:merchant_id>/", get_dashboard),
    path("payout/<int:merchant_id>/", create_payout_view),
]