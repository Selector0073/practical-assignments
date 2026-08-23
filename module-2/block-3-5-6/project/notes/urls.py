from django.urls import path

from .views import (
    LoginView,
    LogoutView,
    MeView,
    SettingsView,
    NotesView,
    NoteDetailView,
    FavoriteAddView,
    FavoriteRemoveView,
    FavoritesView,
)

urlpatterns = [
    # Authentication
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('me/', MeView.as_view(), name='me'),
    # Settings (session)
    path('settings/', SettingsView.as_view(), name='settings'),
    # Notes
    path('api/notes/', NotesView.as_view(), name='notes'),
    path('api/notes/<int:note_id>/', NoteDetailView.as_view(), name='note_detail'),
    # Favorites (session)
    path('api/favorites/add/', FavoriteAddView.as_view(), name='favorite_add'),
    path('api/favorites/<int:note_id>/', FavoriteRemoveView.as_view(), name='favorite_remove'),
    path('api/favorites/', FavoritesView.as_view(), name='favorites'),
]
