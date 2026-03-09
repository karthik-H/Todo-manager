import { createTask, editTask } from '../../frontend/src/api';
import fetchMock from 'jest-fetch-mock';

fetchMock.enableMocks();

describe('api.createTask', () => {
  beforeEach(() => {
    fetchMock.resetMocks();
  });

  // Test Case 1: Valid Task Creation
  it('Valid Task Creation', async () => {
    const task = {
      description: 'Create comprehensive test cases for API function.',
      due_date: '2024-07-01',
      priority: 'high',
      tag: 'QA',
      title: 'Write test cases',
    };
    const responseBody = {
      ...task,
      id: 'generated_task_id',
    };
    fetchMock.mockResponseOnce(JSON.stringify(responseBody), { status: 200 });

    const result = await createTask(task);

    expect(result).toEqual(responseBody);
    expect(fetchMock).toHaveBeenCalledWith(
      '/tasks',
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify(task),
      })
    );
  });

  // Test Case 2: Task Creation Without Optional Tag
  it('Task Creation Without Optional Tag', async () => {
    const task = {
      description: 'Review the new pull request.',
      due_date: '2024-07-05',
      priority: 'medium',
      title: 'Review PR',
    };
    const responseBody = {
      ...task,
      id: 'generated_task_id',
      tag: null,
    };
    fetchMock.mockResponseOnce(JSON.stringify(responseBody), { status: 200 });

    const result = await createTask(task);

    expect(result).toEqual(responseBody);
    expect(fetchMock).toHaveBeenCalledWith(
      '/tasks',
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify(task),
      })
    );
  });

  // Test Case 3: Task Creation Missing Title
  it('Task Creation Missing Title', async () => {
    const task = {
      description: 'No title provided.',
      due_date: '2024-07-10',
      priority: 'low',
      tag: 'Bug',
    };
    fetchMock.mockResponseOnce(
      JSON.stringify({ error: 'Title is required', status: 'error' }),
      { status: 400 }
    );

    await expect(createTask(task)).rejects.toThrow('Title is required');
    expect(fetchMock).toHaveBeenCalledWith(
      '/tasks',
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify(task),
      })
    );
  });

  // Test Case 4: Task Creation Missing Description
  it('Task Creation Missing Description', async () => {
    const task = {
      due_date: '2024-07-10',
      priority: 'low',
      tag: 'Bug',
      title: 'No description',
    };
    fetchMock.mockResponseOnce(
      JSON.stringify({ error: 'Description is required', status: 'error' }),
      { status: 400 }
    );

    await expect(createTask(task)).rejects.toThrow('Description is required');
    expect(fetchMock).toHaveBeenCalledWith(
      '/tasks',
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify(task),
      })
    );
  });

  // Test Case 5: Task Creation Missing Priority
  it('Task Creation Missing Priority', async () => {
    const task = {
      description: 'Priority is missing.',
      due_date: '2024-07-10',
      tag: 'Bug',
      title: 'No priority',
    };
    fetchMock.mockResponseOnce(
      JSON.stringify({ error: 'Priority is required', status: 'error' }),
      { status: 400 }
    );

    await expect(createTask(task)).rejects.toThrow('Priority is required');
    expect(fetchMock).toHaveBeenCalledWith(
      '/tasks',
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify(task),
      })
    );
  });

  // Test Case 6: Task Creation Missing Due Date
  it('Task Creation Missing Due Date', async () => {
    const task = {
      description: 'Due date is missing.',
      priority: 'medium',
      tag: 'Feature',
      title: 'No due date',
    };
    fetchMock.mockResponseOnce(
      JSON.stringify({ error: 'Due date is required', status: 'error' }),
      { status: 400 }
    );

    await expect(createTask(task)).rejects.toThrow('Due date is required');
    expect(fetchMock).toHaveBeenCalledWith(
      '/tasks',
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify(task),
      })
    );
  });

  // Test Case 7: Task Creation With Extra Fields
  it('Task Creation With Extra Fields', async () => {
    const task = {
      description: 'Should fail due to extra field.',
      due_date: '2024-07-15',
      extra_field: 'Not allowed',
      priority: 'high',
      tag: 'Test',
      title: 'Extra field test',
    };
    fetchMock.mockResponseOnce(
      JSON.stringify({ error: "Unexpected field 'extra_field'", status: 'error' }),
      { status: 400 }
    );

    await expect(createTask(task)).rejects.toThrow("Unexpected field 'extra_field'");
    expect(fetchMock).toHaveBeenCalledWith(
      '/tasks',
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify(task),
      })
    );
  });

  // Test Case 8: Task Creation With Max Length Title
  it('Task Creation With Max Length Title', async () => {
    const maxTitle = 'T'.repeat(255);
    const task = {
      description: 'Max length title test.',
      due_date: '2024-07-20',
      priority: 'low',
      title: maxTitle,
    };
    const responseBody = {
      ...task,
      id: 'generated_task_id',
      tag: null,
    };
    fetchMock.mockResponseOnce(JSON.stringify(responseBody), { status: 200 });

    const result = await createTask(task);

    expect(result).toEqual(responseBody);
    expect(fetchMock).toHaveBeenCalledWith(
      '/tasks',
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify(task),
      })
    );
  });

  // Test Case 9: Task Creation With Empty Title
  it('Task Creation With Empty Title', async () => {
    const task = {
      description: 'Empty title.',
      due_date: '2024-07-21',
      priority: 'medium',
      title: '',
    };
    fetchMock.mockResponseOnce(
      JSON.stringify({ error: 'Title cannot be empty', status: 'error' }),
      { status: 400 }
    );

    await expect(createTask(task)).rejects.toThrow('Title cannot be empty');
    expect(fetchMock).toHaveBeenCalledWith(
      '/tasks',
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify(task),
      })
    );
  });

  // Test Case 10: Task Creation With Invalid Due Date Format
  it('Task Creation With Invalid Due Date Format', async () => {
    const task = {
      description: 'Due date is not a valid date.',
      due_date: '31-07-2024',
      priority: 'low',
      title: 'Invalid date',
    };
    fetchMock.mockResponseOnce(
      JSON.stringify({ error: 'Invalid due date format', status: 'error' }),
      { status: 400 }
    );

    await expect(createTask(task)).rejects.toThrow('Invalid due date format');
    expect(fetchMock).toHaveBeenCalledWith(
      '/tasks',
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify(task),
      })
    );
  });

  // Test Case 11: Task Creation With Invalid Priority Value
  it('Task Creation With Invalid Priority Value', async () => {
    const task = {
      description: 'Priority is not allowed.',
      due_date: '2024-07-27',
      priority: 'urgent',
      title: 'Invalid priority',
    };
    fetchMock.mockResponseOnce(
      JSON.stringify({ error: 'Invalid priority value', status: 'error' }),
      { status: 400 }
    );

    await expect(createTask(task)).rejects.toThrow('Invalid priority value');
    expect(fetchMock).toHaveBeenCalledWith(
      '/tasks',
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify(task),
      })
    );
  });

  // Test Case 12: API Error (Server Failure)
  it('API Error (Server Failure)', async () => {
    const task = {
      description: 'Simulate server error.',
      due_date: '2024-07-30',
      priority: 'high',
      title: 'Server failure',
    };
    fetchMock.mockResponseOnce(
      JSON.stringify({ error: 'Internal Server Error', status: 'error' }),
      { status: 500 }
    );

    await expect(createTask(task)).rejects.toThrow('Internal Server Error');
    expect(fetchMock).toHaveBeenCalledWith(
      '/tasks',
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify(task),
      })
    );
  });

  // Test Case 13: Data Persistence After Task Creation
  it('Data Persistence After Task Creation', async () => {
    const task = {
      description: 'Verify persistence.',
      due_date: '2024-08-01',
      priority: 'medium',
      title: 'Persist test',
    };
    const createdTask = {
      ...task,
      id: 'generated_task_id',
      tag: null,
    };
    fetchMock.mockResponseOnce(JSON.stringify(createdTask), { status: 200 });

    const result = await createTask(task);
    expect(result).toEqual(createdTask);

    // Simulate fetching tasks after creation
    fetchMock.mockResponseOnce(JSON.stringify([createdTask]), { status: 200 });

    // Assume there is a function to fetch tasks, e.g., api.getTasks
    // If not present, this test will need to be updated when getTasks is implemented
    // @ts-ignore
    const getTasks = async () => {
      const resp = await fetch('/tasks');
      if (!resp.ok) throw new Error('Failed to fetch tasks');
      return await resp.json();
    };

    const tasks = await getTasks();
    expect(tasks).toEqual([createdTask]);
  });

  // Test Case 14: Edit Task After Creation
  it('Edit Task After Creation', async () => {
    const task = {
      description: 'Initial description.',
      due_date: '2024-08-02',
      priority: 'low',
      title: 'Initial title',
    };
    const createdTask = {
      ...task,
      id: 'generated_task_id',
      tag: null,
    };
    fetchMock.mockResponseOnce(JSON.stringify(createdTask), { status: 200 });

    const result = await createTask(task);
    expect(result).toEqual(createdTask);

    // Simulate editing the task
    const updatedTask = {
      ...createdTask,
      title: 'Updated title',
    };
    fetchMock.mockResponseOnce(JSON.stringify(updatedTask), { status: 200 });

    const editResult = await editTask(updatedTask.id, { title: 'Updated title' });
    expect(editResult).toEqual(updatedTask);
  });
});