import json
import os
import re

import nuke
import nukescripts

FOLLOW_WRITE_VIDEO = '跟随原 Write'
FOLDER_MODE_AUTO = '自动命名'
FOLDER_MODE_CUSTOM = '自定义'

SUPPORTED_STILL_TYPES = ['exr', 'png', 'jpeg', 'tiff', 'targa', 'tga', 'bmp', 'dpx']
STILL_TYPE_SET = set(SUPPORTED_STILL_TYPES)
MOVIE_TYPES = {'mov', 'mov64', 'mp4', 'avi', 'mpeg', 'mpg'}
COMMON_MOVIE_TYPES = ['mov', 'mov64', 'mp4', 'avi']
EXTENSION_MAP = {
    'jpeg': 'jpg',
    'jpg': 'jpg',
    'tiff': 'tif',
    'tif': 'tif',
    'targa': 'tga',
}
FRAME_TOKEN_PATTERN = re.compile(r'(%\d*d|#+)')
WINDOWS_DRIVE_PATTERN = re.compile(r'^[A-Za-z]:[/\\]')
DEFAULT_SETTINGS = {
    'frame_range': '',
    'video_output': FOLLOW_WRITE_VIDEO,
    'folder_mode': FOLDER_MODE_AUTO,
    'custom_folder': '',
    'render_head_tail': False,
    'still_output': '',
    'reverse_render': False,
}


def normalize_path(path):
    return (path or '').replace('\\', '/')


def get_module_dir():
    try:
        return normalize_path(os.path.dirname(__file__))
    except Exception:
        return get_script_dir()


def get_settings_file_path():
    return normalize_path(os.path.join(get_module_dir(), 'render_assist_settings.json'))


SETTINGS_FILE_PATH = get_settings_file_path()


def load_settings():
    try:
        with open(SETTINGS_FILE_PATH, 'r') as handle:
            data = json.load(handle)
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    return {}


def save_settings(settings):
    data = DEFAULT_SETTINGS.copy()
    data.update(settings or {})
    try:
        with open(SETTINGS_FILE_PATH, 'w') as handle:
            json.dump(data, handle, indent=2, ensure_ascii=False)
    except Exception:
        pass


def merge_settings(settings):
    merged = DEFAULT_SETTINGS.copy()
    if isinstance(settings, dict):
        for key in DEFAULT_SETTINGS:
            if key in settings:
                merged[key] = settings[key]
    return merged


def get_script_path():
    try:
        script_path = nuke.root().name()
        if script_path and script_path != 'Root':
            return normalize_path(script_path)
    except Exception:
        pass
    return ''


def get_script_dir():
    script_path = get_script_path()
    if script_path:
        return normalize_path(os.path.dirname(script_path))
    return normalize_path(os.path.expanduser('~'))


def get_script_name():
    script_path = get_script_path()
    if script_path:
        return os.path.splitext(os.path.basename(script_path))[0]
    return 'untitled'


def get_default_extension(file_type):
    normalized_type = (file_type or '').lower()
    return EXTENSION_MAP.get(normalized_type, normalized_type or 'exr')


def is_movie_format(file_type):
    return (file_type or '').lower() in MOVIE_TYPES


def strip_frame_tokens(value):
    cleaned = FRAME_TOKEN_PATTERN.sub('', value or '')
    cleaned = re.sub(r'[._\-\s]+$', '', cleaned)
    return cleaned


def get_base_name_from_path(path):
    normalized = normalize_path(path)
    if not normalized:
        return ''

    stem = os.path.splitext(os.path.basename(normalized))[0]
    return strip_frame_tokens(stem)


def parse_frame_range(frame_str):
    value = (frame_str or '').strip()
    if not value:
        raise ValueError('Frame Range 不能为空。')

    if '-' in value:
        start_text, end_text = value.split('-', 1)
        start = int(start_text.strip())
        end = int(end_text.strip())
    else:
        start = int(value)
        end = start

    if end < start:
        raise ValueError('结束帧不能小于起始帧。')

    return start, end


def format_frame_range_name(start, end):
    if start == end:
        return str(start)
    return '{}-{}'.format(start, end)


def build_render_folder_name(start, end, reverse):
    folder_name = format_frame_range_name(start, end)
    if reverse:
        return 'R{}'.format(folder_name)
    return folder_name


def build_render_suffix(start, end, reverse):
    return build_render_folder_name(start, end, reverse)


def ensure_output_directory(output_path):
    directory = os.path.dirname(normalize_path(output_path))
    if directory and not os.path.exists(directory):
        os.makedirs(directory)


