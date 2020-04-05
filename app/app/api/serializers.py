from django.contrib.auth.models import User, Group
from rest_framework import serializers
from app.api.models import Profile, ProfileData, Comment, Reason


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']

class ReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reason
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'

class ProfileDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileData
        fields = '__all__'

class ProfileSerializer(serializers.ModelSerializer):
    data = ProfileDataSerializer(read_only=True)
    validated_data = ProfileDataSerializer()

    # Create a custom method field
    datas = serializers.SerializerMethodField('_datas')

    # Use this method for the custom field
    def _datas(self, obj):
        if (obj.validated_data != None):
            return ProfileDataSerializer(obj.validated_data).data
        return ProfileDataSerializer(obj.data).data

    class Meta:
        model = Profile
        fields = ['datas', 'experiment_id', 'reddit_username', 'is_valid', 'validated_by', 'data', 'validated_data']
        read_only_fields = ['experiment_id', 'reddit_username', 'is_valid', 'validated_by', 'data']

    def update(self, instance, v_data):
        validated_data_v_data = v_data.pop('validated_data')
        validated_data_serializer = self.fields['validated_data']
        if instance.validated_data != None:
            instance.validated_data = validated_data_serializer.update(instance.validated_data, validated_data_v_data)
        else:
            instance.validated_data = validated_data_serializer.create(validated_data_v_data)
        instance.is_valid = True
        instance.validated_by = self.context['request'].user
        instance.save()
        return instance
