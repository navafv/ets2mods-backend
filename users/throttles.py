from rest_framework.throttling import UserRateThrottle

class UploadRateThrottle(UserRateThrottle):
    scope = 'uploads'

class DownloadRateThrottle(UserRateThrottle):
    scope = 'downloads'