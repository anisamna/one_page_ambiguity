import re

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic.base import TemplateView

from functions.segmentation import segmentation, segmentation_edit_userstory

from .forms import InputUserStory_Form
from .models import (AdjustedUserStory, Glossary, KeywordGlossary,
                     NameFileUsed, Personas, ProcessBackground, Project,
                     ReportUserStory, Result, Role, US_Upload,
                     UserStory_element)

# from .tasks import task_process_analys_data

# from functions.well_formed import well_formed_an
# from functions.analysis import well_formed_an, stat_preciseness


class AddSingleUserStory(TemplateView):
    template_name = "inputUS/userstory/add.html"
    project_list = Project.objects.all()
    upload_list = US_Upload.objects.all()

    def get(self, request):
        return render(
            request,
            self.template_name,
            {
                "title": "Add User Story",
                "projects": self.project_list,
                "uploads": self.upload_list,
            },
        )

    def post(self, request):
        project = request.POST.get("project", None)
        file = request.POST.get("file", None)
        custom_file = request.POST.get("custom_file", None)
        input_custom_file = request.POST.get("input_custom_file", None)
        userstory = request.POST.get("userstory", None)
        user = request.user

        if userstory and project:
            userstory_obj = UserStory_element.objects.create(
                Project_Name_id=project,
                UserStory_Full_Text=userstory,
                created_by=user
            )
            if custom_file == "on":
                us_upload_obj, created = US_Upload.objects.get_or_create(
                    US_Project_Domain_id=project,
                    US_File_Name=input_custom_file,
                    US_File_Content={},
                    is_show=False,
                    created_by=user,
                )
                userstory_obj.UserStory_File_ID = us_upload_obj
            else:
                userstory_obj.UserStory_File_ID_id = file
            userstory_obj.save()

            if userstory_obj.UserStory_File_ID:
                file_obj, created = NameFileUsed.objects.get_or_create(
                    name_file=userstory_obj.UserStory_File_ID,
                    created_by=userstory_obj.created_by,
                )
                file_obj.is_active = True
                file_obj.save()
            segmentation_edit_userstory(userstory_obj.id, True)
            messages.success(request, "Success, add new user story")
            return redirect(reverse_lazy("show_splitted_UserStory"))

        return redirect(reverse_lazy("add_single_userstory"))


