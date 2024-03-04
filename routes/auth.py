from datetime import datetime, timedelta

otp_expiry_time = None
datetime.utcnow()  > otp_expiry_time + timedelta(hours=5, minutes=30)