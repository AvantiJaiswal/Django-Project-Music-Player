from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import View
from .models import *
import json
from django.db.models import Q
import os
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError
from .validate import *
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate,login

# Create your views here.


#UserSignup
class UserSignup(View):
	def get(self,request, *args, **kwargs):
		return render(request,'register.html')

	def post(self,request, *args, **kwargs):
		validators = [UserAttributeSimilarityValidator,MinimumLengthValidator, NumericPasswordValidator]
		
		filled_data = dict(request.POST)
		filled_data.pop('csrfmiddlewaretoken')
		
		username = request.POST.get('name', None)
		email = request.POST.get('email', None)
		password = request.POST.get('password1', None)
		conform_pwd = request.POST.get('password2', None)

		if password != conform_pwd:
			context = {
				"filled_data":filled_data
			}
			messages.error(request, ('Password and Confirm Password does not match'))
			return render(request, 'signup.html', context)
		else:
			try:
				for validator in validators:
					if validator == UserAttributeSimilarityValidator:
						user_attributes_array = (username, email)
						er = validator().validate(password, user_attributes_array)
					else:
						er = validator().validate(password)
			except ValidationError as e:
				messages.error(request, str(e.message))
				context = {
					"filled_data":filled_data
				}
				return render(request, 'signup.html', context)

			hashed_pwd = make_password(password)

			check_email = User.objects.filter(email=email).exists()
			if check_email:
				messages.error(request, ("User with this email already exist's, please try again with new one."))
				context = {
					"filled_data":filled_data
					}
				return render(request, 'signup.html',context)
			else:
				try:
					user = User(username=username,email=email,password=hashed_pwd)
					
					user.save()
					# setting default role for user 
					role = Roles.objects.get(name="customer")
					user_detail = UserDetails(user_id=user.id, role_id=role.id)
					user_detail.save()
					if user:
						messages.success(request, ("Account Created Successfully"))
						return redirect('login')
				except Exception as ex:
					messages.error(request, ("User with this username already exist's, please try again with new one."))
					context = {
						"filled_data":filled_data
					}
					return render(request, 'signup.html',context)

		

class UserLogin(View):
	def get(self,request, *args, **kwargs):
		return render(request,'login.html')
	def post(self,request, *args, **kwargs):
		email = request.POST.get('email',None)
		password = request.POST.get('password',None)
		user = authenticate(request,username=email,password=password)
		if user is not None:
			user_details = UserDetails.objects.get(user=user)
			print('request.session',request.session)
			request.session['role'] = user_details.role.name
			login(request,user)
			return redirect('playlists')       
		else:
			return render(request,'login.html')



