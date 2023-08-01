from django.test import TestCase
from inputUS.models import Project, UserStory_element
from functions.analysis_userstory import AnalysisData

def test_analysis(project_id):
    project_ = Project.objects.get(id=project_id)
    userstory_list = UserStory_element.objects.filter(Project_Name=project_).values_list('id', flat=True)
    story_list_id = list(set(userstory_list))
    print(story_list_id)
    AnalysisData(story_list_id).start()
