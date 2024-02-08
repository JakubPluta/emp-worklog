Employees Time Tracking App

Description:

This application allows employees to track their time spent on different projects and provides managers with reports on employee productivity.

Features:

Time logging for different projects.
Automatic weekly summaries of worked hours and projects.
Monthly reports for each employee with detailed breakdown of hours worked, projects, and clients.
Project management features including creating, editing, and assigning projects.
User management with different roles and permissions.
Calendar integration to sync time logs with Google or Outlook calendar.
Use Cases:

Employee:

Logs time spent on various projects.
Edits and deletes their own time logs.
Approves their weekly summaries.
Reviews their monthly reports.
Manager:

Reviews time logs and weekly summaries of their subordinates.
Approves weekly summaries.
Generates monthly reports for their team.
Manages projects and clients.
Client:

Reviews time logs and monthly reports for their projects.
Contacts the manager with questions or feedback.
Data Model:

Users:
id (int, primary key)
name (string)
surname (string)
email (string)
role (string)
password (string)
Projects:
id (int, primary key)
name (string)
description (string)
deadline (date)
budget (float)
client_id (int, foreign key)
Clients:
id (int, primary key)
name (string)
address (string)
email (string)
Time Logs:
id (int, primary key)
user_id (int, foreign key)
project_id (int, foreign key)
date (date)
start_time (time)
end_time (time)
duration (float)
note (string)


