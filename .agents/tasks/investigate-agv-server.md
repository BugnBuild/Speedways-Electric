# AGV Server — Codebase Investigation Report

## Summary

The Django AGV server project is functional in structure but contains **5 confirmed bugs** ranging from a critical `NameError` crash in `response()`, a misconfigured settings key (`STATICFILES_DIR` instead of `STATICFILES_DIRS`), a broken JS `<script>` tag in `Map.html`, and two minor logic issues. No templates are missing — every template referenced in views exists on disk. The static files are all present. The core issue most likely to cause an immediate runtime crash is the use of the bare name `id` (a Python builtin) instead of `data['AGV_ID']` inside the `response()` function.

---

## 1. URL Configuration

### `ui/urls.py` (root URLconf)
```
path('admin/', admin.site.urls)
path('',       include('Map_generation.urls'))
```
All app URLs are delegated to `Map_generation/urls.py`.

### `Map_generation/urls.py` (app URLconf)
| URL pattern          | View function       | Name              |
|----------------------|---------------------|-------------------|
| `''`                 | `views.map1`        | `home-page`       |
| `generate_map`       | `views.maps_detail` | *(no name)*       |
| `node_details_save`  | `views.node_details_save` | `node_detail_save` |
| `shortest_dist`      | `views.shortest_dist` | `shortest_dist` |
| `agvreq`             | `views.agvreq`      | `agvreq`          |
| `agvstat`            | `views.agvstat`     | `agvstat`         |
| `regagv`             | `views.regagv`      | `regagv`          |

All 7 patterns are well-formed. No missing `path()` entries.

---

## 2. View Functions

All views are defined in `Map_generation/views.py`.

| View function      | Template rendered                          | Notes                        |
|--------------------|--------------------------------------------|------------------------------|
| `map1`             | `Map_generation/home page.html`            | Home page; static files used |
| `maps_detail`      | `Map_generation/Map.html` (GET), `Map_generation/Map2.html` (POST) | Map generation form |
| `node_details_save`| `Map_generation/Map2.html`                 | Returns `HttpResponse` when tot==1 |
| `shortest_dist`    | `Map_generation/Map3.html`                 | Server start/stop + task assign |
| `agvreq`           | `Map_generation/agvreq.html`               | View requests from AGVs      |
| `agvstat`          | `Map_generation/list.html`                 | AGV status list              |
| `regagv`           | `Map_generation/registeragv.html` (GET), `Map_generation/Done.html` (POST) | Register AGV |

Helper functions (not views): `create_socket`, `bind_socket`, `make_edge`, `Graph`, `path`, `auto_assign`, `threaded_client`, `assign_task`, `response`, `main`, `start_server`, `stop_server`.

---

## 3. Templates Under `Map_generation/templates/Map_generation/`

| File                  | Renders for view     | `{% load static %}` present |
|-----------------------|----------------------|-----------------------------|
| `home page.html`      | `map1`               | ✅ Yes                       |
| `Map.html`            | `maps_detail` (GET)  | ✅ Yes                       |
| `Map2.html`           | `maps_detail` (POST), `node_details_save` | ✅ Yes |
| `Map3.html`           | `shortest_dist`      | ✅ Yes                       |
| `agvreq.html`         | `agvreq`             | ✅ Yes                       |
| `list.html`           | `agvstat`            | ✅ Yes                       |
| `registeragv.html`    | `regagv` (GET)       | ✅ Yes                       |
| `Done.html`           | `regagv` (POST)      | ✅ Yes                       |

**8 templates total — all present.**

---

## 4. Does the `agvstat` Template Exist?

Yes. The `agvstat` view (URL: `/agvstat`, name: `agvstat`) renders **`Map_generation/list.html`**, which exists at:
```
Map_generation/templates/Map_generation/list.html
```
No `agvstat.html` file is needed — the view uses `list.html` as the AGV status page.

---

## 5. Static Files in the Home Template

`home page.html` opens with `{% load static %}` on line 1 — correct.

Static file references:
```
{% static 'css/bootstrap.css' %}
{% static 'css/normalize.css' %}
{% static 'css/component.css' %}
{% static 'css/custom-styles.css' %}
{% static 'css/demo.css' %}
{% static 'img/banner-image.jpg' %}
{% static 'img/img1.jpg' %}
{% static 'img/status.png' %}
{% static 'img/img3.png' %}
{% static 'img/img4.png' %}
{% static 'img/reg.png' %}
```

All of these files **exist** in `Map_generation/static/`. No missing static files for the home template.

---

## 6. `settings.py` — Key Configuration

### INSTALLED_APPS
```python
'django.contrib.admin',
'django.contrib.auth',
'django.contrib.contenttypes',
'django.contrib.sessions',
'django.contrib.messages',
'django.contrib.staticfiles',
'Map_generation.apps.MapGenerationConfig',
```
`django.contrib.staticfiles` is present. `Map_generation` registered via its `AppConfig` — correct.

### Static files
```python
STATIC_URL = '/static/'

STATICFILES_DIR = [                            # ← BUG: wrong key name
    os.path.join(BASE_DIR, 'Map_generation/static')
]
```
`STATICFILES_DIR` is **not a recognised Django setting**. The correct key is `STATICFILES_DIRS` (plural). Because `APP_DIRS: True` is set and `Map_generation/static/` is inside the app directory, Django's `AppDirectoriesFinder` will still find static files at runtime — so this bug is silent in development. However if `collectstatic` is ever run, the custom directory listed here will not be collected.

