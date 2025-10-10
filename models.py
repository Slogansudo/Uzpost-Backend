from django.db import models
import os
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from django.forms import ImageField
from django.dispatch import receiver
from django.db.models.signals import pre_save


class BannersLinks(models.Model):
    title_uz = models.CharField(max_length=100)
    link_uz = models.CharField(max_length=200)
    title_ru = models.CharField(max_length=100)
    link_ru = models.CharField(max_length=200)
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('id', )
        verbose_name = "Banner Uchun Linklar"
        verbose_name_plural = "Banner Uchun Linklar"
        db_table = 'bannerslinks'
        indexes = [
            models.Index(fields=['id'])
        ]

    def __str__(self):
        return self.title_uz


class Banners(models.Model):
    """
        banner modelida saytni yuqoriq qismdagi rasm va rangni qo'shish o'zgartirish va o'chirish imkoniyatini
        yaratib beradi
    """
    title = models.CharField(max_length=200, verbose_name='title')
    image_uz = models.ImageField(upload_to="banners/", unique=True, null=True, blank=True)
    image_ru = models.ImageField(upload_to="banners/", unique=True, null=True, blank=True)
    links = models.ManyToManyField(BannersLinks, verbose_name='bannerslinks', blank=True)
    status = models.BooleanField(default=False)
    fizlitso_status = models.BooleanField(default=False)
    yurlitso_status = models.BooleanField(default=False)    
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('id', )
        verbose_name = "Banner"
        verbose_name_plural = "Bannerlar"
        db_table = 'banners'
        indexes = [
            models.Index(fields=['id'])
        ]

    def delete(self, *args, **kwargs):
        # model o'chirilishidan oldin faylni o'chirish
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.title


class FuterMenuItems(models.Model):
    name_ru = models.CharField(max_length=200)
    name_uz = models.CharField(max_length=200)
    description_ru = models.TextField(null=True, blank=True)
    description_uz = models.TextField(null=True, blank=True)
    text_ru = RichTextUploadingField(null=True, blank=True)
    text_uz = RichTextUploadingField(null=True, blank=True)
    shortcut_ru = models.SlugField(max_length=100, unique=True, null=True, blank=True)
    shortcut_uz = models.SlugField(max_length=100, unique=True, null=True, blank=True)
    meta_title_ru = models.CharField(max_length=100, null=True, blank=True)
    meta_title_uz = models.CharField(max_length=100, null=True, blank=True)
    meta_link_uz = models.CharField(max_length=100, null=True, blank=True)
    meta_link_ru = models.CharField(max_length=100, null=True, blank=True)
    meta_description_ru = models.TextField(null=True, blank=True)
    meta_description_uz = models.TextField(null=True, blank=True)
    meta_words_ru = models.CharField(max_length=100, null=True, blank=True)
    meta_words_uz = models.CharField(max_length=100, null=True, blank=True)
    link_ru = models.CharField(max_length=100, null=True, blank=True)
    link_uz = models.CharField(max_length=100, null=True, blank=True)
    image_uz = models.ImageField(upload_to="futerimages/", null=True, blank=True)
    image_ru = models.ImageField(upload_to="futerimages/", null=True, blank=True)
    pdf_uz = models.FileField(upload_to="futers/", null=True, blank=True)
    pdf_ru = models.FileField(upload_to="futers/", null=True, blank=True)
    status = models.BooleanField()
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('id', )
        verbose_name = "Futer Menyu elementlar"
        verbose_name_plural = "Futer Menyu elementlar"
        db_table = 'futer_menu_items'
        indexes = [
            models.Index(fields=['id'])
        ]

    def __str__(self):
        return self.name_uz


class FuterMenu(models.Model):
    """
    menu elementlari saqlanadigan model bunda hamma
    yaratilgan menu elementlarini bir joyda saqlash imkonini beradi
    """
    name_uz = models.CharField(max_length=200)
    name_ru = models.CharField(max_length=200)
    # description_ru = models.TextField(null=True, blank=True)
    # description_uz = models.TextField(null=True, blank=True)
    # text_ru = RichTextUploadingField(null=True, blank=True)
    # text_uz = RichTextUploadingField(null=True, blank=True)
    # shortcut_ru = models.SlugField(max_length=100, unique=True)
    # shortcut_uz = models.SlugField(max_length=100, unique=True)
    # meta_title_ru = models.CharField(max_length=100, null=True, blank=True)
    # meta_title_uz = models.CharField(max_length=100, null=True, blank=True)
    # meta_description_ru = models.TextField(null=True, blank=True)
    # meta_description_uz = models.TextField(null=True, blank=True)
    # meta_words_ru = models.CharField(max_length=100, null=True, blank=True)
    # meta_words_uz = models.CharField(max_length=100, null=True, blank=True)
    # link_ru = models.CharField(max_length=100, null=True, blank=True)
    # link_uz = models.CharField(max_length=100, null=True, blank=True)
    elements = models.ManyToManyField(FuterMenuItems, related_name='futer_menu_elements_uz', blank=True)
    status = models.BooleanField(default=False)
    create_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('id', )
        verbose_name = "Futer Menyu"
        verbose_name_plural = "Futer Menyu"
        db_table = 'futer_menu'
        indexes = [
            models.Index(fields=['id'])
        ]

    def __str__(self):
        return self.name_uz
    ########################################################################

##############################################################################
###############################################################################


class MenuItemPages(models.Model):
    """
     tariflarni saqlaydigan jadval
    """
    title_ru = models.CharField(max_length=200)
    title_uz = models.CharField(max_length=200)
    description_ru = models.TextField(null=True, blank=True)
    description_uz = models.TextField(null=True, blank=True)
    text_ru = RichTextUploadingField(null=True, blank=True)
    text_uz = RichTextUploadingField(null=True, blank=True)
    save_image_uz = models.ImageField(upload_to='images/', null=True, blank=True)
    save_image_ru = models.ImageField(upload_to='images/', null=True, blank=True)
    status = models.BooleanField(default=False)
    date = models.DateTimeField(auto_created=True)

    class Meta:
        ordering = ('id',)
        verbose_name = "Menu 4-darajali Elementlar"
        verbose_name_plural = "Menu 4-darajali Elementlar"
        db_table = 'menu_item_pages'
        indexes = [
            models.Index(fields=['id'])
        ]

    def __str__(self):
        return self.title_uz


class CategoryMenuItemPages(models.Model):
    name_uz = models.CharField(max_length=200, null=True, blank=True)
    name_ru = models.CharField(max_length=200, null=True, blank=True)
    pages_id = models.ManyToManyField(MenuItemPages, related_name='category_menu_item_pages', blank=True)

    class Meta:
        ordering = ('id',)
        verbose_name = "Menu 3-darajali Elementlar"
        verbose_name_plural = "Menu 3-darajali Elementlar"
        db_table = 'category_menu_item_pages'
        indexes = [
            models.Index(fields=['id'])
        ]

    def __str__(self):
        return self.name_uz


class MenuElementItems(models.Model):
    name_ru = models.CharField(max_length=200)
    name_uz = models.CharField(max_length=200)
    link_ru = models.CharField(max_length=200, null=True, blank=True)
    link_uz = models.CharField(max_length=200, null=True, blank=True)
    item_pages = models.ManyToManyField(CategoryMenuItemPages, related_name='menu_item_pages', blank=True)
    status = models.BooleanField()
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('id', )
        verbose_name = "Menu 2-darajali Elementlar"
        verbose_name_plural = "Menu 2-darajali Elementlar"
        db_table = 'menu_element_items'
        indexes = [
            models.Index(fields=['id'])
        ]

    def __str__(self):
        return self.name_uz


