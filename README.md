# Dark Pattern Annotation Interface

A comprehensive web-based interface for UI Dark Pattern Experts to annotate screenshots with bounding boxes and descriptions of dark patterns.

## Features

- **Systematic Navigation**: Browse through folders and images one by one
- **Bounding Box Annotation**: Draw bounding boxes around dark patterns on images
- **Dark Pattern Descriptions**: Add detailed descriptions of identified dark patterns
- **Folder Comments**: Provide general comments about dark patterns in each folder
- **Progress Tracking**: Visual progress bar showing completion status
- **Annotation Management**: Add, edit, and remove annotations
- **Auto-save**: Annotations are saved to JSON files for later analysis

## Setup Instructions

### Prerequisites

- Python 3.7 or higher
- All image files organized in folders as per your project structure

### Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Ensure your project structure:**
   - `folders_summary.json` - Contains folder information
   - Image folders with screenshots
   - The annotation interface files

### Running the Server

1. **Start the annotation server:**
   ```bash
   python annotation_server.py
   ```

2. **Access the interface:**
   - Open your web browser
   - Navigate to `http://localhost:5000`
   - The interface will load automatically

## Usage Guide

### Getting Started

1. **Load the Interface**: The interface will automatically load the first folder and its images
2. **View Images**: Use the navigation buttons to move between images and folders
3. **Draw Bounding Boxes**: Click and drag on images to create bounding boxes around dark patterns
4. **Add Descriptions**: Type descriptions of dark patterns and click "Add Annotation"
5. **Save Work**: Click "Save Annotations" to save your work

### Annotation Process

1. **Navigate to an Image**: Use the Previous/Next buttons to move between images
2. **Identify Dark Patterns**: Look for UI elements that could be considered dark patterns
3. **Draw Bounding Boxes**: Click and drag to create boxes around suspicious elements
4. **Describe the Pattern**: Type a clear description of what makes this a dark pattern
5. **Add Multiple Annotations**: You can add multiple annotations per image
6. **Add Folder Comments**: Provide general observations about the folder's dark patterns
7. **Save and Continue**: Save your work and move to the next image

### Interface Controls

- **Navigation**: Use Previous/Next buttons to move between images and folders
- **Bounding Boxes**: Click and drag to create, click to select, use "Delete Selected Box" to remove
- **Annotations**: Type descriptions and click "Add Annotation" or press Enter
- **Clear All**: Use "Clear All Annotations" to start over on an image
- **Save**: Click "Save Annotations" to save your work

### Keyboard Shortcuts

- **Enter**: Add annotation (when typing in the description field)
- **Mouse Drag**: Create bounding boxes
- **Click**: Select bounding boxes

## File Structure

```
project/
├── annotation_interface.html    # Main interface file
├── annotation_server.py         # Flask server
├── requirements.txt             # Python dependencies
├── folders_summary.json         # Folder information
├── annotations/                 # Saved annotation files
├── folder1/                     # Image folders
│   ├── image1.png
│   └── image2.png
└── folder2/
    ├── image1.png
    └── image2.png
```

## Output Format

Annotations are saved as JSON files in the `annotations/` directory with the following structure:

```json
{
  "folder": "folder_path",
  "image": "image_path",
  "annotations": [
    {
      "description": "Dark pattern description",
      "coordinates": [
        {
          "x": 100,
          "y": 200,
          "width": 150,
          "height": 50
        }
      ],
      "timestamp": "2024-01-01T12:00:00.000Z"
    }
  ],
  "folder_comment": "General comments about this folder",
  "expert": "UI_Dark_Pattern_Expert",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "total_annotations": 1
}
```

## API Endpoints

The server provides several API endpoints:

- `GET /` - Main interface
- `GET /folders_summary.json` - Folder information
- `GET /api/images?folder=<path>` - Get images from a folder
- `POST /api/save-annotations` - Save annotations
- `GET /api/annotations` - List all saved annotations
- `GET /api/folders` - List folders with image counts
- `GET /api/statistics` - Get annotation statistics

## Troubleshooting

### Common Issues

1. **Images not loading**: Check that image paths in `folders_summary.json` are correct
2. **Server not starting**: Ensure all dependencies are installed with `pip install -r requirements.txt`
3. **Annotations not saving**: Check that the `annotations/` directory is writable
4. **CORS errors**: The server includes CORS headers, but ensure you're accessing via `http://localhost:5000`

### Debug Mode

The server runs in debug mode by default. Check the console output for detailed error messages and logging information.

## Expert Guidelines

When annotating dark patterns, consider:

1. **Clarity**: Be specific about what makes an element a dark pattern
2. **Context**: Consider the user's goal and how the pattern might mislead them
3. **Severity**: Note the potential impact of the dark pattern
4. **Consistency**: Use consistent terminology across annotations
5. **Completeness**: Ensure all suspicious elements are annotated

## Support

For technical issues or questions about the annotation interface, check the console output for error messages and ensure all files are in the correct locations. 