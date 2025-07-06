from django.urls import path
from .views import (
    InventoryItemListCreateAPIView,
    InventoryItemRetrieveUpdateDestroyAPIView,
)

urlpatterns = [
    path('inventory/', InventoryItemListCreateAPIView.as_view(), name='inventory-list-create'),
    path('inventory/<int:pk>/', InventoryItemRetrieveUpdateDestroyAPIView.as_view(), name='inventory-detail'),
]
