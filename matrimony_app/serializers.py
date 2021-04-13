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

class LikedStatusSerializer(serializers.ModelSerializer):
	class Meta:
		model = LikedStatus
		fields = '__all__'

class ViewdDetailsSerialzers(serializers.ModelSerializer):
	class Meta:
		model=Viewed_matches
		fields = '__all__'

class Partner_PreferencesSerialzers(serializers.ModelSerializer):
	class Meta:
		model=Partner_Preferences
		fields = '__all__'

class CountrySerializer(serializers.ModelSerializer):
	class Meta:
		model = Country
		fields = '__all__'


class StateSerializer(serializers.ModelSerializer):
	class Meta:
		model = State
		fields = '__all__'


class CitySerializer(serializers.ModelSerializer):
	class Meta:
		model = City
		fields = '__all__'

class FriendRequestsSerializer(serializers.ModelSerializer):
	class Meta:
		model = FriendRequests
		fields = '__all__'

class NullDataRequestSerialzers(serializers.ModelSerializer):
	class Meta:
		model=NullDataRequest
		fields = '__all__'
		
class ReligionSerializer(serializers.ModelSerializer):
	class Meta:
		model = Religion
		fields = '__all__'
class Job_sectorSerializer(serializers.ModelSerializer):
	class Meta:
		model = Job_sector
		fields = '__all__'
class Marital_statusSerializer(serializers.ModelSerializer):
	class Meta:
		model = Marital_status
		fields = '__all__'
class Mother_OccSerializer(serializers.ModelSerializer):
	class Meta:
		model = Mother_Occ
		fields = '__all__'
class Physical_statusSerializer(serializers.ModelSerializer):
	class Meta:
		model = Physical_status
		fields = '__all__'
class Mother_TongueSerializer(serializers.ModelSerializer):
	class Meta:
		model = Mother_Tongue
		fields = '__all__'
class Post_graduationSerializer(serializers.ModelSerializer):
	class Meta:
		model = Post_graduation
		fields = '__all__'
class ProfessionSerializer(serializers.ModelSerializer):
	class Meta:
		model = Profession
		fields = '__all__'
class QualificationSerializer(serializers.ModelSerializer):
	class Meta:
		model = Qualification
		fields = '__all__'
class RasiSerializer(serializers.ModelSerializer):
	class Meta:
		model = Rasi
		fields = '__all__'
class Smoke_HobbitSerializer(serializers.ModelSerializer):
	class Meta:
		model = Smoke_Hobbit
		fields = '__all__'
class StarsSerializer(serializers.ModelSerializer):
	class Meta:
		model = Stars
		fields = '__all__'
class Super_specialitySerializer(serializers.ModelSerializer):
	class Meta:
		model = Super_speciality
		fields = '__all__'
class Under_graduationSerializer(serializers.ModelSerializer):
	class Meta:
		model = Under_graduation
		fields = '__all__'

class CasteSerializer(serializers.ModelSerializer):
	class Meta:
		model = Caste
		fields = '__all__'

class Birth_placeSerializer(serializers.ModelSerializer):
	class Meta:
		model = Birth_place
		fields = '__all__'
class Annual_incomeSerializer(serializers.ModelSerializer):
	class Meta:
		model = Annual_income
		fields = '__all__'
class CitizenSerializer(serializers.ModelSerializer):
	class Meta:
		model = Citizen
		fields = '__all__'
class Created_bySerializer(serializers.ModelSerializer):
	class Meta:
		model = Created_by
		fields = '__all__'
class Drink_HobbitSerializer(serializers.ModelSerializer):
	class Meta:
		model = Drink_Hobbit
		fields = '__all__'
class Family_typeSerializer(serializers.ModelSerializer):
	class Meta:
		model = Family_type
		fields = '__all__'
class Father_OccSerializer(serializers.ModelSerializer):
	class Meta:
		model = Father_Occ
		fields = '__all__'
class Food_HobbitSerializer(serializers.ModelSerializer):
	class Meta:
		model = Food_Hobbit
		fields = '__all__'
class GenderSerializer(serializers.ModelSerializer):
	class Meta:
		model = Gender
		fields = '__all__'
class HeightSerializer(serializers.ModelSerializer):
	class Meta:
		model = Height
		fields = '__all__'
class AgeSerializer(serializers.ModelSerializer):
	class Meta:
		model = Age
		fields = '__all__'
