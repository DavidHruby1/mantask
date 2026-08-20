<script setup lang="ts">
// Get tasks and separate them into status columns
</script>

<template>
    <div class="box-border overflow-hidden flex flex-col min-h-0 h-full pl-2">
        <!-- KanbanControls -->
        <div>
            <div class="flex justify-between items-center bg-white p-4">
                <div>
                    <span>Selected Layers</span>
                </div>

                <div class="flex gap-3">
                    <input class="bg-gray-300"/>
                    <button type="button">Sort</button>
                    <button type="button">Filter</button>
                </div>
            </div>

            <div class="flex justify-start items-center gap-3 bg-white p-4 mt-2">
                <button type="button">Layers</button>
                <button type="button">My tasks</button>
            </div>
        </div>

        <!-- KanbanBoard -->
        <div class="kanban bg-white">
            <div>Col 1</div>
            <div>Col 2</div>
            <div>Col 3</div>
            <div>Col 4</div>
            <div>Col 5</div>
        </div>
    </div>
</template>

<style scoped>
.kanban {
    display: flex;
    min-height: 0;
    flex: 1;
    gap: 12px;
    margin-top: 0.5rem;
    overflow-x: auto;
}

.kanban > div {
    min-width: 20vw;
    height: 100%;
    background: red;
}
</style>
