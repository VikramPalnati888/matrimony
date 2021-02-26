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

class ViewdDetailsSerialzers(serializers.ModelSerializer):
	class Meta:
		model=Viewed_matches
		fields = '__all__'

class Partner_PreferencesSerialzers(serializers.ModelSerializer):
	class Meta:
		model=Partner_Preferences
		fields = '__all__'
