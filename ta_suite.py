# -*- coding: utf-8 -*-
"""TA Analysis Suite Lite QGIS plugin."""
import csv, datetime, os, re, webbrowser
import matplotlib.pyplot as plt
import numpy as np
try:
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
except ImportError:
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.ticker import FuncFormatter
from qgis.PyQt.QtCore import Qt, QCoreApplication, QDate, QSettings, QSize
from qgis.PyQt.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame,
    QPushButton, QMessageBox, QLineEdit, QComboBox, QFileDialog, QSizePolicy, QApplication, QDialog,
    QToolButton,
    QTabWidget, QSpinBox, QFormLayout, QColorDialog, QFontComboBox, QDoubleSpinBox, QScrollArea, QDateEdit,
    QStackedWidget, QInputDialog, QSplitter, QMenu)
from qgis.PyQt.QtGui import QColor, QIcon, QFont, QPalette
try:
    from qgis.PyQt.QtGui import QAction
except ImportError:
    from qgis.PyQt.QtWidgets import QAction

def _flatten_qt_enums(*classes):
    import enum
    for cls in classes:
        for name in dir(cls):
            if name.startswith('_'): continue
            try: attr=getattr(cls,name)
            except Exception: continue
            if isinstance(attr,type) and issubclass(attr,enum.Enum):
                for member in attr:
                    if not hasattr(cls,member.name):
                        try: setattr(cls,member.name,member)
                        except Exception: pass
_flatten_qt_enums(Qt,QSizePolicy,QFrame,QDialog,QLineEdit,QMessageBox,QComboBox,QFileDialog,QColorDialog,QFontComboBox,QMainWindow,QTabWidget,QScrollArea,QStackedWidget)

APP_NAME='TA Analysis Suite Lite'; VERSION='1.0.0'; AUTHOR='Jujun Junaedi'; EMAIL='dev.qgis.plugin@gmail.com'
WHATSAPP_URL='https://wa.me/6281510027058'; EMAIL_URL='https://outlook.live.com/mail/0/deeplink/compose?to=jujun.junaedi%40outlook.com'
GUMROAD_URL='https://jujunet.gumroad.com/l/TA_Analysis_Suite_Pro'
LYNK_ID_URL='https://lynk.id/kangjun/83jpjwm7lyk4'
TA_TEMPLATE_URL='https://drive.google.com/drive/folders/1DFhfw20mtoNP8x1slHTApGS6gNpahrFy?usp=sharing'
PRO_VIDEO_URL='https://youtu.be/fEZy4M0M9p8?si=HfbhnMpZ_jqV8YwS'
DEFAULT_UI_THEME={'ui_font':'Arial','ui_font_size':10,'ui_text_color':'#dfe3e8','ui_bg':'#26272b','ui_toolbar_bg':'#3a3b3f','ui_button_bg':'#3d3e42','ui_button_text':'#dfe3e8','ui_button_active':'#3a6ea8','ui_header_bg':'#2f5f8f','chart_font':'Arial','chart_font_size':9,'chart_font_color':'#f5f5f0','chart_bar_color':'#00BFFF','chart_cdf_color':'#FF8C00','chart_fill_color':'#1E1E1E','chart_grid_color':'#555555'}
BAND_OPTIONS=['900','1800','2100','2300']
VENDOR_CONFIG={
'ZTE':{'bins':['0-78m','78-234m','234-390m','390-546m','546-703m','703-859m','859-1015m','1015-1562','1562-2109m','2109-2656m','2656-3125m','3125-3906m','3906-6328m','6328-10078m','TA >10km'],'labels':['0-78m','78-234m','234-390m','390-546m','546-703m','703-859m','859-1015m','1015-1562','1562-2109m','2109-2656m','2656-3125m','3125-3906m','3906-6328m','6328-10078m','>10km'],'threshold_col_kw':['TA','85'],'implemented':True},
'ERICSSON':{'bins':['0.0 - 0.078','0.078 - 0.156','0.156 - 0.234','0.234 - 0.312','0.312 - 0.391','0.391 - 0.469','0.469 - 0.547','0.547 - 0.625','0.625 - 0.703','0.703 - 0.781','0.781 - 0.859','0.859 - 0.937','0.937 - 1.016','1.016 - 1.094','1.094 - 1.172','1.172 - 1.25','1.25 - 1.328','1.328 - 1.406','1.406 - 1.484','1.484 - 1.562','1.562 - 1.641','1.641 - 1.719','1.719 - 1.797','1.797 - 1.875','1.875 - 1.953','1.953 - 2.031','2.031 - 2.109','2.109 - 2.187','2.187 - 2.265','2.265 - 2.344','2.344 - 2.422','2.422 - 2.5','2.5 - 2.578','2.578 - 2.656','2.656 - 2.734','2.734 - 2.812','2.812 - 2.89','2.89 - 2.969','2.969 - 3.047','3.047 - 4.062','4.062 - 5.0','5.0 - 6.015','6.015 - 7.031','7.031 - 8.046','8.046 - 9.062','9.062 - 10.077','>10.000'],'labels':['0-78','78-156','156-234','234-312','312-391','391-469','469-547','547-625','625-703','703-781','781-859','859-937','937-1k','1k-1.1k','1.1k-1.2k','1.2k-1.25k','1.25k-1.3k','1.3k-1.4k','1.4k-1.5k','1.5k-1.6k','1.6k-1.64k','1.64k-1.7k','1.7k-1.8k','1.8k-1.9k','1.9k-2k','2k-2.03k','2.03k-2.1k','2.1k-2.2k','2.2k-2.3k','2.3k-2.34k','2.34k-2.4k','2.4k-2.5k','2.5k-2.6k','2.6k-2.66k','2.66k-2.7k','2.7k-2.8k','2.8k-2.9k','2.9k-3k','3k-3.05k','3.05k-4k','4k-5k','5k-6k','6k-7k','7k-8k','8k-9k','9k-10k','>10km'],'threshold_col_kw':['TA','90'],'implemented':True}}

_BEGIN_TIME_FORMATS = [
    "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d",
    "%Y/%m/%d %H:%M:%S", "%Y/%m/%d %H:%M", "%Y/%m/%d",
    "%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M", "%d/%m/%Y",
    "%m/%d/%Y %H:%M:%S", "%m/%d/%Y %H:%M", "%m/%d/%Y",
    "%d-%m-%Y %H:%M:%S", "%d-%m-%Y",
    "%m/%d/%Y %I:%M:%S %p", "%d/%m/%Y %I:%M:%S %p",
]

def _bg_luminance(h):
    try:
        c=QColor(h); return .2126*c.redF()+.7152*c.greenF()+.0722*c.blueF()
    except Exception:return 0.0
def _is_light_bg(h): return _bg_luminance(h)>.58


def comma_format(x, pos): return '{:,}'.format(int(x))


def safe_float(val):
    try: return float(str(val).strip().replace(',', '.')) if val else 0.0
    except Exception: return 0.0


def parse_begin_time_to_date(value, fmt_hint=None):
    """Parse a TA timestamp into a date without forcing one global format."""
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None

    # ISO timestamps, including the common ``T`` and timezone variants.
    if len(s) >= 10 and s[0:4].isdigit() and s[4] in ('-', '/') and s[7] in ('-', '/'):
        try:
            iso = s.replace('Z', '+00:00')
            return datetime.datetime.fromisoformat(iso).date()
        except (ValueError, TypeError):
            pass

    date_part = s.split()[0]

    # Month-name exports such as 01-Aug-2026 / 22-Sep-2026.
    for fmt in (
        '%d-%b-%Y', '%d-%B-%Y', '%b-%d-%Y', '%B-%d-%Y',
        '%d-%b-%Y %H:%M:%S', '%d-%B-%Y %H:%M:%S',
        '%d-%b-%Y %H:%M', '%d-%B-%Y %H:%M',
        '%b-%d-%Y %H:%M:%S', '%B-%d-%Y %H:%M:%S',
        '%b-%d-%Y %H:%M', '%B-%d-%Y %H:%M',
    ):
        try:
            return datetime.datetime.strptime(s, fmt).date()
        except ValueError:
            continue

    # Numeric slash dates: resolve unambiguous values from their own shape.
    if '/' in date_part:
        parts = date_part.split('/')
        if len(parts) == 3 and all(p.isdigit() for p in parts):
            a, b, y = map(int, parts)
            fmt = None
            if a > 12 and b <= 12:
                fmt = '%d/%m/%Y'
            elif b > 12 and a <= 12:
                fmt = '%m/%d/%Y'
            elif a <= 12 and b <= 12:
                fmt = '%m/%d/%Y'
            if fmt:
                tail = ' '.join(s.split()[1:])
                for tfmt in ('%H:%M:%S', '%H:%M', '%I:%M:%S %p') if tail else (None,):
                    try:
                        return datetime.datetime.strptime(
                            date_part if not tail else f'{date_part} {tail}',
                            fmt if not tail else f'{fmt} {tfmt}'
                        ).date()
                    except (ValueError, TypeError):
                        continue

    # Numeric dash dates: resolve from the actual value before fmt_hint.
    if '-' in date_part:
        parts = date_part.split('-')
        if len(parts) == 3 and all(p.isdigit() for p in parts):
            a, b, y = map(int, parts)
            if len(parts[0]) == 4:
                pass
            else:
                fmts = []
                if a > 12 and b <= 12:
                    fmts.append('%d-%m-%Y')
                elif b > 12 and a <= 12:
                    fmts.append('%m-%d-%Y')
                else:
                    fmts.extend(('%d-%m-%Y', '%m-%d-%Y'))
                tail = ' '.join(s.split()[1:])
                for fmt in fmts:
                    candidates = ((fmt,),) if not tail else ((f'{fmt} %H:%M:%S',), (f'{fmt} %H:%M',))
                    for (full_fmt,) in candidates:
                        try:
                            return datetime.datetime.strptime(s, full_fmt).date()
                        except ValueError:
                            continue

    # Compatibility fallback for unusual but previously supported formats.
    if fmt_hint:
        try:
            return datetime.datetime.strptime(s, fmt_hint).date()
        except ValueError:
            pass
    for fmt in _BEGIN_TIME_FORMATS + (
        '%d-%b-%Y', '%d-%B-%Y', '%b-%d-%Y', '%B-%d-%Y',
        '%d-%b-%Y %H:%M:%S', '%d-%B-%Y %H:%M:%S',
    ):
        try:
            return datetime.datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def detect_begin_time_format(sample_values):
    """Detect a representative timestamp format for compatibility."""
    values = [str(v).strip() for v in sample_values if v is not None and str(v).strip()]
    if not values:
        return None
    candidates = (
        '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%d',
        '%Y/%m/%d %H:%M:%S', '%Y/%m/%d %H:%M', '%Y/%m/%d',
        '%d-%b-%Y %H:%M:%S', '%d-%b-%Y %H:%M', '%d-%b-%Y',
        '%d-%B-%Y %H:%M:%S', '%d-%B-%Y %H:%M', '%d-%B-%Y',
        '%d/%m/%Y %H:%M:%S', '%d/%m/%Y %H:%M', '%d/%m/%Y',
        '%m/%d/%Y %H:%M:%S', '%m/%d/%Y %H:%M', '%m/%d/%Y',
        '%d-%m-%Y %H:%M:%S', '%d-%m-%Y',
        '%m-%d-%Y %H:%M:%S', '%m-%d-%Y',
    )
    for fmt in candidates:
        try:
            if all(datetime.datetime.strptime(v, fmt) for v in values):
                return fmt
        except ValueError:
            continue
    return None


