from django.core.management.base import BaseCommand

from matrimony_app.models import City


class Command(BaseCommand):
	help = "Enter the city details"

	@staticmethod
	def handle(*args, **options):
		print("Creating cities...")
		country = 1
		state = 32
		cities = [
				"Adilabad",
				"Komaram Bheem",
				"Bhadradri",
				"Hyderabad",
				"Jagtial",
				"Jangaon",
				"Jayashankar",
				"Jogulamba",
				"Kamareddy",
				"Karimnagar",
				"Khammam",
				"Mahabubabad",
				"Mahbubnagar",
				"Mancherial",
				"Medak",
				"Medchal–Malkajgiri",
				"Mulugu",
				"Nagarkurnool",
				"Nalgonda",
				"Narayanapet",
				"Nirmal",
				"Nizamabad",
				"Peddapalli",
				"Rajanna Sircilla",
				"Ranga Reddy",
				"Sangareddy",
				"Siddipet",
				"Suryapet",
				"Vikarabad",
				"Wanaparthy",
				"Warangal Rural",
				"Warangal Urban",
				"Yadadri"
				]
		# country = 1
		# state = 2
		# cities = [
		#  "East Godavari", 
		#  "West Godavari", 
		#  "Krishna", 
		#  "Guntur", 
		#  "Prakasam", 
		#  "Nellore", 
		#  "Srikakulam", 
		#  "Vizianagaram",
		#  "Visakhapatnam",
		# "Kurnool",
		# "Chittoor",
		# "Kadapa", 
		# "Anantapur"
		# ]
		# City.objects.all().delete()
		# print('All cities are deleted')
		index = 0
		while index < len(cities):
			city_obj = City()
			city_obj.country_id = country
			city_obj.state_id = state
			city_obj.city = cities[index]
			city_obj.save()
			index += 1
		print('Successfully created cities.')
