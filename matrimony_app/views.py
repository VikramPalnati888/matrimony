import requests
import pytz
import json
import uuid
from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Q
from operator import itemgetter 
from django.core.exceptions import ObjectDoesNotExist
from matrimony_app.send_otp import *
from matrimony_app.models import *
from matrimony_app.serializers import *
from datetime import datetime, date 


def generate_otp():
	"""Generating 4 digits OTP automatically"""
	otp = str(uuid.uuid4().fields[-1])[:4]
	return otp

def generate_Id():
	userid = str(uuid.uuid4().fields[-1])[:4]
	return "MID"+userid

def calculate_age(born):
	today = date.today()
	born_date = born.split('/')
	age = today.year - int(born_date[2]) - ((today.month, today.day) < (int(born_date[1]), int(born_date[0])))
	return age

class Login(APIView):

	def post(self,request,format = "json"):
		data = request.data
		try:
			phn_num_obj= UserBasicDetails.objects.get(phone_number = data['phone_number'])
			generated_otp = generate_otp()
			try:
				existed_otp = SaveOTP.objects.get(phone_number__phone_number=data['phone_number'])
				sending_otp(existed_otp.otp,data['phone_number'])
				return Response({'status':True,
									'otp': existed_otp.otp,
									'phone_number': data['phone_number'],
									'message':"Otp resent Successful"},status=status.HTTP_201_CREATED)
			except Exception as e:
				SaveOTP.objects.create(phone_number=phn_num_obj, otp= generated_otp)
				sending_otp(generated_otp,data['phone_number'])
				return Response({'status':True,
									'otp': generated_otp,
									'phone_number': data['phone_number'],
									'message':"otp sent Successful"},status=status.HTTP_201_CREATED)
		except Exception as e:
			user_profile = User.objects.create_user(username=data['phone_number'])
			user_details = UserBasicDetails.objects.create(user=user_profile,matrimony_id=generate_Id(),phone_number=data['phone_number'])
			otp_generated = generate_otp()
			SaveOTP.objects.create(phone_number=user_details, otp= otp_generated)
			sending_otp(otp_generated,data['phone_number'])
			return Response({'status':True,
								'otp': otp_generated,
								'phone_number': data['phone_number'],
								'message':"Profile created Successful"},status=status.HTTP_201_CREATED)
		else:
			return Response({'status':False,
								'message':'given details already existed or worng details entered'},status=status.HTTP_400_BAD_REQUEST)

class resend_otp(APIView):
	
	def post(self, request):
		data =  request.data
		try:
			existed_otp = SaveOTP.objects.get(phone_number__phone_number=data['phone_number'])
			sending_otp(existed_otp.otp,data['phone_number'])
			return Response({'status':True,
								'otp': existed_otp.otp,
								'phone_number': data['phone_number'],
								'message':"Otp resent Successful"},status=status.HTTP_201_CREATED)
		except Exception as e:
			print(e)
			return Response({'status':False,
								'message':'details not exist please register'},status=status.HTTP_400_BAD_REQUEST)

class otp_verification(APIView):

	def post(self, request, format=None):
		data = request.data
		user_obj = UserBasicDetails.objects.get(phone_number=data['phone_number'])
			
		try:
			otp_obj = SaveOTP.objects.get(phone_number=user_obj)
			if otp_obj.otp == int(data['otp']):
				user=authenticate(request,username=data['phone_number'])
				if user is not None:
					login(request,user)
					otp_obj.delete()
					try:
						user_name = UserFullDetails.objects.get(basic_details__id=user_obj.id)
						return Response({
										"status":True,
										"user_status":user.is_authenticated, 
										"user_id": user.id,
										"phone_number":data['phone_number'],
										"matrimony_id":user_obj.matrimony_id,
										"username": user_name.name,
										"message": "Login Successful"
										},status=status.HTTP_200_OK)
					except Exception as e:
						return Response({
										"status":True,
										"user_status":user.is_authenticated, 
										"user_id": user.id,
										"phone_number":data['phone_number'],
										"matrimony_id":user_obj.matrimony_id,
										"username": None,
										"message": "Login Successful"
										},status=status.HTTP_200_OK)
				else:
					return Response({"user":"Not valid",
										"user_status":False},status=status.HTTP_400_BAD_REQUEST)
			else:
				return Response({"status":False,
									"error":"invalid otp"},status = status.HTTP_401_UNAUTHORIZED)
		except ObjectDoesNotExist:
			return Response({"status":False,
								"message":"No Data found"},status=status.HTTP_400_BAD_REQUEST)


