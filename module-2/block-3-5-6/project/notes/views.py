"""
Domain 2 — Personal Notes API (Django sessions instead of Flask sessions).

    POST   /login/                   log in (session)
    POST   /logout/                  log out (clear session)
    GET    /me/                      current user + settings
    PUT    /settings/                update per-user settings (session)
    DELETE /settings/                reset settings to defaults
    POST   /api/notes/               create a note
    GET    /api/notes/               list current user's notes
    DELETE /api/notes/<id>/          delete a note (owner only)
    POST   /api/favorites/add/       add a note to favorites (session)
    DELETE /api/favorites/<note_id>/ remove a note from favorites
    GET    /api/favorites/           list favorite notes

Notes persist in the DB (keyed to the session username as ``author``).
Favorites are a list of note IDs stored ONLY in the session, so they vanish on
logout, exactly like the Flask original.
"""
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .auth import (
    USERS,
    SessionUserAuthentication,
    SessionLoginRequired,
    get_settings,
    DEFAULT_SETTINGS,
    InvalidCredentials,
    display_name_for,
)
from .models import Note
from .serializers import NoteSerializer


class LoginView(APIView):
    """POST /login/ — validate against the seeded USERS map and open a
    session. 200 on success, 400 when fields are missing, 401 on bad
    credentials."""

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if username is None or password is None:
            return Response(
                {'error': 'username and password are required'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if USERS.get(username) != password:
            raise InvalidCredentials()

        request.session.flush()
        request.session['username'] = username
        return Response(
            {'message': f"Welcome, {display_name_for(username)}!"},
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    """POST /logout/ — flush the session. Always 200."""

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        request.session.flush()
        return Response({'message': 'Logged out'}, status=status.HTTP_200_OK)


class MeView(APIView):
    """GET /me/ — return the logged-in username plus session settings."""

    authentication_classes = [SessionUserAuthentication]
    permission_classes = [SessionLoginRequired]

    def get(self, request):
        username = request.session['username']
        return Response({
            'username': username,
            'settings': get_settings(request.session),
        }, status=status.HTTP_200_OK)


class SettingsView(APIView):
    """PUT /settings/ & DELETE /settings/ — per-user session settings."""

    authentication_classes = [SessionUserAuthentication]
    permission_classes = [SessionLoginRequired]

    def put(self, request):
        language = request.data.get('language')
        notes_per_page = request.data.get('notes_per_page')

        if language is not None:
            request.session['language'] = language
        if notes_per_page is not None:
            request.session['notes_per_page'] = notes_per_page

        return Response({
            'message': 'Settings updated',
            'settings': get_settings(request.session),
        }, status=status.HTTP_200_OK)

    def delete(self, request):
        request.session.pop('language', None)
        request.session.pop('notes_per_page', None)
        return Response({
            'message': 'Settings reset to defaults',
            'settings': dict(DEFAULT_SETTINGS),
        }, status=status.HTTP_200_OK)


class NotesView(APIView):
    """POST /api/notes/ (create) & GET /api/notes/ (list user's notes)."""

    authentication_classes = [SessionUserAuthentication]
    permission_classes = [SessionLoginRequired]

    def post(self, request):
        username = request.session['username']
        title = request.data.get('title')
        text = request.data.get('text')

        if not title or not text or not str(title).strip() or not str(text).strip():
            missing = []
            if not title or not str(title).strip():
                missing.append('title')
            if not text or not str(text).strip():
                missing.append('text')
            return Response(
                {'error': f"field '{missing[0]}' is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        note = Note.objects.create(title=title, text=text, author=username)
        return Response(NoteSerializer(note).data, status=status.HTTP_201_CREATED)

    def get(self, request):
        username = request.session['username']
        notes = Note.objects.filter(author=username)
        return Response(
            {'notes': NoteSerializer(notes, many=True).data},
            status=status.HTTP_200_OK,
        )


class NoteDetailView(APIView):
    """DELETE /api/notes/<id>/ — owner only. 204/401/403/404."""

    authentication_classes = [SessionUserAuthentication]
    permission_classes = [SessionLoginRequired]

    def delete(self, request, note_id):
        username = request.session['username']
        try:
            note = Note.objects.get(pk=note_id)
        except Note.DoesNotExist:
            return Response(
                {'error': 'Note not found'}, status=status.HTTP_404_NOT_FOUND)

        if note.author != username:
            return Response(
                {'error': 'You can only delete your own notes'},
                status=status.HTTP_403_FORBIDDEN,
            )

        note.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteAddView(APIView):
    """POST /api/favorites/add/ — add a note id to session favorites."""

    authentication_classes = [SessionUserAuthentication]
    permission_classes = [SessionLoginRequired]

    def post(self, request):
        username = request.session['username']
        raw = request.data.get('note_id')
        if raw is None:
            return Response(
                {'error': "field 'note_id' is required"},
                status=status.HTTP_400_BAD_REQUEST)

        try:
            note_id = int(raw)
        except (TypeError, ValueError):
            return Response(
                {'error': "field 'note_id' must be an integer"},
                status=status.HTTP_400_BAD_REQUEST)

        try:
            note = Note.objects.get(pk=note_id)
        except Note.DoesNotExist:
            return Response(
                {'error': 'Note not found'}, status=status.HTTP_404_NOT_FOUND)

        if note.author != username:
            return Response(
                {'error': 'You can only favorite your own notes'},
                status=status.HTTP_400_BAD_REQUEST)

        favorites = list(request.session.get('favorites', []))
        if note_id in favorites:
            return Response({
                'message': 'Note already in favorites',
                'favorites': favorites,
            }, status=status.HTTP_200_OK)

        favorites.append(note_id)
        request.session['favorites'] = favorites
        return Response({
            'message': 'Note added to favorites',
            'favorites': favorites,
        }, status=status.HTTP_200_OK)


class FavoriteRemoveView(APIView):
    """DELETE /api/favorites/<note_id>/ — drop an id from session favorites."""

    authentication_classes = [SessionUserAuthentication]
    permission_classes = [SessionLoginRequired]

    def delete(self, request, note_id):
        favorites = list(request.session.get('favorites', []))
        try:
            favorites.remove(int(note_id))
        except (ValueError, TypeError):
            pass
        request.session['favorites'] = favorites
        return Response({
            'message': 'Note removed from favorites',
            'favorites': favorites,
        }, status=status.HTTP_200_OK)


class FavoritesView(APIView):
    """GET /api/favorites/ — return full note objects for favorited ids."""

    authentication_classes = [SessionUserAuthentication]
    permission_classes = [SessionLoginRequired]

    def get(self, request):
        favorites = list(request.session.get('favorites', []))
        notes = Note.objects.filter(pk__in=favorites)
        # Preserve the order in which the ids were favorited.
        ordered = sorted(notes, key=lambda n: favorites.index(n.pk))
        return Response(
            {'favorites': NoteSerializer(ordered, many=True).data},
            status=status.HTTP_200_OK,
        )
