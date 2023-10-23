from django.contrib import admin

from .models import Answer, Question, Quiz


# Add the Quiz model for the admin interface
@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('id', 'company', 'title', 'frequency', 'created_at', 'updated_at')
    list_display_links = ('id', )
    list_editable = ('company', 'title', 'frequency', )
    search_fields = ('company', 'title', 'frequency', 'created_at', 'updated_at')
    list_filter = ('company', 'title', 'frequency', 'created_at', 'updated_at')
    list_per_page = 50
    list_max_show_all = 200

    # fieldsets for the 'add' form for a new Quiz
    add_fieldsets = (
        ('Company', {'fields': ('company', )}),
        ('Info', {'fields': ('title', 'frequency', 'description')}),
    )

    # fieldsets for the 'change' form for an existing Quiz
    fieldsets = (
        ('Company', {'fields': ('company', )}),
        ('Info', {'fields': ('title', 'frequency', 'description')}),
    )


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'quiz', 'question_text', 'created_at', 'updated_at')
    list_display_links = ('id', )
    list_editable = ('quiz', 'question_text', )
    search_fields = ('quiz', 'question_text', 'created_at', 'updated_at')
    list_filter = ('quiz', 'created_at', 'updated_at')
    list_per_page = 50
    list_max_show_all = 200

    add_fieldsets = (
        ('Quiz', {'fields': ('quiz', )}),
        ('Info', {'fields': ('question_text', )}),
    )

    fieldsets = (
        ('Quiz', {'fields': ('quiz', )}),
        ('Info', {'fields': ('question_text', )}),
    )


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'is_right')
    list_display_links = ('id', )
    list_editable = ('text', 'is_right')
    search_fields = ('text', 'is_right')
    list_filter = ('question', 'is_right')
    list_per_page = 100
    list_max_show_all = 200

    add_fieldsets = (
        ('Question', {'fields': ('question', )}),
        ('Info', {'fields': ('text', 'is_right')}),
    )

    fieldsets = (
        ('Question', {'fields': ('question',)}),
        ('Info', {'fields': ('text', 'is_right')}),
    )
