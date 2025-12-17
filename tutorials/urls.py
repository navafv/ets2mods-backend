from rest_framework.routers import DefaultRouter
from .views import TutorialViewSet

router = DefaultRouter()
router.register(r'', TutorialViewSet)
urlpatterns = router.urls