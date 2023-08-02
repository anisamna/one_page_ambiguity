import re

from django.contrib import messages

from django.http import JsonResponse
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from functions.segmentation import segmentation, segmentation_edit_userstory
# from functions.well_formed import well_formed_an
from functions.analysis import well_formed_an, stat_preciseness

from .forms import InputUserStory_Form
from .models import (
    US_Upload,
    UserStory_element,
    Result,
    Project,
    ReportUserStory
)

# # Create your views here.


def Upload_UserStory(request):

    if request.method == "POST":
        upload_US_File = InputUserStory_Form(request.POST, request.FILES)
        readFile = request.FILES["US_File_Txt"]
        readLine = readFile.readlines()

        File_content = []

        for line in readLine:
            # print('readLine', readLine)
            # decode bytes to string
            newLine = line.decode("utf-8")
            # newLine = re.sub(r"[^A-Za-z0-9, ]", "", newLine)
            newLine = re.sub(r"[^[^A-Za-z0-9(-){-}[-]⟨-⟩, ]", "", newLine)
            newLine = newLine.strip()
            # print('newLine', newLine)
            if newLine:
                File_content.append(newLine)

        if upload_US_File.is_valid():

            Project_Name = upload_US_File.cleaned_data["US_Project_Domain"]
            File_Name = upload_US_File.cleaned_data["US_File_Name"]
            File_text = readFile

            upload_user_story = US_Upload()

            upload_user_story.US_Project_Domain = Project_Name
            upload_user_story.US_File_Name = File_Name
            upload_user_story.US_File_Txt = File_text
            upload_user_story.US_File_Content = File_content

            upload_user_story.save()

            messages.success(request, "New set of user stories have been successfully added")
            # upload_user_story = InputUserStory_Form()
            # return render(
            #     request,
            #     "inputUS/upload_US.html",
            #     {"form": upload_US_File, "upload_user_story": upload_user_story},
            # )
            return redirect(reverse('show_UserStory'))
        else:
            return redirect("/")
    else:
        upload_US_File = InputUserStory_Form()
        upload_user_story = US_Upload.objects.all()

    return render(
        request,
        "inputUS/upload_US.html",
        {"form": upload_US_File, "upload_user_story": upload_user_story},
    )


def show_uploaded_UserStory(request):

    # show table US_File_Upload
    upload_user_story = US_Upload.objects.all()

    return render(
        request,
        "inputUS/see_uploaded_US.html",
        {"upload_user_story": upload_user_story},
    )

def del_Upload_US(request, id):
    
    delete_user_story = get_object_or_404(US_Upload, pk=id)

    if delete_user_story:
        delete_segmented_US = UserStory_element.objects.filter(
            UserStory_File_ID=delete_user_story 
        )

        delete_user_story.delete()
        delete_segmented_US.delete()
        # delete_atomic.delete()

        messages.success(request, "User story have been successfully deleted")

        update_user_story = US_Upload.objects.all()
        return render(
            request,
            "inputUS/see_uploaded_US.html",
            {"update_user_story": update_user_story},
        )


def split_user_story_to_segment(request, id):

    retrieve_UserStory_data = get_object_or_404(US_Upload, pk=id)

    segmentation(retrieve_UserStory_data.id)

    messages.success(request, "User stories have been successfully splitted")

    see_splitted_user_stories = UserStory_element.objects.all()

    return render(
        request,
        "inputUS/preprocessed_US.html",
        {"see_splitted_user_stories": see_splitted_user_stories},
    )

def show_splitted_UserStory(request):
    # show table user story
    project = request.GET.get('project', None)
    userstory_list = UserStory_element.objects.filter(is_processed=False).order_by('-id')
    extra_context = {
        "view_all": userstory_list,
        "project_list": Project.objects.all()
    }
    if project:
        userstory_list = userstory_list.filter(Project_Name_id=project)
        extra_context.update({
            "view_all": userstory_list,
            "project_id": int(project)
        })

    return render(request, "inputUS/see_splitted_US1.html", extra_context)


def analyze_data(request):
    from functions.analysis_userstory import AnalysisData
    data_list_id = request.POST.getlist("userstory_id", [])
    
    if len(data_list_id) < 2:
        # jika user story hanya dipilih hanya 1 akan muncul message
        messages.warning(
            request,
            "Warning, please select more than 1 user story !",
        )
        return redirect(reverse('show_splitted_UserStory'))

    AnalysisData(data_list_id).start()
    messages.success(
        request,
        "User stories have been successfully analyzed. The list of user stories with potential ambiguities have been updated !",
    )
    
    return redirect(reverse('show_splitted_UserStory'))
    

def see_wellformed(request):
    project = request.GET.get('project', None)
    wellformed_list = Result.objects.filter(
        result_desc__icontains="has been achieved",
    )

    extra_context = {
        "view_all": wellformed_list,
        "project_list": Project.objects.all()
    }

    if project:
        wellformed_list = wellformed_list.filter(UserStory_Segment_ID__Project_Name_id=project)
        extra_context.update({
            "view_all": wellformed_list,
            "project_id": int(project)
        })
    return render(request, "inputUS/see_well_formed_US.html", extra_context)