def get_edited_cellname(row):
    return str(row.get('cellband', row.get('cellname', row.get('cellname(edit)-Sector', row.get('cell', 'N/A'))))).strip()


def get_sector_num(row):
    sec = str(row.get('Sector', '')).strip()
    if not sec:
        cname = get_edited_cellname(row)
        if cname and cname != 'N/A': sec = cname[-1]
    try: return int(sec)
    except Exception: return 99


def get_base_sector_num(row):
    sec = get_sector_num(row)
    if sec >= 99: return 99
    return ((sec - 1) % 3) + 1


def get_band_grp(row):
    b = str(row.get('Band', '')).strip().upper()
    if '900' in b or 'L09' in b or 'L9' in b: return "900"
    if '1800' in b or 'L18' in b: return "1800"
    if '2100' in b or 'L21' in b: return "2100"
    if '2300' in b or 'L23' in b: return "2300"
    return b or "UNKNOWN"


def get_band_sort_num(row):
    b = str(row.get('Band', '')).strip().upper()
    if '900' in b or 'L09' in b or 'L9' in b: return 1
    if '1800' in b or 'L18' in b: return 2
    if '2100' in b or 'L21' in b: return 3
    if '2300' in b or 'L23' in b: return 4
    return 99


def get_bin_distance(label_str):
    nums = [float(s) for s in re.findall(r'\d+\.?\d*', label_str.replace(',', '.'))]
    if 'k' in label_str.lower(): nums = [n * 1000 for n in nums]
    if nums and max(nums) < 20 and 'm' not in label_str.lower(): nums = [n * 1000 for n in nums]
    if len(nums) >= 2: return sum(nums[:2]) / 2.0
    elif len(nums) == 1: return nums[0] + 1000 if '>' in label_str else nums[0]
    return 100.0


def get_vendor_cfg(vendor):
    return VENDOR_CONFIG.get(vendor, VENDOR_CONFIG['ZTE'])


def _parse_ta_distance_range(label):
    """Parse TA distance-bin headers into metres.

    Supports the canonical template format (e.g. ``0-156m``), legacy
    ZTE/EID integer ranges without a unit (e.g. ``1015-1562``), and the
    Ericsson-style decimal-kilometre ranges used by the Pro parser
    (e.g. ``0.0-0.078`` or ``3.047-4.062``). Open-ended forms such as
    ``>10km`` are also supported.

    The important distinction is that a decimal range without an explicit
    unit and with values below 20 is interpreted as kilometres, not metres.
    This prevents Ericsson ranges such as 0.0-0.078 from being rounded to
    the incorrect labels 0-0m.
    """
    raw = str(label or '').strip()
    if not raw:
        return None
    low = raw.lower().replace(',', '.')

    if not ('>' in low or '-' in low or re.search(r'\d\s*(m|km)\b', low)):
        return None

    nums = [float(x) for x in re.findall(r'\d+(?:\.\d+)?', low)]
    if not nums:
        return None

    has_km = 'km' in low
    has_m = bool(re.search(r'\d\s*m\b', low)) and not has_km

    def to_m(x):
        if has_km:
            return x * 1000.0
        if has_m:
            return x
        if x < 20:
            return x * 1000.0
        return x

    vals = [to_m(x) for x in nums]

    if '>' in low:
        start = vals[0]
        return start, None, start, True

    if len(vals) >= 2:
        start, end = vals[0], vals[1]
        if end <= start:
            return None
        return start, end, (start + end) / 2.0, False

    return None

def _ta_format_warning(headers):
    """Return a useful validation message for common non-standard TA headers."""
    hs = [str(h).strip() for h in (headers or [])]
    ta_like = [h for h in hs if re.fullmatch(r'(?i)TA\s*\d+', h)]
    numeric_like = [h for h in hs if re.fullmatch(r'\d+(?:\.\d+)?', h)]
    if ta_like:
        return (
            'TA range columns use labels such as TA0, TA1, TA2. ' 
            'Please standardize them to explicit distance ranges, for example: ' 
            '0-156m, 156-234m, 234-546m, ...'
        )
    if len(numeric_like) >= 3:
        return (
            'TA range columns appear to use cumulative distance values such as ' 
            '156, 234, 546, ... . Please standardize them to explicit distance ' 
            'ranges, for example: 0-156m, 156-234m, 234-546m, ...'
        )
    return (
        'TA distribution columns were not detected. Use one common TA range ' 
        'format for all vendors/operators, for example: 0-156m, 156-234m, ' 
        '234-546m, ... . Do not use TA0/TA1 or bare cumulative distances.'
    )


def detect_ta_bins(headers):
    """Detect TA distribution columns directly from CSV headers.

    Vendor-independent: bin definitions come from the CSV header itself,
    while the selected Vendor remains metadata/reporting information.
    """
    detected = []
    for idx, h in enumerate(headers or []):
        parsed = _parse_ta_distance_range(h)
        if parsed is None:
            continue
        start_m, end_m, mid_m, open_ended = parsed
        detected.append({
            'column': h,
            'label': h,
            'start_m': start_m,
            'end_m': end_m,
            'mid_m': mid_m,
            'open_ended': open_ended,
            'index': idx,
        })
    detected.sort(key=lambda x: x['index'])
    if not detected:
        return []
    runs = [[detected[0]]]
    for prev, cur in zip(detected, detected[1:]):
        contiguous = cur['index'] == prev['index'] + 1
        increasing = cur['start_m'] >= prev['start_m'] - 1e-6
        prev_end = prev['end_m'] if prev['end_m'] is not None else prev['start_m']
        gap = abs(cur['start_m'] - prev_end)
        adjacent = gap <= max(50.0, prev_end * 0.25)
        if contiguous and increasing and adjacent:
            runs[-1].append(cur)
        else:
            runs.append([cur])
    best = max(runs, key=len)
    if len(best) < 3:
        return []
    return best


def detect_data_mapping(headers):
    """Detect logical TA metadata fields using common header synonyms."""
    normalized = {re.sub(r'[^a-z0-9]+', '', str(h).lower()): h for h in headers or []}

    def pick(names):
        for name in names:
            key = re.sub(r'[^a-z0-9]+', '', name.lower())
            if key in normalized:
                return normalized[key]
        return None

    mapping = {
        'longitude': pick(['Longitude', 'LON', 'LONG', 'GPS_LON', 'GPS_LONGITUDE', 'X']),
        'latitude': pick(['Latitude', 'LAT', 'GPS_LAT', 'GPS_LATITUDE', 'Y']),
        'azimuth': pick(['Azimuth', 'AZI', 'Bearing', 'Direction', 'DIR']),
        'cell': pick(['cellname(edit)-Sector', 'Cell ID', 'CellID', 'Cell Name', 'Cell', 'CELL_NAME', 'EUtranCell', 'LTE Name']),
        'sector': pick(['Sector', 'Sector ID', 'SectorID', 'SECTOR_ID']),
        'siteid': pick(['siteid', 'Site ID', 'SiteID', 'Site ID', 'SITE_ID']),
        'band': pick(['Band', 'Band Name', 'BandName', 'Frequency', 'Freq']),
        'vendor': pick(['Vendor', 'Vendor Name', 'VendorName', 'NE Vendor', 'Manufacturer', 'OEM', 'Operator Vendor']),
        'timestamp': pick(['Begin Time', 'Date Time', 'DateTime', 'Timestamp', 'Time', 'Start Time']),
        'end_time': pick(['End Time', 'Finish Time', 'Stop Time']),
        'sitename': pick(['sitename', 'Site Name', 'SiteName', 'SITE_NAME']),
    }
    return mapping


def _format_ta_bin_label(meta):
    """Create compact, engineering-friendly TA range labels in metres."""
    start = meta.get('start_m')
    end = meta.get('end_m')
    if start is None:
        return str(meta.get('label', 'TA'))
    def m(v):
        return str(int(round(v)))
    if meta.get('open_ended') or end is None:
        return f">{m(start)}m" if start < 10000 else '>10km'
    return f"{m(start)}-{m(end)}m"


def _axis_label_indices(n, max_labels=24):
    """Return at most max_labels evenly distributed tick indices."""
    if n <= 0:
        return []
    if n <= max_labels:
        return list(range(n))
    return list(np.linspace(0, n - 1, max_labels, dtype=int))


def build_ta_profile(headers):
    bins = detect_ta_bins(headers)
    if len(bins) < 2:
        return None
    labels = [_format_ta_bin_label(b) for b in bins]
    return {
        'bins': [b['column'] for b in bins],
        'labels': labels,
        'bin_meta': bins,
        'threshold_col_kw': [],
        'implemented': True,
        'source': 'CSV_AUTO_DETECT',
    }


