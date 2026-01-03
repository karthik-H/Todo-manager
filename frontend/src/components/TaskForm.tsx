import React, { useState } from 'react';
import type { TaskCreate, Task } from '../api';

interface TaskFormProps {
    initialTask?: Task | null;
    onSubmit: (task: TaskCreate) => Promise<void>;
    onCancel: () => void;
}

export const TaskForm: React.FC<TaskFormProps> = ({ initialTask, onSubmit, onCancel }) => {
    const [title, setTitle] = useState(initialTask?.title || '');
    const [description, setDescription] = useState(initialTask?.description || '');
    const [priority, setPriority] = useState<TaskCreate['priority']>(initialTask?.priority || 'Medium');
    const [category, setCategory] = useState<TaskCreate['category'] | ''>(initialTask?.category || '');
    const [dueDate, setDueDate] = useState(initialTask?.due_date || '');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        await onSubmit({
            title,
            description: description || undefined,
            priority,
            category: category === '' ? undefined : category,
            due_date: dueDate || undefined,
            completed: initialTask ? initialTask.completed : false,
        });
    };

    return (
        <form onSubmit={handleSubmit} className="card">
            <h2>{initialTask ? 'Edit Task' : 'Add New Task'}</h2>

            <div className="form-group">
                <label>Title *</label>
                <input
                    type="text"
                    className="form-control"
                    value={title}
                    onChange={e => setTitle(e.target.value)}
                    required
                    placeholder="What needs to be done?"
                />
            </div>

            <div className="form-group">
                <label>Description</label>
                <textarea
                    className="form-control"
                    value={description}
                    onChange={e => setDescription(e.target.value)}
                    placeholder="Details..."
                />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div className="form-group">
                    <label>Priority</label>
                    <select
                        className="form-control"
                        value={priority}
                        onChange={e => setPriority(e.target.value as any)}
                    >
                        <option value="Low">Low</option>
                        <option value="Medium">Medium</option>
                        <option value="High">High</option>
                    </select>
                </div>

                <div className="form-group">
                    <label>Category</label>
                    <select
                        className="form-control"
                        value={category}
                        onChange={e => setCategory(e.target.value as any)}
                    >
                        <option value="">None</option>
                        <option value="Work">Work</option>
                        <option value="Personal">Personal</option>
                        <option value="Study">Study</option>
                    </select>
                </div>
            </div>

            <div className="form-group">
                <label>Due Date</label>
                <input
                    type="date"
                    className="form-control"
                    value={dueDate}
                    onChange={e => setDueDate(e.target.value)}
                />
            </div>

            <div className="flex gap-2 justify-end mt-4">
                <button type="button" onClick={onCancel} className="btn btn-ghost">Cancel</button>
                <button type="submit" className="btn btn-primary">Save Task</button>
            </div>
        </form>
    );
};
