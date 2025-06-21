import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.properties import ObjectProperty, ListProperty, StringProperty, NumericProperty
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Line
from kivy.metrics import dp
from kivy_garden.contextmenu import ContextMenu, ContextMenuItem
from loguru import logger as log


kivy.require('2.0.0')  # specify Kivy version


class BBoxData(RecycleDataViewBehavior, BoxLayout):
    ''' Add selection support to the RecycleDataViewBehavior. '''
    index = None
    right = NumericProperty(0)
    top = NumericProperty(0)
    left = NumericProperty(0)
    bottom = NumericProperty(0)
    selected = ListProperty([False])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        log.info(f"BBoxData init: {kwargs}")
        self.orientation = 'horizontal'  # Ensure it's horizontal to lay out labels
        self.padding = dp(5)
        self.spacing = dp(5)

        # Add Labels to display the bounding box coordinates
        self.right_label = Label(size_hint_x=0.25)
        self.top_label = Label(size_hint_x=0.25)
        self.left_label = Label(size_hint_x=0.25)
        self.bottom_label = Label(size_hint_x=0.25)

        self.add_widget(self.right_label)
        self.add_widget(self.top_label)
        self.add_widget(self.left_label)
        self.add_widget(self.bottom_label)

    def on_touch_down(self, touch):
        if super(BBoxData, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos):
            self.parent.select_with_touch(self.index, touch)
            return True
        return False

    def refresh_view_attrs(self, rv, index, data):
        log.info(f"Refresh view attrs called: {index}")
        self.index = index
        self.right = data['right']
        self.top = data['top']
        self.left = data['left']
        self.bottom = data['bottom']
        self.selected = data['selected']

        # Update Label texts with the new data
        self.right_label.text = str(self.right)
        self.top_label.text = str(self.top)
        self.left_label.text = str(self.left)
        self.bottom_label.text = str(self.bottom)

        # This will visually indicate selection in the table row
        if self.selected[0]:
            self.background_color = (0.7, 0.9, 1, 1)  # Light blue for selected
        else:
            self.background_color = (1, 1, 1, 1)  # White for unselected (or default)

        super(BBoxData, self).refresh_view_attrs(rv, index, data)


class RV(RecycleView):
    def __init__(self, app_ref, **kwargs):
        super(RV, self).__init__(**kwargs)
        self.data = []
        self.selected_indices = set()
        self.app_instance = app_ref

        # --- THE CRITICAL FIX: Set the layout_manager ---
        # RecycleBoxLayout is specifically designed for RecycleView to handle item recycling.
        self.add_widget(RecycleBoxLayout(
            orientation='vertical',
            spacing=dp(2),
            padding=dp(2),
            size_hint_y=None,  # Crucial for vertical scrolling
            default_size_hint=(1, None),  # Each item takes full width
            default_size=(None, dp(48))  # Use the height defined in BBoxData
        ))
        # Now set the layout_manager property to the instance you just added.
        # This will internally point to the correct layout for the RecycleView.
        self.layout_manager = self.children[0]  # Get the first child (the RecycleBoxLayout)
        self.layout_manager.bind(minimum_height=self.layout_manager.setter('height'))
        # You do NOT add this layout_manager as a child directly.
        # RecycleView uses this property to manage its views internally.

        # Attach the context menu to the RecycleView itself
        self.context_menu = ContextMenu()
        delete_item = ContextMenuItem()
        delete_item.add_widget(Label(text='Delete Selected BBox'))
        delete_item.bind(on_release=self.app_instance.delete_selected_bbox)
        self.context_menu.add_widget(delete_item)
        self.bind(on_touch_down=self._on_rv_touch_down)

    def _on_rv_touch_down(self, rv, touch):
        if touch.button == 'right' and self.collide_point(*touch.pos):
            self.context_menu.show(touch.pos)
            return True
        return False

    def select_with_touch(self, index, touch):
        if index in self.selected_indices:
            self.deselect_node(index)
        else:
            self.select_node(index)
        self.app_instance.update_bbox_selection(index, self.data[index]['selected'][0])

    def select_node(self, index):
        if index < len(self.data):  # Ensure index is valid
            self.data[index]['selected'][0] = True
            self.selected_indices.add(index)
            self.refresh_from_data()

    def deselect_node(self, index):
        if index < len(self.data): # Ensure index is valid
            self.data[index]['selected'][0] = False
            if index in self.selected_indices:
                self.selected_indices.remove(index)
            self.refresh_from_data()

    def get_selected_bbox_indices(self):
        return sorted(list(self.selected_indices))  # Return sorted indices for consistent deletion


