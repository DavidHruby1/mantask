import { api } from '@/api/client'

import type {
    TaskCreate,
    TaskRead,
    TaskUpdate,
    TaskMove
} from '@/interfaces/index'

export const tasksApi = {
    async getTasks(): Promise<TaskRead[]> {
        const response = await api.get<TaskRead[]>('/api/tasks')
        return response.data
    },
    async getTaskById(id: number): Promise<TaskRead> {
        const response = await api.get<TaskRead>(`/api/tasks/${id}`)
        return response.data
    },
    async createTask(payload: TaskCreate): Promise<TaskRead> {
        const response = await api.post<TaskRead>('/api/tasks', payload)
        return response.data
    },
    async updateTask(id: number, payload: TaskUpdate): Promise<TaskRead> {
        const response = await api.patch<TaskRead>(`/api/tasks/${id}`, payload)
        return response.data
    },
    async deleteTask(id: number): Promise<void> {
        await api.delete(`/api/tasks/${id}`)
    },
    async moveTask(id: number, payload: TaskMove): Promise<TaskRead> {
        const response = await api.patch<TaskRead>(`/api/tasks/${id}/move`, payload)
        return response.data
    }
}
