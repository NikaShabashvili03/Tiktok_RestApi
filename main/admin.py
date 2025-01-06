from django.contrib import admin
from .models import Session, User, Video, Like, HashTag, Recomended, View


admin.site.register(User)
admin.site.register(Session)
admin.site.register(Recomended)
# Register your models here.

class HashTagInline(admin.TabularInline):
    model = HashTag
    extra = 1


class LikeInline(admin.TabularInline):
    model = Like
    extra = 0

class ViewInline(admin.TabularInline):
    model = View
    extra = 0

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('id', 'description', 'category', 'created_at', 'creator', 'likes_count', 'views_count', 'hashtags_list')
    inlines = [HashTagInline, LikeInline, ViewInline]

    def views_count(self, obj):
        return obj.views.count()
    
    def likes_count(self, obj):
        return obj.likes.count()

    def hashtags_list(self, obj):
        return ", ".join([hashtag.tag for hashtag in obj.hashtags.all()])

    likes_count.short_description = "Likes"
    views_count.short_description = "Views"
    hashtags_list.short_description = "Hashtags"