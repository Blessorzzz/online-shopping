from django.contrib import admin
from django.utils.html import format_html
from .models import Product, ProductPhoto, ProductVideo
from shoppingcart.models import Order, OrderItem
from .forms import ProductForm
from .mhi import get_material_risk_class, convert_mhi_to_score
from django.utils.safestring import SafeString

class ProductPhotoInline(admin.TabularInline):
    model = ProductPhoto
    extra = 3
    max_num = 10
    fk_name = 'product'

class ProductVideoInline(admin.TabularInline):
    model = ProductVideo
    extra = 1
    max_num = 5
    fk_name = 'product'

class ProductAdmin(admin.ModelAdmin):
    form = ProductForm  # Use the custom form
    inlines = [ProductPhotoInline, ProductVideoInline]
    list_display = (
        'product_name',
        'product_type',
        'price',
        'vendor',
        'safety_rating_display'
    )
    list_filter = ('product_type', 'vendor')
    search_fields = ('product_name', 'vendor__username')
    readonly_fields = (
        'get_mhi_score',
        'get_acr_score',
        'get_vhd_score',
        'get_ics_score',
        'safety_score',
        'material_safety_report',
    )
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('product_name', 'price', 'is_active', 'description', 'thumbnail_image', 'vendor', 'stock_quantity'),
        }),
        ('Product Classification', {
            'fields': ('product_type', 'min_age', 'max_age'),
        }),
        ('Material and Safety', {
            'fields': ('material_choices', 'warnings'),
            'classes': ('wide',),
        }),
        ('Hazard Detection', {
            'fields': ('safety_issues',),
            'description': 'Safety issues are used to calculate the Visual Hazard Detection (VHD) score and Age Compliance Risk (ACR) score.',
            'classes': ('wide',),
        }),
        ('Safety Analysis', {
            'fields': ('safety_score', 'get_mhi_score', 'get_acr_score', 'get_vhd_score', 'get_ics_score', 'material_safety_report'),
            'classes': ('collapse',),
            'description': 'Comprehensive safety analysis results. These fields are read-only and calculated automatically based on product information.'
        }),
    )


    def get_mhi_score(self, obj):
        """Display the Material Hazard Index (MHI) score with a progress bar."""
        try:
            # Skip calculation for unsaved or non-tangible products
            if not obj.pk or obj.product_type != 'tangible':
                return "N/A"
                
            score = obj.get_mhi_score()
            if score is None:
                return "N/A"
                
            # Make sure score is a number - convert from SafeString if needed
            if isinstance(score, SafeString):
                score = float(str(score))
            else:
                try:
                    score = float(score)
                except (TypeError, ValueError):
                    return "Error: Invalid score value"
            
            return format_html(
                '<div style="width:100%; max-width:200px; background-color:#f0f0f0; border-radius:5px;">'
                '<div style="width:{}%; background-color:{}; height:20px; border-radius:5px; text-align:center; overflow:hidden;">'
                '<span style="line-height:20px; color:#fff; text-shadow:1px 1px 1px rgba(0,0,0,0.5); white-space:nowrap;">{}</span>'
                '</div></div>',
                min(100, score),  # Ensure width never exceeds 100%
                self._get_color_for_score(score),
                round(score, 1)  # Use round instead of format string
            )
        except Exception as e:
            import logging
            logging.error(f"Error displaying MHI score: {e}")
            return "N/A"  # Simplified error handling to avoid template issues
    get_mhi_score.short_description = "Material Hazard Index Score"

    def get_acr_score(self, obj):
        """Display the Age Compliance Risk score with a progress bar."""
        try:
            # Skip calculation for unsaved or non-tangible products
            if not obj.pk or obj.product_type != 'tangible':
                return "N/A"
                
            score = obj.get_acr_score()
            if score is None:
                return "N/A"
                
            # Make sure score is a number - convert from SafeString if needed
            if isinstance(score, SafeString):
                score = float(str(score))
            else:
                try:
                    score = float(score)
                except (TypeError, ValueError):
                    return "Error: Invalid score value"
            
            return format_html(
                '<div style="width:100%; max-width:200px; background-color:#f0f0f0; border-radius:5px;">'
                '<div style="width:{}%; background-color:{}; height:20px; border-radius:5px; text-align:center; overflow:hidden;">'
                '<span style="line-height:20px; color:#fff; text-shadow:1px 1px 1px rgba(0,0,0,0.5); white-space:nowrap;">{}</span>'
                '</div></div>',
                min(100, score),  # Ensure width never exceeds 100%
                self._get_color_for_score(score),
                round(score, 1)  # Use round instead of format string
            )
        except Exception as e:
            import logging
            logging.error(f"Error displaying ACR score: {e}")
            return "N/A"  # Simplified error handling to avoid template issues
    get_acr_score.short_description = "Age Compliance Risk Score"

    def get_vhd_score(self, obj):
        """Display the Visual Hazard Detection score with a progress bar."""
        try:
            # Skip calculation for unsaved or non-tangible products
            if not obj.pk or obj.product_type != 'tangible':
                return "N/A"
                
            score = obj.get_vhd_score()
            if score is None:
                return "N/A"
                
            # Make sure score is a number - convert from SafeString if needed
            if isinstance(score, SafeString):
                score = float(str(score))
            else:
                try:
                    score = float(score)
                except (TypeError, ValueError):
                    return "Error: Invalid score value"
            
            return format_html(
                '<div style="width:100%; max-width:200px; background-color:#f0f0f0; border-radius:5px;">'
                '<div style="width:{}%; background-color:{}; height:20px; border-radius:5px; text-align:center; overflow:hidden;">'
                '<span style="line-height:20px; color:#fff; text-shadow:1px 1px 1px rgba(0,0,0,0.5); white-space:nowrap;">{}</span>'
                '</div></div>',
                min(100, score),  # Ensure width never exceeds 100%
                self._get_color_for_score(score),
                round(score, 1)  # Use round instead of format string
            )
        except Exception as e:
            import logging
            logging.error(f"Error displaying VHD score: {e}")
            return "N/A"  # Simplified error handling to avoid template issues
    get_vhd_score.short_description = "Visual Hazard Detection Score"

    def get_ics_score(self, obj):
        """Display the Information Completeness Score with a progress bar."""
        try:
            # Skip calculation for unsaved or non-tangible products
            if not obj.pk or obj.product_type != 'tangible':
                return "N/A"
                
            score = obj.get_ics_score()
            if score is None:
                return "N/A"
                
            # Make sure score is a number - convert from SafeString if needed
            if isinstance(score, SafeString):
                score = float(str(score))
            else:
                try:
                    score = float(score)
                except (TypeError, ValueError):
                    return "Error: Invalid score value"
            
            return format_html(
                '<div style="width:100%; max-width:200px; background-color:#f0f0f0; border-radius:5px;">'
                '<div style="width:{}%; background-color:{}; height:20px; border-radius:5px; text-align:center; overflow:hidden;">'
                '<span style="line-height:20px; color:#fff; text-shadow:1px 1px 1px rgba(0,0,0,0.5); white-space:nowrap;">{}</span>'
                '</div></div>',
                min(100, score),  # Ensure width never exceeds 100%
                self._get_color_for_score(score),
                round(score, 1)  # Use round instead of format string
            )
        except Exception as e:
            import logging
            logging.error(f"Error displaying ICS score: {e}")
            return "N/A"  # Simplified error handling to avoid template issues
    get_ics_score.short_description = "Information Completeness Score"

    def safety_rating_display(self, obj):
        """Display safety rating as a letter grade based on the safety score."""
        if obj.product_type != 'tangible' or obj.safety_score is None:
            return "N/A"
            
        # Get safety rating letter based on score
        score = obj.safety_score
        if score >= 90:
            rating = "A"
            color = "#28a745"  # Green
        elif score >= 80:
            rating = "B"
            color = "#5cb85c"  # Light green
        elif score >= 70:
            rating = "C"
            color = "#f0ad4e"  # Yellow
        elif score >= 60:
            rating = "D"
            color = "#ff7f50"  # Orange
        elif score >= 50:
            rating = "E"
            color = "#d9534f"  # Light red
        else:
            rating = "F"
            color = "#cc0000"  # Dark red
            
        return format_html(
            '<span style="font-weight:bold; color:white; background-color:{}; padding:3px 8px; border-radius:3px;">{}</span>',
            color, rating
        )
    safety_rating_display.short_description = "Safety Rating"

    def material_safety_report(self, obj):
        """Generate and display a comprehensive material safety report."""
        try:
            # Skip report for unsaved or non-tangible products
            if not obj.pk or obj.product_type != 'tangible':
                return "Not applicable for virtual products"
                
            report = obj.get_material_safety_report()
            if not report or not isinstance(report, dict):
                return "Unable to generate material safety report"
                
            if not report.get('applicable', False):
                return report.get('message', "Unable to generate material safety report")
                
            # Format material report as HTML
            html = '<div style="padding: 10px;">'
            
            # Overall risk
            risk_class = report.get('risk_class', '?')
            risk_value = report.get('risk_value', 0)
            score = report.get('score', 0)
            color = self._get_color_for_score(score)
            
            html += f'<h3 style="margin-top:0;">Material Safety Summary</h3>'
            html += f'<p><strong>Overall Risk:</strong> {report.get("risk_level", "Unknown")} (Class {risk_class}, Score: {score})</p>'
            html += f'<div style="width:50%; background-color:#f0f0f0; border-radius:5px; margin-bottom:15px;">'
            html += f'<div style="width:{score}%; background-color:{color}; height:20px; border-radius:5px;"></div></div>'
            
            # Materials breakdown
            materials = report.get('materials', {})
            if materials:
                html += '<h4>Material Breakdown</h4>'
                html += '<table style="width:100%; border-collapse:collapse;">'
                html += '<tr style="background-color:#487494;"><th style="text-align:left; padding:5px;">Material</th>'
                html += '<th style="text-align:center; padding:5px;">Risk Class</th>'
                html += '<th style="text-align:center; padding:5px;">Risk Value</th>'
                html += '<th style="text-align:left; padding:5px;">Notes</th></tr>'
                
                for material, info in materials.items():
                    if not isinstance(info, dict):
                        continue
                        
                    material_score = convert_mhi_to_score(info.get('risk_value', 6))
                    material_color = self._get_color_for_score(material_score)
                    
                    html += f'<tr style="border-bottom:1px solid #ddd;">'
                    html += f'<td style="padding:5px;">{material}</td>'
                    html += f'<td style="text-align:center; padding:5px;"><span style="font-weight:bold; color:white; '
                    html += f'background-color:{material_color}; padding:2px 6px; border-radius:3px;">{info.get("risk_class", "?")}</span></td>'
                    html += f'<td style="text-align:center; padding:5px;">{info.get("risk_value", "?")}</td>'
                    
                    notes = []
                    if info.get('reasons'):
                        notes.extend(info.get('reasons', []))
                    if info.get('allergen'):
                        notes.append("<strong>Allergen warning</strong>")
                    if info.get('restricted'):
                        notes.append("<strong>Restricted material</strong>")
                    if info.get('banned'):
                        notes.append("<strong>Banned material</strong>")
                        
                    notes_html = "<br>".join(notes) if notes else "No special concerns"
                    html += f'<td style="padding:5px;">{notes_html}</td></tr>'
                    
                html += '</table>'
            else:
                html += '<p>No material information available.</p>'
            
            # Recommendations
            recommendations = report.get('recommendations', [])
            if recommendations:
                html += '<h4>Recommendations</h4><ul>'
                for rec in recommendations:
                    html += f'<li>{rec}</li>'
                html += '</ul>'
                
            html += '</div>'
            return format_html(html)
        except Exception as e:
            import logging
            logging.error(f"Error generating material safety report: {e}")
            return "Unable to generate material safety report"
    material_safety_report.short_description = "Material Safety Report"

        
    def _get_color_for_score(self, score):
        """Return color based on score value"""
        if score >= 90:
            return "#28a745"  # Green
        elif score >= 80:
            return "#5cb85c"  # Light green
        elif score >= 70:
            return "#f0ad4e"  # Yellow
        elif score >= 60:
            return "#ff7f50"  # Orange
        elif score >= 50:
            return "#d9534f"  # Light red
        else:
            return "#cc0000"  # Dark red

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if obj and obj.product_type != 'tangible':
            # For virtual products, hide safety fields
            return readonly_fields
        return readonly_fields
    
    def save_model(self, request, obj, form, change):
        # Handle the case where materials field might be hidden in the form
        if 'material_choices' in form.cleaned_data:
            selected_materials = form.cleaned_data.get('material_choices', [])
            # Convert selected material keys to proper format and save to materials field
            formatted_materials = [m.replace('_', ' ') for m in selected_materials]
            obj.materials = ', '.join(formatted_materials)
        super().save_model(request, obj, form, change)

    class Media:
        css = {
            'all': ('admin/css/product_admin.css',)
        }
        js = ('admin/js/product_safety.js',)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    list_display = ('po_number', 'customer', 'total_amount', 'status', 'purchase_date')
    list_filter = ('status', 'purchase_date')
    search_fields = ('po_number', 'customer__username')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:
            product_type = obj.items.first().product.product_type if obj.items.exists() else 'tangible'
            if product_type == 'tangible':
                form.base_fields['status'].choices = Order.STATUS_CHOICES_TANGIBLE
            else:
                form.base_fields['status'].choices = Order.STATUS_CHOICES_VIRTUAL
        return form

admin.site.register(Product, ProductAdmin)
admin.site.register(ProductPhoto)
admin.site.register(ProductVideo)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
