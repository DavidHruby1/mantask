<script setup lang="ts">
import { onMounted } from 'vue'
import { TaskStatus, type TaskCreate, type TaskRead } from '@/interfaces'
import { tasksStore } from '@/stores/tasks'

const taskStore = tasksStore()

type EntryTaskStatus = NonNullable<TaskCreate['status']>

const columns: { title: string; status: TaskStatus; createStatus?: EntryTaskStatus }[] = [
    { title: 'Backlog', status: TaskStatus.BACKLOG, createStatus: TaskStatus.BACKLOG },
    { title: 'To do', status: TaskStatus.TODO, createStatus: TaskStatus.TODO },
    { title: 'In progress', status: TaskStatus.IN_PROGRESS, createStatus: TaskStatus.IN_PROGRESS },
    { title: 'Review', status: TaskStatus.REVIEW },
    { title: 'Done', status: TaskStatus.DONE },
]

// Creates one minimal task in the requested entry column through the shared task store.
// Browser prompts keep this temporary testing UI free from a form or modal implementation.
async function createTask(status?: EntryTaskStatus): Promise<void> {
    const title = window.prompt('Task title')?.trim()

    if (!title) {
        return
    }

    await taskStore.createTask({ title, status, should_review: false })
}

// Updates only the task title through the shared store.
// The task is reloaded after a failed update so the board does not retain an unsaved title.
async function updateTask(task: TaskRead): Promise<void> {
    const title = window.prompt('Task title', task.title)?.trim()

    if (!title || title === task.title) {
        return
    }

    const updatedTask = await taskStore.updateTask(task.id, { title })

    if (!updatedTask) {
        await taskStore.getTasks()
    }
}

// Deletes the selected task only after the browser confirmation.
// No local state is changed here because the store removes it after a successful API response.
async function deleteTask(task: TaskRead): Promise<void> {
    if (!window.confirm(`Delete "${task.title}"?`)) {
        return
    }

    await taskStore.deleteTask(task.id)
}

onMounted(() => {
    void taskStore.getTasks()
})
</script>

<template>
    <div class="app-shell">
        <aside class="dashboard-navigation">
            <section class="user-profile" aria-label="User profile">
                <div class="avatar">U</div>
                <div>
                    <strong>User name</strong>
                    <span>user@example.com</span>
                </div>
            </section>

            <label class="team-switcher">
                Workspace
                <select>
                    <option>My workspace</option>
                </select>
            </label>

            <nav class="nav-menu" aria-label="Dashboard navigation">
                <button type="button" @click="createTask()">+ Add Task</button>
            </nav>
        </aside>

        <section class="dashboard-workspace">
            <header class="dashboard-topbar">
                <input type="search" placeholder="Search tasks" aria-label="Search tasks" />

                <div class="topbar-actions">
                    <button type="button">Manual order</button>
                    <button type="button">Filters (0)</button>
                </div>
            </header>

            <main class="kanban-container">
                <div class="kanban-toolbar">
                    <button type="button">All layers</button>

                    <label class="my-tasks-switch">
                        <input type="checkbox" />
                        My tasks
                    </label>
                </div>

                <section class="kanban-board" aria-label="Kanban board">
                    <article v-for="column in columns" :key="column.status" class="kanban-column">
                        <header>
                            <h2>{{ column.title }}</h2>
                            <span>
                                {{
                                    taskStore.tasks.filter((task) => task.status === column.status)
                                        .length
                                }}
                            </span>
                            <button
                                v-if="column.createStatus"
                                type="button"
                                :aria-label="`Add task to ${column.title}`"
                                @click="createTask(column.createStatus)"
                            >
                                +
                            </button>
                        </header>
                        <div
                            v-for="task in taskStore.tasks.filter(
                                (task) => task.status === column.status,
                            )"
                            :key="task.id"
                            class="task-card"
                        >
                            <strong>{{ task.title }}</strong>
                            <div class="task-actions">
                                <button type="button" @click="updateTask(task)">Edit</button>
                                <button type="button" @click="deleteTask(task)">Delete</button>
                            </div>
                        </div>
                        <p
                            v-if="!taskStore.tasks.some((task) => task.status === column.status)"
                            class="empty-state"
                        >
                            No tasks
                        </p>
                    </article>
                </section>
            </main>
        </section>

        <aside class="filter-sidebar" aria-label="Filters">
            <header>
                <h2>Filters</h2>
                <button type="button" aria-label="Close filters">x</button>
            </header>
            <button type="button">Clear all</button>
            <p>Filter controls will be added here.</p>
        </aside>
    </div>