def is_absolute_path(path):
    normalized = normalize_path(path).strip()
    return os.path.isabs(normalized) or bool(WINDOWS_DRIVE_PATTERN.match(normalized))


def set_knob_enabled(knob, enabled):
    try:
        knob.setEnabled(enabled)
        return
    except Exception:
        pass

    try:
        if enabled:
            knob.clearFlag(nuke.DISABLED)
        else:
            knob.setFlag(nuke.DISABLED)
    except Exception:
        pass


def get_selected_write_node():
    try:
        node = nuke.selectedNode()
        if node.Class() == 'Write':
            return node
    except Exception:
        pass
    return None


def get_current_write_path(node):
    for getter in ('value', 'evaluate'):
        try:
            value = getattr(node['file'], getter)()
            if value:
                return normalize_path(value)
        except Exception:
            pass
    return ''


def get_current_file_type(node):
    try:
        value = node['file_type'].value()
        if value:
            return value
    except Exception:
        pass
    return ''


def get_available_write_types(node):
    try:
        values = node['file_type'].values()
        if values:
            return [value for value in values if value]
    except Exception:
        pass
    return []


def get_available_still_types(node):
    available = []
    for value in get_available_write_types(node):
        normalized = value.lower()
        if normalized in STILL_TYPE_SET and value not in available:
            available.append(value)

    if not available:
        return ['jpeg', 'png', 'exr', 'dpx']

    return available


def get_available_video_types(node):
    available = []
    for value in get_available_write_types(node):
        normalized = value.lower()
        if normalized in MOVIE_TYPES and value not in available:
            available.append(value)

    current_type = get_current_file_type(node)
    if current_type and current_type.lower() in MOVIE_TYPES and current_type not in available:
        available.insert(0, current_type)

    if not available:
        available.extend(COMMON_MOVIE_TYPES)

    return [FOLLOW_WRITE_VIDEO] + available


def ensure_value_in_list(values, target_value, insert_after_first=False):
    if target_value and target_value not in values:
        if insert_after_first and values:
            values.insert(1, target_value)
        else:
            values.insert(0, target_value)


def get_default_still_type(node):
    current_type = get_current_file_type(node)
    if current_type and current_type.lower() in STILL_TYPE_SET:
        return current_type

    return get_available_still_types(node)[0]


def get_output_base_dir(node):
    write_path = get_current_write_path(node)
    if write_path:
        return normalize_path(os.path.dirname(write_path))

    fallback_dir = os.path.join(get_script_dir(), 'RenderAssistant')
    return normalize_path(fallback_dir)


def get_output_base_name(node):
    write_path = get_current_write_path(node)
    if write_path:
        base_name = get_base_name_from_path(write_path)
        if base_name:
            return base_name

    try:
        return node.name()
    except Exception:
        return get_script_name()


def resolve_video_output_type(node, selected_video_type):
    if selected_video_type and selected_video_type != FOLLOW_WRITE_VIDEO:
        return selected_video_type

    current_type = get_current_file_type(node)
    if current_type:
        return current_type

    return 'mov'


def resolve_output_folder(node, start, end, reverse, folder_mode, custom_folder):
    base_dir = get_output_base_dir(node)
    if folder_mode == FOLDER_MODE_CUSTOM:
        custom_value = normalize_path(custom_folder).strip()
        if custom_value:
            if is_absolute_path(custom_value):
                return custom_value
            return normalize_path(os.path.join(base_dir, custom_value))

    return normalize_path(os.path.join(base_dir, build_render_folder_name(start, end, reverse)))


def build_main_output_path(node, output_folder, video_output_type, start, end, reverse):
    base_name = get_output_base_name(node)
    render_suffix = build_render_suffix(start, end, reverse)
    render_name = '{}_{}'.format(base_name, render_suffix)
    extension = get_default_extension(video_output_type)
    if is_movie_format(video_output_type):
        file_name = '{}.{}'.format(render_name, extension)
    else:
        file_name = '{}.%04d.{}'.format(render_name, extension)
    return normalize_path(os.path.join(output_folder, file_name))


def build_extra_still_path(main_output_path, suffix, output_type):
    target_dir = normalize_path(os.path.dirname(main_output_path))
    base_name = get_base_name_from_path(main_output_path)
    extension = get_default_extension(output_type)
    file_name = '{}_{}.{}'.format(base_name, suffix, extension)
    return normalize_path(os.path.join(target_dir, file_name))


def build_output_folder_preview(node, frame_range_text, reverse, folder_mode, custom_folder):
    try:
        start, end = parse_frame_range(frame_range_text)
    except ValueError:
        return '请输入合法帧范围'

    return resolve_output_folder(node, start, end, reverse, folder_mode, custom_folder)


