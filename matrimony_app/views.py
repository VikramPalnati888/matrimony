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
from django.conf import settings

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

# def timeDiff(time1):
#     timeA = datetime.strptime(time1, "%H:%M")
#     timeB = datetime.strptime(datetime.now().strftime("%H:%M:%S"), "%H:%M")
#     newTime = timeA - timeB
#     return newTime.seconds/60 

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
		main_user_id = request.GET.get('userId')
		another_user_id = request.GET.get('another_user_id')
		try:
			if userId:
				user_basic_obj = UserBasicDetails.objects.get(user__id = userId)
				user_qs = UserFullDetails.objects.get(basic_details__id=user_basic_obj.id)
			else:	
				user_basic_obj = UserBasicDetails.objects.get(user__id = another_user_id)
				user_qs = UserFullDetails.objects.get(basic_details__id=user_basic_obj.id)
		except Exception as e:
			return Response({"message":str(e)})

		serializer1=UserBasicDetailsSerialzers(user_basic_obj,many=False)
		response[main_user_id] = serializer1.data
		serializer2=UserFullDetailsSerialzers(user_qs,many=False)
		response[main_user_id].update({"age":calculate_age(user_qs.dateofbirth)})
		response[main_user_id].update(serializer2.data)
		try:
			if userId:
				liked_obj = LikedStatus.objects.get(user__id = main_user_id,user_liked=another_user_id)
				response[main_user_id].update({"LikedStatus":liked_obj.LikedStatus})
			else:
				liked_obj = LikedStatus.objects.get(user__id = main_user_id,user_liked=another_user_id)
				response[main_user_id].update({"LikedStatus":liked_obj.LikedStatus})
		except Exception as e:
			response[main_user_id].update({"LikedStatus":False})
		try:
			req_status = FriendRequests.objects.get(user__id=main_user_id,requested_user_id=another_user_id)
			response[main_user_id].update({"requested_user_id":req_status.requested_user_id,
										"created_at":req_status.created_at,
										"created_time":req_status.created_time,
										"request_status":req_status.request_status,
										"updated_at":req_status.updated_at,
										"updated_time":req_status.updated_time,
										"status":req_status.status,
										"Req_status":req_status.status})
		except Exception as e:
			response[main_user_id].update({"Req_status":False})
		visible_obj = VisibleDataRequest.objects.filter(main_user_id=main_user_id,visible_user_id=another_user_id)
		res = {}
		if visible_obj:
			for visible_dt in visible_obj:
				try:
					visible_food = VisibleDataRequest.objects.get(main_user_id=main_user_id,visible_user_id=another_user_id,key_name='food')
					response[main_user_id].update({"food_status":True})
				except:
					response[main_user_id].update({"food_status":False})
									
				try:
					visible_smoke = VisibleDataRequest.objects.get(main_user_id=main_user_id,visible_user_id=another_user_id,key_name='smoke')
					response[main_user_id].update({"smoke_status":True})
				except:
					response[main_user_id].update({"smoke_status":False})
				try:
					visible_drink = VisibleDataRequest.objects.get(main_user_id=main_user_id,visible_user_id=another_user_id,key_name='drink')
					response[main_user_id].update({"drink_status":True})
				except:
					response[main_user_id].update({"drink_status":False})

				try:
					visible_phone = VisibleDataRequest.objects.get(main_user_id=main_user_id,visible_user_id=another_user_id,key_name='phone')
					response[main_user_id].update({"phone_status":True})
				except:
					response[main_user_id].update({"phone_status":False})
				res[visible_dt.key_name] = {"key_name": visible_dt.key_name,
										"visible_status": visible_dt.visible_status}

			response[main_user_id].update({"visible_data":res.values()})
		else:
			response[main_user_id].update({"food_status":False})
			response[main_user_id].update({"smoke_status":False})
			response[main_user_id].update({"drink_status":False})
			response[main_user_id].update({"phone_status":False})
			response[main_user_id].update({"visible_data": [{
															"visible_status":"Pending",
															'key_name':None
															}]
										})
		return Response(response.values(),status=status.HTTP_200_OK)

	def post(self, request):
		if not request.POST._mutable:
			request.POST._mutable = True
		user_id = request.GET.get('user_id')
		data = ast.literal_eval(request.data['registerdata'])
		try:
			user_basic_obj = UserBasicDetails.objects.get(user__id = user_id)
			userFull_details = UserFullDetails.objects.get(basic_details=user_basic_obj)
			data['image'] = request.FILES.get('image')
			data['basic_details'] = int(user_basic_obj.id)
			if data['image'] == None:
				del data['image']
				serializer = UserFullDetailsSerialzers(userFull_details,data = data, partial=True)
			else:
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
		data = ast.literal_eval(request.data['registerdata'])
		data['image'] = request.FILES.get('image')
		user_id = request.GET.get('user_id')
		user_obj = UserBasicDetails.objects.get(user__id = user_id)
		try:
			if data['image'] == None:
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
					"College":[coll.college for coll in College.objects.all()],
					"Weight":[weight.weight for weight in Weight.objects.all()],
					}
		return Response(response, status=status.HTTP_200_OK)

class CountryList(APIView):
	def get(self,request):
		queryset = Country.objects.all()
		response=CountrySerializer(queryset,many=True)
		return Response(response.data, status=status.HTTP_200_OK)

class StatesList(APIView):
	def get(self,request):
		country_id = request.GET.get('country_id')
		country_name = request.GET.get('country_name')
		if country_id:
			queryset = State.objects.filter(country__id=country_id)
		else:
			queryset = State.objects.filter(country__country=country_name)
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


class CollegeView(APIView):
	def post(self, request):
		data = request.data
		serializer = CollegeSerializer(data = data)
		if serializer.is_valid(): 
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class WeightView(APIView):
	def post(self, request):
		data = request.data
		serializer = WeightSerializer(data = data)
		if serializer.is_valid(): 
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# main Funcationality start from here

