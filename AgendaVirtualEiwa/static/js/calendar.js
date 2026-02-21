// Calendario - Agenda Virtual Eiwa
let currentDate = new Date();
let currentView = 'month';
let tasksData = [];

// Inicializar calendario
document.addEventListener('DOMContentLoaded', function () {
    loadCalendar();
    setupEventListeners();
});

function setupEventListeners() {
    // Navegación
    document.getElementById('prevMonth').addEventListener('click', () => {
        if (currentView === 'week') {
            currentDate.setDate(currentDate.getDate() - 7);
        } else {
            currentDate.setMonth(currentDate.getMonth() - 1);
        }
        loadCalendar();
    });

    document.getElementById('nextMonth').addEventListener('click', () => {
        if (currentView === 'week') {
            currentDate.setDate(currentDate.getDate() + 7);
        } else {
            currentDate.setMonth(currentDate.getMonth() + 1);
        }
        loadCalendar();
    });

    document.getElementById('todayBtn').addEventListener('click', () => {
        currentDate = new Date();
        loadCalendar();
    });

    // Vista
    document.querySelectorAll('.btn-view').forEach(btn => {
        btn.addEventListener('click', function () {
            document.querySelectorAll('.btn-view').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            currentView = this.dataset.view;
            loadCalendar();
        });
    });

    // Filtros
    ['groupFilter', 'subjectFilter', 'statusFilter'].forEach(id => {
        document.getElementById(id).addEventListener('change', loadCalendar);
    });

    // Modal
    document.getElementById('closeModal').addEventListener('click', closeModal);
    document.getElementById('dayModal').addEventListener('click', function (e) {
        if (e.target === this) closeModal();
    });
}

async function loadCalendar() {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth() + 1;

    // Actualizar título
    const monthNames = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];

    if (currentView === 'week') {
        // Para vista semanal, mostrar rango de fechas
        const today = new Date(year, month - 1, currentDate.getDate());
        const dayOfWeek = today.getDay();
        const weekStart = new Date(today);
        weekStart.setDate(today.getDate() - dayOfWeek);
        const weekEnd = new Date(weekStart);
        weekEnd.setDate(weekStart.getDate() + 6);

        const startMonth = monthNames[weekStart.getMonth()];
        const endMonth = monthNames[weekEnd.getMonth()];

        if (weekStart.getMonth() === weekEnd.getMonth()) {
            document.getElementById('currentMonth').textContent =
                `${weekStart.getDate()} - ${weekEnd.getDate()} ${startMonth} ${year}`;
        } else {
            document.getElementById('currentMonth').textContent =
                `${weekStart.getDate()} ${startMonth} - ${weekEnd.getDate()} ${endMonth} ${year}`;
        }
    } else {
        document.getElementById('currentMonth').textContent = `${monthNames[month - 1]} ${year}`;
    }

    // Obtener filtros
    const groupFilter = document.getElementById('groupFilter').value;
    const subjectFilter = document.getElementById('subjectFilter').value;
    const statusFilter = document.getElementById('statusFilter').value;

    // Construir URL
    const day = currentDate.getDate();
    let url = `/calendar/api/data/?year=${year}&month=${month}&view=${currentView}`;
    if (currentView === 'week') {
        url += `&day=${day}`;
    }
    if (groupFilter) url += `&group=${groupFilter}`;
    if (subjectFilter) url += `&subject=${subjectFilter}`;
    if (statusFilter) url += `&status=${statusFilter}`;

    try {
        showLoading();
        const response = await fetch(url);
        const data = await response.json();
        tasksData = data.tasks;

        renderCalendar(data);
        renderWorkload(data.workload);
        hideLoading();
    } catch (error) {
        console.error('Error cargando calendario:', error);
        hideLoading();
        showToast('Error al cargar el calendario', 'error');
    }
}

function renderCalendar(data) {
    const grid = document.getElementById('calendarGrid');
    grid.innerHTML = '';

    if (currentView === 'month') {
        renderMonthView(grid, data);
    } else {
        renderWeekView(grid, data);
    }
}