def apply_output_settings(write_node, output_type):
    normalized_type = (output_type or '').lower()
    if normalized_type in ('jpeg', 'jpg') and '_jpeg_quality' in write_node.knobs():
        try:
            write_node['_jpeg_quality'].setValue(0.85)
        except Exception:
            pass


def collect_panel_settings(panel):
    return {
        'frame_range': panel.frame_range.value(),
        'video_output': panel.video_output.value(),
        'folder_mode': panel.folder_mode.value(),
        'custom_folder': panel.custom_folder.value(),
        'render_head_tail': bool(panel.render_head_tail.value()),
        'still_output': panel.still_output.value(),
        'reverse_render': bool(panel.reverse_render.value()),
    }


class RenderAssistPanel(nukescripts.PythonPanel):
    def __init__(self, node):
        super(RenderAssistPanel, self).__init__('Render Assistant')
        self.target_node = node
        self.saved_settings = merge_settings(load_settings())
        self.available_video_types = get_available_video_types(node)
        self.available_still_types = get_available_still_types(node)

        ensure_value_in_list(self.available_video_types, self.saved_settings['video_output'], insert_after_first=True)
        ensure_value_in_list(self.available_still_types, self.saved_settings['still_output'])

        try:
            start = int(nuke.root()['first_frame'].value())
            end = int(nuke.root()['last_frame'].value())
        except Exception:
            start = 1
            end = 100

        default_frame_range = self.saved_settings['frame_range'] or '{}-{}'.format(start, end)
        default_video_output = self.saved_settings['video_output'] or FOLLOW_WRITE_VIDEO
        default_folder_mode = self.saved_settings['folder_mode'] or FOLDER_MODE_AUTO
        default_custom_folder = self.saved_settings['custom_folder'] or ''
        default_still_output = self.saved_settings['still_output'] or get_default_still_type(node)
        default_render_head_tail = bool(self.saved_settings['render_head_tail'])
        default_reverse_render = bool(self.saved_settings['reverse_render'])

        self.frame_range = nuke.String_Knob('frame_range', 'Frame Range', default_frame_range)
        self.frame_range.setTooltip('输入要渲染的帧范围，例如 10-15。')
        self.addKnob(self.frame_range)

        self.video_output = nuke.Enumeration_Knob('video_output', 'Video Output', self.available_video_types)
        self.video_output.setValue(default_video_output)
        self.video_output.setTooltip('主渲染输出格式。默认跟随原始 Write，也可以手动指定。')
        self.addKnob(self.video_output)

        self.folder_mode = nuke.Enumeration_Knob('folder_mode', 'Folder Mode', [FOLDER_MODE_AUTO, FOLDER_MODE_CUSTOM])
        self.folder_mode.setValue(default_folder_mode)
        self.folder_mode.setTooltip('自动命名会按帧范围生成目录；自定义可手动输入文件夹名或完整路径。')
        self.addKnob(self.folder_mode)

        self.custom_folder = nuke.String_Knob('custom_folder', 'Custom Folder', default_custom_folder)
        self.custom_folder.setTooltip('可输入文件夹名，或输入完整绝对路径。')
        self.addKnob(self.custom_folder)

        preview_value = build_output_folder_preview(node, default_frame_range, default_reverse_render, default_folder_mode, default_custom_folder)
        self.output_folder = nuke.Text_Knob('output_folder', 'Output Folder', preview_value)
        self.addKnob(self.output_folder)

        self.addKnob(nuke.Text_Knob('divider', ''))

        self.render_head_tail = nuke.Boolean_Knob('render_head_tail', 'Export Head/Tail Stills')
        self.render_head_tail.setTooltip('勾选后，完整渲染结束后会额外导出首帧和尾帧单帧图片。')
        self.render_head_tail.setFlag(nuke.STARTLINE)
        self.render_head_tail.setValue(default_render_head_tail)
        self.addKnob(self.render_head_tail)

        self.still_output = nuke.Enumeration_Knob('still_output', 'Still Output', self.available_still_types)
        self.still_output.setValue(default_still_output)
        self.still_output.setTooltip('只对首尾单帧图片导出格式生效。')
        self.addKnob(self.still_output)

        self.reverse_render = nuke.Boolean_Knob('reverse_render', 'Reverse Render')
        self.reverse_render.setTooltip('勾选后，自动命名目录会使用 `R10-15` 这样的规则，文件名也会带对应后缀。')
        self.reverse_render.setFlag(nuke.STARTLINE)
        self.reverse_render.setValue(default_reverse_render)
        self.addKnob(self.reverse_render)

        self.refresh_ui_state()

    def refresh_ui_state(self):
        set_knob_enabled(self.still_output, self.render_head_tail.value())
        set_knob_enabled(self.custom_folder, self.folder_mode.value() == FOLDER_MODE_CUSTOM)
        self.output_folder.setValue(
            build_output_folder_preview(
                self.target_node,
                self.frame_range.value(),
                self.reverse_render.value(),
                self.folder_mode.value(),
                self.custom_folder.value(),
            )
        )

    def knobChanged(self, knob):
        if knob.name() in ('frame_range', 'reverse_render', 'folder_mode', 'custom_folder', 'render_head_tail'):
            self.refresh_ui_state()


