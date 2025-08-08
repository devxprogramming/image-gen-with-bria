from django.urls import path
from . import views

urlpatterns = [
    path("", views.GenerateImage.as_view(), name="create"),
    # path("<int:pk>/", ImageDetailView.as_view(), name="image-detail"),
    # path("create/", ImageCreateView.as_view(), name="image-create"),
    # path("<int:pk>/update/", ImageUpdateView.as_view(), name="image-update"),
    # path("<int:pk>/delete/", ImageDeleteView.as_view(), name="image-delete"),
]