function renderMonthView(grid, data) {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();

    // Agregar clase para vista mensual y remover estilos de vista semanal
    grid.classList.add('month-view');
    grid.classList.remove('week-view');

    // Primer día del mes
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const startDay = firstDay.getDay();

    // Días de la semana
    const weekDays = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'];
    weekDays.forEach(day => {
        const dayHeader = document.createElement('div');
        dayHeader.className = 'calendar-day-header';
        dayHeader.textContent = day;
        grid.appendChild(dayHeader);
    });

    // Días vacíos al inicio
    for (let i = 0; i < startDay; i++) {
        const emptyDay = document.createElement('div');
        emptyDay.className = 'calendar-day empty';
        grid.appendChild(emptyDay);
    }

    // Días del mes
    const today = new Date();
    for (let day = 1; day <= lastDay.getDate(); day++) {
        const dayDate = new Date(year, month, day);
        const dayElement = document.createElement('div');
        dayElement.className = 'calendar-day';

        // Marcar día actual
        if (dayDate.toDateString() === today.toDateString()) {
            dayElement.classList.add('today');
        }

        // Número del día
        const dayNumber = document.createElement('div');
        dayNumber.className = 'day-number';
        dayNumber.textContent = day;
        dayElement.appendChild(dayNumber);

        // Tareas del día
        const dayTasks = tasksData.filter(task => {
            // Parsear fecha sin conversión de zona horaria
            const [taskYear, taskMonth, taskDay] = task.due_date.split('-').map(Number);
            return taskDay === day &&
                taskMonth === (month + 1) &&
                taskYear === year;
        });

        if (dayTasks.length > 0) {
            // Agregar borde de color de la primera tarea
            const primaryColor = dayTasks[0].subject_color;
            dayElement.style.borderLeftColor = primaryColor;
            dayElement.style.borderLeftWidth = '4px';

            const tasksContainer = document.createElement('div');
            tasksContainer.className = 'day-tasks';

            dayTasks.slice(0, 3).forEach(task => {
                const taskItem = document.createElement('div');
                taskItem.className = `task-item ${task.status}`;

                const taskDot = document.createElement('div');
                taskDot.className = 'task-dot';

                // Color del punto según estado
                if (task.is_archived) {
                    taskDot.style.backgroundColor = '#9ca3af'; // Gris para archivadas
                } else if (task.status === 'completed' || task.status === 'overdue_completed') {
                    taskDot.style.backgroundColor = '#4caf50'; // Verde
                } else if (task.status === 'overdue') {
                    taskDot.style.backgroundColor = '#f44336'; // Rojo
                } else {
                    taskDot.style.backgroundColor = '#ff9800'; // Amarillo
                }

                const taskText = document.createElement('span');
                taskText.className = 'task-subject';
                if (task.is_archived) {
                    taskText.style.opacity = '0.6';
                    taskText.style.textDecoration = 'line-through';
                }
                taskText.textContent = task.title;

                taskItem.appendChild(taskDot);
                taskItem.appendChild(taskText);
                tasksContainer.appendChild(taskItem);
            });

            if (dayTasks.length > 3) {
                const moreIndicator = document.createElement('div');
                moreIndicator.className = 'more-tasks';
                moreIndicator.textContent = `+${dayTasks.length - 3} más`;
                tasksContainer.appendChild(moreIndicator);
            }

            dayElement.appendChild(tasksContainer);
        }

        // Click para ver detalles
        dayElement.addEventListener('click', () => showDayDetails(year, month + 1, day, dayTasks));

        grid.appendChild(dayElement);
    }
}