class MenuElements(models.Model):
    """
    menu elementlari saqlanadigan model bunda biror sahifaga o'tganda
     sahifa nomi va o'sha sahifani yuqori qismi rangi va qanaqadir
      rasm qo'yilmoqchi bo'lsa rasm qo'yish mumkin
    """
    name_ru = models.CharField(max_length=200)
    link_ru = models.CharField(max_length=200, null=True, blank=True)
    name_uz = models.CharField(max_length=200)
    link_uz = models.CharField(max_length=200, null=True, blank=True)
    elements = models.ManyToManyField(MenuElementItems, blank=True, related_name='menu_elements_items_uz')
    status = models.BooleanField()
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('id', )
        verbose_name = "Menyu Elementlar"
        verbose_name_plural = "Menyu Elementlar"
        db_table = 'menu_elements'
        indexes = [
            models.Index(fields=['id'])
        ]

    def __str__(self):
        return self.name_uz


class StatisticItems(models.Model):
    """
     statistic elementlari saqlanadigan jadval
      qandaydir baxolash mezoni qo'shish mumkin
    """
    title_ru = models.CharField(max_length=200)
    title_uz = models.CharField(max_length=200)
    order_count = models.IntegerField()
    number_responses = models.IntegerField(default=0)
    create_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('id', )
        verbose_name = "Statistic Elementlar"
        verbose_name_plural = "Statistic Elementlar"
        db_table = 'statistic_items'
        indexes = [
            models.Index(fields=['id'])
        ]

    def __str__(self):
        return self.title_uz


class Statistics(models.Model):
    """ statistika sarlavhasi saqlanadigan model
    bu modelga sarlavha qo'yib statistic_items jadvalidagi ma'lumotlarni qo'shimiz mukin"""

    title_ru = models.CharField(max_length=200)
    title_uz = models.CharField(max_length=200)
    statistic_items = models.ManyToManyField(StatisticItems, blank=True)
    status = models.BooleanField(default=False)
    create_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('id', )
        verbose_name = "Statistikalar"
        verbose_name_plural = "Statistikalar"
        db_table = 'statistics'
        indexes = [
            models.Index(fields=['id'])
        ]

    def __str__(self):
        return self.title_uz


class TegRegions(models.Model):
    """ filiali bor viloyatlar ro'yhati uchun kamchilik bo'lishi mukin"""
    name_ru = models.CharField(max_length=100)
    name_uz = models.CharField(max_length=100)
    sorting = models.IntegerField(default=1)
    create_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('id', )
        verbose_name = "Teg Viloyatlar"
        verbose_name_plural = "Teg Viloyatlar"
        db_table = 'teg_regions'
        indexes = [
            models.Index(fields=['id'])
        ]

    def __str__(self):
        return self.name_uz


class TegWorkingDays(models.Model):
    """ ish kunlarini saqlash uchun kerak bo'lgan jadval"""
    name_ru = models.CharField(max_length=100)
    name_uz = models.CharField(max_length=100)
    sorting = models.IntegerField(default=1)
    create_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('id', )
        verbose_name = "Teg Ish Kunlarini"
        verbose_name_plural = "Teg Ish Kunlarini"
        db_table = 'teg_working_days'
        indexes = [
            models.Index(fields=['id'])
        ]

    def __str__(self):
        return self.name_uz


class TegExperience(models.Model):

    """ ish tajribasi ro'yhati jadvali kamchilik bo'lishi mukin"""

    name_ru = models.CharField(max_length=100)
    name_uz = models.CharField(max_length=100)
    sorting = models.IntegerField(default=1)
    create_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('id', )
        verbose_name = "Teg Tajribalr"
        verbose_name_plural = "Teg Tajribalar"
        db_table = 'teg_experience'
        indexes = [
            models.Index(fields=['id'])
        ]

    def __str__(self):
        return self.name_uz


class TegVacancies(models.Model):

    """ vacansiya uchun teglar ro'yhati jadvali'"""

    name_ru = models.CharField(max_length=100)
    name_uz = models.CharField(max_length=100)
    sorting = models.IntegerField(default=1)
    create_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('id', )
        verbose_name = "Teg Vakansiyalar"
        verbose_name_plural = "Teg Vakansiyalar"
        db_table = 'teg_vacancies'
        indexes = [
            models.Index(fields=['id'])
        ]

    def __str__(self):
        return self.name_uz


class TegBranches2(models.Model):

    """ filiallar uchun teglar ro'yhati jadvali 2 """

    name_ru = models.CharField(max_length=100)
    name_uz = models.CharField(max_length=100)
    sorting = models.IntegerField(default=1)
    create_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('id', )
        verbose_name = "Teg Filliallar 2"
        verbose_name_plural = "Teg Filliallar 2"
        db_table = 'teg_branches'
        indexes = [
            models.Index(fields=['id'])
        ]

    def __str__(self):
        return self.name_uz


class Vacancies(models.Model):

    """
    vacansiyalar ro'yhati jadvali'
    """
    title_ru = models.CharField(max_length=100)
    title_uz = models.CharField(max_length=100)
    description_ru = models.TextField(null=True, blank=True)
    description_uz = models.TextField(null=True, blank=True)
    text_ru = RichTextUploadingField(null=True, blank=True)
    text_uz = RichTextUploadingField(null=True, blank=True)
    shortcut_ru = models.SlugField(max_length=100, unique=True, null=True, blank=True)
    shortcut_uz = models.SlugField(max_length=100, unique=True, null=True, blank=True)
    meta_title_ru = models.CharField(max_length=100, null=True, blank=True)
    meta_title_uz = models.CharField(max_length=100, null=True, blank=True)
    meta_description_ru = models.TextField(null=True, blank=True)
    meta_description_uz = models.TextField(null=True, blank=True)
    meta_words_ru = models.CharField(max_length=100, null=True, blank=True)
    meta_words_uz = models.CharField(max_length=100, null=True, blank=True)
    link_ru = models.CharField(max_length=100, null=True, blank=True)
    link_uz = models.CharField(max_length=100, null=True, blank=True)
    teg_vacancies = models.ManyToManyField(TegVacancies, blank=True)
    teg_regions = models.ManyToManyField(TegRegions, blank=True)
    teg_experiences = models.ManyToManyField(TegExperience, blank=True)
    price_ru = models.CharField(max_length=100, null=True, blank=True)
    price_uz = models.CharField(max_length=100, null=True, blank=True)
    save_image = models.ImageField(upload_to='images/', null=True, blank=True)
    status = models.BooleanField(default=False)
    date = models.DateTimeField(auto_created=True)

    class Meta:
        ordering = ('id', )
        verbose_name = "Vakansiyalar"
        verbose_name_plural = "Vakansiyalar"
        db_table = 'vacancies'
        indexes = [
            models.Index(fields=['id'])
        ]

    def __str__(self):
        return self.title_uz