class Logout(APIView):

	def get(self,request,format="json"):
		logout(request)
		return Response({"message": "Successful Logout"},status=status.HTTP_200_OK)

class UserFullDetailsView(APIView):
	def get(self, request):
		if not request.POST._mutable:
			request.POST._mutable = True
		response = {}
		userId = request.data.get('user_id')
		try:
			if userId:
				user_basic_obj = UserBasicDetails.objects.get(user__id = userId)
				user_qs = UserFullDetails.objects.get(basic_details__id=user_basic_obj.id)
			else:	
				user_basic_obj = UserBasicDetails.objects.get(user__id = request.user.id)
				user_qs = UserFullDetails.objects.get(basic_details__id=user_basic_obj.id)

		except ObjectDoesNotExist:
			return Response({"message":"UserDetail ObjectDoesNotExist"})
		serializer1=UserBasicDetailsSerialzers(user_basic_obj,many=False)
		response[request.user.id] = serializer1.data
		serializer2=UserFullDetailsSerialzers(user_qs,many=False)
		response[request.user.id].update({"age":calculate_age(user_qs.dateofbirth)})
		response[request.user.id].update(serializer2.data)
		return Response(response.values(),status=status.HTTP_200_OK)

	def post(self, request):
		if not request.POST._mutable:
			request.POST._mutable = True
		data = request.data
		user_basic_obj = UserBasicDetails.objects.get(user__id = request.user.id)
		data['basic_details'] = user_basic_obj.id
		serializer = UserFullDetailsSerialzers(data = data)
		if serializer.is_valid(): 
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	def put(self, request):
		if not request.POST._mutable:
			request.POST._mutable = True
		response = {}
		data = request.data
		user_obj = UserBasicDetails.objects.get(user__id = request.user.id)
		try:
			if data['image'] == '':
				del data['image']
				queryset = UserFullDetails.objects.get(basic_details__user__id=request.user.id)
				serializer = UserFullDetailsSerialzers(queryset, data=data, partial=True)
			else:
				queryset = UserFullDetails.objects.get(basic_details__user__id=request.user.id)
				serializer = UserFullDetailsSerialzers(queryset, data=data, partial=True)
		except Exception as e:
			print(e)
			queryset = UserFullDetails.objects.get(basic_details__user__id=request.user.id)
			serializer = UserFullDetailsSerialzers(queryset, data=data, partial=True)
		if serializer.is_valid():
			serializer.save()
			serializer1=UserBasicDetailsSerialzers(user_obj,many=False)
			response[request.user.id] = serializer1.data
			serializer2=UserFullDetailsSerialzers(queryset,many=False)
			response[request.user.id].update({"age":calculate_age(queryset.dateofbirth)})
			response[request.user.id].update(serializer2.data)
			return Response(response.values(),status=status.HTTP_200_OK)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class droplistDetails(APIView):
	def get(self,request):
		gender_list = ["Male","Female","Others"]
		height_list = ["4’6”","4’7”","4’8”","4’9”","4’10”","4’11”","5’0”",
						"5’1”","5’2”","5’3”","5’4”","5’5”","5’6”","5’7”",
						"5’8”","5’9”","5’10”","5’11”","6’0”"]
		religion_list = ["Hindu","Muslim","Christan","Sikh","Budhist","Jain","Other Religion"]
		qualification_list = ["B.tech","Degree","Inter","BE","10th","Others"]
		caste_list = ["BC","OC","SC","ST","GENERAL","OTEHRS"]
		profession_list = ["Software Developer","Software Engineer","Teacher","Driver","Govt Job","Police"]
		citizen_list = ["Indian","USA","Sweden","Uk"]
		created_by_list = ["Father","Mother","Brother","sister","Grand Father","Grand Mother"]
		mother_tongue_list = ["Telugu","Hindi","Tamil","kannada"]
		physical_status_list = ["Yes","No"]
		marital_status_list = ["Married","Single"]
		annual_income_list = ["1-2","2-3","3-4","5-6","6-7","7+"]
		family_type_list = ["1","2","3","4","5","6"]
		birth_place_list = ["Hyderabad","Warangal","Karimanagr","Medak"]
		under_graduation_list = ["BA","BE","Btech","Bcom"]
		post_graduation_list = ["MA","MBA","MCA","MCom"]
		super_speciality_list = ["Cardiology","Oncology","Nephrology","Neurology","Endocrinology"]

		response = {
					"Height": height_list,
					"Religion":religion_list,
					"Qualification":qualification_list,
					"Gender":gender_list,
					"Caste":caste_list,
					"SubCaste":sub_caste_list,
					"Profession":profession_list,
					"Location":location_list,
					"State":states_list,
					"Citizen":citizen_list,
					"Created_by":created_by_list,
					"Mother_Tongue":mother_tongue_list,
					"Physical_status":physical_status_list,
					"Marital_status":marital_status_list,
					"Annual_income":annual_income_list,
					"Family_type":family_type_list,
					"Birth_place":birth_place_list,
					"Under_graduation":under_graduation_list,
					"Post_graduation":post_graduation_list,
					"Super_speciality":super_speciality_list,
					}
		return Response(response, status=status.HTTP_200_OK)

