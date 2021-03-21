from django.db import models
from django.contrib.auth.models import User

class UserBasicDetails(models.Model):
	user = models.OneToOneField(User, null=True, blank=True,on_delete=models.CASCADE)
	matrimony_id = models.CharField(max_length=20,null=True)
	phone_number = models.CharField(max_length=20,null=True)
	
	class Meta:
		unique_together = ("phone_number","matrimony_id",)
	
	def __str__(self):
		return "%s" %(self.user)

class UserFullDetails(models.Model):
	basic_details = models.ForeignKey(UserBasicDetails, on_delete=models.CASCADE)
	name = models.CharField(max_length=20,null=True)
	gender = models.CharField(max_length=20,null=True)
	dateofbirth = models.CharField(max_length=20,null=True)
	image = models.ImageField(upload_to='profile_pic/')

#basic details
	# age	= models.CharField(max_length=100,null=True)
	height = models.CharField(max_length=100,null=True)
	physical_status = models.CharField(max_length=100,null=True)
	weight	= models.CharField(max_length=100,null=True)
	body_type	= models.CharField(max_length=100,null=True)
	marital_status	= models.CharField(max_length=100,null=True)
	mother_tongue = models.CharField(max_length=100,null=True)
	food_type	= models.CharField(max_length=100,null=True)
	drink_habbit	= models.CharField(max_length=100,null=True)
	smoke_habbit	= models.CharField(max_length=100,null=True)
	
#birth & religious
	birth_time	= models.CharField(max_length=100,null=True)
	birth_place	= models.CharField(max_length=100,null=True)
	gotram	= models.CharField(max_length=100,null=True)
	star	= models.CharField(max_length=100,null=True)
	rashi = models.CharField(max_length=100,null=True)
	caste = models.CharField(max_length=100,null=True)
	sub_caste	= models.CharField(max_length=100,null=True)
	religion = models.CharField(max_length=100,null=True)
	
#location & contact
	city = models.CharField(max_length=100,null=True)
	state = models.CharField(max_length=100,null=True)
	country = models.CharField(max_length=100,null=True)
	citizenship = models.CharField(max_length=100,null=True)

#profession & education
	occupation = models.CharField(max_length=100,null=True)
	graduation = models.CharField(max_length=100,null=True)
	graduation_status = models.CharField(max_length=100,null=True)
	annual_income = models.CharField(max_length=100,null=True)
	job_sector = models.CharField(max_length=100,null=True)
	college	= models.CharField(max_length=100,null=True)
	under_graduation = models.CharField(max_length=100,null=True)
	post_graduation	= models.CharField(max_length=100,null=True)
	super_speciality = models.CharField(max_length=100,null=True)

#family details
	total_family_members = models.CharField(max_length=100,null=True)
	father_details = models.CharField(max_length=100,null=True)
	mother_details = models.CharField(max_length=100,null=True)
	brother_details = models.CharField(max_length=100,null=True)
	sister_details = models.CharField(max_length=100,null=True)

	Few_Words_MySelf =  models.TextField()

	def __str__(self):
		return "%s" %(self.basic_details.id)

class SaveOTP(models.Model):

	phone_number = models.ForeignKey(UserBasicDetails, on_delete=models.CASCADE)
	otp = models.IntegerField(null=True) 

	class Meta:
		unique_together = ('phone_number',)

	def __str__(self):
		return "%s"%(self.phone_number)

