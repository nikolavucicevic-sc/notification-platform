"""
Schedules usage examples for the Notification Platform SDK.
"""

from notification_platform_sdk import NotificationPlatformClient

# Initialize the client
client = NotificationPlatformClient(
    base_url="https://notifications.example.com",
    api_key="np_your_api_key_here"
)

# Example 1: Create a customer
print("Example 1: Creating a customer...")
customer = client.customers.create(
    email="bob@example.com",
    first_name="Bob",
    last_name="Johnson"
)
print(f"✓ Customer created: {customer['email']}")

# Example 2: Create a daily reminder schedule
print("\nExample 2: Creating a daily reminder schedule...")
daily_schedule = client.schedules.create(
    name="Daily standup reminder",
    customer_id=customer["id"],
    channel="email",
    cron_expression="0 9 * * MON-FRI",  # 9 AM on weekdays
    subject="Daily Standup Reminder",
    body="Don't forget the daily standup meeting at 10 AM!",
    timezone="America/New_York"
)
print(f"✓ Daily schedule created with ID: {daily_schedule['id']}")

# Example 3: Create a weekly report schedule with template
print("\nExample 3: Creating a weekly report schedule...")

# First create a template
template = client.templates.create(
    name="weekly_report",
    channel="email",
    subject="Weekly Report - Week of {{week_start}}",
    body_template="""
    Hi {{name}},

    Here's your weekly report for the week starting {{week_start}}:

    - Tasks completed: {{tasks_completed}}
    - Active projects: {{active_projects}}

    Keep up the great work!
    """,
    variables=["name", "week_start", "tasks_completed", "active_projects"]
)

weekly_schedule = client.schedules.create(
    name="Weekly report",
    customer_id=customer["id"],
    channel="email",
    cron_expression="0 8 * * MON",  # 8 AM every Monday
    template_id="weekly_report",
    template_data={
        "name": customer["first_name"],
        "week_start": "{{current_week}}",
        "tasks_completed": "{{task_count}}",
        "active_projects": "{{project_count}}"
    },
    timezone="UTC"
)
print(f"✓ Weekly schedule created with ID: {weekly_schedule['id']}")

# Example 4: Get next run time
print("\nExample 4: Getting next run time...")
next_run = client.schedules.get_next_run(daily_schedule["id"])
print(f"✓ Next run scheduled for: {next_run.get('next_run', 'Not available')}")

# Example 5: List all schedules
print("\nExample 5: Listing all schedules...")
schedules = client.schedules.list()
print(f"✓ Found {len(schedules)} schedules:")
for s in schedules:
    status = "enabled" if s.get("enabled") else "disabled"
    print(f"  - {s['name']} ({s['cron_expression']}) - {status}")

# Example 6: Temporarily disable a schedule
print("\nExample 6: Disabling a schedule...")
client.schedules.disable(daily_schedule["id"])
print(f"✓ Daily schedule disabled")

# Example 7: Re-enable the schedule
print("\nExample 7: Re-enabling the schedule...")
client.schedules.enable(daily_schedule["id"])
print(f"✓ Daily schedule re-enabled")

# Example 8: Update schedule time
print("\nExample 8: Updating schedule time...")
updated_schedule = client.schedules.update(
    daily_schedule["id"],
    cron_expression="0 8 * * MON-FRI"  # Change to 8 AM
)
print(f"✓ Schedule updated to: {updated_schedule['cron_expression']}")

print("\n✓ All schedule examples completed successfully!")

# Clean up
client.close()
