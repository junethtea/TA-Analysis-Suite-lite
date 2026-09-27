# TA Analysis Suite Lite 📡📊

[![QGIS](https://img.shields.io/badge/QGIS-3.4%20%7C%204.x-589632?logo=qgis&logoColor=white)](https://qgis.org/) [![Version](https://img.shields.io/badge/version-1.0.0-2f5f8f)](https://github.com/junethtea/TA-Analysis-Suite-lite/releases) [![License](https://img.shields.io/badge/license-GPL--2.0--or--later-green)](LICENSE) [![Repository](https://img.shields.io/badge/GitHub-TA--Analysis--Suite--Lite-181717?logo=github)](https://github.com/junethtea/TA-Analysis-Suite-lite)

> *"Sebaik-baiknya Manusia adalah yang bermanfaat bagi sesama."*

**TA Analysis Suite Lite** is a focused QGIS plugin for **Timing Advance (TA) analysis** from raw CSV data. It is designed for RF engineers, RF post-processing workflows, and GIS/QGIS users who need a practical **single-site Cell Level TA analysis** workflow without the advanced spatial and comparison modules included in the Pro edition.

---

## 🧭 Quick Navigation

- [📖 Overview](#-overview)
- [✨ Lite Features](#-lite-features)
- [📡 Universal TA Parser](#-universal-ta-parser)
- [📊 Cell Level Analysis](#-cell-level-analysis)
- [🎛️ Filters & Chart Settings](#️-filters--chart-settings)
- [🔒 Pro Edition](#-pro-edition-upgrade-required)
- [🚀 How to Use](#-how-to-use)
- [📄 TA.csv Template](#-tacsv-template)
- [⚡ Performance](#-performance)
- [🖥️ Compatibility](#️-compatibility)
- [☕ Support & Donate](#-support--donate)
- [👤 Author](#-author)

---

## 📖 Overview

TA Analysis Suite Lite provides a lightweight workflow for turning raw Timing Advance CSV data into a readable Cell Level distribution analysis inside QGIS.

The Lite edition is intentionally focused on one core workflow:

**Load CSV → detect TA structure → select one site → filter → generate Cell Level charts → inspect TA distribution and CDF.**

The parser is designed to work with different TA range structures rather than assuming a fixed number of TA bins. Vendor-specific profiles such as **Ericsson** and **ZTE** can be recognized from the available source data and TA range definitions.

---

## ✨ Lite Features

- **Universal TA CSV Parser** — Automatically detects common metadata fields and available TA distance-range columns.
- **Single-Site Analysis** — Focused on one SiteID at a time for a clean RF post-processing workflow.
- **Cell Level TA Distribution** — Generates individual charts for the cells available at the selected site.
- **TA Bar + CDF Visualization** — TA sample bars are combined with a cumulative distribution function (CDF) line.
- **Interactive Tooltips** — Hover over TA bars to inspect the corresponding range and sample count.
- **Ericsson & ZTE Support** — Supports different TA range structures rather than forcing one universal fixed-bin layout.
- **Site / Vendor / Band / Sector Filters** — Narrow the analysis to the required network scope.
- **Threshold Analysis** — Configure the TA percentage threshold used by the Cell Level result.
- **Aggregate Control** — Select the available aggregate/date scope supported by the loaded source data.
- **Chart Customization** — Configure chart font, font size, colors, grid, axis rotation and related visualization settings.
- **Dark UI** — Designed for a compact RF engineering workflow with a dark interface and readable chart styling.
- **QGIS 3.x / 4.x Compatibility** — Uses the QGIS PyQt compatibility layer for the supported QGIS range.

---

## 📡 Universal TA Parser

TA Analysis Suite Lite does **not** require the raw CSV to contain exactly 15 TA ranges.

The parser detects the TA range fields available in the source data and builds the analysis profile from the actual CSV structure. This is particularly useful when different vendors or source systems use different TA bin definitions.

### Supported source examples

- **ZTE-style ranges** such as `0-78m`, `78-234m`, `234-390m`, and longer distance ranges.
- **Ericsson-style ranges** such as `0.0 - 0.078`, `0.078 - 0.156`, `0.156 - 0.234`, and extended ranges above 10 km.

Keep the original TA fields from the source system whenever possible. Do not rename or manually reshape TA range columns simply to match an example template.

### Required metadata

The recommended metadata fields are:

- `Vendor`
- `Longitude`
- `Latitude`
- `Azimuth`
- `cellband`
- `Sector`
- `siteid`
- `Band`
- `Begin Time`
- `End Time`
- `sitename`

`Begin Time` and `End Time` should contain valid date/time values when date-based filtering or aggregate selection is required.

For the detailed bilingual CSV structure reference, see [`TA_CSV_Template_Notes_EN_ID.txt`](TA_CSV_Template_Notes_EN_ID.txt).

---

## 📊 Cell Level Analysis

The main Lite dashboard is intentionally centered on **Cell Level** analysis.

For each selected cell, the chart can show:

- TA distance ranges on the X-axis
- Sample count on the primary Y-axis
- CDF percentage on the secondary Y-axis
- TA 85% distance summary in the chart title
- Interactive bar tooltips

The CDF line is rendered above the bars so both distributions remain visible when the chart contains many TA bins.

---

## 🎛️ Filters & Chart Settings

The Lite interface provides the controls needed for the single-site workflow:

| Control | Purpose |
| --- | --- |
| **Site** | Select the single SiteID to analyze. |
| **Vendor** | Auto-detect or select the available vendor scope. |
| **Band** | Analyze all available bands or a selected LTE band. |
| **Sector** | Narrow the analysis to a selected sector. |
| **Threshold** | Configure the TA percentage threshold used for the result. |
| **Aggregate** | Select the available date/aggregate scope. |
| **Chart Settings** | Adjust chart appearance including font, colors, grid and axis rotation. |

The current chart configuration uses a **90° X-axis label rotation** for better readability when a source contains many TA bins.

---

## 🔒 Pro Edition (Upgrade Required)

TA Analysis Suite Lite intentionally does **not** contain the implementation of the advanced Pro modules.

The Lite interface may show locked navigation controls for the Pro edition, but those controls are **visual placeholders only**. The corresponding Pro feature implementations are not embedded in the Lite source.

The Pro edition adds advanced workflows such as:

- **🗺️ Map View**
- **📊 Band Comparison**
- **↔️ Before-After by Cell**
- **↔️ Before-After by Band**
- **📡 Beam View**
- **⛰️ Elevation Profile & TA Distribution**
- **🔄 Update Azimuth**
- **📋 Data Table and Summary workflows**
- **🎨 Professional themes and advanced visualization workflows**
- **📤 Advanced export/reporting capabilities**

### Get TA Analysis Suite Pro

- 🌎 **Global Users:** [Purchase via Gumroad](https://gumroad.com/juneth)
- 🇮🇩 **Indonesia:** [Purchase via Lynk.id](https://lynk.id/kangjun)
- 🎥 **Pro Video / Demo:** [Watch the Pro demonstration](https://youtu.be/fEZy4M0M9p8?si=w-zLYZ-n3WtJEa2z)

---

## 🚀 How to Use

### 1. Load the CSV

Open TA Analysis Suite Lite from QGIS and use **Browse** to select the raw TA CSV file.

The parser reads the source structure and detects the available metadata and TA range fields.

### 2. Select one site

Lite is intentionally a **single-site** analysis tool. Enter or select the required SiteID.

### 3. Generate the analysis

Click **Generated** to build the Cell Level charts for the selected site.

### 4. Apply filters

Use Vendor, Band, Sector, Threshold and Aggregate controls to narrow the analysis.

### 5. Inspect the charts

Hover over a TA bar to view its TA range and sample count. The orange CDF line provides the cumulative distribution on the secondary axis.

### 6. Clear the current analysis

Use **Clear** to remove the generated Cell Level charts and return the workspace to an empty state.

---

## 📄 TA.csv Template

The TA CSV template is provided as a **reference structure**, not as a fixed limitation on the number of TA ranges.

- 📥 [Download TA.csv Template](https://drive.google.com/drive/folders/1DFhfw20mtoNP8x1slHTApGS6gNpahrFy?usp=sharing)
- 📘 [Read the bilingual TA.csv Template Notes](https://drive.google.com/drive/folders/1DFhfw20mtoNP8x1slHTApGS6gNpahrFy?usp=sharing)

Keep the original TA range columns from your source system. The Universal TA Parser is designed to detect the available range structure automatically.

---

## ⚡ Performance

The Lite loader is optimized for large raw TA CSV workflows by minimizing repeated full-data scans and building reusable indexes during loading.

The loading workflow is designed around:

- Single-pass CSV reading where possible
- Canonical field mapping during ingestion
- Site indexing for faster single-site generation
- Cached date parsing for repeated timestamp values
- Vendor, band and sector indexing for filtering
- Event processing during large CSV reads to keep the QGIS interface responsive

Actual loading time depends on CSV size, row count, storage speed, QGIS/Python environment and source structure.

---

## 🖥️ Compatibility

| Component | Supported |
| --- | --- |
| **QGIS** | 3.4 through 4.x |
| **Python** | QGIS bundled Python environment |
| **Matplotlib** | Required |
| **NumPy** | Required |
| **License** | GPL-2.0-or-later |

The plugin uses the QGIS PyQt compatibility layer to support both the QGIS 3.x and QGIS 4.x generation of Qt bindings.

---

## 📦 Installation

### From ZIP

1. Download the latest plugin ZIP release.
2. Open **QGIS → Plugins → Manage and Install Plugins**.
3. Select **Install from ZIP**.
4. Choose the downloaded TA Analysis Suite Lite ZIP.
5. Enable the plugin from the Installed Plugins list.

### From the QGIS Official Plugin Repository

Once published, TA Analysis Suite Lite can be installed directly from the QGIS Plugin Manager.

---

## ☕ Support & Donate

TA Analysis Suite Lite is developed as an independent tool for RF engineering and QGIS workflows. If it saves you time in daily analysis or post-processing work, support is greatly appreciated.

- 🇮🇩 **Indonesia:** [Donate via Saweria](https://saweria.co/juneth)
- 🌎 **Global:** [Buy me a coffee](https://buymeacoffee.com/juneth)
- 💳 **PayPal:** [paypal.me/junjunan81](https://paypal.me/junjunan81)

Your support helps fund continued development, testing and maintenance across QGIS versions and telecom data formats.

---

## 👤 Author

**Jujun Junaedi**  
RF Engineer | RF Post-Processing | GIS & QGIS Enthusiast

- 📧 Email: [dev.qgis.plugin@gmail.com](mailto:dev.qgis.plugin@gmail.com)
- 💻 GitHub: [github.com/junethtea](https://github.com/junethtea)
- 📦 TA Analysis Suite Lite: [GitHub Repository](https://github.com/junethtea/TA-Analysis-Suite-lite)

---

## 📜 License

TA Analysis Suite Lite is released under the **GNU General Public License v2.0 or later**.

See [`LICENSE`](LICENSE) for the full license text.

---

> *"Sebaik-baiknya Manusia adalah yang bermanfaat bagi sesama."*

---

by **Jujun Junaedi** | © 2023–2026