class Viewed_matches(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	viewed_user_id = models.CharField(max_length=100,null=True)
	viewd_status = models.BooleanField(default=True)
	
	def __str__(self):
		return "%s"%(self.user)

class Partner_Preferences(models.Model):
	basic_details = models.ForeignKey(UserBasicDetails, on_delete=models.CASCADE)
# basic details
	min_age = models.CharField(max_length=100,null=True)
	max_age = models.CharField(max_length=100,null=True)
	min_height = models.CharField(max_length=100,null=True)
	max_height = models.CharField(max_length=100,null=True)
	physical_status = models.CharField(max_length=100,null=True)
	mother_tongue = models.CharField(max_length=100,null=True)
	marital_status = models.CharField(max_length=100,null=True)
	diet_preference = models.CharField(max_length=100,null=True)
	drinking_habbit = models.CharField(max_length=100,null=True)
	smoking_habbit = models.CharField(max_length=100,null=True)
# birth & religious
	caste = models.CharField(max_length=100,null=True)
	religion = models.CharField(max_length=100,null=True)
	star = models.CharField(max_length=100,null=True)
# education & profession
	occupation = models.CharField(max_length=100,null=True)
	under_graduation = models.CharField(max_length=100,null=True)
	post_graduation = models.CharField(max_length=100,null=True)
	super_speciality = models.CharField(max_length=100,null=True)
	annual_income = models.CharField(max_length=100,null=True)
	job_sector = models.CharField(max_length=100,null=True)
# residential 
	city = models.CharField(max_length=100,null=True)
	state = models.CharField(max_length=100,null=True)
	country = models.CharField(max_length=100,null=True)
	citizenship = models.CharField(max_length=100,null=True)

	def __str__(self):
		return "%s" %(self.basic_details.id)

class Country(models.Model):
	country= models.CharField(max_length=20)

	class Meta:
			unique_together = ("country",)
	def __str__(self):
		return self.country

class State(models.Model):

	state=models.CharField(max_length=20)
	country = models.ForeignKey(Country, on_delete=models.CASCADE)

	class Meta:
			unique_together = ("state",)	
	def __str__(self):
		return self.state
		
class City(models.Model):

	city=models.CharField(max_length=20)
	state=models.ForeignKey(State, on_delete=models.CASCADE)

	class Meta:
			unique_together = ("city",)

	def __str__(self):
		return self.city

class Height(models.Model):

	height=models.CharField(max_length=20)
	class Meta:
		unique_together = ('height',)	
	def __str__(self):
		return self.city

class Religion(models.Model):

	religion=models.CharField(max_length=20)
	class Meta:
		unique_together = ('religion',)	
	def __str__(self):
		return self.city

class Qualification(models.Model):

	qualification=models.CharField(max_length=20)
	class Meta:
		unique_together = ('qualification',)	
	def __str__(self):
		return self.qualification

class Under_graduation(models.Model):

	under_graduation=models.CharField(max_length=20)
	class Meta:
		unique_together = ('under_graduation',)	
	def __str__(self):
		return self.qualification

class Post_graduation(models.Model):

	post_graduation=models.CharField(max_length=20)
	class Meta:
		unique_together = ('post_graduation',)	
	def __str__(self):
		return self.post_graduation

class Super_speciality(models.Model):

	super_speciality=models.CharField(max_length=20)
	class Meta:
		unique_together = ('super_speciality',)	
	def __str__(self):
		return self.super_speciality

class Rasi(models.Model):

	rasi=models.CharField(max_length=20)
	class Meta:
		unique_together = ('rasi',)	
	def __str__(self):
		return self.rasi

class Age(models.Model):

	age=models.CharField(max_length=20)
	class Meta:
		unique_together = ('age',)	
	def __str__(self):
		return self.age

class Stars(models.Model):

	stars=models.CharField(max_length=20)
	class Meta:
		unique_together = ('stars',)	
	def __str__(self):
		return self.stars

class Mother_Occ(models.Model):

	mother_Occ=models.CharField(max_length=20)
	class Meta:
		unique_together = ('mother_Occ',)	
	def __str__(self):
		return self.mother_Occ

class Father_Occ(models.Model):

	father_Occ=models.CharField(max_length=20)
	class Meta:
		unique_together = ('father_Occ',)	
	def __str__(self):
		return self.father_Occ

class Food_Hobbit(models.Model):

	food_Hobbit=models.CharField(max_length=20)
	class Meta:
		unique_together = ('food_Hobbit',)	
	def __str__(self):
		return self.food_Hobbit

class Drink_Hobbit(models.Model):

	drink_Hobbit=models.CharField(max_length=20)
	class Meta:
		unique_together = ('drink_Hobbit',)	
	def __str__(self):
		return self.drink_Hobbit

class Smoke_Hobbit(models.Model):

	smoke_Hobbit=models.CharField(max_length=20)
	class Meta:
		unique_together = ('smoke_Hobbit',)	
	def __str__(self):
		return self.smoke_Hobbit

class Job_sector(models.Model):

	job_sector=models.CharField(max_length=20)
	class Meta:
		unique_together = ('job_sector',)	
	def __str__(self):
		return self.job_sector

class Gender(models.Model):

	gender=models.CharField(max_length=20)
	class Meta:
		unique_together = ('gender',)	
	def __str__(self):
		return self.gender

class Caste(models.Model):

	caste=models.CharField(max_length=20)
	class Meta:
		unique_together = ('caste',)	
	def __str__(self):
		return self.caste


class Annual_income(models.Model):

	annual_income=models.CharField(max_length=20)
	class Meta:
		unique_together = ('annual_income',)	
	def __str__(self):
		return self.annual_income

class Marital_status(models.Model):

	marital_status=models.CharField(max_length=20)
	class Meta:
		unique_together = ('marital_status',)	
	def __str__(self):
		return self.marital_status

class Physical_status(models.Model):

	physical_status=models.CharField(max_length=20)
	class Meta:
		unique_together = ('physical_status',)	
	def __str__(self):
		return self.physical_status

class Mother_Tongue(models.Model):

	mother_Tongue=models.CharField(max_length=20)
	class Meta:
		unique_together = ('mother_Tongue',)	
	def __str__(self):
		return self.mother_Tongue

class Created_by(models.Model):

	created_by=models.CharField(max_length=20)
	class Meta:
		unique_together = ('created_by',)	
	def __str__(self):
		return self.created_by

class Citizen(models.Model):

	citizen=models.CharField(max_length=20)
	class Meta:
		unique_together = ('citizen',)	
	def __str__(self):
		return self.citizen

class Profession(models.Model):

	profession=models.CharField(max_length=20)
	class Meta:
		unique_together = ('profession',)	
	def __str__(self):
		return self.profession

class Birth_place(models.Model):

	birth_place=models.CharField(max_length=20)
	class Meta:
		unique_together = ('birth_place',)	
	def __str__(self):
		return self.birth_place

class Family_type(models.Model):

	family_type=models.CharField(max_length=20)
	class Meta:
		unique_together = ('family_type',)	
	def __str__(self):
		return self.family_type

# class requests(models.Model):

# 	request_status_types = (
# 		("Pending","Pending"),
# 		("Approved","Approved"),
# 		("Rejected","Rejected"),
# 		)

# 	user = models.ForeignKey(User, on_delete=models.CASCADE)
# 	requested_user_id = models.CharField(max_length=100,null=True)
# 	created_at = models.DateField()
# 	request_status = models.CharField(choices = request_status_types, default="Pending", max_length = 25)
# 	updated_at = models.DateField()

# 	def __str__(self):
# 		return "%s"%(self.user)