</template>

<style scoped>
.app-shell {
    display: grid;
    grid-template-columns: 240px minmax(0, 1fr);
    min-height: 100vh;
    color: rgba(235, 237, 242, 0.9);
}

.dashboard-navigation {
    display: flex;
    flex-direction: column;
    gap: 24px;
    padding: 24px;
    border-right: 1px solid rgba(235, 237, 242, 0.18);
}

.user-profile {
    display: flex;
    align-items: center;
    gap: 12px;
}

.avatar {
    display: grid;
    width: 36px;
    height: 36px;
    place-items: center;
    border: 1px solid rgba(235, 237, 242, 0.5);
    border-radius: 50%;
}

.user-profile span,
.team-switcher,
.empty-state,
.filter-sidebar p {
    display: block;
    color: rgba(235, 237, 242, 0.6);
    font-size: 0.875rem;
}

.team-switcher {
    display: grid;
    gap: 6px;
}

.dashboard-workspace {
    min-width: 0;
}

.dashboard-topbar,
.kanban-toolbar,
.kanban-column > header,
.filter-sidebar > header {
    display: flex;
    align-items: center;
    gap: 12px;
}

.dashboard-topbar {
    justify-content: space-between;
    padding: 20px 24px;
    border-bottom: 1px solid rgba(235, 237, 242, 0.18);
}

.dashboard-topbar input {
    width: 280px;
}

.topbar-actions {
    display: flex;
    gap: 8px;
}

.kanban-container {
    padding: 24px;
}

.kanban-toolbar {
    margin-bottom: 16px;
}

.my-tasks-switch {
    display: flex;
    align-items: center;
    gap: 6px;
}

.kanban-board {
    display: grid;
    grid-template-columns: repeat(5, minmax(220px, 1fr));
    gap: 16px;
    overflow-x: auto;
}

.kanban-column {
    min-height: 420px;
    padding: 12px;
    border: 1px solid rgba(235, 237, 242, 0.18);
}

.kanban-column > header h2 {
    margin: 0;
    font-size: 1rem;
}

.kanban-column > header span {
    color: rgba(235, 237, 242, 0.6);
}

.kanban-column > header button {
    margin-left: auto;
}

.empty-state {
    margin-top: 24px;
    text-align: center;
}

.task-card {
    display: grid;
    gap: 12px;
    margin-top: 12px;
    padding: 12px;
    border: 1px solid rgba(235, 237, 242, 0.3);
}

.task-actions {
    display: flex;
    gap: 8px;
}

.filter-sidebar {
    position: fixed;
    top: 0;
    right: 0;
    display: none;
    width: min(360px, 100vw);
    min-height: 100vh;
    padding: 24px;
    background: #080808;
    border-left: 1px solid rgba(235, 237, 242, 0.18);
}

.filter-sidebar > header {
    justify-content: space-between;
}

.filter-sidebar h2 {
    margin: 0;
    font-size: 1rem;
}

button,
input,
select {
    padding: 8px 10px;
    color: rgba(235, 237, 242, 0.9);
    font: inherit;
    background: transparent;
    border: 1px solid rgba(235, 237, 242, 0.3);
}

button {
    cursor: pointer;
}

input::placeholder {
    color: rgba(235, 237, 242, 0.5);
}
</style>
