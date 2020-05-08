from rest_framework import serializers
from user.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "password", "name", "sex", "email", "phone", "address")

    def create(self, validated_data):
        return User.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.username = validated_data.get("username", instance.username)
        instance.password = validated_data.get("password", instance.password)
        instance.sex = validated_data.get("sex", instance.sex)
        instance.email = validated_data.get("email", instance.email)
        instance.phone = validated_data.get("phone", instance.phone)
        instance.address = validated_data.get("address", instance.address)
        return instance