class ImageWidget(Image):
    drawing = False
    start_pos = ListProperty([0, 0])
    end_pos = ListProperty([0, 0])
    current_rect = ObjectProperty(None, allownone=True)
    bbox_rects = ListProperty([])

    def on_touch_down(self, touch):
        app = App.get_running_app()
        if self.collide_point(*touch.pos) and app.draw_mode:
            self.drawing = True
            self.start_pos = touch.pos
            self.end_pos = touch.pos
            with self.canvas:
                Color(1, 0, 0, 1)  # Red color for drawing
                self.current_rect = Line(rectangle=(self.start_pos[0], self.start_pos[1], 1, 1), width=2)
            return True
        return super(ImageWidget, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.drawing:
            self.end_pos = touch.pos
            x1, y1 = self.start_pos
            x2, y2 = self.end_pos
            self.current_rect.rectangle = (min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
            return True
        return super(ImageWidget, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        log.info(f'touch_up: {self.drawing} {self.current_rect}')
        if self.drawing:
            self.drawing = False
            if self.current_rect:
                x1, y1, width, height = self.current_rect.rectangle
                # self.canvas.remove(self.current_rect)
                self.current_rect = None

                # Calculate actual image coordinates
                img_x, img_y = self.pos
                img_w, img_h = self.norm_image_size

                # Ensure drawn rectangle is within the image bounds for calculations
                rect_left = max(img_x, min(x1, x1 + width))
                rect_top = max(img_y, min(y1, y1 + height))  # y1 is bottom, y1+height is top
                rect_right = min(img_x + img_w, max(x1, x1 + width))
                rect_bottom = min(img_y + img_h, max(y1, y1 + height))  # y1 is bottom, y1+height is top

                # Adjust width/height if clamped
                width = rect_right - rect_left
                height = rect_bottom - rect_top  # This is tricky with Kivy's inverted Y
                log.info(f"width:{width}, height:{height}")
                # If drawing was too small or outside image area, don't add
                if width < 5 or height < 5:
                    return True

                # Convert to normalized coordinates (0 to 1) relative to image
                norm_left = (rect_left - img_x) / img_w
                norm_bottom = (rect_bottom - img_y) / img_h  # Kivy's y is bottom-up
                norm_right = (rect_right - img_x) / img_w
                norm_top = (rect_top - img_y) / img_h  # Kivy's y is bottom-up

                app = App.get_running_app()
                app.add_bbox_record(norm_right, norm_top, norm_left, norm_bottom)
                return True
        return super(ImageWidget, self).on_touch_up(touch)

    def draw_bbox_on_image(self, right, top, left, bottom, is_selected=False, bbox_id=None):
        # Convert normalized coordinates to widget coordinates
        img_x, img_y = self.pos
        img_w, img_h = self.norm_image_size

        x1 = img_x + left * img_w
        y1 = img_y + bottom * img_h  # Kivy's y is bottom-up
        width = (right - left) * img_w
        height = (top - bottom) * img_h

        with self.canvas:
            if is_selected:
                Color(0, 0, 1, 1)  # Blue for selected
            else:
                Color(0, 1, 0, 1)  # Green for unselected
            rect = Line(rectangle=(x1, y1, width, height), width=2)
            self.bbox_rects.append({'rect': rect, 'id': bbox_id, 'selected': is_selected})

    def clear_all_bboxes_on_image(self):
        for bbox_info in self.bbox_rects:
            self.canvas.remove(bbox_info['rect'])
        self.bbox_rects = []

    def update_bbox_visuals(self, rv_data):
        self.clear_all_bboxes_on_image()
        for i, data in enumerate(rv_data):
            self.draw_bbox_on_image(
                data['right'], data['top'], data['left'], data['bottom'],
                is_selected=data['selected'][0],
                bbox_id=i # Use index as a temporary ID for visual management
            )


class BBoxApp(App):
    image_source = StringProperty('05-03-yoffset-02166-xoffset-01913-h448-w640.png') # Default image path
    draw_mode = True
    bbox_counter = 0

    def build(self):
        self.title = 'Image Bounding Box Annotation'
        main_layout = BoxLayout(orientation='horizontal')

        # Left side: Image and drawing controls
        image_panel = BoxLayout(orientation='vertical', size_hint_x=0.7)
        self.image_widget = ImageWidget(source=self.image_source, allow_stretch=True, keep_ratio=True)
        image_panel.add_widget(self.image_widget)

        draw_button = Button(text='Toggle Draw Mode: OFF', size_hint_y=None, height=dp(48))
        draw_button.bind(on_release=self.toggle_draw_mode)
        image_panel.add_widget(draw_button)
        main_layout.add_widget(image_panel)

        # Right side: Table and controls
        table_panel = BoxLayout(orientation='vertical', size_hint_x=0.3)

        table_header = BoxLayout(size_hint_y=None, height=dp(48), padding=dp(5), spacing=dp(5))
        table_header.add_widget(Label(text='Right', size_hint_x=0.25))
        table_header.add_widget(Label(text='Top', size_hint_x=0.25))
        table_header.add_widget(Label(text='Left', size_hint_x=0.25))
        table_header.add_widget(Label(text='Bottom', size_hint_x=0.25))
        table_panel.add_widget(table_header)

        # Pass a reference to the current BBoxApp instance (self) to the RV
        self.rv = RV(app_ref=self)
        self.rv.viewclass = 'BBoxData'
        table_panel.add_widget(self.rv)

        # The delete button in the main UI
        delete_button = Button(text='Delete Selected BBox(es)', size_hint_y=None, height=dp(48))
        delete_button.bind(on_release=self.delete_selected_bbox)
        table_panel.add_widget(delete_button)

        main_layout.add_widget(table_panel)
        return main_layout

    def toggle_draw_mode(self, instance):
        self.draw_mode = not self.draw_mode
        instance.text = f'Draw Mode: {"ON" if self.draw_mode else "OFF"}'
        if not self.draw_mode:
            if self.image_widget.current_rect:
                self.image_widget.canvas.remove(self.image_widget.current_rect)
                self.image_widget.current_rect = None

    def add_bbox_record(self, right, top, left, bottom):
        log.info("app.add_bbox_record")
        self.bbox_counter += 1
        new_bbox = {
            'right': round(right, 4),
            'top': round(top, 4),
            'left': round(left, 4),
            'bottom': round(bottom, 4),
            'selected': [False],  # Use a list to make it mutable for RecycleView
            'bbox_id': self.bbox_counter  # Unique ID for each bbox
        }
        self.rv.data.append(new_bbox)
        log.info(f"len(rv.data)={len(self.rv.data)}")
        self.rv.refresh_from_data()
        self.image_widget.update_bbox_visuals(self.rv.data)

    def delete_selected_bbox(self, instance=None):
        selected_indices = self.rv.get_selected_bbox_indices() # Get sorted selected indices
        if not selected_indices:
            print("No bounding box selected for deletion.")
            return

        # Create new data list excluding selected items
        new_data = []
        # No need for new_bbox_map unless you had external references by original index
        # For simplicity, we just rebuild the data list.

        for i, item in enumerate(self.rv.data):
            # Check if the current item's original index is NOT in the selected_indices
            if i not in selected_indices:
                new_data.append(item)

        self.rv.data = new_data
        self.rv.selected_indices.clear()  # Clear selections as indices have changed
        self.rv.refresh_from_data()
        self.image_widget.update_bbox_visuals(self.rv.data) # Redraw all remaining bboxes

    def update_bbox_selection(self, index, is_selected):
        # This function is called by the RecycleView when a row is selected/deselected
        self.image_widget.update_bbox_visuals(self.rv.data)

if __name__ == '__main__':
    # Create a dummy image file for testing if it doesn't exist
    import os
    from PIL import Image as PILImage
    if not os.path.exists('05-03-yoffset-02166-xoffset-01913-h448-w640.png'):
        img = PILImage.new('RGB', (800, 600), color = (73, 109, 137))
        img.save('image.jpg')
        print("Created a dummy 'image.jpg' for testing.")
    BBoxApp().run()