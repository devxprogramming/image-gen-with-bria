# Core Django imports
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import get_user_model
from django.views.generic import FormView

# apps forms
from .forms import ImageForm

# restframework imports
from rest_framework import viewsets


# import BriaClient
from bria_client.client import BriaClient



# CONSTANTS
User = get_user_model()
client = BriaClient()

# Create your views here.

class GenerateImage(FormView):
    template_name = "images/test.html"
    form_class = ImageForm
    success_url = "/"

    def get_success_url(self):
        return self.request.path

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.

        # 1. Get form data
        prompt = form.cleaned_data.get('prompt')
        num_results = form.cleaned_data.get('num_results', 1)
        promp_enhancement = form.cleaned_data.get('promp_enhancement', False)

        payload = {
            "prompt": prompt,
            "num_results": num_results,
            "prompt_enhancement": promp_enhancement,
            "sync": True
        }

        # 2. Call the BriaClient to generate the image

        if num_results < 1 or num_results > 4:
            forms.add_error("num_results", "Number of results must be between 1 and 4.")
            return self.form_invalid(form)

        try:
            response = client._base_generation(payload)

            getImages =list(dict.fromkeys(url.strip()
                for item in response.get("result", [])
                for url in item.get("urls", [])
            ))[:num_results]

            # 3. Save the generated images, prompt and num_results to the session
            self.request.session["generated_images"] = getImages
            self.request.session["prompt"] = prompt
            self.request.session["num_results"] = num_results

            # print(self.request.session["generated_images"])

            return HttpResponseRedirect(self.get_success_url())
           
        except Exception as e:
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["images"] = self.request.session.get("generated_images", [])
        print(f"Session Image: {context['images']}")
        context["prompt"] = self.request.session.get("prompt", "")
        context["num_results"] = self.request.session.get("num_results", "")

        return context
        
        
    

class TestImageSuccessRedirect(HttpResponse):
    template_name = 'images/test_image_success.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)