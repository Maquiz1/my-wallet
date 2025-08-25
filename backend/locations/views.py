from multiprocessing import context
from django.views.generic import ListView, DetailView
from .models import Country, Region, District, Site
from django.db.models import Count,Q
from mentorship.models import VisitDay

class CountryListView(ListView):
    model = Country
    template_name = 'locations/country_list.html'
    
    def get_queryset(self):
        return Country.objects.annotate(
            region_count=Count("regions", distinct=True),
            district_count=Count("regions__districts", distinct=True),
            site_count=Count("regions__districts__sites", distinct=True),
        )

class CountryDetailView(DetailView):
    model = Country
    template_name = 'locations/country_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['regions'] = Region.objects.filter(country=self.object)
        return context
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["regions"] = (
            Region.objects.filter(country=self.object)
            .annotate(
                district_count=Count("districts", distinct=True),
                site_count=Count("districts__sites", distinct=True),
            )
        )
        return context

class RegionDetailView(DetailView):
    model = Region
    template_name = 'locations/region_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["districts"] = (
            District.objects.filter(region=self.object)
            .annotate(site_count=Count("sites"))  # 👈 if you added related_name="sites"
        )
        return context

class DistrictDetailView(DetailView):
    model = District
    template_name = 'locations/district_detail.html'
    context_object_name = 'object'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Annotate each site with total VisitDays and completed VisitDays
        sites = (
            Site.objects.filter(district=self.object)
            .annotate(
                mentorship_count=Count("visit__days", distinct=True),  # all VisitDays
                completed_count=Count(
                    "visit__days",
                    filter=Q(visit__days__status="completed"),
                    distinct=True
                )
            )
        )
        
        context.update({
            'sites': sites,
            'region': self.object.region,
            'country': self.object.region.country,
        })
        
        return context

class SiteDetailView(DetailView):
    model = Site
    template_name = 'locations/site_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        district = self.object.district
        region = district.region
        country = region.country

        # Count all VisitDay entries linked to this site
        mentorship_count = VisitDay.objects.filter(visit__site=self.object).count()

        context.update({
            'district': district,
            'region': region,
            'country': country,
            'mentorship_count': mentorship_count,
        })
        return context
