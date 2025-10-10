from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (Barcode, TrackIsAuth, RegisterUserView, MyProfileView, UsersRequestsDetailView, VacanciesAPIViewSet, BannerAPIViewSet,MenuElementsAPIViewSet,
                    MenuAPIViewSet, StatisticItemsAPIViewSet, StatisticsAPIViewSet, TegRegionsAPIViewSet, TegWorkingDaysAPIViewSet,
                    TegExperiencesAPIViewSet, TegVacanciesAPIViewSet, TegBranches2APIViewSet,
                    PurchasesAPIViewSet, MarksAPIViewSet, SaveMediaFilesAPIViewSet, EventsAPIViewSet,
                    UzPostNewsAPIViewSet,
                    PostalServicesAPIViewSet, PagesAPIViewSet, BranchServicesAPIViewSet, ShablonServicesAPIViewSet,
                    BranchesAPIViewSet, VacanciesImagesAPIViewSet, InternalDocumentsAPIViewSet,
                    ThemaQuestionsAPIViewSet,
                    BusinessPlansCompletedAPIViewSet, AnnualReportsAPIViewSet, DividendsAPIViewSet,
                    QuarterReportsAPIViewSet,
                    UserInstructionsAPIViewSet, ExecutiveApparatusAPIViewSet, ShablonUzPostTelNumberAPIViewSet,
                    ShablonContactSpecialTitleAPIViewSet, ContactAPIViewSet, AdvertisementsAPIViewSet,
                    OrganicManagementsAPIViewSet,
                    PartnersAPIViewSet, RegionalBranchesAPIViewSet, AdvertisingAPIViewSet,
                    InformationAboutIssuerAPIViewSet,
                    SlidesAPIViewSet, SocialMediaAPIViewSet, EssentialFactsAPIViewSet, RatesAPIViewSet,
                    ServicesAPIViewSet, CharterSocietyAPIViewSet,
                    SecurityPapersAPIViewSet, FAQAPIViewSet, SiteSettingsAPIViewSet, CategoryPagesViewSet, ControlCategoryPageViewSet, TmuTrackAPIView,
<<<<<<< HEAD
                    Test, CategoryServicesAPIViewSet, MarksAsosiyAPIViewSet, CategoryFAQAPIViewSet)
=======
                    CategoryServicesAPIViewSet, MarksAsosiyAPIViewSet, CategoryFAQAPIViewSet)
>>>>>>> 2d32d04 (full complated uzpost backend)

from .views import CustomTokenObtainPairView, RegisterUser2View, RegisterUser3View, Barcode_new
from .recover_password import RecoverPassword3APIView
from .new_register import RegisterNEWAPIView
from .newtrackapk import NewTrackAPK