class Purchases(models.Model):
    """
     bu model xaridlar jadvali hisoblanadi
        yani закупки
    """
    title_ru = models.CharField(max_length=100)
    title_uz = models.CharField(max_length=100)
    description_ru = models.TextField(null=True, blank=True)
    description_uz = models.TextField(null=True, blank=True)
    text_ru = RichTextUploadingField(null=True, blank=True)
    text_uz = RichTextUploadingField(null=True, blank=True)
    shortcut_ru = models.SlugField(max_length=100, unique=True, null=True, blank=True)
    shortcut_uz = models.SlugField(max_length=100, unique=True, null=True, blank=True)
    meta_title_ru = models.CharField(max_length=100, null=True, blank=True)
    meta_title_uz = models.CharField(max_length=100, null=True, blank=True)
    meta_description_ru = models.TextField(null=True, blank=True)
    meta_description_uz = models.TextField(null=True, blank=True)
    meta_words_ru = models.CharField(max_length=100, null=True, blank=True)
    meta_words_uz = models.CharField(max_length=100, null=True, blank=True)
    link_ru = models.CharField(max_length=100, null=True, blank=True)
    link_uz = models.CharField(max_length=100, null=True, blank=True)
    save_image = models.ImageField(upload_to='images/', null=True, blank=True)
    status = models.BooleanField(default=False)
    date = models.DateTimeField(auto_created=True)

    class Meta:
        ordering = ('id', )
        verbose_name = "Xaridlar"
        verbose_name_plural = "Xaridlar"
        db_table = 'purchases'
        indexes = [
            models.Index(fields=['id'])
        ]

    def __str__(self):
        return self.title_uz


class Marks(models.Model):
    """
     bu model markalar modeli hisoblanadi jadvali hisoblanadi
        yani закупки
    """
    title_ru = models.CharField(max_length=100)
    title_uz = models.CharField(max_length=100)
    description_ru = models.TextField(null=True, blank=True)
    description_uz = models.TextField(null=True, blank=True)
    text_ru = RichTextUploadingField(null=True, blank=True)
    text_uz = RichTextUploadingField(null=True, blank=True)
    shortcut_ru = models.SlugField(max_length=100, unique=True, null=True, blank=True)
    shortcut_uz = models.SlugField(max_length=100, unique=True, null=True, blank=True)
    meta_title_ru = models.CharField(max_length=100, null=True, blank=True)
    meta_title_uz = models.CharField(max_length=100, null=True, blank=True)
    meta_description_ru = models.TextField(null=True, blank=True)
    meta_description_uz = models.TextField(null=True, blank=True)
    meta_words_ru = models.CharField(max_length=100, null=True, blank=True)
    meta_words_uz = models.CharField(max_length=100, null=True, blank=True)
    link_ru = models.CharField(max_length=100, null=True, blank=True)
    link_uz = models.CharField(max_length=100, null=True, blank=True)
    save_image_uz = models.ImageField(upload_to='images/', null=True, blank=True)
    save_image_ru = models.ImageField(upload_to='images/', null=True, blank=True)
    marks_count_ru = models.CharField(max_length=100, null=True, blank=True)
    marks_count_uz = models.CharField(max_length=100, null=True, blank=True)
    years = models.BigIntegerField(null=True, blank=True)
    count_number = models.BigIntegerField(null=True, blank=True)
    price_uz = models.CharField(max_length=100, null=True, blank=True)
    price_ru = models.CharField(max_length=100, null=True, blank=True)
    status = models.BooleanField(default=False)
    date = models.DateTimeField(auto_created=True)

    class Meta:
        ordering = ('id', )
        verbose_name = "Markalar"
        verbose_name_plural = "Markalar"
        db_table = 'marks'
        indexes = [
            models.Index(fields=['id'])
        ]

    def __str__(self):
        return self.title_uz


class SaveMediaFiles(models.Model):
    """
        umumiy mediya yoki pdf filelarni saqlash uchun yaratilgan model
    """
    file = models.FileField(upload_to='')
    create_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('id', )
        verbose_name = "Media Fayllar Saqlash"
        verbose_name_plural = "Media Fayllar Saqlash"
        db_table = 'save_media_files'
        indexes = [
            models.Index(fields=['id'])
        ]

    def __str__(self):
        return self.file.name


class Events(models.Model):
    title_ru = models.CharField(max_length=100)
    title_uz = models.CharField(max_length=100)
    description_ru = models.TextField(null=True, blank=True)
    description_uz = models.TextField(null=True, blank=True)
    text_ru = RichTextUploadingField(null=True, blank=True)
    text_uz = RichTextUploadingField(null=True, blank=True)
    shortcut_ru = models.SlugField(max_length=100, unique=True, null=True, blank=True)
    shortcut_uz = models.SlugField(max_length=100, unique=True, null=True, blank=True)
    meta_title_ru = models.CharField(max_length=100, null=True, blank=True)
    meta_title_uz = models.CharField(max_length=100, null=True, blank=True)
    meta_description_ru = models.TextField(null=True, blank=True)
    meta_description_uz = models.TextField(null=True, blank=True)
    meta_words_ru = models.CharField(max_length=100, null=True, blank=True)
    meta_words_uz = models.CharField(max_length=100, null=True, blank=True)
    link_ru = models.CharField(max_length=100, null=True, blank=True)
    link_uz = models.CharField(max_length=100, null=True, blank=True)
    video_preview = models.ManyToManyField(SaveMediaFiles, blank=True, related_name='video_preview_events')
    video = models.ManyToManyField(SaveMediaFiles, blank=True, related_name='video_events')
    save_image = models.ImageField(upload_to='images/', null=True, blank=True)
    teg_branches = models.ManyToManyField(TegBranches2, blank=True)
    status = models.BooleanField(default=False)
    date = models.DateTimeField(auto_created=True)

    class Meta:
        ordering = ('id', )
        db_table = 'events'
        indexes = [
            models.Index(fields=['id'])
        ]

    def __str__(self):
        return self.title_uz


class UzPostNews(models.Model):
    """yangiliklar jadvaliga o'zbekcha ruscha ma'lumotlar saqlanadi"""
    title_ru = models.CharField(max_length=100)
    title_uz = models.CharField(max_length=100)
    description_ru = models.TextField(null=True, blank=True)
    description_uz = models.TextField(null=True, blank=True)
    text_ru = RichTextUploadingField(null=True, blank=True)
    text_uz = RichTextUploadingField(null=True, blank=True)
    video_ru = models.ManyToManyField(SaveMediaFiles, blank=True, related_name='video_ru_uzpostnews')
    video_uz = models.ManyToManyField(SaveMediaFiles, blank=True, related_name='video_uz_uzpostnews')
    save_image = models.ImageField(upload_to='images/', null=True, blank=True)
    status = models.BooleanField(default=False)
    date = models.DateTimeField(auto_created=True)

    class Meta:
        ordering = ('id', )
        verbose_name = "Uzpost Yangiliklar"
        verbose_name_plural = "Uzpost Yangiliklar"
        db_table = 'uz_post_news'
        indexes = [
            models.Index(fields=['id'])
        ]

    def __str__(self):
        return self.title_uz


