from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.tasks.models import Task, TaskAttachment
import os


class Command(BaseCommand):
    help = 'Elimina archivos físicos de tareas archivadas pero mantiene metadata'

    def handle(self, *args, **options):
        # Obtener tareas archivadas con documentos
        archived_tasks = Task.objects.filter(status='archived')
        
        total_files = 0
        deleted_files = 0
        
        self.stdout.write(f'Buscando archivos en {archived_tasks.count()} tareas archivadas...')
        
        for task in archived_tasks:
            attachments = TaskAttachment.objects.filter(task=task, file_deleted=False)
            
            for attachment in attachments:
                total_files += 1
                
                if attachment.file:
                    try:
                        # Verificar si el archivo existe
                        if os.path.exists(attachment.file.path):
                            # Eliminar archivo físico
                            os.remove(attachment.file.path)
                            deleted_files += 1
                            self.stdout.write(f'  ✓ Eliminado: {attachment.original_filename} (Tarea: {task.title})')
                        
                        # Marcar como eliminado en BD
                        attachment.file_deleted = True
                        attachment.deleted_at = timezone.now()
                        attachment.save()
                        
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'  ✗ Error al eliminar {attachment.original_filename}: {e}'))
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Limpieza completada: {deleted_files}/{total_files} archivos eliminados'
            )
        )
