import re

from django.contrib import messages
from django.contrib.auth.decorators import login_required

# from django.http import JsonResponse
# from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy

from functions.segmentation import segmentation, segmentation_edit_userstory

from .forms import InputUserStory_Form
from .models import (
    Glossary,
    KeywordGlossary,
    Project,
    ProcessBackground,
    ReportUserStory,
    Result,
    Role,
    US_Upload,
    UserStory_element,
)
from .tasks import task_process_analys_data

# from functions.well_formed import well_formed_an
# from functions.analysis import well_formed_an, stat_preciseness


@login_required(login_url=reverse_lazy("login_"))
def Upload_UserStory(request):
    if request.method == "POST":
        upload_US_File = InputUserStory_Form(request.POST, request.FILES, user=request.user)
        readFile = request.FILES["US_File_Txt"]
        readLine = readFile.readlines()

        File_content = []

        for line in readLine:
            # print('readLine', readLine)
            # decode bytes to string
            # newLine = line.decode("utf-8")
            newLine = line.decode("unicode_escape")
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
            upload_user_story.created_by = request.user
            upload_user_story.US_Project_Domain = Project_Name
            upload_user_story.US_File_Name = File_Name
            upload_user_story.US_File_Txt = File_text
            upload_user_story.US_File_Content = File_content

            upload_user_story.save()

            messages.success(
                request, "New set of user stories have been successfully added"
            )
            # upload_user_story = InputUserStory_Form()
            # return render(
            #     request,
            #     "inputUS/upload_US.html",
            #     {"form": upload_US_File, "upload_user_story": upload_user_story},
            # )
            return redirect(reverse("show_UserStory"))
        else:
            return redirect("/")
    else:
        upload_US_File = InputUserStory_Form(user=request.user)
        upload_user_story = US_Upload.objects.all()

    return render(
        request,
        "inputUS/upload_US.html",
        {"form": upload_US_File, "upload_user_story": upload_user_story},
    )


@login_required(login_url=reverse_lazy("login_"))
def show_uploaded_UserStory(request):
    # show table US_File_Upload
    upload_user_story = US_Upload.objects.all()
    if not request.user.is_superuser:
        upload_user_story = upload_user_story.filter(created_by=request.user)

    return render(
        request,
        "inputUS/see_uploaded_US.html",
        {"upload_user_story": upload_user_story},
    )


def del_Upload_US(request, id):
    delete_user_story = get_object_or_404(US_Upload, pk=id)

    # if delete_user_story:
    delete_segmented_US = UserStory_element.objects.filter(
        UserStory_File_ID=delete_user_story
    )
    delete_user_story.delete()
    delete_segmented_US.delete()

        # delete_atomic.delete()

    messages.success(request, "User story have been successfully deleted")
    return redirect(reverse('show_UserStory'))

    # update_user_story = US_Upload.objects.all()
    # return render(
    #     request,
    #     "inputUS/see_uploaded_US.html",
    #     {"update_user_story": update_user_story},
    # )


@login_required(login_url=reverse_lazy("login_"))
def split_user_story_to_segment(request, id):
    retrieve_UserStory_data = get_object_or_404(US_Upload, pk=id)
    segmentation(retrieve_UserStory_data.id)
    messages.success(request, "User stories have been successfully splitted")
    see_splitted_user_stories = UserStory_element.objects.all()
    if retrieve_UserStory_data.US_Project_Domain:
        see_splitted_user_stories = see_splitted_user_stories.filter(
            Project_Name=retrieve_UserStory_data.US_Project_Domain
        )

    return render(
        request,
        "inputUS/preprocessed_US.html",
        {"see_splitted_user_stories": see_splitted_user_stories},
    )


@login_required(login_url=reverse_lazy("login_"))
def show_splitted_UserStory(request):
    # show table user story
    project = request.GET.get("project", None)
    userstory_list = UserStory_element.objects.filter(is_processed=False).order_by(
        "-id"
    )

    if not request.user.is_superuser:
        userstory_list = userstory_list.filter(created_by=request.user)
    extra_context = {"view_all": userstory_list, "project_list": Project.objects.all()}
    if project:
        userstory_list = userstory_list.filter(Project_Name_id=project)
        extra_context.update({"view_all": userstory_list, "project_id": int(project)})

    return render(request, "inputUS/see_splitted_US1.html", extra_context)