class PostalServices(models.Model):
    """
     pochta usluga jadvali bundan ruscha uzbekcha ma'lumotlar saqlanadi
    """
    title_ru = models.CharField(max_length=100)
    title_uz = models.CharField(max_length=100)
    description_ru = models.TextField(null=True, blank=True)
    description_uz = models.TextField(null=True, blank=True)
    text_ru = RichTextUploadingField(null=True, blank=True)
    text_uz = RichTextUploadingField(null=True, blank=True)
    shortcut_ru = models.SlugField(max_length=100, unique=True, null=True, blank=True)
    shortcut_uz = models.SlugField(max_length=100, unique=True, null=True, blank=True)
    meta_title_ru = models.CharField(max_length=100, null=True, blank=True)
    meta_title_uz = models.CharField(max_length=100, null=True, blank=True)
    meta_description_ru = models.TextField(null=True, blank=True)
    meta_description_uz = models.TextField(null=True, blank=True)
    meta_words_ru = models.CharField(max_length=100, null=True, blank=True)
    meta_words_uz = models.CharField(max_length=100, null=True, blank=True)
    link_ru = models.CharField(max_length=100, null=True, blank=True)
    link_uz = models.CharField(max_length=100, null=True, blank=True)
    save_image = models.ImageField(upload_to='images/', null=True, blank=True)
    status = models.BooleanField(default=False)
    date = models.DateTimeField(auto_created=True)

    class Meta:
        ordering = ('id', )
        db_table = 'postal_services'
        indexes = [
            models.Index(fields=['id'])
        ]

    def __str__(self):
        return self.title_uz


class Pages(models.Model):
    title_ru = models.CharField(max_length=100)
    title_uz = models.CharField(max_length=100)
    description_ru = models.TextField(null=True, blank=True)
    description_uz = models.TextField(null=True, blank=True)
    text_ru = RichTextUploadingField(null=True, blank=True)
    text_uz = RichTextUploadingField(null=True, blank=True)
    shortcut_ru = models.SlugField(max_length=100, unique=True, null=True, blank=True)
    shortcut_uz = models.SlugField(max_length=100, unique=True, null=True, blank=True)
    meta_title_ru = models.CharField(max_length=100, null=True, blank=True)
    meta_title_uz = models.CharField(max_length=100, null=True, blank=True)
    meta_description_ru = models.TextField(null=True, blank=True)
    meta_description_uz = models.TextField(null=True, blank=True)
    meta_words_ru = models.CharField(max_length=100, null=True, blank=True)
    meta_words_uz = models.CharField(max_length=100, null=True, blank=True)
    link_ru = models.CharField(max_length=100, null=True, blank=True)
    link_uz = models.CharField(max_length=100, null=True, blank=True)
    save_image = models.ImageField(upload_to='images/', null=True, blank=True)
    status = models.BooleanField(default=False)
    date = models.DateTimeField(auto_created=True)

    class Meta:
        ordering = ('id', )
        db_table = 'pages'
        indexes = [
            models.Index(fields=['id'])
        ]

    def __str__(self):
        return self.title_uz


class CategoryPages(models.Model):
    """ Category pages bu model uzpostda tariflar sahifasi uchun tariflar categoriyasi kerak"""
    title_ru = models.CharField(max_length=100)
    title_uz = models.CharField(max_length=100)
    pages = models.ManyToManyField(Pages, blank=True, related_name='category_pages')

    class Meta:
        ordering = ('id',)
        db_table = 'category_page'
        indexes = [
            models.Index(fields=['id'])
        ]

    def __str__(self):
        return self.title_uz


class ControlCategoryPages(models.Model):
    """ Control category pages bu model uzpostda category lar uchun2-category vazifasini bajaradi"""
    title_ru = models.CharField(max_length=100)
    title_uz = models.CharField(max_length=100)
    page_categories = models.ManyToManyField(CategoryPages, blank=True, related_name='control_categories')

    class Meta:
        ordering = ('id', )
        db_table = 'control_categories'
        indexes = [
            models.Index(fields=['id'])
        ]

    def __str__(self):
        return self.title_uz


class BranchServices(models.Model):
    """
        branch services model filial xizmat ko'rsatish jadvali
    """
    title_ru = models.CharField(max_length=100)
    title_uz = models.CharField(max_length=100)
    description_ru = models.TextField(null=True, blank=True)
    description_uz = models.TextField(null=True, blank=True)
    text_ru = RichTextUploadingField(null=True, blank=True)
    text_uz = RichTextUploadingField(null=True, blank=True)
    shortcut_ru = models.SlugField(max_length=100, unique=True, null=True, blank=True)
    shortcut_uz = models.SlugField(max_length=100, unique=True, null=True, blank=True)
    meta_title_ru = models.CharField(max_length=100, null=True, blank=True)
    meta_title_uz = models.CharField(max_length=100, null=True, blank=True)
    meta_description_ru = models.TextField(null=True, blank=True)
    meta_description_uz = models.TextField(null=True, blank=True)
    meta_words_ru = models.CharField(max_length=100, null=True, blank=True)
    meta_words_uz = models.CharField(max_length=100, null=True, blank=True)
    link_ru = models.CharField(max_length=100, null=True, blank=True)
    link_uz = models.CharField(max_length=100, null=True, blank=True)
    save_image = models.ImageField(upload_to='images/', null=True, blank=True)
    status = models.BooleanField(default=False)
    date = models.DateTimeField(auto_created=True)

    class Meta:
        ordering = ('id', )
        db_table = 'branch_services'
        indexes = [
            models.Index(fields=['id'])
        ]

    def __str__(self):
        return self.title_uz


class ShablonServices(models.Model):
    """
    filiallar ro'yhati uchun kerak bo'lgan usluga yaratish jadvali
    """

    title_ru = models.CharField(max_length=50, null=True, blank=True)
    title_uz = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        ordering = ('id', )
        db_table = 'shablon_servises'
        indexes = [
            models.Index(fields=['id'])
        ]

    def __str__(self):
        return self.title_uz


class Branches(models.Model):
    """ filiallar ro'yhati saqlanadigan jadval"""
    title_ru = models.CharField(max_length=100)
    title_uz = models.CharField(max_length=100)
    description_ru = models.TextField(null=True, blank=True)
    description_uz = models.TextField(null=True, blank=True)
    text_ru = RichTextUploadingField(null=True, blank=True)
    text_uz = RichTextUploadingField(null=True, blank=True)
    shortcut_ru = models.SlugField(max_length=100, unique=True, null=True, blank=True)
    shortcut_uz = models.SlugField(max_length=100, unique=True, null=True, blank=True)
    meta_title_ru = models.CharField(max_length=100, null=True, blank=True)
    meta_title_uz = models.CharField(max_length=100, null=True, blank=True)
    meta_description_ru = models.TextField(null=True, blank=True)
    meta_description_uz = models.TextField(null=True, blank=True)
    meta_words_ru = models.CharField(max_length=100, null=True, blank=True)
    meta_words_uz = models.CharField(max_length=100, null=True, blank=True)
    link_ru = models.CharField(max_length=100, null=True, blank=True)
    link_uz = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=50, null=True, blank=True)
    facts = models.CharField(max_length=100, null=True, blank=True)
    address_ru = models.CharField(max_length=100, null=True, blank=True)
    address_uz = models.CharField(max_length=100, null=True, blank=True)
    director = models.CharField(max_length=100, null=True, blank=True)
    deputy_director = models.CharField(max_length=100, null=True, blank=True)
    work_time = models.CharField(max_length=100, null=True, blank=True)
    header_image = models.ManyToManyField(SaveMediaFiles, blank=True, related_name='header_image')
    branch_sidebar_image = models.ManyToManyField(SaveMediaFiles, blank=True, related_name='branches_sidebar_image')
    postal_service = models.ManyToManyField(ShablonServices, blank=True, related_name='postal_service')
    kurier_services = models.ManyToManyField(ShablonServices, blank=True, related_name='kurier_services')
    additional_services = models.ManyToManyField(ShablonServices, blank=True, related_name='additional_services')
    contractual_services = models.ManyToManyField(ShablonServices, blank=True, related_name='contractual_services')
    modern_ict_services = models.ManyToManyField(ShablonServices, blank=True, related_name='modern_ict_services')
    save_image = models.ImageField(upload_to='images/', null=True, blank=True)
    working_days = models.ManyToManyField(TegWorkingDays, blank=True)
    status = models.BooleanField(default=False)
    date = models.DateTimeField(auto_created=True)

    class Meta:
        ordering = ('id', )
        verbose_name = "Filliallar"
        verbose_name_plural = "Filliallar"
        db_table = 'branches'
        indexes = [
            models.Index(fields=['id'])
        ]

    def __str__(self):
        return self.title_uz


