from django.utils import timezone

def filter_day_locked(qs, get_day_number, get_class_group):
    today = timezone.now().date()
    unlocked_ids = []
    for obj in qs :
        class_group = get_class_group(obj)
        started_at = class_group.program_started_at if class_group else None
        day_number = get_day_number(obj)
        if  started_at  and day_number <= (today - started_at).days + 1 :
            unlocked_ids.append(obj.id)

    return qs.filter(id__in = unlocked_ids)

def get_current_day(class_group):
    started_at = class_group.program_started_at
    program = class_group.current_program
    if not started_at or not program or not program.duration_days:
        return None
    day = (timezone.localdate() - started_at).days + 1
    if day < 1:
        return None
    return min(day, program.duration_days)