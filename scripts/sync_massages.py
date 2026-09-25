#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sync all 16 massages from old-site data into the multipage deploy."""
from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / ".firecrawl" / "massages-raw.json"
ASSETS = ROOT / "assets"
ORIGIN = "https://pattaya-massage.ru"
CACHE_BUST = "20260924-massages16"

ICON_ARROW = (
    '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="1.25" stroke-linecap="round" stroke-linejoin="round" '
    'aria-hidden="true" focusable="false"><path d="M4 12h16m-6-6 6 6-6 6"/></svg>'
)
ICON_DIAG = (
    '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="1.25" stroke-linecap="round" stroke-linejoin="round" '
    'aria-hidden="true" focusable="false"><path d="M5 19 19 5M5 5h14v14"/></svg>'
)
ICON_PLUS = (
    '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="1.25" stroke-linecap="round" stroke-linejoin="round" '
    'aria-hidden="true" focusable="false"><path d="M4 12h16M12 4v16"/></svg>'
)

# Curated copy in the new site voice (no medical claims).
CURATED = {
    928217006382: {
        "id": "candle",
        "slug": "massazh-tayushchey-svechoy",
        "title": "Прикосновение тающей свечи",
        "caption": "Тёплое прикосновение и ароматерапия.",
        "time": "70 минут",
        "image": "service-candle",
        "keep_image": True,
        "headline": "Тепло свечи и неспешный ритм",
        "lead": "Ритуал, в котором массаж дополняют ароматерапия и тепло тающей массажной свечи.",
        "body": [
            "Прикосновение тающей свечи в «Паттайе» — отдельный сеанс с ароматом и мягким теплом. Это не длинная SPA-программа из нескольких этапов, а церемония отдыха: приглушённый свет, тёплый воск из массажной свечи и внимание мастера.",
            "В меню указана стоимость 4 300 ₽ за сеанс 70 минут. Перед записью администратор подтвердит доступность и ваши пожелания по аромату.",
        ],
        "fit": "Если хочется совместить массаж с теплом и ароматом в одном спокойном ритуале.",
        "steps": ["Массаж с тающей свечой", "Ароматерапия", "Сеанс 70 минут"],
        "faq": [
            ("Насколько горячий воск?", "Массажные свечи плавятся при комфортной температуре. Если вы пробуете процедуру впервые, расскажите об этом администратору."),
            ("Это подарочный вариант?", "Да, такой формат часто выбирают для особенного повода или сертификата."),
        ],
    },
    156645439592: {
        "id": "oil",
        "slug": "tayskiy-oyl-massazh",
        "title": "Тайский ойл-массаж",
        "caption": "Мягкие техники. Ароматные масла.",
        "time": "от 60 минут",
        "image": "service-oil",
        "keep_image": True,
        "headline": "Масла, тайские техники и внимание к ощущениям",
        "lead": "Сочетание традиционных тайских техник и массажа с маслами.",
        "body": [
            "Тайский ойл-массаж в «Паттайе» — вариант для тех, кто ищет отдельный сеанс с маслами, а не длинную программу из нескольких SPA-этапов.",
            "В меню есть три продолжительности: 60 минут — 3 500 ₽, 90 минут — 4 700 ₽, 120 минут — 6 500 ₽. Перед записью администратор уточнит удобный вариант.",
        ],
        "fit": "Если хочется выбрать массаж с маслами как самостоятельную процедуру и заранее обсудить продолжительность.",
        "steps": [
            "Тайские массажные техники",
            "Использование масел",
            "Варианты: 60 / 90 / 120 минут",
        ],
        "faq": [
            ("Сколько длится ойл-массаж?", "Доступны сеансы 60, 90 и 120 минут. Цена зависит от выбранной продолжительности."),
            ("Чем разовый сеанс отличается от абонемента?", "Разовый сеанс — для одного посещения. Абонемент на тайский ойл-массаж включает 5, 7 или 10 встреч по 60 минут."),
        ],
    },
    620943645202: {
        "id": "tandem",
        "slug": "massazh-v-chetyre-ruki",
        "title": "Тандем. В четыре руки",
        "caption": "Два мастера. Единый ритм.",
        "time": "от 30 минут",
        "image": "service-tandem",
        "keep_image": True,
        "headline": "Два мастера работают одновременно",
        "lead": "Массаж, во время которого два мастера работают синхронно.",
        "body": [
            "Формат «в четыре руки» создаёт ощущение единого ритма: два специалиста ведут сеанс одновременно.",
            "В меню: 30 минут — 4 200 ₽, 60 минут — 6 400 ₽. Итоговую длительность подтверждают при записи.",
        ],
        "fit": "Если хочется более насыщенного сеанса и синхронной работы двух мастеров.",
        "steps": [
            "Одновременная работа двух мастеров",
            "Синхронные массажные техники",
            "Варианты: 30 / 60 минут",
        ],
        "faq": [
            ("Нужно ли записываться заранее?", "Да: для формата нужны два свободных мастера в одно время."),
            ("Можно ли прийти вдвоём?", "Этот сеанс — для одного гостя. Совместные программы собраны в разделе «Для двоих»."),
        ],
    },
    303981314862: {
        "id": "juniper",
        "slug": "massazh-mozhzhevelovymi-sharikami",
        "title": "Массаж с можжевеловыми шариками",
        "caption": "Особенный ритуал «Паттайи».",
        "time": "90 минут",
        "image": "service-juniper",
        "keep_image": True,
        "headline": "Авторская программа с можжевеловыми шариками",
        "lead": "Массажная программа салона «Паттайя» с можжевеловыми шариками.",
        "body": [
            "Процедура с особой фактурой: мастер работает можжевеловыми шариками в неспешном ритме. Это фирменный формат салона.",
            "В меню: 4 900 ₽ за сеанс 90 минут.",
        ],
        "fit": "Если хочется попробовать авторскую программу салона, а не классический ойл-массаж.",
        "steps": [
            "Массаж с можжевеловыми шариками",
            "Сеанс 90 минут",
            "Детали уточняются у администратора",
        ],
        "faq": [
            ("Чем это отличается от обычного массажа?", "Главное отличие — работа с можжевеловыми шариками и более длинный формат сеанса."),
            ("Есть ли похожая SPA-программа?", "Да, посмотрите «Шёпот можжевельника» в разделе SPA-программ."),
        ],
    },
    249832099112: {
        "id": "oranges",
        "slug": "massazh-goryachimi-apelsinami",
        "title": "Массаж горячими апельсинами",
        "caption": "Цитрусовое тепло и аромат.",
        "time": "70 минут",
        "image": "service-oranges",
        "headline": "Тёплые апельсины и тонизирующий ритм",
        "lead": "Массаж с горячими апельсинами — аромат, тепло и мягкая проработка тела.",
        "body": [
            "В «Паттайе» эту процедуру часто называют сочным перерывом: мастер работает с тёплыми апельсинами, и сеанс наполняется цитрусовым ароматом.",
            "В меню: 4 200 ₽ за 70 минут. Перед записью уточните пожелания и возможные ограничения по ароматам.",
        ],
        "fit": "Если хочется необычного формата с теплом и ярким ароматом.",
        "steps": ["Массаж с горячими апельсинами", "Ароматерапия", "Сеанс 70 минут"],
        "faq": [
            ("Будет ли сильный запах цитруса?", "Аромат заметный и тёплый. Если вы чувствительны к эфирным маслам, скажите об этом заранее."),
            ("Это длинная SPA-программа?", "Нет, это отдельный массажный сеанс на 70 минут."),
        ],
    },
    589416178562: {
        "id": "balinese",
        "slug": "baliyskiy-massazh",
        "title": "Балийский массаж",
        "caption": "Ароматы, плавные техники, глубокое расслабление.",
        "time": "от 60 минут",
        "image": "service-balinese",
        "headline": "Балийские техники и работа с маслами",
        "lead": "Традиционный индонезийский подход: плавные движения, ароматерапия и внимание ко всему телу.",
        "body": [
            "Балийский массаж выбирают, когда хочется мягкого, но собранного сеанса с маслами и спокойным ритмом.",
            "Варианты: 60 минут — 3 500 ₽, 90 минут — 4 700 ₽, 120 минут — 6 500 ₽.",
        ],
        "fit": "Если близок спокойный масляный массаж с акцентом на расслабление.",
        "steps": [
            "Балийские массажные техники",
            "Ароматерапия и масла",
            "Варианты: 60 / 90 / 120 минут",
        ],
        "faq": [
            ("Чем отличается от тайского ойл-массажа?", "Оба формата с маслами, но техники и ритм разные. Администратор поможет выбрать по ощущениям."),
            ("Какую длительность выбрать впервые?", "Чаще начинают с 60 минут, затем при желании увеличивают время."),
        ],
    },
    105759472652: {
        "id": "herbal",
        "slug": "massazh-travyanymi-meshkami",
        "title": "Массаж травяными мешками",
        "caption": "Тёплая фактура трав и специй.",
        "time": "60 минут",
        "image": "service-herbal",
        "headline": "Тёплые травяные мешочки вместо привычных рук",
        "lead": "Сеанс, в котором мастер работает специальными мешочками с травами и специями.",
        "body": [
            "Травяные мешочки добавляют сеансу тепло и аромат. Формат знаком по тайским и индонезийским традициям и хорошо подходит как самостоятельная процедура.",
            "В меню: 3 800 ₽ за 60 минут.",
        ],
        "fit": "Если хочется мягкого тепла и аромата трав в одном сеансе.",
        "steps": ["Массаж травяными мешочками", "Сеанс 60 минут"],
        "faq": [
            ("Мешочки горячие?", "Они тёплые и комфортные. Если у вас чувствительная кожа, предупредите администратора."),
            ("Можно ли совместить с пилингом?", "Да, такие сочетания есть в SPA-программах — посмотрите раздел SPA."),
        ],
    },
    412007548192: {
        "id": "stones",
        "slug": "massazh-goryachimi-kamnyami",
        "title": "Массаж горячими камнями",
        "caption": "Гладкие камни и глубокое тепло.",
        "time": "60 минут",
        "image": "service-stones",
        "headline": "Тепло камней и медленный ритм",
        "lead": "Массаж с гладкими нагретыми камнями для тех, кто любит ощущение глубокого тепла.",
        "body": [
            "Камни помогают держать спокойный, прогревающий темп сеанса. Это отдельная массажная программа на час.",
            "В меню: 3 800 ₽ за 60 минут.",
        ],
        "fit": "Если хочется прогревающего формата и неспешного расслабления.",
        "steps": ["Массаж горячими камнями", "Сеанс 60 минут"],
        "faq": [
            ("Камни не обжигают?", "Температуру подбирают комфортной. Сообщите, если предпочитаете более мягкое тепло."),
            ("Есть ли акционные сочетания?", "Иногда камни входят в сезонные предложения — уточняйте у администратора."),
        ],
    },
    408507949902: {
        "id": "feet",
        "slug": "massazh-nog",
        "title": "Массаж ног",
        "caption": "Лёгкость после долгого дня.",
        "time": "от 30 минут",
        "image": "service-feet",
        "headline": "Отдельное внимание стопам и ногам",
        "lead": "Короткий или часовой сеанс для тех, кому хочется снять усталость ног.",
        "body": [
            "Массаж ног — самостоятельная процедура, которую удобно выбрать после рабочего дня или в дополнение к другому уходу.",
            "Варианты: 30 минут — 2 200 ₽, 60 минут — 3 400 ₽.",
        ],
        "fit": "Если ноги устали от дня на каблуках, в зале или в дороге.",
        "steps": ["Массаж ног и стоп", "Варианты: 30 / 60 минут"],
        "faq": [
            ("Можно ли добавить к основной программе?", "Да, часто выбирают как дополнение. Состав подтвердят при записи."),
            ("Делают ли только стопы?", "Работают с ногами и стопами; детали пожеланий обсуждают с мастером."),
        ],
    },
    447404468052: {
        "id": "face",
        "slug": "massazh-litsa",
        "title": "Массаж лица",
        "caption": "Мягкая пауза для лица.",
        "time": "30 минут",
        "image": "service-face",
        "headline": "Короткий уход за лицом без длинной программы",
        "lead": "Отдельный массаж лица на 30 минут — когда хочется освежиться и расслабить мышцы.",
        "body": [
            "Формат подходит и сам по себе, и как завершение более длинного визита.",
            "В меню: 2 200 ₽ за 30 минут.",
        ],
        "fit": "Если нужен короткий локальный сеанс без полного SPA-пакета.",
        "steps": ["Массаж лица", "Сеанс 30 минут"],
        "faq": [
            ("Это косметологическая чистка?", "Нет, это массаж. Аппаратные и инъекционные процедуры салон не позиционирует как медицинские."),
            ("Можно ли совместить с массажем головы?", "Да, такие сочетания часто собирают при записи."),
        ],
    },
    910360552632: {
        "id": "head",
        "slug": "massazh-golovy",
        "title": "Массаж головы",
        "caption": "Снять напряжение в конце дня.",
        "time": "30 минут",
        "image": "service-head",
        "headline": "Волосистая часть головы и спокойный финал",
        "lead": "Короткий сеанс, который часто выбирают отдельно или как завершение другого ритуала.",
        "body": [
            "Массаж головы помогает переключиться и завершить визит на спокойной ноте.",
            "В меню: 2 200 ₽ за 30 минут.",
        ],
        "fit": "Если хочется короткой, точечной паузы без длинной программы.",
        "steps": ["Массаж головы", "Сеанс 30 минут"],
        "faq": [
            ("Нужно ли мыть голову после?", "Обычно специальный уход не требуется; уточните у мастера, если используете масла."),
            ("Подходит ли мужчинам?", "Да, формат одинаково популярен у гостей с любыми предпочтениями."),
        ],
    },
    896758684452: {
        "id": "back",
        "slug": "massazh-spiny-i-plech",
        "title": "Массаж спины и плеч",
        "caption": "Для тех, кто много сидит.",
        "time": "от 30 минут",
        "image": "service-back",
        "headline": "Спина, плечи и воротниковая зона",
        "lead": "Локальный массаж для зоны, которая чаще всего «держит» день.",
        "body": [
            "Удобный формат, если не нужен массаж всего тела, а хочется проработать спину и плечи.",
            "Варианты: 30 минут — 2 800 ₽, 45 минут — 3 200 ₽. Для регулярных визитов есть абонементы.",
        ],
        "fit": "Если работа за компьютером или нагрузка на плечи дают о себе знать к вечеру.",
        "steps": ["Массаж спины и плеч", "Варианты: 30 / 45 минут"],
        "faq": [
            ("Есть ли абонемент?", "Да, на массаж спины и плеч есть пакеты на 5, 7 и 10 сеансов — см. раздел «Абонементы»."),
            ("Можно ли сделать сильнее или мягче?", "Да, интенсивность обсуждают с мастером в начале сеанса."),
        ],
    },
    416131058942: {
        "id": "anticellulite",
        "slug": "antitsellyulitnyy-massazh",
        "title": "Антицеллюлитный массаж",
        "caption": "Плотная работа с проблемными зонами.",
        "time": "от 30 минут",
        "image": "service-anticellulite",
        "headline": "Целенаправленная работа с силуэтом",
        "lead": "Более интенсивный формат для тех, кто выбирает антицеллюлитную технику.",
        "body": [
            "Это не расслабляющий ойл-массаж «для сна», а более активная проработка. Результат индивидуален и зависит от курса и образа жизни.",
            "Варианты: 30 минут — 2 400 ₽, 60 минут — 3 800 ₽. Для регулярных визитов доступен абонемент на 60 минут.",
        ],
        "fit": "Если хотите именно антицеллюлитную технику и готовы к более плотной работе.",
        "steps": [
            "Антицеллюлитные техники",
            "Варианты: 30 / 60 минут",
            "Курс обсуждается при записи",
        ],
        "faq": [
            ("Это больно?", "Интенсивность подбирают индивидуально. Важно сразу сказать о комфорте."),
            ("Сколько сеансов нужно?", "Обычно думают курсом. Точный план лучше обсудить с администратором."),
        ],
    },
    732506660222: {
        "id": "lymph",
        "slug": "limfodrenazhnyy-massazh",
        "title": "Лимфодренажный массаж",
        "caption": "Мягкий ритм и ощущение лёгкости.",
        "time": "60 минут",
        "image": "service-lymph",
        "headline": "Спокойная техника с акцентом на отток",
        "lead": "Часовой сеанс лимфодренажной техники для тех, кто предпочитает мягкий, последовательный ритм.",
        "body": [
            "Формат отличается от спортивного или антицеллюлитного массажа более мягкой динамикой.",
            "В меню: 3 500 ₽ за 60 минут.",
        ],
        "fit": "Если ближе мягкая техника и ощущение лёгкости после сеанса.",
        "steps": ["Лимфодренажные техники", "Сеанс 60 минут"],
        "faq": [
            ("Чем отличается от классического массажа?", "Другой ритм и акцент на мягкой последовательной работе."),
            ("Нужна ли подготовка?", "Обычные рекомендации администратора: прийти без спешки и сообщить о самочувствии."),
        ],
    },
    183363705712: {
        "id": "honey",
        "slug": "medovyy-massazh",
        "title": "Медовый массаж",
        "caption": "Натуральный мёд и тёплая фактура.",
        "time": "60 минут",
        "image": "service-honey",
        "headline": "Массаж с натуральным мёдом",
        "lead": "Сеанс, в котором классические приёмы сочетаются с работой мёдом.",
        "body": [
            "Медовый массаж выбирают за особую фактуру и ощущения во время процедуры. Сообщите об аллергии на продукты пчеловодства заранее.",
            "В меню: 3 500 ₽ за 60 минут.",
        ],
        "fit": "Если нет аллергии на мёд и хочется попробовать характерный медовый формат.",
        "steps": ["Массаж с мёдом", "Сеанс 60 минут"],
        "faq": [
            ("Можно ли при аллергии на мёд?", "Нет, при аллергии на продукты пчеловодства эту процедуру не выбирают."),
            ("Останется ли липкость?", "Мастер завершает сеанс так, чтобы комфортно встать и одеться; детали уточнят на месте."),
        ],
    },
    449512171162: {
        "id": "sport",
        "slug": "sportivnyy-massazh",
        "title": "Спортивный массаж",
        "caption": "Для активных и после нагрузки.",
        "time": "от 60 минут",
        "image": "service-sport",
        "headline": "Более плотная работа с мышцами",
        "lead": "Формат для тех, кто занимается спортом или хочет более интенсивную проработку.",
        "body": [
            "Спортивный массаж отличается большей плотностью приёмов. Интенсивность всегда можно согласовать с мастером.",
            "Варианты: 60 минут — 3 900 ₽, 90 минут — 5 200 ₽.",
        ],
        "fit": "Если нужен не мягкий SPA-ритм, а более собранная мышечная работа.",
        "steps": [
            "Спортивные массажные техники",
            "Варианты: 60 / 90 минут",
        ],
        "faq": [
            ("Подходит ли новичкам?", "Да, но важно сказать о предпочтительной силе нажатия."),
            ("Когда лучше приходить — до или после тренировки?", "Зависит от цели. Администратор подскажет удобный слот."),
        ],
    },
}