class CountryList(APIView):
	def get(self,request):
		queryset = Country.objects.all()
		response=CountrySerializer(queryset,many=True)
		return Response(response.data, status=status.HTTP_200_OK)

class StatesList(APIView):
	def get(self,request):
		queryset = State.objects.filter(country__id=request.GET.get('country_id'))
		response=StateSerializer(queryset,many=True)
		return Response(response.data, status=status.HTTP_200_OK)

class CitiesList(APIView):
	def get(self,request):
		queryset = City.objects.filter(state__id=request.GET.get('state_id'))
		response=CitySerializer(queryset,many=True)
		return Response(response.data, status=status.HTTP_200_OK)

# main Funcationality start from here

class NewMatches(APIView):
	def get(self, request):
		response = {}
		try:
			user_qs	= User.objects.all().order_by('-id')[:10]
			main_obj = UserFullDetails.objects.get(basic_details__user__id=request.user.id)
			for dt in user_qs:
				if not dt.is_superuser:
					user_basic_obj = UserBasicDetails.objects.get(user__id = dt.id)
					user_full_obj = UserFullDetails.objects.get(basic_details__id=user_basic_obj.id)
					if main_obj.gender != user_full_obj.gender:
						serializer1=UserBasicDetailsSerialzers(user_basic_obj,many=False)
						response[dt.id] = serializer1.data
						serializer2=UserFullDetailsSerialzers(user_full_obj,many=False)
						response[dt.id].update({"age":calculate_age(user_full_obj.dateofbirth)})
						response[dt.id].update(serializer2.data)
		except  Exception as e:
			return Response({"message":"UserDetail ObjectDoesNotExist"})
		return Response(response.values(),status=status.HTTP_200_OK)

