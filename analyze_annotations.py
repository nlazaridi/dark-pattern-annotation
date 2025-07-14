#!/usr/bin/env python3
"""
Dark Pattern Annotation Analysis Script
Analyzes collected annotations and provides summaries and statistics.
"""

import os
import json
import glob
from collections import defaultdict, Counter
from datetime import datetime
import argparse

def load_annotations(annotations_dir='annotations'):
    """Load all annotation files from the annotations directory."""
    annotations = []
    
    if not os.path.exists(annotations_dir):
        print(f"Annotations directory '{annotations_dir}' not found.")
        return annotations
    
    annotation_files = glob.glob(os.path.join(annotations_dir, '*.json'))
    
    for file_path in annotation_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                data['file'] = os.path.basename(file_path)
                annotations.append(data)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
    
    return annotations

def analyze_annotations(annotations):
    """Analyze annotations and return statistics."""
    if not annotations:
        print("No annotations found.")
        return
    
    # Basic statistics
    total_files = len(annotations)
    total_annotations = sum(len(ann.get('annotations', [])) for ann in annotations)
    unique_folders = set(ann.get('folder', 'unknown') for ann in annotations)
    unique_experts = set(ann.get('expert', 'unknown') for ann in annotations)
    
    print("=== ANNOTATION STATISTICS ===")
    print(f"Total annotation files: {total_files}")
    print(f"Total annotations: {total_annotations}")
    print(f"Unique folders: {len(unique_folders)}")
    print(f"Unique experts: {len(unique_experts)}")
    print()
    
    # Expert statistics
    print("=== EXPERT STATISTICS ===")
    expert_stats = defaultdict(lambda: {'files': 0, 'annotations': 0})
    for ann in annotations:
        expert = ann.get('expert', 'unknown')
        expert_stats[expert]['files'] += 1
        expert_stats[expert]['annotations'] += len(ann.get('annotations', []))
    
    for expert, stats in expert_stats.items():
        print(f"{expert}: {stats['files']} files, {stats['annotations']} annotations")
    print()
    
    # Folder statistics
    print("=== FOLDER STATISTICS ===")
    folder_stats = defaultdict(lambda: {'files': 0, 'annotations': 0})
    for ann in annotations:
        folder = ann.get('folder', 'unknown')
        folder_stats[folder]['files'] += 1
        folder_stats[folder]['annotations'] += len(ann.get('annotations', []))
    
    for folder, stats in sorted(folder_stats.items()):
        print(f"{folder}: {stats['files']} files, {stats['annotations']} annotations")
    print()
    
    # Dark pattern descriptions analysis
    print("=== DARK PATTERN DESCRIPTIONS ===")
    descriptions = []
    for ann in annotations:
        for annotation in ann.get('annotations', []):
            desc = annotation.get('description', '').strip()
            if desc:
                descriptions.append(desc)
    
    print(f"Total dark pattern descriptions: {len(descriptions)}")
    print()
    
    # Show some example descriptions
    print("Sample descriptions:")
    for i, desc in enumerate(descriptions[:10]):
        print(f"{i+1}. {desc}")
    if len(descriptions) > 10:
        print(f"... and {len(descriptions) - 10} more")
    print()
    
    # Folder comments analysis
    print("=== FOLDER COMMENTS ===")
    folder_comments = []
    for ann in annotations:
        comment = ann.get('folder_comment', '').strip()
        if comment:
            folder_comments.append({
                'folder': ann.get('folder', 'unknown'),
                'comment': comment
            })
    
    print(f"Folders with comments: {len(folder_comments)}")
    print()
    
    for comment_data in folder_comments[:5]:
        print(f"Folder: {comment_data['folder']}")
        print(f"Comment: {comment_data['comment']}")
        print()
    
    if len(folder_comments) > 5:
        print(f"... and {len(folder_comments) - 5} more folder comments")
    print()
    
    return {
        'total_files': total_files,
        'total_annotations': total_annotations,
        'unique_folders': len(unique_folders),
        'unique_experts': len(unique_experts),
        'expert_stats': dict(expert_stats),
        'folder_stats': dict(folder_stats),
        'descriptions': descriptions,
        'folder_comments': folder_comments
    }

def export_summary(stats, output_file='annotation_summary.json'):
    """Export analysis summary to JSON file."""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        print(f"Summary exported to {output_file}")
    except Exception as e:
        print(f"Error exporting summary: {e}")

def generate_report(annotations, output_file='annotation_report.txt'):
    """Generate a detailed text report."""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("DARK PATTERN ANNOTATION REPORT\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Write statistics
            stats = analyze_annotations(annotations)
            if not stats:
                return
            
            f.write("STATISTICS\n")
            f.write("-" * 20 + "\n")
            f.write(f"Total annotation files: {stats['total_files']}\n")
            f.write(f"Total annotations: {stats['total_annotations']}\n")
            f.write(f"Unique folders: {stats['unique_folders']}\n")
            f.write(f"Unique experts: {stats['unique_experts']}\n\n")
            
            # Write expert details
            f.write("EXPERT DETAILS\n")
            f.write("-" * 20 + "\n")
            for expert, expert_stats in stats['expert_stats'].items():
                f.write(f"{expert}: {expert_stats['files']} files, {expert_stats['annotations']} annotations\n")
            f.write("\n")
            
            # Write folder details
            f.write("FOLDER DETAILS\n")
            f.write("-" * 20 + "\n")
            for folder, folder_stats in stats['folder_stats'].items():
                f.write(f"{folder}: {folder_stats['files']} files, {folder_stats['annotations']} annotations\n")
            f.write("\n")
            
            # Write all descriptions
            f.write("ALL DARK PATTERN DESCRIPTIONS\n")
            f.write("-" * 40 + "\n")
            for i, desc in enumerate(stats['descriptions'], 1):
                f.write(f"{i}. {desc}\n")
            f.write("\n")
            
            # Write folder comments
            f.write("FOLDER COMMENTS\n")
            f.write("-" * 20 + "\n")
            for comment_data in stats['folder_comments']:
                f.write(f"Folder: {comment_data['folder']}\n")
                f.write(f"Comment: {comment_data['comment']}\n\n")
        
        print(f"Detailed report generated: {output_file}")
        
    except Exception as e:
        print(f"Error generating report: {e}")

def main():
    parser = argparse.ArgumentParser(description='Analyze dark pattern annotations')
    parser.add_argument('--annotations-dir', default='annotations', 
                       help='Directory containing annotation files')
    parser.add_argument('--export-summary', action='store_true',
                       help='Export summary to JSON file')
    parser.add_argument('--generate-report', action='store_true',
                       help='Generate detailed text report')
    parser.add_argument('--output-file', default='annotation_summary.json',
                       help='Output file for summary export')
    
    args = parser.parse_args()
    
    print("Dark Pattern Annotation Analysis")
    print("=" * 40)
    print()
    
    # Load annotations
    annotations = load_annotations(args.annotations_dir)
    
    if not annotations:
        print("No annotations found. Make sure you have annotation files in the annotations directory.")
        return
    
    # Analyze annotations
    stats = analyze_annotations(annotations)
    
    # Export options
    if args.export_summary:
        export_summary(stats, args.output_file)
    
    if args.generate_report:
        generate_report(annotations)

if __name__ == '__main__':
    main() 