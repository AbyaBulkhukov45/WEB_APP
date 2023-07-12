from django.contrib import admin
from django.contrib.admin import register
from .models import Post, Location, Category

admin.site.empty_value_display = 'Не задано'


@register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'text',
        'pub_date',
        'author',
        'location',
        'category',
        'is_published',
        'created_at'
    )
    list_editable = (
        'is_published',
        'category'
    )
    search_fields = ('title',)
    list_filter = ('category',)
    list_display_links = ('title',)


class PostInline(admin.TabularInline):
    model = Post
    extra = 1


@register(Category)
class CategoryAdmin(admin.ModelAdmin):
    inlines = (
        PostInline,
    )

    list_display = (
        'title',
    )


@register(Location)
class LocationAdmin(admin.ModelAdmin):
    inlines = (
        PostInline,
    )

    list_display = (
        'name',
    )
