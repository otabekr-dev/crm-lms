from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'first_name', 'last_name',
            'username','password', 'confirm',
            'role'
        ]
        read_only_fields = ['id']


    def validate(self, attrs):
        if attrs['password'] != attrs['confirm']:
            raise serializers.ValidationError(
                'Passwords not matching'
            )
        if len(attrs['password']) < 8:
            raise serializers.ValidationError(
                'Password should have at least 8 characters'
            )
        return attrs


    def create(self, validated_data):
        validated_data.pop('confirm')
        user = User.objects.create_user(
            username=validated_data['username'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),   
            password=validated_data['password'],              
            role=validated_data['role']
        )
        return user

class MeSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'role']
                

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)                
    confirm = serializers.CharField(write_only=True)


    def validate(self, attrs):
        request = self.context['request']
        user = request.user

        if not user.check_password(attrs['old_password']):
            raise serializers.ValidationError('Incorrect password')


        if attrs['new_password'] != attrs['confirm']:
            raise serializers.ValidationError('Passwords are not matching')


        if len(attrs['new_password']) < 8:
            raise serializers.ValidationError('Password is short')

        return attrs


    def save(self, **kwargs):
        request = self.context['request']
        user = request.user 
        new_password = self.validated_data['new_password']

        user.set_password(new_password)
        user.must_change_password = False
        user.save()
        return user
                                  