from django import forms
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from .models import US_Upload, UserStory_element


class InputUserStory_Form(ModelForm):
    class Meta:
        model = US_Upload
        fields = ["US_Project_Domain", "US_File_Name", "US_File_Txt"]
        labels = {
            "US_Project_Domain": _("Select Project Domain"),
            "US_File_Name": _("Input file name"),
            "US_File_Txt": _("Upload file in text format"),
        }

        widgets = {
            "US_Project_Domain": forms.Select(attrs={"class": "form-control"}),
            "US_File_Name": forms.TextInput(attrs={"class": "form-control"}),
            "US_File_Txt": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }


class SplitUserStory_to_Segment_Form(ModelForm):
    class Meta:
        model = UserStory_element
        fields = [
            "Project_Name",
            "UserStory_Full_Text",
            "Who_full",
            "What_full",
            "Why_full",
        ]
        labels = {
            "Project_Name": _("Project domain"),
            "UserStory_Full_Text": _("User Story"),
            "Who_full": _("Actor"),
            "What_full": _("Action"),
            "Why_full": _("Goal"),
        }
