from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookViewSet, AuthorViewSet, RegisterView, LoginView, FavoriteViewSet, RecommendationView

router = DefaultRouter()
router.register(r'books', BookViewSet, basename='book')
router.register(r'authors', AuthorViewSet, basename='author')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('', include(router.urls)),
]

favorite_list = FavoriteViewSet.as_view({
    'get': 'list',
    'post': 'create',
})

favorite_detail = FavoriteViewSet.as_view({
    'delete': 'destroy',
})

urlpatterns += [
    path('favorites/', favorite_list, name='favorite-list'),
    path('favorites/<int:book_id>/', favorite_detail, name='favorite-detail'),
    path('recommendations/', RecommendationView.as_view(), name='recommendations'),
]