#SongView
class SongView(View):

	def __init__(self,*args,**kwargs):
		path = os.getcwd()

		with open(os.path.join(path, "form_jsons/Song.json"), 'r') as file:
			self.queryset = file.read()

	def get(self,request,*args, **kwargs):
		file = self.queryset 
		queryset_dict = json.loads(file)

		action = request.GET.get('action',None)
		instance_id = request.GET.get('id',None)
		search = request.GET.get('search',None)
		entries = request.GET.get('entries', '5')

		table_values = queryset_dict['HTML_table']['values']
		list_table_values = [x["name"] for x in table_values]
		
		if action == 'create':	
			context = {
				"redirect":"song"
			}       
			return render(request, 'create_songs.html', context)

		elif action == 'edit':
			if instance_id:
				data = Song.objects.filter(status_code=1).get(id=instance_id)

				

				json_string = str(queryset_dict)
				context = {"data":data, "redirect":"song", }
				return render(request,'edit_songs.html',context)

		elif action == 'delete':	
			if instance_id:
				return self.delete(request)

		elif action == 'search':
			data = Song.objects.filter(Q(song_name__icontains=search)|Q(genre__icontains=search)|Q(album_name__icontains=search)|Q(artist_name__icontains=search)|Q(year_of_release__icontains=search)|Q(audio__icontains=search),status_code=1).all()

			paginator = Paginator(data, int(entries)) 
			page_number = request.GET.get('page')
			page_obj = paginator.get_page(page_number)
			pagination_url = request.path + "?entries=" + entries + "&search=" + search + "&action=" + action + "&"

			#TODO: Uncomment if checkbox field is included in the form.
			#for i in data:
				#var =i.checkbox.replace("[","")
				#var = var.replace("]","")
				#var = var.replace("'", "")
				#var = var.split(",")
				#i.checkbox = var
				#i.save()

			context = {
				"data":data, 
				"values":table_values, 
				"JsonForm": queryset_dict, 
				"redirect":"song",
				"entries" : entries,
				"page_obj" : page_obj,
				"pagination_url" : pagination_url,
				}
			return render(request,'table.html',context)

		else:    						
			data = Song.objects.filter(status_code = 1).only(*list_table_values)

			paginator = Paginator(data, int(entries)) 
			page_number = request.GET.get('page')
			page_obj = paginator.get_page(page_number)

			if action:
				pagination_url = request.path + "?entries=" + entries + "&action=" + action + "&"          
			else:
				pagination_url = request.path + "?entries=" + entries + "&"


			#TODO: Uncomment if checkbox field is included in the form.
			
			#for i in data:
				#var =i.checkbox.replace("[","")
				#var = var.replace("]","")
				#var = var.replace("'", "")
				#var = var.split(",")
				#i.checkbox = var
				#i.save()

			context = {
				"data":data,
				"redirect":"song",
				"values":table_values,
				"JsonForm": queryset_dict,
				"entries" : entries,
				"page_obj" : page_obj,
			   	"pagination_url" : pagination_url
			}
			return render(request,'table_songs.html',context)

	# Create
	def post(self,request,*args, **kwargs):
		if '_put' in request.POST:
			return self.put(request)
			
		
		song_name = request.POST.get('song_name', None)
		genre = request.POST.get('genre', None)
		favourite = request.POST.get('favourite', None)
		album_name = request.POST.get('album_name', None)
		artist_name = request.POST.get('artist_name', None)
		year_of_release = request.POST.get('year_of_release', None)
		audio = request.FILES.get('audio',None)
		
		
		data = Song.objects.create(
			song_name = song_name, 
			genre = genre, 
			favourite = favourite,
			album_name = album_name,
			artist_name = artist_name, 
			year_of_release = year_of_release, 
			audio = audio,
			  )
		
		if data:
			return redirect('song')

	# Edit
	def put(self,request,*args,**kwargs):
		
		song_name = request.POST.get('song_name', None)
		genre = request.POST.get('genre', None)
		album_name = request.POST.get('album_name', None)
		artist_name = request.POST.get('artist_name', None)
		year_of_release = request.POST.get('year_of_release', None)
		audio = request.FILES.get('audio',None)
		
		id   = request.POST.get('id',None)

		#TODO: Implement IF validation if file field available in the form

		#if file:
			#obj = Song.objects.get(id=id)
			#'''obj.audio= audio'''
			#obj.save()
		# TODO: Remove file field
		update = Song.objects.filter(id=id).update(song_name = song_name, genre = genre, album_name = album_name, artist_name = artist_name, year_of_release = year_of_release, audio = audio, )
		
		#else: 
		#	old_data = Song.objects.get(id=id)

		#	update = Song.objects.filter(id=id).update(song_name = song_name, genre = genre, album_name = album_name, artist_name = artist_name, year_of_release = year_of_release, audio = audio, )

		if update:
			return redirect('song')
		else:
			return HttpResponse("Not updated")

	# Delete
	def delete(self,request,*args,**kwargs):
		id = request.GET.get('id',None)

		update = Song.objects.filter(id=id).update(status_code=0)
		if update:
			return redirect('song')
		else:
			return HttpResponse("Not updated")