def apply_data_mapping(rows, mapping):
    """Add canonical aliases without removing original CSV columns."""
    if not rows:
        return rows
    for row in rows:
        for canonical, source in mapping.items():
            if source and canonical not in row:
                row[canonical] = row.get(source, '')
        if 'cellname(edit)-Sector' not in row and mapping.get('cell'):
            row['cellname(edit)-Sector'] = row.get(mapping['cell'], '')
        if 'siteid' not in row and mapping.get('siteid'):
            row['siteid'] = row.get(mapping['siteid'], '')
        if 'Band' not in row and mapping.get('band'):
            row['Band'] = row.get(mapping['band'], '')
        if 'Vendor' not in row and mapping.get('vendor'):
            row['Vendor'] = row.get(mapping['vendor'], '')
        if 'Sector' not in row and mapping.get('sector'):
            row['Sector'] = row.get(mapping['sector'], '')
        if 'Azimuth' not in row and mapping.get('azimuth'):
            row['Azimuth'] = row.get(mapping['azimuth'], '')
        if 'Latitude' not in row and mapping.get('latitude'):
            row['Latitude'] = row.get(mapping['latitude'], '')
        if 'Longitude' not in row and mapping.get('longitude'):
            row['Longitude'] = row.get(mapping['longitude'], '')
        if 'Begin Time' not in row and mapping.get('timestamp'):
            row['Begin Time'] = row.get(mapping['timestamp'], '')
        if 'End Time' not in row and mapping.get('end_time'):
            row['End Time'] = row.get(mapping['end_time'], '')
        if 'sitename' not in row and mapping.get('sitename'):
            row['sitename'] = row.get(mapping['sitename'], '')
    return rows


def get_row_ta_bins(row, window=None):
    """Return the active normalized TA profile for a row/window."""
    profile = getattr(window, 'ta_profile', None) if window is not None else None
    if profile and profile.get('bins'):
        return profile
    vendor = getattr(window, 'vendor', 'ZTE') if window is not None else 'ZTE'
    return get_vendor_cfg(vendor)


def compute_dynamic_ta(row, cfg, threshold_pct):
    """Hitung percentile TA secara dinamis dari distribution bins aktif."""
    bins = cfg.get('bins', [])
    values = [safe_float(row.get(b, 0)) for b in bins]
    total = sum(values)
    if total <= 0 or not bins:
        return 0.0
    meta = cfg.get('bin_meta') or []
    if len(meta) != len(bins):
        distances = [get_bin_distance((cfg.get('labels', bins) or bins)[i]) for i in range(len(bins))]
    else:
        distances = [float(m.get('mid_m', m.get('start_m', 0))) for m in meta]
    running, cum_pct = 0.0, []
    for v in values:
        running += v
        cum_pct.append(running / total * 100.0)
    threshold_pct = max(0.0, min(100.0, float(threshold_pct)))
    for i, cp in enumerate(cum_pct):
        if cp >= threshold_pct:
            if i == 0:
                return distances[0]
            prev_cp, prev_d, d = cum_pct[i - 1], distances[i - 1], distances[i]
            if cp == prev_cp:
                return d
            frac = (threshold_pct - prev_cp) / (cp - prev_cp)
            return prev_d + frac * (d - prev_d)
    return distances[-1] if distances else 0.0


class SingleTAChart(QFrame):
    def __init__(self, row, window, parent=None):
        super().__init__(parent)
        self.row = row
        self._window = window
        self.vendor = window.vendor
        self.cfg = get_row_ta_bins(None, self._window)
        self.bins = self.cfg['bins']
        self.display_labels = self.cfg.get('labels', self.bins)
        if len(self.display_labels) != len(self.bins):
            self.display_labels = self.bins

        self.setMinimumWidth(320)
        self.setFixedHeight(250)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        bg_color = window.chart_fill_color
        font_color = window.chart_font_color
        bar_color = window.chart_bar_color
        line_color = window.chart_cdf_color
        grid_color = window.chart_grid_color
        is_prof = _is_light_bg(bg_color)

        self.setStyleSheet(f"background-color: {bg_color}; border: 1px solid #ccc; margin: 2px; border-radius: 4px;")
        self.setMinimumHeight(250)
        self.setMaximumHeight(285)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(2)
        self.fig, self.ax1 = plt.subplots(figsize=(3.5, 2.5), facecolor=bg_color, dpi=90)
        self.ax1.set_facecolor(bg_color)
        self.ax2 = self.ax1.twinx()
        self.ax2.set_facecolor('none')

        try:
            threshold = window.threshold
            ta_val = compute_dynamic_ta(row, self.cfg, threshold)
            c_name_edited = get_edited_cellname(row)
            title_text = f"{c_name_edited} ({row.get('Band', '-')}) | TA {threshold:.0f}%: {ta_val:.1f}m"
            self.ax1.set_title(title_text, color=font_color, fontsize=window.chart_font_size, fontweight='bold', pad=5, fontfamily=window.chart_font)

            values = [int(safe_float(row.get(b, 0))) for b in self.bins]
            total = sum(values)
            cdf = np.cumsum(values) / total * 100 if total > 0 else [0] * len(values)

            self.bars = self.ax1.bar(self.bins, values, width=0.48, color=bar_color, alpha=0.9, zorder=3)
            self.ax2.plot(self.bins, cdf, color=line_color, marker='o', markersize=2, linewidth=1, zorder=4)
            self.ax2.axhline(y=threshold, color=font_color, linestyle='--', linewidth=0.8, alpha=0.5, zorder=1)

            self.ax1.set_ylabel('Sample #', color=font_color, fontsize=window.chart_font_size, fontweight='bold', labelpad=8, fontfamily=window.chart_font)
            self.ax1.tick_params(axis='y', colors=font_color, labelsize=window.axis_font_size)
            self.ax1.yaxis.set_major_formatter(FuncFormatter(comma_format))
            self.ax2.set_ylabel('CDF %', color=font_color, fontsize=window.chart_font_size, fontweight='bold', fontfamily=window.chart_font)
            self.ax2.tick_params(axis='y', colors=font_color, labelsize=window.axis_font_size); self.ax2.set_ylim(0, 110)

            n_bins = len(self.bins)
            if n_bins > 40:
                auto_rotation, auto_fontsize, auto_margin, auto_pad = 90, 4, 0.44, 16
            elif n_bins > 24:
                auto_rotation, auto_fontsize, auto_margin, auto_pad = 90, 5, 0.40, 14
            else:
                auto_rotation, auto_fontsize, auto_margin, auto_pad = 55, 5, 0.28, 12
            max_labels = getattr(window, 'axis_max_labels', 0) or 24
            rotation = getattr(window, 'axis_rotation', 0) or auto_rotation
            tick_fontsize = getattr(window, 'axis_font_size', 0) or auto_fontsize
            manual_margin = getattr(window, 'axis_bottom_margin', 0)
            b_margin = (manual_margin / 100.0) if manual_margin else auto_margin
            manual_pad = getattr(window, 'axis_label_pad', 0)
            pad_x = manual_pad if manual_pad else auto_pad
            align = 'center' if rotation >= 80 else 'right'
            ticks_loc = _axis_label_indices(n_bins, max_labels)
            self.ax1.set_xticks(ticks_loc)
            self.ax1.set_xticklabels([self.display_labels[i] for i in ticks_loc],
                                     rotation=rotation, ha=align, va='top', rotation_mode='anchor', fontsize=tick_fontsize, fontfamily=window.chart_font)
            self.ax1.tick_params(axis='x', colors=font_color, labelsize=tick_fontsize, pad=pad_x, length=3)
            self.ax1.grid(True, axis='both', color=grid_color, linestyle='--', alpha=0.55 if is_prof else 0.35, zorder=0)

            self.annot = self.ax1.annotate("", xy=(0, 0), xytext=(10, 10), textcoords="offset points", fontsize=6,
                                            bbox=dict(boxstyle="round,pad=0.3", fc=(1, 0.7, 0.8, 0.5), ec=(1, 0.4, 0.6), lw=1),
                                            arrowprops=dict(arrowstyle="->", color=(1, 0.4, 0.6)), zorder=10)
            self.annot.set_visible(False)
            self.ax2.set_zorder(self.ax1.get_zorder() + 1)
            self.ax2.patch.set_visible(False)
            self.ax1.patch.set_visible(True)
            self.ax1.set_facecolor(bg_color)
            self.fig.patch.set_facecolor(bg_color)
            self.fig.subplots_adjust(bottom=b_margin, left=0.27, right=0.85, top=0.88)
            self.canvas = FigureCanvas(self.fig); self.canvas.mpl_connect("motion_notify_event", self.hover)
            self.canvas.setMinimumHeight(225)
            self.canvas.setMaximumHeight(255)
            layout.addWidget(self.canvas)
        except Exception as e:
            print(f"SingleTAChart error: {e}")

    def close_figure(self):
        fig = getattr(self, 'fig', None)
        if fig is not None:
            try:
                plt.close(fig)
            except Exception:
                pass
            self.fig = None
        canvas = getattr(self, 'canvas', None)
        if canvas is not None:
            try:
                canvas.close()
            except Exception:
                pass

    def hover(self, event):
        if event.inaxes in (self.ax1, self.ax2) and event.xdata is not None:
            idx = int(round(event.xdata))
            if 0 <= idx < len(self.bars):
                bar = self.bars[idx]
                lbl = self.display_labels[idx] if idx < len(self.display_labels) else "N/A"
                self.annot.xy = (bar.get_x() + bar.get_width() / 2., bar.get_height())
                self.annot.set_text(f"{lbl}\nSamples: {comma_format(bar.get_height(), 0)}")
                self.annot.set_visible(True); self.fig.canvas.draw_idle(); return
        if self.annot.get_visible():
            self.annot.set_visible(False); self.fig.canvas.draw_idle()




