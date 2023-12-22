from django.db import models

# Add these:
from modelcluster.fields import ParentalKey
from wagtail.models import Page, Orderable
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.search import index
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock




class DoctorPage(Page):
	pass 




class BlogIndexPage(Page):
    intro = RichTextField(blank=True)


    def get_context(self, request):
        # Update context to include only published posts, ordered by reverse-chron
        context = super().get_context(request)
        # blogpages = self.get_children().live().order_by('-first_published_at').type(BlogPage)
        blogpages = BlogPage.objects.live().order_by('-first_published_at').descendant_of(self)
     
        category_page =  BlogIndexPage.objects.live().order_by('-first_published_at').descendant_of(self)

        context['blogpages'] = blogpages
        context['category_page'] = category_page
        return context


    content_panels = Page.content_panels + [
        FieldPanel('intro')
    ]


class BlogPage(Page):
    date = models.DateField("Post date")
    intro = models.CharField(max_length=250)
    body = StreamField([
        ('heading', blocks.CharBlock(form_classname="title")),
        ('richTextParagraph', blocks.RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('quote', blocks.BlockQuoteBlock()),
        ('paragraph', blocks.TextBlock()), 
        ('rawHTML',blocks.RawHTMLBlock(help_text="for ordered list, use class='list-numbers' 2.")),
        ('twoImage', blocks.StructBlock([
        	('image1',ImageChooserBlock(required=True)),
        	('image2', ImageChooserBlock(required=True)), 

        	])), #need caption, also one image (wide and standard )
        ('highlight', blocks.TextBlock()), #not implemented yet

    ], use_json_field=True)


    def main_image(self):
        gallery_item = self.gallery_images.first()
        if gallery_item:
            return gallery_item.image
        else:
            return None	


    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.SearchField('body'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('date'),
        FieldPanel('intro'),
        FieldPanel('body'),
        InlinePanel('gallery_images', label="Gallery images"),
    ]

class BlogPageGalleryImage(Orderable):
    page = ParentalKey(BlogPage, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.CASCADE, related_name='+'
    )
    caption = models.CharField(blank=True, max_length=250)

    panels = [
        FieldPanel('image'),
        FieldPanel('caption'),
    ]