class NewMatches(APIView):
	def get(self, request):
		response = {}
		user_id = request.GET.get('user_id')
		user_qs	= User.objects.all().order_by('-id')
		try:
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
						try:
							req_status = FriendRequests.objects.get(user__id=user_id,requested_user_id=int(dt.id))
							response[dt.id].update({"Req_status":req_status.status})
						except Exception as e:
							response[dt.id].update({"Req_status":False})
						visible_obj = VisibleDataRequest.objects.filter(main_user_id=dt.id,visible_user_id=user_id)
						res = {}
						if visible_obj:
							for visible_dt in visible_obj:
								try:
									visible_food = VisibleDataRequest.objects.get(main_user_id=dt.id,visible_user_id=user_id,key_name='food')
									response[dt.id].update({"food_status":True})
								except:
									response[dt.id].update({"food_status":False})
													
								try:
									visible_smoke = VisibleDataRequest.objects.get(main_user_id=dt.id,visible_user_id=user_id,key_name='smoke')
									response[dt.id].update({"smoke_status":True})
								except:
									response[dt.id].update({"smoke_status":False})
								try:
									visible_drink = VisibleDataRequest.objects.get(main_user_id=dt.id,visible_user_id=user_id,key_name='drink')
									response[dt.id].update({"drink_status":True})
								except:
									response[dt.id].update({"drink_status":False})
								
								try:
									visible_phone = VisibleDataRequest.objects.get(main_user_id=dt.id,visible_user_id=user_id,key_name='phone')
									response[dt.id].update({"phone_status":True})
								except:
									response[dt.id].update({"phone_status":False})
								res[visible_dt.key_name] = {"key_name": visible_dt.key_name,
														"visible_status": visible_dt.visible_status}

							response[dt.id].update({"visible_data":res.values()})
						else:
							response[dt.id].update({"food_status":False})
							response[dt.id].update({"smoke_status":False})
							response[dt.id].update({"drink_status":False})
							response[dt.id].update({"phone_status":False})
							response[int(dt.id)].update({"visible_data": [{
																			"visible_status":"Pending",
																			'key_name':None
																			}]})
		except  Exception as e:
			print(e)
			if str(e) == "UserFullDetails matching query does not exist.":
				dl_user = User.objects.get(id=dt.id)
				dl_user.delete()
				print("delete Successful")
			return Response({"message":str(e)})
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
			return Response({"message":str(e)})
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
				
				viewed_details_obj = Viewed_matches.objects.get(user__id=user_id,viewed_user_id = int(viewed_data.viewed_user_id))
				serializer3=ViewdDetailsSerialzers(viewed_details_obj,many=False)
				response[user_full_obj.basic_details.user.id].update({'viewd_status':viewed_data.viewd_status})
				try:
					liked_obj = LikedStatus.objects.get(user__id=user_id,user_liked = viewed_data.viewed_user_id)
					response[user_full_obj.basic_details.user.id].update({"LikedStatus":liked_obj.LikedStatus})
				except Exception as e:
					print(e)
					response[user_full_obj.basic_details.user.id].update({"LikedStatus":False})
				try:
					req_status = FriendRequests.objects.get(user__id=user_id,requested_user_id=viewed_data.viewed_user_id)
					response[user_full_obj.basic_details.user.id].update({"Req_status":req_status.status})
				except Exception as e:
					response[user_full_obj.basic_details.user.id].update({"Req_status":False})
				visible_obj = VisibleDataRequest.objects.filter(main_user_id=user_id,visible_user_id=viewed_data.viewed_user_id)
				res = {}
				if visible_obj:
					try:
						visible_food = VisibleDataRequest.objects.get(main_user_id=user_id,visible_user_id=viewed_data.viewed_user_id,key_name='food')
						response[user_full_obj.basic_details.user.id].update({"food_status":True})
					except:
						response[user_full_obj.basic_details.user.id].update({"food_status":False})
										
					try:
						visible_smoke = VisibleDataRequest.objects.get(main_user_id=user_id,visible_user_id=viewed_data.viewed_user_id,key_name='smoke')
						response[user_full_obj.basic_details.user.id].update({"smoke_status":True})
					except:
						response[user_full_obj.basic_details.user.id].update({"smoke_status":False})
					try:
						visible_drink = VisibleDataRequest.objects.get(main_user_id=user_id,visible_user_id=viewed_data.viewed_user_id,key_name='drink')
						response[user_full_obj.basic_details.user.id].update({"drink_status":True})
					except:
						response[user_full_obj.basic_details.user.id].update({"drink_status":False})
					
					try:
						visible_phone = VisibleDataRequest.objects.get(main_user_id=user_id,visible_user_id=viewed_data.viewed_user_id,key_name='phone')
						response[user_full_obj.basic_details.user.id].update({"phone_status":True})
					except:
						response[user_full_obj.basic_details.user.id].update({"phone_status":False})
					for visible_dt in visible_obj:
						res[visible_dt.key_name] = {"key_name": visible_dt.key_name,
												"visible_status": visible_dt.visible_status}

					response[user_full_obj.basic_details.user.id].update({"visible_data":res.values()})
				else:
					response[user_full_obj.basic_details.user.id].update({"food_status":False})
					response[user_full_obj.basic_details.user.id].update({"smoke_status":False})
					response[user_full_obj.basic_details.user.id].update({"drink_status":False})
					response[user_full_obj.basic_details.user.id].update({"phone_status":False})
					response[user_full_obj.basic_details.user.id].update({"visible_data": [{
																	"visible_status":"Pending",
																	'key_name':None
																	}]
												})
		except  Exception as e:
			return Response({"message":str(e)})
		return Response(response.values(),status=status.HTTP_200_OK)


class PPView(APIView):
	def get(self, request):
		user_id = request.GET.get('user_id')
		response = {}
		try:
				user_basic_obj = UserBasicDetails.objects.get(user__id = user_id)
				user_pp = Partner_Preferences.objects.get(basic_details__id=user_basic_obj.id)
		except Exception as e:
				return Response({"message":str(e)})
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
			response['message'] = {'message': 'No data found'}
			return Response(response.values(),status=status.HTTP_400_BAD_REQUEST)
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
			print(data['under_graduation'])
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
		except Exception as e:
			return Response({"message":str(e)})
		return Response(response.values(),status=status.HTTP_200_OK)

