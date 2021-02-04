from django.db import models
from django.contrib.auth.models import User

class UserBasicDetails(models.Model):
	user = models.OneToOneField(User, null=True, blank=True,on_delete=models.CASCADE)
	matrimony_id = models.CharField(max_length=20,null=True)
	name = models.CharField(max_length=20,null=True)
	phone_number = models.CharField(max_length=20,null=True)
	
	class Meta:
		unique_together = ("phone_number","matrimony_id",)
	
	def __str__(self):
		return "%s" %(self.user)

class UserFullDetails(models.Model):
	basic_details = models.ForeignKey(UserBasicDetails, on_delete=models.CASCADE)
	gender = models.CharField(max_length=20,null=True)
	dateofbirth = models.CharField(max_length=20,null=True)
	image = models.ImageField(upload_to='profile_pic/')

#basic details
	height = models.CharField(max_length=100,null=True)
	age	= models.CharField(max_length=100,null=True)
	marital_status	= models.CharField(max_length=100,null=True)
	body_type	= models.CharField(max_length=100,null=True)
	food_type	= models.CharField(max_length=100,null=True)
	drink_habbit	= models.CharField(max_length=100,null=True)
	smoke_habbit	= models.CharField(max_length=100,null=True)
	weight	= models.CharField(max_length=100,null=True)

#location & contact
	city = models.CharField(max_length=100,null=True)
	state = models.CharField(max_length=100,null=True)
	country = models.CharField(max_length=100,null=True)

#profession & education
	profession  = models.CharField(max_length=100,null=True)
	education = models.CharField(max_length=100,null=True)
	salary = models.CharField(max_length=100,null=True)
	company_name = models.CharField(max_length=100,null=True)
	sector = models.CharField(max_length=100,null=True)
	qualification = models.CharField(max_length=100,null=True)
	university = models.CharField(max_length=100,null=True)

#family details
	total_family_members = models.CharField(max_length=100,null=True)
	father_details = models.CharField(max_length=100,null=True)
	mother_details = models.CharField(max_length=100,null=True)
	brother_details = models.CharField(max_length=100,null=True)
	sister_details = models.CharField(max_length=100,null=True)

#other details
	caste = models.CharField(max_length=100,null=True)
	religion = models.CharField(max_length=100,null=True)
	nakshatra = models.CharField(max_length=100,null=True)
	rashi = models.CharField(max_length=100,null=True)
	birthoftime = models.CharField(max_length=100,null=True)
	
	def __str__(self):
		return "%s" %(self.user)

class SaveOTP(models.Model):

	phone_number = models.ForeignKey(UserBasicDetails, on_delete=models.CASCADE)
	otp = models.IntegerField(null=True) 

	class Meta:
		unique_together = ('phone_number',)

	def __str__(self):
		return "%s"%(self.phone_number)

# class Partner_Preferences(models.Model):
	# user = models.ForeignKey(UserDetails, on_delete=models.CASCADE)
#basic details
	#age
	#physical_status
	#mother_tongue
	#marital_status
	#diet_preference
	#drinking_habbit
	#smoking_habbit
#residential 
	#city
	#state
	#country
	#citizenship
#religious
	#commounity
	#sub_caste
	#religion
	#star
	#dosham
#education & profession
	#occupation
	#state
	#employee_in
	#citizenship


# 	def __str__(self):
# 		return "%s"%(self.user)

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

# class Viewed_matches(models.Model):
	#user = models.ForeignKey(User, on_delete=models.CASCADE)
	#viewed_user_id = models.CharField(max_length=100,null=True)

# 	def __str__(self):
# 		return "%s"%(self.user)