from django.shortcuts import render

from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import action
from app.api.serializers import UserSerializer, GroupSerializer, ProfileSerializer, ProfileDataSerializer, ReasonSerializer, ExportSerializer
from app.api.models import Profile, ProfileData, Reason
from rest_framework.response import Response


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