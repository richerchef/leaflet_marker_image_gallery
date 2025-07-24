import cv2
import csv
import numpy as np

IMAGE_PATH = 'diagram.png'
CSV_PATH = 'tagged_labels.csv'

WINDOW_NAME = "Tag Editor"

# Constants
POINT_RADIUS = 7
CLICK_TOLERANCE = 10  # pixels for "near" a point

# Load existing tags
tags = []  # List of dicts: {'x': int, 'y': int, 'label': str}

def load_tags(csv_path):
    loaded = []
    try:
        with open(csv_path, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                loaded.append({'x': int(row['x']), 'y': int(row['y']), 'label': row['label']})
        print(f"Loaded {len(loaded)} tags from {csv_path}")
    except FileNotFoundError:
        print(f"No existing CSV found at {csv_path}, starting fresh.")
    return loaded

def save_tags(csv_path, tags):
    with open(csv_path, 'w', newline='') as f:
        fieldnames = ['x', 'y', 'label']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for tag in tags:
            writer.writerow(tag)
    print(f"Saved {len(tags)} tags to {csv_path}")

# Helper to find closest tag within tolerance (in image coordinates)
def find_tag_near(x, y, tags):
    for i, tag in enumerate(tags):
        if abs(tag['x'] - x) <= CLICK_TOLERANCE and abs(tag['y'] - y) <= CLICK_TOLERANCE:
            return i
    return None

# Draw tags on the image with scaling/offset
def draw_tags(img, tags, scale, offset_x, offset_y):
    for tag in tags:
        px = int(tag['x'] * scale + offset_x)
        py = int(tag['y'] * scale + offset_y)
        cv2.circle(img, (px, py), POINT_RADIUS, (0, 255, 0), -1)
        cv2.putText(img, tag['label'], (px + 10, py - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

def main():
    global tags

    img_original = cv2.imread(IMAGE_PATH)
    if img_original is None:
        print(f"Could not load image {IMAGE_PATH}")
        return

    tags = load_tags(CSV_PATH)

    scale = 1.0
    offset_x, offset_y = 0, 0
    dragging = False
    drag_start = (0, 0)
    offset_start = (0, 0)

    current_edit_index = None  # index of tag being edited or deleted

    def on_mouse(event, x, y, flags, param):
        nonlocal scale, offset_x, offset_y, dragging, drag_start, offset_start, current_edit_index

        # Convert screen coords back to image coords
        ix = int((x - offset_x) / scale)
        iy = int((y - offset_y) / scale)

        if event == cv2.EVENT_LBUTTONDOWN:
            idx = find_tag_near(ix, iy, tags)
            if idx is not None:
                # Edit existing tag
                print(f"Editing tag at ({tags[idx]['x']}, {tags[idx]['y']}) labeled '{tags[idx]['label']}'")
                new_label = input("Enter new label (empty to cancel): ").strip()
                if new_label != "":
                    tags[idx]['label'] = new_label
                    print("Label updated.")
                else:
                    print("Edit cancelled.")
            else:
                # Add new tag
                label = input(f"Enter label for point ({ix},{iy}): ").strip()
                if label != "":
                    tags.append({'x': ix, 'y': iy, 'label': label})
                    print("Tag added.")
                else:
                    print("Tag cancelled.")

        elif event == cv2.EVENT_RBUTTONDOWN:
            idx = find_tag_near(ix, iy, tags)
            if idx is not None:
                print(f"Deleting tag at ({tags[idx]['x']}, {tags[idx]['y']}) labeled '{tags[idx]['label']}'")
                confirm = input("Confirm delete? (y/n): ").strip().lower()
                if confirm == 'y':
                    tags.pop(idx)
                    print("Tag deleted.")
                else:
                    print("Delete cancelled.")

        elif event == cv2.EVENT_MOUSEWHEEL:
            # Zoom in/out
            if flags > 0:
                scale *= 1.1
            else:
                scale /= 1.1

            # Limit scale
            scale = max(0.1, min(10, scale))

            # Optional: Adjust offset so zoom is centered on cursor
            offset_x = x - (ix * scale)
            offset_y = y - (iy * scale)

        elif event == cv2.EVENT_LBUTTONDOWN and not dragging:
            # Start drag
            dragging = True
            drag_start = (x, y)
            offset_start = (offset_x, offset_y)

        elif event == cv2.EVENT_MOUSEMOVE and dragging:
            # Update pan offset
            dx = x - drag_start[0]
            dy = y - drag_start[1]
            offset_x = offset_start[0] + dx
            offset_y = offset_start[1] + dy

        elif event == cv2.EVENT_LBUTTONUP:
            dragging = False

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(WINDOW_NAME, on_mouse)

    print("Instructions:")
    print("- Left click: add new tag or edit existing tag if close")
    print("- Right click near tag: delete tag")
    print("- Mouse wheel: zoom in/out")
    print("- Drag (hold left button on blank area): pan")
    print("- Press 'q' to quit and save")

    while True:
        # Prepare image to show with zoom and pan
        h, w = img_original.shape[:2]
        resized = cv2.resize(img_original, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_LINEAR)
        display = resized.copy()

        # Draw tags
        draw_tags(display, tags, scale, offset_x, offset_y)

        cv2.imshow(WINDOW_NAME, display)
        key = cv2.waitKey(20) & 0xFF
        if key == ord('q'):
            break

    cv2.destroyAllWindows()

    # Save on exit
    save_tags(CSV_PATH, tags)

if __name__ == "__main__":
    main()
