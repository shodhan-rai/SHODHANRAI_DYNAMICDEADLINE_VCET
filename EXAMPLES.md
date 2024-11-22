# Example Inputs

### Assigning Initial Due Dates Based On Priority:
**Present Date: 2024-11-22**
- Create 4 tasks namely Task 1, Task 2, Task 3 and Task 4 in 'To do' section
- Assign Priorities:
  - Task 1 & Task 2: High Priority
  - Task 3: Mid Priority
  - Task 4: Low Priority
- Upon creating above tasks with said priorities, the due dates were automatically assigned as follows:
  - Task 1 and Task 2: Due date was assigned automatically as 2024-11-24(High Priority, 2 days from present date)
  - Task 3: Due date was assigned automatically as 2024-11-29(Mid Priority, 7 days from present date)
  - Task 4: Due date was assigned automatically as 2024-12-06(Low Priority, 14 days from present date)

### Extending Due Dates in 'In Progress' Section

- Scenario:
Initially 2 task are there in 'In Progress' section
- Initial State:
  - Task 3(Mid Priority), Due Date: 2024-11-29
  - Task 4(Low Priority), Due Date: 2024-12-06
 
- Action:
  - Move Task 1(High Priority), Due Date: 2024-11-24 from 'To do' section to 'In Progress' section

- Result:
The Due dates of Task 3 and Task 4 gets extended by 2 days
  - Task 3(Mid Priority), Due Date: 2024-12-01
  - Task 4(Low Priority), Due Date: 2024-12-08
 
- Final State of 'In Progress' Section:
  - Task 1(High Priority), Due Date: 2024-11-24
  - Task 3(Mid Priority), Due Date: 2024-11-29
  - Task 4(Low Priority), Due Date: 2024-12-06