class PopupSelectButton(QPushButton):
    """Compact Pro-style dropdown button used by Data & Filter."""
    def __init__(self, label, options, multi=False, selected=None, on_change=None, parent=None):
        super().__init__(label, parent)
        self.label_text=label; self.multi=multi; self.options=list(options or []); self.on_change=on_change
        self.selected=set(selected or [])
        self.setMinimumHeight(34); self.setCursor(Qt.PointingHandCursor)
        self._arrow=QLabel('▼', self); self._arrow.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self._arrow.setAlignment(Qt.AlignCenter); self._arrow.setFixedWidth(22); self._arrow.setStyleSheet('background:transparent;color:#777;font-size:9px;')
        self.clicked.connect(self._show_menu); self._position_arrow(); self._build_menu(); self._refresh_text()
    def resizeEvent(self,e):
        super().resizeEvent(e); self._position_arrow()
    def _position_arrow(self):
        self._arrow.setGeometry(max(0,self.width()-25),0,22,self.height())
    def _build_menu(self):
        self.menu=QMenu(self); self.menu.setStyleSheet('QMenu{background:#3a3b3f;color:#dfe3e8;border:1px solid #777;} QMenu::item:selected{background:#3a6ea8;color:#fff;}')
        self._actions={}
        if self.multi:
            a=self.menu.addAction('Select All'); a.triggered.connect(self._select_all)
            a=self.menu.addAction('Deselect All'); a.triggered.connect(self._deselect_all)
            self.menu.addSeparator()
        for opt in self.options:
            a=self.menu.addAction(str(opt)); a.setCheckable(True); a.setChecked(str(opt) in self.selected)
            a.triggered.connect(lambda checked,o=str(opt): self._toggle(o,checked)); self._actions[str(opt)]=a
    def _refresh_text(self):
        if self.multi:
            if not self.selected: text=f'{self.label_text} : All'
            else: text=f'{self.label_text} : {", ".join(sorted(self.selected, key=str))}'
        else: text=f'{self.label_text} : {next(iter(self.selected), "Auto Detect" if self.label_text=="Vendor" else "All")}'
        self.setText(text)
    def _show_menu(self): self.menu.exec(self.mapToGlobal(self.rect().bottomLeft()))
    def _select_all(self):
        self.selected=set(self.options)
        for a in self._actions.values(): a.setChecked(True)
        self._refresh_text(); self._changed()
    def _deselect_all(self):
        self.selected=set()
        for a in self._actions.values(): a.setChecked(False)
        self._refresh_text(); self._changed()
    def _toggle(self,opt,checked):
        if self.multi:
            if checked:self.selected.add(opt)
            else:self.selected.discard(opt)
        else:
            self.selected={opt}
            for o,a in self._actions.items():
                if o!=opt:a.setChecked(False)
        self._refresh_text(); self._changed()
    def _changed(self):
        if self.on_change:self.on_change(set(self.selected))
    def refresh_options(self,options,selected=None):
        self.options=list(options or [])
        if selected is not None:self.selected=set(selected)
        self._build_menu(); self._refresh_text()

class ChartSettingDialog(QDialog):
    def __init__(self,w,parent=None):
        super().__init__(parent); self.w=w; self.setWindowTitle(APP_NAME+' - Chart Setting'); self.setMinimumWidth(470); lay=QVBoxLayout(self); f=QFormLayout()
        self.font=QFontComboBox(); self.font.setCurrentFont(QFont(w.chart_font)); f.addRow('Chart Font:',self.font)
        self.size=QSpinBox(); self.size.setRange(6,18); self.size.setValue(w.chart_font_size); f.addRow('Font Size:',self.size)
        self.maxlab=QSpinBox(); self.maxlab.setRange(6,60); self.maxlab.setValue(w.axis_max_labels); f.addRow('Max Axis Labels:',self.maxlab)
        self.rot=QSpinBox(); self.rot.setRange(0,90); self.rot.setValue(w.axis_rotation); f.addRow('Axis Rotation:',self.rot)
        self.af=QDoubleSpinBox(); self.af.setRange(4,12); self.af.setSingleStep(.5); self.af.setValue(w.axis_font_size); f.addRow('Axis Font Size:',self.af); lay.addLayout(f)
        self.btns={}
        for k,lab in [('chart_font_color','Font Color'),('chart_bar_color','TA Bar Color'),('chart_cdf_color','CDF Line Color'),('chart_fill_color','Chart Background'),('chart_grid_color','Grid Color')]:
            b=QPushButton(lab); b.setProperty('v',getattr(w,k)); b.clicked.connect(lambda _,kk=k,bb=b:self.pick(kk,bb)); self.btns[k]=b; lay.addWidget(b)
        row=QHBoxLayout(); reset=QPushButton('Reset Default'); reset.clicked.connect(self.reset_default); row.addWidget(reset); row.addStretch(); ok=QPushButton('Save'); ca=QPushButton('Cancel'); ok.clicked.connect(self.accept); ca.clicked.connect(self.reject); row.addWidget(ok); row.addWidget(ca); lay.addLayout(row); self.refresh()
    def reset_default(self):
        self.font.setCurrentFont(QFont('Arial')); self.size.setValue(9); self.maxlab.setValue(24); self.rot.setValue(90); self.af.setValue(5.5); self.w.chart_font='Arial'; self.w.chart_font_size=9; self.w.axis_max_labels=24; self.w.axis_rotation=90; self.w.axis_font_size=5.5
        defaults={'chart_font_color':'#f5f5f0','chart_bar_color':'#00BFFF','chart_cdf_color':'#FF8C00','chart_fill_color':'#1E1E1E','chart_grid_color':'#555555'}
        for k,c in defaults.items():
            setattr(self.w,k,c); self.btns[k].setProperty('v',c)
        self.refresh()
    def pick(self,k,b):
        c=QColorDialog.getColor(QColor(getattr(self.w,k)),self)
        if c.isValid(): setattr(self.w,k,c.name()); b.setProperty('v',c.name()); self.refresh()
    def refresh(self):
        for b in self.btns.values():
            c=b.property('v'); b.setStyleSheet(f'background:{c};color:{"#111" if _is_light_bg(c) else "#fff"};')
    def accept(self):
        self.w.chart_font=self.font.currentFont().family(); self.w.chart_font_size=self.size.value(); self.w.axis_max_labels=self.maxlab.value(); self.w.axis_rotation=self.rot.value(); self.w.axis_font_size=self.af.value(); super().accept()

class AggregationDialog(QDialog):
    DAYS={'1 Day':1,'3 Days':3,'1 Week':7}
    def __init__(self,w,parent=None):
        super().__init__(parent); self.w=w; self.setWindowTitle('Aggregate'); lay=QVBoxLayout(self); lay.addWidget(QLabel(f'Data available: {w.data_date_min:%d %b %Y} - {w.data_date_max:%d %b %Y}')); f=QFormLayout(); self.cmb=QComboBox(); self.cmb.addItems(['Full Month (All Data)','1 Day','3 Days','1 Week']); f.addRow('Granularity:',self.cmb); self.start=QDateEdit(); self.start.setCalendarPopup(True); self.start.setDisplayFormat('dd MMM yyyy'); self.start.setMinimumDate(QDate(w.data_date_min.year,w.data_date_min.month,w.data_date_min.day)); self.start.setMaximumDate(QDate(w.data_date_max.year,w.data_date_max.month,w.data_date_max.day)); self.start.setDate(self.start.minimumDate()); f.addRow('Start Date:',self.start); self.end=QLabel('-'); f.addRow('End Date:',self.end); lay.addLayout(f); self.cmb.currentTextChanged.connect(self.update); self.start.dateChanged.connect(self.update); self.update(); r=QHBoxLayout(); r.addStretch(); ok=QPushButton('OK'); ca=QPushButton('Cancel'); ok.clicked.connect(self.accept); ca.clicked.connect(self.reject); r.addWidget(ok); r.addWidget(ca); lay.addLayout(r)
    def update(self,*a):
        if self.cmb.currentText().startswith('Full'): self.start.setEnabled(False); self.end.setText('-'); return
        self.start.setEnabled(True); s=self.start.date().toPyDate(); e=min(s+datetime.timedelta(days=self.DAYS.get(self.cmb.currentText(),1)-1),self.w.data_date_max); self.end.setText(e.strftime('%d %b %Y'))
    def get_result(self):
        g=self.cmb.currentText()
        if g.startswith('Full'): return 'All',None,None,'All'
        s=self.start.date().toPyDate(); e=min(s+datetime.timedelta(days=self.DAYS.get(g,1)-1),self.w.data_date_max); return g,s,e,(s.strftime('%d %b %Y') if s==e else f'{s:%d}–{e:%d %b %Y}')

