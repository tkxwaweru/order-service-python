from django.shortcuts import render
from rest_framework import generics, permissions
from .models import InventoryItem
from .serializers import InventoryItemSerializer
from rest_framework.permissions import IsAdminUser

class InventoryItemListCreateAPIView(generics.ListCreateAPIView):
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemSerializer
    permission_classes = [IsAdminUser]

class InventoryItemRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemSerializer
    permission_classes = [IsAdminUser]