@login_required(login_url=reverse_lazy("login_"))
def Upload_UserStory(request):
    if request.method == "POST":
        upload_US_File = InputUserStory_Form(
            request.POST, request.FILES, user=request.user
        )
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

            file_obj, created = NameFileUsed.objects.get_or_create(
                name_file=upload_user_story, created_by=request.user
            )
            file_obj.is_active = True
            file_obj.save()

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
    upload_user_story = US_Upload.objects.filter(is_show=True)
    if not request.user.is_superuser:
        upload_user_story = upload_user_story.filter(created_by=request.user)

    return render(
        request,
        "inputUS/see_uploaded_US.html",
        {"upload_user_story": upload_user_story, "title": "Preprocessing"},
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
    return redirect(reverse("show_UserStory"))

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
    # messages.success(request, "User stories have been successfully splitted")
    messages.success(request, "User stories have been successfully preprocessed")
    return redirect(reverse("show_splitted_UserStory"))
    # see_splitted_user_stories = UserStory_element.objects.all()
    # if retrieve_UserStory_data.US_Project_Domain:
    #     see_splitted_user_stories = see_splitted_user_stories.filter(
    #         Project_Name=retrieve_UserStory_data.US_Project_Domain
    #     )

    # return render(
    #     request,
    #     "inputUS/preprocessed_US.html",
    #     {"see_splitted_user_stories": see_splitted_user_stories},
    # )


@login_required(login_url=reverse_lazy("login_"))
def show_splitted_UserStory(request):
    # show table user story
    project = request.GET.get("project", None)
    file_name_id = request.GET.get("filename", None)
    userstory_list = UserStory_element.objects.filter(is_processed=False)

    if not request.user.is_superuser:
        userstory_list = userstory_list.filter(created_by=request.user)

    file_used_list = NameFileUsed.objects.filter(
        created_by=request.user, is_active=True
    )
    if file_used_list.exists():
        file_used_list_id = file_used_list.values_list("name_file__id", flat=True)
        userstory_list = userstory_list.filter(
            UserStory_File_ID__in=list(file_used_list_id)
        )
    else:
        userstory_list = UserStory_element.objects.none()
    
    project_list = Project.objects.all()
    if not request.user.is_superuser:
        project_list = project_list.filter(created_by=request.user)

    extra_context = {
        "view_all": userstory_list.order_by("-id"),
        "project_list": project_list,
    }
    if project:
        file_names = US_Upload.objects.filter(US_Project_Domain_id=project, created_by=request.user)
        if file_name_id:
            extra_context.update({"file_name_id": int(file_name_id)})
            userstory_list = userstory_list.filter(
                Project_Name_id=project, UserStory_File_ID=file_name_id
            )
        extra_context.update(
            {
                "view_all": userstory_list,
                "project_id": int(project),
                "file_names": file_names,
            }
        )
    return render(request, "inputUS/see_splitted_US1.html", extra_context)


@login_required(login_url=reverse_lazy("login_"))
def analyze_data(request):
    import gc

    import torch

    from functions.analysis_userstory import AnalysisData

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

    (
        is_preciseness,
        is_well_formedness,
        is_conciseness,
        is_atomicity,
        is_conceptually_sound,
        is_uniqueness,
    ) = (False, False, False, False, False, False)
    preciseness_checkbox = request.POST.get("preciseness_checkbox", None)
    if preciseness_checkbox == "on":
        is_preciseness = True
        preciseness_input = request.POST.get("preciseness_input", None)
        if preciseness_input:
            eps_value = preciseness_input

    well_formedness_checkbox = request.POST.get("well_formedness_checkbox", None)
    if well_formedness_checkbox == "on":
        is_well_formedness = True

    conciseness_checkbox = request.POST.get("conciseness_checkbox", None)
    if conciseness_checkbox == "on":
        is_conciseness = True

    atomicity_checkbox = request.POST.get("atomicity_checkbox", None)
    if atomicity_checkbox == "on":
        is_atomicity = True

    conceptually_sound_checkbox = request.POST.get("conceptually_sound_checkbox", None)
    if conceptually_sound_checkbox == "on":
        is_conceptually_sound = True
        conceptually_sound_input = request.POST.get("conceptually_sound_input", None)
        if conceptually_sound_input:
            topics_value = conceptually_sound_input

    uniqueness_checkbox = request.POST.get("uniqueness_checkbox", None)
    if uniqueness_checkbox == "on":
        is_uniqueness = True
        uniqueness_input = request.POST.get("uniqueness_input", None)
        if uniqueness_input:
            similarity_value = uniqueness_input

    if (
        preciseness_checkbox != "on"
        and well_formedness_checkbox != "on"
        and conciseness_checkbox != "on"
        and atomicity_checkbox != "on"
        and conceptually_sound_checkbox != "on"
        and uniqueness_checkbox != "on"
    ):
        messages.warning(
            request,
            "Warning! Select at least one assessment criteria.",
        )
        return redirect(reverse("show_splitted_UserStory"))

    all_in_project = request.POST.get("all_in_project", None)
    if all_in_project == "on":
        # NOTE: process all user stories on the project
        project_id = request.POST.get("project", None)
        project = get_object_or_404(Project, id=project_id)
        userstory_list = UserStory_element.objects.filter(
            Project_Name=project
        ).values_list("id", flat=True)
        story_list_id = list(set(userstory_list))
        AnalysisData(
            story_list_id,
            eps_value,
            min_samples_value,
            terms_role_value,
            terms_action_value,
            topics_value,
            similarity_value,
            request.user,
        ).start(
            is_preciseness,
            is_well_formedness,
            is_conciseness,
            is_atomicity,
            is_conceptually_sound,
            is_uniqueness,
        )
        messages.success(
            request,
            "User stories have been successfully analyzed. The list of user stories with potential ambiguities have been updated !",
        )
        return redirect(f"{reverse('report_userstory_list')}?project_id={project_id}&filename_id=&type=&potential_problem=&status=1&q=")
        # return redirect(reverse("view_process_background"))
    else:
        data_list_id = request.POST.getlist("userstory_id", [])

        if len(data_list_id) < 2:
            # jika user story hanya dipilih hanya 1 akan muncul message
            messages.warning(
                request,
                "Warning, please select more than 1 user story !",
            )
            return redirect(reverse("show_splitted_UserStory"))

        userstory_list = UserStory_element.objects.filter(
            id__in=data_list_id
        ).values_list("id", flat=True)
        story_list_id = list(set(userstory_list))

        # process_obj = ProcessBackground.objects.create(
        #     created_by=request.user,
        #     eps_value=eps_value,
        #     min_samples_value=min_samples_value,
        #     terms_role_value=terms_role_value,
        #     terms_action_value=terms_action_value,
        #     topics_value=topics_value,
        #     similarity_value=similarity_value,
        # )
        # process_obj.userstorys.add(*story_list_id)
        # process_obj.save()
        # task_process_analys_data.delay(process_obj.id)
        AnalysisData(
            data_list_id,
            eps_value,
            min_samples_value,
            terms_role_value,
            terms_action_value,
            topics_value,
            similarity_value,
            request.user,
        ).start(
            is_preciseness,
            is_well_formedness,
            is_conciseness,
            is_atomicity,
            is_conceptually_sound,
            is_uniqueness,
        )
        messages.success(
            request,
            "User stories have been successfully analyzed. The list of user stories with potential ambiguities have been updated !",
        )
        return redirect(f"{reverse('report_userstory_list')}")

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
        (5, "No Selection"),
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

    analys_type_choices = ReportUserStory.ANALYS_TYPE.choices
    del analys_type_choices[4]

    extra_context = {
        "project_list": project_list,
        "potential_problem_list": potential_problem_list,
        "analyze_type": analys_type_choices,
        "status_list": status_list,
    }
    project_id = request.GET.get("project_id", None)
    filename_id = request.GET.get("filename_id", None)
    # status = request.GET.get('status', None)
    if project_id:
        userstory_list = UserStory_element.objects.filter(
            Project_Name_id=project_id, is_processed=True
        )
        if filename_id:
            userstory_list = userstory_list.filter(
                UserStory_File_ID_id=filename_id
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
        elif not type_value and potential_problem_value == "5":
            pass
        if type_value in [
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

        filename_list = US_Upload.objects.filter(
            US_Project_Domain_id=project_id,
            is_show=True
        )
        if not request.user.is_superuser:
            filename_list = filename_list.filter(
                created_by=request.user
            )

        file_used_list = NameFileUsed.objects.filter(
            created_by=request.user, is_active=True
        )
        if file_used_list.exists():
            file_used_list_id = file_used_list.values_list("name_file__id", flat=True)
            userstory_list = userstory_list.filter(
                UserStory_File_ID__in=list(file_used_list_id)
            )
        report = ReportUserStory.objects.filter(userstory__in=userstory_list)
        if type_value:
            report = report.filter(type=int(type_value))

        agree = report.filter(is_submited=True, is_agree=True).count()
        disagree = report.filter(is_submited=True, is_agree=False).count()
        try:
            agree_count = (agree/userstory_list.count())*100
        except Exception:
            agree_count = 0

        try:
            disagree_count = (disagree/userstory_list.count())*100
        except Exception:
            disagree_count = 0
        extra_context.update(
            {
                "userstory_list": userstory_list,
                "project_id": int(project_id),
                "filename_list": filename_list,
                "agree_count": round(agree_count, 2),
                "disagree_count": round(disagree_count, 2),
                "type": int(request.GET.get("type", None))
                if request.GET.get("type", None)
                else None,
                "status": int(request.GET.get("status", None))
                if request.GET.get("status", None)
                else None,
                "filename_id": int(request.GET.get("filename_id"))
                if request.GET.get("filename_id", None)
                else None,
                "potential_problem": int(request.GET.get("potential_problem", None))
                if request.GET.get("potential_problem", None)
                else None,
            }
        )

    return render(request, "inputUS/report_userstory_list.html", extra_context)


@login_required(login_url=reverse_lazy("login_"))
def edit_userstory(request, report_id):
    reportuserstory = get_object_or_404(ReportUserStory, id=report_id)
    userstory = reportuserstory.userstory
    improved_terms_show = False
    status = request.GET.get("status", None)
    path_url = request.get_full_path().split("?")
    extra_context = {"title": f"Change Userstory: {userstory.UserStory_Full_Text}"}

    # type = request.GET.get("type", None)
    # if type:
    #     type = int(type)

    # reportuserstory = userstory.reportuserstory_set.filter(type=type)
    # if reportuserstory.exists():
    #     reportuserstory = reportuserstory.last()
    is_edit_role = False
    is_edit_action = False
    if reportuserstory.recommendation_type:
        # print("recommendation_type", reportuserstory.recommendation_type)
        is_edit_role = reportuserstory.recommendation_type in [
            ReportUserStory.RECOMENDATION_TYPE.ROLE,
            ReportUserStory.RECOMENDATION_TYPE.ACTION_ROLE,
        ]
        is_edit_action = reportuserstory.recommendation_type in [
            ReportUserStory.RECOMENDATION_TYPE.ACTION,
            ReportUserStory.RECOMENDATION_TYPE.ACTION_ROLE,
            ReportUserStory.RECOMENDATION_TYPE.ACTION_MANUAL,
        ]
    else:
        extra_context.update(
            {
                "role_custom_list": Role.objects.filter(
                    userstory__Project_Name=userstory.Project_Name
                ).distinct("role_key"),
                "keyword_custom_list": KeywordGlossary.objects.all(),
                "glossary_custom_list": Glossary.objects.all(),
            }
        )
    extra_context.update(
        {
            "reportuserstory": reportuserstory,
            "is_edit_role": is_edit_role,
            "is_edit_action": is_edit_action,
        }
    )

    if status:
        status = int(status)

    role_label = "Role"
    action_label = "Action"
    action_improve_label = action_label

    if (
        reportuserstory.type
        in [
            ReportUserStory.ANALYS_TYPE.PRECISE,
            ReportUserStory.ANALYS_TYPE.CONSISTENT,
            ReportUserStory.ANALYS_TYPE.CONCEPTUALLY,
        ]
        and status == 1
    ):
        improved_terms_show = True
        role_list = Role.objects.filter(userstory=userstory)
        extra_context.update(
            {
                "keywords": KeywordGlossary.objects.all(),
                "glossarys": Glossary.objects.all(),
            }
        )

        if reportuserstory.type == ReportUserStory.ANALYS_TYPE.PRECISE:
            reportterms = userstory.reportterms_set.filter(
                type=ReportUserStory.ANALYS_TYPE.PRECISE
            )
            if reportterms.exists():
                data = reportterms.last()
                extra_context.update({"reportterms": reportterms.last()})
            role_list = role_list.filter(status=ReportUserStory.ANALYS_TYPE.PRECISE)
            if role_list.exists():
                extra_context.update(
                    {
                        "role_list": role_list,
                    }
                )
            else:
                extra_context.update(
                    {
                        "role_custom_list": Role.objects.filter(
                            userstory__Project_Name=userstory.Project_Name
                        ).distinct("role_key"),
                    }
                )
        elif reportuserstory.type == ReportUserStory.ANALYS_TYPE.CONSISTENT:
            role_list = role_list.filter(status=ReportUserStory.ANALYS_TYPE.CONSISTENT)
            extra_context.update(
                {
                    "role_list": role_list,
                }
            )
        elif reportuserstory.type == ReportUserStory.ANALYS_TYPE.CONCEPTUALLY:
            role_label = "Subject"
            action_label = "Predicate"
            action_improve_label = "Implied Action"
            reportterms = userstory.reportterms_set.filter(
                type=ReportUserStory.ANALYS_TYPE.CONCEPTUALLY
            )
            if reportterms.exists():
                extra_context.update({"reportterms": reportterms.last()})
            role_list = role_list.filter(
                status=ReportUserStory.ANALYS_TYPE.CONCEPTUALLY
            )
            extra_context.update(
                {
                    "role_list": role_list,
                }
            )
    elif (
        reportuserstory.type
        in [
            ReportUserStory.ANALYS_TYPE.ATOMICITY,
            ReportUserStory.ANALYS_TYPE.CONCISENESS,
        ]
        and status == 1
    ):
        reportterms = userstory.reportterms_set.filter(type=reportuserstory.type)
        if reportterms.exists():
            extra_context.update({"reportterms_label": reportterms.last()})

    extra_context.update(
        {
            "userstory": userstory,
            "improved_terms_show": improved_terms_show,
            "role_label": role_label,
            "action_label": action_label,
            "action_improve_label": action_improve_label,
        }
    )

    if request.POST:
        type_status = request.POST.get("status", 0)
        submit_type = request.POST.get("submit_type", None)
        userstory_list = request.POST.getlist("userstory_list[]", [])
        if int(type_status) == ReportUserStory.ANALYS_TYPE.WELL_FORMED:
            userstory_improved = request.POST.get('userstory_improved', None)
            if userstory_improved:
                if submit_type == "submit":
                    AdjustedUserStory.objects.create(
                        created_by=request.user,
                        userstory=userstory,
                        userstory_text=userstory.UserStory_Full_Text,
                        adjusted=userstory_improved,
                        status=ReportUserStory.ANALYS_TYPE.WELL_FORMED,
                    )
                    userstory.UserStory_Full_Text = userstory_improved
                    userstory.old_userstory = userstory.UserStory_Full_Text
                    userstory.is_processed = False
                    userstory.save()
                    segmentation_edit_userstory(userstory.id, True)
                    messages.success(request, "Success update userstory.")
                    return redirect(
                        reverse("report_userstory_list") + f"?{path_url[1]}"
                        if len(path_url) > 1
                        else ""
                    )
            else:
                messages.warning(
                    request, "Warning, Improved User Story must not be empty."
                )
        elif int(type_status) in [ReportUserStory.ANALYS_TYPE.ATOMICITY, ReportUserStory.ANALYS_TYPE.CONCISENESS]:
            if len(userstory_list):
                # NOTE: add new child userstory only in status type Atomicity
                # userstory.is_processed = False
                # userstory.save()

                # segmentation_edit_userstory(userstory_id)
                # if userstory.get_report_list().exists():
                # delete data report
                # userstory.get_report_list().delete()

                if len(userstory_list):
                    for item in userstory_list:
                        if item:
                            userstory_child = UserStory_element.objects.create(
                                UserStory_Full_Text=item,
                                Project_Name=userstory.Project_Name,
                                UserStory_File_ID=userstory.UserStory_File_ID,
                                parent=userstory,
                                created_by=request.user
                            )
                            AdjustedUserStory.objects.create(
                                created_by=request.user,
                                userstory=userstory,
                                userstory_text=userstory.UserStory_Full_Text,
                                adjusted=item,
                                status=int(type_status),
                            )
                            segmentation_edit_userstory(userstory_child.id, True)

                messages.success(request, "Success update userstory.")
                return redirect(
                    reverse("report_userstory_list") + f"?{path_url[1]}"
                    if len(path_url) > 1
                    else ""
                )
            else:
                messages.warning(
                    request, "Warning, at least one user story must be inputted."
                )
        elif int(type_status) == ReportUserStory.ANALYS_TYPE.CONCEPTUALLY:
            is_edit = False
            improved_predicate = request.POST.get("improved_action", None)
            problematic_predicate = request.POST.get("problematic_action", None)
            rewrite_predicate = request.POST.get("rewrite_predicate", None)
            improved_action_new = request.POST.get("improved_action_new", None)
            improved_action_new_text = request.POST.get("improved_action_new_text", None)
            new_userstory = userstory.UserStory_Full_Text
            if improved_action_new == "on":
                improved_predicate = improved_action_new_text
                extra_context.update({
                    "improved_action_new_on": True,
                })

            if improved_predicate and problematic_predicate:
                # adjusted = userstory.UserStory_Full_Text.replace(
                #     problematic_predicate, improved_predicate
                # )
                if problematic_predicate in new_userstory:
                    if rewrite_predicate:
                        if improved_predicate in rewrite_predicate:
                            new_userstory = new_userstory.replace(problematic_predicate, rewrite_predicate)
                            is_edit = True
                        else:
                            messages.warning(request, "Warning!, rewriting predicates must have the Implied Action word selected")
                    else:
                        new_userstory = new_userstory.replace(problematic_predicate, improved_predicate)
                        is_edit = True
                    if submit_type == "submit":
                        if is_edit:
                            AdjustedUserStory.objects.create(
                                created_by=request.user,
                                userstory=userstory,
                                userstory_text=userstory.UserStory_Full_Text,
                                adjusted=new_userstory,
                                status=ReportUserStory.ANALYS_TYPE.CONCEPTUALLY,
                            )
                            userstory.UserStory_Full_Text = new_userstory
                            userstory.old_userstory = userstory.UserStory_Full_Text
                            userstory.is_processed = False
                            userstory.save()
                            segmentation_edit_userstory(userstory.id, True)
                            messages.success(request, "Success update userstory.")
                            return redirect(
                                reverse("report_userstory_list") + f"?{path_url[1]}"
                                if len(path_url) > 1
                                else ""
                            )
                    elif submit_type == "preview":
                        if rewrite_predicate:
                            extra_context.update({
                                "rewrite_predicate": rewrite_predicate,
                                "improved_action_select": improved_predicate,
                            })
                        else:
                            extra_context.update({
                                "improved_action_select": improved_predicate,
                            })
                        extra_context.update({
                            "new_userstory": new_userstory
                            })
                else:
                    messages.warning(request, "Warning!, predicates not found in the user story")
        else:
            is_edit = False
            problematic_role = request.POST.get("problematic_role", None)
            improved_role = request.POST.get("improved_role", None)
            # print(problematic_role, improved_role)
            new_userstory = userstory.UserStory_Full_Text
            old_text = userstory.UserStory_Full_Text
            if problematic_role and improved_role:
                if submit_type == "preview":
                    extra_context.update({"improved_role_select": improved_role})
                improved_role = f" {improved_role} "
                textstory = userstory.UserStory_Full_Text.replace(
                    problematic_role, improved_role
                )
                textstory = re.sub(" +", " ", textstory.strip())
                new_userstory = textstory
                if submit_type == "submit":
                    userstory.UserStory_Full_Text = textstory
                    userstory.old_userstory = old_text
                    userstory.save()
                    AdjustedUserStory.objects.create(
                        created_by=request.user,
                        userstory=userstory,
                        userstory_text=old_text,
                        adjusted=textstory,
                        status=int(type_status) if type_status else None,
                    )
                    is_edit = True

            problematic_action = request.POST.get("problematic_action", None)
            improved_action = request.POST.get("improved_action", None)
            improved_action_new = request.POST.get("improved_action_new", None)
            improved_action_new_text = request.POST.get(
                "improved_action_new_text", None
            )
            if improved_action_new == "on":
                improved_action = improved_action_new_text
            # print('problematic_action', problematic_action)
            # print('improved_action', improved_action)
            # print(problematic_action, improved_action)
            if problematic_action and improved_action:
                if submit_type == "preview":
                    extra_context.update(
                        {
                            "problematic_action_select": problematic_action,
                            "improved_action_select": improved_action,
                            "improved_action_new_on": improved_action_new,
                        }
                    )
                if submit_type == "submit":
                    glosasry_obj, created = Glossary.objects.get_or_create(
                        Action_item=problematic_action
                    )

                    keyword_obj, created = KeywordGlossary.objects.get_or_create(
                        keyword=improved_action
                    )
                    keyword_obj.item_name.add(glosasry_obj)
                    keyword_obj.save()

                improved_action = f" {improved_action} "
                textstory = new_userstory.replace(problematic_action, improved_action)
                textstory = re.sub(" +", " ", textstory.strip())
                new_userstory = textstory
                if submit_type == "submit":
                    userstory.UserStory_Full_Text = textstory
                    userstory.old_userstory = old_text
                    userstory.save()
                    AdjustedUserStory.objects.create(
                        created_by=request.user,
                        userstory=userstory,
                        userstory_text=old_text,
                        adjusted=textstory,
                        status=int(type_status) if type_status else None,
                    )
                    is_edit = True

            if submit_type == "preview":
                extra_context.update({"new_userstory": new_userstory})
            if is_edit:
                if submit_type == "submit":
                    userstory.is_processed = False
                    userstory.save()
                    segmentation_edit_userstory(userstory.id)
                    if userstory.get_report_list().exists():
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
                        created_by=request.user
                    )
                    segmentation_edit_userstory(userstory.id, True)
            messages.success(request, "Success add userstory.")
    return render(request, "inputUS/add_userstory.html", extra_context)


@login_required(login_url=reverse_lazy("login_"))
def view_list_project(request):
    projects = Project.objects.all()
    if not request.user.is_superuser:
        projects = projects.filter(created_by=request.user)
    paginator = Paginator(projects.order_by("-created_at"), 20)
    page = request.GET.get("page", 1)
    view_all = paginator.get_page(page)
    extra_context = {"view_all": view_all, "title": "View Projects"}
    return render(request, "inputUS/project/view.html", extra_context)


@login_required(login_url=reverse_lazy("login_"))
def view_add_project(request):
    extra_context = {"title": "Add Projects"}

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
    extra_context = {"project": project, "title": "Edit Projects"}
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


def print_report(request):
    project_id = request.GET.get("project_id", None)
    project = get_object_or_404(Project, pk=project_id)
    extra_context = {}
    if project_id:
        userstory_list = UserStory_element.objects.filter(
            Project_Name_id=project_id, is_processed=True
        )

        if not request.user.is_superuser:
            userstory_list = userstory_list.filter(created_by=request.user)

        file_used_list = NameFileUsed.objects.filter(
            created_by=request.user, is_active=True
        )
        if file_used_list.exists():
            file_used_list_id = file_used_list.values_list("name_file__id", flat=True)
            userstory_list = userstory_list.filter(
                UserStory_File_ID__in=list(file_used_list_id)
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
    queryset = KeywordGlossary.objects.all()
    paginator = Paginator(queryset.order_by("-id"), 20)
    page = request.GET.get("page", 1)
    view_all = paginator.get_page(page)
    return render(
        request,
        "inputUS/keyword/view.html",
        {"title": "Keyword", "view_all": view_all},
    )


@login_required(login_url=reverse_lazy("login_"))
def view_add_keyword(request):
    if request.POST:
        keyword = request.POST.get("keyword", None)
        if keyword:
            key, created = KeywordGlossary.objects.get_or_create(keyword=keyword)
            messages.success(request, "Success add keyword.")
            return redirect(reverse("master_keyword"))

    return render(
        request,
        "inputUS/keyword/add.html",
        {
            "title": "Add Keyword",
        },
    )


@login_required(login_url=reverse_lazy("login_"))
def view_add_action(request):
    keyword_list = KeywordGlossary.objects.all()
    if request.POST:
        keyword = request.POST.get("keyword", None)
        action = request.POST.get("action", None)

        if keyword and action:
            action, created = Glossary.objects.get_or_create(Action_item=action)
            try:
                keyword_obj = KeywordGlossary.objects.get(id=keyword)
            except KeywordGlossary.DoesNotExist:
                pass
            else:
                keyword_obj.item_name.add(action)
                keyword_obj.save()
                messages.success(request, "Success add action.")
                return redirect(reverse("master_keyword"))
    return render(
        request,
        "inputUS/keyword/add_action.html",
        {"title": "Add Action", "keyword_list": keyword_list},
    )


@login_required(login_url=reverse_lazy("login_"))
def view_list_processbackground(request):
    process = ProcessBackground.objects.all()
    if not request.user.is_superuser:
        process = process.filter(created_by=request.user)
    paginator = Paginator(process.order_by("-created_at"), 20)
    page = request.GET.get("page", 1)
    view_all = paginator.get_page(page)
    return render(
        request,
        "inputUS/background/view.html",
        {"title": "Process Background User Stories", "view_all": view_all},
    )


@login_required(login_url=reverse_lazy("login_"))
def view_list_accounts(request):
    accounts = User.objects.all()
    paginator = Paginator(accounts.order_by("-id"), 20)
    page = request.GET.get("page", 1)
    view_all = paginator.get_page(page)
    return render(
        request,
        "inputUS/accounts/view.html",
        {"title": "Accounts", "view_all": view_all},
    )


@login_required(login_url=reverse_lazy("login_"))
def view_list_adjusted_userstory(request):
    adjusted_list = AdjustedUserStory.objects.all()
    project_list = Project.objects.all()

    if not request.user.is_superuser:
        # adjusted_list = adjusted_list.filter(created_by=request.user)
        project_list = project_list.filter(created_by=request.user)
        adjusted_list = adjusted_list.filter(created_by=request.user)
    # file_used_list = NameFileUsed.objects.filter(created_by=request.user, is_active=True)
    # if file_used_list.exists():
    #     file_used_list_id = file_used_list.values_list('name_file__id', flat=True)
    #     adjusted_list = adjusted_list.filter(
    #         userstory__UserStory_File_ID__in=list(file_used_list_id)
    #     )

    q = request.GET.get("q", None)
    if q:
        adjusted_list = adjusted_list.filter(
            Q(userstory_text__icontains=q) | Q(adjusted__icontains=q)
        )
    project = request.GET.get("project", None)
    if project:
        adjusted_list = adjusted_list.filter(userstory__Project_Name_id=project)
    status = request.GET.get("status", None)
    if status:
        adjusted_list = adjusted_list.filter(status=status)

    mode = request.GET.get("mode", None)
    if mode == "pdf":
        return render(
            request,
            "inputUS/adjusted/view_pdf.html",
            {
                "title": "Adjusted User Story",
                "adjusted_list": adjusted_list,
            },
        )

    paginator = Paginator(adjusted_list.order_by("-created_at"), 20)
    page = request.GET.get("page", 1)
    view_all = paginator.get_page(page)

    return render(
        request,
        "inputUS/adjusted/view.html",
        {
            "title": "Adjusted User Story",
            "view_all": view_all,
            "project_list": project_list,
            "status_list": ReportUserStory.ANALYS_TYPE.choices,
            "project_value": int(project) if project else None,
            "status_value": int(status) if status else None,
        },
    )


@login_required(login_url=reverse_lazy("login_"))
def get_json_project_use(request):
    respon = {
        "success": False,
    }
    projects = Project.objects.all()
    if not request.user.is_superuser:
        projects = projects.filter(created_by=request.user)

    if projects.exists():
        data = []
        for project in projects:
            files = project.us_upload_set.all()
            data_file = []
            if files.exists():
                for file in files:
                    name_obj = NameFileUsed.objects.filter(
                        created_by=request.user, name_file=file, is_active=True
                    )
                    data_file.append(
                        {
                            "name": file.US_File_Name,
                            "id": file.id,
                            "selected": name_obj.exists(),
                        }
                    )
            item = {
                "project": project.Project_Name,
                "project_id": project.id,
                "file": data_file,
            }
            data.append(item)
        respon = {"success": True, "data": data}
    return JsonResponse(respon)


def update_json_project_use(request):
    respon = {
        "success": False,
    }
    file_id = request.GET.get("file_id", None)
    is_active = request.GET.get("is_active", None)

    if file_id and request.user:
        file_obj, created = NameFileUsed.objects.get_or_create(
            name_file_id=file_id, created_by=request.user
        )
        if is_active and is_active == "true":
            file_obj.is_active = True
        else:
            file_obj.is_active = False
        file_obj.save()
        respon = {
            "success": True,
        }
    return JsonResponse(respon)


def load_name_file_project(request):
    respon = {
        "success": False,
    }
    project_id = request.GET.get("project_id", None)
    try:
        project_ = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        pass
    else:
        files = project_.us_upload_set.all()
        if files.exists():
            data = []
            for item in files:
                data.append({"id": item.id, "text": item.US_File_Name})
            respon = {"success": True, "data": data}
    return JsonResponse(respon)


@login_required(login_url=reverse_lazy("login_"))
def persona_list_view(request):
    # NOTE: untuk who action ditampilkan semua dari userstory atau ditampilkan satu dari semua userstory yang who actionya sama
    extra_context = {
        'title': "Personas"
    }

    personas_list = Personas.objects.all().order_by('project', 'file_name')

    paginator = Paginator(personas_list, 20)
    page = request.GET.get("page", 1)
    view_all = paginator.get_page(page)

    # userstory_list = UserStory_element.objects.filter(
    #     Who_full__Who_action__isnull=False
    # )\
    # .distinct('Who_full__Who_action')\
    # .order_by('Project_Name', 'UserStory_File_ID')
    extra_context.update({
        'view_all': view_all
    })
    
    return render(request, "inputUS/persona_list.html", extra_context)

@login_required(login_url=reverse_lazy("login_"))
def persona_add_view(request):
    project_list = Project.objects.all()
    extra_context = {
        'title': "Personas",
        'project_list': project_list
    }
    if request.POST:
        project = request.POST.get('project')
        file_name = request.POST.get('file_name')
        persona = request.POST.get('persona')
        if project and file_name and persona:
            key_name = persona.strip().lower()
            persona_obj, created = Personas.objects.get_or_create(
                key_name=key_name,
                file_name_id=file_name,
                project_id=project,
            )
            persona_obj.persona = persona
            persona_obj.created_by = request.user
            persona_obj.save()
            messages.success(request, "Successfully added persona data")
            return redirect(reverse('persona_list_view'))
        messages.warning(request, "please check again")
    return render(request, "inputUS/persona_add.html", extra_context)


@login_required(login_url=reverse_lazy("login_"))
def save_comment_report(request):
    respon = {
        "success": False,
    }
    if request.POST:
        report_id = request.POST.get('report_id', None)
        report_agree = request.POST.get('report_agree', None)
        report_comment = request.POST.get('report_comment', None)
        is_submited = False
        if report_id:
            report_obj = get_object_or_404(ReportUserStory, pk=report_id)
            if report_agree == "agree":
                report_agree = True
                report_comment = None
                is_submited = True
            elif report_agree == "disagree":
                report_agree = False
                is_submited = True
            else:
                report_agree = None
                report_comment = None

            report_obj.is_submited = is_submited
            report_obj.is_agree = report_agree
            report_obj.disagree_comment = report_comment
            report_obj.save()
            respon = {
                "success": True,
            }
            if report_obj.is_problem:
                respon = {
                    "success": True,
                    'url': reverse_lazy("report_userstory_edit", kwargs={
                        'report_id': report_obj.id
                    })
                }
    return JsonResponse(respon)