def view_report_userstory_list(request):
    extra_context = {
        'project_list': Project.objects.all(),
    }
    project_id = request.GET.get('project_id', None)
    if project_id:
        userstory_list = UserStory_element.objects.filter(Project_Name_id=project_id, is_processed=True)
        # report_list = ReportUserStory.objects.filter(userstory__Project_Name_id=project_id).order_by('userstory', 'id')
        extra_context.update({
            'userstory_list': userstory_list,
            'project_id': int(project_id)
        })
    
    return render(request, "inputUS/report_userstory_list.html", extra_context)

def edit_userstory(request, userstory_id):
    userstory = get_object_or_404(UserStory_element, id=userstory_id)
    extra_context = {
        'userstory': userstory
    }

    if request.POST:
        text_story = request.POST.get('userstory', None)
        if text_story:
            userstory.UserStory_Full_Text = text_story
            userstory.is_processed = False
            userstory.save()
            segmentation_edit_userstory(userstory_id)

            if userstory.get_report_list().exists():
                # delete data report
                userstory.get_report_list().delete()
            
            messages.success(request, "Success update userstory.")
            return redirect(reverse('report_userstory_list')+"?project_id="+str(userstory.Project_Name_id))
    return render(request, "inputUS/edit_userstory.html", extra_context)


# def see_precise(request):

#     precise_db = WordNet_classification.objects.all()

#     paginator = Paginator(precise_db, 5)
#     page = request.GET.get("page", 1)
#     view_all = paginator.get_page(page)
#     extra_context = {
#         "view_all": view_all,
#         "current": view_all.number,
#         "has_next": view_all.has_next(),
#         "has_previous": view_all.has_previous(),
#         "page_next": int(page) + 1 if view_all.has_next() else None,
#         "page_previous": int(page) - 1 if view_all.has_previous() else None,
#         "list_pagination": list(
#             view_all.paginator.get_elided_page_range(page, on_each_side=1)
#         ),
#         "active_page": int(page),
#     }

#     return render(request, "importUS/see_precise_US.html", extra_context)


# def see_explicit(request):

#     explicit_db = TopicModeling.objects.all()

#     paginator = Paginator(explicit_db, 5)
#     page = request.GET.get("page", 1)
#     view_all = paginator.get_page(page)
#     extra_context = {
#         "view_all": view_all,
#         "current": view_all.number,
#         "has_next": view_all.has_next(),
#         "has_previous": view_all.has_previous(),
#         "page_next": int(page) + 1 if view_all.has_next() else None,
#         "page_previous": int(page) - 1 if view_all.has_previous() else None,
#         "list_pagination": list(
#             view_all.paginator.get_elided_page_range(page, on_each_side=1)
#         ),
#         "active_page": int(page),
#     }

#     return render(request, "importUS/see_explicit_US.html", extra_context)


# def get_list_parsing_detail_json(request):
#     '''
#         function untuk mendapatkan daftar improvement dengan parameter parser
#     '''
#     response = {'success': False, 'message': 'parsing detail not found'}
#     parser_id = request.GET.get('id', None)
#     if parser_id:
#         try:
#             parser_obj = Parser.objects.get(id=parser_id)
#         except Parser.DoesNotExist:
#             pass
#         else:
#             data = []
#             parsing_list = parser_obj.parsingdetail_set.all()
#             if parsing_list.exists():
#                 for item in parsing_list:
#                     data.append({
#                         'id': item.id,
#                         'text': item.Text_improvement,
#                         'is_selected': item.is_selected
#                     })
#                 response = {'success': True, 'data': data, 'is_lock': parser_obj.is_lock}
#     return JsonResponse(response)

# def set_or_unset_selected_improvement(request):
#     response = {'success': False, 'message': 'parsing detail not found'}
#     parsing_id = request.POST.get('id', None)
#     is_selected_value = request.POST.get('is_selected', None)
#     is_selected = False
#     if is_selected_value == 'true':
#         is_selected = True
        
#     if parsing_id:
#         try:
#             parsing_obj = ParsingDetail.objects.get(id=parsing_id)
#         except ParsingDetail.DoesNotExist:
#             pass
#         else:
#             parsing_obj.is_selected = is_selected
#             parsing_obj.save()
#             response = {'success': True, 'message': 'Success'}
#     return JsonResponse(response)

# def save_improvement(request):
#     response = {'success': False, 'message': 'parsing detail not found'}
#     parser_id = request.POST.get('id', None)
#     is_manual_value = request.POST.get('is_manual', None)
#     value = request.POST.get('value', None)
#     is_manual = False
#     if is_manual_value == 'true':
#         is_manual = True
#     if parser_id:
#         try:
#             parser_obj = Parser.objects.get(id=parser_id)
#         except Parser.DoesNotExist:
#             pass
#         else:
#             if is_manual:
#                 ParsingDetail.objects.create(
#                     is_manual=True,
#                     is_selected=True,
#                     Text_improvement=value,
#                     Parsing_ID_fk=parser_obj
#                 )
#             parser_obj.is_lock = True
#             parser_obj.save()
#             response = {'success': True, 'message': 'Success save'}
#     return JsonResponse(response)