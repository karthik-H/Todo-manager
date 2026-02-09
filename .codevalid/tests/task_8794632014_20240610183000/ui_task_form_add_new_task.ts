import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import TaskForm from '../../../frontend/src/components/TaskForm';

// Helper to fill form fields
const fillForm = ({
  title = 'Test Task',
  description = 'Test Description',
  priority = 'Medium',
  category = 'Work',
  dueDate = '',
} = {}) => {
  if (title !== undefined) {
    fireEvent.change(screen.getByLabelText(/title/i), { target: { value: title } });
  }
  if (description !== undefined) {
    fireEvent.change(screen.getByLabelText(/description/i), { target: { value: description } });
  }
  if (priority !== undefined) {
    fireEvent.change(screen.getByLabelText(/priority/i), { target: { value: priority } });
  }
  if (category !== undefined) {
    fireEvent.change(screen.getByLabelText(/category/i), { target: { value: category } });
  }
  if (dueDate !== undefined && dueDate !== '') {
    fireEvent.change(screen.getByLabelText(/due date/i), { target: { value: dueDate } });
  }
};

const getFutureDate = () => {
  const date = new Date();
  date.setDate(date.getDate() + 1);
  return date.toISOString().split('T')[0];
};

const getPastDate = () => {
  const date = new Date();
  date.setDate(date.getDate() - 1);
  return date.toISOString().split('T')[0];
};

