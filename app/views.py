from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .models import Frame
from .forms import AddFrameForm, EditFrameForm, CustomUserCreationForm, DeleteConfirmationForm
import json
from .models import OutputImage
from .utils import parse_feed_and_get_images
from django.shortcuts import get_object_or_404

@login_required
def frame_list(request):
    frames = Frame.objects.filter(owner=request.user)
    return render(request, 'app/frame_list.html', {'frames': frames})

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Save the user
            user = form.save()
            
            # Success message
            messages.success(request, 'Your account has been created successfully!')
            
            # Auto login
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            
            # Redirect to home page
            return redirect('frame_list')
        else:
            # Show error messages if form is invalid
            messages.error(request, 'Error occurred during registration. Please check the information.')
    else:
        # Show empty form on GET request
        form = CustomUserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})

@login_required
def add_frame(request):
    if request.method == 'POST':
        form = AddFrameForm(request.POST, request.FILES)
        if form.is_valid():
            frame = form.save(commit=False)
            frame.owner = request.user
            frame.save()
            messages.success(request, f'Frame "{frame.name}" created successfully!')
            return redirect('frame_list')
        else:
            messages.error(request, 'There are errors in the form. Please check the information.')
    else:
        form = AddFrameForm()
    return render(request, 'app/add_frame.html', {'form': form})

@login_required
def preview_frame(request, frame_id):
    frame = get_object_or_404(Frame, id=frame_id, owner=request.user)
    feed_url = frame.xmlFeedPath
    image_links = parse_feed_and_get_images(feed_url)
    first_image = image_links[0] if image_links else None

    if request.method == 'POST':
        coordinates_str = request.POST.get('coordinates')
        if coordinates_str:
            try:
                coordinates = json.loads(coordinates_str)
                frame.coordinates = coordinates
                frame.save()
                
                # Start processing directly without checking existing outputs
                try:
                    from .tasks import process_feed_entries
                    process_feed_entries.delay(frame.id)
                    messages.success(request, 'Coordinates saved! Background processing started for all images.')
                except Exception as e:
                    # Fallback: Sync processing
                    from .tasks import process_feed_entries
                    process_feed_entries(frame.id)  # Run synchronously
                    messages.success(request, 'Coordinates saved! Images processed synchronously.')
                    
                return redirect('frame_detail', frame_id=frame.id)
            except json.JSONDecodeError:
                messages.error(request, 'Invalid JSON format for coordinates.')
        else:
            messages.error(request, 'No coordinates provided.')
    
    return render(request, 'app/preview_frame.html', {
        'frame': frame,
        'first_image': first_image,
        'image_links': image_links
    })

@login_required
def frame_detail(request, frame_id):
    """Frame detail page - Shows details and outputs of the given frame"""
    frame = get_object_or_404(Frame, id=frame_id, owner=request.user)
    
    return render(request, 'app/frame_detail.html', {'frame': frame})

@login_required
def frame_outputs_ajax(request, frame_id):
    frame = get_object_or_404(Frame, id=frame_id, owner=request.user)
    
    # DataTable parameters
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 5))
    search_value = request.GET.get('search[value]', '')
    
    # Filter outputs
    outputs = frame.outputs.all()
    if search_value:
        # Search in the product_id field
        outputs = outputs.filter(product_id__icontains=search_value)
    
    # Pagination
    total_records = outputs.count()
    outputs = outputs[start:start + length]
    
    # Prepare data for DataTable
    data = []
    for output in outputs:
        data.append({
            'id': output.id,
            'product_id': output.product_id,
            'image_url': output.image.url if output.image else '',
            'created_at': output.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        })
    
    return JsonResponse({
        'draw': int(request.GET.get('draw', 1)),
        'recordsTotal': total_records,
        'recordsFiltered': total_records,
        'data': data
    })

@login_required
def delete_output(request, output_id):
    if request.method == 'POST':
        try:
            output = get_object_or_404(OutputImage, id=output_id, frame__owner=request.user)
            product_id = output.product_id
            
            # Delete the image file if it exists
            if output.image:
                output.image.delete()
            output.delete()
            
            return JsonResponse({
                'success': True, 
                'message': f'Output for product {product_id} deleted successfully'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@login_required
def edit_frame(request, frame_id):
    frame = get_object_or_404(Frame, id=frame_id, owner=request.user)
    
    if request.method == 'POST':
        form = EditFrameForm(request.POST, request.FILES, instance=frame)
        if form.is_valid():
            # Check if image was changed
            image_changed = 'image' in form.changed_data
            
            form.save()
            
            if image_changed:
                messages.warning(request, f'Frame "{frame.name}" updated successfully! Note: You may need to re-set coordinates due to image change.')
            else:
                messages.success(request, f'Frame "{frame.name}" updated successfully!')
            
            return redirect('frame_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EditFrameForm(instance=frame)
    
    return render(request, 'app/edit_frame.html', {
        'form': form,
        'frame': frame
    })

@login_required
def delete_frame(request, frame_id):
    frame = get_object_or_404(Frame, id=frame_id, owner=request.user)
    
    if request.method == 'POST':
        # Simple POST handling without complex form validation
        frame_name = frame.name
        
        # Delete all output images and their files
        outputs = frame.outputs.all()
        deleted_outputs = 0
        for output in outputs:
            if output.image:
                try:
                    output.image.delete()  # This deletes the file from filesystem
                    deleted_outputs += 1
                except:
                    pass  # Continue even if file deletion fails
        
        # Delete frame image file
        if frame.image:
            try:
                frame.image.delete()
            except:
                pass
        
        # Delete frame record (this will cascade delete all outputs due to ForeignKey)
        frame.delete()
        
        messages.success(request, f'Frame "{frame_name}" and {deleted_outputs} output images have been deleted successfully.')
        return redirect('frame_list')
    
    # If GET request, show confirmation page with a simple confirmation form
    form = DeleteConfirmationForm(item_name=frame.name)
    
    return render(request, 'app/delete_frame_confirm.html', {
        'frame': frame,
        'form': form
    })