class ViewdMatches(APIView):
	def post(self, request):
		v_user_id = request.data.get('user_id')
		instance = User.objects.get(id=request.user.id)
		try:
			viewed_obj = Viewed_matches.objects.get(user=instance,viewed_user_id=v_user_id,viewd_status=True)
			return Response({"message":"Already Viewed",
							"status":True})
		except Exception as e:
			Viewed_matches.objects.create(user=instance,viewed_user_id=v_user_id,viewd_status=True)
			return Response({"message":"Viewed Details Saved Successful",
								"status":True})
		

	def get(self, request):
		response = {}
		try:
			viewed_obj = Viewed_matches.objects.filter(user__id=request.user.id)
			for viewed_data in viewed_obj:
				user_basic_obj = UserBasicDetails.objects.get(user = int(viewed_data.viewed_user_id))
				serializer1=UserBasicDetailsSerialzers(user_basic_obj,many=False)
				response[int(viewed_data.viewed_user_id)] = serializer1.data
				
				user_full_obj = UserFullDetails.objects.get(basic_details=user_basic_obj)
				serializer2=UserFullDetailsSerialzers(user_full_obj,many=False)
				response[int(viewed_data.viewed_user_id)].update({"age":calculate_age(user_full_obj.dateofbirth)})
				response[int(viewed_data.viewed_user_id)].update(serializer2.data)
				
				viewed_details_obj = Viewed_matches.objects.get(viewed_user_id = int(viewed_data.viewed_user_id))
				serializer3=ViewdDetailsSerialzers(viewed_details_obj,many=False)
				response[int(viewed_data.viewed_user_id)].update(serializer3.data)
		except  Exception as e:
			print(e)
			return Response({"message":"UserDetail ObjectDoesNotExist"})
		return Response(response.values(),status=status.HTTP_200_OK)


class PPView(APIView):
	def get(self, request):
		userId = request.data.get('user_id')
		try:
			if userId:
				user_basic_obj = UserBasicDetails.objects.get(user__id = userId)
				user_pp = Partner_Preferences.objects.get(basic_details__id=user_basic_obj.id)

			else:	
				user_basic_obj = UserBasicDetails.objects.get(user__id = request.user.id)
				user_pp = Partner_Preferences.objects.get(basic_details__id=user_basic_obj.id)
		except ObjectDoesNotExist:
			return Response({"message":"UserDetail ObjectDoesNotExist"})

		serializer2=Partner_PreferencesSerialzers(user_pp,many=True)
		response[request.user.id].update(serializer2.data)
		return Response(response.values(),status=status.HTTP_200_OK)

	def post(self, request):
		if not request.POST._mutable:
			request.POST._mutable = True
		data = request.data
		user_basic_obj = UserBasicDetails.objects.get(user__id = request.user.id)
		data['basic_details'] = user_basic_obj.id
		serializer = Partner_PreferencesSerialzers(data = data)
		if serializer.is_valid(): 
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	def put(self, request):
		if not request.POST._mutable:
			request.POST._mutable = True
		response = {}
		data = request.data

		queryset = Partner_Preferences.objects.get(basic_details__user__id=request.user.id)
		pp_serializer = Partner_PreferencesSerialzers(queryset, data=data, partial=True)
		if pp_serializer.is_valid():
			pp_serializer.save()
			return Response(pp_serializer.data,status=status.HTTP_200_OK)
		return Response(pp_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PP_matches_View(APIView):
	def get(self, request):
		main_user_id = request.user.id
		userId = request.data.get('user_id')
		try:
			if userId:
				user_basic_obj = UserBasicDetails.objects.get(user__id = userId)
				user_pp = Partner_Preferences.objects.get(basic_details__id=user_basic_obj.id)

			else:	
				user_basic_obj = UserBasicDetails.objects.get(user__id = request.user.id)
				user_pp = Partner_Preferences.objects.get(basic_details__id=user_basic_obj.id)
		except ObjectDoesNotExist:
			return Response({"message":"UserDetail ObjectDoesNotExist"})

		serializer2=Partner_PreferencesSerialzers(user_pp,many=True)
		response[request.user.id].update(serializer2.data)
		return Response(response.values(),status=status.HTTP_200_OK)
