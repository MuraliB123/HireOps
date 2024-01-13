import numpy as np
import matplotlib.pyplot as plt
class TaskData:
    def __init__(self, task,m_index, expertise, hours, urgency):
        self.task = task
        self.m_index = m_index
        self.expertise = expertise
        self.hours = hours
        self.urgency = urgency


def expertise_function(x):
    return x*2  


def urgency_function(x):
    return x/8 

def calculate_credit_score(tasks):
    manager_weight = 2.5
    expertise_weight = 2.5
    hours_weight = 2.5
    urgency_weight = 2.5
    total_available_hours = 8
    total_score = 0.0
    allotted_hours = 0
    for task in tasks:
        normalized_manager_index = task.m_index/ 10.0
        normalized_expertise = expertise_function(task.expertise / 10.0)
        normalized_hours = (total_available_hours-task.hours) / 10.0
        normalized_urgency = urgency_function((10-task.urgency) / 10.0)
        allotted_hours = allotted_hours + task.hours 
        
        task_score = (
            manager_weight * normalized_manager_index +
            expertise_weight * normalized_expertise +
            hours_weight * normalized_hours +
            urgency_weight * normalized_urgency
        )

        total_score += task_score

    
    overall_credit_score = total_score / len(tasks) + (total_available_hours - allotted_hours)

    return overall_credit_score

tasks = [
    TaskData("Task1",5,5,5,9),
    TaskData("Task2",9,9,3,8) 
]


output = calculate_credit_score(tasks)

print(output)



