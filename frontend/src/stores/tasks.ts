import { defineStore } from 'pinia'
import { ref } from 'vue'
import type {
    TaskRead,
    TaskCreate,
    TaskUpdate,
    TaskMove
} from '@/interfaces'

import { tasksApi } from '@/api/tasks'

export const tasksStore = defineStore('tasks', () => {
    const tasks = ref<TaskRead[]>([]) // All tasks without status separation
    const isLoadingTasks = ref<boolean>(false)

    async function getTasks(): Promise<TaskRead[] | undefined> {
        isLoadingTasks.value = true
        try {
            const fetchedTasks: TaskRead[] = await tasksApi.getTasks()
            tasks.value = fetchedTasks
            return fetchedTasks
        } catch (error) {
            console.error(
                'Fetching tasks failed:',
                error instanceof Error ? error.message : 'Unknown error',
            )
            return
        } finally {
            isLoadingTasks.value = false
        }
    }

    async function getTask(id: number): Promise<TaskRead | undefined> {
        try {
            const fetchedTask: TaskRead = await tasksApi.getTaskById(id)
            return fetchedTask
        } catch (error) {
            console.error(
                'Fetching task by id failed:',
                error instanceof Error ? error.message : 'Unknown error',
            )
            return
        }
    }

    async function createTask(
        payload: TaskCreate
    ): Promise<TaskRead | undefined> {
        try {
            const createdTask: TaskRead = await tasksApi.createTask(payload)
            tasks.value.push(createdTask)
            return createdTask
        } catch (error) {
            console.error(
                'Creating task failed:',
                error instanceof Error ? error.message : 'Unknown error',
            )
            return
        }
    }

    async function updateTask(
        id: number, payload: TaskUpdate
    ): Promise<TaskRead | undefined> {
        try {
            const updatedTask: TaskRead = await tasksApi.updateTask(id, payload)
            tasks.value = tasks.value.map((task) => {
                return task.id === id ? updatedTask : task
            })
            return updatedTask
        } catch (error) {
            console.error(
                'Updating task failed:',
                error instanceof Error ? error.message : 'Unknown error',
            )
            return
        }
    }

    async function deleteTask(id: number): Promise<void> {
        try {
            await tasksApi.deleteTask(id)
            tasks.value = tasks.value.filter(task => task.id !== id)
        } catch (error) {
            console.error(
                'Deleting task failed:',
                error instanceof Error ? error.message : 'Unknown error',
            )
            return
        }
    }

    async function moveTask(
        id: number, payload: TaskMove
    ): Promise<TaskRead | undefined> {
        try {
            const movedTask = await tasksApi.moveTask(id, payload)
            tasks.value = tasks.value.map((task) => {
                return task.id === id ? movedTask : task
            })
            return movedTask
        } catch (error) {
            console.error(
                'Deleting task failed:',
                error instanceof Error ? error.message : 'Unknown error',
            )
            return
        }
    }

    return {
        tasks,
        getTasks,
        getTask,
        createTask,
        updateTask,
        deleteTask,
        moveTask
    }
})
