from celery import shared_task

@shared_task
def send_attendance_sms(number:str, sms:str):
    return f'SMS xabar yuborildi:{number} -> {sms}'