function renderWeekView(grid, data) {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();

    // Obtener el primer día de la semana actual
    const today = new Date(year, month, currentDate.getDate());
    const dayOfWeek = today.getDay();
    const weekStart = new Date(today);
    weekStart.setDate(today.getDate() - dayOfWeek);

    // Días de la semana
    const weekDays = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'];

    // Agregar clase para vista semanal
    grid.classList.add('week-view');
    grid.classList.remove('month-view');

    for (let i = 0; i < 7; i++) {
        const currentDay = new Date(weekStart);
        currentDay.setDate(weekStart.getDate() + i);

        const dayContainer = document.createElement('div');
        dayContainer.className = 'week-day-container';

        // Header del día
        const dayHeader = document.createElement('div');
        dayHeader.className = 'week-day-header';

        const isToday = currentDay.toDateString() === new Date().toDateString();
        if (isToday) {
            dayHeader.classList.add('today');
        }

        dayHeader.innerHTML = `
            <div class="week-day-name">${weekDays[i]}</div>
            <div class="week-day-number">${currentDay.getDate()}</div>
        `;

        dayContainer.appendChild(dayHeader);

        // Tareas del día
        const dayTasks = tasksData.filter(task => {
            const [taskYear, taskMonth, taskDay] = task.due_date.split('-').map(Number);
            return taskDay === currentDay.getDate() &&
                taskMonth === (currentDay.getMonth() + 1) &&
                taskYear === currentDay.getFullYear();
        });

        const tasksContainer = document.createElement('div');
        tasksContainer.className = 'week-tasks-container';

        if (dayTasks.length === 0) {
            tasksContainer.innerHTML = '<p class="no-tasks-week">Sin tareas</p>';
        } else {
            dayTasks.forEach(task => {
                const taskCard = document.createElement('div');
                taskCard.className = `week-task-card ${task.status}`;
                taskCard.style.borderLeftColor = task.subject_color;

                // Determinar color del punto
                let dotColor;
                if (task.is_archived) {
                    dotColor = '#9ca3af'; // Gris para archivadas
                } else if (task.status === 'completed' || task.status === 'overdue_completed') {
                    dotColor = '#4caf50';
                } else if (task.status === 'overdue') {
                    dotColor = '#f44336';
                } else {
                    dotColor = '#ff9800';
                }

                const archivedClass = task.is_archived ? 'archived' : '';
                const archivedStyle = task.is_archived ? 'opacity: 0.6;' : '';

                taskCard.innerHTML = `
                    <div class="week-task-info" style="${archivedStyle}">
                        <div class="week-task-title">${task.title}${task.is_archived ? ' <span style="font-size: 0.75rem; color: #9ca3af;">(Archivada)</span>' : ''}</div>
                        <div class="week-task-subject" style="color: ${task.subject_color}">${task.subject}</div>
                    </div>
                    <div class="week-task-dot" style="background: ${dotColor}"></div>
                `;

                taskCard.addEventListener('click', () => {
                    showDayDetails(
                        currentDay.getFullYear(),
                        currentDay.getMonth() + 1,
                        currentDay.getDate(),
                        dayTasks
                    );
                });

                tasksContainer.appendChild(taskCard);
            });
        }

        dayContainer.appendChild(tasksContainer);
        grid.appendChild(dayContainer);
    }
}

function renderWorkload(workload) {
    const indicator = document.getElementById('workloadIndicator');
    indicator.innerHTML = '';

    if (workload.length === 0) return;

    const monthNames = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];

    // Mostrar TODAS las semanas
    workload.forEach(week => {
        const weekCard = document.createElement('div');
        weekCard.className = `workload-card ${week.level}`;

        // Formatear fechas
        const startDate = new Date(week.start);
        const endDate = new Date(week.end);

        const dateRange = `${startDate.getDate()} ${monthNames[startDate.getMonth()]} - ${endDate.getDate()} ${monthNames[endDate.getMonth()]}`;

        weekCard.innerHTML = `
            <div class="workload-header">
                <span class="workload-label">${week.label}</span>
                <span class="workload-date">${dateRange}</span>
            </div>
            <div class="workload-count">${week.task_count} tarea${week.task_count !== 1 ? 's' : ''}</div>
        `;

        indicator.appendChild(weekCard);
    });
}

