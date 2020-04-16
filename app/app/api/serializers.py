from django.contrib.auth.models import User, Group
from rest_framework import serializers
from app.api.models import Profile, ProfileData, Comment, Reason


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']

class UserNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username']

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']

class ProfileDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileData
        fields = '__all__'

class ExportSerializer(serializers.ModelSerializer):
    validated_data = ProfileDataSerializer()
    class Meta:
        model = Profile        
        fields = ['experiment_id', 'validated_data']
        read_only_fields = ['experiment_id', 'validated_data']

class ReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reason
        fields = ['reason', 'profile_data_type']

class ProfileSerializer(serializers.ModelSerializer):
    system_data = ProfileDataSerializer(read_only=True)
    validated_data = ProfileDataSerializer()
    validated_by = UserNameSerializer()
    reasons = ReasonSerializer(many=True)

    # Create a custom method field
    data = serializers.SerializerMethodField('_datas')

    # Use this method for the custom field
    def _datas(self, obj):
        if (obj.validated_data != None):
            return ProfileDataSerializer(obj.validated_data).data
        return ProfileDataSerializer(obj.system_data).data

    class Meta:
        model = Profile
        fields = ['id', 'experiment_id', 'reddit_username', 'is_valid', 'validated_by', 'system_data', 'validated_data', 'data', 'reasons']
        read_only_fields = ['experiment_id', 'reddit_username', 'is_valid', 'validated_by', 'system_data', 'reasons']

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

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['date', 'text']

class ProfileNLPSerializer(serializers.ModelSerializer):
    system_data = ProfileDataSerializer()
    validated_data = ProfileDataSerializer(read_only=True)
    reasons = ReasonSerializer(many=True)
    comments = CommentSerializer(many=True)

    class Meta:
        model = Profile        
        fields = ['id', 'experiment_id', 'reddit_username', 'system_data', 'validated_data', 'reasons', 'comments']
        read_only_fields = ['validated_data']

    def create(self, v_data):
        system_data_v_data = v_data.pop('system_data')
        reasons_v_data = v_data.pop('reasons')
        comments_v_data = v_data.pop('comments')

        instance = Profile.objects.create(**v_data)
        system_data_serializer = self.fields['system_data']
        instance.system_data = system_data_serializer.create(system_data_v_data)
        instance.save()
        for reason in reasons_v_data:
            Reason.objects.create(profile=instance, **reason)
        for comment in comments_v_data:
            Comment.objects.create(profile=instance, **comment)
        return instance

