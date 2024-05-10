from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class ObjectManager(models.Manager):
	def get_queryset(self):
		return super().get_queryset().filter(status_code=1)

#Base
class Base(models.Model):
	created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="%(app_label)s_%(class)s_creator_name",null=True, blank=True)
	updated_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="%(app_label)s_%(class)s_editor_name",null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True,null=True,blank=True)
	updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
	status_code = models.BooleanField(default=1)
	objects = ObjectManager()

	class Meta:
		abstract = True

#Privileges
class Privileges(Base):
	privilege_name = models.CharField(max_length=100, blank=True, null=True)
	description = models.CharField(max_length=500, blank=True, null=True)

	def __str__(self):
		return self.privilege_name

#Roles
class Roles(Base):
	role_name = models.CharField(max_length=100, blank=True, null=True)
	privilege = models.ManyToManyField(Privileges)
	description = models.CharField(max_length=500, blank=True, null=True)

	def __str__(self):
		return self.role_name
	
#TypeMasterCategory
class TypeMasterCategory(Base):
	category_name = models.CharField(max_length=100, blank=True, null=True)
	value = models.CharField(max_length=100, blank=True, null=True)
	description = models.CharField(max_length=500, blank=True, null=True)

	def __str__(self):
		return self.category_name
	
#TypeMaster 
class TypeMaster(Base):
	name = models.CharField(max_length=100, blank=True, null=True)
	value = models.CharField(max_length=100, blank=True, null=True)
	category = models.ForeignKey(TypeMasterCategory, on_delete = models.CASCADE)
	description = models.CharField(max_length=500, blank=True, null=True)
	sequence = models.IntegerField(default=0, blank=True, null=True)

	def __str__(self):
		return self.name

#UserDetails
class UserDetails(Base):
	user = models.ForeignKey(User, on_delete = models.CASCADE)
	role = models.ManyToManyField(Roles)

	def __str__(self):
		return self.user.username
	


#Songs
class Song(Base):
	song_name = models.CharField(max_length=100, blank=True, null=True)
	genre = models.CharField(max_length=100, blank=True, null=True)
	favourite = models.BooleanField(default=False, blank=True, null=True)
	album_name = models.CharField(max_length=100, blank=True, null=True)
	artist_name = models.CharField(max_length=100, blank=True, null=True)
	year_of_release = models.IntegerField(default=0, blank=True, null=True)
	audio = models.FileField(upload_to='attachment/',blank=True, null=True)
	 
	def __str__(self):
		return self.song_name



#Playlists
class Playlists(Base):
	playlists_name = models.CharField(max_length=100, blank=True, null=True)
	song_name = models.ForeignKey(Song,on_delete = models.CASCADE)
	 
	def __str__(self):
		return self.playlists_name
	