@login_required(login_url=reverse_lazy("login_"))
def analyze_data(request):
    from functions.analysis_userstory import AnalysisData
    import gc
    import torch
    gc.collect()
    torch.cuda.empty_cache()

    (
        eps_value,
        min_samples_value,
        terms_role_value,
        terms_action_value,
        topics_value,
        similarity_value,
    ) = (0.5, 2, 5, 7, 10, None)
    eps_checkbox = request.POST.get("eps_checkbox", None)
    if eps_checkbox == "on":
        eps_value = request.POST.get("eps_value", None)

    min_samples_checkbox = request.POST.get("min_samples_checkbox", None)
    if min_samples_checkbox == "on":
        min_samples_value = request.POST.get("min_samples_value", None)

    terms_role_checkbox = request.POST.get("terms_role_checkbox", None)
    if terms_role_checkbox == "on":
        terms_role_value = request.POST.get("terms_role_value", None)

    terms_action_checkbox = request.POST.get("terms_action_checkbox", None)
    if terms_action_checkbox == "on":
        terms_action_value = request.POST.get("terms_action_value", None)

    topics_checkbox = request.POST.get("topics_checkbox", None)
    if topics_checkbox == "on":
        topics_value = request.POST.get("topics_value", None)

    similarity_checkbox = request.POST.get("similarity_checkbox", None)
    if similarity_checkbox == "on":
        similarity_value = request.POST.get("similarity_value", None)

    all_in_project = request.POST.get('all_in_project', None)
    if all_in_project == "on":
        project_id = request.POST.get('project', None)
        project = get_object_or_404(Project, id=project_id)
        userstory_list = UserStory_element.objects.filter(Project_Name=project).values_list('id', flat=True)
        story_list_id = list(set(userstory_list))

        process_obj = ProcessBackground.objects.create(
            created_by=request.user,
            eps_value=eps_value,
            min_samples_value=min_samples_value,
            terms_role_value=terms_role_value,
            terms_action_value=terms_action_value,
            topics_value=topics_value,
            similarity_value=similarity_value,
        )
        process_obj.userstorys.add(*story_list_id)
        process_obj.save()
        task_process_analys_data.delay(process_obj.id)
        # AnalysisData(
        #     story_list_id,
        #     eps_value,
        #     min_samples_value,
        #     terms_role_value,
        #     terms_action_value,
        #     topics_value,
        #     similarity_value,
        #     request.user,
        # ).start()
        messages.success(
            request,
            "User stories have been successfully analyzed. The list of user stories with potential ambiguities have been updated !",
        )
        return redirect(reverse("view_process_background"))
    else:
        data_list_id = request.POST.getlist("userstory_id", [])

        if len(data_list_id) < 2:
            # jika user story hanya dipilih hanya 1 akan muncul message
            messages.warning(
                request,
                "Warning, please select more than 1 user story !",
            )
            return redirect(reverse("show_splitted_UserStory"))

        # print(
        #     eps_value,
        #     min_samples_value,
        #     terms_role_value,
        #     terms_action_value,
        #     topics_value,
        #     similarity_value,
        # )

        AnalysisData(
            data_list_id,
            eps_value,
            min_samples_value,
            terms_role_value,
            terms_action_value,
            topics_value,
            similarity_value,
            request.user,
        ).start()
        messages.success(
            request,
            "User stories have been successfully analyzed. The list of user stories with potential ambiguities have been updated !",
        )

    return redirect(reverse("show_splitted_UserStory"))


@login_required(login_url=reverse_lazy("login_"))
def see_wellformed(request):
    project = request.GET.get("project", None)
    wellformed_list = Result.objects.filter(
        result_desc__icontains="has been achieved",
    )

    extra_context = {"view_all": wellformed_list, "project_list": Project.objects.all()}

    if project:
        wellformed_list = wellformed_list.filter(
            UserStory_Segment_ID__Project_Name_id=project
        )
        extra_context.update({"view_all": wellformed_list, "project_id": int(project)})
    return render(request, "inputUS/see_well_formed_US.html", extra_context)


