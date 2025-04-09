from django.urls import path
from rest_framework.routers import DefaultRouter
from api.views import PayerViewSet, FavouritesViewSet, GenerateInvoiceAPIView

app_name = 'api'

router = DefaultRouter()

router.register(r'payers', PayerViewSet, basename='payer')
router.register(r'favourites', FavouritesViewSet, basename='favourite')

urlpatterns = router.urls

urlpatterns += [
    path('generate_invoice/', GenerateInvoiceAPIView.as_view(), name='generate_invoice'),
]