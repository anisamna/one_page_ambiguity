from functions.analysis_userstory import AnalysisData
from inputUS.models import ProcessBackground
from one_page_ambiguity_base.celery import app


@app.task
def task_process_analys_data(obj_id):
    process = ProcessBackground.objects.get(id=obj_id)
    userstorys = process.userstorys.all()
    if userstorys.exists():
        userstory_list = userstorys.values_list("id", flat=True)
        userstory_list = list(set(userstory_list))
        process.is_process = True
        process.save()
        AnalysisData(
            userstory_list,
            process.eps_value,
            process.min_samples_value,
            process.terms_role_value,
            process.terms_action_value,
            process.topics_value,
            process.similarity_value,
            process.created_by,
        ).start()
        process.is_done = True
        process.save()
    return True
