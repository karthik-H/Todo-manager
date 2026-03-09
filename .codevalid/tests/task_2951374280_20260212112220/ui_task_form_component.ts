import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import TaskForm from '../../../frontend/src/components/TaskForm';
import { act } from 'react-dom/test-utils';

const defaultProps = {
  onSubmit: jest.fn(),
  onCancel: jest.fn(),
  initialValues: undefined,
};

const fillForm = ({
  title = 'Test Task',
  description = 'Test Description',
  priority = 'High',
  category = 'Work',
  dueDate = '2026-03-10',
  tag = 'Urgent',
} = {}) => {
  fireEvent.change(screen.getByLabelText(/title/i), { target: { value: title } });
  if (screen.queryByLabelText(/description/i)) {
    fireEvent.change(screen.getByLabelText(/description/i), { target: { value: description } });
  }
  if (screen.queryByLabelText(/priority/i)) {
    fireEvent.change(screen.getByLabelText(/priority/i), { target: { value: priority } });
  }
  if (screen.queryByLabelText(/category/i)) {
    fireEvent.change(screen.getByLabelText(/category/i), { target: { value: category } });
  }
  if (screen.queryByLabelText(/due date/i)) {
    fireEvent.change(screen.getByLabelText(/due date/i), { target: { value: dueDate } });
  }
  if (screen.queryByLabelText(/tag/i)) {
    fireEvent.change(screen.getByLabelText(/tag/i), { target: { value: tag } });
  }
};

