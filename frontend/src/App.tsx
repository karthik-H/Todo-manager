import { useEffect, useState } from 'react';
import { api } from './api';
import type { Task, TaskCreate } from './api';
import { TaskItem } from './components/TaskItem';
import { TaskForm } from './components/TaskForm';

type SortOption = 'dueDate' | 'priority';
type FilterStatus = 'all' | 'completed' | 'pending';

function App() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const [filterStatus, setFilterStatus] = useState<FilterStatus>('all');
  const [sortOption, setSortOption] = useState<SortOption>('dueDate');

  useEffect(() => {
    loadTasks();
  }, []);

  const loadTasks = async () => {
    try {
      const data = await api.getTasks();
      setTasks(data);
    } catch (error) {
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateTask = async (taskData: TaskCreate) => {
    try {
      await api.createTask(taskData);
      await loadTasks();
      setIsFormOpen(false);
    } catch (error) {
      alert('Failed to create task');
    }
  };

  const handleUpdateTask = async (taskData: TaskCreate) => {
    if (!editingTask) return;
    try {
      await api.updateTask(editingTask.id, taskData);
      await loadTasks();
      setEditingTask(null);
      setIsFormOpen(false);
    } catch (error) {
      alert('Failed to update task');
    }
  };

  const handleDeleteTask = async (id: string) => {
    try {
      await api.deleteTask(id);
      setTasks(tasks.filter(t => t.id !== id));
    } catch (error) {
      alert('Failed to delete task');
    }
  };

  const handleToggleComplete = async (task: Task) => {
    try {
      await api.updateTask(task.id, { ...task, completed: !task.completed });
      await loadTasks();
    } catch (error) {
      alert('Failed to update task status');
    }
  };

  const openEdit = (task: Task) => {
    setEditingTask(task);
    setIsFormOpen(true);
  };

  const filteredTasks = tasks
    .filter(task => {
      if (filterStatus === 'completed') return task.completed;
      if (filterStatus === 'pending') return !task.completed;
      return true;
    })
    .sort((a, b) => {
      if (sortOption === 'dueDate') {
        if (!a.due_date) return 1;
        if (!b.due_date) return -1;
        return new Date(a.due_date).getTime() - new Date(b.due_date).getTime();
      }
      if (sortOption === 'priority') {
        const priorityMap = { High: 0, Medium: 1, Low: 2 };
        return priorityMap[a.priority] - priorityMap[b.priority];
      }
      return 0;
    });

  return (
    <div className="container">
      <header className="flex justify-between items-center mb-8">
        <h1>My Tasks</h1>
        <button
          className="btn btn-primary"
          onClick={() => { setEditingTask(null); setIsFormOpen(true); }}
        >
          + Add Task
        </button>
      </header>

      {isFormOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50 overflow-y-auto">
          <div className="w-full max-w-md">
            <TaskForm
              initialTask={editingTask}
              onSubmit={editingTask ? handleUpdateTask : handleCreateTask}
              onCancel={() => { setIsFormOpen(false); setEditingTask(null); }}
            />
          </div>
        </div>
      )}

      <div className="flex gap-4 mb-6 flex-wrap">
        <div className="form-group mb-0">
          <select
            className="form-control"
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value as FilterStatus)}
          >
            <option value="all">All Status</option>
            <option value="pending">Pending</option>
            <option value="completed">Completed</option>
          </select>
        </div>

        <div className="form-group mb-0">
          <select
            className="form-control"
            value={sortOption}
            onChange={(e) => setSortOption(e.target.value as SortOption)}
          >
            <option value="dueDate">Sort by Due Date</option>
            <option value="priority">Sort by Priority</option>
          </select>
        </div>
      </div>

      <div className="flex flex-col gap-4">
        {isLoading ? (
          <p>Loading tasks...</p>
        ) : filteredTasks.length === 0 ? (
          <div className="text-center py-12 text-gray-500 bg-white rounded-lg border border-dashed border-gray-300">
            <p>No tasks found. Create one to get started!</p>
          </div>
        ) : (
          filteredTasks.map(task => (
            <TaskItem
              key={task.id}
              task={task}
              onToggleComplete={handleToggleComplete}
              onDelete={handleDeleteTask}
              onEdit={openEdit}
            />
          ))
        )}
      </div>
    </div>
  );
}

export default App;
