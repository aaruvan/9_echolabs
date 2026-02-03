from django.contrib import admin
from .models import Conversation, TranscriptSegment, ImprovementNote


class TranscriptSegmentInline(admin.TabularInline):
    model = TranscriptSegment
    extra = 1


class ImprovementNoteInline(admin.TabularInline):
    model = ImprovementNote
    extra = 1


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ["title", "user", "recorded_at", "duration_seconds"]
    list_filter = ["recorded_at"]
    search_fields = ["title", "user__username"]
    inlines = [TranscriptSegmentInline]
    date_hierarchy = "recorded_at"


@admin.register(TranscriptSegment)
class TranscriptSegmentAdmin(admin.ModelAdmin):
    list_display = ["conversation", "segment_order", "text_preview", "created_at"]
    list_filter = ["conversation"]
    search_fields = ["text"]
    inlines = [ImprovementNoteInline]
    ordering = ["conversation", "segment_order"]

    @admin.display(description="Text")
    def text_preview(self, obj):
        return obj.text[:60] + "..." if len(obj.text) > 60 else obj.text


@admin.register(ImprovementNote)
class ImprovementNoteAdmin(admin.ModelAdmin):
    list_display = ["segment", "note_type", "feedback_text_preview", "severity", "created_at"]
    list_filter = ["note_type"]
    search_fields = ["feedback_text"]

    @admin.display(description="Feedback")
    def feedback_text_preview(self, obj):
        return obj.feedback_text[:50] + "..." if len(obj.feedback_text) > 50 else obj.feedback_text
