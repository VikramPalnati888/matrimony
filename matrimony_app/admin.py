from django.contrib import admin
from matrimony_app.models import *


class UserMultiFileAdmin(admin.StackedInline):
	model = UserMultiFile

class UserBasicDetailsAdmin(admin.ModelAdmin):
	list_display=['id','phone_number','matrimony_id']

class UserFullDetailsAdmin(admin.ModelAdmin):
	list_display=['id','name','basic_details','gender','dateofbirth']
	inlines = [UserMultiFileAdmin]	

@admin.register(UserMultiFile)
class UserMultiFileAdmin(admin.ModelAdmin):
	list_display = ('get_user',)

	def get_user(self,obj):
		return obj.basic_details.basic_details.user.id
	get_user.short_description = 'User'



admin.site.register(UserBasicDetails,UserBasicDetailsAdmin)
admin.site.register(UserFullDetails,UserFullDetailsAdmin)
admin.site.register(SaveOTP)
admin.site.register(Viewed_matches)
admin.site.register(Partner_Preferences)
admin.site.register(Country)
admin.site.register(State)
admin.site.register(City)
admin.site.register(LikedStatus)
admin.site.register(FriendRequests)
admin.site.register(MatchOfTheDay)
admin.site.register(VisibleDataRequest)

admin.site.register(Height)
admin.site.register(Religion)
admin.site.register(Qualification)
admin.site.register(Under_graduation)
admin.site.register(Post_graduation)
admin.site.register(Super_speciality)
admin.site.register(Rasi)
admin.site.register(Age)
admin.site.register(Stars)
admin.site.register(Mother_Occ)
admin.site.register(Father_Occ)
admin.site.register(Food_Hobbit)
admin.site.register(Drink_Hobbit)
admin.site.register(Smoke_Hobbit)
admin.site.register(Job_sector)
admin.site.register(Gender)
admin.site.register(Caste)
admin.site.register(Annual_income)
admin.site.register(Marital_status)
admin.site.register(Physical_status)
admin.site.register(Mother_Tongue)
admin.site.register(Created_by)
admin.site.register(Citizen)
admin.site.register(Profession)
admin.site.register(Birth_place)
admin.site.register(Family_type)