SPA_AND_COUPLE = [
  {
    "id": "buddha",
    "category": "spa",
    "title": "Энергия Будды",
    "caption": "Жасмин, пилинг и тайский ойл-массаж.",
    "price": 5500,
    "image": "service-buddha",
    "time": "90 минут",
    "description": "Три последовательных этапа ухода: от молочной ванны для ног с жасмином до тайского ойл-массажа.",
    "steps": [
      "Молочная ванна для ног с жасмином — 15 минут",
      "Пилинг тела на выбор — 15 минут",
      "Тайский ойл-массаж — 60 минут"
    ],
    "url": "spa-programmy/energiya-buddy/"
  },
  {
    "id": "figure",
    "category": "spa",
    "title": "Идеальная фигура",
    "caption": "Кофейный пилинг и уход с ламинарией.",
    "price": 6100,
    "image": "service-figure",
    "time": "120 минут",
    "description": "Комплексная программа ухода за телом с кофейным пилингом, обёртыванием и массажем. Название программы сохранено из меню салона; результат индивидуален.",
    "steps": [
      "Пилинг «Кофейное суфле» — 15 минут",
      "Обёртывание с ламинарией и голубой глиной — 35 минут",
      "Слим-массаж — 50 минут; массаж головы — 10 минут",
      "Лосьон с ламинарией — 10 минут"
    ],
    "url": "spa-programmy/idealnaya-figura/"
  },
  {
    "id": "whisper",
    "category": "spa",
    "title": "Шёпот можжевельника",
    "caption": "Кедр, тёплый массаж, ароматерапия.",
    "price": 6300,
    "image": "service-whisper",
    "time": "130 минут",
    "description": "Программа с кедровым обёртыванием, термо-массажем и ароматерапией лица и декольте.",
    "steps": [
      "Кедровое обёртывание — 35 минут",
      "Термо-массаж с можжевеловыми шариками — 60 минут",
      "Ароматерапия лица и декольте — 35 минут"
    ],
    "url": "spa-programmy/shepot-mozhzhevelnika/"
  },
  {
    "id": "creme",
    "category": "spa",
    "title": "Крем-брюле",
    "caption": "Шоколад, сливки и маленькая пауза.",
    "price": 6400,
    "image": "service-creme",
    "time": "130 минут",
    "description": "Тёплая, неспешная программа с шоколадно-сливочным уходом, ойл-массажем и каолиновой маской.",
    "steps": [
      "Пилинг «Шоколад со сливками» — 15 минут",
      "Обёртывание «Шоколад со сливками» — 30 минут",
      "Ойл-массаж — 60 минут",
      "Каолиновая маска и крем — 25 минут"
    ],
    "url": "spa-programmy/krem-bryule/"
  },
  {
    "id": "you-me",
    "category": "couple",
    "title": "Ты и Я",
    "caption": "Время, которое вы проводите вместе.",
    "price": 10000,
    "image": "service-you-me",
    "time": "90 минут · для двоих",
    "description": "Совместная программа с пилингом, ойл-массажем и уходом на выбор. Стоимость указана за двоих.",
    "steps": [
      "Пилинг тела на выбор — 15 минут",
      "Ойл-массаж — 60 минут",
      "СПА для лица или массаж головы — 15 минут"
    ],
    "url": "spa-dlya-dvoih/ty-i-ya/"
  },
  {
    "id": "eden",
    "category": "couple",
    "title": "Эдем для двоих",
    "caption": "Две программы. Одно настроение.",
    "price": 12000,
    "image": "service-eden",
    "time": "Программа для двоих",
    "description": "Парная программа с отдельным составом ухода для неё и для него. Стоимость указана за двоих.",
    "steps": [
      "Для неё: пилинг «Табак и вишня» — 15 мин, обёртывание — 30 мин, балийский массаж — 30 мин, ойл-массаж — 30 мин, СПА для лица — 20 мин",
      "Для него: бамбуковые веники — 15 мин, обёртывание «Табак и вишня» — 35 мин, балийский массаж — 30 мин, ойл-массаж — 30 мин, массаж головы — 15 мин"
    ],
    "url": "spa-dlya-dvoih/edem-dlya-dvoih/"
  },
  {
    "id": "romance",
    "category": "couple",
    "title": "Романтическое путешествие",
    "caption": "Особенный повод побыть рядом.",
    "price": 18000,
    "image": "service-romance",
    "time": "150 минут · для двоих",
    "description": "Продолжительная программа для двоих с уходами, массажем и завершением с шампанским и фруктами, как указано в меню салона. Стоимость — за двоих.",
    "steps": [
      "Для неё: пилинг «Ежевика-мимоза» — 15 мин, обёртывание — 35 мин, травяные мешочки — 20 мин, массаж с горячей свечой — 50 мин, ароматерапия лица и декольте — 30 мин",
      "Для него: сандаловый пилинг — 15 мин, обёртывание — 35 мин, массаж с горячей свечой — 60 мин, креольский массаж — 20 мин, СПА для лица — 20 мин",
      "Шампанское и фрукты"
    ],
    "url": "spa-dlya-dvoih/romanticheskoe-puteshestvie/"
  }
]


