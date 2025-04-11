from django import forms
from .models import Product
from .mhi import get_material_options  # Import the function from your mhi module
from django.contrib.admin.widgets import FilteredSelectMultiple
import json

class ProductForm(forms.ModelForm):
    # Use get_material_options function to get the material choices
    material_choices = forms.MultipleChoiceField(
        choices=get_material_options(),  # This will use your existing function
        required=False,
        widget=FilteredSelectMultiple("Materials", False),
        help_text="Select all materials used in this product."
    )
    
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'safety_issues': forms.Textarea(attrs={'rows': 4}),
        }
        help_texts = {
            'safety_issues': 'Enter safety issues as a JSON list of objects. Each object should have a "type" field.',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Special handling for safety_issues JSONField
        if 'safety_issues' in self.fields:
            instance = kwargs.get('instance', None)
            if instance and hasattr(instance, 'safety_issues') and instance.safety_issues:
                if isinstance(instance.safety_issues, list):
                    # Convert list to formatted JSON string for the textarea
                    self.initial['safety_issues'] = json.dumps(instance.safety_issues, indent=2)
        
        # If we have an existing instance with materials, pre-select them in the material_choices
        if self.instance.pk and self.instance.materials:
            selected_materials = [m.strip().lower().replace(' ', '_') 
                                for m in self.instance.materials.split(',')]
            self.fields['material_choices'].initial = selected_materials
    
    def clean_safety_issues(self):
        """Ensure safety_issues is properly formatted as JSON"""
        safety_issues = self.cleaned_data.get('safety_issues')
        
        if not safety_issues:
            return []
            
        # If it's a string, try to parse it as JSON
        if isinstance(safety_issues, str):
            try:
                safety_issues = json.loads(safety_issues)
            except json.JSONDecodeError:
                raise forms.ValidationError("Safety issues must be valid JSON format")
        
        # Ensure it's a list
        if not isinstance(safety_issues, list):
            raise forms.ValidationError("Safety issues must be a list of objects")
            
        # Verify each item has a 'type' field
        for item in safety_issues:
            if not isinstance(item, dict) or 'type' not in item:
                raise forms.ValidationError("Each safety issue must be an object with at least a 'type' field")
                
        return safety_issues
    
    class Media:
        css = {
            'all': ('admin/css/widgets.css',)
        }
        js = ('/admin/jsi18n/',)