@login_required(login_url=reverse_lazy("login_"))
def view_report_userstory_list(request):
    potential_problem_list = (
        (0, "None"),
        (1, "Vagueness"),
        (2, "Inconsistency"),
        (3, "Insufficiency"),
        (4, "Duplication"),
    )
    status_list = (
        (0, "All"),
        (1, "Potentially Ambiguous"),
        (2, "Good Quality"),
    )

    project_list = Project.objects.all()
    if not request.user.is_superuser:
        project_list = project_list.filter(created_by=request.user)

    extra_context = {
        "project_list": project_list,
        "potential_problem_list": potential_problem_list,
        "analyze_type": ReportUserStory.ANALYS_TYPE.choices,
        "status_list": status_list,
    }
    project_id = request.GET.get("project_id", None)
    # status = request.GET.get('status', None)
    if project_id:
        userstory_list = UserStory_element.objects.filter(
            Project_Name_id=project_id, is_processed=True
        )

        if not request.user.is_superuser:
            userstory_list = userstory_list.filter(created_by=request.user)
        type_value = request.GET.get("type", None)
        potential_problem_value = request.GET.get("potential_problem", None)
        search = request.GET.get("q", None)
        if search:
            userstory_list = userstory_list.filter(
                UserStory_Full_Text__icontains=search
            )

        if type_value:
            type_value = int(type_value)
        if not type_value and not potential_problem_value:
            extra_context.update({"status_list": ((1, "Potentially Ambiguous"),)})
        elif not type_value and potential_problem_value == "0":
            extra_context.update({"status_list": ((2, "Good Quality"),)})
        elif type_value in [
            ReportUserStory.ANALYS_TYPE.WELL_FORMED,
            ReportUserStory.ANALYS_TYPE.PRECISE,
        ]:
            extra_context.update({"potential_problem_list": ((1, "Vagueness"),)})
        elif type_value in [
            ReportUserStory.ANALYS_TYPE.CONSISTENT,
            ReportUserStory.ANALYS_TYPE.ATOMICITY,
            ReportUserStory.ANALYS_TYPE.CONCEPTUALLY,
        ]:
            extra_context.update(
                {
                    "potential_problem_list": (
                        (2, "Inconsistency"),
                        (3, "Insufficiency"),
                    )
                }
            )
        elif type_value in [ReportUserStory.ANALYS_TYPE.UNIQUENESS]:
            extra_context.update({"potential_problem_list": ((4, "Duplication"),)})

        extra_context.update(
            {
                "userstory_list": userstory_list,
                "project_id": int(project_id),
                "type": int(request.GET.get("type", None))
                if request.GET.get("type", None)
                else None,
                "status": int(request.GET.get("status", None))
                if request.GET.get("status", None)
                else None,
                "potential_problem": int(request.GET.get("potential_problem", None))
                if request.GET.get("potential_problem", None)
                else None,
            }
        )

    return render(request, "inputUS/report_userstory_list.html", extra_context)


@login_required(login_url=reverse_lazy("login_"))
def edit_userstory(request, userstory_id):
    userstory = get_object_or_404(UserStory_element, id=userstory_id)
    improved_terms_show = False
    type = request.GET.get("type", None)
    status = request.GET.get("status", None)

    path_url = request.get_full_path().split("?")

    extra_context = {}

    if type:
        type = int(type)

    if status:
        status = int(status)

    if (
        type
        in [
            ReportUserStory.ANALYS_TYPE.PRECISE,
            ReportUserStory.ANALYS_TYPE.CONSISTENT,
            ReportUserStory.ANALYS_TYPE.CONCEPTUALLY,
        ]
        and status == 1
    ):
        improved_terms_show = True
        role_list = Role.objects.filter(userstory__Project_Name=userstory.Project_Name)
        extra_context.update(
            {
                "role_list": role_list,
                "keywords": KeywordGlossary.objects.all(),
                "glossarys": Glossary.objects.all(),
            }
        )

        if type == ReportUserStory.ANALYS_TYPE.PRECISE:
            reportterms = userstory.reportterms_set.filter(
                type=ReportUserStory.ANALYS_TYPE.PRECISE
            )
            if reportterms.exists():
                extra_context.update({"reportterms": reportterms.last()})
            # ReportTerms.objects.filter()
        elif type == ReportUserStory.ANALYS_TYPE.CONCEPTUALLY:
            reportterms = userstory.reportterms_set.filter(
                type=ReportUserStory.ANALYS_TYPE.CONCEPTUALLY
            )
            if reportterms.exists():
                extra_context.update({"reportterms": reportterms.last()})

    extra_context.update(
        {"userstory": userstory, "improved_terms_show": improved_terms_show}
    )

    if request.POST:
        # text_story = request.POST.get("userstory", None)
        userstory_list = request.POST.getlist("userstory_list[]", [])
        # print(text_story)
        # print(userstory_list)
        # if text_story:
        #     userstory.UserStory_Full_Text = text_story
            
        if len(userstory_list):
            # userstory.is_processed = False
            # userstory.save()

            # segmentation_edit_userstory(userstory_id)
            if userstory.get_report_list().exists():
                # delete data report
                userstory.get_report_list().delete()

            if len(userstory_list):
                for item in userstory_list:
                    if item:
                        userstory_child = UserStory_element.objects.create(
                            UserStory_Full_Text=item,
                            Project_Name=userstory.Project_Name,
                            parent=userstory,
                        )
                        segmentation_edit_userstory(userstory_child.id, True)

            messages.success(request, "Success update userstory.")
            return redirect(
                reverse("report_userstory_list") + f"?{path_url[1]}"
                if len(path_url) > 1
                else ""
            )
        else:
            is_edit = False
            problematic_role = request.POST.get("problematic_role", None)
            improved_role = request.POST.get("improved_role", None)
            # print(problematic_role, improved_role)
            if problematic_role and improved_role:
                old_text = userstory.UserStory_Full_Text
                textstory = userstory.UserStory_Full_Text.replace(
                    problematic_role, improved_role
                )
                userstory.UserStory_Full_Text = textstory
                userstory.old_userstory = old_text
                userstory.save()
                is_edit = True

            problematic_action = request.POST.get("problematic_action", None)
            improved_action = request.POST.get("improved_action", None)
            # print(problematic_action, improved_action)
            if problematic_action and improved_action:
                glosasry_obj, created = Glossary.objects.get_or_create(
                    Action_item=problematic_action
                )

                keyword_obj, created = KeywordGlossary.objects.get_or_create(
                    keyword=improved_action
                )
                keyword_obj.item_name.add(glosasry_obj)
                keyword_obj.save()
                is_edit = True

            if is_edit:
                userstory.is_processed = False
                userstory.save()
                segmentation_edit_userstory(userstory_id)
                if userstory.get_report_list().exists():
                    # delete data report
                    userstory.get_report_list().delete()
                messages.success(request, "Success update userstory.")
                return redirect(
                    reverse("report_userstory_list") + f"?{path_url[1]}"
                    if len(path_url) > 1
                    else ""
                )
    return render(request, "inputUS/edit_userstory.html", extra_context)


