from django.contrib import admin
from matrimony_app.models import *

class UserBasicDetailsAdmin(admin.ModelAdmin):
	list_display=['id','phone_number','matrimony_id']

class UserFullDetailsAdmin(admin.ModelAdmin):
	list_display=['id','name','basic_details','gender','dateofbirth']

admin.site.register(UserBasicDetails,UserBasicDetailsAdmin)
admin.site.register(UserFullDetails,UserFullDetailsAdmin)
admin.site.register(SaveOTP)
admin.site.register(Viewed_matches)
admin.site.register(Partner_Preferences)
admin.site.register(Country)
admin.site.register(State)
admin.site.register(City)
admin.site.register(LikedStatus)
