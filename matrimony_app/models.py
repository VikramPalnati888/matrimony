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
	age = models.CharField(max_length=100,null=True)
	height = models.CharField(max_length=100,null=True)
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


class Country(models.Model):
	country= models.CharField(max_length=20)
	def __str__(self):
		return self.country

class State(models.Model):

	state=models.CharField(max_length=20)
	country = models.ForeignKey(Country, on_delete=models.CASCADE)       
	def __str__(self):
		return self.state
		
class City(models.Model):

	city=models.CharField(max_length=20)
	state=models.ForeignKey(State, on_delete=models.CASCADE)
	def __str__(self):
		return self.city

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

