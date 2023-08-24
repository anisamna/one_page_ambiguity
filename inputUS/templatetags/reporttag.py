from django import template

from inputUS.models import ReportUserStory, UserStory_element

register = template.Library()


@register.filter(name="get_report_list")
def get_report_list(userstory_id, request):
    # print(userstory_id)
    # print(request)
    try:
        userstory = UserStory_element.objects.get(id=userstory_id)
    except UserStory_element.DoesNotExist:
        pass
    else:
        report_list = userstory.get_report_list()
        if request.GET.get("type", None):
            report_list = report_list.filter(type=request.GET.get("type", None))
        status = request.GET.get("status", None)
        if status:
            if status == "1":
                report_list = report_list.filter(is_problem=True)
            elif status == "2":
                report_list = report_list.filter(is_problem=False)
        potential_problem = request.GET.get("potential_problem", None)
        if potential_problem:
            if potential_problem == "0":
                report_list = report_list.filter(status__icontains="is achieved")
            elif potential_problem == "1":
                report_list = report_list.filter(
                    type__in=[
                        ReportUserStory.ANALYS_TYPE.PRECISE,
                        ReportUserStory.ANALYS_TYPE.WELL_FORMED,
                        ReportUserStory.ANALYS_TYPE.CONSISTENT,
                    ]
                )
            elif potential_problem == "2":
                report_list = report_list.filter(
                    type__in=[
                        ReportUserStory.ANALYS_TYPE.CONSISTENT,
                        ReportUserStory.ANALYS_TYPE.ATOMICITY,
                        ReportUserStory.ANALYS_TYPE.CONCEPTUALLY,
                    ]
                )
            elif potential_problem == "3":
                report_list = report_list.filter(
                    type__in=[
                        ReportUserStory.ANALYS_TYPE.CONCEPTUALLY,
                    ]
                )
            elif potential_problem == "4":
                report_list = report_list.filter(
                    type__in=[
                        ReportUserStory.ANALYS_TYPE.UNIQUENESS,
                    ]
                )
        return report_list
    return ReportUserStory.objects.none()


@register.filter(name="get_count_report")
def get_count_report(userstory_id, request):
    report_list = get_report_list(userstory_id, request)
    return report_list.count() + 1