class UgPgMatchesView(APIView):
	def get(self, request):
		response = {}
		user_id = request.GET.get('user_id')
		under_graduation_name = request.GET.get('ug_name')
		multi_ug_name = request.GET.get('multi_ug_name')
		multi_pg_name = request.GET.get('multi_pg_name')
		post_graduation_name = request.GET.get('pg_name')
		ug = request.GET.get('ug')
		pg = request.GET.get('pg')
		lc = request.GET.get('lc')
		location_based = request.GET.get('location')
		multi_location_based = request.GET.get('multi_locations')
		try:
			main_user = UserBasicDetails.objects.get(user__id = user_id)
			main_user_full = UserFullDetails.objects.get(basic_details__id=main_user.id)
			if ug == 'under_graduation':
				user_full_obj = UserFullDetails.objects.filter(post_graduation="None")#.order_by('under_graduation')
			elif pg == 'post_graduation':
				user_full_obj = UserFullDetails.objects.all().order_by('post_graduation')
			elif under_graduation_name:
				user_full_obj = UserFullDetails.objects.filter(under_graduation=under_graduation_name)
			elif multi_ug_name:
				ug_names =  multi_ug_name.split(',')
				user_full_obj = UserFullDetails.objects.filter(under_graduation__in=ug_names)
			elif post_graduation_name:
				user_full_obj = UserFullDetails.objects.filter(post_graduation=post_graduation_name)
			elif multi_pg_name:
				pg_names =  multi_pg_name.split(',')
				user_full_obj = UserFullDetails.objects.filter(post_graduation__in=pg_names)
			elif lc == 'location':
				user_full_obj = UserFullDetails.objects.filter(state=main_user_full.state)
			elif location_based:	
				user_full_obj = UserFullDetails.objects.filter(city=location_based)
			elif multi_location_based:
				locations =  multi_location_based.split(',')
				user_full_obj = UserFullDetails.objects.filter(city__in=locations)
			else:
				user_full_obj = UserFullDetails.objects.all()
			for dt in user_full_obj:
				if main_user.user.id != dt.basic_details.user.id and  main_user_full.gender != dt.gender:
					user_basic_obj = UserBasicDetails.objects.get(user__id = dt.basic_details.user.id)

					user_full = UserFullDetails.objects.get(basic_details__id=user_basic_obj.id)
					if pg:
						if user_full.post_graduation != 'None':
							print("entered if")
							serializer1=UserBasicDetailsSerialzers(user_basic_obj, many=False)
							response[int(dt.id)] = serializer1.data
							serializer2=UserFullDetailsSerialzers(user_full, many=False)
							response[int(dt.id)].update({"age":calculate_age(dt.dateofbirth)})
							response[int(dt.id)].update(serializer2.data)
							try:
								liked_obj = LikedStatus.objects.get(user__id=user_id, user_liked = dt.basic_details.user.id)
								response[int(dt.id)].update({"LikedStatus":liked_obj.LikedStatus})
							except Exception as e:
								response[int(dt.id)].update({"LikedStatus":False})
							try:
								req_status = FriendRequests.objects.get(user__id=user_id,requested_user_id=dt.basic_details.user.id)
								response[int(dt.id)].update({"Req_status":req_status.status})
							except Exception as e:
								response[int(dt.id)].update({"Req_status":False})
							visible_obj = VisibleDataRequest.objects.filter(main_user_id=user_id,visible_user_id=dt.basic_details.user.id)
							res = {}
							if visible_obj:
								for visible_dt in visible_obj:
									try:
										visible_food = VisibleDataRequest.objects.get(main_user_id=user_id,visible_user_id=dt.basic_details.user.id,key_name='food')
										response[int(dt.id)].update({"food_status":True})
									except:
										response[int(dt.id)].update({"food_status":False})
														
									try:
										visible_smoke = VisibleDataRequest.objects.get(main_user_id=user_id,visible_user_id=dt.basic_details.user.id,key_name='smoke')
										response[int(dt.id)].update({"smoke_status":True})
									except:
										response[int(dt.id)].update({"smoke_status":False})
									try:
										visible_drink = VisibleDataRequest.objects.get(main_user_id=user_id,visible_user_id=dt.basic_details.user.id,key_name='drink')
										response[int(dt.id)].update({"drink_status":True})
									except:
										response[int(dt.id)].update({"drink_status":False})

									try:
										visible_phone = VisibleDataRequest.objects.get(main_user_id=user_id,visible_user_id=dt.basic_details.user.id,key_name='phone')
										response[int(dt.id)].update({"phone_status":True})
									except:
										response[int(dt.id)].update({"phone_status":False})
									res[visible_dt.key_name] = {"key_name": visible_dt.key_name,
															"visible_status": visible_dt.visible_status}

								response[int(dt.id)].update({"visible_data":res.values()})
							else:
								response[int(dt.id)].update({"food_status":False})
								response[int(dt.id)].update({"smoke_status":False})
								response[int(dt.id)].update({"drink_status":False})
								response[int(dt.id)].update({"phone_status":False})
								response[int(dt.id)].update({"visible_data": [{
																				"visible_status":"Pending",
																				'key_name':None
																				}]
															})	
					else:
						print("entered else")
						serializer1=UserBasicDetailsSerialzers(user_basic_obj, many=False)
						response[int(dt.id)] = serializer1.data
						serializer2=UserFullDetailsSerialzers(user_full, many=False)
						response[int(dt.id)].update({"age":calculate_age(dt.dateofbirth)})
						response[int(dt.id)].update(serializer2.data)
						try:
							liked_obj = LikedStatus.objects.get(user__id=user_id, user_liked = dt.basic_details.user.id)
							response[int(dt.id)].update({"LikedStatus":liked_obj.LikedStatus})
						except Exception as e:
							response[int(dt.id)].update({"LikedStatus":False})
						try:
							req_status = FriendRequests.objects.get(user__id=user_id,requested_user_id=dt.basic_details.user.id)
							response[int(dt.id)].update({"Req_status":req_status.status})
						except Exception as e:
							response[int(dt.id)].update({"Req_status":False})
						visible_obj = VisibleDataRequest.objects.filter(main_user_id=user_id,visible_user_id=dt.basic_details.user.id)
						res = {}
						if visible_obj:
							for visible_dt in visible_obj:
								try:
									visible_food = VisibleDataRequest.objects.get(main_user_id=user_id,visible_user_id=dt.basic_details.user.id,key_name='food')
									response[int(dt.id)].update({"food_status":True})
								except:
									response[int(dt.id)].update({"food_status":False})
													
								try:
									visible_smoke = VisibleDataRequest.objects.get(main_user_id=user_id,visible_user_id=dt.basic_details.user.id,key_name='smoke')
									response[int(dt.id)].update({"smoke_status":True})
								except:
									response[int(dt.id)].update({"smoke_status":False})
								try:
									visible_drink = VisibleDataRequest.objects.get(main_user_id=user_id,visible_user_id=dt.basic_details.user.id,key_name='drink')
									response[int(dt.id)].update({"drink_status":True})
								except:
									response[int(dt.id)].update({"drink_status":False})

								try:
									visible_phone = VisibleDataRequest.objects.get(main_user_id=user_id,visible_user_id=dt.basic_details.user.id,key_name='phone')
									response[int(dt.id)].update({"phone_status":True})
								except:
									response[int(dt.id)].update({"phone_status":False})
								res[visible_dt.key_name] = {"key_name": visible_dt.key_name,
														"visible_status": visible_dt.visible_status}

							response[int(dt.id)].update({"visible_data":res.values()})
						else:
							response[int(dt.id)].update({"food_status":False})
							response[int(dt.id)].update({"smoke_status":False})
							response[int(dt.id)].update({"drink_status":False})
							response[int(dt.id)].update({"phone_status":False})
							response[int(dt.id)].update({"visible_data": [{
																			"visible_status":"Pending",
																			'key_name':None
																			}]
														})		
		except Exception as e:
			return Response({"message":str(e)})
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
			response['caste'] = {
								'count':int(UserFullDetails.objects.filter(gender='Female',caste=user_full_obj.caste).count()),
								'name':'caste'
								}
			response['profession'] = {
										'count':int(UserFullDetails.objects.filter(gender='Female',occupation=user_full_obj.occupation).count()),
										'name':'profession'
									}
			response['horoscope'] = {
									'count':int(UserFullDetails.objects.filter(gender='Female',rashi=user_full_obj.rashi).count()),
									'name':'horoscope'
									}
			response['under_graduation'] = {
											'count':int(UserFullDetails.objects.filter(gender='Female').order_by('under_graduation').count()),
											'name':'under graduation'
											}
			response['post_graduation'] = {
											'count':int(UserFullDetails.objects.filter(gender='Female').order_by('post_graduation').count()),
											'name':'post graduation'
										}
			response['location'] = {
									'count':int(UserFullDetails.objects.filter(gender='Female',state=user_full_obj.state).count()),
									'name':'location'
									}
		else:
			response['caste'] = {
								'count':int(UserFullDetails.objects.filter(gender='Male',caste=user_full_obj.caste).count()),
								'name':'caste'
								}
			response['profession'] = {
										'count':int(UserFullDetails.objects.filter(gender='Male',occupation=user_full_obj.occupation).count()),
										'name':'profession'
									}
			response['horoscope'] = {
										'count':int(UserFullDetails.objects.filter(gender='Male',rashi=user_full_obj.rashi).count()),
										'name':'horoscope'
									}
			response['under_graduation'] = {
											'count':int(UserFullDetails.objects.filter(gender='Male').order_by('under_graduation').count()),
											'name':'under graduation'
											}
			response['post_graduation'] = {
											'count':int(UserFullDetails.objects.filter(gender='Male').order_by('post_graduation').count()),
											'name':'post graduation'
											}
			response['location'] = {
									'count':int(UserFullDetails.objects.filter(gender='Male',state=user_full_obj.state).count()),
									'name':'location'
									}
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
					try:
						req_status = FriendRequests.objects.get(user__id=user_id,requested_user_id=dt.basic_details.user.id)
						response[int(dt.id)].update({"Req_status":req_status.status})
					except Exception as e:
						response[int(dt.id)].update({"Req_status":False})
					visible_obj = VisibleDataRequest.objects.filter(main_user_id=user_id,visible_user_id=dt.basic_details.user.id)
					res = {}
					if visible_obj:
						for visible_dt in visible_obj:
							try:
								visible_food = VisibleDataRequest.objects.get(main_user_id=user_id,visible_user_id=dt.basic_details.user.id,key_name='food')
								response[int(dt.id)].update({"food_status":True})
							except:
								response[int(dt.id)].update({"food_status":False})
												
							try:
								visible_smoke = VisibleDataRequest.objects.get(main_user_id=user_id,visible_user_id=dt.basic_details.user.id,key_name='smoke')
								response[int(dt.id)].update({"smoke_status":True})
							except:
								response[int(dt.id)].update({"smoke_status":False})
							try:
								visible_drink = VisibleDataRequest.objects.get(main_user_id=user_id,visible_user_id=dt.basic_details.user.id,key_name='drink')
								response[int(dt.id)].update({"drink_status":True})
							except:
								response[int(dt.id)].update({"drink_status":False})

							try:
								visible_phone = VisibleDataRequest.objects.get(main_user_id=user_id,visible_user_id=dt.basic_details.user.id,key_name='phone')
								response[int(dt.id)].update({"phone_status":True})
							except:
								response[int(dt.id)].update({"phone_status":False})
							res[visible_dt.key_name] = {"key_name": visible_dt.key_name,
													"visible_status": visible_dt.visible_status}

						response[int(dt.id)].update({"visible_data":res.values()})
					else:
						response[int(dt.id)].update({"food_status":False})
						response[int(dt.id)].update({"smoke_status":False})
						response[int(dt.id)].update({"drink_status":False})
						response[int(dt.id)].update({"phone_status":False})
						response[int(dt.id)].update({"visible_data": [{
																		"visible_status":"Pending",
																		'key_name':None
																		}]
													})		
		except Exception as e:
			return Response({"message":str(e)})
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
						try:
							req_status = FriendRequests.objects.get(user__id=user_id,requested_user_id=int(dt.id))
							response[dt.id].update({"Req_status":req_status.status})
						except Exception as e:
							response[dt.id].update({"Req_status":False})
						visible_obj = VisibleDataRequest.objects.filter(main_user_id=user_id,visible_user_id=dt.id)
						res = {}
						if visible_obj:
							for visible_dt in visible_obj:
								try:
									visible_food = VisibleDataRequest.objects.get(main_user_id=user_id,visible_user_id=dt.id,key_name='food')
									response[dt.id].update({"food_status":True})
								except:
									response[dt.id].update({"food_status":False})
													
								try:
									visible_smoke = VisibleDataRequest.objects.get(main_user_id=user_id,visible_user_id=dt.id,key_name='smoke')
									response[dt.id].update({"smoke_status":True})
								except:
									response[dt.id].update({"smoke_status":False})
								try:
									visible_drink = VisibleDataRequest.objects.get(main_user_id=user_id,visible_user_id=dt.id,key_name='drink')
									response[dt.id].update({"drink_status":True})
								except:
									response[dt.id].update({"drink_status":False})

								try:
									visible_phone = VisibleDataRequest.objects.get(main_user_id=user_id,visible_user_id=dt.id,key_name='phone')
									response[dt.id].update({"phone_status":True})
								except:
									response[dt.id].update({"phone_status":False})
								res[visible_dt.key_name] = {"key_name": visible_dt.key_name,
														"visible_status": visible_dt.visible_status}

							response[dt.id].update({"visible_data":res.values()})
						else:
							response[dt.id].update({"food_status":False})
							response[dt.id].update({"smoke_status":False})
							response[dt.id].update({"drink_status":False})
							response[dt.id].update({"phone_status":False})
							response[dt.id].update({"visible_data": [{
																			"visible_status":"Pending",
																			'key_name':None
																			}]
														})
		except  Exception as e:
			if str(e) == "UserFullDetails matching query does not exist.":
				dl_user = User.objects.get(id=dt.id)
				dl_user.delete()
				print("delete Successful")
			response['message'] = {'message': str(e)}
			return Response(response.values(),status=status.HTTP_400_BAD_REQUEST)
		values = list(response.values())
		random.shuffle(values)
		res = dict(zip(response, values))
		return Response(res.values(),status=status.HTTP_200_OK)


