from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models import KnowledgeBaseSource, Role


ROLES = [
    ("admin_customer", "Администратор заказчика"),
    ("manager", "Менеджер"),
    ("content_operator", "Оператор контента"),
    ("observer", "Наблюдатель"),
]


KB_SOURCES = [
    ("KB-SRC-01", "Aleado (Япония)", "https://aleado.com/", "Web", "approved"),
    ("KB-SRC-02", "Che168 (Китай)", "https://www.che168.com/", "Web", "approved"),
    ("KB-SRC-03", "Dongchedi (Китай)", "https://www.dongchedi.com/", "Web", "approved"),
    ("KB-SRC-04", "Yoojia (Китай)", "https://www.yoojia.com/", "Web", "approved"),
    ("KB-SRC-05", "Encar (Корея)", "http://encar.com/", "Web", "approved"),
    (
        "KB-SRC-06",
        "KB Cha Cha Cha (Корея)",
        "https://www.kbchachacha.com/public/main.kbc",
        "Web",
        "approved",
    ),
    ("KB-SRC-07", "Drom (комплектации)", "https://drom.ru/", "Web", "approved"),
    ("KB-SRC-08", "Материалы заказчика (FAQ)", None, "TBD", "waiting_customer"),
    ("KB-SRC-09", "Диалоги менеджеров (обезличенные)", None, "TBD", "waiting_customer"),
]


def main() -> None:
    db: Session = SessionLocal()
    try:
        for code, title in ROLES:
            role = db.query(Role).filter(Role.code == code).one_or_none()
            if not role:
                db.add(Role(code=code, title=title))
        db.commit()

        for code, title, url, fmt, status in KB_SOURCES:
            src = (
                db.query(KnowledgeBaseSource)
                .filter(KnowledgeBaseSource.code == code)
                .one_or_none()
            )
            if not src:
                src = KnowledgeBaseSource(code=code, title=title)
                db.add(src)
            src.title = title
            src.url = url
            src.format = fmt
            src.moderation_status = status
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    main()
