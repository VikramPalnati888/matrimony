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
				path('new_matches/',NewMatches.as_view(), name="new matches details"),
				path('viewd_details/',ViewdMatches.as_view(), name="viewd matches details"),
				path('pp_details/',PPView.as_view(), name="Partner Preferences details"),
				path('countries/',CountryList.as_view(), name="countries list"),
				path('states/',StatesList.as_view(), name="states list"),
				path('cities/',CitiesList.as_view(), name="cities list"),
	
			]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
