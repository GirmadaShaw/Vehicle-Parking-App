from backend import celery  
from celery.schedules import crontab


celery.conf.beat_schedule = {
    'daily-reminder-task': {
        'task': 'send_daily_reminders',
        'schedule': crontab(hour=18, minute=0),  
    },
    'monthly-report-task': {
        'task': 'generate_monthly_reports',
        'schedule': crontab(hour=0, minute=0, day_of_month=1), 
    }
}