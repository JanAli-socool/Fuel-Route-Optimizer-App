from django.urls import path
from .views import OptimizeRouteAPIView

urlpatterns = [
    path(
        "optimize-route/",
        OptimizeRouteAPIView.as_view(),
        name="optimize-route",
    ),
]