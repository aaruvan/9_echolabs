from django import forms


class CoachSearchForm(forms.Form):
    """User text query for semantic search over the local coaching knowledge base."""

    query = forms.CharField(
        label="Search coaching tips",
        max_length=500,
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "class": "w-full rounded-lg border border-border bg-background px-3 py-2 text-sm text-foreground",
                "placeholder": "e.g. How can I reduce filler words before an interview?",
            }
        ),
    )

    def clean_query(self):
        q = (self.cleaned_data.get("query") or "").strip()
        if not q:
            raise forms.ValidationError("Enter a search query.")
        return q
