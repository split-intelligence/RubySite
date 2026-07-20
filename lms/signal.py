from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import CompletedMaterial

@receiver(post_save, sender=CompletedMaterial)
@receiver(post_delete, sender=CompletedMaterial)
def update_enrollment_progress(sender, instance, **kwargs):
    enrollment = instance.enrollment
    course = enrollment.course
    total_materials = course.materials.count()
    if total_materials == 0:
        progress = 0.0
    else:
        completed_count = enrollment.completed_materials.count()
        progress = (completed_count / total_materials) * 100.0
    enrollment.progress = progress
    enrollment.completed = (progress == 100.0)  # optionally auto‑set completion
    enrollment.save(update_fields=['progress', 'completed'])