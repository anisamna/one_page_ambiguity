from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.contenttypes.models import ContentType


def log_admin_action(user, object_instance, action_flag=CHANGE, message=''):
    """
    Membuat log admin untuk suatu aksi (default: CHANGE).
    
    :param user: User yang melakukan aksi
    :param object_instance: Objek model yang dimodifikasi
    :param action_flag: Tipe aksi (CHANGE default, bisa ADDITION atau DELETION)
    :param message: Pesan tambahan (opsional)
    """
    if action_flag not in [ADDITION, CHANGE, DELETION]:
        raise ValueError("Aksi hanya bisa berupa ADDITION, CHANGE, atau DELETION")

    content_type = ContentType.objects.get_for_model(object_instance.__class__)
    
    LogEntry.objects.log_action(
        user_id=user.pk,
        content_type_id=content_type.pk,
        object_id=object_instance.pk,
        object_repr=str(object_instance),
        action_flag=action_flag,
        change_message=message
    )
