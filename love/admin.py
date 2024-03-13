from django.contrib import admin
from love.models import CategoryModel, PostModel, Comment
# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
    list_display = [ 'id', 'name', 'description', 'create_date']

class PostAdmin(admin.ModelAdmin):
    list_display = [ 'id', 'title', 'content', 'author', 'category', 'create_date']

class CommentAdmin(admin.ModelAdmin):
    list_display = [ 'id', 'file', 'content', 'create_date']

admin.site.register(CategoryModel, CategoryAdmin)
admin.site.register(PostModel, PostAdmin)
admin.site.register(Comment, CommentAdmin)