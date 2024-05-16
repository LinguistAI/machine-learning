from django.contrib import admin
from .models import MCTQuestion, MCTTest, DoubleAnswerItem, EliminateItem


class MCTQuestionAdmin(admin.ModelAdmin):
    list_display = ('question', 'email', 'createdAt', 'updatedAt')
    list_filter = ('createdAt', 'updatedAt')
    search_fields = ('question', 'email')


class MCTTestAdmin(admin.ModelAdmin):
    list_display = ('email', 'conversation', 'createdAt', 'updatedAt', 'isCompleted')
    list_filter = ('createdAt', 'updatedAt', 'isCompleted')
    search_field = 'email'

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:
            # If editing an existing object, limit the queryset of questions to those belonging to the current test
            form.base_fields['questions'].queryset = obj.questions.all()
        return form

class DoubleAnswerItemAdmin(admin.ModelAdmin):
    list_display = ('type', 'question', 'maxNumOfUses', 'usesSoFar')
    list_filter = ('maxNumOfUses', 'usesSoFar')
    search_field = 'question__question'


class EliminateItemAdmin(admin.ModelAdmin):
    list_display = ('type', 'question', 'maxNumOfUses', 'usesSoFar')
    list_filter = ('maxNumOfUses', 'usesSoFar')
    search_field = 'question__question'


admin.site.register(MCTQuestion, MCTQuestionAdmin)
admin.site.register(MCTTest, MCTTestAdmin)
admin.site.register(DoubleAnswerItem, DoubleAnswerItemAdmin)
admin.site.register(EliminateItem, EliminateItemAdmin)
