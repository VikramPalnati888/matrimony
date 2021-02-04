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

def generate_otp():
	"""Generating 4 digits OTP automatically"""
	otp = str(uuid.uuid4().fields[-1])[:4]
	return otp

def generate_Id():
	userid = str(uuid.uuid4().fields[-1])[:4]
	return "MID"+userid


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
					return Response({
									"status":True,
									"user_status":user.is_authenticated, 
									"user_id": user.id,
									"phone_number":data['phone_number'],
									"matrimony_id":user_obj.matrimony_id,
									"name":user_obj.name,
									"message": "Login Successful"
									},status=status.HTTP_200_OK)
				else:
					return Response({"user":"Not valid",
										"user_status":False,
											})
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
		response = {}
		try:
			user_basic_obj = UserBasicDetails.objects.get(user__id = request.user.id)
			print(user_basic_obj)
			user_qs = UserFullDetails.objects.get(basic_details__id=user_basic_obj.id)
		except ObjectDoesNotExist:
			return Response({"message":"UserDetail ObjectDoesNotExist"})
		serializer1=UserBasicDetailsSerialzers(user_basic_obj,many=False)
		response[request.user.id] = serializer1.data
		serializer2=UserFullDetailsSerialzers(user_qs,many=False)
		response[request.user.id].update(serializer2.data)
		return Response(response.values(),status=status.HTTP_200_OK)

	def post(self, request):
		data = request.data
		user_basic_obj = UserBasicDetails.objects.get(user__id = request.user.id)
		user_basic_obj.name = data['name']
		user_basic_obj.save()
		if not request.POST._mutable:
			request.POST._mutable = True
		data['basic_details'] = user_basic_obj.id

		serializer = UserFullDetailsSerialzers(data = data)
		if serializer.is_valid(): 
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	def put(self, request):
		if not request.POST._mutable:
			request.POST._mutable = True
		data = request.data
		if data['name']:
			user_obj = UserBasicDetails.objects.get(id=request.user.id)
			user_obj.name = data['name']
			user_obj.save()
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
			return Response(serializer.data, status=status.HTTP_200_OK)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class NewMatches(APIView):
# 	def get(self, request):

# 	return Response(response, status=status.HTTP_200_OK)

class droplistDetails(APIView):
	def get(self,request):
		height_list = ["4’6”","4’7”","4’8”","4’9”","4’10”","4’11”","5’0”",
						"5’1”","5’2”","5’3”","5’4”","5’5”","5’6”","5’7”",
						"5’8”","5’9”","5’10”","5’11”","6’0”"]
		religion_list = ["Hindu","Muslim","Christan","Sikh","Budhist","Jain","Other Religion"]
		qualification_list = ["B.tech","Degree","Inter","BE","10th","Others"]
		response = {
					"Height": height_list,
					"Religion":religion_list,
					"Qualification":qualification_list
					}
		return Response(response, status=status.HTTP_200_OK)