from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.tracking.models import RevertibleAction
from apps.tasks.models import TaskAttachment
import os


class Command(BaseCommand):
    help = 'Limpia acciones reversibles mayores a 7 días y elimina archivos asociados'

    def handle(self, *args, **options):
        # Calcular fecha límite (7 días atrás)
        cutoff_date = timezone.now() - timedelta(days=7)
        
        # Obtener acciones antiguas
        old_actions = RevertibleAction.objects.filter(
            created_at__lt=cutoff_date,
            is_reverted=False
        )
        
        total_actions = old_actions.count()
        deleted_files = 0
        
        self.stdout.write(f'Encontradas {total_actions} acciones antiguas para limpiar...')
        
        for action in old_actions:
            # Si la acción tiene archivos eliminados en el snapshot, borrarlos físicamente
            if action.action_type == 'task_edit' and action.snapshot_data:
                # Buscar archivos que fueron marcados para eliminar
                if 'deleted_attachments' in action.snapshot_data:
                    for att_id in action.snapshot_data['deleted_attachments']:
                        try:
                            attachment = TaskAttachment.objects.get(id=att_id)
                            if attachment.file:
                                # Eliminar archivo físico
                                if os.path.exists(attachment.file.path):
                                    os.remove(attachment.file.path)
                                    deleted_files += 1
                                    self.stdout.write(f'  Archivo eliminado: {attachment.original_filename}')
                            # Eliminar registro de BD
                            attachment.delete()
                        except TaskAttachment.DoesNotExist:
                            pass
                        except Exception as e:
                            self.stdout.write(self.style.WARNING(f'  Error al eliminar archivo: {e}'))
            
            # Eliminar la acción reversible
            action.delete()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✓ Limpieza completada: {total_actions} acciones eliminadas, {deleted_files} archivos borrados'
            )
        )
