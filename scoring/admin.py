from django.contrib import admin
from scoring.models import WordScore


class WordScoreAdmin(admin.ModelAdmin):
    list_display = ('word', 'email', 'createdAt', 'updatedAt', 'listId')
    list_filter = ('createdAt', 'updatedAt')
    search_fields = ('word', 'email')
    
    def email(self, obj: WordScore):
        return obj.unknownWord.email
    
    def listId(self, obj: WordScore):
        return obj.unknownWord.listId
    

admin.site.register(WordScore, WordScoreAdmin)
    