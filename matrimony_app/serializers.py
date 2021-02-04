from rest_framework import serializers
from matrimony_app.models import *
from django.contrib.auth.models import User


class UserBasicDetailsSerialzers(serializers.ModelSerializer):
	class Meta:
		model=UserBasicDetails
		fields = '__all__'

class UserFullDetailsSerialzers(serializers.ModelSerializer):
	class Meta:
		model=UserFullDetails
		fields = '__all__'