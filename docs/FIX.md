# Follow-Up Fixes

## HIGH #28: Broken post-authentication navigation

`frontend/src/views/Login.vue` and `frontend/src/views/Bootstrap.vue` navigate
to the removed `dashboard` route after a successful login or bootstrap. Update
them to a valid application route.

## HIGH #30: Modal submits a stale column status

`AddTaskModal` initializes its local `status` only once. Opening the already
mounted modal from `To do` or `In progress` can display that status but submit
the previous value. Synchronize or reset the status when the modal opens.

## MEDIUM #30: Failed task creation is treated as success

`createTask()` returns `undefined` when the API request fails, but the modal
still refreshes, clears the title, and closes. Keep the form open and show an
error unless a task was created.

## MEDIUM #29: Inactive Kanban controls are rendered

Kanban renders Search, Sort, Filter, Layers, and My tasks controls without
state or handlers. Hide them until their behavior is implemented.

## MEDIUM: Session dependency test uses stale argument order

`backend/tests/api/test_dependencies.py` calls `get_current_session()` with
the session token before the `Response`. The dependency now accepts the
`Response` before the token, so the test fails while trying to call
`set_cookie()` on a string. Update the test invocation to match the current
function signature.
