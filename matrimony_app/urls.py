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
				path('search/',SearchingView.as_view(), name="searching"),
				path('searchpp/',SearchingPPView.as_view(), name="searching pp"),
				path('ug_pg_matches/',UgPgMatchesView.as_view(), name="Ug & Pg Matches"),
				path('pp_matches/',PPMatchingView.as_view(), name="Pp Matches"),
				path('like_unlike/',LikeView.as_view(), name="like status"),
				path('matchebycat/',MatchesByCatView.as_view(), name="Matches By Cat"),
				path('matchescount/',MatchesCountView.as_view(), name="Matches count"),
				path('dailyreco/',DailyRecoView.as_view(), name="daily recommended"),
				# path('matcheoftheday/',MatcheOfthedayView.as_view(), name="Maatch of the day"),

				path('religion/',ReligionView.as_view(), name="religion"),
				path('job_sector/',Job_sectorView.as_view(), name="Job sectorView"),
				path('marital_status/',Marital_statusView.as_view(), name="Marital statusView"),
				path('food_Hobbit/',Food_HobbitView.as_view(), name="food Hobbit"),
				path('gender/',GenderView.as_view(), name="gender"),
				path('height/',HeightView.as_view(), name="height"),
				path('age/',AgeView.as_view(), name="age"),
				path('created_by/',Created_byView.as_view(), name="created_by"),
				path('drink_Hobbit/',Drink_HobbitView.as_view(), name="drink_Hobbit"),
				path('family_type/',Family_typeView.as_view(), name="family_type"),
				path('father_Occ/',Father_OccView.as_view(), name="father_Occ"),
				path('caste/',CasteView.as_view(), name="caste"),
				path('birth_place/',Birth_placeView.as_view(), name="birth_place"),
				path('annual_income/',Annual_incomeView.as_view(), name="annual_income"),
				path('citizen/',CitizenView.as_view(), name="citizen"),
				path('stars/',StarsView.as_view(), name="stars"),
				path('super_speciality/',Super_specialityView.as_view(), name="super_speciality"),
				path('under_graduation/',Under_graduationView.as_view(), name="under_graduation"),
				path('smoke_Hobbit/',Smoke_HobbitView.as_view(), name="smoke_Hobbit"),
				path('rasi/',RasiView.as_view(), name="rasi"),
				path('qualification/',QualificationView.as_view(), name="qualification"),
				path('post_graduation/',Post_graduationView.as_view(), name="Post_graduation"),
				path('profession/',ProfessionView.as_view(), name="profession"),
				path('mother_Tongue/',Mother_TongueView.as_view(), name="mother_Tongue"),
				path('physical_status/',Physical_statusView.as_view(), name="physical_status"),
				path('mother_Occ/',Mother_OccView.as_view(), name="mother_Occ"),


			]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