class VacanciesImages(models.Model):
    """
    vacansiyalar ro'yhati uchun head qismida chiqib turadigan rasmlar
    """
    title_ru = models.CharField(max_length=100)
    title_uz = models.CharField(max_length=100)
    description_ru = models.TextField(null=True, blank=True)
    description_uz = models.TextField(null=True, blank=True)
    text_ru = RichTextUploadingField(null=True, blank=True)
    text_uz = RichTextUploadingField(null=True, blank=True)
    link_ru = models.CharField(max_length=100, null=True, blank=True)
    link_uz = models.CharField(max_length=100, null=True, blank=True)
    save_image = models.ImageField(upload_to='images/', null=True, blank=True)
    status = models.BooleanField(default=False)
    date = models.DateTimeField(auto_created=True)

    class Meta:
        ordering = ('id', )
        verbose_name = "Rasmli Vacansiyalar"
        verbose_name_plural = "Rasmli Vacansiyalar"
        db_table = 'vacancies_images'
        indexes = [
            models.Index(fields=['id'])
        ]

    def __str__(self):
        return self.title_uz


class InternalDocuments(models.Model):
    """
    Internal Documents jadvali document ma'lumotlarini saqlaydigan jadval
    """
    title_ru = models.CharField(max_length=100)
    title_uz = models.CharField(max_length=100)
    description_ru = models.TextField(null=True, blank=True)
    description_uz = models.TextField(null=True, blank=True)
    text_ru = RichTextUploadingField(null=True, blank=True)
    text_uz = RichTextUploadingField(null=True, blank=True)
    link_ru = models.CharField(max_length=100, null=True, blank=True)
    link_uz = models.CharField(max_length=100, null=True, blank=True)
    save_image = models.ImageField(upload_to='images/', null=True, blank=True)
    status = models.BooleanField(default=False)
    date = models.DateTimeField(auto_created=True)

    class Meta:
        ordering = ('id', )
        db_table = 'internal_documents'
        indexes = [
            models.Index(fields=['id'])
        ]

    def __str__(self):
        return self.title_uz


class ThemaQuestions(models.Model):
    """
    tema voprosi jadvali malumotlarni saqlaydi
    """
    title_ru = models.CharField(max_length=100)
    title_uz = models.CharField(max_length=100)
    description_ru = models.TextField(null=True, blank=True)
    description_uz = models.TextField(null=True, blank=True)
    text_ru = RichTextUploadingField(null=True, blank=True)
    text_uz = RichTextUploadingField(null=True, blank=True)
    link_ru = models.CharField(max_length=100, null=True, blank=True)
    link_uz = models.CharField(max_length=100, null=True, blank=True)
    save_image = models.ImageField(upload_to='images/', null=True, blank=True)
    status = models.BooleanField(default=False)
    date = models.DateTimeField(auto_created=True)

    class Meta:
        ordering = ('id', )
        verbose_name = "Mavzu Yuzasidan Savollar"
        verbose_name_plural = "Mavzu Yuzasidan Savollar"
        db_table = 'thema_questions'
        indexes = [
            models.Index(fields=['id'])
        ]

    def __str__(self):
        return self.title_uz


class BusinessPlansCompleted(models.Model):
    """
        Бизнес-план «Виполнение» jadvali yuqoridagi theme_questions jadvali bilan bir xil malumot yuklanadi
    """
    title_ru = models.CharField(max_length=100)
    title_uz = models.CharField(max_length=100)
    description_ru = models.TextField(null=True, blank=True)
    description_uz = models.TextField(null=True, blank=True)
    text_ru = RichTextUploadingField(null=True, blank=True)
    text_uz = RichTextUploadingField(null=True, blank=True)
    link_ru = models.CharField(max_length=100, null=True, blank=True)
    link_uz = models.CharField(max_length=100, null=True, blank=True)
    save_image = models.ImageField(upload_to='images/', null=True, blank=True)
    status = models.BooleanField(default=False)
    date = models.DateTimeField(auto_created=True)

    class Meta:
        ordering = ('id',)
        db_table = 'business_plans_completed'
        indexes = [
            models.Index(fields=['id'])
        ]

    def __str__(self):
        return self.title_uz


class AnnualReports(models.Model):
    """
        yullik hisobotlar saqlanadigan jadval
    """

    title_ru = models.CharField(max_length=100)
    title_uz = models.CharField(max_length=100)
    description_ru = models.TextField(null=True, blank=True)
    description_uz = models.TextField(null=True, blank=True)
    text_ru = RichTextUploadingField(null=True, blank=True)
    text_uz = RichTextUploadingField(null=True, blank=True)
    link_ru = models.CharField(max_length=100, null=True, blank=True)
    link_uz = models.CharField(max_length=100, null=True, blank=True)
    save_image = models.ImageField(upload_to='images/', null=True, blank=True)
    status = models.BooleanField(default=False)
    date = models.DateTimeField(auto_created=True)

    class Meta:
        ordering = ('id',)
        db_table = 'annual_reposts'
        indexes = [
            models.Index(fields=['id'])
        ]

    def __str__(self):
        return self.title_uz


class Dividends(models.Model):
    """
       ruschasiga дивиденды deb nomlangan jadval dividentlarni saqlovchi jadval
    """
    title_ru = models.CharField(max_length=100)
    title_uz = models.CharField(max_length=100)
    description_ru = models.TextField(null=True, blank=True)
    description_uz = models.TextField(null=True, blank=True)
    text_ru = RichTextUploadingField(null=True, blank=True)
    text_uz = RichTextUploadingField(null=True, blank=True)
    link_ru = models.CharField(max_length=100, null=True, blank=True)
    link_uz = models.CharField(max_length=100, null=True, blank=True)
    save_image = models.ImageField(upload_to='images/', null=True, blank=True)
    status = models.BooleanField(default=False)
    date = models.DateTimeField(auto_created=True)

    class Meta:
        ordering = ('id',)
        db_table = 'dividends'
        indexes = [
            models.Index(fields=['id'])
        ]

    def __str__(self):
        return self.title_uz


class QuarterReports(models.Model):
    """ chorak hisobotlarni saqlovchi jadval"""
    title_ru = models.CharField(max_length=100)
    title_uz = models.CharField(max_length=100)
    description_ru = models.TextField(null=True, blank=True)
    description_uz = models.TextField(null=True, blank=True)
    text_ru = RichTextUploadingField(null=True, blank=True)
    text_uz = RichTextUploadingField(null=True, blank=True)
    link_ru = models.CharField(max_length=100, null=True, blank=True)
    link_uz = models.CharField(max_length=100, null=True, blank=True)
    save_image = models.ImageField(upload_to='images/', null=True, blank=True)
    status = models.BooleanField(default=False)
    date = models.DateTimeField(auto_created=True)

    class Meta:
        ordering = ('id',)
        db_table = 'quarter_reports'
        indexes = [
            models.Index(fields=['id'])
        ]

    def __str__(self):
        return self.title_uz

