#!/usr/bin/env python3
"""
Dark Pattern Annotation Server
Serves images and handles annotation saving for the UI Dark Pattern Experts interface.
"""

import os
import json
import glob
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
    
    # Sort images by filename for consistent ordering
    images.sort()
    return images

@app.route('/')
def index():
    """Serve the main annotation interface."""
    return send_from_directory('.', 'annotation_interface.html')

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
    
    logger.info(f"Looking for images in folder: {folder}")
    
    images = get_images_from_folder(folder)
    
    logger.info(f"Found {len(images)} images in {folder}")
    
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
            
            # Count images in this folder
            images = get_images_from_folder(folder_path)
            
            folder_info['image_count'] = len(images)
            folder_info['actual_path'] = folder_path
            folders_info.append(folder_info)
        
        return jsonify({
            "folders": folders_info,
            "total_folders": len(folders_info)
        })
        
    except Exception as e:
        logger.error(f"Error listing folders: {str(e)}")
        return jsonify({"error": f"Failed to list folders: {str(e)}"}), 500

@app.route('/api/statistics')
def get_statistics():
    """Get annotation statistics."""
    try:
        # Count annotation files
        annotation_files = glob.glob(os.path.join(ANNOTATIONS_DIR, '*.json'))
        
        # Count total annotations across all files
        total_annotations = 0
        experts = set()
        folders = set()
        
        for file_path in annotation_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    total_annotations += len(data.get('annotations', []))
                    experts.add(data.get('expert', 'unknown'))
                    folders.add(data.get('folder', 'unknown'))
            except Exception as e:
                logger.warning(f"Error reading annotation file {file_path}: {e}")
        
        return jsonify({
            "total_annotation_files": len(annotation_files),
            "total_annotations": total_annotations,
            "unique_experts": len(experts),
            "unique_folders": len(folders),
            "experts": list(experts),
            "folders": list(folders)
        })
        
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        return jsonify({"error": f"Failed to get statistics: {str(e)}"}), 500

@app.route('/<path:filename>')
def serve_file(filename):
    """Serve static files (images, etc.)."""
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