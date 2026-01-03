import React from 'react';
import type { Task } from '../api';

interface TaskItemProps {
    task: Task;
    onToggleComplete: (task: Task) => void;
    onDelete: (id: string) => void;
    onEdit: (task: Task) => void;
}

const getPriorityBadgeClass = (priority: string) => {
    switch (priority) {
        case 'High': return 'badge badge-high';
        case 'Medium': return 'badge badge-medium';
        case 'Low': return 'badge badge-low';
        default: return 'badge';
    }
};

export const TaskItem: React.FC<TaskItemProps> = ({ task, onToggleComplete, onDelete, onEdit }) => {
    const handleDelete = () => {
        if (window.confirm('Are you sure you want to delete this task?')) {
            onDelete(task.id);
        }
    };

    return (
        <div className={`card ${task.completed ? 'opacity-50' : ''}`} style={{ opacity: task.completed ? 0.7 : 1 }}>
            <div className="flex justify-between items-start">
                <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                        <h3 style={{ textDecoration: task.completed ? 'line-through' : 'none' }}>
                            {task.title}
                        </h3>
                        <span className={getPriorityBadgeClass(task.priority)}>{task.priority}</span>
                        {task.category && <span className="badge" style={{ backgroundColor: '#f1f5f9' }}>{task.category}</span>}
                    </div>

                    {task.description && (
                        <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.9rem', marginBottom: '0.5rem' }}>
                            {task.description}
                        </p>
                    )}

                    <div className="flex items-center gap-4 text-sm text-gray-500">
                        {task.due_date && (
                            <span>Due: {new Date(task.due_date).toLocaleDateString()}</span>
                        )}
                    </div>
                </div>

                <div className="flex gap-2">
                    <button
                        onClick={() => onToggleComplete(task)}
                        className={`btn ${task.completed ? 'btn-ghost' : 'btn-primary'}`}
                        title={task.completed ? "Mark as pending" : "Mark as completed"}
                    >
                        {task.completed ? 'Undo' : 'Done'}
                    </button>
                    <button onClick={() => onEdit(task)} className="btn btn-ghost">Edit</button>
                    <button onClick={handleDelete} className="btn btn-danger">Delete</button>
                </div>
            </div>
        </div>
    );
};
