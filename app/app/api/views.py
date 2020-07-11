from django.contrib.auth import authenticate
from django.contrib.auth.models import Group, User
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

from app.api.models import Profile, ProfileData, Reason, GlobalData
from app.api.serializers import (ExportSerializer, GroupSerializer,
                                 ProfileDataSerializer, ProfileNLPSerializer,
                                 ProfileSerializer, ReasonSerializer,
                                 UserSerializer, GlobalDataSerializer)


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

class ProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows profiles to be viewed or edited.
    """
    queryset = Profile.objects.all().order_by('experiment_id')
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

class GlobalDataViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows global data to be viewed or edited.
    """
    queryset = GlobalData.objects.all().order_by('id')
    serializer_class = GlobalDataSerializer
    permission_classes = [permissions.IsAuthenticated]