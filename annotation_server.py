#!/usr/bin/env python3
"""
Dark Pattern Annotation Server
Serves images and handles annotation saving for the UI Dark Pattern Experts interface.
"""

import os
import json
import glob
import re
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory, render_template_string
from flask_cors import CORS
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
IMAGES_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'}
ANNOTATIONS_DIR = 'annotations'
os.makedirs(ANNOTATIONS_DIR, exist_ok=True)

def natural_sort_key(text):
    """Convert a string into a list of string and number chunks.
    "z23a" -> ["z", 23, "a"]
    """
    def atoi(text):
        return int(text) if text.isdigit() else text
    return [atoi(c) for c in re.split(r'(\d+)', text)]

def get_images_from_folder(folder_path):
    """Get all image files from a folder and its subfolders."""
    images = []
    
    if not os.path.exists(folder_path):
        logger.warning(f"Folder does not exist: {folder_path}")
        return images
    
    # Walk through the folder and find all image files
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            file_ext = os.path.splitext(file)[1].lower()
            
            if file_ext in IMAGES_EXTENSIONS:
                # Create a relative path from the current directory
                rel_path = os.path.relpath(file_path, os.getcwd())
                images.append(rel_path.replace('\\', '/'))  # Normalize path separators
    
    # Sort images using natural sorting for consistent ordering
    images.sort(key=natural_sort_key)
    return images

@app.route('/')
def index():
    """Serve the main annotation interface."""
    return send_from_directory('.', 'annotation_interface.html')

@app.route('/viewer')
def viewer():
    """Serve the annotation viewer interface."""
    return send_from_directory('.', 'annotation_viewer.html')