#PlaylistsView
class PlaylistsView(View):

	def __init__(self,*args,**kwargs):
		path = os.getcwd()

		with open(os.path.join(path, "form_jsons/Playlists.json"), 'r') as file:
			self.queryset = file.read()

	def get(self,request,*args, **kwargs):
		file = self.queryset 
		queryset_dict = json.loads(file)

		action = request.GET.get('action',None)
		instance_id = request.GET.get('id',None)
		search = request.GET.get('search',None)
		entries = request.GET.get('entries', '5')

		table_values = queryset_dict['HTML_table']['values']
		list_table_values = [x["name"] for x in table_values]
		
		songs = Song.objects.values('id','song_name').all()
		
		if action == 'create':	
			context = {
				"redirect":"playlists",
				"songs":songs
			}       
			return render(request, 'create_playlists.html', context)

		elif action == 'edit':
			if instance_id:
				data = Playlists.objects.filter(status_code=1).get(id=instance_id)

				

				json_string = str(queryset_dict)
				context = {"data":data, "redirect":"playlists", }
				return render(request,'edit.html',context)

		elif action == 'delete':	
			if instance_id:
				return self.delete(request)

		elif action == 'search':
			data = Playlists.objects.filter(Q(playlists_name__icontains=search)|Q(song_name__icontains=search),status_code=1).all()

			paginator = Paginator(data, int(entries)) 
			page_number = request.GET.get('page')
			page_obj = paginator.get_page(page_number)
			pagination_url = request.path + "?entries=" + entries + "&search=" + search + "&action=" + action + "&"

			#TODO: Uncomment if checkbox field is included in the form.
			#for i in data:
				#var =i.checkbox.replace("[","")
				#var = var.replace("]","")
				#var = var.replace("'", "")
				#var = var.split(",")
				#i.checkbox = var
				#i.save()

			context = {
				"data":data, 
				"values":table_values, 
				"JsonForm": queryset_dict, 
				"redirect":"playlists",
				"entries" : entries,
				"page_obj" : page_obj,
				"pagination_url" : pagination_url,
				}
			return render(request,'table.html',context)

		else:    						
			data = Playlists.objects.filter(playlists_name="Romance")

			paginator = Paginator(data, int(entries)) 
			page_number = request.GET.get('page')

			if action:
				pagination_url = request.path + "?entries=" + entries + "&action=" + action + "&"          
			else:
				pagination_url = request.path + "?entries=" + entries + "&"


			#TODO: Uncomment if checkbox field is included in the form.
			
			#for i in data:
				#var =i.checkbox.replace("[","")
				#var = var.replace("]","")
				#var = var.replace("'", "")
				#var = var.split(",")
				#i.checkbox = var
				#i.save()

			context = {
				"data":data,
				"redirect":"playlists",
				"values":table_values,
				"JsonForm": queryset_dict,
				"entries" : entries,
			   	"pagination_url" : pagination_url
			}
			return render(request,'table_playlists.html',context)

	# Create
	def post(self,request,*args, **kwargs):
		if '_put' in request.POST:
			return self.put(request)
			
		
		playlists_name = request.POST.get('playlists_name', None)
		song = request.POST.get('song_name', None)

		song_instance = Song.objects.get(id = song)
		
		data = Playlists.objects.create(playlists_name = playlists_name, song_name = song_instance, )

		if data:
			return redirect('playlists')

	# Edit
	def put(self,request,*args,**kwargs):
		
		playlists_name = request.POST.get('playlists_name', None)
		song_name = request.POST.get('song_name', None)
		
		id   = request.POST.get('id',None)

		#TODO: Implement IF validation if file field available in the form

		#if file:
			#obj = Playlists.objects.get(id=id)
			#''''''
			#obj.save()
		# TODO: Remove file field
		update = Playlists.objects.filter(id=id).update(playlists_name = playlists_name, song_name = song_name, )
		
		#else: 
		#	old_data = Playlists.objects.get(id=id)

		#	update = Playlists.objects.filter(id=id).update(playlists_name = playlists_name, song_name = song_name, )

		if update:
			return redirect('playlists')
		else:
			return HttpResponse("Not updated")

	# Delete
	def delete(self,request,*args,**kwargs):
		id = request.GET.get('id',None)

		update = Playlists.objects.filter(id=id).update(status_code=0)
		if update:
			return redirect('playlists')
		else:
			return HttpResponse("Not updated")
		








