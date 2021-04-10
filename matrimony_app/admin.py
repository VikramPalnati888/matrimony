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

