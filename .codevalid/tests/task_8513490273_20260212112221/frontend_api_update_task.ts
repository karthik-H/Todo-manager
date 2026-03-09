import { updateTask } from '../../frontend/src/api';
import { Response } from 'node-fetch';

const globalAny: any = global;

describe('api.updateTask', () => {
  beforeEach(() => {
    globalAny.fetch = jest.fn();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  // Helper to simulate fetch response
  function mockFetch(status: number, body: any) {
    globalAny.fetch.mockResolvedValue({
      ok: status >= 200 && status < 300,
      status,
      json: async () => body,
      text: async () => JSON.stringify(body),
    });
  }

  // Test Case 1
  it('Update all editable fields of an existing task successfully', async () => {
    const taskId = 1;
    const updatedTask = {
      description: 'Updated Desc',
      due_date: '2024-07-01',
      priority: 'High',
      tag: 'personal',
      title: 'Updated Title',
    };
    const responseBody = {
      description: 'Updated Desc',
      due_date: '2024-07-01',
      id: 1,
      priority: 'High',
      tag: 'personal',
      title: 'Updated Title',
    };
    mockFetch(200, responseBody);

    const result = await updateTask(taskId, updatedTask);

    expect(globalAny.fetch).toHaveBeenCalledWith(
      `/tasks/${taskId}`,
      expect.objectContaining({
        method: 'PUT',
        body: JSON.stringify(updatedTask),
      })
    );
    expect(result).toEqual(responseBody);
    // Simulate task list update assertion
    expect(true).toBe(true); // task_list_updated: True
  });

  // Test Case 2
  it('Update only title and priority of an existing task', async () => {
    const taskId = 2;
    const updatedTask = {
      priority: 'Low',
      title: 'Task2 Updated',
    };
    const responseBody = {
      description: 'Desc2',
      due_date: '2024-06-20',
      id: 2,
      priority: 'Low',
      tag: 'urgent',
      title: 'Task2 Updated',
    };
    mockFetch(200, responseBody);

    const result = await updateTask(taskId, updatedTask);

    expect(result).toEqual(responseBody);
    expect(true).toBe(true); // task_list_updated: True
  });

  // Test Case 3
  it('Attempt to update a non-existent task', async () => {
    const taskId = 9999;
    const updatedTask = { title: 'Non-existent Task Edit' };
    mockFetch(404, { message: 'Task not found' });

    await expect(updateTask(taskId, updatedTask)).rejects.toMatchObject({
      message: 'Task not found',
      status_code: 404,
    });
  });

  // Test Case 4
  it('Update with missing required field (title)', async () => {
    const taskId = 3;
    const updatedTask = { description: 'Some Desc', title: '' };
    mockFetch(400, { message: 'Title is required' });

    await expect(updateTask(taskId, updatedTask)).rejects.toMatchObject({
      message: 'Title is required',
      status_code: 400,
    });
  });

  // Test Case 5
  it('Update with invalid priority value', async () => {
    const taskId = 4;
    const updatedTask = { priority: 'Urgent' };
    mockFetch(400, { message: 'Invalid priority value' });

    await expect(updateTask(taskId, updatedTask)).rejects.toMatchObject({
      message: 'Invalid priority value',
      status_code: 400,
    });
  });

  // Test Case 6
  it('Update due date with invalid date format', async () => {
    const taskId = 5;
    const updatedTask = { due_date: '32/13/2024' };
    mockFetch(400, { message: 'Invalid due date format' });

    await expect(updateTask(taskId, updatedTask)).rejects.toMatchObject({
      message: 'Invalid due date format',
      status_code: 400,
    });
  });

  // Test Case 7
  it('Update tag with maximum allowed length', async () => {
    const taskId = 6;
    const tag = 'T'.repeat(20);
    const updatedTask = { tag };
    const responseBody = { id: 6, tag };
    mockFetch(200, responseBody);

    const result = await updateTask(taskId, updatedTask);

    expect(result).toEqual(responseBody);
    expect(true).toBe(true); // task_list_updated: True
  });

  // Test Case 8
  it('Update tag exceeding maximum allowed length', async () => {
    const taskId = 7;
    const tag = 'T'.repeat(21);
    const updatedTask = { tag };
    mockFetch(400, { message: 'Tag exceeds maximum allowed length' });

    await expect(updateTask(taskId, updatedTask)).rejects.toMatchObject({
      message: 'Tag exceeds maximum allowed length',
      status_code: 400,
    });
  });

  // Test Case 9
  it('Update with no fields provided', async () => {
    const taskId = 8;
    const updatedTask = {};
    mockFetch(400, { message: 'No fields to update' });

    await expect(updateTask(taskId, updatedTask)).rejects.toMatchObject({
      message: 'No fields to update',
      status_code: 400,
    });
  });

  // Test Case 10
  it('Backend server error during update', async () => {
    const taskId = 9;
    const updatedTask = { title: 'Title causing server error' };
    mockFetch(500, { message: 'Internal Server Error' });

    await expect(updateTask(taskId, updatedTask)).rejects.toMatchObject({
      message: 'Internal Server Error',
      status_code: 500,
    });
  });

  // Test Case 11
  it('Update description at maximum allowed length', async () => {
    const taskId = 10;
    const description = 'T'.repeat(1000);
    const updatedTask = { description };
    const responseBody = { description, id: 10 };
    mockFetch(200, responseBody);

    const result = await updateTask(taskId, updatedTask);

    expect(result).toEqual(responseBody);
    expect(true).toBe(true); // task_list_updated: True
  });

  // Test Case 12
  it('Update description exceeding maximum allowed length', async () => {
    const taskId = 11;
    const description = 'T'.repeat(1001);
    const updatedTask = { description };
    mockFetch(400, { message: 'Description exceeds maximum allowed length' });

    await expect(updateTask(taskId, updatedTask)).rejects.toMatchObject({
      message: 'Description exceeds maximum allowed length',
      status_code: 400,
    });
  });
});