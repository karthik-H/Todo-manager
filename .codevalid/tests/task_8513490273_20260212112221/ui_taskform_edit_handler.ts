import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import TaskForm from '../../../frontend/src/components/TaskForm';
import '@testing-library/jest-dom';

// Helper to create initialTask object
const getInitialTask = (overrides = {}) => ({
  title: 'Buy groceries',
  description: 'Milk, Bread',
  priority: 'High',
  category: 'Shopping',
  dueDate: '2024-06-30',
  ...overrides,
});

describe('TaskForm Component', () => {
  // Test Case 1: Prefill fields with initialTask values
  it('Prefill fields with initialTask values', () => {
    render(<TaskForm initialTask={getInitialTask()} onSubmit={jest.fn()} />);
    expect(screen.getByLabelText(/title/i)).toHaveValue('Buy groceries');
    expect(screen.getByLabelText(/description/i)).toHaveValue('Milk, Bread');
    expect(screen.getByLabelText(/priority/i)).toHaveValue('High');
    expect(screen.getByLabelText(/category/i)).toHaveValue('Shopping');
    expect(screen.getByLabelText(/due date/i)).toHaveValue('2024-06-30');
  });

  // Test Case 2: Edit title and submit form
  it('Edit title and submit form', async () => {
    const mockSubmit = jest.fn();
    render(<TaskForm initialTask={getInitialTask()} onSubmit={mockSubmit} />);
    fireEvent.change(screen.getByLabelText(/title/i), { target: { value: 'Buy fruits' } });
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));
    await waitFor(() => {
      expect(mockSubmit).toHaveBeenCalledWith(expect.objectContaining({
        title: 'Buy fruits',
        description: 'Milk, Bread',
        priority: 'High',
        category: 'Shopping',
        dueDate: '2024-06-30',
      }));
    });
  });

  // Test Case 3: Edit multiple fields and submit form
  it('Edit multiple fields and submit form', async () => {
    const mockSubmit = jest.fn();
    render(<TaskForm initialTask={getInitialTask()} onSubmit={mockSubmit} />);
    fireEvent.change(screen.getByLabelText(/description/i), { target: { value: 'Milk, Bread, Eggs' } });
    fireEvent.change(screen.getByLabelText(/priority/i), { target: { value: 'Medium' } });
    fireEvent.change(screen.getByLabelText(/category/i), { target: { value: 'Groceries' } });
    fireEvent.change(screen.getByLabelText(/due date/i), { target: { value: '2024-07-01' } });
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));
    await waitFor(() => {
      expect(mockSubmit).toHaveBeenCalledWith(expect.objectContaining({
        title: 'Buy groceries',
        description: 'Milk, Bread, Eggs',
        priority: 'Medium',
        category: 'Groceries',
        dueDate: '2024-07-01',
      }));
    });
  });

  // Test Case 4: Submit without changing fields
  it('Submit without changing fields', async () => {
    const mockSubmit = jest.fn();
    render(<TaskForm initialTask={getInitialTask()} onSubmit={mockSubmit} />);
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));
    await waitFor(() => {
      expect(mockSubmit).toHaveBeenCalledWith(getInitialTask());
    });
  });

  // Test Case 5: Empty title field validation
  it('Empty title field validation', async () => {
    const mockSubmit = jest.fn();
    render(<TaskForm initialTask={getInitialTask()} onSubmit={mockSubmit} />);
    fireEvent.change(screen.getByLabelText(/title/i), { target: { value: '' } });
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));
    await waitFor(() => {
      expect(screen.getByText(/title is required/i)).toBeInTheDocument();
      expect(mockSubmit).not.toHaveBeenCalled();
    });
  });

  // Test Case 6: Invalid due date validation
  it('Invalid due date validation', async () => {
    const mockSubmit = jest.fn();
    render(<TaskForm initialTask={getInitialTask()} onSubmit={mockSubmit} />);
    fireEvent.change(screen.getByLabelText(/due date/i), { target: { value: '2020-01-01' } });
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));
    await waitFor(() => {
      expect(screen.getByText(/due date cannot be in the past/i)).toBeInTheDocument();
      expect(mockSubmit).not.toHaveBeenCalled();
    });
  });

  // Test Case 7: Invalid priority value handling
  it('Invalid priority value handling', async () => {
    const mockSubmit = jest.fn();
    render(<TaskForm initialTask={getInitialTask()} onSubmit={mockSubmit} />);
    fireEvent.change(screen.getByLabelText(/priority/i), { target: { value: 'Urgent' } });
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));
    await waitFor(() => {
      expect(screen.getByText(/invalid priority selected/i)).toBeInTheDocument();
      expect(mockSubmit).not.toHaveBeenCalled();
    });
  });

  // Test Case 8: Category field left empty
  it('Category field left empty', async () => {
    const mockSubmit = jest.fn();
    render(<TaskForm initialTask={getInitialTask()} onSubmit={mockSubmit} />);
    fireEvent.change(screen.getByLabelText(/category/i), { target: { value: '' } });
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));
    await waitFor(() => {
      expect(mockSubmit).toHaveBeenCalledWith(expect.objectContaining({
        category: '',
      }));
      expect(screen.queryByText(/category is required/i)).not.toBeInTheDocument();
    });
  });

  // Test Case 9: Title field max length handling
  it('Title field max length handling', async () => {
    const maxTitle = 'T'.repeat(255);
    const mockSubmit = jest.fn();
    render(<TaskForm initialTask={getInitialTask()} onSubmit={mockSubmit} />);
    fireEvent.change(screen.getByLabelText(/title/i), { target: { value: maxTitle } });
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));
    await waitFor(() => {
      expect(mockSubmit).toHaveBeenCalledWith(expect.objectContaining({
        title: maxTitle,
      }));
      expect(screen.queryByText(/title is too long/i)).not.toBeInTheDocument();
    });
  });

  // Test Case 10: Special characters in fields
  it('Special characters in fields', async () => {
    const mockSubmit = jest.fn();
    render(<TaskForm initialTask={getInitialTask()} onSubmit={mockSubmit} />);
    fireEvent.change(screen.getByLabelText(/title/i), { target: { value: 'Hello @#$%' } });
    fireEvent.change(screen.getByLabelText(/description/i), { target: { value: '*(&^%$#@!' } });
    fireEvent.change(screen.getByLabelText(/category/i), { target: { value: 'Work!@#' } });
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));
    await waitFor(() => {
      expect(mockSubmit).toHaveBeenCalledWith(expect.objectContaining({
        title: 'Hello @#$%',
        description: '*(&^%$#@!',
        category: 'Work!@#',
      }));
    });
  });

  // Test Case 11: Render form without initialTask
  it('Render form without initialTask', () => {
    render(<TaskForm onSubmit={jest.fn()} />);
    expect(screen.getByLabelText(/title/i)).toHaveValue('');
    expect(screen.getByLabelText(/description/i)).toHaveValue('');
    expect(screen.getByLabelText(/priority/i)).toHaveValue('');
    expect(screen.getByLabelText(/category/i)).toHaveValue('');
    expect(screen.getByLabelText(/due date/i)).toHaveValue('');
  });

  // Test Case 12: Rapid field changes before submit
  it('Rapid field changes before submit', async () => {
    const mockSubmit = jest.fn();
    render(<TaskForm initialTask={getInitialTask()} onSubmit={mockSubmit} />);
    fireEvent.change(screen.getByLabelText(/title/i), { target: { value: 'A' } });
    fireEvent.change(screen.getByLabelText(/description/i), { target: { value: 'B' } });
    fireEvent.change(screen.getByLabelText(/due date/i), { target: { value: '2024-08-01' } });
    fireEvent.change(screen.getByLabelText(/title/i), { target: { value: 'Final Title' } });
    fireEvent.change(screen.getByLabelText(/description/i), { target: { value: 'Final Desc' } });
    fireEvent.change(screen.getByLabelText(/due date/i), { target: { value: '2024-09-01' } });
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));
    await waitFor(() => {
      expect(mockSubmit).toHaveBeenCalledWith(expect.objectContaining({
        title: 'Final Title',
        description: 'Final Desc',
        dueDate: '2024-09-01',
      }));
    });
  });

  // Test Case 13: Form reset functionality
  it('Form reset functionality', async () => {
    render(<TaskForm initialTask={getInitialTask()} onSubmit={jest.fn()} />);
    fireEvent.change(screen.getByLabelText(/title/i), { target: { value: 'Changed Title' } });
    fireEvent.change(screen.getByLabelText(/description/i), { target: { value: 'Changed Desc' } });
    fireEvent.click(screen.getByRole('button', { name: /reset/i }));
    await waitFor(() => {
      expect(screen.getByLabelText(/title/i)).toHaveValue('Buy groceries');
      expect(screen.getByLabelText(/description/i)).toHaveValue('Milk, Bread');
      expect(screen.getByLabelText(/priority/i)).toHaveValue('High');
      expect(screen.getByLabelText(/category/i)).toHaveValue('Shopping');
      expect(screen.getByLabelText(/due date/i)).toHaveValue('2024-06-30');
    });
  });

  // Test Case 14: Persisted edits visible in task listing
  it('Persisted edits visible in task listing', async () => {
    // Mock TaskForm and TaskItem listing
    const tasks = [getInitialTask()];
    const mockSubmit = jest.fn((updatedTask) => {
      tasks[0] = updatedTask;
    });

    render(
      <>
        <TaskForm initialTask={tasks[0]} onSubmit={mockSubmit} />
        <div data-testid="task-listing">
          <span>{tasks[0].title}</span>
          <span>{tasks[0].priority}</span>
        </div>
      </>
    );
    fireEvent.change(screen.getByLabelText(/title/i), { target: { value: 'Buy fruit' } });
    fireEvent.change(screen.getByLabelText(/priority/i), { target: { value: 'Medium' } });
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));

    await waitFor(() => {
      // Simulate re-render after submit
      expect(mockSubmit).toHaveBeenCalled();
      expect(screen.getByTestId('task-listing')).toHaveTextContent('Buy fruit');
      expect(screen.getByTestId('task-listing')).toHaveTextContent('Medium');
    });
  });
});