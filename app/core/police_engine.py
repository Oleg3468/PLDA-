from dataclasses import dataclass, field
from typing import List


@dataclass
class PoliceQuestion:
    code: str
    title: str
    description: str
    required_sources: List[str] = field(default_factory=list)


POLICE_QUESTIONS = [
    PoliceQuestion(
        "STOP_GROUND",
        "Основание остановки",
        "Почему лицо остановили и существовало ли законное основание?",
        ["national_law", "police_law", "human_rights"],
    ),
    PoliceQuestion(
        "OFFICER_IDENTIFICATION",
        "Представление сотрудника",
        "Обязан ли сотрудник назвать себя, должность или идентификатор?",
        ["police_law", "national_law"],
    ),
    PoliceQuestion(
        "OFFICER_ID",
        "Удостоверение",
        "Должен ли сотрудник предъявить служебное удостоверение и при каких условиях?",
        ["police_law", "national_law"],
    ),
    PoliceQuestion(
        "AUTHORITY",
        "Полномочия",
        "Имел ли конкретный сотрудник полномочия совершать данное действие?",
        ["police_law", "national_law"],
    ),
    PoliceQuestion(
        "DEMANDS",
        "Требования полиции",
        "Что полиция вправе потребовать и что лицо обязано выполнить?",
        ["police_law", "national_law"],
    ),
    PoliceQuestion(
        "RECORDING",
        "Фото и видеосъёмка",
        "Разрешена ли съёмка действий полиции и существуют ли ограничения?",
        ["national_law", "human_rights"],
    ),
    PoliceQuestion(
        "AUDIO_RECORDING",
        "Аудиозапись",
        "Допустима ли запись разговоров и существуют ли специальные ограничения?",
        ["national_law", "human_rights"],
    ),
    PoliceQuestion(
        "PHONE",
        "Телефон и цифровые данные",
        "Может ли полиция потребовать телефон, разблокировку или доступ к данным?",
        ["national_law", "human_rights"],
    ),
    PoliceQuestion(
        "SEARCH",
        "Обыск и досмотр",
        "Какие основания и процедуры необходимы для досмотра или обыска?",
        ["national_law", "police_law", "human_rights"],
    ),
    PoliceQuestion(
        "SEIZURE",
        "Изъятие имущества",
        "Может ли полиция изъять имущество и какие требования должны быть соблюдены?",
        ["national_law", "police_law"],
    ),
    PoliceQuestion(
        "DETENTION",
        "Задержание",
        "Существовало ли законное основание для задержания и соблюдалась ли процедура?",
        ["national_law", "human_rights"],
    ),
    PoliceQuestion(
        "FORCE",
        "Применение силы",
        "Были ли основания, необходимость и соразмерность применения силы?",
        ["police_law", "national_law", "human_rights"],
    ),
    PoliceQuestion(
        "PROCEDURE",
        "Соблюдение процедуры",
        "Выполнила ли полиция все обязательные процессуальные требования?",
        ["national_law", "police_law"],
    ),
    PoliceQuestion(
        "REMEDY",
        "Средства защиты",
        "Какие жалобы, обжалование или судебные средства защиты доступны?",
        ["national_law", "human_rights"],
    ),
]


def get_police_questions() -> List[PoliceQuestion]:
    return POLICE_QUESTIONS


def get_question_codes() -> List[str]:
    return [question.code for question in POLICE_QUESTIONS]


def required_source_layers() -> List[str]:
    layers = set()

    for question in POLICE_QUESTIONS:
        layers.update(question.required_sources)

    return sorted(layers)


def build_checklist() -> list:
    return [
        {
            "code": question.code,
            "title": question.title,
            "description": question.description,
            "required_sources": question.required_sources,
        }
        for question in POLICE_QUESTIONS
    ]