def money(n: int) -> str:
    return f"{n:,}".replace(",", "\u00a0") + "\u00a0₽"


def price_label(editions: list[dict], base: int) -> tuple[int, bool, str]:
    prices = [e["price"] for e in editions if e.get("price")]
    if not prices:
        return base, False, money(base)
    lo = min(prices)
    multi = len(set(prices)) > 1 or len(editions) > 1
    label = ("от " if multi else "") + money(lo)
    return lo, multi, label


def download_image(url: str, image_stem: str) -> str:
    """Download photo; return filename with extension (prefer jpg via ffmpeg)."""
    dest_jpg = ASSETS / f"{image_stem}.jpg"
    dest_webp = ASSETS / f"{image_stem}.webp"
    if dest_webp.exists() and dest_webp.stat().st_size > 1000 and dest_webp.read_bytes()[:4] == b"RIFF":
        return f"{image_stem}.webp"
    if dest_jpg.exists() and dest_jpg.stat().st_size > 1000:
        return f"{image_stem}.jpg"
    tmp = ASSETS / f"{image_stem}.src"
    ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    subprocess.check_call(["curl", "-sL", "-A", ua, "-o", str(tmp), url])
    cwebp = shutil.which("cwebp")
    if cwebp and subprocess.call(
        [cwebp, "-q", "78", "-resize", "1040", "0", str(tmp), "-o", str(dest_webp)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ) == 0 and dest_webp.exists() and dest_webp.stat().st_size > 1000:
        tmp.unlink(missing_ok=True)
        return f"{image_stem}.webp"
    subprocess.check_call(
        [
            "ffmpeg", "-y", "-i", str(tmp),
            "-vf", "scale=1040:-1:flags=lanczos",
            "-q:v", "4",
            str(dest_jpg),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    tmp.unlink(missing_ok=True)
    return f"{image_stem}.jpg"


def build_massages(raw: list[dict]) -> list[dict]:
    out = []
    for item in raw:
        uid = item["uid"]
        c = CURATED[uid]
        lo, multi, label = price_label(item["editions"], item["price"])
        editions = item["editions"]
        duration_note = ", ".join(
            f"{e['duration']} — {money(e['price'])}" for e in editions if e.get("price")
        )
        product = {
            **c,
            "category": "massage",
            "price": lo,
            "from": multi,
            "price_label": label,
            "editions": editions,
            "duration_note": duration_note,
            "description": c["lead"],
            "url": f"massazh/{c['slug']}/",
            "old_path": item["old_path"],
            "img_src": item.get("img"),
            "image_file": f"{c['image']}.webp" if c.get("keep_image") else f"{c['image']}.jpg",
        }
        product["_uid"] = uid
        out.append(product)
    order = list(CURATED.keys())
    out.sort(key=lambda p: order.index(p["_uid"]))
    for p in out:
        del p["_uid"]
    return out


def write_data_js(massages: list[dict]) -> None:
    products = []
    for m in massages:
        entry = {
            "id": m["id"],
            "category": "massage",
            "title": m["title"],
            "caption": m["caption"],
            "price": m["price"],
            "image": m["image_file"],
            "time": m["time"],
            "description": m["description"],
            "steps": m["steps"],
            "url": m["url"],
        }
        if m["from"]:
            entry["from"] = True
        products.append(entry)
    # SPA/couple keep stem names — app.js adds nothing if extension present
    for item in SPA_AND_COUPLE:
        entry = dict(item)
        if not str(entry["image"]).endswith((".webp", ".jpg", ".jpeg", ".png")):
            entry["image"] = f'{entry["image"]}.webp'
        products.append(entry)
    text = "window.PATTAYA_PRODUCTS = " + json.dumps(products, ensure_ascii=False, indent=2) + ";\n"
    (ROOT / "data.js").write_text(text, encoding="utf-8")


def shared_chrome(prefix: str) -> tuple[str, str, str]:
    """Return (head_assets, header, footer) with correct relative prefix."""
    head = (
        f'<link rel="icon" href="{prefix}assets/favicon.svg" type="image/svg+xml">'
        f'<link rel="preload" href="{prefix}assets/fonts/cormorant-garamond.ttf" as="font" type="font/ttf" crossorigin>'
        f'<link rel="stylesheet" href="{prefix}styles.css?v={CACHE_BUST}">'
        f'<link rel="stylesheet" href="{prefix}pages.css?v={CACHE_BUST}">'
        f'<script src="{prefix}data.js?v={CACHE_BUST}" defer></script>'
        f'<script src="{prefix}app.js?v={CACHE_BUST}" defer></script>'
    )
    header = f'''<a class="skip" href="#main">Перейти к содержимому</a><div class="utility"><span>Маленький отпуск, не покидая город</span><span>Иваново, Батурина, 23 <i></i> Ежедневно 10:00–22:00</span></div>
<header class="header"><a class="logo" href="{prefix}./#top" aria-label="Паттайя — в начало"><svg class="icon icon-lotus " viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.25" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M24 36C10 33 5 23 6 13c9 1 16 9 18 23Zm0 0c14-3 19-13 18-23-9 1-16 9-18 23Zm0 0C14 23 14 12 24 3c10 9 10 20 0 33ZM24 40C10 42 2 35 1 26c10-1 18 4 23 14Zm0 0c14 2 22-5 23-14-10-1-18 4-23 14Z"/></svg><span><strong>паттайя</strong><small>М А С С А Ж &nbsp; &amp; &nbsp; S P A</small></span></a><nav id="navigation" aria-label="Основная навигация"><a href="{prefix}massazh/" aria-current="page">Массажи</a><a href="{prefix}spa-programmy/">SPA</a><a href="{prefix}spa-dlya-dvoih/">Для двоих</a><a href="{prefix}podarochnye-sertifikaty/">Сертификаты</a><a href="{prefix}ceny/">Цены</a><a href="{prefix}kontakty/">Контакты</a></nav><button class="button button-small" data-book="Знакомство с салоном">Записаться {ICON_ARROW}</button><button class="menu-toggle" aria-label="Открыть меню" aria-expanded="false" aria-controls="navigation"><span></span><span></span></button></header>'''
    # Fix aria-current only on massazh pages - will adjust per page
    footer = f'''<nav class="site-directory wrap" aria-label="Разделы сайта"><div><p>Ритуалы</p><a href="{prefix}massazh/">Массажи</a><a href="{prefix}spa-programmy/">SPA-программы</a><a href="{prefix}spa-dlya-dvoih/">Для двоих</a></div><div><p>Особенный повод</p><a href="{prefix}spa-devichnik/">SPA-девичник</a><a href="{prefix}podarochnye-sertifikaty/">Сертификаты</a><a href="{prefix}abonementy/">Абонементы</a></div><div><p>Салон</p><a href="{prefix}ceny/">Все цены</a><a href="{prefix}o-salone/">О салоне</a><a href="{prefix}kontakty/">Контакты</a><a href="{prefix}karta-sayta/">Все страницы</a></div></nav><footer class="footer wrap"><div class="footer-top"><a class="logo" href="{prefix}./#top"><svg class="icon icon-lotus " viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.25" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M24 36C10 33 5 23 6 13c9 1 16 9 18 23Zm0 0c14-3 19-13 18-23-9 1-16 9-18 23Zm0 0C14 23 14 12 24 3c10 9 10 20 0 33ZM24 40C10 42 2 35 1 26c10-1 18 4 23 14Zm0 0c14 2 22-5 23-14-10-1-18 4-23 14Z"/></svg><span><strong>паттайя</strong><small>М А С С А Ж &nbsp; &amp; &nbsp; S P A</small></span></a><span>Маленький отпуск.<br><em>Большая забота о себе.</em></span><div><a href="https://vk.com/pattaya_massage" target="_blank" rel="noopener">ВКонтакте {ICON_DIAG}</a><a href="https://t.me/pattaya_ivanovo" target="_blank" rel="noopener">Telegram {ICON_DIAG}</a></div></div><div class="footer-bottom"><span>© <span id="year">2026</span> СПА-салон «Паттайя»</span><span>Не является медицинской услугой</span><a href="#main">Наверх {ICON_DIAG}</a></div></footer><div class="mobile-booking"><a href="tel:+74932372151" aria-label="Позвонить в салон"><svg class="icon icon-phone " viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.25" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M5 3h4l2 5-3 2a15 15 0 0 0 6 6l2-3 5 2v4a2 2 0 0 1-2 2C10 21 3 14 3 5a2 2 0 0 1 2-2Z"/></svg></a><button data-book="Запись на процедуру">Выбрать время {ICON_ARROW}</button></div><dialog id="booking-dialog" class="booking-dialog" aria-labelledby="booking-title"><button class="dialog-close" aria-label="Закрыть запись"><svg class="icon icon-close " viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.25" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="m6 6 12 12M6 18 18 6"/></svg></button><div class="booking-inner"><svg class="icon icon-lotus " viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.25" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M24 36C10 33 5 23 6 13c9 1 16 9 18 23Zm0 0c14-3 19-13 18-23-9 1-16 9-18 23Zm0 0C14 23 14 12 24 3c10 9 10 20 0 33ZM24 40C10 42 2 35 1 26c10-1 18 4 23 14Zm0 0c14 2 22-5 23-14-10-1-18 4-23 14Z"/></svg><p class="eyebrow">ВРЕМЯ ДЛЯ ВАШЕГО ОТДЫХА</p><h2 id="booking-title">Давайте выберем<br><em>вашу паузу.</em></h2><p class="booking-selection" id="booking-selection"></p><p>Свяжитесь с администратором: подберём программу и подтвердим удобное время.</p><a class="button" href="tel:+74932372151">Позвонить и записаться <svg class="icon icon-phone " viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.25" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M5 3h4l2 5-3 2a15 15 0 0 0 6 6l2-3 5 2v4a2 2 0 0 1-2 2C10 21 3 14 3 5a2 2 0 0 1 2-2Z"/></svg></a><a class="button button-bordered" href="https://t.me/pattaya_ivanovo" target="_blank" rel="noopener">Написать в Telegram {ICON_DIAG}</a><button id="copy-request" class="text-link">Скопировать пожелание {ICON_ARROW}</button><p class="copy-status" id="copy-status" role="status"></p><p class="small-note">Батурина, 23 · ежедневно 10:00–22:00.<br>Запись оформляется напрямую с салоном. Сайт не отправляет заявки автоматически и не принимает оплату.</p></div></dialog><noscript><p class="noscript-note">Записаться можно по телефону <a href="tel:+74932372151">+7 (4932) 37-21-51</a> или в Telegram. Цены и описания доступны без JavaScript.</p></noscript>'''
    return head, header, footer


def product_card(m: dict, prefix: str) -> str:
    href = f"{prefix}{m['url']}"
    img = f"{prefix}assets/{m['image_file']}"
    return (
        f'<article class="product-card"><a class="product-photo" href="{href}" aria-label="{m["title"]}: состав и цена">'
        f'<img src="{img}" alt="{m["title"]} — фото из материалов салона Паттайя" width="520" height="570" loading="lazy">'
        f'<span class="product-time">{m["time"]}</span><span class="photo-arrow">{ICON_DIAG}</span></a>'
        f'<div class="product-card-copy"><h3><a href="{href}">{m["title"]}</a></h3><p>{m["caption"]}</p>'
        f'<div><span>{m["price_label"]}</span><a class="product-link" href="{href}" aria-label="Состав программы {m["title"]}">Подробнее {ICON_ARROW}</a></div></div></article>'
    )


def write_detail_page(m: dict, all_massages: list[dict]) -> None:
    prefix = "../../"
    head_assets, header, footer = shared_chrome(prefix)
    header = header.replace(' aria-current="page"', "", 1)  # remove from Массажи default - keep without current on detail? Actually massages section is still active
    # re-add aria-current on Массажи
    header = header.replace(
        f'<a href="{prefix}massazh/">Массажи</a>',
        f'<a href="{prefix}massazh/" aria-current="page">Массажи</a>',
        1,
    )
    url = f"{ORIGIN}/{m['url']}"
    title = f"{m['title']} в Иванове — {m['price_label']} | Паттайя"
    desc = f"{m['title']} в СПА-салоне «Паттайя», Иваново. {m['price_label']}. {m['time']}. Запись: ул. Батурина, 23."
    img = f"{ORIGIN}/assets/{m['image_file']}"
    book = f"{m['title']} — {m['price_label']}"
    steps = "".join(
        f'<li><span>{i:02d}</span><p>{step}</p></li>' for i, step in enumerate(m["steps"], 1)
    )
    faqs = "".join(
        f'<details><summary>{q} {ICON_PLUS}</summary><p>{a}</p></details>' for q, a in m["faq"]
    )
    body = "".join(f"<p>{p}</p>" for p in m["body"])
    related = [x for x in all_massages if x["id"] != m["id"]][:3]
    related_html = "".join(product_card(x, prefix) for x in related)
    editions_note = ""
    if len(m["editions"]) > 1:
        editions_note = f'<p class="price-note">Варианты по меню: {m["duration_note"]}.</p>'

    ld = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "DaySpa",
                "@id": f"{ORIGIN}/#salon",
                "name": "СПА-салон «Паттайя»",
                "url": f"{ORIGIN}/",
                "image": f"{ORIGIN}/assets/hero.webp",
                "telephone": "+74932372151",
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": "ул. Батурина, 23",
                    "addressLocality": "Иваново",
                    "addressCountry": "RU",
                },
            },
            {
                "@type": "WebPage",
                "@id": f"{url}#page",
                "url": url,
                "name": title,
                "description": desc,
                "inLanguage": "ru-RU",
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Главная", "item": f"{ORIGIN}/"},
                    {"@type": "ListItem", "position": 2, "name": "Массажи", "item": f"{ORIGIN}/massazh/"},
                    {"@type": "ListItem", "position": 3, "name": m["title"], "item": url},
                ],
            },
            {
                "@type": "Service",
                "@id": f"{url}#service",
                "name": m["title"],
                "description": m["description"],
                "url": url,
                "image": img,
                "serviceType": "Массажи",
                "provider": {"@id": f"{ORIGIN}/#salon"},
                "areaServed": {"@type": "City", "name": "Иваново"},
            },
        ],
    }

    html = f'''<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#4b292f"><meta name="format-detection" content="telephone=no"><title>{title}</title><meta name="description" content="{desc}"><meta name="robots" content="index,follow,max-image-preview:large"><link rel="canonical" href="{url}"><meta property="og:type" content="website"><meta property="og:locale" content="ru_RU"><meta property="og:site_name" content="Паттайя"><meta property="og:title" content="{title}"><meta property="og:description" content="{desc}"><meta property="og:url" content="{url}"><meta property="og:image" content="{img}"><meta name="twitter:card" content="summary_large_image">{head_assets}<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script></head><body class="inner-page">{header}<main id="main"><nav class="breadcrumbs wrap" aria-label="Хлебные крошки"><ol><li><a href="{prefix}./">Главная</a></li><li><a href="{prefix}massazh/">Массажи</a></li><li><span aria-current="page">{m["title"]}</span></li></ol></nav><section class="page-hero wrap"><div class="page-hero-copy"><p class="eyebrow">МАССАЖИ / ИВАНОВО</p><h1 class="">{m["title"]}</h1><p class="page-lead">{m["caption"]}</p><div class="hero-facts"><span>{m["time"]}</span><span>{m["price_label"]}</span></div><button class="button" data-book="{book}">Выбрать время {ICON_ARROW}</button></div><figure class="page-hero-photo"><img src="{prefix}assets/{m["image_file"]}" alt="{m["title"]} — Паттайя" width="1200" height="900" fetchpriority="high"><figcaption>ПАТТАЙЯ / МАЛЕНЬКИЙ ОТПУСК В ГОРОДЕ</figcaption></figure></section><section class="detail-layout wrap"><div class="detail-main"><p class="eyebrow">О ВАШЕМ РИТУАЛЕ</p><h2>{m["headline"]}</h2>{body}<div class="fit-note"><span>КОГДА ВЫБРАТЬ</span><p>{m["fit"]}</p></div><h2>В программе</h2><ol class="ritual-stages">{steps}</ol>{editions_note}<p class="price-note">Время и состав подтверждаются при записи. Услуги не являются медицинскими.</p><div class="page-faq"><h2>Чуть больше <em>ясности.</em></h2><div class="faq-list">{faqs}</div></div><div class="context-links"><a href="{prefix}massazh/">Все массажи</a><a href="{prefix}ceny/">Сравнить цены</a><a href="{prefix}podarochnye-sertifikaty/">Подарочный сертификат</a></div></div><aside class="booking-card" id="booking"><p class="eyebrow">ВАША ПАУЗА НАЧИНАЕТСЯ ЗДЕСЬ</p><h2>{m["price_label"]}</h2><p>Стоимость по меню</p><div class="booking-card-rule"></div><p>{m["time"]}</p><p>Иваново, Батурина, 23<br>Ежедневно 10:00–22:00</p><button class="button" data-book="{book}">Выбрать время {ICON_ARROW}</button><a class="text-link" href="tel:+74932372151">+7 (4932) 37-21-51 {ICON_DIAG}</a><small>Администратор подтвердит программу, стоимость и свободное время. Онлайн-оплата не требуется.</small></aside></section><section class="section related-section wrap"><div class="section-heading"><div><p class="eyebrow">ПРОДОЛЖИМ ВЫБИРАТЬ</p><h2>Другие <em>ритуалы.</em></h2></div></div><div class="product-grid page-product-grid related-grid">{related_html}</div></section><section class="page-cta"><div class="wrap"><div><p class="eyebrow light">БАТУРИНА, 23 / ЕЖЕДНЕВНО 10:00–22:00</p><h2>Давайте выберем<br><em>вашу паузу.</em></h2><p>Расскажите, какого отдыха хочется. Уточним программу и удобное время.</p></div><div><button class="button button-cream" data-book="Помогите выбрать программу">Выбрать время {ICON_ARROW}</button><a class="page-phone" href="tel:+74932372151">+7 (4932) 37-21-51</a><a class="text-link" href="{prefix}kontakty/">Как нас найти {ICON_DIAG}</a></div></div></section></main>{footer}</body></html>'''
    dest = ROOT / "massazh" / m["slug"] / "index.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html, encoding="utf-8")


