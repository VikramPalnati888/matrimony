from django.contrib import admin
from matrimony_app.models import *

class UserBasicDetailsAdmin(admin.ModelAdmin):
	list_display=['id','phone_number','name']

class UserFullDetailsAdmin(admin.ModelAdmin):
	list_display=['basic_details','gender','dateofbirth']


admin.site.register(UserBasicDetails,UserBasicDetailsAdmin)
admin.site.register(UserFullDetails,UserFullDetailsAdmin)
admin.site.register(SaveOTP)