def process_render(node, frame_str, head_tail, reverse, still_output_type, video_output_selection, folder_mode, custom_folder):
    try:
        start, end = parse_frame_range(frame_str)
    except ValueError as error:
        nuke.message(str(error))
        return False

    original_input = node.input(0)
    if original_input is None:
        nuke.message('当前 Write 节点没有输入，无法执行渲染。')
        return False

    video_output_type = resolve_video_output_type(node, video_output_selection)
    output_folder = resolve_output_folder(node, start, end, reverse, folder_mode, custom_folder)
    main_output_path = build_main_output_path(node, output_folder, video_output_type, start, end, reverse)

    undo = nuke.Undo()
    undo.begin('Render Assistant')

    timewarp_node = None
    main_write = None
    still_write = None
    extra_still_paths = []

    try:
        ensure_output_directory(main_output_path)

        render_input = original_input
        if reverse:
            timewarp_node = nuke.nodes.TimeWarp(name='RenderAssist_Reverse_TMP')
            timewarp_node.setInput(0, original_input)

            lookup = timewarp_node['lookup']
            lookup.setAnimated()
            lookup.setValueAt(float(end), start)
            lookup.setValueAt(float(start), end)
            render_input = timewarp_node

        main_write = nuke.nodes.Write(name='RenderAssist_Main_TMP')
        main_write.setInput(0, render_input)
        main_write['file_type'].setValue(video_output_type)
        main_write['file'].setValue(main_output_path)
        apply_output_settings(main_write, video_output_type)
        nuke.execute(main_write, start, end)

        if head_tail:
            still_write = nuke.nodes.Write(name='RenderAssist_Still_TMP')
            still_write.setInput(0, render_input)
            still_write['file_type'].setValue(still_output_type)
            apply_output_settings(still_write, still_output_type)

            head_path = build_extra_still_path(main_output_path, 'head', still_output_type)
            tail_path = build_extra_still_path(main_output_path, 'tail', still_output_type)

            still_write['file'].setValue(head_path)
            nuke.execute(still_write, start, start)
            extra_still_paths.append(head_path)

            still_write['file'].setValue(tail_path)
            nuke.execute(still_write, end, end)
            extra_still_paths.append(tail_path)

        message = 'Render Completed Successfully!\n\nSource Write:\n{}\n\nVideo Output:\n{}\n\nOutput Folder:\n{}\n\nMain Output:\n{}'.format(
            node.name(),
            video_output_type,
            output_folder,
            main_output_path,
        )
        if extra_still_paths:
            message += '\n\nHead/Tail Stills ({})\n- {}'.format(
                still_output_type,
                '\n- '.join(extra_still_paths),
            )
        nuke.message(message)
        return True

    except Exception as error:
        nuke.message('Render Failed:\n{}'.format(error))
        return False

    finally:
        if still_write is not None:
            try:
                nuke.delete(still_write)
            except Exception:
                pass

        if main_write is not None:
            try:
                nuke.delete(main_write)
            except Exception:
                pass

        if timewarp_node is not None:
            try:
                nuke.delete(timewarp_node)
            except Exception:
                pass

        undo.end()


def show_dialog():
    node = get_selected_write_node()
    if not node:
        nuke.message('Please select a Write node first.')
        return

    panel = RenderAssistPanel(node)
    if panel.showModalDialog():
        settings = collect_panel_settings(panel)
        try:
            parse_frame_range(settings['frame_range'])
        except ValueError as error:
            nuke.message(str(error))
            return

        save_settings(settings)
        process_render(
            node=node,
            frame_str=settings['frame_range'],
            head_tail=settings['render_head_tail'],
            reverse=settings['reverse_render'],
            still_output_type=settings['still_output'],
            video_output_selection=settings['video_output'],
            folder_mode=settings['folder_mode'],
            custom_folder=settings['custom_folder'],
        )