def write_catalog(massages: list[dict]) -> None:
    prefix = "../"
    head_assets, header, footer = shared_chrome(prefix)
    cards = "".join(product_card(m, prefix) for m in massages)
    min_price = min(m["price"] for m in massages)
    title = "Массаж в Иванове — виды и цены | Паттайя"
    desc = f"16 видов массажа в салоне «Паттайя», Иваново: ойл, свеча, камни, апельсины и другие. Цены от {money(min_price)}. Батурина, 23."
    url = f"{ORIGIN}/massazh/"
    item_list = [
        {"@type": "ListItem", "position": i, "name": m["title"], "url": f"{ORIGIN}/{m['url']}"}
        for i, m in enumerate(massages, 1)
    ]
    ld = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "DaySpa", "@id": f"{ORIGIN}/#salon", "name": "СПА-салон «Паттайя»", "url": f"{ORIGIN}/"},
            {
                "@type": "CollectionPage",
                "@id": f"{url}#page",
                "url": url,
                "name": title,
                "description": desc,
            },
            {
                "@type": "ItemList",
                "name": "Массажи",
                "itemListElement": item_list,
            },
        ],
    }
    html = f'''<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#4b292f"><meta name="format-detection" content="telephone=no"><title>{title}</title><meta name="description" content="{desc}"><meta name="robots" content="index,follow,max-image-preview:large"><link rel="canonical" href="{url}"><meta property="og:type" content="website"><meta property="og:locale" content="ru_RU"><meta property="og:site_name" content="Паттайя"><meta property="og:title" content="{title}"><meta property="og:description" content="{desc}"><meta property="og:url" content="{url}"><meta property="og:image" content="{ORIGIN}/assets/service-oil.webp"><meta name="twitter:card" content="summary_large_image">{head_assets}<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script></head><body class="inner-page">{header}<main id="main"><nav class="breadcrumbs wrap" aria-label="Хлебные крошки"><ol><li><a href="{prefix}./">Главная</a></li><li><span aria-current="page">Массаж в Иванове.</span></li></ol></nav><section class="page-hero wrap"><div class="page-hero-copy"><p class="eyebrow">ПАТТАЙЯ / ИВАНОВО</p><h1 class="">Массаж<br><em>в Иванове.</em></h1><p class="page-lead">От знакомого ойл-массажа до локальных сеансов для спины, ног и лица. Выберите формат — время и детали обсудим лично.</p><div class="hero-facts"><span>16 программ</span><span>от {money(min_price)}</span><span>Батурина, 23</span></div></div><figure class="page-hero-photo"><img src="{prefix}assets/service-oil.webp" alt="Массаж в Иванове — Паттайя" width="1200" height="900" fetchpriority="high"><figcaption>ПАТТАЙЯ / МАЛЕНЬКИЙ ОТПУСК В ГОРОДЕ</figcaption></figure></section><nav class="category-pills wrap" aria-label="Категории процедур"><a href="{prefix}massazh/" aria-current="page">Массажи</a><a href="{prefix}spa-programmy/">SPA-программы</a><a href="{prefix}spa-dlya-dvoih/">Для двоих</a><a href="{prefix}ceny/">Все цены</a></nav><section class="section wrap category-catalog"><div class="product-grid page-product-grid ">{cards}</div><p class="price-note">Цена и состав подтверждаются при записи. Услуги не являются медицинскими.</p></section><section class="page-story wrap"><p class="eyebrow">КАК ВЫБРАТЬ</p><h2>Шестнадцать способов сделать паузу</h2><p>В этом разделе — индивидуальные массажные программы: от коротких локальных сеансов до полноценных ритуалов с маслами, камнями, травами или свечой. Если хочется совместить массаж с пилингом и обёртыванием, посмотрите SPA-программы.</p><div class="context-links"><a href="{prefix}spa-devichnik/">Отдых компанией</a><a href="{prefix}podarochnye-sertifikaty/">Подарить посещение</a><a href="{prefix}abonementy/">Регулярные визиты</a></div><div class="page-faq"><h2>Чуть больше <em>ясности.</em></h2><div class="faq-list"><details><summary>Как выбрать массаж? {ICON_PLUS}</summary><p>Начните с формата и длительности. Администратор расскажет о различиях и поможет уточнить ваши пожелания.</p></details><details><summary>Можно ли прийти вдвоём? {ICON_PLUS}</summary><p>В этом разделе цены относятся к индивидуальным процедурам. Совместные посещения собраны в разделе «Для двоих».</p></details></div></div></section><section class="page-cta"><div class="wrap"><div><p class="eyebrow light">БАТУРИНА, 23 / ЕЖЕДНЕВНО 10:00–22:00</p><h2>Давайте выберем<br><em>вашу паузу.</em></h2><p>Расскажите, какого отдыха хочется. Уточним программу и удобное время.</p></div><div><button class="button button-cream" data-book="Помогите выбрать программу">Выбрать время {ICON_ARROW}</button><a class="page-phone" href="tel:+74932372151">+7 (4932) 37-21-51</a><a class="text-link" href="{prefix}kontakty/">Как нас найти {ICON_DIAG}</a></div></div></section></main>{footer}</body></html>'''
    (ROOT / "massazh" / "index.html").write_text(html, encoding="utf-8")