class TASuiteWindow(QMainWindow):
    def __init__(self,plugin,parent=None):
        super().__init__(parent); self.plugin=plugin; self.setWindowTitle(f'{APP_NAME} v{VERSION} | Jujun.J'); self.resize(1500,900)
        self.data=[]; self.file_path=''; self.vendor='ZTE'; self.vendor_name='ZTE'; self.ta_profile=None; self.data_mapping={}; self.threshold=85; self.aggregation_start=None; self.aggregation_end=None; self.data_date_min=None; self.data_date_max=None; self._begin_time_fmt=None; self.site_input_text=''; self.current_matched_rows=[]; self.current_charts=[]
        self.chart_font='Arial'; self.chart_font_size=9; self.chart_font_color='#f5f5f0'; self.chart_bar_color='#00BFFF'; self.chart_cdf_color='#FF8C00'; self.chart_fill_color='#1E1E1E'; self.chart_grid_color='#555555'; self.axis_max_labels=24; self.axis_rotation=90; self.axis_font_size=5.5
        self._load_settings(); self._build_ui(); self._apply_theme()
    def _load_settings(self):
        s=QSettings('JujunJ','TAAnalysisSuiteLite')
        for k,v in DEFAULT_UI_THEME.items(): setattr(self,k,s.value(k,v))
        self.ui_font_size=int(float(s.value('ui_font_size',10))); self.chart_font_size=int(float(s.value('chart_font_size',9))); self.axis_max_labels=int(float(s.value('axis_max_labels',24))); self.axis_rotation=int(float(s.value('axis_rotation',90))); self.axis_font_size=float(s.value('axis_font_size',5.5))
        if not s.value('axis_rotation_migrated_90', False, type=bool):
            self.axis_rotation=90
            s.setValue('axis_rotation',90)
            s.setValue('axis_rotation_migrated_90', True)
    def _apply_theme(self):
        self.setStyleSheet(f"QMainWindow,QWidget{{background:{self.ui_bg};color:{self.ui_text_color};font-family:'{self.ui_font}';font-size:{self.ui_font_size}px}} QFrame#header{{background:{self.ui_header_bg}}} QFrame#topnav,QFrame#filterbar{{background:{self.ui_toolbar_bg}}} QFrame#iconRail,QFrame#dataDrawer{{background:{self.ui_toolbar_bg}}} QPushButton{{background:{self.ui_button_bg};color:{self.ui_button_text};border:1px solid #666;border-radius:5px;padding:6px 10px}} QPushButton:hover{{background:{self.ui_button_active};color:#fff}} QPushButton[navButton=\"true\"],QToolButton[navButton=\"true\"]{{border:none;border-radius:0;padding:8px 14px;font-weight:bold;color:{self.ui_button_text};background:transparent}} QToolButton[navButton=\"true\"]:checked,QPushButton[navButton=\"true\"]:checked{{color:#4fa3ff;border-bottom:3px solid #4fa3ff;background:{self.ui_toolbar_bg}}} QPushButton[railButton=\"true\"]{{padding:5px;border:1px solid transparent;border-radius:6px}} QPushButton[railButton=\"true\"]:checked{{background:{self.ui_button_active};border:1px solid #4fa3ff}} QPushButton#filterChip{{border:1px solid #666;border-radius:8px;padding:6px 12px;background:{self.ui_button_bg}}} QLineEdit,QComboBox,QSpinBox,QDoubleSpinBox{{background:{self.ui_button_bg};color:{self.ui_button_text};border:1px solid #666;border-radius:4px;padding:5px}} QTabWidget::pane{{border:1px solid #555}} QTabBar::tab{{background:{self.ui_button_bg};color:{self.ui_button_text};padding:7px 14px}} QTabBar::tab:selected{{background:{self.ui_button_active};color:#fff}}")
    def _icon(self, rel):
        return QIcon(os.path.join(os.path.dirname(__file__), 'icons', rel))

    def _build_ui(self):
        root = QWidget()
        outer = QVBoxLayout(root)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        header = QFrame()
        header.setObjectName('header')
        header.setFixedHeight(58)
        hl = QHBoxLayout(header)
        hl.setContentsMargins(18, 0, 18, 0)
        self.page_title = QLabel('Dashboard TA by Cell Level')
        self.page_title.setAlignment(Qt.AlignCenter)
        self.page_title.setStyleSheet('color:white;font-size:16px;font-weight:bold;background:transparent;border:none')
        hl.addStretch(1)
        hl.addWidget(self.page_title)
        hl.addStretch(1)
        outer.addWidget(header)

        navw = QFrame()
        navw.setObjectName('topnav')
        nav = QHBoxLayout(navw)
        nav.setContentsMargins(14, 2, 14, 2)
        nav.setSpacing(2)
        self.views = {}
        names = ['Map View', 'Cell Level', 'Band Comparison', 'Before-After by Cell',
                 'Before-After by Band', 'Data Table', 'Summary']
        locked = {'Map View', 'Band Comparison', 'Before-After by Cell', 'Before-After by Band', 'Data Table', 'Summary'}
        for name in names:
            b = QToolButton()
            b.setText(name)
            b.setCheckable(True)
            b.setAutoRaise(True)
            b.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
            b.setCursor(Qt.PointingHandCursor)
            b.setMinimumHeight(36)
            b.setProperty('navButton', True)
            if name in locked:
                b.setIcon(self._icon('common/lock.svg'))
                b.setIconSize(QSize(14, 14))
                b.setToolTip(f'{name} — Pro Feature')
            b.clicked.connect(lambda checked, x=name: self.activate_view(x))
            self.views[name] = b
            nav.addWidget(b)
        nav.addStretch(1)
        self.views['Cell Level'].setChecked(True)
        outer.addWidget(navw)

        topbar = QFrame()
        topbar.setObjectName('filterbar')
        fr = QHBoxLayout(topbar)
        fr.setContentsMargins(18, 0, 18, 7)
        fr.setSpacing(7)
        self.chip_site = self._chip('Site: —')
        self.chip_vendor = self._chip('Vendor: —')
        self.chip_band = self._chip('Band: All')
        self.chip_threshold = self._chip('Threshold: 85%')
        self.chip_aggregate = self._chip('Aggregate: All')
        for x in (self.chip_site, self.chip_vendor, self.chip_band, self.chip_threshold, self.chip_aggregate):
            fr.addWidget(x)
        fr.addStretch(1)
        self.export_btn = QPushButton('Export')
        self.export_btn.setIcon(self._icon('toolbar/export.svg'))
        self.export_btn.clicked.connect(lambda: self.locked('Export'))
        self.clear_btn = QPushButton('Clear')
        self.clear_btn.setIcon(self._icon('actions/clear.svg'))
        self.clear_btn.clicked.connect(self.clear_all)
        fr.addWidget(self.export_btn)
        fr.addWidget(self.clear_btn)
        outer.addWidget(topbar)

        self.main_splitter = QSplitter(Qt.Horizontal)
        self.main_splitter.setHandleWidth(4)
        self.main_splitter.setStyleSheet('QSplitter::handle{background:#444;}')

        sidebar = QFrame()
        sidebar.setObjectName('sidebar')
        sidebar.setMinimumWidth(56)
        sidebar.setMaximumWidth(464)
        sb = QHBoxLayout(sidebar)
        sb.setContentsMargins(0, 0, 0, 0)
        sb.setSpacing(0)

        rail = QFrame()
        rail.setObjectName('iconRail')
        rail.setFixedWidth(44)
        rl = QVBoxLayout(rail)
        rl.setContentsMargins(6, 8, 6, 8)
        rl.setSpacing(5)
        self.data_btn = self._rail_button('common/data_source.svg', 'Data & Filter')
        self.set_btn = self._rail_button('toolbar/settings.svg', 'Setting')
        self.about_btn = self._rail_button('common/info.svg', 'About')
        self.data_btn.setChecked(True)
        rl.addWidget(self.data_btn)
        rl.addWidget(self.set_btn)
        rl.addWidget(self.about_btn)
        rl.addStretch(1)
        sb.addWidget(rail)

        self.drawer = QFrame()
        self.drawer.setObjectName('dataDrawer')
        self.drawer.setMinimumWidth(208)
        self.drawer.setMaximumWidth(408)
        dl = QVBoxLayout(self.drawer)
        dl.setContentsMargins(10, 7, 10, 8)
        dl.setSpacing(8)
        head = QHBoxLayout()
        lab = QLabel('Data & Filter')
        lab.setStyleSheet('font-weight:bold;font-size:13px;background:transparent;border:none')
        head.addWidget(lab)
        head.addStretch(1)
        self.drawer_toggle = QPushButton('‹')
        self.drawer_toggle.setFixedSize(30, 30)
        self.drawer_toggle.setToolTip('Collapse Data & Filter')
        self.drawer_toggle.clicked.connect(self.toggle_drawer)
        head.addWidget(self.drawer_toggle)
        dl.addLayout(head)

        grid = QGridLayout()
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(8)
        button_h = 36

        browse = QPushButton('Browse')
        browse.setIcon(self._icon('toolbar/browse.svg'))
        browse.setIconSize(QSize(18, 18))
        browse.setFixedHeight(button_h)
        browse.clicked.connect(self.browse_file)
        grid.addWidget(browse, 0, 0)

        generated = QPushButton('Generated')
        generated.setIcon(self._icon('toolbar/generated.svg'))
        generated.setIconSize(QSize(18, 18))
        generated.setFixedHeight(button_h)
        generated.clicked.connect(self.generate_sites)
        grid.addWidget(generated, 0, 1)

        self.site_label = QPushButton('Input Site (1 site only) : —')
        self.site_label.setFixedHeight(button_h)
        self.site_label.setCursor(Qt.PointingHandCursor)
        self.site_label.clicked.connect(self.edit_site)
        grid.addWidget(self.site_label, 1, 0, 1, 2)

        self.selected_bands = set()
        self.selected_sectors = set()
        self.vendor_btn = PopupSelectButton('Vendor', ['Auto Detect'], multi=False,
                                            selected={'Auto Detect'}, on_change=self._on_vendor_change)
        self.band_btn = PopupSelectButton('Band', ['All Bands'], multi=True,
                                          selected=set(), on_change=self._on_band_change)
        self.vendor_btn.setFixedHeight(button_h)
        self.band_btn.setFixedHeight(button_h)
        grid.addWidget(self.vendor_btn, 3, 0)
        grid.addWidget(self.band_btn, 3, 1)

        self.sector_btn = PopupSelectButton('Sector', [f'Sector {i}' for i in range(1, 10)],
                                            multi=True, selected=set(), on_change=self._on_sector_change)
        self.elev = self.lock_button('Elevation')
        self.sector_btn.setFixedHeight(button_h)
        self.elev.setFixedHeight(button_h)
        grid.addWidget(self.sector_btn, 4, 0)
        grid.addWidget(self.elev, 4, 1)

        self.beam = self.lock_button('Beam View')
        self.azimuth_btn = self.lock_button('Update Azimuth')
        self.beam.setFixedHeight(button_h)
        self.azimuth_btn.setFixedHeight(button_h)
        grid.addWidget(self.beam, 5, 0)
        grid.addWidget(self.azimuth_btn, 5, 1)

        self.th = QPushButton('Threshold 85%')
        self.th.setFixedHeight(button_h)
        self.th.clicked.connect(self.edit_threshold)
        grid.addWidget(self.th, 6, 0)
        self.agg = QPushButton('Aggregate: All')
        self.agg.setFixedHeight(button_h)
        self.agg.clicked.connect(self.edit_aggregate)
        grid.addWidget(self.agg, 6, 1)

        dl.addLayout(grid)
        dl.addStretch(1)
        sb.addWidget(self.drawer, 1)

        self.stack = QStackedWidget()
        self.cell = QWidget()
        self.cell_layout = QVBoxLayout(self.cell)
        self.cell_layout.setContentsMargins(18, 10, 18, 18)
        self.cell_layout.setAlignment(Qt.AlignTop)
        cell_scroll = QScrollArea()
        cell_scroll.setWidgetResizable(True)
        cell_scroll.setFrameShape(QFrame.NoFrame)
        cell_scroll.setWidget(self.cell)
        self.stack.addWidget(cell_scroll)


        self.main_splitter.addWidget(sidebar)
        self.main_splitter.addWidget(self.stack)
        self.main_splitter.setStretchFactor(0, 0)
        self.main_splitter.setStretchFactor(1, 1)
        self.main_splitter.setSizes([324, 1176])
        outer.addWidget(self.main_splitter, 1)
        self.setCentralWidget(root)

        self.data_btn.clicked.connect(self.toggle_drawer)
        self.set_btn.clicked.connect(self.show_settings)
        self.about_btn.clicked.connect(self.show_about)


    def _chip(self,text):
        b=QPushButton(text); b.setObjectName('filterChip'); b.setMinimumHeight(38); return b

    def _field_label(self,text):
        x=QLabel(text); x.setStyleSheet('font-weight:bold'); return x

    def _rail_button(self,icon_rel,tip):
        b=QPushButton(); b.setCheckable(True); b.setFixedSize(44,44); b.setIcon(self._icon(icon_rel)); b.setIconSize(QSize(23,23)); b.setToolTip(tip); b.setProperty('railButton',True); return b

    def toggle_drawer(self):
        vis=self.drawer.isVisible()
        self.drawer.setVisible(not vis)
        if vis:
            self.main_splitter.setSizes([56, max(1, self.main_splitter.width()-56)])
        else:
            self.main_splitter.setSizes([408, max(1, self.main_splitter.width()-408)])
        self.drawer_toggle.setText('‹' if not vis else '›')
        self.drawer_toggle.setToolTip('Collapse Data & Filter' if not vis else 'Expand Data & Filter')
        self.data_btn.setChecked(not vis)

    def edit_site(self):
        current=self.site_input_text
        text,ok=QInputDialog.getText(self,'Input Site','SiteID (1 site only):',text=current)
        if ok:
            text=text.strip().upper()
            if ',' in text or ';' in text:
                return self.info('Input Site','Lite supports one SiteID only.')
            self.site_input_text=text
            self.update_filter_chips()

    def lock_button(self,label):
        b=QPushButton(label); b.setIcon(self._icon('common/lock.svg')); b.setIconSize(QSize(15,15)); b.setToolTip(f'{label} — Pro Feature'); b.clicked.connect(lambda:self.locked(label)); return b

    def locked(self,feature):
        d=QDialog(self); d.setWindowTitle('TA Analysis Suite Pro'); d.setMinimumWidth(560); d.setStyleSheet("QDialog{background:#ffffff;color:#263238;} QLabel{color:#263238;} QPushButton{min-height:32px;padding:6px 14px;} QFrame{background:#f7f9fb;border:1px solid #d9dee5;border-radius:6px;}")
        lay=QVBoxLayout(d); lay.setContentsMargins(24,20,24,20); lay.setSpacing(11)
        title=QLabel(f'<b style="font-size:18px;color:#2f5f8f;">{feature}</b><br><span style="font-size:12px;color:#66727f;">TA Analysis Suite Pro Feature</span>'); title.setTextFormat(Qt.RichText); lay.addWidget(title)
        msg=QLabel('You are currently using <b>TA Analysis Suite Lite</b>, focused on Single-Site Cell Level Analysis.<br><br>Upgrade to Pro to unlock the complete TA analysis experience, including Map View, Band Comparison, Before-After Analysis, Beam View, Elevation Profile, Professional Themes, and other advanced capabilities.')
        msg.setWordWrap(True); msg.setTextFormat(Qt.RichText); lay.addWidget(msg)
        cta=QLabel('<b style="color:#2f5f8f;">Want the Pro Edition?</b><br><span style="color:#4f5b66;">Watch the Pro demo, then choose the purchase option that matches your location.</span>')
        cta.setWordWrap(True); cta.setTextFormat(Qt.RichText); lay.addWidget(cta)
        links=QGridLayout(); links.setHorizontalSpacing(18); links.setVerticalSpacing(8)
        links.addWidget(QLabel('<b>Pro Video</b>'),0,0); links.addWidget(self._link_label('Watch Pro Video / Demo',PRO_VIDEO_URL),0,1)
        links.addWidget(QLabel('<b>Global Users</b>'),1,0); links.addWidget(self._link_label('Purchase via Gumroad',GUMROAD_URL),1,1)
        links.addWidget(QLabel('<b>Indonesia</b>'),2,0); links.addWidget(self._link_label('Purchase via Lynk.id',LYNK_ID_URL),2,1)
        links.addWidget(QLabel('<b>TA.csv Template</b>'),3,0); links.addWidget(self._link_label('Download TA.csv Template',TA_TEMPLATE_URL),3,1)
        lay.addLayout(links)
        note=QLabel('<span style="color:#66727f;font-size:11px;">Gumroad is for users outside Indonesia. Lynk.id is provided for users in Indonesia with local payment options.</span>'); note.setWordWrap(True); note.setTextFormat(Qt.RichText); lay.addWidget(note)
        close=QPushButton('Maybe Later'); close.clicked.connect(d.accept); lay.addWidget(close); d.exec()

    def activate_view(self, name):
        if name != 'Cell Level':
            self.views['Cell Level'].setChecked(True)
            self.views[name].setChecked(False)
            self.locked(name)
            return
        for key, button in self.views.items():
            button.setChecked(key == 'Cell Level')
        self.page_title.setText('Dashboard TA by Cell Level')
        self.stack.setCurrentIndex(0)

    def filters_changed(self,*args):
        if self.current_matched_rows: self.generate_sites(True)
        self.update_filter_chips()

    def update_filter_chips(self):
        sid=self.site_input_text or '—'
        vendor=next(iter(self.vendor_btn.selected), 'Auto Detect') if hasattr(self,'vendor_btn') else '—'
        band=', '.join(sorted(self.selected_bands,key=str)) if getattr(self,'selected_bands',set()) else 'All'
        sec=', '.join(sorted(self.selected_sectors,key=str)) if getattr(self,'selected_sectors',set()) else 'All'
        self.chip_site.setText(f'Site: {sid}'); self.chip_vendor.setText(f'Vendor: {vendor}'); self.chip_band.setText(f'Band: {band}'); self.chip_threshold.setText(f'Threshold: {self.threshold}%'); self.chip_aggregate.setText(f'Aggregate: {self.agg.text().replace("Aggregate: ","")}')
        self.site_label.setText(f'Input Site (1 site only) : {sid if sid != "—" else "—"}')
        self.vendor_btn._refresh_text(); self.band_btn._refresh_text(); self.sector_btn._refresh_text()

    def clear_all(self):
        self.data=[]; self.file_path=''; self.site_input_text=''; self.current_matched_rows=[]; self._site_index={}; self._vendor_values=[]; self._band_values=[]; self._sector_values=[]; self.clear_charts()
        self.selected_bands=set(); self.selected_sectors=set(); self.vendor='ZTE'; self.vendor_name='ZTE'; self.vendor_btn.selected={'Auto Detect'}; self.band_btn.refresh_options(['All Bands'],set()); self.sector_btn.refresh_options([f'Sector {i}' for i in range(1,10)],set()); self.threshold=85; self.aggregation_start=self.aggregation_end=None; self.agg.setText('Aggregate: All'); self.update_filter_chips(); self.stack.setCurrentIndex(0); self.views['Cell Level'].setChecked(True)

    def _on_vendor_change(self,selected):
        text=next(iter(selected),'Auto Detect')
        if text == 'Auto Detect':
            self._auto_detect_vendor_from_data(); return
        self.vendor=text
        self.vendor_name=text
        if self.current_charts:self.generate_sites(True)
        self.update_filter_chips()

    def _on_band_change(self,selected):
        self.selected_bands=set(selected)
        if 'All Bands' in self.selected_bands:self.selected_bands=set()
        if self.current_matched_rows:self.generate_sites(True)
        self.update_filter_chips()

    def _on_sector_change(self,selected):
        self.selected_sectors=set(selected)
        if self.current_matched_rows:self.generate_sites(True)
        self.update_filter_chips()

    def refresh_bands(self):
        bands=sorted(self._band_values, key=str)
        self.selected_bands &= set(bands)
        self.band_btn.refresh_options(bands or ['All Bands'],self.selected_bands)
        sectors=sorted(self._sector_values, key=lambda x: (get_sector_num({'Sector': x}), str(x)))
        self.sector_btn.refresh_options(sectors or [f'Sector {i}' for i in range(1,10)], self.selected_sectors)
        self.update_filter_chips()
    def detect_prepare(self,headers, apply_rows=True):
        self.data_mapping=detect_data_mapping(headers); self.ta_profile=build_ta_profile(headers)
        if not self.ta_profile: raise ValueError(_ta_format_warning(headers))
        req=('latitude','longitude','cell','siteid','band','azimuth'); miss=[x for x in req if not self.data_mapping.get(x)]
        if miss: raise ValueError('Required fields not found: '+', '.join(miss))
        if apply_rows:
            apply_data_mapping(self.data,self.data_mapping)
    def info(self, title, message):
        """Show a compact informational message without depending on QGIS message-bar helpers."""
        QMessageBox.information(self, title, message)

    def error(self, title, message):
        """Show a compact error message without depending on QGIS message-bar helpers."""
        QMessageBox.critical(self, title, message)

    def browse_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Select TA Data File', '', 'CSV Files (*.csv)')
        if not fname:
            return
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            with open(fname, 'r', encoding='utf-8-sig', newline='') as fh:
                first = fh.readline()
                sep = ';' if ';' in first else ','
                fh.seek(0)
                reader = csv.reader(fh, delimiter=sep)
                try:
                    headers = next(reader)
                except StopIteration:
                    headers = []
                self.detect_prepare(headers, apply_rows=False)
                header_count = len(headers)
                normalized = {re.sub(r'[^a-z0-9]+', '', str(h).lower()): h for h in headers}
                source_for = self.data_mapping
                canonical_sources = {k: source_for.get(k) for k in source_for}
                canonical_indices = {k: headers.index(v) for k,v in canonical_sources.items() if v in headers}
                self.data=[]
                self._site_index={}
                vendor_seen=set(); band_seen=set(); sector_seen=set()
                dates=[]; date_cache={}
                timestamp_idx=canonical_indices.get('timestamp')
                # Keep the first-pass parser format-independent; cache repeated timestamps.
                for i, values in enumerate(reader, 1):
                    if len(values) < header_count:
                        values = list(values) + [''] * (header_count - len(values))
                    elif len(values) > header_count:
                        values = values[:header_count]
                    row = dict(zip(headers, values))
                    for canonical, idx in canonical_indices.items():
                        if canonical not in row:
                            row[canonical] = values[idx]
                    self.data.append(row)

                    sid=str(row.get('siteid','')).strip().upper()
                    if sid:
                        self._site_index.setdefault(sid, []).append(row)
                    v=str(row.get('Vendor','')).strip()
                    if v and v not in vendor_seen and len(vendor_seen)<50:
                        vendor_seen.add(v)
                    b=str(row.get('Band','')).strip()
                    if b:
                        band_seen.add(b)
                    sec=str(row.get('Sector','')).strip()
                    if sec:
                        sector_seen.add(f'Sector {sec}' if not sec.lower().startswith('sector') else sec)
                    if timestamp_idx is not None:
                        raw_date=values[timestamp_idx].strip()
                        if raw_date:
                            if raw_date in date_cache:
                                d=date_cache[raw_date]
                            else:
                                d=parse_begin_time_to_date(raw_date)
                                date_cache[raw_date]=d
                            if d:
                                dates.append(d)
                    if i % 50000 == 0:
                        QCoreApplication.processEvents()
            self.file_path = fname
            self._vendor_values=sorted(vendor_seen, key=str)
            self._band_values=band_seen
            self._sector_values=sector_seen
            self.data_date_min=min(dates) if dates else None
            self.data_date_max=max(dates) if dates else None
            self._auto_detect_vendor_from_data()
            self.refresh_bands()
            self.aggregation_start = self.aggregation_end = None
            self.agg.setText('Aggregate: All')
            self.info('Browse', f'Loaded {len(self.data):,} rows and {len(self.ta_profile["bins"])} TA bins.')
        except Exception as e:
            self.error('Unable to read CSV', str(e))
        finally:
            QApplication.restoreOverrideCursor()

    def _auto_detect_vendor_from_data(self):
        """Refresh the vendor selector from values collected while loading."""
        values=list(self._vendor_values)
        options=['Auto Detect'] + values
        self.vendor_btn.refresh_options(options, set())
        if len(values)==1:
            detected=values[0]
            self.vendor=detected
            self.vendor_name=detected
            self.vendor_btn.selected={detected}
        else:
            self.vendor='Auto Detect'
            self.vendor_name='Auto Detect'
            self.vendor_btn.selected={'Auto Detect'}
        self.vendor_btn._refresh_text(); self.update_filter_chips()

    def scan_dates(self):
        """Date bounds are collected during the CSV load pass."""
        if not self.data:
            self.data_date_min=self.data_date_max=None

    def edit_threshold(self):
        v,ok=QInputDialog.getInt(self,'TA Threshold','Percentile:',self.threshold,50,99,1)
        if ok:self.threshold=v; self.th.setText(f'Threshold {v}%'); self.generate_sites(True)
    def edit_aggregate(self):
        if not self.data:return self.info('Aggregate','Browse a CSV file first.')
        if not self.data_date_min:return self.info('Aggregate','No usable date/time field was detected.')
        d=AggregationDialog(self,self)
        if d.exec()==QDialog.Accepted:
            _,s,e,label=d.get_result(); self.aggregation_start=s; self.aggregation_end=e; self.agg.setText('Aggregate: '+label); self.generate_sites(True)
    def merge_rows(self,rows):
        groups={}; order=[]
        for r in rows:
            k=(str(r.get('siteid','')).upper(),get_edited_cellname(r),str(r.get('Band','')))
            if k not in groups: groups[k]=dict(r); order.append(k); [groups[k].__setitem__(b,safe_float(r.get(b,0))) for b in self.ta_profile['bins']]
            else:
                for b in self.ta_profile['bins']: groups[k][b]=safe_float(groups[k].get(b,0))+safe_float(r.get(b,0))
        return [groups[k] for k in order]
    def clear_charts(self):
        charts = list(self.current_charts)
        self.current_charts = []
        for c in charts:
            try:
                c.close_figure()
            except Exception:
                try:
                    fig = getattr(c, 'fig', None)
                    if fig is not None:
                        plt.close(fig)
                        c.fig = None
                except Exception:
                    pass
            c.setParent(None)
            c.deleteLater()
            QCoreApplication.processEvents()
        while self.cell_layout.count():
            it=self.cell_layout.takeAt(0)
            if it.widget():
                it.widget().deleteLater()
        QCoreApplication.processEvents()
    def generate_sites(self,rerender_only=False):
        if not self.data:return self.info('Generate','Browse a CSV file first.')
        sid=self.site_input_text.strip().upper()
        if not sid:return self.info('Generate','Enter one SiteID first.')
        if ',' in sid or ';' in sid:return self.info('Generate','Lite supports one SiteID only.')
        self.site_input_text=sid; self.clear_charts(); self.current_matched_rows=[]; QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            bands=set(self.selected_bands); sectors=set(self.selected_sectors); rows=[]
            source_rows=self._site_index.get(sid, [])
            for r in source_rows:
                if bands and str(r.get('Band','')).strip() not in bands:continue
                if sectors and f'Sector {get_sector_num(r)}' not in sectors:continue
                if self.aggregation_start and self.aggregation_end:
                    d=parse_begin_time_to_date(r.get('timestamp', r.get('Begin Time', '')),self._begin_time_fmt)
                    if d is None or not(self.aggregation_start<=d<=self.aggregation_end):continue
                rows.append(r)
            if not rows:return self.info('Generate',f'SiteID {sid} was not found with the current filters.')
            rows=self.merge_rows(rows); self.current_matched_rows=rows; self.update_filter_chips(); self.cell_layout.addWidget(QLabel(f'<b style="font-size:16px;color:#55b8ff;">Site : {sid} ({rows[0].get("sitename","-")})</b>')); grid=QGridLayout(); grid.setHorizontalSpacing(10); grid.setVerticalSpacing(10); holder=QWidget(); holder.setLayout(grid); self.cell_layout.addWidget(holder)
            for i,r in enumerate(sorted(rows,key=lambda x:(get_band_sort_num(x),get_sector_num(x)))):
                c=SingleTAChart(r,self); self.current_charts.append(c); rr,cc=divmod(i,3); grid.addWidget(c,rr,cc)
            self.cell_layout.addStretch(1)
        finally: QApplication.restoreOverrideCursor()

    def show_settings(self):
        d=QDialog(self); d.setWindowTitle(APP_NAME+' - Setting'); d.setMinimumSize(700,560); lay=QVBoxLayout(d); tabs=QTabWidget()
        c=QWidget(); cl=QVBoxLayout(c); cl.addWidget(QLabel('Cell Level Chart Setting'))
        b=QPushButton('Open Chart Setting'); b.setIcon(self._icon('common/analysis.svg')); b.clicked.connect(lambda:(d.accept(),self.open_chart_setting())); cl.addWidget(b)
        cl.addWidget(QLabel('Chart customization is available in Lite for the active Cell Level analysis.')); cl.addStretch(); tabs.addTab(c,'Chart Setting')
        t=QWidget(); tl=QVBoxLayout(t); tl.addWidget(QLabel('UI Theme'))
        for n in ['Default','Modern Dark','Light Professional','Warm Earth','Ocean Blue','High Contrast']:
            row=QHBoxLayout(); x=QPushButton(n); x.setIcon(self._icon('common/lock.svg')) if n!='Default' else None; x.setIconSize(QSize(14,14))
            if n=='Default': x.setText('Default  •  Included')
            else: x.setText(n+'  •  Pro'); x.clicked.connect(lambda _,nn=n:self.locked(nn+' Theme'))
            row.addWidget(x); row.addStretch(1); tl.addLayout(row)
        tl.addStretch(); tabs.addTab(t,'UI Theme')
        be=QWidget(); bl=QVBoxLayout(be); bl.addWidget(QLabel('Beam / Wedge Setting')); x=QPushButton('Beam View / Wedge  •  Pro'); x.setIcon(self._icon('common/lock.svg')); x.setIconSize(QSize(14,14)); x.clicked.connect(lambda:self.locked('Beam / Wedge Setting')); bl.addWidget(x); y=QPushButton('Elevation Profile  •  Pro'); y.setIcon(self._icon('common/lock.svg')); y.setIconSize(QSize(14,14)); y.clicked.connect(lambda:self.locked('Elevation Profile')); bl.addWidget(y); bl.addStretch(); tabs.addTab(be,'Beam / Wedge')
        lay.addWidget(tabs); close=QPushButton('Close'); close.clicked.connect(d.accept); lay.addWidget(close); d.exec()

    def open_chart_setting(self):
        d=ChartSettingDialog(self,self)
        if d.exec()==QDialog.Accepted:
            s=QSettings('JujunJ','TAAnalysisSuiteLite')
            for k in ['chart_font','chart_font_size','chart_font_color','chart_bar_color','chart_cdf_color','chart_fill_color','chart_grid_color','axis_max_labels','axis_rotation','axis_font_size']:s.setValue(k,getattr(self,k))
            if self.current_matched_rows:self.generate_sites(True)

    def _link_label(self,label,url):
        x=QLabel(f'<a href="{url}"><span style="color:#2980b9;">{label}</span></a>')
        x.setOpenExternalLinks(True)
        x.setTextFormat(Qt.RichText)
        pal=x.palette()
        try:
            link_role = QPalette.Link
            visited_role = QPalette.LinkVisited
        except AttributeError:
            link_role = QPalette.ColorRole.Link
            visited_role = QPalette.ColorRole.LinkVisited
        pal.setColor(link_role, QColor('#2980b9'))
        pal.setColor(visited_role, QColor('#2980b9'))
        x.setPalette(pal)
        x.setStyleSheet('font-size:11px;')
        x.setCursor(Qt.PointingHandCursor)
        return x

    def _open_url(self, url):
        try:
            webbrowser.open(url)
        except Exception:
            pass

    def _support_button(self, text, url):
        b=QPushButton(text)
        b.setCursor(Qt.PointingHandCursor)
        b.setMinimumHeight(30)
        b.clicked.connect(lambda _,u=url:self._open_url(u))
        return b

    def show_template_details(self):
        """Show concise bilingual notes for the TA.csv reference template."""
        d=QDialog(self)
        d.setWindowTitle('TA.csv Template — Reference Notes')
        d.setMinimumWidth(650)
        d.setMaximumWidth(760)
        d.setStyleSheet("QDialog{background:#ffffff;color:#263238;} QLabel{color:#263238;} QPushButton{min-height:30px;padding:5px 14px;} QFrame{border:1px solid #d9dee5;border-radius:5px;background:#f7f9fb;}")
        lay=QVBoxLayout(d); lay.setContentsMargins(24,20,24,18); lay.setSpacing(10)

        head=QHBoxLayout(); head.setSpacing(12)
        ico=QLabel(); ico.setPixmap(self._icon('common/info.svg').pixmap(QSize(38,38))); ico.setFixedSize(42,42); head.addWidget(ico)
        ht=QLabel('<b style="font-size:18px;color:#2f5f8f;">TA.csv Template</b><br><span style="font-size:12px;color:#66727f;">Reference structure for Universal TA Parser input</span>')
        ht.setTextFormat(Qt.RichText); head.addWidget(ht,1); lay.addLayout(head)

        box=QFrame(); bl=QVBoxLayout(box); bl.setContentsMargins(14,12,14,12); bl.setSpacing(7)
        en=QLabel('<b>English</b><br>The template is a reference for the required raw-data structure. The Universal TA Parser is <b>not limited to 15 TA ranges</b>; the number of TA ranges may differ by vendor or operator.<br><br><b>Required metadata:</b> Vendor, Longitude, Latitude, Azimuth, cellband, Sector, siteid, Band, Begin Time, End Time, sitename.<br><br><b>TA range columns:</b> use explicit metre ranges such as <b>0-156m, 156-234m, 234-546m</b>. The number and distance boundaries may differ, but the range-column format should remain standardized. If a source provides <b>TA0, TA1...</b> or cumulative values such as <b>156, 234, 546...</b>, normalize them to explicit ranges before using the CSV.')
        en.setWordWrap(True); en.setTextFormat(Qt.RichText); bl.addWidget(en)
        line=QFrame(); line.setFrameShape(QFrame.HLine); line.setStyleSheet('color:#d9dee5;background:#d9dee5;border:none;max-height:1px;'); bl.addWidget(line)
        idn=QLabel('<b>Bahasa Indonesia</b><br>Template ini adalah referensi struktur data mentah. Universal TA Parser <b>tidak dibatasi 15 range TA</b>; jumlah range dapat berbeda antar vendor atau operator.<br><br><b>Metadata wajib:</b> Vendor, Longitude, Latitude, Azimuth, cellband, Sector, siteid, Band, Begin Time, End Time, sitename.<br><br><b>Kolom range TA:</b> gunakan format jarak meter yang eksplisit seperti <b>0-156m, 156-234m, 234-546m</b>. Jumlah dan batas jaraknya boleh berbeda, tetapi format kolom range harus distandarkan. Jika sumber memberikan <b>TA0, TA1...</b> atau nilai kumulatif seperti <b>156, 234, 546...</b>, ubah terlebih dahulu menjadi range eksplisit sebelum digunakan.')
        idn.setWordWrap(True); idn.setTextFormat(Qt.RichText); bl.addWidget(idn)
        lay.addWidget(box)

        foot=QLabel('<span style="font-size:11px;color:#66727f;">The template is a structural reference, not a restriction on the number of TA ranges.</span>')
        foot.setWordWrap(True); lay.addWidget(foot)
        close=QPushButton('OK'); close.clicked.connect(d.accept); lay.addWidget(close,0,Qt.AlignCenter)
        d.exec()

    def show_about(self):
        """Jujun.J-style About dialog, matching the compact plugin-family layout."""
        msg = QMessageBox(self)
        msg.setWindowTitle(f"About {APP_NAME}")
        msg.setIcon(QMessageBox.Information)
        msg.setTextFormat(Qt.RichText)
        msg.setStyleSheet("""
            QMessageBox { background-color: #ffffff; color: #333333; }
            QMessageBox QLabel { color: #333333; background-color: transparent; }
            QMessageBox QPushButton {
                color: #333333; background-color: #ffffff;
                border: 1px solid #bdc3c7; border-radius: 3px;
                padding: 5px 18px; min-width: 70px; min-height: 24px;
            }
            QMessageBox QPushButton:hover { background-color: #f2f4f6; }
        """)

        text = (
            "<div style='font-family: Arial, sans-serif;'>"
            "<h2 style='color: #2c3e50; margin-bottom: 5px;'>TA Analysis Suite Lite</h2>"
            "<p style='color: #7f8c8d; margin-top: 0px; margin-bottom: 15px;'>"
            "Universal TA Parser and Single-Site Cell Level Analysis.</p>"

            "<table style='margin-bottom: 15px;' cellpadding='3'>"
            f"<tr><td width='70'><b>Version:</b></td><td>{VERSION}</td></tr>"
            f"<tr><td><b>Author:</b></td><td>{AUTHOR}</td></tr>"
            f"<tr><td><b>Contact:</b></td><td><a href='mailto:{EMAIL}' style='color: #2980b9; text-decoration: none;'>{EMAIL}</a></td></tr>"
            "</table>"
            "<hr style='border: 0; border-top: 1px solid #bdc3c7; margin-bottom: 15px;'>"
            "<div style='background-color: #fdf2f2; border-left: 4px solid #e74c3c; padding: 10px; margin-bottom: 15px;'>"


            "<p style='margin: 0 0 6px 0; color: #b9770e; font-size: 11px;'>"
            "<b>🚀 TA Analysis Suite Pro is now available</b></p>"
            "<p style='margin: 0 0 7px 0; font-size: 11px; color: #333;'>"
            "The Pro version adds Map View, Band Comparison, Before-After Analysis, Beam View, "
            "Elevation Profile, advanced themes, and other advanced RF analysis features."
            "</p>"
            "<p style='margin: 0 0 8px 0;'>"
            f"<a href='{PRO_VIDEO_URL}' style='text-decoration: none;'>"
            "<span style='background-color: #2980b9; color: white; padding: 6px 12px; border-radius: 4px; font-weight: bold; font-size: 11px;'>"
            "Watch Pro Video / Demo</span></a>"
            "</p>"
            "<p style='margin: 0 0 7px 0; font-size: 11px; color: #333;'>"
            "🌎 <b>For users worldwide:</b> Purchase TA Analysis Suite Pro via Gumroad:"
            "</p>"
            f"<p style='margin: 0 0 8px 0;'><a href='{GUMROAD_URL}' style='text-decoration: none;'>"
            "<span style='background-color: #ff5a36; color: white; padding: 6px 12px; border-radius: 4px; font-weight: bold; font-size: 11px;'>"
            "Click 👉 Get TA Analysis Suite Pro</span></a></p>"
            "<p style='margin: 8px 0 5px 0; font-size: 11px; color: #333;'>"
            "🇮🇩 <b>Untuk pengguna di Indonesia:</b> Purchase TA Analysis Suite Pro via Lynk.id:"
            "</p>"
            "<p style='margin: 0 0 8px 0;'>"
            f"<a href='{LYNK_ID_URL}' style='text-decoration: none;'>"
            "<span style='background-color: #ff5a36; color: white; padding: 6px 12px; border-radius: 4px; font-weight: bold; font-size: 11px;'>"
            "Click 👉 Get TA Analysis Suite Pro</span></a>"
            "</p>"
            "</div>"
            
            "<br><p style='font-size: 10px; color: #95a5a6; margin-top: 0px;'>"
            "<table cellpadding='3' cellspacing='0' border='0' style='margin-bottom: 10px;'>"
            "<tr>"
            "<td valign='middle' style='font-size: 11px; color: #333;'><b>TA.csv Template:</b></td>"
            f"<td valign='middle'><a href='{TA_TEMPLATE_URL}' style='color: #2980b9; text-decoration: none;'>Download Template</a></td>"
            "<td valign='middle' style='font-size: 14px;'>"
            "<a href='template_details' style='color: #2980b9; text-decoration: none;' title='View TA.csv template reference details'>ⓘ</a>"
            "</td>"
            "</tr>"
            "</table>"

            "<div style='background-color: #fdf2f2; border-left: 4px solid #e74c3c; padding: 10px; margin-bottom: 15px;'>"
            "<p style='margin: 0 0 5px 0; color: #c0392b; font-size: 11px;'><b>☕ Support &amp; Donate:</b></p>"
            "<p style='margin: 0 0 8px 0; font-size: 11px; color: #333;'>"
            "If TA Analysis Suite helps you save time in your RF work, consider supporting independent development."
            "</p>"
            "<table cellpadding='4' cellspacing='0' border='0'>"
            "<tr><td valign='middle' style='font-size: 11px; color: #333;'>Click 👉 : </td>"
            "<td valign='middle'><a href='https://saweria.co/juneth' style='text-decoration: none;'>"
            "<span style='background-color: #2ecc71; color: white; padding: 6px 12px; border-radius: 4px; font-weight: bold; font-size: 11px;'>Saweria (IDN)</span></a></td></tr>"
            "<tr><td valign='middle' style='font-size: 11px; color: #333;'>Click 👉 : </td>"
            "<td valign='middle'><a href='https://paypal.me/junjunan81' style='text-decoration: none;'>"
            "<span style='background-color: #0070ba; color: white; padding: 6px 12px; border-radius: 4px; font-weight: bold; font-size: 11px;'>Via PayPal</span></a></td></tr>"
            "<tr><td valign='middle' style='font-size: 11px; color: #333;'>Click 👉 : </td>"
            "<td valign='middle'><a href='https://buymeacoffee.com/juneth' style='text-decoration: none;'>"
            "<span style='background-color: #f39c12; color: white; padding: 6px 12px; border-radius: 4px; font-weight: bold; font-size: 11px;'>Buy me a coffee</span></a></td></tr>"
            "</table>"
            "</div>"

            "<br><p style='font-size: 10px; color: #95a5a6; margin-top: 10px;'>"
            "© 2023-2026 Jujun Junaedi. All Rights Reserved.</p>"
            "</div>"
        )

        msg.setText(text)

        for label in msg.findChildren(QLabel):
            try:
                if 'template_details' in label.text():
                    label.setOpenExternalLinks(False)
                    label.linkActivated.connect(lambda link: self.show_template_details() if link == 'template_details' else self._open_url(link))
            except Exception:
                pass

        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()
