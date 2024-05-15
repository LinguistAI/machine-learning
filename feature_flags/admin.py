from django.contrib import admin

from feature_flags.models import Feature, FeatureCategory, UserFeature

@admin.register(FeatureCategory)
class FeatureCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'createdAt', 'updatedAt')
    search_fields = ('name',)
    list_filter = ('createdAt', 'updatedAt')
    readonly_fields = ('createdAt', 'updatedAt')

@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ('name', 'enabled', 'rollout_percentage', 'user_controlled', 'createdAt', 'updatedAt')
    search_fields = ('name',)
    list_filter = ('enabled', 'user_controlled', 'createdAt', 'updatedAt')
    readonly_fields = ('createdAt', 'updatedAt')

@admin.register(UserFeature)
class UserFeatureAdmin(admin.ModelAdmin):
    list_display = ('email', 'feature', 'enabled', 'expiresAt', 'createdAt', 'updatedAt')
    search_fields = ('email', 'feature__name')
    list_filter = ('enabled', 'createdAt', 'updatedAt', 'expiresAt')
    readonly_fields = ('createdAt', 'updatedAt')