### TEMPLATES
```python
'BACKEND': 'django.template.backends.django.DjangoTemplates',
'DIRS': [],
'APP_DIRS': True,
```
`APP_DIRS: True` makes Django look for templates in each app's `templates/` subdirectory automatically. `DIRS: []` is fine because templates are app-local. This is correct.

---

## 7. Missing Templates Check

Cross-referencing every `render(request, '<template>')` call in `views.py` against the files on disk:

| Template path called in view          | Exists on disk? |
|---------------------------------------|-----------------|
| `Map_generation/home page.html`       | ✅ Yes           |
| `Map_generation/Map.html`             | ✅ Yes           |
| `Map_generation/Map2.html`            | ✅ Yes           |
| `Map_generation/Map3.html`            | ✅ Yes           |
| `Map_generation/agvreq.html`          | ✅ Yes           |
| `Map_generation/list.html`            | ✅ Yes           |
| `Map_generation/registeragv.html`     | ✅ Yes           |
| `Map_generation/Done.html`            | ✅ Yes           |

**No missing templates.** All 8 templates referenced in views exist.

---

## 8. Models (`models.py`)

| Model         | Fields                                                            |
|---------------|-------------------------------------------------------------------|
| `Maps`        | `nodes` (IntegerField), `stations` (IntegerField)                 |
| `Node_details`| `current`, `right`, `left`, `straight` (CharField), `ldist`, `rdist`, `sdist` (IntegerField, nullable) |
| `Short`       | `start`, `dest` (CharField, nullable)                             |
| `Regagv`      | `agvsname`, `agvsid` (CharField, nullable)                        |

All models are clean. Unused import in `models.py`: `F`, `Sum`, `Value`, `Coalesce` from `django.db.models` — not harmful but unnecessary.

---

## 9. Bugs Found

### BUG 1 — Critical: `NameError` in `response()` (`views.py`, line ~294)

```python
def response(data, connection):
    ...
    agv_status[id]['OBJECT'].sendall(...)   # ← uses Python builtin `id`, not data['AGV_ID']
```

`id` here refers to Python's built-in `id()` function, not an AGV identifier. This will raise a `TypeError` at runtime because `id` is a function, not a string/dict key. The correct variable is `data['AGV_ID']`.

**Fix:** Replace `agv_status[id]['OBJECT']` with `agv_status[data['AGV_ID']]['OBJECT']`.

---

### BUG 2 — Settings: `STATICFILES_DIR` typo (`settings.py`, line ~20)

```python
STATICFILES_DIR = [...]    # ← should be STATICFILES_DIRS
```

Django ignores unknown settings silently. The correct name is `STATICFILES_DIRS`. While `APP_DIRS` prevents a visible runtime failure, `collectstatic` will skip this directory.

**Fix:** Rename `STATICFILES_DIR` → `STATICFILES_DIRS`.

---

### BUG 3 — Broken script tag in `Map.html`

```html
<scripts src ="{% static 'js/jquery-1.7.1.min' %}" ></scripts>
```

Two problems:
1. The tag is `<scripts>` instead of `<script>` — browsers will not execute it.
2. The filename is `jquery-1.7.1.min` with no `.js` extension, while the actual file is `jquery-1.7.1.min.js`.

**Fix:** `<script src="{% static 'js/jquery-1.7.1.min.js' %}"></script>`

---

### BUG 4 — Duplicate import in `views.py` (line 9–10)

```python
from collections import deque, namedtuple
from collections import deque, namedtuple    # ← exact duplicate
```

Not a crash, but dead code that should be cleaned up.

**Fix:** Remove the duplicate import line.

---

### BUG 5 — `agvreq` view ignores its own POST logic

```python
def agvreq(request):
    if request.method == 'POST':
        start_server()              # always starts server on POST, no condition check
    return render(request, 'Map_generation/agvreq.html')
```

The view calls `start_server()` unconditionally on any POST, but the template's button is labelled "Assign task to requested AGV". The server-start logic here appears to be a copy-paste artifact; there is no task-assignment logic implemented. This is likely unfinished, not a crash-level bug, but a logic gap.

---

### BUG 6 — `response()` guard condition is always truthy

```python
def response(data, connection):
    if data['START']:
        ...
```

If `data` does not contain a `'START'` key, this raises a `KeyError`. There is no `.get()` fallback. Combined with Bug 1, `response()` is unreliable.

**Fix:** Use `if data.get('START'):` to safely handle missing keys.

---

## Conclusions and Recommendations

| Priority | Issue                                                 | File            | Action                                              |
|----------|-------------------------------------------------------|-----------------|-----------------------------------------------------|
| P1       | `id` used instead of `data['AGV_ID']` in `response()`| `views.py` ~294 | Replace `agv_status[id]` → `agv_status[data['AGV_ID']]` |
| P2       | `STATICFILES_DIR` typo in settings                   | `settings.py`   | Rename to `STATICFILES_DIRS`                        |
| P2       | `<scripts>` tag + missing `.js` extension            | `Map.html`      | Fix tag name and filename                           |
| P3       | `data['START']` KeyError risk in `response()`         | `views.py` ~289 | Use `data.get('START')`                             |
| P3       | `agvreq` view logic is a stub                        | `views.py` ~250 | Implement actual request-assignment logic           |
| P4       | Duplicate `from collections import` line             | `views.py` line 9-10 | Remove duplicate                              |
| P4       | Unused model imports (`F`, `Sum`, etc.)              | `models.py`     | Remove unused imports                               |

The project will load and serve pages correctly because templates, static files, and URL patterns are all properly wired. The socket server functionality will crash as soon as an AGV sends a message that triggers `response()` due to Bug 1.
