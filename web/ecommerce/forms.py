from django import forms
from .models import Product
from .safety.mhi import get_material_options  # Import the function from your mhi module
from django.contrib.admin.widgets import FilteredSelectMultiple
import json

# Define common safety issue choices
SAFETY_ISSUE_CHOICES = [
    ('small_part', 'Small Parts'),
    ('sharp_edges', 'Sharp Edges'),
    ('toxic_paint', 'Toxic Paint'),
    ('long_cords', 'Long Cords'),
    ('choking_hazard', 'Choking Hazard'),
    ('suffocation_risk', 'Suffocation Risk'),
    ('magnets', 'Magnets'),
    ('batteries', 'Button/Coin Batteries')
]

class ProductForm(forms.ModelForm):
    # Use get_material_options function to get the material choices
    material_choices = forms.MultipleChoiceField(
        choices=get_material_options(),  # This will use your existing function
        required=False,
        widget=FilteredSelectMultiple("Materials", False),
        help_text="Select all materials used in this product."
    )
    
    # Add common safety issues as checkboxes for easier selection
    common_safety_issues = forms.MultipleChoiceField(
        choices=SAFETY_ISSUE_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Common Safety Issues",
        help_text="Select any common safety concerns for this product."
    )
    
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'safety_issues': forms.Textarea(attrs={'rows': 4}),
        }
        help_texts = {
            'safety_issues': 'Optional: Enter additional safety issues as JSON. Format: [{"type": "issue_name", "details": "description"}]',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Make safety_issues not required
        if 'safety_issues' in self.fields:
            self.fields['safety_issues'].required = False
        
        # Special handling for safety_issues JSONField
        if 'safety_issues' in self.fields:
            instance = kwargs.get('instance', None)
            if instance and hasattr(instance, 'safety_issues') and instance.safety_issues:
                if isinstance(instance.safety_issues, list):
                    # Pre-select common safety issues checkboxes
                    selected_issues = []
                    custom_issues = []
                    
                    for issue in instance.safety_issues:
                        if isinstance(issue, dict) and 'type' in issue:
                            issue_type = issue['type']
                            if issue_type in dict(SAFETY_ISSUE_CHOICES).keys():
                                selected_issues.append(issue_type)
                            else:
                                custom_issues.append(issue)
                        elif isinstance(issue, str):
                            if issue in dict(SAFETY_ISSUE_CHOICES).keys():
                                selected_issues.append(issue)
                            else:
                                custom_issues.append({"type": issue})
                    
                    # Set initial values
                    self.fields['common_safety_issues'].initial = selected_issues
                    if custom_issues:
                        self.initial['safety_issues'] = json.dumps(custom_issues, indent=2)
                    else:
                        self.initial['safety_issues'] = '[]'
        
        # If we have an existing instance with materials, pre-select them in the material_choices
        if self.instance.pk and self.instance.materials:
            selected_materials = [m.strip().lower().replace(' ', '_') 
                                for m in self.instance.materials.split(',')]
            self.fields['material_choices'].initial = selected_materials
    
    def clean_safety_issues(self):
        """Ensure safety_issues is properly formatted as JSON"""
        safety_issues = self.cleaned_data.get('safety_issues')
        
        # Handle empty values
        if not safety_issues or safety_issues == '[]':
            return []
            
        # If it's a string, try to parse it as JSON
        if isinstance(safety_issues, str):
            try:
                safety_issues = json.loads(safety_issues)
            except json.JSONDecodeError:
                raise forms.ValidationError("Safety issues must be valid JSON format")
        
        # Ensure it's a list
        if not isinstance(safety_issues, list):
            raise forms.ValidationError("Safety issues must be a list")
            
        # Convert simple strings to objects with type field if needed
        formatted_issues = []
        for item in safety_issues:
            if isinstance(item, str):
                formatted_issues.append({"type": item})
            elif isinstance(item, dict) and 'type' in item:
                formatted_issues.append(item)
            else:
                raise forms.ValidationError("Each safety issue must be an object with at least a 'type' field")
                
        return formatted_issues
    
    def clean(self):
        """
        Custom clean method to make safety_issues optional when common_safety_issues are selected
        """
        cleaned_data = super().clean()
        common_issues = cleaned_data.get('common_safety_issues', [])
        
        # If common_safety_issues are selected, we don't need to require safety_issues
        if common_issues and 'safety_issues' in self._errors:
            # Remove the error if it's just about required field
            if any('required' in str(error).lower() for error in self._errors['safety_issues']):
                del self._errors['safety_issues']
                # Re-add the field to cleaned_data with empty list
                cleaned_data['safety_issues'] = []
        
        return cleaned_data
    
    def save(self, commit=True):
        """Save both common and custom safety issues together"""
        instance = super().save(commit=False)
        
        # Get common safety issues from checkboxes
        common_issues = [{"type": issue} for issue in self.cleaned_data.get('common_safety_issues', [])]
        
        # Get custom safety issues from JSON field
        custom_issues = self.cleaned_data.get('safety_issues', []) or []
        
        # Combine all safety issues
        instance.safety_issues = common_issues + custom_issues
        
        if commit:
            instance.save()
        return instance
    
    class Media:
        css = {
            'all': ('admin/css/widgets.css',)
        }
        js = ('/admin/jsi18n/',)