class UserInstructions(models.Model):
    """
    foydalanuvchi ko'rsatmalar ro'yhagti
    (инструкции пользователя)
    """
    title_ru = models.CharField(max_length=100)
    title_uz = models.CharField(max_length=100)
    description_ru = models.TextField(null=True, blank=True)
    description_uz = models.TextField(null=True, blank=True)
    text_ru = RichTextUploadingField(null=True, blank=True)
    text_uz = RichTextUploadingField(null=True, blank=True)
    link_ru = models.CharField(max_length=100, null=True, blank=True)
    link_uz = models.CharField(max_length=100, null=True, blank=True)
    save_image = models.ImageField(upload_to='images/', null=True, blank=True)
    status = models.BooleanField(default=False)
    date = models.DateTimeField(auto_created=True)

    class Meta:
        ordering = ('id',)
        db_table = 'user_instructions'
        indexes = [
            models.Index(fields=['id'])
        ]

    def __str__(self):
        return self.title_uz


class ExecutiveApparatus(models.Model):
    """
        ijro apparati yani ijro bo'lim boshliqlari ro'yhati
    """
    title_ru = models.CharField(max_length=100)
    title_uz = models.CharField(max_length=100)
    description_ru = models.TextField(null=True, blank=True)
    description_uz = models.TextField(null=True, blank=True)
    text_ru = RichTextUploadingField(null=True, blank=True)
    text_uz = RichTextUploadingField(null=True, blank=True)
    link_ru = models.CharField(max_length=100, null=True, blank=True)
    link_uz = models.CharField(max_length=100, null=True, blank=True)
    branch_ru = models.CharField(max_length=100, null=True, blank=True)
    branch_uz = models.CharField(max_length=100, null=True, blank=True)
    save_image = models.ImageField(upload_to='images/', null=True, blank=True)
    status = models.BooleanField(default=False)
    date = models.DateTimeField(auto_created=True)

    class Meta:
        ordering = ('id',)
        db_table = 'executive_apparatus'
        indexes = [
            models.Index(fields=['id'])
        ]

    def __str__(self):
        return self.title_uz


class ShablonUzPostTelNumber(models.Model):
    """
    contact jadvali uchun shablon uzpost telnummer
    jadvali
    """
    tel_number = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        ordering = ('id',)
        db_table = 'shablon_uzpost_tel_number'
        indexes = [
            models.Index(fields=['id'])
        ]

    def __str__(self):
        return self.tel_number


class ShablonContactSpecialTitle(models.Model):
    """
    contact modeli uchun many to many bo'g'laandigan shablon
    """
    title_ru = models.CharField(max_length=100, null=True, blank=True)
    title_uz = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        ordering = ('id',)
        db_table = 'shablon_contact_special_title'
        indexes = [
            models.Index(fields=['id'])
        ]

    def __str__(self):
        return self.title_uz


class Contact(models.Model):
    """
    contact modeli uzpost haqida ma'lumotlar
    """
    title_ru = models.CharField(max_length=100)
    title_uz = models.CharField(max_length=100)
    description_ru = models.TextField(null=True, blank=True)
    description_uz = models.TextField(null=True, blank=True)
    text_ru = RichTextUploadingField(null=True, blank=True)
    text_uz = RichTextUploadingField(null=True, blank=True)
    link_ru = models.CharField(max_length=100, null=True, blank=True)
    link_uz = models.CharField(max_length=100, null=True, blank=True)
    tel_number = models.ManyToManyField(ShablonUzPostTelNumber, blank=True)
    title_2 = models.ManyToManyField(ShablonContactSpecialTitle, blank=True, related_name='title_2')
    description_2 = models.ManyToManyField(ShablonContactSpecialTitle, blank=True, related_name='description_2')
    save_image = models.ImageField(upload_to='images/', null=True, blank=True)
    status = models.BooleanField(default=False)
    date = models.DateTimeField(auto_created=True)

    class Meta:
        ordering = ('id',)
        db_table = 'contact'
        indexes = [
            models.Index(fields=['id'])
        ]

    def __str__(self):
        return self.title_uz


class Advertisements(models.Model):
    """
    reklamalar jadvali

    """
    title_ru = models.CharField(max_length=100)
    title_uz = models.CharField(max_length=100)
    description_ru = models.TextField(null=True, blank=True)
    description_uz = models.TextField(null=True, blank=True)
    text_ru = RichTextUploadingField(null=True, blank=True)
    text_uz = RichTextUploadingField(null=True, blank=True)
    link_ru = models.CharField(max_length=100, null=True, blank=True)
    link_uz = models.CharField(max_length=100, null=True, blank=True)
    save_image = models.ImageField(upload_to='images/', null=True, blank=True)
    status = models.BooleanField(default=False)
    date = models.DateTimeField(auto_created=True)

    class Meta:
        ordering = ('id',)
        db_table = 'advertisements'
        indexes = [
            models.Index(fields=['id'])
        ]

    def __str__(self):
        return self.title_uz


class OrganicManagements(models.Model):
    title_ru = models.CharField(max_length=100)
    title_uz = models.CharField(max_length=100)
    description_ru = models.TextField(null=True, blank=True)
    description_uz = models.TextField(null=True, blank=True)
    text_ru = RichTextUploadingField(null=True, blank=True)
    text_uz = RichTextUploadingField(null=True, blank=True)
    link_ru = models.CharField(max_length=100, null=True, blank=True)
    link_uz = models.CharField(max_length=100, null=True, blank=True)
    tel_number = models.CharField(max_length=50, null=True, blank=True)
    facts = models.CharField(max_length=50, null=True, blank=True)
    working_time = models.CharField(max_length=50, null=True, blank=True)
    save_image = models.ImageField(upload_to='images/', null=True, blank=True)
    working_days = models.ManyToManyField(TegWorkingDays, blank=True, related_name='working_days')
    status = models.BooleanField(default=False)
    date = models.DateTimeField(auto_created=True)

    class Meta:
        ordering = ('id',)
        db_table = 'organic_managements'
        indexes = [
            models.Index(fields=['id'])
        ]

    def __str__(self):
        return self.title_uz


class Partners(models.Model):
    """
        hamkorlar jadvali malumotlarini saqlash uchun model
    """
    title_ru = models.CharField(max_length=100)
    title_uz = models.CharField(max_length=100)
    description_ru = models.TextField(null=True, blank=True)
    description_uz = models.TextField(null=True, blank=True)
    text_ru = RichTextUploadingField(null=True, blank=True)
    text_uz = RichTextUploadingField(null=True, blank=True)
    link_ru = models.CharField(max_length=100, null=True, blank=True)
    link_uz = models.CharField(max_length=100, null=True, blank=True)
    image_ru = models.ManyToManyField(SaveMediaFiles, blank=True, related_name='image_ru')
    image_uz = models.ManyToManyField(SaveMediaFiles, blank=True, related_name='image_uz')
    save_image = models.ImageField(upload_to='images/', null=True, blank=True)
    status = models.BooleanField(default=False)
    date = models.DateTimeField(auto_created=True)

    class Meta:
        ordering = ('id',)
        verbose_name = "Hamkorlar"
        verbose_name_plural = "Hamkorlar"
        db_table = 'partners'
        indexes = [
            models.Index(fields=['id'])
        ]

    def __str__(self):
        return self.title_uz