describe('TaskForm', () => {
  // Test Case 1: Render all form fields
  test('Render all form fields', () => {
    render(<TaskForm onSubmit={jest.fn()} />);
    expect(screen.getByLabelText(/title/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/description/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/priority/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/category/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/due date/i)).toBeInTheDocument();
  });

  // Test Case 2: Submit form with valid data
  test('Submit form with valid data', async () => {
    const onSubmit = jest.fn();
    render(<TaskForm onSubmit={onSubmit} />);
    fillForm({ dueDate: getFutureDate() });
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));
    await waitFor(() => expect(onSubmit).toHaveBeenCalledTimes(1));
    expect(onSubmit).toHaveBeenCalledWith(
      expect.objectContaining({
        title: 'Test Task',
        description: 'Test Description',
        priority: 'Medium',
        category: 'Work',
        dueDate: getFutureDate(),
      })
    );
  });

  // Test Case 3: Submit form with missing title
  test('Submit form with missing title', async () => {
    const onSubmit = jest.fn();
    render(<TaskForm onSubmit={onSubmit} />);
    fillForm({ title: '', dueDate: getFutureDate() });
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));
    await waitFor(() =>
      expect(screen.getByText(/title is required/i)).toBeInTheDocument()
    );
    expect(onSubmit).not.toHaveBeenCalled();
  });

  // Test Case 4: Submit form with missing category
  test('Submit form with missing category', async () => {
    const onSubmit = jest.fn();
    render(<TaskForm onSubmit={onSubmit} />);
    fillForm({ category: '', dueDate: getFutureDate() });
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));
    await waitFor(() =>
      expect(screen.getByText(/category is required/i)).toBeInTheDocument()
    );
    expect(onSubmit).not.toHaveBeenCalled();
  });

  // Test Case 5: Submit form with missing priority
  test('Submit form with missing priority', async () => {
    const onSubmit = jest.fn();
    render(<TaskForm onSubmit={onSubmit} />);
    fillForm({ priority: '', dueDate: getFutureDate() });
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));
    await waitFor(() =>
      expect(screen.getByText(/priority is required/i)).toBeInTheDocument()
    );
    expect(onSubmit).not.toHaveBeenCalled();
  });

  // Test Case 6: Submit form with empty description
  test('Submit form with empty description', async () => {
    const onSubmit = jest.fn();
    render(<TaskForm onSubmit={onSubmit} />);
    fillForm({ description: '', dueDate: getFutureDate() });
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));
    await waitFor(() => expect(onSubmit).toHaveBeenCalledTimes(1));
    expect(onSubmit).toHaveBeenCalledWith(
      expect.objectContaining({
        description: '',
      })
    );
  });

  // Test Case 7: Submit form with past due date
  test('Submit form with past due date', async () => {
    const onSubmit = jest.fn();
    render(<TaskForm onSubmit={onSubmit} />);
    fillForm({ dueDate: getPastDate() });
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));
    await waitFor(() =>
      expect(screen.getByText(/due date cannot be in the past/i)).toBeInTheDocument()
    );
    expect(onSubmit).not.toHaveBeenCalled();
  });

  // Test Case 8: Submit form with no due date
  test('Submit form with no due date', async () => {
    const onSubmit = jest.fn();
    render(<TaskForm onSubmit={onSubmit} />);
    fillForm({ dueDate: '' });
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));
    await waitFor(() => expect(onSubmit).toHaveBeenCalledTimes(1));
    expect(onSubmit).toHaveBeenCalledWith(
      expect.objectContaining({
        dueDate: expect.anything(),
      })
    );
  });

  // Test Case 9: Category field with special characters
  test('Category field with special characters', async () => {
    const onSubmit = jest.fn();
    render(<TaskForm onSubmit={onSubmit} />);
    fillForm({ category: '@Work#2024!', dueDate: getFutureDate() });
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));
    await waitFor(() => expect(onSubmit).toHaveBeenCalledTimes(1));
    expect(onSubmit).toHaveBeenCalledWith(
      expect.objectContaining({
        category: '@Work#2024!',
      })
    );
  });

  // Test Case 10: Title field at max allowed length
  test('Title field at max allowed length', async () => {
    const onSubmit = jest.fn();
    const maxTitle = 'a'.repeat(100);
    render(<TaskForm onSubmit={onSubmit} />);
    fillForm({ title: maxTitle, dueDate: getFutureDate() });
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));
    await waitFor(() => expect(onSubmit).toHaveBeenCalledTimes(1));
    expect(onSubmit).toHaveBeenCalledWith(
      expect.objectContaining({
        title: maxTitle,
      })
    );
  });

  // Test Case 11: Title field over max allowed length
  test('Title field over max allowed length', async () => {
    const onSubmit = jest.fn();
    const overMaxTitle = 'a'.repeat(101);
    render(<TaskForm onSubmit={onSubmit} />);
    fillForm({ title: overMaxTitle, dueDate: getFutureDate() });
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));
    await waitFor(() =>
      expect(screen.getByText(/title cannot exceed 100 characters/i)).toBeInTheDocument()
    );
    expect(onSubmit).not.toHaveBeenCalled();
  });

  // Test Case 12: Priority field options rendering
  test('Priority field options rendering', () => {
    render(<TaskForm onSubmit={jest.fn()} />);
    expect(screen.getByLabelText(/priority/i)).toBeInTheDocument();
    expect(screen.getByText(/low/i)).toBeInTheDocument();
    expect(screen.getByText(/medium/i)).toBeInTheDocument();
    expect(screen.getByText(/high/i)).toBeInTheDocument();
  });

  // Test Case 13: Category field options rendering
  test('Category field options rendering', () => {
    const categories = ['Work', 'Personal', 'Errand'];
    render(<TaskForm onSubmit={jest.fn()} categories={categories} />);
    categories.forEach(cat => {
      expect(screen.getByText(cat)).toBeInTheDocument();
    });
  });

  // Test Case 14: Form resets after successful submit
  test('Form resets after successful submit', async () => {
    const onSubmit = jest.fn();
    render(<TaskForm onSubmit={onSubmit} />);
    fillForm({ dueDate: getFutureDate() });
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));
    await waitFor(() => expect(onSubmit).toHaveBeenCalledTimes(1));
    expect(screen.getByLabelText(/title/i)).toHaveValue('');
    expect(screen.getByLabelText(/description/i)).toHaveValue('');
    expect(screen.getByLabelText(/priority/i)).toHaveValue('');
    expect(screen.getByLabelText(/category/i)).toHaveValue('');
    expect(screen.getByLabelText(/due date/i)).toHaveValue('');
  });

  // Test Case 15: Submit form with invalid priority value
  test('Submit form with invalid priority value', async () => {
    const onSubmit = jest.fn();
    render(<TaskForm onSubmit={onSubmit} />);
    fillForm({ priority: 'InvalidPriority', dueDate: getFutureDate() });
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));
    await waitFor(() =>
      expect(screen.getByText(/invalid priority/i)).toBeInTheDocument()
    );
    expect(onSubmit).not.toHaveBeenCalled();
  });

  // Test Case 16: Title field with only whitespace
  test('Title field with only whitespace', async () => {
    const onSubmit = jest.fn();
    render(<TaskForm onSubmit={onSubmit} />);
    fillForm({ title: '   ', dueDate: getFutureDate() });
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));
    await waitFor(() =>
      expect(screen.getByText(/title is required/i)).toBeInTheDocument()
    );
    expect(onSubmit).not.toHaveBeenCalled();
  });
});