class RequestsView(APIView):
	def get(self, request):
		user_id = request.GET.get('user_id')
		response = {}
		try:
			req = FriendRequests.objects.filter(requested_user_id=user_id, request_status='Pending')
			for data in req:
				user_basic_obj = UserBasicDetails.objects.get(user__id = data.user.id)
				serializer1=UserBasicDetailsSerialzers(user_basic_obj, many=False)
				response[data.id] = serializer1.data
				user_full = UserFullDetails.objects.get(basic_details__id=user_basic_obj.id)
				serializer2=UserFullDetailsSerialzers(user_full, many=False)
				response[data.id].update({"age":calculate_age(user_full.dateofbirth)})
				response[data.id].update(serializer2.data)
				req_data = FriendRequests.objects.get(user__id = data.user.id,requested_user_id=user_id)
				# response[data.id].update({"past_time":timeDiff(user_full.dateofbirth)})
				serializer3=FriendRequestsSerializer(req_data,many=False)
				response[data.id].update(serializer3.data)
				try:
					liked_obj = LikedStatus.objects.get(user__id=user_id,user_liked =data.id)
					response[data.id].update({"LikedStatus":liked_obj.LikedStatus})
				except Exception as e:
					response[data.id].update({"LikedStatus":False})
				try:
					req_status = FriendRequests.objects.get(user__id=user_id,requested_user_id=data.id)
					response[data.id].update({"Req_status":req_status.status})
				except Exception as e:
					response[data.id].update({"Req_status":False})
				visible_obj = VisibleDataRequest.objects.filter(main_user_id=user_id,visible_user_id=data.id)
				res = {}
				if visible_obj:
					for visible_dt in visible_obj:
						try:
							visible_food = VisibleDataRequest.objects.get(main_user_id=user_id,visible_user_id=data.id,key_name='food')
							response[data.id].update({"food_status":True})
						except:
							response[data.id].update({"food_status":False})
											
						try:
							visible_smoke = VisibleDataRequest.objects.get(main_user_id=user_id,visible_user_id=data.id,key_name='smoke')
							response[data.id].update({"smoke_status":True})
						except:
							response[data.id].update({"smoke_status":False})
						try:
							visible_drink = VisibleDataRequest.objects.get(main_user_id=user_id,visible_user_id=data.id,key_name='drink')
							response[data.id].update({"drink_status":True})
						except:
							response[data.id].update({"drink_status":False})

						try:
							visible_phone = VisibleDataRequest.objects.get(main_user_id=user_id,visible_user_id=data.id,key_name='phone')
							response[data.id].update({"phone_status":True})
						except:
							response[data.id].update({"phone_status":False})
						res[visible_dt.key_name] = {"key_name": visible_dt.key_name,
												"visible_status": visible_dt.visible_status}

					response[data.id].update({"visible_data":res.values()})
				else:
					response[data.id].update({"visible_data": [{
																	"visible_status":"Pending",
																	'key_name':None
																	}]
												})
		except Exception as e:
			response['message'] = {'message': str(e)}
			return Response(response.values(),status=status.HTTP_400_BAD_REQUEST)
		return Response(response.values(),status=status.HTTP_200_OK)

	def post(self, request):
		if not request.POST._mutable:
			request.POST._mutable = True
		data = request.data
		response = {}
		user_id = request.GET.get('user_id')
		data['user'] = user_id
		data['created_at'] = date.today()
		data['updated_at'] = date.today()
		data['created_time'] = datetime.now().strftime("%H:%M:%S")
		data['updated_time'] = datetime.now().strftime("%H:%M:%S")
		data['request_status'] = "Pending"
		try:
			user_pp = FriendRequests.objects.get(user__id=user_id,requested_user_id=data['requested_user_id'])
			serializer2=FriendRequestsSerializer(user_pp,many=False)
			response.update(serializer2.data)
			return Response(response,status=status.HTTP_200_OK)
		except Exception as e:
			serializer = FriendRequestsSerializer(data = data)
			if serializer.is_valid(): 
				serializer.save()
				return Response(serializer.data, status=status.HTTP_201_CREATED)
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
	
	def put(self, request):
		if not request.POST._mutable:
			request.POST._mutable = True
		response = {}
		data = request.data
		accepted_user_id = request.GET.get('accepted_user_id')
		data['updated_at'] = date.today()
		data['updated_time'] = datetime.now().strftime("%H:%M:%S")
		queryset = FriendRequests.objects.get(user__id=data['user_id'],requested_user_id=accepted_user_id)
		print(queryset)
		req_serializer = FriendRequestsSerializer(queryset, data=data, partial=True)
		if req_serializer.is_valid():
			req_serializer.save()
			return Response(req_serializer.data,status=status.HTTP_200_OK)
		return Response(req_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InterestedView(APIView):
	def get(self, request):
		user_id = request.GET.get('user_id')
		response = {}
		try:
			req = FriendRequests.objects.filter(user__id=user_id)
			print(req)
			for data in req:
				user_basic_obj = UserBasicDetails.objects.get(user__id = int(data.requested_user_id))
				serializer1=UserBasicDetailsSerialzers(user_basic_obj, many=False)
				response[data.id] = serializer1.data
				user_full = UserFullDetails.objects.get(basic_details__id=user_basic_obj.id)
				serializer2=UserFullDetailsSerialzers(user_full, many=False)
				response[data.id].update({"age":calculate_age(user_full.dateofbirth)})
				response[data.id].update(serializer2.data)
				try:
					liked_obj = LikedStatus.objects.get(user__id=user_id,user_liked =data.requested_user_id)
					response[data.id].update({"LikedStatus":liked_obj.LikedStatus})
				except Exception as e:
					response[data.id].update({"LikedStatus":False})
				try:
					req_status = FriendRequests.objects.get(user__id=user_id,requested_user_id=data.requested_user_id)
					response[data.id].update({"Req_status":req_status.status})
				except Exception as e:
					response[data.id].update({"Req_status":False})
				visible_obj = VisibleDataRequest.objects.filter(main_user_id=user_id,visible_user_id=data.requested_user_id)
				res = {}
				if visible_obj:
					for visible_dt in visible_obj:
						try:
							visible_food = VisibleDataRequest.objects.get(main_user_id=user_id,visible_user_id=data.requested_user_id,key_name='food')
							response[data.id].update({"food_status":True})
						except:
							response[data.id].update({"food_status":False})
											
						try:
							visible_smoke = VisibleDataRequest.objects.get(main_user_id=user_id,visible_user_id=data.requested_user_id,key_name='smoke')
							response[data.id].update({"smoke_status":True})
						except:
							response[data.id].update({"smoke_status":False})
						try:
							visible_drink = VisibleDataRequest.objects.get(main_user_id=user_id,visible_user_id=data.requested_user_id,key_name='drink')
							response[data.id].update({"drink_status":True})
						except:
							response[data.id].update({"drink_status":False})

						try:
							visible_phone = VisibleDataRequest.objects.get(main_user_id=user_id,visible_user_id=data.requested_user_id,key_name='phone')
							response[data.id].update({"phone_status":True})
						except:
							response[data.id].update({"phone_status":False})
						res[visible_dt.key_name] = {"key_name": visible_dt.key_name,
												"visible_status": visible_dt.visible_status}

					response[data.id].update({"visible_data":res.values()})
				else:
					response[data.id].update({"food_status":False})
					response[data.id].update({"smoke_status":False})
					response[data.id].update({"drink_status":False})
					response[data.id].update({"phone_status":False})
					response[data.id].update({"visible_data": [{
																	"visible_status":"Pending",
																	'key_name':None
																	}]
												})
		except Exception as e:
			print(e)
			response['message'] = {'message': str(e)}
			return Response(response.values(),status=status.HTTP_400_BAD_REQUEST)
		return Response(response.values(),status=status.HTTP_200_OK)

class AcceptedView(APIView):
	def get(self, request):
		user_id = request.GET.get('user_id')
		response = {}
		try:
			req = FriendRequests.objects.filter(user__id=user_id,request_status='Approved')
			print(req)
			for data in req:
				user_basic_obj = UserBasicDetails.objects.get(user__id = int(data.requested_user_id))
				serializer1=UserBasicDetailsSerialzers(user_basic_obj, many=False)
				response[data.id] = serializer1.data
				user_full = UserFullDetails.objects.get(basic_details__id=user_basic_obj.id)
				serializer2=UserFullDetailsSerialzers(user_full, many=False)
				response[data.id].update({"age":calculate_age(user_full.dateofbirth)})
				response[data.id].update(serializer2.data)
				req_data = FriendRequests.objects.get(user__id = user_id,requested_user_id= int(data.requested_user_id))
				serializer3=FriendRequestsSerializer(req_data,many=False)
				response[data.id].update(serializer3.data)
				try:
					liked_obj = LikedStatus.objects.get(user__id=user_id,user_liked =data.requested_user_id)
					response[data.id].update({"LikedStatus":liked_obj.LikedStatus})
				except Exception as e:
					response[data.id].update({"LikedStatus":False})
				try:
					req_status = FriendRequests.objects.get(user__id=user_id,requested_user_id=data.requested_user_id)
					response[data.id].update({"Req_status":req_status.status})
				except Exception as e:
					response[data.id].update({"Req_status":False})
				visible_obj = VisibleDataRequest.objects.filter(main_user_id=user_id,visible_user_id=data.requested_user_id)
				res = {}
				if visible_obj:
					for visible_dt in visible_obj:
						try:
							visible_food = VisibleDataRequest.objects.get(main_user_id=user_id,visible_user_id=data.requested_user_id,key_name='food')
							response[data.id].update({"food_status":True})
						except:
							response[data.id].update({"food_status":False})
											
						try:
							visible_smoke = VisibleDataRequest.objects.get(main_user_id=user_id,visible_user_id=data.requested_user_id,key_name='smoke')
							response[data.id].update({"smoke_status":True})
						except:
							response[data.id].update({"smoke_status":False})
						try:
							visible_drink = VisibleDataRequest.objects.get(main_user_id=user_id,visible_user_id=data.requested_user_id,key_name='drink')
							response[data.id].update({"drink_status":True})
						except:
							response[data.id].update({"drink_status":False})

						try:
							visible_phone = VisibleDataRequest.objects.get(main_user_id=user_id,visible_user_id=data.requested_user_id,key_name='phone')
							response[data.id].update({"phone_status":True})
						except:
							response[data.id].update({"phone_status":False})
						res[visible_dt.key_name] = {"key_name": visible_dt.key_name,
												"visible_status": visible_dt.visible_status}

					response[data.id].update({"visible_data":res.values()})
				else:
					response[data.id].update({"food_status":False})
					response[data.id].update({"smoke_status":False})
					response[data.id].update({"drink_status":False})
					response[data.id].update({"phone_status":False})
					response[data.id].update({"visible_data": [{
																	"visible_status":"Pending",
																	'key_name':None
																	}]
												})
		except Exception as e:
			print(e)
			response['message'] = {'message':str(e)}
			return Response(response.values(),status=status.HTTP_400_BAD_REQUEST)
		return Response(response.values(),status=status.HTTP_200_OK)

class RejectedView(APIView):
	def get(self, request):
		user_id = request.GET.get('user_id')
		response = {}
		try:
			req = FriendRequests.objects.filter(user__id=user_id,request_status='Rejected')
			print(req)
			for data in req:
				user_basic_obj = UserBasicDetails.objects.get(user__id = int(data.requested_user_id))
				serializer1=UserBasicDetailsSerialzers(user_basic_obj, many=False)
				response[data.id] = serializer1.data
				user_full = UserFullDetails.objects.get(basic_details__id=user_basic_obj.id)
				serializer2=UserFullDetailsSerialzers(user_full, many=False)
				response[data.id].update({"age":calculate_age(user_full.dateofbirth)})
				response[data.id].update(serializer2.data)
				req_data = FriendRequests.objects.get(user__id = user_id,requested_user_id= int(data.requested_user_id))
				serializer3=FriendRequestsSerializer(req_data,many=False)
				response[data.id].update(serializer3.data)
				try:
					liked_obj = LikedStatus.objects.get(user__id=user_id,user_liked =data.requested_user_id)
					response[data.id].update({"LikedStatus":liked_obj.LikedStatus})
				except Exception as e:
					response[data.id].update({"LikedStatus":False})
				visible_obj = VisibleDataRequest.objects.filter(main_user_id=user_id,visible_user_id=data.requested_user_id)
				res = {}
				if visible_obj:
					for visible_dt in visible_obj:
						try:
							visible_food = VisibleDataRequest.objects.get(main_user_id=user_id,visible_user_id=data.requested_user_id,key_name='food')
							response[data.id].update({"food_status":True})
						except:
							response[data.id].update({"food_status":False})
											
						try:
							visible_smoke = VisibleDataRequest.objects.get(main_user_id=user_id,visible_user_id=data.requested_user_id,key_name='smoke')
							response[data.id].update({"smoke_status":True})
						except:
							response[data.id].update({"smoke_status":False})
						try:
							visible_drink = VisibleDataRequest.objects.get(main_user_id=user_id,visible_user_id=data.requested_user_id,key_name='drink')
							response[data.id].update({"drink_status":True})
						except:
							response[data.id].update({"drink_status":False})

						try:
							visible_phone = VisibleDataRequest.objects.get(main_user_id=user_id,visible_user_id=data.requested_user_id,key_name='phone')
							response[data.id].update({"phone_status":True})
						except:
							response[data.id].update({"phone_status":False})
						res[visible_dt.key_name] = {"key_name": visible_dt.key_name,
												"visible_status": visible_dt.visible_status}

					response[data.id].update({"visible_data":res.values()})
				else:
					response[data.id].update({"food_status":False})
					response[data.id].update({"smoke_status":False})
					response[data.id].update({"drink_status":False})
					response[data.id].update({"phone_status":False})
					response[data.id].update({"visible_data": [{
																	"visible_status":"Pending",
																	'key_name':None
																	}]
												})
		except Exception as e:
			print(e)
			response['message'] = {'message': str(e)}
			return Response(response.values(),status=status.HTTP_400_BAD_REQUEST)
		return Response(response.values(),status=status.HTTP_200_OK)

class ViewdByOthersMatches(APIView):
	def get(self, request):
		response = {}
		user_id = request.GET.get('user_id')
		try:
			viewed_obj = Viewed_matches.objects.filter(viewed_user_id=user_id)
			for viewed_data in viewed_obj:
				user_basic_obj = UserBasicDetails.objects.get(user = int(viewed_data.user.id))
				serializer1=UserBasicDetailsSerialzers(user_basic_obj,many=False)
				response[user_basic_obj.user.id] = serializer1.data
				
				user_full_obj = UserFullDetails.objects.get(basic_details=user_basic_obj)
				serializer2=UserFullDetailsSerialzers(user_full_obj,many=False)
				response[user_full_obj.basic_details.user.id].update({"age":calculate_age(user_full_obj.dateofbirth)})
				response[user_full_obj.basic_details.user.id].update(serializer2.data)
				
				viewed_details_obj = Viewed_matches.objects.get(user__id = int(viewed_data.user.id),viewed_user_id=user_id)
				serializer3=ViewdDetailsSerialzers(viewed_details_obj,many=False)
				response[int(viewed_data.user.id)].update({'viewd_status':viewed_data.viewd_status})
				try:
					liked_obj = LikedStatus.objects.get(user__id=user_id,user_liked = viewed_data.user.id)
					response[int(liked_obj.user_liked)].update({"LikedStatus":liked_obj.LikedStatus})
				except Exception as e:
					print(e)
					response[int(viewed_data.user.id)].update({"LikedStatus":False})
				try:
					req_status = FriendRequests.objects.get(user__id=user_id,requested_user_id=viewed_data.user.id)
					response[int(req_status.requested_user_id)].update({"Req_status":req_status.status})
				except Exception as e:
					response[int(viewed_data.user.id)].update({"Req_status":False})
				visible_obj = VisibleDataRequest.objects.filter(main_user_id=user_id,visible_user_id=viewed_data.user.id)
				res = {}
				if visible_obj:
					for visible_dt in visible_obj:
						try:
							visible_food = VisibleDataRequest.objects.get(main_user_id=user_id,visible_user_id=viewed_data.user.id,key_name='food')
							response[int(viewed_data.user.id)].update({"food_status":True})
						except:
							response[int(viewed_data.user.id)].update({"food_status":False})
											
						try:
							visible_smoke = VisibleDataRequest.objects.get(main_user_id=user_id,visible_user_id=viewed_data.user.id,key_name='smoke')
							response[int(viewed_data.user.id)].update({"smoke_status":True})
						except:
							response[int(viewed_data.user.id)].update({"smoke_status":False})
						try:
							visible_drink = VisibleDataRequest.objects.get(main_user_id=user_id,visible_user_id=viewed_data.user.id,key_name='drink')
							response[int(viewed_data.user.id)].update({"drink_status":True})
						except:
							response[int(viewed_data.user.id)].update({"drink_status":False})

						try:
							visible_phone = VisibleDataRequest.objects.get(main_user_id=user_id,visible_user_id=viewed_data.user.id,key_name='phone')
							response[int(viewed_data.user.id)].update({"phone_status":True})
						except:
							response[int(viewed_data.user.id)].update({"phone_status":False})
						res[visible_dt.key_name] = {"key_name": visible_dt.key_name,
												"visible_status": visible_dt.visible_status}

					response[int(viewed_data.user.id)].update({"visible_data":res.values()})
				else:
					response[int(viewed_data.user.id)].update({"food_status":False})
					response[int(viewed_data.user.id)].update({"smoke_status":False})
					response[int(viewed_data.user.id)].update({"drink_status":False})
					response[int(viewed_data.user.id)].update({"phone_status":False})
					response[int(viewed_data.user.id)].update({"visible_data": [{
																	"visible_status":"Pending",
																	'key_name':None
																	}]
												})
		except  Exception as e:
			print(e)
			return Response({"message":str(e)})
		return Response(response.values(),status=status.HTTP_200_OK)

class MultipleImagesView(APIView):
	def post(self, request):
		user_id = request.GET.get('user_id')
		list_of_images = request.FILES.getlist('multi_images')
		print(list_of_images)
		try:
			user_full_obj = UserFullDetails.objects.get(basic_details__user__id=user_id)
			for file in list_of_images:
				miltiple_images = UserMultiFile.objects.create(basic_details=user_full_obj, files=file)
		except  Exception as e:
			print(e)
			return Response([{"message":str(e)}])
		return Response([{"message":"Images Stored Successful"}],status=status.HTTP_200_OK)


	def get(self, request):
		response = {}
		user_id = request.GET.get('user_id')
		list_of_images = request.FILES.getlist('multi_images')
		try:
			user_full_obj = UserFullDetails.objects.get(basic_details__user__id=user_id)
			multiple_images = UserMultiFile.objects.filter(basic_details=user_full_obj)
			for file in multiple_images:
				response[file.id] = {
										"id":file.id,
										"multi_images":file.files.url 
									}
		except  Exception as e:
			print(e)
			return Response([{"message":str(e)}])
		return Response(response.values(),status=status.HTTP_200_OK)

	def delete(self, request):
		response = {}
		user_id = request.GET.get('user_id')
		image_id = request.GET.get('multi_images_id')
		try:
			user_full_obj = UserFullDetails.objects.get(basic_details__user__id=user_id)
			multiple_images = UserMultiFile.objects.get(basic_details=user_full_obj,id=image_id)
			multiple_images.delete()
		except  Exception as e:
			print(e)
			return Response([{"message":str(e)}])
		return Response([{"message":"delete Successful"}],status=status.HTTP_200_OK)

class MatchOfTheDayView(APIView):
	def post(self, request):
		Match_user_id = request.GET.get('Match_user_id')
		Today_date = date.today()
		try:
			ls_obj = MatchOfTheDay.objects.get(user_id=Match_user_id)
			return Response({"message":"Data Already existed",
							"status": False})
		except Exception as e:
			MatchOfTheDay.objects.create(user_id=Match_user_id,created_at=Today_date,Ative_status=True)
			return Response({"message":"Match of the data saved",
							"status":True})
		return Response([{"message":"Images Stored Successful"}],status=status.HTTP_200_OK)


	def get(self, request):
		response = {}
		user = request.GET.get('user_id')
		try:
			user_qs	= MatchOfTheDay.objects.filter(created_at=date.today(),Ative_status=True)
			main_obj = UserFullDetails.objects.get(basic_details__user__id=user)
			for dt in user_qs:
				user_basic_obj = UserBasicDetails.objects.get(user__id = int(dt.user_id))
				user_full_obj = UserFullDetails.objects.get(basic_details__id=user_basic_obj.id)
				if main_obj.gender != user_full_obj.gender:
					serializer1=UserBasicDetailsSerialzers(user_basic_obj,many=False)
					response[int(dt.user_id)] = serializer1.data
					serializer2=UserFullDetailsSerialzers(user_full_obj,many=False)
					response[int(dt.user_id)].update({"age":calculate_age(user_full_obj.dateofbirth)})
					response[int(dt.user_id)].update(serializer2.data)
					try:
						liked_obj = LikedStatus.objects.get(user__id=user,user_liked =int(dt.user_id))
						response[int(dt.user_id)].update({"LikedStatus":liked_obj.LikedStatus})
					except Exception as e:
						response[int(dt.user_id)].update({"LikedStatus":False})
					try:
						req_status = FriendRequests.objects.get(user__id=user,requested_user_id=int(dt.user_id))
						response[int(dt.user_id)].update({"Req_status":req_status.status})
					except Exception as e:
						response[int(dt.user_id)].update({"Req_status":False})
					visible_obj = VisibleDataRequest.objects.filter(main_user_id=user,visible_user_id=dt.user_id)
					res = {}
					if visible_obj:
						for visible_dt in visible_obj:
							try:
								visible_food = VisibleDataRequest.objects.get(main_user_id=user,visible_user_id=dt.user_id,key_name='food')
								response[int(dt.user_id)].update({"food_status":True})
							except:
								response[int(dt.user_id)].update({"food_status":False})
												
							try:
								visible_smoke = VisibleDataRequest.objects.get(main_user_id=user,visible_user_id=dt.user_id,key_name='smoke')
								response[int(dt.user_id)].update({"smoke_status":True})
							except:
								response[int(dt.user_id)].update({"smoke_status":False})
							try:
								visible_drink = VisibleDataRequest.objects.get(main_user_id=user,visible_user_id=dt.user_id,key_name='drink')
								response[int(dt.user_id)].update({"drink_status":True})
							except:
								response[int(dt.user_id)].update({"drink_status":False})

							try:
								visible_phone = VisibleDataRequest.objects.get(main_user_id=user,visible_user_id=dt.user_id,key_name='phone')
								response[int(dt.user_id)].update({"phone_status":True})
							except:
								response[int(dt.user_id)].update({"phone_status":False})
							res[visible_dt.key_name] = {"key_name": visible_dt.key_name,
													"visible_status": visible_dt.visible_status}

						response[int(dt.user_id)].update({"visible_data":res.values()})
					else:
						response[int(dt.user_id)].update({"food_status":False})
						response[int(dt.user_id)].update({"smoke_status":False})
						response[int(dt.user_id)].update({"drink_status":False})
						response[int(dt.user_id)].update({"phone_status":False})
						response[int(dt.user_id)].update({"visible_data": [{
																		"visible_status":"Pending",
																		'key_name':None
																		}]
													})

		except  Exception as e:
			print(e)
			return Response({"message":str(e)})
		return Response(response.values(),status=status.HTTP_200_OK)

class VisibleDataRequestView(APIView):
	def post(self, request):
		if not request.POST._mutable:
			request.POST._mutable = True
		user_id = request.GET.get('user_id')
		data = request.data
		response = {}
		data['main_user_id']=user_id
		data['visible_status']="Pending"
		try:
			visible_obj = VisibleDataRequest.objects.get(main_user_id=user_id,visible_user_id=data['visible_user_id'],key_name=data['key_name'])
			serializer2=VisibleDataRequestSerialzers(visible_obj,many=False)
			response.update(serializer2.data)
			return Response(response,status=status.HTTP_200_OK)
		except Exception as e:
			serializer = VisibleDataRequestSerialzers(data = data)
			if serializer.is_valid(): 
				serializer.save()
				return Response(serializer.data, status=status.HTTP_201_CREATED)
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
	
	def get(self, request):
			user_id = request.GET.get('user_id')
			response = {}
			try:
				req = VisibleDataRequest.objects.filter(visible_user_id=user_id, visible_status='Pending')
				for data in req:
					user_basic_obj = UserBasicDetails.objects.get(user__id = data.main_user_id)
					serializer1=UserBasicDetailsSerialzers(user_basic_obj, many=False)
					response[data.main_user_id] = serializer1.data
					user_full = UserFullDetails.objects.get(basic_details__id=user_basic_obj.id)
					serializer2=UserFullDetailsSerialzers(user_full, many=False)
					response[data.main_user_id].update({"age":calculate_age(user_full.dateofbirth)})
					response[data.main_user_id].update(serializer2.data)
					try:
						liked_obj = LikedStatus.objects.get(user__id=data.main_user_id,user_liked =user_id)
						response[data.main_user_id].update({"LikedStatus":liked_obj.LikedStatus})
					except Exception as e:
						response[data.main_user_id].update({"LikedStatus":False})
					try:
						req_status = FriendRequests.objects.get(user__id=data.main_user_id,requested_user_id=user_id)
						response[data.main_user_id].update({"requested_user_id":req_status.requested_user_id,
													"created_at":req_status.created_at,
													"created_time":req_status.created_time,
													"request_status":req_status.request_status,
													"updated_at":req_status.updated_at,
													"updated_time":req_status.updated_time,
													"status":req_status.status,
													"Req_status":req_status.status})
					except Exception as e:
						response[data.main_user_id].update({"Req_status":False})
					
					visible_obj = VisibleDataRequest.objects.filter(main_user_id=data.main_user_id,visible_user_id=user_id)
					res = {}
					if visible_obj:
						for visible_dt in visible_obj:
							try:
								visible_food = VisibleDataRequest.objects.get(main_user_id=data.main_user_id,visible_user_id=user_id,key_name='food')
								response[data.main_user_id].update({"food_status":True})
							except:
								response[data.main_user_id].update({"food_status":False})
												
							try:
								visible_smoke = VisibleDataRequest.objects.get(main_user_id=data.main_user_id,visible_user_id=user_id,key_name='smoke')
								response[data.main_user_id].update({"smoke_status":True})
							except:
								response[data.main_user_id].update({"smoke_status":False})
							try:
								visible_drink = VisibleDataRequest.objects.get(main_user_id=data.main_user_id,visible_user_id=user_id,key_name='drink')
								response[data.main_user_id].update({"drink_status":True})
							except:
								response[data.main_user_id].update({"drink_status":False})

							try:
								visible_phone = VisibleDataRequest.objects.get(main_user_id=data.main_user_id,visible_user_id=user_id,key_name='phone')
								response[data.main_user_id].update({"phone_status":True})
							except:
								response[data.main_user_id].update({"phone_status":False})
							res[visible_dt.key_name] = {"key_name": visible_dt.key_name,
													"visible_status": visible_dt.visible_status}

						response[data.main_user_id].update({"visible_data":res.values()})
					else:
						response[data.main_user_id].update({"food_status":False})
						response[data.main_user_id].update({"smoke_status":False})
						response[data.main_user_id].update({"drink_status":False})
						response[data.main_user_id].update({"phone_status":False})
						response[data.main_user_id].update({"visible_data": [{
																		"visible_status":"Pending",
																		'key_name':None
																		}]
													})
			except Exception as e:
				response['message'] = {'message': str(e)}
				return Response(response.values(),status=status.HTTP_400_BAD_REQUEST)
			return Response(response.values(),status=status.HTTP_200_OK)
	
	def put(self, request):
		if not request.POST._mutable:
			request.POST._mutable = True
		visible_user_id = request.GET.get('visible_user_id')
		data = request.data
		queryset = VisibleDataRequest.objects.get(main_user_id=data['user_id'],visible_user_id=visible_user_id,key_name=data['key_name'])
		req_serializer = VisibleDataRequestSerialzers(queryset, data=data, partial=True)
		if req_serializer.is_valid():
			req_serializer.save()
			return Response(req_serializer.data,status=status.HTTP_200_OK)
		return Response(req_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AcceptedVisibleDataView(APIView):
	def get(self, request):
				user_id = request.GET.get('user_id')
				response = {}
				try:
					req = VisibleDataRequest.objects.filter(main_user_id=user_id, visible_status='Visible')
					for data in req:
						user_basic_obj = UserBasicDetails.objects.get(user__id = data.visible_user_id)
						serializer1=UserBasicDetailsSerialzers(user_basic_obj, many=False)
						response[data.visible_user_id] = serializer1.data
						user_full = UserFullDetails.objects.get(basic_details__id=user_basic_obj.id)
						serializer2=UserFullDetailsSerialzers(user_full, many=False)
						response[data.visible_user_id].update({"age":calculate_age(user_full.dateofbirth)})
						response[data.visible_user_id].update(serializer2.data)
						try:
							liked_obj = LikedStatus.objects.get(user__id=data.visible_user_id,user_liked =user_id)
							response[data.visible_user_id].update({"LikedStatus":liked_obj.LikedStatus})
						except Exception as e:
							response[data.visible_user_id].update({"LikedStatus":False})
						try:
							req_status = FriendRequests.objects.get(user__id=data.visible_user_id,requested_user_id=user_id)
							response[data.visible_user_id].update({"requested_user_id":req_status.requested_user_id,
														"created_at":req_status.created_at,
														"created_time":req_status.created_time,
														"request_status":req_status.request_status,
														"updated_at":req_status.updated_at,
														"updated_time":req_status.updated_time,
														"status":req_status.status,
														"Req_status":req_status.status})
						except Exception as e:
							response[data.visible_user_id].update({"Req_status":False})
						
						visible_obj = VisibleDataRequest.objects.filter(visible_user_id=data.visible_user_id,main_user_id=user_id)
						res = {}
						if visible_obj:
							print(visible_obj)
							for visible_dt in visible_obj:
								try:
									visible_food = VisibleDataRequest.objects.get(main_user_id=user_id,visible_user_id=data.visible_user_id,key_name='food')
									response[data.visible_user_id].update({"food_status":True})
								except:
									response[data.visible_user_id].update({"food_status":False})
													
								try:
									visible_smoke = VisibleDataRequest.objects.get(main_user_id=user_id,visible_user_id=data.visible_user_id,key_name='smoke')
									response[data.visible_user_id].update({"smoke_status":True})
								except:
									response[data.visible_user_id].update({"smoke_status":False})
								try:
									visible_drink = VisibleDataRequest.objects.get(main_user_id=user_id,visible_user_id=data.visible_user_id,key_name='drink')
									response[data.visible_user_id].update({"drink_status":True})
								except:
									response[data.visible_user_id].update({"drink_status":False})

								try:
									visible_phone = VisibleDataRequest.objects.get(main_user_id=user_id,visible_user_id=data.visible_user_id,key_name='phone')
									response[data.visible_user_id].update({"phone_status":True})
								except:
									response[data.visible_user_id].update({"phone_status":False})
								res[visible_dt.key_name] = {"key_name": visible_dt.key_name,
														"visible_status": visible_dt.visible_status}

							response[data.visible_user_id].update({"visible_data":res.values()})
						else:
							response[data.visible_user_id].update({"food_status":False})
							response[data.visible_user_id].update({"smoke_status":False})
							response[data.visible_user_id].update({"drink_status":False})
							response[data.visible_user_id].update({"phone_status":False})
							response[data.visible_user_id].update({"visible_data": [{
																			"visible_status":"Pending",
																			'key_name':None
																			}]
														})
				except Exception as e:
					response['message'] = {'message': str(e)}
					return Response(response.values(),status=status.HTTP_400_BAD_REQUEST)
				return Response(response.values(),status=status.HTTP_200_OK)

class RejectedVisibleDataView(APIView):
	def get(self, request):
				user_id = request.GET.get('user_id')
				response = {}
				try:
					req = VisibleDataRequest.objects.filter(main_user_id=user_id, visible_status='Unvisible')
					for data in req:
						user_basic_obj = UserBasicDetails.objects.get(user__id = data.visible_user_id)
						serializer1=UserBasicDetailsSerialzers(user_basic_obj, many=False)
						response[data.visible_user_id] = serializer1.data
						user_full = UserFullDetails.objects.get(basic_details__id=user_basic_obj.id)
						serializer2=UserFullDetailsSerialzers(user_full, many=False)
						response[data.visible_user_id].update({"age":calculate_age(user_full.dateofbirth)})
						response[data.visible_user_id].update(serializer2.data)
						try:
							liked_obj = LikedStatus.objects.get(user__id=data.visible_user_id,user_liked =user_id)
							response[data.visible_user_id].update({"LikedStatus":liked_obj.LikedStatus})
						except Exception as e:
							response[data.visible_user_id].update({"LikedStatus":False})
						try:
							req_status = FriendRequests.objects.get(user__id=data.visible_user_id,requested_user_id=user_id)
							response[data.visible_user_id].update({"requested_user_id":req_status.requested_user_id,
														"created_at":req_status.created_at,
														"created_time":req_status.created_time,
														"request_status":req_status.request_status,
														"updated_at":req_status.updated_at,
														"updated_time":req_status.updated_time,
														"status":req_status.status,
														"Req_status":req_status.status})
						except Exception as e:
							response[data.visible_user_id].update({"Req_status":False})
						
						visible_obj = VisibleDataRequest.objects.filter(visible_user_id=data.visible_user_id,main_user_id=user_id)
						res = {}
						if visible_obj:
							print(visible_obj)
							for visible_dt in visible_obj:
								try:
									visible_food = VisibleDataRequest.objects.get(main_user_id=user_id,visible_user_id=data.visible_user_id,key_name='food')
									response[data.visible_user_id].update({"food_status":True})
								except:
									response[data.visible_user_id].update({"food_status":False})
													
								try:
									visible_smoke = VisibleDataRequest.objects.get(main_user_id=user_id,visible_user_id=data.visible_user_id,key_name='smoke')
									response[data.visible_user_id].update({"smoke_status":True})
								except:
									response[data.visible_user_id].update({"smoke_status":False})
								try:
									visible_drink = VisibleDataRequest.objects.get(main_user_id=user_id,visible_user_id=data.visible_user_id,key_name='drink')
									response[data.visible_user_id].update({"drink_status":True})
								except:
									response[data.visible_user_id].update({"drink_status":False})

								try:
									visible_phone = VisibleDataRequest.objects.get(main_user_id=user_id,visible_user_id=data.visible_user_id,key_name='phone')
									response[data.visible_user_id].update({"phone_status":True})
								except:
									response[data.visible_user_id].update({"phone_status":False})
								res[visible_dt.key_name] = {"key_name": visible_dt.key_name,
														"visible_status": visible_dt.visible_status}

							response[data.visible_user_id].update({"visible_data":res.values()})
						else:
							response[data.visible_user_id].update({"food_status":False})
							response[data.visible_user_id].update({"smoke_status":False})
							response[data.visible_user_id].update({"drink_status":False})
							response[data.visible_user_id].update({"phone_status":False})
							response[data.visible_user_id].update({"visible_data": [{
																			"visible_status":"Pending",
																			'key_name':None
																			}]
														})
				except Exception as e:
					response['message'] = {'message': str(e)}
					return Response(response.values(),status=status.HTTP_400_BAD_REQUEST)
				return Response(response.values(),status=status.HTTP_200_OK)