class RegionalBranches(models.Model):
    """
    Regional Branches jadvali viloyat filiallari ma'lumotlari saqlanadigan jadval
    """
    title_ru = models.CharField(max_length=100)
    title_uz = models.CharField(max_length=100)
    description_ru = models.TextField(null=True, blank=True)
    description_uz = models.TextField(null=True, blank=True)
    text_ru = RichTextUploadingField(null=True, blank=True)
    text_uz = RichTextUploadingField(null=True, blank=True)
    link_ru = models.CharField(max_length=100, null=True, blank=True)
    link_uz = models.CharField(max_length=100, null=True, blank=True)
    filial_name_ru = models.CharField(max_length=100, null=True, blank=True)
    filial_name_uz = models.CharField(max_length=100, null=True, blank=True)
    save_image = models.ImageField(upload_to='images/', null=True, blank=True)
    status = models.BooleanField(default=False)
    date = models.DateTimeField(auto_created=True)

    class Meta:
        ordering = ('id',)
        db_table = 'regional_branches'
        indexes = [
            models.Index(fields=['id'])
        ]

    def __str__(self):
        return self.title_uz


class Advertising(models.Model):
    """
        Reklamalarni yaratish saqlash jadvali
    """
    title_ru = models.CharField(max_length=100)
    title_uz = models.CharField(max_length=100)
    description_ru = models.TextField(null=True, blank=True)
    description_uz = models.TextField(null=True, blank=True)
    text_ru = RichTextUploadingField(null=True, blank=True)
    text_uz = RichTextUploadingField(null=True, blank=True)
    link_ru = models.CharField(max_length=100, null=True, blank=True)
    link_uz = models.CharField(max_length=100, null=True, blank=True)
    save_image = models.ImageField(upload_to='images/', null=True, blank=True)
    status = models.BooleanField(default=False)
    date = models.DateTimeField(auto_created=True)

    class Meta:
        ordering = ('id',)
        db_table = 'advertising'
        indexes = [
            models.Index(fields=['id'])
        ]

    def __str__(self):
        return self.title_uz


class InformationAboutIssuer(models.Model):
    title_ru = models.CharField(max_length=100)
    title_uz = models.CharField(max_length=100)
    description_ru = models.TextField(null=True, blank=True)
    description_uz = models.TextField(null=True, blank=True)
    text_ru = RichTextUploadingField(null=True, blank=True)
    text_uz = RichTextUploadingField(null=True, blank=True)
    link_ru = models.CharField(max_length=100, null=True, blank=True)
    link_uz = models.CharField(max_length=100, null=True, blank=True)
    save_image = models.ImageField(upload_to='images/', null=True, blank=True)
    status = models.BooleanField(default=False)
    date = models.DateTimeField(auto_created=True)

    class Meta:
        ordering = ('id',)
        db_table = 'information_about_issuer'
        indexes = [
            models.Index(fields=['id'])
        ]

    def __str__(self):
        return self.title_uz


class Slides(models.Model):
    """
    slidelar jadvali asosan bosh menuga chiqariladigan ma'lumotlarni saqlaydi
    """
    title_ru = models.CharField(max_length=100)
    title_uz = models.CharField(max_length=100)
    description_ru = models.TextField(null=True, blank=True)
    description_uz = models.TextField(null=True, blank=True)
    text_ru = RichTextUploadingField(null=True, blank=True)
    text_uz = RichTextUploadingField(null=True, blank=True)
    link_ru = models.CharField(max_length=100, null=True, blank=True)
    link_uz = models.CharField(max_length=100, null=True, blank=True)
    google_play = models.CharField(max_length=100, null=True, blank=True)
    app_store = models.CharField(max_length=100, null=True, blank=True)
    knopka_1_ru = models.CharField(max_length=100, null=True, blank=True)
    link_1_ru = models.CharField(max_length=100, null=True, blank=True)
    knopka_1_uz = models.CharField(max_length=100, null=True, blank=True)
    link_1_uz = models.CharField(max_length=100, null=True, blank=True)
    knopka_2_ru = models.CharField(max_length=100, null=True, blank=True)
    link_2_ru = models.CharField(max_length=100, null=True, blank=True)
    knopka_2_uz = models.CharField(max_length=100, null=True, blank=True)
    link_2_uz = models.CharField(max_length=100, null=True, blank=True)
    save_image = models.ImageField(upload_to='images/', null=True, blank=True)
    status = models.BooleanField(default=False)
    date = models.DateTimeField(auto_created=True)

    class Meta:
        ordering = ('id',)
        db_table = 'slides'
        indexes = [
            models.Index(fields=['id'])
        ]

    def __str__(self):
        return self.title_uz


class SocialMedia(models.Model):
    """
    ijtimoiy tarmoqlardagi faol profillarni saqlaydiagn jadval
    """
    title_ru = models.CharField(max_length=100)
    title_uz = models.CharField(max_length=100)
    description_ru = models.TextField(null=True, blank=True)
    description_uz = models.TextField(null=True, blank=True)
    text_ru = RichTextUploadingField(null=True, blank=True)
    text_uz = RichTextUploadingField(null=True, blank=True)
    link_ru = models.CharField(max_length=100, null=True, blank=True)
    link_uz = models.CharField(max_length=100, null=True, blank=True)
    save_image = models.ImageField(upload_to='images/', null=True, blank=True)
    status = models.BooleanField(default=False)
    date = models.DateTimeField(auto_created=True)

    class Meta:
        ordering = ('id',)
        db_table = 'social_medial'
        indexes = [
            models.Index(fields=['id'])
        ]

    def __str__(self):
        return self.title_uz


class EssentialFacts(models.Model):
    """
        muhim bo'lgan factlarni saqlash uchun kerak bo'lgan jadval
    """
    title_ru = models.CharField(max_length=100)
    title_uz = models.CharField(max_length=100)
    description_ru = models.TextField(null=True, blank=True)
    description_uz = models.TextField(null=True, blank=True)
    text_ru = RichTextUploadingField(null=True, blank=True)
    text_uz = RichTextUploadingField(null=True, blank=True)
    link_ru = models.CharField(max_length=100, null=True, blank=True)
    link_uz = models.CharField(max_length=100, null=True, blank=True)
    save_image = models.ImageField(upload_to='images/', null=True, blank=True)
    status = models.BooleanField(default=False)
    date = models.DateTimeField(auto_created=True)

    class Meta:
        ordering = ('id',)
        db_table = 'essential_facts'
        indexes = [
            models.Index(fields=['id'])
        ]

    def __str__(self):
        return self.title_uz


class Rates(models.Model):
    """
     tariflarni saqlaydigan jadval
    """
    title_ru = models.CharField(max_length=200)
    title_uz = models.CharField(max_length=200)
    description_ru = models.TextField(null=True, blank=True)
    description_uz = models.TextField(null=True, blank=True)
    text_ru = RichTextUploadingField(null=True, blank=True)
    text_uz = RichTextUploadingField(null=True, blank=True)
    save_image_uz = models.ImageField(upload_to='images/', null=True, blank=True)
    save_image_ru = models.ImageField(upload_to='images/', null=True, blank=True)
    videos_uz = models.ManyToManyField(SaveMediaFiles, related_name='rates_videos_uz', blank=True)
    videos_ru = models.ManyToManyField(SaveMediaFiles, related_name='rates_videos_ru', blank=True)
    status = models.BooleanField(default=False)
    date = models.DateTimeField(auto_created=True)

    class Meta:
        ordering = ('id',)
        verbose_name = "Link Bilan Murojaat qilinuvchi Sahifalar"
        verbose_name_plural = "Link Bilan Murojaat qilinuvchi Sahifalar"
        db_table = 'rates'
        indexes = [
            models.Index(fields=['id'])
        ]

    def __str__(self):
        return self.title_uz


