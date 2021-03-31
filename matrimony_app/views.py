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
import base64
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings
import ast
from django.forms.models import model_to_dict
from collections import ChainMap
import random

def generate_otp():
	"""Generating 4 digits OTP automatically"""
	otp = str(uuid.uuid4().fields[-1])[:4]
	return otp

def generate_Id():
	userid = str(uuid.uuid4().fields[-1])[:4]
	return "MID"+userid

def calculate_age(born):
	today = date.today()
	DOB = born.split('/')
	born_date = DOB[1]
	born_month = DOB[0]
	born_year  = DOB[2]
	age = today.year - int(born_year) - ((today.month, today.day) < (int(born_month), int(born_date)))
	return age

def height_replaced(height):
	ht = height.replace('’','.')
	return float(ht)

def min_height_replaced(height):
	ht = height.replace('’','.')
	return float(ht)

def max_height_replaced(height):
	ht = height.replace('’','.')
	return float(ht)

def height_range(min_height,max_height):
	return_height = []
	height_list = [4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 4.10, 4.11, 5.0, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8,
					5.9, 5.10, 5.11, 6.0, 6.1, 6.2]
	for i in height_list:
		if min_height < i < max_height:
			return_height.append(i)
	return return_height

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
										"image":user_name.image.url,
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
										"image": None,
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
		userId = request.GET.get('user_id')
		main_user_id = request.GET.get('main_user_id')
		login_user_id = request.GET.get('login_user_id')
		try:
			if userId:
				user_basic_obj = UserBasicDetails.objects.get(user__id = userId)
				user_qs = UserFullDetails.objects.get(basic_details__id=user_basic_obj.id)
			else:	
				user_basic_obj = UserBasicDetails.objects.get(user__id = main_user_id)
				user_qs = UserFullDetails.objects.get(basic_details__id=user_basic_obj.id)
		except ObjectDoesNotExist:
			return Response({"message":"UserDetail ObjectDoesNotExist"})

		serializer1=UserBasicDetailsSerialzers(user_basic_obj,many=False)
		response[main_user_id] = serializer1.data
		serializer2=UserFullDetailsSerialzers(user_qs,many=False)
		response[main_user_id].update({"age":calculate_age(user_qs.dateofbirth)})
		response[main_user_id].update(serializer2.data)
		try:
			if userId:
				liked_obj = LikedStatus.objects.get(user__id = login_user_id,user_liked=userId)
				response[main_user_id].update({"LikedStatus":liked_obj.LikedStatus})
			else:
				liked_obj = LikedStatus.objects.get(user__id = login_user_id,user_liked=main_user_id)
				response[main_user_id].update({"LikedStatus":liked_obj.LikedStatus})
		except Exception as e:
			response[main_user_id].update({"LikedStatus":False})
		return Response(response.values(),status=status.HTTP_200_OK)

	def post(self, request):
		if not request.POST._mutable:
			request.POST._mutable = True
		user_id = request.GET.get('user_id')
		data = ast.literal_eval(request.data['registerdata'])
		user_basic_obj = UserBasicDetails.objects.get(user__id = user_id)
		
		try:
			userFull_details = UserFullDetails.objects.get(basic_details__id=user_basic_obj.id)
			data['image'] = request.FILES['image']
			data['basic_details'] = int(user_basic_obj.id)
			serializer = UserFullDetailsSerialzers(userFull_details,data = data, partial=True)
			if serializer.is_valid():
				serializer.save()
				return Response(serializer.data, status=status.HTTP_200_OK)
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
		except Exception as e:
			data['image'] = request.FILES['image']
			data['basic_details'] = int(user_basic_obj.id)
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
		user_id = request.GET.get('user_id')
		user_obj = UserBasicDetails.objects.get(user__id = user_id)
		try:
			if data['image'] == '':
				del data['image']
				queryset = UserFullDetails.objects.get(basic_details__user__id=user_id)
				serializer = UserFullDetailsSerialzers(queryset, data=data, partial=True)
			else:
				queryset = UserFullDetails.objects.get(basic_details__user__id=user_id)
				serializer = UserFullDetailsSerialzers(queryset, data=data, partial=True)
		except Exception as e:
			print(e)
			queryset = UserFullDetails.objects.get(basic_details__user__id=user_id)
			serializer = UserFullDetailsSerialzers(queryset, data=data, partial=True)
		if serializer.is_valid():
			serializer.save()
			serializer1=UserBasicDetailsSerialzers(user_obj,many=False)
			response[user_id] = serializer1.data
			serializer2=UserFullDetailsSerialzers(queryset,many=False)
			response[user_id].update({"age":calculate_age(queryset.dateofbirth)})
			response[user_id].update(serializer2.data)
			return Response(response.values(),status=status.HTTP_200_OK)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class droplistDetails(APIView):
	def get(self,request):
		response = {
					"Height": [h.height for h in Height.objects.all()],
					"Religion":[rel.religion for rel in Religion.objects.all()],
					"Qualification":[qual.qualification for qual in Qualification.objects.all()],
					"Gender":[gen.gender for gen in Gender.objects.all()],
					"Caste":[cast.caste for cast in Caste.objects.all()],
					"Profession":[pro.profession for pro in Profession.objects.all()],
					"Citizen":[cit.citizen for cit in Citizen.objects.all()],
					"Created_by":[cb.created_by for cb in Created_by.objects.all()],
					"Mother_Tongue":[mt.mother_Tongue for mt in Mother_Tongue.objects.all()],
					"Physical_status":[ps.physical_status for ps in Physical_status.objects.all()],
					"Marital_status":[ms.marital_status for ms in Marital_status.objects.all()],
					"Annual_income":[ai.annual_income for ai in Annual_income.objects.all()],
					"Family_type":[ft.family_type for ft in Family_type.objects.all()],
					"Birth_place":[bp.birth_place for bp in Birth_place.objects.all()],
					"Under_graduation":[ug.under_graduation for ug in Under_graduation.objects.all()],
					"Post_graduation":[pg.post_graduation for pg in Post_graduation.objects.all()],
					"Super_speciality":[ss.super_speciality for ss in Super_speciality.objects.all()],
					"Rasi": [r.rasi for r in Rasi.objects.all()],
					"Age": [a.age for a in Age.objects.all()],
					"Stars": [s.stars for s in Stars.objects.all()],
					"Mother_Occ": [mo.mother_Occ for mo in Mother_Occ.objects.all()],
					"Father_Occ":[fo.father_Occ for fo in Father_Occ.objects.all()],
					"Food_Hobbit":[fh.food_Hobbit for fh in Food_Hobbit.objects.all()],
					"Drink_Hobbit":[dh.drink_Hobbit for dh in Drink_Hobbit.objects.all()],
					"Smoke_Hobbit":[smoke.smoke_Hobbit for smoke in Smoke_Hobbit.objects.all()],
					"Job_sector":[job.job_sector for job in Job_sector.objects.all()],
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
		state_id = request.GET.get('state_id')
		state_name = request.GET.get('state_name')
		if state_id:
			queryset = City.objects.filter(state__id=state_id)
		else:
			queryset = City.objects.filter(state__state=state_name)
		response=CitySerializer(queryset,many=True)
		return Response(response.data, status=status.HTTP_200_OK)

class ReligionView(APIView):
	def post(self, request):
		data = request.data
		serializer = ReligionSerializer(data = data)
		if serializer.is_valid(): 
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Job_sectorView(APIView):
	def post(self, request):
		data = request.data
		serializer = Job_sectorSerializer(data = data)
		if serializer.is_valid(): 
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Marital_statusView(APIView):
	def post(self, request):
		data = request.data
		serializer = Marital_statusSerializer(data = data)
		if serializer.is_valid(): 
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Mother_OccView(APIView):
	def post(self, request):
		data = request.data
		serializer = Mother_OccSerializer(data = data)
		if serializer.is_valid(): 
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Physical_statusView(APIView):
	def post(self, request):
		data = request.data
		serializer = Physical_statusSerializer(data = data)
		if serializer.is_valid(): 
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Mother_TongueView(APIView):
	def post(self, request):
		data = request.data
		serializer = Mother_TongueSerializer(data = data)
		if serializer.is_valid(): 
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Post_graduationView(APIView):
	def post(self, request):
		data = request.data
		serializer = Post_graduationSerializer(data = data)
		if serializer.is_valid(): 
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	def get(self, request):
		response = {}
		pg	= Post_graduation.objects.all()
		for dt in pg:
			response[dt.id] = {'id':dt.id,
								'post_graduation':dt.post_graduation}
		return Response(response.values(),status=status.HTTP_200_OK)

class ProfessionView(APIView):
	def post(self, request):
		data = request.data
		serializer = ProfessionSerializer(data = data)
		if serializer.is_valid(): 
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class QualificationView(APIView):
	def post(self, request):
		data = request.data
		serializer = QualificationSerializer(data = data)
		if serializer.is_valid(): 
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RasiView(APIView):
	def post(self, request):
		data = request.data
		serializer = RasiSerializer(data = data)
		if serializer.is_valid(): 
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Smoke_HobbitView(APIView):
	def post(self, request):
		data = request.data
		serializer = Smoke_HobbitSerializer(data = data)
		if serializer.is_valid(): 
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class StarsView(APIView):
	def post(self, request):
		data = request.data
		serializer = StarsSerializer(data = data)
		if serializer.is_valid(): 
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Super_specialityView(APIView):
	def post(self, request):
		data = request.data
		serializer = Super_specialitySerializer(data = data)
		if serializer.is_valid(): 
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Under_graduationView(APIView):
	def post(self, request):
		data = request.data
		serializer = Under_graduationSerializer(data = data)
		if serializer.is_valid(): 
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	def get(self, request):
		response = {}
		ug	= Under_graduation.objects.all()
		for dt in ug:
			response[dt.id] = {'id':dt.id,
								'under_graduation':dt.under_graduation}
		return Response(response.values(),status=status.HTTP_200_OK)
		
class CasteView(APIView):
	def post(self, request):
		data = request.data
		serializer = CasteSerializer(data = data)
		if serializer.is_valid(): 
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Birth_placeView(APIView):
	def post(self, request):
		data = request.data
		serializer = Birth_placeSerializer(data = data)
		if serializer.is_valid(): 
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Annual_incomeView(APIView):
	def post(self, request):
		data = request.data
		serializer = Annual_incomeSerializer(data = data)
		if serializer.is_valid(): 
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CitizenView(APIView):
	def post(self, request):
		data = request.data
		serializer = CitizenSerializer(data = data)
		if serializer.is_valid(): 
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Created_byView(APIView):
	def post(self, request):
		data = request.data
		serializer = Created_bySerializer(data = data)
		if serializer.is_valid(): 
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Drink_HobbitView(APIView):
	def post(self, request):
		data = request.data
		serializer = Drink_HobbitSerializer(data = data)
		if serializer.is_valid(): 
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Family_typeView(APIView):
	def post(self, request):
		data = request.data
		serializer = Family_typeSerializer(data = data)
		if serializer.is_valid(): 
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Father_OccView(APIView):
	def post(self, request):
		data = request.data
		serializer = Father_OccSerializer(data = data)
		if serializer.is_valid(): 
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Food_HobbitView(APIView):
	def post(self, request):
		data = request.data
		serializer = Food_HobbitSerializer(data = data)
		if serializer.is_valid(): 
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GenderView(APIView):
	def post(self, request):
		data = request.data
		serializer = GenderSerializer(data = data)
		if serializer.is_valid(): 
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class HeightView(APIView):
	def post(self, request):
		data = request.data
		serializer = HeightSerializer(data = data)
		if serializer.is_valid(): 
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AgeView(APIView):
	def post(self, request):
		data = request.data
		serializer = AgeSerializer(data = data)
		if serializer.is_valid(): 
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# main Funcationality start from here

class NewMatches(APIView):
	def get(self, request):
		response = {}
		user_id = request.GET.get('user_id')
		try:
			user_qs	= User.objects.all().order_by('-id')
			main_obj = UserFullDetails.objects.get(basic_details__user__id=user_id)
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
						try:
							liked_obj = LikedStatus.objects.get(user__id=user_id,user_liked =int(dt.id))
							response[dt.id].update({"LikedStatus":liked_obj.LikedStatus})
						except Exception as e:
							response[dt.id].update({"LikedStatus":False})
		except  Exception as e:
			print(e)
			return Response({"message":"UserDetail ObjectDoesNotExist"})
		return Response(response.values(),status=status.HTTP_200_OK)


class LikeView(APIView):
	def post(self, request):
		user_id = request.GET.get('user_id')
		lu_id = request.data.get('liked_user_id')
		ls = request.data.get('liked_status')
		instance = User.objects.get(id=user_id)
		try:
			ls_obj = LikedStatus.objects.get(user=instance,user_liked=lu_id)
			ls_obj.delete()
			return Response({"message":"unliked",
							"status": False})
		except Exception as e:
			LikedStatus.objects.create(user=instance,user_liked=lu_id,LikedStatus=True)
			return Response({"message":"liked",
							"status":True})
	def get(self, request):
		response = {}
		user_id = request.GET.get('user_id')
		try:
			liked_obj = LikedStatus.objects.filter(user__id=user_id)
			for liked_data in liked_obj:
				user_basic_obj = UserBasicDetails.objects.get(user = int(liked_data.user_liked))
				serializer1=UserBasicDetailsSerialzers(user_basic_obj,many=False)
				response[int(liked_data.user_liked)] = serializer1.data
				
				user_full_obj = UserFullDetails.objects.get(basic_details=user_basic_obj)
				serializer2=UserFullDetailsSerialzers(user_full_obj,many=False)
				response[int(liked_data.user_liked)].update({"age":calculate_age(user_full_obj.dateofbirth)})
				response[int(liked_data.user_liked)].update(serializer2.data)
				
				liked_details_obj = LikedStatus.objects.get(user__id=user_id,user_liked = int(liked_data.user_liked))
				serializer3=ViewdDetailsSerialzers(liked_details_obj,many=False)
				response[int(liked_data.user_liked)].update({"LikedStatus":liked_details_obj.LikedStatus})
		except  Exception as e:
			print(e)
			return Response({"message":"UserDetail ObjectDoesNotExist"})
		return Response(response.values(),status=status.HTTP_200_OK)	

class ViewdMatches(APIView):
	def post(self, request):
		v_user_id = request.data.get('view_user_id')
		user_id = request.GET.get('user_id')
		instance = User.objects.get(id=user_id)
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
		user_id = request.GET.get('user_id')
		try:
			viewed_obj = Viewed_matches.objects.filter(user__id=user_id)
			for viewed_data in viewed_obj:
				user_basic_obj = UserBasicDetails.objects.get(user = int(viewed_data.viewed_user_id))
				serializer1=UserBasicDetailsSerialzers(user_basic_obj,many=False)
				response[user_basic_obj.user.id] = serializer1.data
				
				user_full_obj = UserFullDetails.objects.get(basic_details=user_basic_obj)
				serializer2=UserFullDetailsSerialzers(user_full_obj,many=False)
				response[user_full_obj.basic_details.user.id].update({"age":calculate_age(user_full_obj.dateofbirth)})
				response[user_full_obj.basic_details.user.id].update(serializer2.data)
				
				viewed_details_obj = Viewed_matches.objects.get(viewed_user_id = int(viewed_data.viewed_user_id))
				serializer3=ViewdDetailsSerialzers(viewed_details_obj,many=False)
				response[int(viewed_data.viewed_user_id)].update({'viewd_status':viewed_data.viewd_status})
				try:
					liked_obj = LikedStatus.objects.get(user__id=user_id,user_liked = viewed_data.viewed_user_id)
					response[int(liked_obj.user_liked)].update({"LikedStatus":liked_obj.LikedStatus})
				except Exception as e:
					print(e)
					response[int(viewed_data.viewed_user_id)].update({"LikedStatus":False})
		except  Exception as e:
			return Response({"message":"UserDetail ObjectDoesNotExist"})
		return Response(response.values(),status=status.HTTP_200_OK)


class PPView(APIView):
	def get(self, request):
		user_id = request.GET.get('user_id')
		response = {}
		try:
				user_basic_obj = UserBasicDetails.objects.get(user__id = user_id)
				user_pp = Partner_Preferences.objects.get(basic_details__id=user_basic_obj.id)
		except ObjectDoesNotExist:
				return Response({"message":"UserDetail ObjectDoesNotExist"})
		serializer2=Partner_PreferencesSerialzers(user_pp,many=False)
		response.update(serializer2.data)
		return Response(response,status=status.HTTP_200_OK)

	def post(self, request):
		if not request.POST._mutable:
			request.POST._mutable = True
		data = request.data
		response = {}
		user_id = request.GET.get('user_id')
		user_basic_obj = UserBasicDetails.objects.get(user__id = user_id)
		data['basic_details'] = user_basic_obj.id
		try:
			user_pp = Partner_Preferences.objects.get(basic_details__id=user_basic_obj.id)
			serializer2=Partner_PreferencesSerialzers(user_pp,many=False)
			response.update(serializer2.data)
			return Response(response,status=status.HTTP_200_OK)
		except Exception as e:
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
		user_id = request.GET.get('user_id')
		queryset = Partner_Preferences.objects.get(basic_details__user__id=user_id)
		pp_serializer = Partner_PreferencesSerialzers(queryset, data=data, partial=True)
		if pp_serializer.is_valid():
			pp_serializer.save()
			return Response(pp_serializer.data,status=status.HTTP_200_OK)
		return Response(pp_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SearchingView(APIView):
	def post(self, request):
		response = {}
		main_user_id = request.GET.get('user_id')
		mId = request.GET.get('matrimony_id')
		try:
			if mId:
				user_basic_obj = UserBasicDetails.objects.get(matrimony_id = mId)
				user_full_obj = UserFullDetails.objects.get(basic_details__id=user_basic_obj.id)
		except ObjectDoesNotExist:
			return Response({"message":"UserDetail ObjectDoesNotExist"})
		serializer1=UserBasicDetailsSerialzers(user_basic_obj,many=False)
		response[user_basic_obj.id] = serializer1.data
		serializer2=UserFullDetailsSerialzers(user_full_obj,many=False)
		response[user_basic_obj.id].update({"age":calculate_age(user_full_obj.dateofbirth)})
		response[user_basic_obj.id].update(serializer2.data)
		return Response(response.values(),status=status.HTTP_200_OK)

class SearchingPPView(APIView):
	def post(self, request):
		response = {}
		main_user_id = request.GET.get('user_id')
		data = request.data
		try:
			main_user = UserBasicDetails.objects.get(user__id = main_user_id)
			main_user_full = UserFullDetails.objects.get(basic_details__id=main_user.id)
			user_full_obj = UserFullDetails.objects.filter(	physical_status = data['physical_status'],
															marital_status = data['marital_status'],
															mother_tongue = data['mother_tongue'],
															occupation = data['occupation'],
															under_graduation = data['under_graduation'],
															post_graduation = data['post_graduation'],
															star = data['star'],
															caste = data['caste'],
															religion = data['religion'],
															city = data['city'],
															state = data['state'],
															country = data['country'],
															citizenship =data['citizenship'])
			for dt in user_full_obj:
				if main_user.user.id != dt.basic_details.user.id and  main_user_full.gender != dt.gender:
					if calculate_age(dt.dateofbirth) in range(int(data['min_age']),int(data['max_age'])):
						if height_replaced(dt.height) in height_range(min_height_replaced(data['min_height']),max_height_replaced(data['max_height'])):
							user_basic_obj = UserBasicDetails.objects.get(user__id = dt.basic_details.user.id)
							serializer1=UserBasicDetailsSerialzers(user_basic_obj,many=False)
							response[dt.id] = serializer1.data
							user_full = UserFullDetails.objects.get(basic_details__id=user_basic_obj.id)
							serializer2=UserFullDetailsSerialzers(user_full,many=False)
							response[dt.id].update({"age":calculate_age(dt.dateofbirth)})
							response[dt.id].update(serializer2.data)
		except ObjectDoesNotExist:
			return Response({"message":"UserDetail ObjectDoesNotExist"})
		return Response(response.values(),status=status.HTTP_200_OK)

class UgPgMatchesView(APIView):
	def get(self, request):
		response = {}
		user_id = request.GET.get('user_id')
		under_graduation_name = request.GET.get('ug_name')
		post_graduation_name = request.GET.get('pg_name')
		ug = request.GET.get('ug')
		pg = request.GET.get('pg')
		lc = request.GET.get('lc')
		location_based = request.GET.get('location')
		try:
			main_user = UserBasicDetails.objects.get(user__id = user_id)
			main_user_full = UserFullDetails.objects.get(basic_details__id=main_user.id)
			if ug == 'under_graduation':
				user_full_obj = UserFullDetails.objects.all().order_by('under_graduation')
			elif pg == 'post_graduation':
				user_full_obj = UserFullDetails.objects.all().order_by('post_graduation')
			elif under_graduation_name:
				user_full_obj = UserFullDetails.objects.filter(under_graduation=under_graduation_name)
			elif post_graduation_name:
				user_full_obj = UserFullDetails.objects.filter(post_graduation=post_graduation_name)
			elif lc == 'location':
				user_full_obj = UserFullDetails.objects.filter(state=main_user_full.state)
			elif location_based:	
				user_full_obj = UserFullDetails.objects.filter(city=location_based)
			else:
				user_full_obj = UserFullDetails.objects.all()
			for dt in user_full_obj:
				if main_user.user.id != dt.basic_details.user.id and  main_user_full.gender != dt.gender:
					user_basic_obj = UserBasicDetails.objects.get(user__id = dt.basic_details.user.id)
					serializer1=UserBasicDetailsSerialzers(user_basic_obj, many=False)
					response[int(dt.id)] = serializer1.data
					user_full = UserFullDetails.objects.get(basic_details__id=user_basic_obj.id)
					serializer2=UserFullDetailsSerialzers(user_full, many=False)
					response[int(dt.id)].update({"age":calculate_age(dt.dateofbirth)})
					response[int(dt.id)].update(serializer2.data)
					try:
						liked_obj = LikedStatus.objects.get(user__id=user_id, user_liked = dt.basic_details.user.id)
						response[int(dt.id)].update({"LikedStatus":liked_obj.LikedStatus})
					except Exception as e:
						response[int(dt.id)].update({"LikedStatus":False})					
		except ObjectDoesNotExist:
			return Response({"message":"UserDetail ObjectDoesNotExist"})
		return Response(response.values(),status=status.HTTP_200_OK)


class PPMatchingView(APIView):
	def get(self, request):
		main_user_id = request.GET.get('user_id')
		partner_user_id = request.GET.get('partner_user_id')
		response = {}
		main_user = UserFullDetails.objects.filter(basic_details__user__id=main_user_id).values()
		partner_user = Partner_Preferences.objects.filter(basic_details__user__id=partner_user_id).values()
		for index , keys in enumerate(partner_user):
			age = [{'age': True} if calculate_age(main_user[0]['dateofbirth']) in range(int(keys['min_age']),int(keys['max_age'])) else {'age': False}]
			age.append({'height': True} if height_replaced(main_user[0]['height']) in height_range(min_height_replaced(keys['min_height']),max_height_replaced(keys['max_height'])) else {'height': False})
			del keys['basic_details_id'], keys['id'],keys['min_age'],keys['max_age'],keys['min_height'],keys['max_height']
			user_full_details = dict(ChainMap(*[{k : True} if partner_user[0][k] == main_user[0][k] else {k:False} for k,v in keys.items()]))
		details = user_full_details
		age_height = dict(ChainMap(*age))
		response.update(details)
		response.update(age_height)
		total = len(response)
		true_total = len([j for i, j in response.items() if j == True])
		percentage = true_total / total *100
		response.update({"matching_percentage":int(percentage)})
		return Response(response,status=status.HTTP_200_OK)

class MatchesCountView(APIView):
	def get(self, request):
		response = {}
		main_user_id = request.GET.get('user_id')
		user_basic_obj = UserBasicDetails.objects.get(user__id = main_user_id)
		user_full_obj = UserFullDetails.objects.get(basic_details__id=user_basic_obj.id)
		if user_full_obj.gender == 'Male':
			response['caste'] = {'caste_count':int(UserFullDetails.objects.filter(gender='Female',caste=user_full_obj.caste).count()),
								'caste_text':'caste'}
			response['profession'] = {'profession_count':int(UserFullDetails.objects.filter(gender='Female',occupation=user_full_obj.occupation).count()),
										'profession_text':'profession'}
			response['horoscope'] = {'horoscope_count':int(UserFullDetails.objects.filter(gender='Female',rashi=user_full_obj.rashi).count()),
									'horoscope_text':'horoscope'}
			response['under_graduation'] = {'under_graduation_count':int(UserFullDetails.objects.filter(gender='Female').order_by('under_graduation').count()),
											'under_graduation_text':'under_graduation'}
			response['post_graduation'] = {'post_graduation_count':int(UserFullDetails.objects.filter(gender='Female').order_by('post_graduation').count()),
											'post_graduation_text':'post_graduation'}
			response['location'] = {'location_count':int(UserFullDetails.objects.filter(gender='Female',state=user_full_obj.state).count()),
									'location_text':'location'}
		else:
			response['caste'] = {'caste_count':int(UserFullDetails.objects.filter(gender='Male',caste=user_full_obj.caste).count()),
								'caste_text':'caste'}
			response['profession'] = {'profession_count':int(UserFullDetails.objects.filter(gender='Male',occupation=user_full_obj.occupation).count()),
										'profession_text':'profession'}
			response['horoscope'] = {'horoscope_count':int(UserFullDetails.objects.filter(gender='Male',rashi=user_full_obj.rashi).count()),
									'horoscope_text':'horoscope'}
			response['under_graduation'] = {'under_graduation_count':int(UserFullDetails.objects.filter(gender='Male').order_by('under_graduation').count()),
											'under_graduation_text':'under_graduation'}
			response['post_graduation'] = {'post_graduation_count':int(UserFullDetails.objects.filter(gender='Male').order_by('post_graduation').count()),
											'post_graduation_text':'post_graduation'}
			response['location'] = {'location_count':int(UserFullDetails.objects.filter(gender='Male',state=user_full_obj.state).count()),
									'location_text':'location'}
		return Response(response.values(),status=status.HTTP_200_OK)

class MatchesByCatView(APIView):
	def get(self, request):
		response = {}
		user_id = request.GET.get('user_id')
		caste = request.GET.get('caste')
		horoscope = request.GET.get('horoscope')
		profession = request.GET.get('profession')
		subcaste = request.GET.get('subcaste_name')
		try:
			main_user = UserBasicDetails.objects.get(user__id = user_id)
			main_user_full = UserFullDetails.objects.get(basic_details__id=main_user.id)

			if caste == 'caste':
				user_full_obj = UserFullDetails.objects.filter(caste=main_user_full.caste)
			elif subcaste:
				user_full_obj = UserFullDetails.objects.filter(caste=main_user_full.caste,sub_caste=main_user_full.sub_caste)
			elif horoscope == 'horoscope':
				user_full_obj = UserFullDetails.objects.filter(rashi=main_user_full.rashi)
			elif profession == 'profession':
				user_full_obj = UserFullDetails.objects.filter(occupation=main_user_full.occupation)
			for dt in user_full_obj:
				if main_user.user.id != dt.basic_details.user.id and  main_user_full.gender != dt.gender:
					user_basic_obj = UserBasicDetails.objects.get(user__id = dt.basic_details.user.id)
					serializer1=UserBasicDetailsSerialzers(user_basic_obj, many=False)
					response[int(dt.id)] = serializer1.data
					user_full = UserFullDetails.objects.get(basic_details__id=user_basic_obj.id)
					serializer2=UserFullDetailsSerialzers(user_full, many=False)
					response[int(dt.id)].update({"age":calculate_age(dt.dateofbirth)})
					response[int(dt.id)].update(serializer2.data)
					try:
						liked_obj = LikedStatus.objects.get(user__id=user_id, user_liked = dt.basic_details.user.id)
						response[int(dt.id)].update({"LikedStatus":liked_obj.LikedStatus})
					except Exception as e:
						response[int(dt.id)].update({"LikedStatus":False})					
		except ObjectDoesNotExist:
			return Response({"message":"UserDetail ObjectDoesNotExist"})
		return Response(response.values(),status=status.HTTP_200_OK)

class DailyRecoView(APIView):
	def get(self, request):
		response = {}
		user_id = request.GET.get('user_id')
		try:
			user_qs	= User.objects.all().order_by('-id')
			main_obj = UserFullDetails.objects.get(basic_details__user__id=user_id)
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
						try:
							liked_obj = LikedStatus.objects.get(user__id=user_id,user_liked =int(dt.id))
							response[dt.id].update({"LikedStatus":liked_obj.LikedStatus})
						except Exception as e:
							response[dt.id].update({"LikedStatus":False})
		except  Exception as e:
			print(e)
			return Response({"message":"UserDetail ObjectDoesNotExist"})
		values = list(response.values())
		random.shuffle(values)
		res = dict(zip(response, values))
		return Response(res.values(),status=status.HTTP_200_OK)