from django.contrib.auth import authenticate
from django.contrib.auth.models import Group, User
from django.shortcuts import render
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from app.api.models import Profile, ProfileData, Reason
from app.api.serializers import (ExportSerializer, GroupSerializer,
                                 ProfileDataSerializer, ProfileNLPSerializer,
                                 ProfileSerializer, ReasonSerializer,
                                 UserSerializer)


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
    queryset = Profile.objects.filter(validated_data__isnull=False).all()
    serializer_class = ExportSerializer
    permission_classes = [permissions.IsAuthenticated]

class ProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows profiles to be viewed or edited.
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

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