def patch_ceny(massages: list[dict]) -> None:
    path = ROOT / "ceny" / "index.html"
    html = path.read_text(encoding="utf-8")
    rows = []
    for m in massages:
        rows.append(
            f'<a href="../{m["url"]}"><span><strong>{m["title"]}</strong><small>{m["time"]}</small></span>'
            f'<span>{m["price_label"]}<small>за программу</small></span>{ICON_DIAG}</a>'
        )
    block = (
        '<div class="price-list">' + "".join(rows) + "</div>"
    )
    html = re.sub(
        r'(<section class="price-category wrap"><div class="section-heading"><h2>Массажи</h2>.*?</div>)<div class="price-list">.*?</div>',
        r"\1" + block,
        html,
        count=1,
        flags=re.S,
    )
    html = html.replace(
        "массаж от 3 500 ₽",
        f"массаж от {money(min(m['price'] for m in massages)).replace(chr(160), ' ')}",
    )
    html = html.replace(f"?v=20260918-multipage", f"?v={CACHE_BUST}")
    html = html.replace(f"?v=20260918-file-preview", f"?v={CACHE_BUST}")
    path.write_text(html, encoding="utf-8")


def patch_homepage() -> None:
    path = ROOT / "index.html"
    html = path.read_text(encoding="utf-8")
    html = html.replace(">Массажи <span>04</span>", ">Массажи <span>16</span>")
    html = html.replace("?v=20260918-multipage", f"?v={CACHE_BUST}")
    html = html.replace("?v=20260918-file-preview", f"?v={CACHE_BUST}")
    path.write_text(html, encoding="utf-8")


