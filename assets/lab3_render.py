from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch

base = Path(__file__).resolve().parent

# ---------- component diagram ----------
fig, ax = plt.subplots(figsize=(12.2, 8.8))
ax.set_xlim(0, 12)
ax.set_ylim(0, 9)
ax.axis('off')

ax.add_patch(Rectangle((0.45, 1.75), 11.05, 5.95, fill=False, edgecolor='#666666', lw=1.4))
ax.text(0.65, 7.55, 'Подсистема интеграции', fontsize=13, va='center')

boxes = {}
def add_box(key, x, y, w, h, label, ext=False, component=False):
    boxes[key] = (x, y, w, h)
    fc = 'white' if ext else '#f4f4f4'
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.03,rounding_size=0.08',
                                fc=fc, ec='#555555', lw=1.1))
    txt = f'«component»\n{label}' if component else label
    ax.text(x + w/2, y + h/2, txt, ha='center', va='center', fontsize=10)

def anchor(key, side):
    x, y, w, h = boxes[key]
    pts = {'l': (x, y+h/2), 'r': (x+w, y+h/2), 't': (x+w/2, y+h), 'b': (x+w/2, y)}
    return pts[side]

def connect(a, b, sa='b', sb='t', label='', dashed=False, rad=0.0):
    p, q = anchor(a, sa), anchor(b, sb)
    arrow = FancyArrowPatch(p, q, arrowstyle='-|>', mutation_scale=10.5,
                            lw=1.0, color='#555555',
                            linestyle='--' if dashed else '-',
                            connectionstyle=f'arc3,rad={rad}')
    ax.add_patch(arrow)
    if label:
        mx, my = (p[0]+q[0])/2, (p[1]+q[1])/2
        ax.text(mx, my+0.08, label, ha='center', va='bottom', fontsize=8.5,
                bbox=dict(fc='white', ec='none', pad=0.8))

add_box('operator', 0.8, 8.05, 3.2, 0.72, 'Оператор / разработчик', ext=True)
add_box('consumer', 7.95, 8.05, 2.9, 0.72, 'Онлайн-консультант', ext=True)
add_box('source', 0.75, 0.35, 3.1, 0.78, 'Внешний каталог\nAPI или файл', ext=True)
add_box('llm', 4.45, 0.35, 2.75, 0.78, 'Внешняя LLM\n(необязательна)', ext=True)
add_box('db', 8.35, 0.35, 2.45, 0.78, 'PostgreSQL', ext=True)

add_box('api', 3.65, 6.55, 3.1, 0.92, 'API и авторизация', component=True)
add_box('coord', 3.65, 5.2, 3.1, 0.92, 'Координатор импорта', component=True)
add_box('adapt', 0.95, 3.75, 2.7, 0.95, 'Адаптеры и\nпрофилирование', component=True)
add_box('match', 4.15, 3.75, 2.25, 0.95, 'Каскад\nсопоставления', component=True)
add_box('norm', 7.35, 3.75, 2.7, 0.95, 'Нормализация\nи валидация', component=True)
add_box('gateway', 0.95, 2.15, 2.9, 0.98, 'Шлюз LLM\nлимиты, тайм-ауты,\nфильтрация контекста', component=True)
add_box('repo', 5.1, 2.15, 4.35, 0.98, 'Слой хранения и аудита', component=True)

connect('operator', 'api', 'b', 't', 'управление', dashed=True)
connect('consumer', 'api', 'b', 't', 'чтение', dashed=True)
connect('api', 'coord', 'b', 't', 'запуск / продолжение')
connect('api', 'repo', 'r', 't', 'статус / выдача', dashed=True, rad=-0.15)
connect('coord', 'adapt', 'l', 't')
connect('coord', 'match', 'b', 't')
connect('coord', 'norm', 'r', 't')
connect('coord', 'repo', 'r', 't', 'состояние запуска', dashed=True, rad=0.08)
connect('adapt', 'source', 'b', 't', 'чтение', dashed=True)
connect('match', 'gateway', 'l', 't', 'сложные случаи')
connect('match', 'repo', 'b', 't', 'кандидаты / решения')
connect('norm', 'repo', 'b', 't', 'результаты / ошибки')
connect('gateway', 'llm', 'b', 't', 'контекст', dashed=True)
connect('repo', 'db', 'b', 't', 'хранение', dashed=True)

fig.savefig(base / 'lab3_components.png', dpi=170, bbox_inches='tight', facecolor='white')
plt.close(fig)