@login_required(login_url=reverse_lazy("login_"))
def add_userstory(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    extra_context = {"project": project}
    if request.POST:
        userstory_list = request.POST.getlist("userstory[]", [])

        if userstory_list:
            for item in userstory_list:
                if item and item != "":
                    userstory = UserStory_element.objects.create(
                        UserStory_Full_Text=item,
                        Project_Name=project,
                    )
                    segmentation_edit_userstory(userstory.id, True)
            messages.success(request, "Success add userstory.")
    return render(request, "inputUS/add_userstory.html", extra_context)


@login_required(login_url=reverse_lazy("login_"))
def view_list_project(request):
    projects = Project.objects.all()
    if not request.user.is_superuser:
        projects = projects.filter(created_by=request.user)
    extra_context = {"projects": projects}
    return render(request, "inputUS/project/view.html", extra_context)


@login_required(login_url=reverse_lazy("login_"))
def view_add_project(request):
    extra_context = {}

    if request.POST:
        project_name = request.POST.get("project_name", None)
        project_description = request.POST.get("project_description", None)
        if project_name:
            Project.objects.create(
                Project_Name=project_name,
                Project_Desc=project_description,
                created_by=request.user,
            )
            messages.success(request, "Success add project.")
            return redirect(reverse("projects_list_view"))
    return render(request, "inputUS/project/add.html", extra_context)


@login_required(login_url=reverse_lazy("login_"))
def view_edit_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    extra_context = {"project": project}
    if request.POST:
        project_name = request.POST.get("project_name", None)
        project_description = request.POST.get("project_description", None)
        if project_name:
            project.Project_Name = project_name
            project.Project_Desc = project_description
            project.save()
            messages.success(request, "Success update project.")
            return redirect(reverse("projects_list_view"))
    return render(request, "inputUS/project/edit.html", extra_context)


@login_required(login_url=reverse_lazy("login_"))
def view_delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if project:
        project.delete()
        messages.success(request, "Success delete project.")
    return redirect(reverse("projects_list_view"))


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
def print_report(request):
    project_id = request.GET.get("project_id", None)
    project = get_object_or_404(Project, pk=project_id)
    extra_context = {}
    if project_id:
        userstory_list = UserStory_element.objects.filter(
            Project_Name_id=project_id, is_processed=True
        )
        extra_context.update(
            {
                "userstory_list": userstory_list,
                "project": project,
                "type": request.GET.get("type", None)
                if request.GET.get("type", None)
                else None,
                "status": request.GET.get("status", None)
                if request.GET.get("status", None)
                else None,
                "analyze_type": ReportUserStory.ANALYS_TYPE.choices,
            }
        )
    return render(request, "inputUS/report/userstory.html", extra_context)


@login_required(login_url=reverse_lazy("login_"))
def view_list_keyword(request):
    keyword_list = KeywordGlossary.objects.all()
    return render(
        request,
        "inputUS/keyword/view.html",
        {"title": "Keyword", "keyword_list": keyword_list},
    )

@login_required(login_url=reverse_lazy("login_"))
def view_list_processbackground(request):
    process = ProcessBackground.objects.all()
    return render(
        request,
        "inputUS/background/view.html",
        {'process': process, 'title': 'Process Background User Stories'}
    )