function showDayDetails(year, month, day, dayTasks) {
    const modal = document.getElementById('dayModal');
    const modalDate = document.getElementById('modalDate');
    const modalBody = document.getElementById('modalBody');

    // Formatear fecha
    const date = new Date(year, month - 1, day);
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    modalDate.textContent = date.toLocaleDateString('es-MX', options);

    modal.style.display = 'flex';

    if (dayTasks.length === 0) {
        modalBody.innerHTML = '<p class="no-tasks">No hay tareas para este día</p>';
        return;
    }

    let html = '<div class="day-tasks-list">';
    dayTasks.forEach(task => {
        const isCompleted = task.status === 'completed' || task.status === 'overdue_completed';
        const isOverdue = task.status === 'overdue' || task.status === 'overdue_completed';
        const isArchived = task.is_archived || false;

        html += `
            <div class="task-card ${isCompleted ? 'completed' : ''} ${isOverdue ? 'overdue' : ''} ${isArchived ? 'archived' : ''}">
                <div class="task-color" style="background: ${task.subject_color}"></div>
                <div class="task-info">
                    <h4>${task.title}</h4>
                    <p class="task-subject">${task.subject} - ${task.group}</p>
                    ${task.description ? `<p class="task-description">${task.description}</p>` : ''}
                    <p class="task-meta">Creada por: ${task.created_by}</p>
                    ${isArchived ? '<span class="badge-archived">ARCHIVADA</span>' : ''}
                    ${isOverdue && !isArchived ? '<span class="badge-overdue">VENCIDA</span>' : ''}
                </div>
                <div class="task-actions">
                    <a href="/tasks/${task.id}/" class="btn btn-sm btn-primary">Ver Tarea</a>
                    ${!isArchived && !isCompleted ? 
                        `<button class="btn btn-sm btn-success" onclick="toggleTask(${task.id})">Completar</button>` : 
                        !isArchived && isCompleted ? 
                        `<button class="btn btn-sm btn-secondary" onclick="toggleTask(${task.id})">Desmarcar</button>` : 
                        ''
                    }
                </div>
            </div>
        `;
    });
    html += '</div>';

    modalBody.innerHTML = html;
}

function closeModal() {
    document.getElementById('dayModal').style.display = 'none';
}

async function toggleTask(taskId) {
    try {
        const url = `/tasks/${taskId}/toggle/`;

        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
            }
        });

        const data = await response.json();

        if (response.ok && data.success) {
            // Mostrar notificación
            const message = data.completed ? 'Tarea completada ✓' : 'Tarea marcada como pendiente';
            showToast(message, 'success');

            // Recargar el calendario
            await loadCalendar();
            // Cerrar el modal
            closeModal();
        } else {
            showToast('Error al cambiar el estado de la tarea', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('Error de conexión', 'error');
    }
}

function showLoading() {
    let loader = document.getElementById('calendarLoader');
    if (!loader) {
        loader = document.createElement('div');
        loader.id = 'calendarLoader';
        loader.className = 'calendar-loading';
        loader.innerHTML = '<div class="spinner"></div>';
        document.body.appendChild(loader);
    }
    loader.classList.add('active');
}

function hideLoading() {
    const loader = document.getElementById('calendarLoader');
    if (loader) {
        loader.classList.remove('active');
    }
}

function showToast(message, type = 'success') {
    // Remover toast anterior si existe
    const existingToast = document.querySelector('.toast');
    if (existingToast) {
        existingToast.remove();
    }

    // Crear nuevo toast
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    const icon = type === 'success' ? '✓' : '✕';
    toast.innerHTML = `
        <span class="toast-icon">${icon}</span>
        <span class="toast-message">${message}</span>
    `;

    document.body.appendChild(toast);

    // Mostrar con animación
    setTimeout(() => toast.classList.add('show'), 10);

    // Ocultar después de 3 segundos
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
