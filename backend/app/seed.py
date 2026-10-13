"""Load a small, repeatable set of classroom demo records."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import engine
from .models import Equipment, Incident

EQUIPMENT = [
    ("ECE-OSC-04", "Digital oscilloscope", "Electronics Lab 2", "Measurement"),
    ("ECE-PSU-02", "Bench power supply", "Electronics Lab 2", "Power"),
    ("MECH-PRN-07", "3D printer", "Prototyping Lab", "Fabrication"),
    ("CHEM-BAL-01", "Analytical balance", "Chemistry Lab 1", "Measurement"),
    ("COMP-GPU-03", "GPU workstation", "Computing Lab", "Computing"),
    ("ROB-ARM-02", "Robotic arm", "Robotics Lab", "Automation"),
]


def seed() -> None:
    with Session(engine) as session:
        equipment_by_code = {}
        for code, name, room, category in EQUIPMENT:
            item = session.scalar(select(Equipment).where(Equipment.code == code))
            if item is None:
                item = Equipment(code=code, name=name, room=room, category=category)
                session.add(item)
                session.flush()
            equipment_by_code[code] = item

        records = [
            ("ECE-OSC-04", "Probe channel reads zero", "Channel B stayed flat during the afternoon practical.", "high", "open", "Electronics lab"),
            ("MECH-PRN-07", "Print bed needs recalibration", "First layers are lifting on the left edge.", "medium", "in_progress", "Workshop desk"),
            ("CHEM-BAL-01", "Level indicator was drifting", "The feet were adjusted and the balance was checked again.", "low", "resolved", "Chemistry lab"),
        ]
        for code, title, detail, severity, status, reporter in records:
            equipment = equipment_by_code[code]
            exists = session.scalar(
                select(Incident.id).where(
                    Incident.equipment_id == equipment.id, Incident.title == title
                )
            )
            if exists is None:
                session.add(
                    Incident(
                        equipment_id=equipment.id,
                        title=title,
                        detail=detail,
                        severity=severity,
                        status=status,
                        reported_by=reporter,
                    )
                )

        # Derive the display status from the incidents that are still active.
        # This keeps a resolved demo incident resolved after a container restart.
        session.flush()
        for equipment in equipment_by_code.values():
            active = session.scalars(
                select(Incident.severity).where(
                    Incident.equipment_id == equipment.id,
                    Incident.status != "resolved",
                )
            ).all()
            equipment.status = (
                "offline"
                if any(level in ("high", "critical") for level in active)
                else "attention" if active else "operational"
            )
        session.commit()


if __name__ == "__main__":
    seed()
