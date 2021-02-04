from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from matrimony_app.views import *


urlpatterns = [
				path('login/',Login.as_view(), name="user login"),
				path('resend/',resend_otp.as_view(), name="resend otp"),
				path('otp_verified/',otp_verification.as_view(), name="otp verification"),
				path('logout/',Logout.as_view(), name="user logout"),
				path('user_full_details/',UserFullDetailsView.as_view(), name="user details"),
				path('dropdown_list/',droplistDetails.as_view(), name="dropdown list details"),
	
			]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
