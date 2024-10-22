from rest_framework import generics, viewsets, filters, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework.response import Response

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from .pagination import StandardResultsSetPagination
from .models import Publication, Writer, UserFavorite, PublicationSimilarity, LibraryShelf
from .serializers import (
    RegisterSerializer,
    CustomTokenObtainPairSerializer,
    PublicationSerializer,
    WriterSerializer,
    UserFavoriteSerializer,
)

CustomUser = get_user_model()

def get_recommendations(user):
    favorite_publications = UserFavorite.objects.filter(user=user).values_list('publication', flat=True)
    favorite_publications = list(favorite_publications)

    if not favorite_publications:
        return []

    # Get similar publications
    similar_publications = PublicationSimilarity.objects.filter(
        publication1_id__in=favorite_publications
    ).exclude(
        publication2_id__in=favorite_publications
    ).values(
        'publication2_id'
    ).annotate(
        total_similarity=Sum('similarity')
    ).order_by('-total_similarity')[:5]

    # Retrieve publication instances
    recommended_publications_ids = [item['publication2_id'] for item in similar_publications]
    recommended_publications = Publication.objects.filter(id__in=recommended_publications_ids)

    serializer = PublicationSerializer(recommended_publications, many=True)
    return serializer.data

class RecommendationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        recommendations = get_recommendations(user)
        return Response(recommendations, status=status.HTTP_200_OK)

class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer

class PublicationViewSet(viewsets.ModelViewSet):
    queryset = Publication.objects.all()
    serializer_class = PublicationSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['book_title', 'writers__given_name', 'writers__surname']
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = []  # Allow any
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

class WriterViewSet(viewsets.ModelViewSet):
    queryset = Writer.objects.all()
    serializer_class = WriterSerializer
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = []  # Allow any
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

class UserFavoriteViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    lookup_field = 'publication_id'

    def get_queryset(self):
        return UserFavorite.objects.filter(user=self.request.user)

    def list(self, request):
        favorites = self.get_queryset()
        publications = [favorite.publication for favorite in favorites]
        serializer = PublicationSerializer(publications, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = UserFavoriteSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        favorite = serializer.save()
        recommendations = get_recommendations(request.user)
        return Response({
            'detail': 'Publication added to favorites.',
            'recommendations': recommendations
        }, status=status.HTTP_201_CREATED)

    def destroy(self, request, publication_id=None):
        favorite = get_object_or_404(UserFavorite, user=request.user, publication_id=publication_id)
        favorite.delete()
        return Response({'detail': 'Publication removed from favorites.'}, status=status.HTTP_204_NO_CONTENT)
