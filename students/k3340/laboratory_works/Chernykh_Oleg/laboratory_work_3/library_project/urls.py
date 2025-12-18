"""
URL configuration for library_project project.
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from library.views import (
    BookViewSet, ReaderViewSet, ReadingHallViewSet, 
    BookCopyViewSet, BookAssignmentViewSet, AuthorViewSet,
    AnalyticsViewSet, LibrarianOperationsViewSet, ReportViewSet
)

schema_view = get_schema_view(
   openapi.Info(
      title="Library API",
      default_version='v1',
      description="API для системы управления библиотекой. Для авторизации используйте заголовок: Authorization: Token <your_token>",
      contact=openapi.Contact(email="support@library.local"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

router = DefaultRouter()
router.register(r'books', BookViewSet, basename='book')
router.register(r'readers', ReaderViewSet, basename='reader')
router.register(r'reading-halls', ReadingHallViewSet, basename='readinghall')
router.register(r'book-copies', BookCopyViewSet, basename='bookcopy')
router.register(r'book-assignments', BookAssignmentViewSet, basename='bookassignment')
router.register(r'authors', AuthorViewSet, basename='author')
router.register(r'analytics', AnalyticsViewSet, basename='analytics')
router.register(r'librarian-operations', LibrarianOperationsViewSet, basename='librarian')
router.register(r'reports', ReportViewSet, basename='report')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.authtoken')),
    path('api/', include(router.urls)),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

