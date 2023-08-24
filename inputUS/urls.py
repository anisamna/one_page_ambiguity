from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('upload_US.html', views.Upload_UserStory, name='Upload_User_Story'),
    #path('upload_US.html/show_US<int:id>', views.show_uploaded_UserStory, name='show_UserStory'),
    path('see_uploaded_US.html', views.show_uploaded_UserStory, name='show_UserStory'),
    path('preprocessed_US/<int:id>', views.split_user_story_to_segment, name='split_user_story_to_segment'),
    path('see_splitted_US1.html', views.show_splitted_UserStory, name='show_splitted_UserStory'),
    path('del_Upload_US/<int:id>/', views.del_Upload_US, name= 'del_Upload_US'),
    path('report/list', views.view_report_userstory_list, name="report_userstory_list"),
    path('report/print', views.print_report, name="report_userstory_print"),
    path('userstory/<int:project_id>/add', views.add_userstory, name="userstory_project_add"),
    path('userstory/<int:userstory_id>/edit', views.edit_userstory, name="userstory_edit"),
    path('userstory/analyze', views.analyze_data, name="analyze_data"),
    path('userstory/projects', views.view_list_project, name="projects_list_view"),
    path('userstory/projects/add', views.view_add_project, name="projects_add_view"),
    path('userstory/projects/<int:project_id>/edit', views.view_edit_project, name="projects_edit_view"),
    path('userstory/projects/<int:project_id>/delete', views.view_delete_project, name="projects_delete_view"),
    path('keyword', views.view_list_keyword, name="master_keyword")
]