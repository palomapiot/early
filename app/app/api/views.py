"""
    Copyright 2020-2021 Paloma Piot Pérez-Abadín
	
	This file is part of early.
    early is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    early is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with early.  If not, see <https://www.gnu.org/licenses/>.
"""

from django.contrib.auth import authenticate
from django.contrib.auth.models import Group, User
from django_filters.rest_framework import DjangoFilterBackend
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)
from app.api.models import Profile, ProfileData, Reason, GlobalData, Corpus, Comment
from app.api.serializers import (ExportSerializer, GroupSerializer,
                                 ProfileDataSerializer, ProfileNLPSerializer,
                                 ProfileSerializer, ReasonSerializer,
                                 UserSerializer, GlobalDataSerializer,
                                 CorpusSerializer, CommentsCorpusSerializer,
                                 LabeledDataSerializer)
import django_filters
from django_filters.rest_framework import filters

@api_view(["POST"])
@permission_classes((AllowAny,))
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")
    if username is None or password is None:
        return Response({'error': 'Please provide both username and password'},
                        status=HTTP_400_BAD_REQUEST)
    user = authenticate(username=username, password=password)
    if not user:
        return Response({'error': 'Invalid Credentials'},
                        status=HTTP_404_NOT_FOUND)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'token': token.key},
                    status=HTTP_200_OK)

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

class ExportViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows profiles to export to be viewed.
    """
    pagination_class = None
    queryset = Profile.objects.filter(validated_data__isnull=False).all()
    serializer_class = ExportSerializer
    permission_classes = [permissions.IsAuthenticated]

from django_filters import rest_framework as filters

class ProfileFilterSet(filters.FilterSet):
    validated_data__age = filters.AllValuesMultipleFilter(
        field_name='validated_data__age',
        lookup_expr='contains'
    )
    validated_data__gender = filters.AllValuesMultipleFilter(
        field_name='validated_data__gender',
        lookup_expr='contains'
    )
    validated_data__location = filters.AllValuesMultipleFilter(
        field_name='validated_data__location',
        lookup_expr='contains'
    )
    validated_data__personality = filters.AllValuesMultipleFilter(
        field_name='validated_data__personality',
        lookup_expr='contains'
    )
    validated_data__depressed = filters.AllValuesMultipleFilter(
        field_name='validated_data__depressed'
    )
    is_valid = filters.AllValuesMultipleFilter(
        field_name='is_valid'
    )
    processed = filters.AllValuesMultipleFilter(
        field_name='processed'
    )

    class Meta:
        model = Profile
        fields = ['validated_data__age', 'validated_data__gender', 'validated_data__location',
        'validated_data__personality', 'validated_data__depressed', 'is_valid', 'processed', 'experiment_id']

        

class ProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows profiles to be viewed or edited.
    """
    queryset = Profile.objects.all().order_by('experiment_id')
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]

    filter_class = ProfileFilterSet

    def get_serializer_context(self):
        context = super(ProfileViewSet, self).get_serializer_context()
        context.update({"request": self.request})
        return context

    @action(detail=True)
    def reasons(self, request, pk=None):
        """
        Returns a list of all the reasons that the given profile has.
        """
        profile = self.get_object()
        profile_data_type = self.request.query_params.get('type')
        reasons = Reason.objects.filter(profile=profile, profile_data_type=profile_data_type).all()
        return Response([reason.reason for reason in reasons])
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProfileNLPSerializer
        return ProfileSerializer

class ProfileDataViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows profile data to be viewed or edited.
    """
    queryset = ProfileData.objects.all()
    serializer_class = ProfileDataSerializer
    permission_classes = [permissions.IsAuthenticated]

class ReasonViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows reasons to be viewed or edited.
    """
    queryset = Reason.objects.all()
    serializer_class = ReasonSerializer
    permission_classes = [permissions.IsAuthenticated]

class GlobalDataViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows global data to be viewed or edited.
    """
    queryset = GlobalData.objects.all().order_by('id')
    serializer_class = GlobalDataSerializer
    permission_classes = [permissions.IsAuthenticated]

class CorpusViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows global data to be viewed or edited.
    """
    queryset = Corpus.objects.all().order_by('id')
    serializer_class = CorpusSerializer
    permission_classes = [permissions.IsAuthenticated]

class CommentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows feching profiles with its comments.
    """
    pagination_class = None
    queryset = Profile.objects.all().order_by('id')
    serializer_class = CommentsCorpusSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Optionally restricts the returned comments to a given corpus,
        by filtering against a `corpus` query parameter in the URL.
        """
        queryset = Profile.objects.all()
        corpus = self.request.query_params.get('corpus', None)
        if corpus is not None:
            queryset = queryset.filter(corpus=corpus)
        return queryset


class LabeledDataViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows profiles to export with labeled data
    to be viewed.
    """
    pagination_class = None
    queryset = Profile.objects.filter(validated_data__isnull=False).all()
    serializer_class = LabeledDataSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Optionally restricts the returned comments to a given corpus,
        by filtering against a `corpus` query parameter in the URL.
        """
        queryset = Profile.objects.filter(validated_data__isnull=False).all()
        corpus = self.request.query_params.get('corpus', None)
        if corpus is not None:
            queryset = queryset.filter(corpus=corpus)
        return queryset