describe('TaskForm Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  // Test Case 1: Render all form fields
  it('Render all form fields', () => {
    render(<TaskForm {...defaultProps} />);
    expect(screen.getByLabelText(/title/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/description/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/priority/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/category/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/due date/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/tag/i)).toBeInTheDocument();
  });

  // Test Case 2: Submit form with all fields filled
  it('Submit form with all fields filled', async () => {
    render(<TaskForm {...defaultProps} />);
    fillForm();
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));
    await waitFor(() =>
      expect(defaultProps.onSubmit).toHaveBeenCalledWith({
        title: 'Test Task',
        description: 'Test Description',
        priority: 'High',
        category: 'Work',
        dueDate: '2026-03-10',
        tag: 'Urgent',
        completed: false,
      })
    );
    expect(defaultProps.onSubmit).toHaveBeenCalledTimes(1);
  });

  // Test Case 3: Form submission fails if title is missing
  it('Form submission fails if title is missing', async () => {
    render(<TaskForm {...defaultProps} />);
    fillForm({ title: '' });
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));
    await waitFor(() =>
      expect(defaultProps.onSubmit).not.toHaveBeenCalled()
    );
    expect(screen.getByText(/title is required/i)).toBeInTheDocument();
  });

  // Test Case 4: Form submission with missing description
  it('Form submission with missing description', async () => {
    render(<TaskForm {...defaultProps} />);
    fillForm({ description: '' });
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));
    await waitFor(() => {
      expect(defaultProps.onSubmit).toHaveBeenCalledWith(
        expect.objectContaining({ description: '' })
      );
    });
  });

  // Test Case 5: Form submission fails if priority is missing
  it('Form submission fails if priority is missing', async () => {
    render(<TaskForm {...defaultProps} />);
    fillForm({ priority: '' });
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));
    await waitFor(() =>
      expect(defaultProps.onSubmit).not.toHaveBeenCalled()
    );
    expect(screen.getByText(/priority is required/i)).toBeInTheDocument();
  });

  // Test Case 6: Form submission fails if due date is missing
  it('Form submission fails if due date is missing', async () => {
    render(<TaskForm {...defaultProps} />);
    fillForm({ dueDate: '' });
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));
    await waitFor(() =>
      expect(defaultProps.onSubmit).not.toHaveBeenCalled()
    );
    expect(screen.getByText(/due date is required/i)).toBeInTheDocument();
  });

  // Test Case 7: Form submission with missing tag (optional field)
  it('Form submission with missing tag (optional field)', async () => {
    render(<TaskForm {...defaultProps} />);
    fillForm({ tag: '' });
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));
    await waitFor(() =>
      expect(defaultProps.onSubmit).toHaveBeenCalledWith(
        expect.objectContaining({ tag: '' })
      )
    );
  });

  // Test Case 8: Cancel button calls onCancel
  it('Cancel button calls onCancel', () => {
    render(<TaskForm {...defaultProps} />);
    fireEvent.click(screen.getByRole('button', { name: /cancel/i }));
    expect(defaultProps.onCancel).toHaveBeenCalledTimes(1);
  });

  // Test Case 9: Title field maximum length edge case
  it('Title field maximum length edge case', async () => {
    const maxTitle = 'a'.repeat(255);
    render(<TaskForm {...defaultProps} />);
    fillForm({ title: maxTitle });
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));
    await waitFor(() =>
      expect(defaultProps.onSubmit).toHaveBeenCalledWith(
        expect.objectContaining({ title: maxTitle })
      )
    );
  });

  // Test Case 10: Edge case: Due date in the past
  it('Edge case: Due date in the past', async () => {
    render(<TaskForm {...defaultProps} />);
    fillForm({ dueDate: '2020-01-01' });
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));
    // If allowed, onSubmit is called; if not, error is shown
    await waitFor(() => {
      const error = screen.queryByText(/due date cannot be in the past/i);
      if (error) {
        expect(defaultProps.onSubmit).not.toHaveBeenCalled();
        expect(error).toBeInTheDocument();
      } else {
        expect(defaultProps.onSubmit).toHaveBeenCalled();
      }
    });
  });

  // Test Case 11: Invalid priority value input
  it('Invalid priority value input', async () => {
    render(<TaskForm {...defaultProps} />);
    fillForm({ priority: 'InvalidPriority' });
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));
    await waitFor(() =>
      expect(defaultProps.onSubmit).not.toHaveBeenCalled()
    );
    expect(screen.getByText(/priority is invalid/i)).toBeInTheDocument();
  });

  // Test Case 12: Submitting with extra field in form state
  it('Submitting with extra field in form state', async () => {
    render(<TaskForm {...defaultProps} />);
    fillForm();
    // Simulate extra field in state
    // @ts-ignore
    screen.getByLabelText(/title/i).value = 'Test Task';
    // @ts-ignore
    screen.getByLabelText(/description/i).value = 'Test Description';
    // @ts-ignore
    screen.getByLabelText(/priority/i).value = 'High';
    // @ts-ignore
    screen.getByLabelText(/category/i).value = 'Work';
    // @ts-ignore
    screen.getByLabelText(/due date/i).value = '2026-03-10';
    // @ts-ignore
    screen.getByLabelText(/tag/i).value = 'Urgent';
    // Simulate extra field
    const form = screen.getByTestId('task-form');
    // @ts-ignore
    form.extraField = 'shouldBeIgnored';
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));
    await waitFor(() =>
      expect(defaultProps.onSubmit).toHaveBeenCalledWith(
        expect.not.objectContaining({ extraField: 'shouldBeIgnored' })
      )
    );
  });

  // Test Case 13: Edit mode shows prefilled values
  it('Edit mode shows prefilled values', () => {
    const initialValues = {
      title: 'Edit Task',
      description: 'Edit Description',
      priority: 'Medium',
      category: 'Personal',
      dueDate: '2026-03-15',
      tag: 'Home',
      completed: true,
    };
    render(<TaskForm {...defaultProps} initialValues={initialValues} />);
    expect(screen.getByLabelText(/title/i)).toHaveValue('Edit Task');
    expect(screen.getByLabelText(/description/i)).toHaveValue('Edit Description');
    expect(screen.getByLabelText(/priority/i)).toHaveValue('Medium');
    expect(screen.getByLabelText(/category/i)).toHaveValue('Personal');
    expect(screen.getByLabelText(/due date/i)).toHaveValue('2026-03-15');
    expect(screen.getByLabelText(/tag/i)).toHaveValue('Home');
  });

  // Test Case 14: Edit existing task and submit changes
  it('Edit existing task and submit changes', async () => {
    const initialValues = {
      title: 'Edit Task',
      description: 'Edit Description',
      priority: 'Medium',
      category: 'Personal',
      dueDate: '2026-03-15',
      tag: 'Home',
      completed: true,
    };
    render(<TaskForm {...defaultProps} initialValues={initialValues} />);
    fireEvent.change(screen.getByLabelText(/title/i), { target: { value: 'Updated Task' } });
    fireEvent.change(screen.getByLabelText(/due date/i), { target: { value: '2026-03-20' } });
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));
    await waitFor(() =>
      expect(defaultProps.onSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Updated Task',
          dueDate: '2026-03-20',
          description: 'Edit Description',
          priority: 'Medium',
          category: 'Personal',
          tag: 'Home',
        })
      )
    );
  });

  // Test Case 15: Title field with only whitespace
  it('Title field with only whitespace', async () => {
    render(<TaskForm {...defaultProps} />);
    fillForm({ title: '   ' });
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));
    await waitFor(() =>
      expect(defaultProps.onSubmit).not.toHaveBeenCalled()
    );
    expect(screen.getByText(/title is required/i)).toBeInTheDocument();
  });

  // Test Case 16: Form resets after successful submission
  it('Form resets after successful submission', async () => {
    render(<TaskForm {...defaultProps} />);
    fillForm();
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));
    await waitFor(() => expect(defaultProps.onSubmit).toHaveBeenCalled());
    expect(screen.getByLabelText(/title/i)).toHaveValue('');
    expect(screen.getByLabelText(/description/i)).toHaveValue('');
    expect(screen.getByLabelText(/priority/i)).toHaveValue('');
    expect(screen.getByLabelText(/category/i)).toHaveValue('');
    expect(screen.getByLabelText(/due date/i)).toHaveValue('');
    expect(screen.getByLabelText(/tag/i)).toHaveValue('');
  });

  // Test Case 17: Cancel resets form fields
  it('Cancel resets form fields', async () => {
    render(<TaskForm {...defaultProps} />);
    fillForm();
    fireEvent.click(screen.getByRole('button', { name: /cancel/i }));
    expect(screen.getByLabelText(/title/i)).toHaveValue('');
    expect(screen.getByLabelText(/description/i)).toHaveValue('');
    expect(screen.getByLabelText(/priority/i)).toHaveValue('');
    expect(screen.getByLabelText(/category/i)).toHaveValue('');
    expect(screen.getByLabelText(/due date/i)).toHaveValue('');
    expect(screen.getByLabelText(/tag/i)).toHaveValue('');
  });
});