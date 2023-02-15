def check_question_is_multichoice(instance) -> bool:
    from .models import Choice

    result = Choice.objects.filter(question__pk=instance.pk, is_correct=True).count()
    return True if result > 1 else False
