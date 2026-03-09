import { api } from '../../../frontend/src/api';
import { TaskCreate } from '../../../frontend/src/api';

const API_URL = 'http://localhost:8000';

function mockFetch(response: any, ok = true, status = 200) {
  return jest.fn().mockResolvedValue({
    ok,
    status,
    json: jest.fn().mockResolvedValue(response),
  });
}

function mockFetchError(message: string, status = 400) {
  return jest.fn().mockResolvedValue({
    ok: false,
    status,
    json: jest.fn(),
    text: jest.fn().mockResolvedValue(message),
  });
}

describe('api.updateTask', () => {
  afterEach(() => {
    jest.resetAllMocks();
  });

  // Test Case 1: Update task with all valid fields
  it('Update task with all valid fields', async () => {
    const id = 'task123';
    const task: TaskCreate = {
      title: 'New Title',
      description: 'Updated description.',
      priority: 2 as any, // priority type mismatch in TaskCreate, but test case expects number
      due_date: '2024-07-10',
      tag: 'work' as any, // not in TaskCreate, but test case expects it
    };
    const response = {
      id,
      title: 'New Title',
      description: 'Updated description.',
      priority: 2,
      due_date: '2024-07-10',
      tag: 'work',
    };
    global.fetch = mockFetch(response);
    const result = await api.updateTask(id, task);
    expect(result).toEqual(response);
  });

  // Test Case 2: Update task omitting optional tag
  it('Update task omitting optional tag', async () => {
    const id = 'task456';
    const task: TaskCreate = {
      title: 'Buy groceries',
      description: 'Milk, eggs, bread.',
      priority: 1 as any,
      due_date: '2024-07-11',
    };
    const response = {
      id,
      title: 'Buy groceries',
      description: 'Milk, eggs, bread.',
      priority: 1,
      due_date: '2024-07-11',
    };
    global.fetch = mockFetch(response);
    const result = await api.updateTask(id, task);
    expect(result).toEqual(response);
    expect(result.tag).toBeUndefined();
  });

  // Test Case 3: Fail update when title is missing
  it('Fail update when title is missing', async () => {
    const id = 'task789';
    const task: any = {
      description: 'No title provided.',
      priority: 3,
      due_date: '2024-08-01',
    };
    global.fetch = mockFetchError('Title is required', 400);
    await expect(api.updateTask(id, task)).rejects.toThrow('Failed to update task');
  });

  // Test Case 4: Fail update when description is missing
  it('Fail update when description is missing', async () => {
    const id = 'task101';
    const task: any = {
      title: 'No Description',
      priority: 1,
      due_date: '2024-08-02',
    };
    global.fetch = mockFetchError('Description is required', 400);
    await expect(api.updateTask(id, task)).rejects.toThrow('Failed to update task');
  });

  // Test Case 5: Fail update when priority is missing
  it('Fail update when priority is missing', async () => {
    const id = 'task102';
    const task: any = {
      title: 'No Priority',
      description: 'Missing priority field.',
      due_date: '2024-08-03',
    };
    global.fetch = mockFetchError('Priority is required', 400);
    await expect(api.updateTask(id, task)).rejects.toThrow('Failed to update task');
  });

  // Test Case 6: Fail update when due date is missing
  it('Fail update when due date is missing', async () => {
    const id = 'task103';
    const task: any = {
      title: 'No Due Date',
      description: 'Missing due date field.',
      priority: 2,
    };
    global.fetch = mockFetchError('Due date is required', 400);
    await expect(api.updateTask(id, task)).rejects.toThrow('Failed to update task');
  });

  // Test Case 7: Fail update with extra fields present
  it('Fail update with extra fields present', async () => {
    const id = 'task104';
    const task: any = {
      title: 'Extra Field',
      description: 'Should not allow extra fields.',
      priority: 1,
      due_date: '2024-08-04',
      tag: 'home',
      unexpected_field: 'should_fail',
    };
    global.fetch = mockFetchError('Unexpected field: unexpected_field', 400);
    await expect(api.updateTask(id, task)).rejects.toThrow('Failed to update task');
  });

  // Test Case 8: Fail update with empty title
  it('Fail update with empty title', async () => {
    const id = 'task105';
    const task: any = {
      title: '',
      description: 'Empty title provided.',
      priority: 1,
      due_date: '2024-08-05',
    };
    global.fetch = mockFetchError('Title cannot be empty', 400);
    await expect(api.updateTask(id, task)).rejects.toThrow('Failed to update task');
  });

  // Test Case 9: Update task with maximum length title
  it('Update task with maximum length title', async () => {
    const id = 'task106';
    const maxTitle = 'T'.repeat(255);
    const task: TaskCreate = {
      title: maxTitle,
      description: 'Max length title.',
      priority: 1 as any,
      due_date: '2024-08-06',
    };
    const response = {
      id,
      title: maxTitle,
      description: 'Max length title.',
      priority: 1,
      due_date: '2024-08-06',
    };
    global.fetch = mockFetch(response);
    const result = await api.updateTask(id, task);
    expect(result).toEqual(response);
  });

  // Test Case 10: Update task with one character title
  it('Update task with one character title', async () => {
    const id = 'task107';
    const task: TaskCreate = {
      title: 'A',
      description: 'Single character title.',
      priority: 1 as any,
      due_date: '2024-08-07',
    };
    const response = {
      id,
      title: 'A',
      description: 'Single character title.',
      priority: 1,
      due_date: '2024-08-07',
    };
    global.fetch = mockFetch(response);
    const result = await api.updateTask(id, task);
    expect(result).toEqual(response);
  });

  // Test Case 11: Fail update with invalid priority type
  it('Fail update with invalid priority type', async () => {
    const id = 'task108';
    const task: any = {
      title: 'Invalid Priority',
      description: 'Priority is a string.',
      priority: 'high',
      due_date: '2024-08-08',
    };
    global.fetch = mockFetchError('Priority must be a number', 400);
    await expect(api.updateTask(id, task)).rejects.toThrow('Failed to update task');
  });

  // Test Case 12: Fail update with invalid due date format
  it('Fail update with invalid due date format', async () => {
    const id = 'task109';
    const task: any = {
      title: 'Invalid Due Date',
      description: 'Due date is not a date.',
      priority: 1,
      due_date: 'invalid-date',
    };
    global.fetch = mockFetchError('Due date must be a valid date', 400);
    await expect(api.updateTask(id, task)).rejects.toThrow('Failed to update task');
  });

  // Test Case 13: Fail update when task does not exist
  it('Fail update when task does not exist', async () => {
    const id = 'not_exist_id';
    const task: TaskCreate = {
      title: 'Nonexistent Task',
      description: 'Trying to update non-existent task.',
      priority: 2 as any,
      due_date: '2024-08-09',
    };
    global.fetch = mockFetchError('Task not found', 404);
    await expect(api.updateTask(id, task)).rejects.toThrow('Failed to update task');
  });

  // Test Case 14: Fail update when backend returns server error
  it('Fail update when backend returns server error', async () => {
    const id = 'task110';
    const task: TaskCreate = {
      title: 'Backend Error',
      description: 'Server should fail.',
      priority: 2 as any,
      due_date: '2024-08-10',
    };
    global.fetch = mockFetchError('Internal server error', 500);
    await expect(api.updateTask(id, task)).rejects.toThrow('Failed to update task');
  });

  // Test Case 15: Update task with tag as empty string
  it('Update task with tag as empty string', async () => {
    const id = 'task111';
    const task: TaskCreate = {
      title: 'Tag Empty',
      description: 'Tag is empty string.',
      priority: 1 as any,
      due_date: '2024-08-11',
      tag: '' as any,
    };
    const response = {
      id,
      title: 'Tag Empty',
      description: 'Tag is empty string.',
      priority: 1,
      due_date: '2024-08-11',
      tag: '',
    };
    global.fetch = mockFetch(response);
    const result = await api.updateTask(id, task);
    expect(result).toEqual(response);
  });
});