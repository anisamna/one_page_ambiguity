from django import template
from inputUS.models import UserStory_element, ReportUserStory
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
        if request.GET.get('type', None):
            report_list = report_list.filter(type=request.GET.get('type', None))
        status = request.GET.get('status', None)
        if status:
            if status == "1":
                report_list = report_list.filter(is_problem=True)
            elif status == "2":
                report_list = report_list.filter(is_problem=False)
        return report_list
    return ReportUserStory.objects.none()

@register.filter(name="get_count_report")
def get_count_report(userstory_id, request):
    report_list = get_report_list(userstory_id, request)
    return report_list.count()+1