class CategoryRates(models.Model):
    name_uz = models.CharField(max_length=200, null=True, blank=True)
    name_ru = models.CharField(max_length=200, null=True, blank=True)
    rates_id = models.ManyToManyField(Rates, related_name='category_rates', blank=True)

    class Meta:
        ordering = ('id',)
        verbose_name = "Link Bilan Murojaat qilinuvchi Sahifalar Kategoriyasi"
        verbose_name_plural = "Link Bilan Murojaat qilinuvchi Sahifalar Kategoriyasi"
        db_table = 'category_rates'
        indexes = [
            models.Index(fields=['id'])
        ]

    def __str__(self):
        return self.name_uz


class Services(models.Model):

    """
    xizmatlar malumotlarini saqlanadigan jadval
    """

    title_ru = models.CharField(max_length=100)
    title_uz = models.CharField(max_length=100)
    description_ru = models.TextField(null=True, blank=True)
    description_uz = models.TextField(null=True, blank=True)
    text_ru = RichTextUploadingField(null=True, blank=True)
    text_uz = RichTextUploadingField(null=True, blank=True)
    link_ru = models.CharField(max_length=100, null=True, blank=True)
    link_uz = models.CharField(max_length=100, null=True, blank=True)
    save_image = models.ImageField(upload_to='images/', null=True, blank=True)
    status = models.BooleanField(default=False)
    date = models.DateTimeField(auto_created=True)

    class Meta:
        ordering = ('id',)
        verbose_name = "Xizmatlar"
        verbose_name_plural = "Xizmatlar"
        db_table = 'services'
        indexes = [
            models.Index(fields=['id'])
        ]

    def __str__(self):
        return self.title_uz

##################################################################### new


class CategoryServices(models.Model):
    name_uz = models.CharField(max_length=200, null=True, blank=True)
    name_ru = models.CharField(max_length=200, null=True, blank=True)
    services_id = models.ManyToManyField(Services, related_name='category_services', blank=True)

    class Meta:
        ordering = ('id',)
        verbose_name = "Xizmatlar Kategoriyasi"
        verbose_name_plural = "Xizmatlar Kategoriyasi"
        db_table = 'category_services'
        indexes = [
            models.Index(fields=['id'])
        ]

    def __str__(self):
        return self.name_uz
###########################################################################


class CharterSociety(models.Model):
    """
    ustav jamiyat ma'lumotlarini saqlaydigan jadval
    """
    title_ru = models.CharField(max_length=100)
    title_uz = models.CharField(max_length=100)
    description_ru = models.TextField(null=True, blank=True)
    description_uz = models.TextField(null=True, blank=True)
    text_ru = RichTextUploadingField(null=True, blank=True)
    text_uz = RichTextUploadingField(null=True, blank=True)
    link_ru = models.CharField(max_length=100, null=True, blank=True)
    link_uz = models.CharField(max_length=100, null=True, blank=True)
    save_image = models.ImageField(upload_to='images/', null=True, blank=True)
    status = models.BooleanField(default=False)
    date = models.DateTimeField(auto_created=True)

    class Meta:
        ordering = ('id',)
        db_table = 'charter_society'
        indexes = [
            models.Index(fields=['id'])
        ]

    def __str__(self):
        return self.title_uz


class SecurityPapers(models.Model):
    """
    xavfsizlik hujjatlari saqlanadigan jadval
    """
    title_ru = models.CharField(max_length=100)
    title_uz = models.CharField(max_length=100)
    description_ru = models.TextField(null=True, blank=True)
    description_uz = models.TextField(null=True, blank=True)
    text_ru = RichTextUploadingField(null=True, blank=True)
    text_uz = RichTextUploadingField(null=True, blank=True)
    link_ru = models.CharField(max_length=100, null=True, blank=True)
    link_uz = models.CharField(max_length=100, null=True, blank=True)
    save_image = models.ImageField(upload_to='images/', null=True, blank=True)
    status = models.BooleanField(default=False)
    date = models.DateTimeField(auto_created=True)

    class Meta:
        ordering = ('id',)
        db_table = 'security_papers'
        indexes = [
            models.Index(fields=['id'])
        ]

    def __str__(self):
        return self.title_uz


class FAQ(models.Model):
    """
    ko'p so'raladigan savollar jadvali malumotlarni saqlash uchun model ORM dan foydalangan holda
    """
    title_ru = models.CharField(max_length=100)
    title_uz = models.CharField(max_length=100)
    description_ru = models.TextField(null=True, blank=True)
    description_uz = models.TextField(null=True, blank=True)
    text_ru = RichTextUploadingField(null=True, blank=True)
    text_uz = RichTextUploadingField(null=True, blank=True)
    link_ru = models.CharField(max_length=100, null=True, blank=True)
    link_uz = models.CharField(max_length=100, null=True, blank=True)
    tel_number = models.CharField(max_length=100, null=True, blank=True)
    name_knopka_ru = models.CharField(max_length=100, null=True, blank=True)
    name_knopka_uz = models.CharField(max_length=100, null=True, blank=True)
    link_knopka_ru = models.CharField(max_length=100, null=True, blank=True)
    link_knopka_uz = models.CharField(max_length=100, null=True, blank=True)
    title_2_ru = models.CharField(max_length=100, null=True, blank=True)
    title_2_uz = models.CharField(max_length=100, null=True, blank=True)
    description_2_ru = models.TextField(null=True, blank=True)
    description_2_uz = models.TextField(null=True, blank=True)
    save_image = models.ImageField(upload_to='images/', null=True, blank=True)
    status = models.BooleanField(default=False)
    date = models.DateTimeField(auto_created=True)

    class Meta:
        ordering = ('id',)
        verbose_name = "Ko'p Beriladigan Savollar"
        verbose_name_plural = "Ko'p Beriladigan Savollar"
        db_table = 'faq'
        indexes = [
            models.Index(fields=['id'])
        ]

    def __str__(self):
        return self.title_uz


class CategoryFaq(models.Model):
    name_uz = models.CharField(max_length=200, null=True, blank=True)
    name_ru = models.CharField(max_length=200, null=True, blank=True)
    faq_id = models.ManyToManyField(FAQ, blank=True)

    class Meta:
        ordering = ('id',)
        verbose_name = "Ko'p Beriladigan Savollar Kategoriyasi"
        verbose_name_plural = "Ko'p Beriladigan Savollar Kategoriyasi"
        db_table = 'category-faq'
        indexes = [
            models.Index(fields=['id'])
        ]

    def __str__(self):
        return self.name_uz


class SiteSettings(models.Model):
    """
    bunda sitega tegishli bo'lgan komandalar yoziladi
    """
    name = models.CharField(max_length=100)
    tab = models.CharField(max_length=100, null=False)
    ru = models.CharField(max_length=150, null=False)
    uz = models.CharField(max_length=150, null=False)
    eng = models.CharField(max_length=150, null=False)

    class Meta:
        ordering = ('id', )
        db_table = 'site_settings'
        indexes = [
            models.Index(fields=['id'])
        ]

    def __str__(self):
        return self.name