def write_sitemap(massages: list[dict]) -> None:
    urls = [
        "/",
        "/massazh/",
        "/spa-programmy/",
        "/spa-dlya-dvoih/",
    ]
    urls += [f"/{m['url']}" for m in massages]
    urls += [
        "/spa-programmy/energiya-buddy/",
        "/spa-programmy/idealnaya-figura/",
        "/spa-programmy/shepot-mozhzhevelnika/",
        "/spa-programmy/krem-bryule/",
        "/spa-dlya-dvoih/ty-i-ya/",
        "/spa-dlya-dvoih/edem-dlya-dvoih/",
        "/spa-dlya-dvoih/romanticheskoe-puteshestvie/",
        "/podarochnye-sertifikaty/",
        "/abonementy/",
        "/spa-devichnik/",
        "/ceny/",
        "/o-salone/",
        "/kontakty/",
        "/karta-sayta/",
    ]
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        lines.append(f"  <url><loc>{ORIGIN}{u}</loc><lastmod>2026-09-24</lastmod></url>")
    lines.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_redirects(massages: list[dict]) -> None:
    mapping = {m["old_path"]: f"/{m['url']}" for m in massages}
    # keep spa redirects
    mapping.update({
        "/tproduct/882075536912-spa-paket-energiya-buddi": "/spa-programmy/energiya-buddy/",
        "/tproduct/381906675812-spa-paket-idealnaya-figura": "/spa-programmy/idealnaya-figura/",
        "/tproduct/619193310032-spa-paket-shyopot-mozhzhevelnika": "/spa-programmy/shepot-mozhzhevelnika/",
        "/tproduct/290796796032-spa-paket-krem-bryule": "/spa-programmy/krem-bryule/",
        "/tproduct/238230467692-ti-i-ya": "/spa-dlya-dvoih/ty-i-ya/",
        "/tproduct/588653158142-edem-dlya-dvoih": "/spa-dlya-dvoih/edem-dlya-dvoih/",
        "/tproduct/628916802002-romanticheskoe-puteshestvie": "/spa-dlya-dvoih/romanticheskoe-puteshestvie/",
    })
    (ROOT / "deploy" / "redirects.json").write_text(
        json.dumps(mapping, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    rules = [
        "Options -Indexes -MultiViews",
        "DirectoryIndex index.html",
        "ErrorDocument 404 /404.html",
        "",
        "RewriteEngine On",
        "# Avoid duplicate /index.html URLs; do not redirect internal DirectoryIndex requests.",
        r"RewriteCond %{THE_REQUEST} \s/+(.*/)?index\.html[?\s] [NC]",
        r"RewriteRule ^(.*)index\.html$ /$1 [R=301,L]",
        "",
    ]
    for old, new in mapping.items():
        slug = old.lstrip("/").replace("tproduct/", "")
        escaped = slug.replace("-", r"\-")
        rules.append(f"RewriteRule ^tproduct/{escaped}/?$ {new} [R=301,L]")
    (ROOT / ".htaccess").write_text("\n".join(rules) + "\n", encoding="utf-8")


def patch_karta(massages: list[dict]) -> None:
    path = ROOT / "karta-sayta" / "index.html"
    html = path.read_text(encoding="utf-8")
    links = "".join(f'<a href="../{m["url"]}">{m["title"]}</a>' for m in massages)
    old_block = (
        '<a href="../massazh/tayskiy-oyl-massazh/">Тайский ойл-массаж</a>'
        '<a href="../massazh/massazh-tayushchey-svechoy/">Прикосновение тающей свечи</a>'
        '<a href="../massazh/massazh-v-chetyre-ruki/">Тандем. В четыре руки</a>'
        '<a href="../massazh/massazh-mozhzhevelovymi-sharikami/">Массаж с можжевеловыми шариками</a>'
    )
    if old_block in html:
        html = html.replace(old_block, links)
    else:
        html, n = re.subn(
            r'(?:<a href="../massazh/(?:tayskiy-oyl-massazh|massazh-[^"]+)/">[^<]+</a>\s*){2,}',
            links,
            html,
            count=1,
        )
        if n == 0:
            print("WARN: karta-sayta massage links not patched")
    html = html.replace("?v=20260918-multipage", f"?v={CACHE_BUST}")
    html = html.replace("?v=20260918-file-preview", f"?v={CACHE_BUST}")
    path.write_text(html, encoding="utf-8")


def main() -> None:
    raw = json.loads(RAW.read_text(encoding="utf-8"))
    massages = build_massages(raw)
    print(f"Building {len(massages)} massages…")
    for m in massages:
        if m.get("keep_image"):
            m["image_file"] = f'{m["image"]}.webp'
        elif m.get("img_src"):
            print("image", m["title"], "…")
            m["image_file"] = download_image(m["img_src"], m["image"])
        write_detail_page(m, massages)
        print("page", m["slug"], m["image_file"])
    write_data_js(massages)
    write_catalog(massages)
    patch_ceny(massages)
    patch_homepage()
    write_sitemap(massages)
    write_redirects(massages)
    patch_karta(massages)
    print("done")


if __name__ == "__main__":
    main()
