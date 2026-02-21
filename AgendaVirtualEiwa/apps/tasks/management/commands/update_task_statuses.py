from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.tasks.models import Task


class Command(BaseCommand):
    help = 'Actualiza los estados de las tareas según las reglas del sistema (archiva tareas antiguas, marca vencidas recientes)'

    def handle(self, *args, **options):
        today = timezone.now().date()
        
        # Obtener todas las tareas activas (no completadas ni archivadas)
        active_tasks = Task.objects.exclude(status__in=['completed', 'archived'])
        
        updated_count = 0
        archived_count = 0
        overdue_count = 0
        
        for task in active_tasks:
            old_status = task.status
            task.update_status()
            
            if old_status != task.status:
                updated_count += 1
                
                if task.status == 'archived':
                    archived_count += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f'Archivada: {task.title} (vencida hace {task.days_overdue} días)'
                        )
                    )
                elif task.status == 'overdue_recent':
                    overdue_count += 1
                    self.stdout.write(
                        self.style.NOTICE(
                            f'Vencida reciente: {task.title} (vencida hace {task.days_overdue} días)'
                        )
                    )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Proceso completado:'
                f'\n  - {updated_count} tareas actualizadas'
                f'\n  - {archived_count} tareas archivadas'
                f'\n  - {overdue_count} tareas marcadas como vencidas recientes'
            )
        )