router = DefaultRouter()
router.register('banners', viewset=BannerAPIViewSet)
router.register('menu-elements', viewset=MenuElementsAPIViewSet)
router.register('menu', viewset=MenuAPIViewSet)
router.register('statistic-items', viewset=StatisticItemsAPIViewSet)
router.register('statistics', viewset=StatisticsAPIViewSet)
router.register('teg-regions', viewset=TegRegionsAPIViewSet)
router.register('teg-working-days', viewset=TegWorkingDaysAPIViewSet)
router.register("teg-experiences", viewset=TegExperiencesAPIViewSet)
router.register("teg-vacancies", viewset=TegVacanciesAPIViewSet)
router.register("teg-branches_2", viewset=TegBranches2APIViewSet)
router.register("vacancies", viewset=VacanciesAPIViewSet)
router.register("purchases", viewset=PurchasesAPIViewSet)
router.register("marks", viewset=MarksAPIViewSet)
router.register("save-media-files", viewset=SaveMediaFilesAPIViewSet)
router.register("events", viewset=EventsAPIViewSet)
router.register("uz-post-news", viewset=UzPostNewsAPIViewSet)
router.register("postal-services", viewset=PostalServicesAPIViewSet)
router.register("pages", viewset=PagesAPIViewSet)
router.register("category-pages", viewset=CategoryPagesViewSet)
router.register("control-category-pages", viewset=ControlCategoryPageViewSet)
router.register("branch-services", viewset=BranchServicesAPIViewSet)
router.register("shablon-services", viewset=ShablonServicesAPIViewSet)
router.register("branches", viewset=BranchesAPIViewSet)
router.register("vacancies-images", viewset=VacanciesImagesAPIViewSet)
router.register("internal-documents", viewset=InternalDocumentsAPIViewSet)
router.register("thema-questions", viewset=ThemaQuestionsAPIViewSet)
router.register("business-plans-completed", viewset=BusinessPlansCompletedAPIViewSet)
router.register("annual-reports", viewset=AnnualReportsAPIViewSet)
router.register("dividends", viewset=DividendsAPIViewSet)
router.register("quarter-reports", viewset=QuarterReportsAPIViewSet)
router.register("user-intructions", viewset=UserInstructionsAPIViewSet)
router.register("executive-apparatus", viewset=ExecutiveApparatusAPIViewSet)
router.register("shablon-uz-post-tel_number", viewset=ShablonUzPostTelNumberAPIViewSet)
router.register("shablon-contact-special-title", viewset=ShablonContactSpecialTitleAPIViewSet)
router.register("contact", viewset=ContactAPIViewSet)
router.register("advertisements", viewset=AdvertisementsAPIViewSet)
router.register("organic-managements", viewset=OrganicManagementsAPIViewSet)
router.register("partners", viewset=PartnersAPIViewSet)
router.register("regional-branches", viewset=RegionalBranchesAPIViewSet)
router.register("advertising", viewset=AdvertisingAPIViewSet)
router.register("information-about-issuer", viewset=InformationAboutIssuerAPIViewSet)
router.register("slides", viewset=SlidesAPIViewSet)
router.register("social-media", viewset=SocialMediaAPIViewSet)
router.register("essential-facts", viewset=EssentialFactsAPIViewSet)
router.register("rates", viewset=RatesAPIViewSet)
router.register("services", viewset=ServicesAPIViewSet)
router.register("charter-society", viewset=CharterSocietyAPIViewSet)
router.register("security-papers", viewset=SecurityPapersAPIViewSet)
router.register("faq", viewset=FAQAPIViewSet)
router.register("site-settings", viewset=SiteSettingsAPIViewSet)
router.register("category-services", viewset=CategoryServicesAPIViewSet)
router.register("marks-page", viewset=MarksAsosiyAPIViewSet, basename="marks-page")
router.register("category-faq", viewset=CategoryFAQAPIViewSet, basename="category-faq")


urlpatterns = [
    path('', include(router.urls)),
    path('authenticate/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('register/1/', RegisterUserView.as_view(), name='register1'),
    path('register/2/', RegisterUser2View.as_view(), name='register2'),
    path('register/3/', RegisterUser3View.as_view(), name='register3'),
    path('profile/', MyProfileView.as_view(), name='profile'),
    path('track/<slug:barcode>/', Barcode_new.as_view(), name='barcode'),
    path('tracking/<slug:barcode>/', TrackIsAuth.as_view(), name='auth-tracking'),
    path('temutrack/<slug:barcode>/', TmuTrackAPIView.as_view(), name='temutrack'),
    path("trackapk/<slug:barcode>", NewTrackAPK.as_view(), name="track-apk"),
    path('userrequests/', UsersRequestsDetailView.as_view(), name='user_requests'),
<<<<<<< HEAD
=======
    path('recovery/password/', RecoverPassword3APIView.as_view(), name='recovery-password-3'),
    path('register/new/', RegisterNEWAPIView.as_view(), name='register-new')
>>>>>>> 2d32d04 (full complated uzpost backend)
]