@app.route('/folders_summary.json')
def get_folders_summary():
    """Serve the folders summary JSON file."""
    try:
        with open('folders_summary.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)
    except FileNotFoundError:
        return jsonify({"error": "folders_summary.json not found"}), 404
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON in folders_summary.json"}), 500

@app.route('/api/images')
def get_images():
    """Get all images from a specific folder."""
    folder = request.args.get('folder')
    
    if not folder:
        return jsonify({"error": "Folder parameter is required"}), 400
    
    # Convert folder path to actual directory path
    # Remove the 'diverse_searchers_task_folders\\' prefix if present
    if folder.startswith('diverse_searchers_task_folders\\'):
        folder = folder.replace('diverse_searchers_task_folders\\', '')
    
    # Handle different path formats
    folder = folder.replace('\\', '/')
    
    # Extract just the folder name (e.g., "United_Airlines_a_alt1" from the full path)
    folder_name = folder.split('/')[-1]
    
    logger.info(f"Looking for images in folder: {folder_name}")
    
    images = get_images_from_folder(folder_name)
    
    logger.info(f"Found {len(images)} images in {folder_name}")
    
    return jsonify({
        "folder": folder,
        "images": images,
        "count": len(images)
    })

@app.route('/api/save-annotations', methods=['POST'])
def save_annotations():
    """Save annotations to a JSON file."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Extract data
        folder = data.get('folder', 'unknown')
        image = data.get('image', 'unknown')
        annotations = data.get('annotations', [])
        folder_comment = data.get('folderComment', '')
        expert = data.get('expert', 'unknown')
        timestamp = data.get('timestamp', datetime.now().isoformat())
        
        # Create a filename based on the folder and image
        folder_name = os.path.basename(folder.replace('\\', '/').replace('/', '_'))
        image_name = os.path.splitext(os.path.basename(image))[0]
        
        # Create a safe filename
        safe_filename = f"{folder_name}_{image_name}_{expert}.json"
        safe_filename = "".join(c for c in safe_filename if c.isalnum() or c in ('-', '_', '.'))
        
        annotation_file = os.path.join(ANNOTATIONS_DIR, safe_filename)
        
        # Prepare the annotation data
        annotation_data = {
            "folder": folder,
            "image": image,
            "annotations": annotations,
            "folder_comment": folder_comment,
            "expert": expert,
            "timestamp": timestamp,
            "total_annotations": len(annotations)
        }
        
        # Save to file
        with open(annotation_file, 'w', encoding='utf-8') as f:
            json.dump(annotation_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved annotations to {annotation_file}")
        
        return jsonify({
            "success": True,
            "message": "Annotations saved successfully",
            "file": annotation_file,
            "annotations_count": len(annotations)
        })
        
    except Exception as e:
        logger.error(f"Error saving annotations: {str(e)}")
        return jsonify({"error": f"Failed to save annotations: {str(e)}"}), 500

@app.route('/api/annotations')
def list_annotations():
    """List all saved annotations."""
    try:
        annotation_files = glob.glob(os.path.join(ANNOTATIONS_DIR, '*.json'))
        annotations = []
        
        for file_path in annotation_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    data['file'] = os.path.basename(file_path)
                    annotations.append(data)
            except Exception as e:
                logger.warning(f"Error reading annotation file {file_path}: {e}")
        
        return jsonify({
            "annotations": annotations,
            "total": len(annotations)
        })
        
    except Exception as e:
        logger.error(f"Error listing annotations: {str(e)}")
        return jsonify({"error": f"Failed to list annotations: {str(e)}"}), 500

@app.route('/api/folders')
def list_folders():
    """List all available folders with their image counts."""
    try:
        with open('folders_summary.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        folders_info = []
        for folder_info in data.get('folders', []):
            folder_path = folder_info.get('folder_path', '')
            
            # Convert to actual path
            if folder_path.startswith('diverse_searchers_task_folders\\'):
                folder_path = folder_path.replace('diverse_searchers_task_folders\\', '')
            
            folder_path = folder_path.replace('\\', '/')
            
            # Extract just the folder name
            folder_name = folder_path.split('/')[-1]
            
            # Count images in this folder
            images = get_images_from_folder(folder_name)
            
            folder_info['image_count'] = len(images)
            folder_info['actual_path'] = folder_name
            folders_info.append(folder_info)
        
        return jsonify({
            "folders": folders_info,
            "total_folders": len(folders_info)
        })
        
    except Exception as e:
        logger.error(f"Error listing folders: {str(e)}")
        return jsonify({"error": f"Failed to list folders: {str(e)}"}), 500

@app.route('/api/folders-dynamic')
def list_folders_dynamic():
    """List all available folders with their image files by scanning the filesystem."""
    try:
        # List all directories in the current directory (excluding special/hidden ones)
        base_dir = os.getcwd()
        all_dirs = [d for d in os.listdir(base_dir) if os.path.isdir(d) and not d.startswith('.')]
        folders_info = []
        for folder_name in all_dirs:
            images = get_images_from_folder(folder_name)
            if images:
                folders_info.append({
                    'folder_name': folder_name,
                    'images': images,
                    'image_count': len(images)
                })
        return jsonify({
            'folders': folders_info,
            'total_folders': len(folders_info)
        })
    except Exception as e:
        logger.error(f"Error listing folders dynamically: {str(e)}")
        return jsonify({"error": f"Failed to list folders dynamically: {str(e)}"}), 500

@app.route('/api/statistics')
def get_statistics():
    """Get statistics about annotations and folders."""
    try:
        # Get annotation statistics
        annotation_files = glob.glob(os.path.join(ANNOTATIONS_DIR, '*.json'))
        total_annotations = 0
        total_files = 0
        
        for file_path in annotation_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    total_annotations += data.get('total_annotations', 0)
                    total_files += 1
            except Exception as e:
                logger.warning(f"Error reading annotation file {file_path}: {e}")
        
        # Get folder statistics
        with open('folders_summary.json', 'r', encoding='utf-8') as f:
            folders_data = json.load(f)
        
        total_folders = len(folders_data.get('folders', []))
        total_images = sum(folder.get('image_count', 0) for folder in folders_data.get('folders', []))
        
        return jsonify({
            "annotations": {
                "total_files": total_files,
                "total_annotations": total_annotations,
                "average_per_file": total_annotations / total_files if total_files > 0 else 0
            },
            "folders": {
                "total_folders": total_folders,
                "total_images": total_images
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        return jsonify({"error": f"Failed to get statistics: {str(e)}"}), 500

@app.route('/api/submit-annotations', methods=['POST'])
def submit_annotations():
    """Submit all annotations for analysis."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        annotations = data.get('annotations', {})
        timestamp = data.get('timestamp', datetime.now().isoformat())
        total_folders = data.get('total_folders', 0)
        total_images = data.get('total_images', 0)
        user_info = data.get('user_info', {})
        
        # Create a comprehensive submission file
        submission_data = {
            "timestamp": timestamp,
            "total_folders": total_folders,
            "total_images": total_images,
            "user_info": {
                "name": user_info.get('name', 'Unknown'),
                "email": user_info.get('email', 'Unknown')
            },
            "annotations": annotations,
            "summary": {
                "folders_with_annotations": len([f for f in annotations.keys() if annotations[f]]),
                "total_annotated_images": sum(len(images) for images in annotations.values()),
                "total_boxes": sum(len(boxes) for folder_images in annotations.values() 
                                 for images in folder_images.values() 
                                 for boxes in [images])
            }
        }
        
        # Create filename with timestamp and user info
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        user_name = user_info.get('name', 'Unknown').replace(' ', '_')
        submission_file = os.path.join(ANNOTATIONS_DIR, f"submission_{user_name}_{timestamp_str}.json")
        
        # Save the complete submission
        with open(submission_file, 'w', encoding='utf-8') as f:
            json.dump(submission_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved complete annotation submission to {submission_file}")
        
        # Also save individual annotation files for each image
        for folder_name, folder_images in annotations.items():
            for image_path, boxes in folder_images.items():
                if boxes:  # Only save if there are boxes
                    # Create individual annotation file
                    safe_filename = f"{folder_name}_{image_path.replace('/', '_').replace('.', '_')}_{user_name}_{timestamp_str}.json"
                    safe_filename = "".join(c for c in safe_filename if c.isalnum() or c in ('-', '_', '.'))
                    
                    individual_file = os.path.join(ANNOTATIONS_DIR, safe_filename)
                    
                    individual_data = {
                        "folder": folder_name,
                        "image": image_path,
                        "annotations": boxes,
                        "timestamp": timestamp,
                        "user_info": {
                            "name": user_info.get('name', 'Unknown'),
                            "email": user_info.get('email', 'Unknown')
                        },
                        "total_annotations": len(boxes)
                    }
                    
                    with open(individual_file, 'w', encoding='utf-8') as f:
                        json.dump(individual_data, f, indent=2, ensure_ascii=False)
        
        return jsonify({
            "success": True,
            "message": "Annotations submitted successfully",
            "submission_file": submission_file,
            "summary": submission_data["summary"]
        })
        
    except Exception as e:
        logger.error(f"Error submitting annotations: {str(e)}")
        return jsonify({"error": f"Failed to submit annotations: {str(e)}"}), 500

@app.route('/<path:filename>')
def serve_file(filename):
    """Serve static files (images, etc.)."""
    # Handle subdirectory paths for images
    if '/' in filename:
        # Split the path to get directory and filename
        directory, file = os.path.split(filename)
        return send_from_directory(directory, file)
    else:
        # Serve files from current directory
        return send_from_directory('.', filename)

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    # Get port from environment variable (for Railway) or use default
    port = int(os.environ.get('PORT', 5000))
    
    print("Dark Pattern Annotation Server")
    print("=" * 40)
    print(f"Annotations will be saved to: {ANNOTATIONS_DIR}")
    print(f"Starting server on port {port}")
    print("Press Ctrl+C to stop the server")
    print("=" * 40)
    
    app.run(host='0.0.0.0', port=port, debug=False) 