# ---------- sequence diagram ----------
fig, ax = plt.subplots(figsize=(13.5, 11.5))
ax.set_xlim(-0.6, 6.6)
ax.set_ylim(24, -1.2)
ax.axis('off')
actors = ['Оператор', 'API', 'Координатор', 'Адаптер', 'Сопоставление', 'Хранилище', 'Нормализация']
for x, name in enumerate(actors):
    ax.text(x, -0.45, name, ha='center', va='center', fontsize=10,
            bbox=dict(boxstyle='square,pad=0.35', fc='#f0f0f0', ec='#555555'))
    ax.plot([x, x], [0.15, 23.2], '--', color='#888888', lw=0.9)

for y, title in [(0.6, 'Запуск импорта'), (7.8, 'Сопоставление и ручная проверка'), (17.4, 'Завершение обработки')]:
    ax.plot([-0.35, 6.35], [y, y], color='#cccccc', lw=0.8)
    ax.text(-0.32, y-0.12, title, fontsize=9, ha='left', va='bottom', color='#555555')

messages = [
    (0,1,'POST /imports', 1.4),
    (1,2,'Проверить права и поставить запуск в очередь', 2.4),
    (2,5,'Создать ImportRun', 3.4),
    (2,3,'Прочитать и профилировать каталог', 4.4),
    (3,2,'Схема и данные', 5.4),
    (2,5,'Сохранить SchemaVersion и SourceAttribute', 6.4),
    (2,1,'run_id', 7.4),
    (1,0,'202 Accepted + run_id', 8.4),
    (0,1,'GET /imports/{id}', 10.0),
    (1,5,'Прочитать статус и кандидатов', 11.0),
    (5,1,'Статус и кандидаты', 12.0),
    (1,0,'Статус и кандидаты', 13.0),
    (2,4,'Сопоставить атрибуты', 14.0),
    (4,5,'Сохранить кандидатов / решения', 15.0),
    (4,2,'Есть спорные поля', 16.0),
    (0,1,'PATCH /mappings/{id}', 17.6),
    (1,5,'Сохранить решение оператора', 18.6),
    (1,2,'Продолжить после проверки', 19.6),
    (2,6,'Нормализовать и валидировать', 20.8),
    (6,5,'Сохранить продукты, ошибки и метрики', 21.8),
    (2,5,'Завершить ImportRun', 22.8),
]
for x1, x2, label, y in messages:
    ax.annotate('', xy=(x2, y), xytext=(x1, y),
                arrowprops=dict(arrowstyle='->', lw=1.05, color='#444444'))
    ax.text((x1+x2)/2, y-0.14, label, ha='center', va='bottom', fontsize=8.6,
            bbox=dict(fc='white', ec='none', pad=0.8))

ax.text(4.95, 16.5, 'повторяется, пока не\nрассмотрены спорные поля', fontsize=8,
        ha='center', va='center', bbox=dict(fc='white', ec='#bbbbbb', boxstyle='round,pad=0.25'))
ax.text(5.45, 21.1, 'включая llm_calls, tokens,\ncost, duration_ms', fontsize=8,
        ha='center', va='center', bbox=dict(fc='white', ec='#bbbbbb', boxstyle='round,pad=0.25'))

fig.savefig(base / 'lab3_sequence.png', dpi=170, bbox_inches='tight', facecolor='white')
plt.close(fig)

sequence_text = '\n'.join([
    'Оператор -> API: POST /imports',
    'API -> Координатор: Проверить права и поставить запуск в очередь',
    'Координатор -> Хранилище: Создать ImportRun',
    'Координатор -> Адаптер: Прочитать и профилировать каталог',
    'Адаптер -> Координатор: Схема и данные',
    'Координатор -> Хранилище: Сохранить SchemaVersion и SourceAttribute',
    'Координатор -> API: run_id',
    'API -> Оператор: 202 Accepted + run_id',
    'Оператор -> API: GET /imports/{id}',
    'API -> Хранилище: Прочитать статус и кандидатов',
    'Хранилище -> API: Статус и кандидаты',
    'API -> Оператор: Статус и кандидаты',
    'Координатор -> Сопоставление: Сопоставить атрибуты',
    'Сопоставление -> Хранилище: Сохранить кандидатов / решения',
    'Сопоставление -> Координатор: Есть спорные поля',
    'Оператор -> API: PATCH /mappings/{id}',
    'API -> Хранилище: Сохранить решение оператора',
    'API -> Координатор: Продолжить после проверки',
    'Координатор -> Нормализация: Нормализовать и валидировать',
    'Нормализация -> Хранилище: Сохранить продукты, ошибки и метрики',
    'Координатор -> Хранилище: Завершить ImportRun',
])
(base / 'lab3_sequence.txt').write_text(sequence_text, encoding='utf-8')
