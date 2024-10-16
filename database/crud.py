from sqlmodel import select, desc, extract, func, or_
from .db import Session, get_db
from . import models
import calendar
from datetime import datetime, timedelta


def get_registered_pc_by_sys_uuid(db: Session, system_uuid: str):
    query = select(models.RegisteredPcs).where(models.RegisteredPcs.System_UUID == system_uuid)
    return db.exec(query).first()


def update_username(new_username, system_uuid):
    db: Session = get_db()
    try:
        # Check if the record exists
        registered_pc: models.RegisteredPcs = get_registered_pc_by_sys_uuid(db=db, system_uuid=system_uuid)

        if registered_pc:
            registered_pc.username_changed = True
            registered_pc.updated_username = new_username

            # update the existing record
            db.merge(registered_pc)
            db.commit()
            db.refresh(registered_pc)

            return registered_pc
        # record not found
        return registered_pc
    except Exception as e:
        print("add_target_pc in to db give Error: ", str(e))
        return None

    finally:
        db.close()


def add_target_pc(detected_pc_data):
    """
    :param detected_pc_data: contains information about who is logged in on that PC and its system UUID
    :return: stored or updated registered_pc
    """
    db: Session = get_db()

    try:
        system_uuid = detected_pc_data["system_uuid"]
        username = detected_pc_data["username"]
        users = detected_pc_data['users']

        # Check if the record exists
        registered_pc: models.RegisteredPcs = get_registered_pc_by_sys_uuid(db=db, system_uuid=system_uuid)

        if registered_pc is None:
            # If the record doesn't exist, create a new one
            registered_pc = models.RegisteredPcs(
                System_UUID=system_uuid,
                username=username,
                users=users
            )
            db.add(registered_pc)
        else:
            # Update the existing record
            if registered_pc.users == users:
                pass
            else:
                registered_pc.users = users  # Update users
                db.add(registered_pc)  # You can use `merge` or `add`, depending on the situation

        db.commit()
        db.refresh(registered_pc)
        return registered_pc

    except Exception as e:
        print("add_target_pc to db gave Error: ", str(e))
        db.rollback()

    finally:
        db.close()


def add_or_update_detected_pc(detected_pc_data, image_path: str):
    print("\nIn db image: ", image_path)
    # Create a database session
    db: Session = get_db()

    try:
        system_uuid = detected_pc_data["System_UUID"]
        username = detected_pc_data["platform_info"]["username"]
        timestamp = datetime.strptime(detected_pc_data["timestamp"], "%Y-%m-%d %H:%M:%S")
        # Check if the record exists
        registered_pc: models.RegisteredUniquePcs = get_registered_pc_by_sys_uuid(db=db, system_uuid=system_uuid)

        if registered_pc is None:
            # If the record doesn't exist, create a new one
            registered_pc = models.RegisteredUniquePcs(
                System_UUID=system_uuid,
                username=username,
                timestamp=timestamp,
                image_path=image_path,
                match_found=1  # Set match_found to 1 for a new record
            )
            db.add(registered_pc)
            db.commit()
            db.refresh(registered_pc)

            also_add_into_detection: models.DetectedPcs = models.DetectedPcs(System_UUID=system_uuid,
                                                                             detected_pc=detected_pc_data,
                                                                             username=username,
                                                                             timestamp=timestamp,
                                                                             image_path=image_path)
            db.add(also_add_into_detection)
            db.commit()
            db.refresh(also_add_into_detection)
            print("\nNew Unique recorde stored in db success...\n")
        else:
            # If the record exists, increment match_found
            registered_pc.match_found += 1
            registered_pc.image_path = image_path
            registered_pc.username = username
            registered_pc.timestamp = timestamp

            # update the existing record
            db.merge(registered_pc)
            db.commit()

            new_detection: models.DetectedPcs = models.DetectedPcs(System_UUID=system_uuid,
                                                                   detected_pc=detected_pc_data,
                                                                   username=username,
                                                                   timestamp=timestamp,
                                                                   image_path=image_path)
            db.add(new_detection)
            db.commit()
            db.refresh(new_detection)

            print("\nNew Detection stored in db success...\n")

    except Exception as e:
        print("add_or_update_detected_pc in to db give Error: ", str(e))

    finally:
        db.close()


def get_pc_from_db(system_uuid: str, current_page: int, db: Session):
    # Define the number of entries per page
    entries_per_page = 10

    # Calculate the offset based on the current page and number of entries per page
    offset = (current_page - 1) * entries_per_page

    # Retrieve entries from the database based on the specified System_UUID and pagination
    result = db.query(models.RegisteredPcs).filter_by(System_UUID=system_uuid).order_by(
        desc(models.RegisteredPcs.timestamp)).offset(offset).limit(entries_per_page).all()

    return result


def get_latest_unique_pcs(current_page: int, db: Session):
    try:
        # Define the number of entries per page
        entries_per_page = 10

        # Calculate the offset based on the current page and number of entries per page
        offset = (current_page - 1) * entries_per_page

        # Retrieve entries from the database for all users based on pagination
        result = db.query(models.RegisteredPcs).order_by(
            desc(models.RegisteredPcs.timestamp)).offset(offset).limit(entries_per_page).all()

        return result
    except Exception as e:
        print("get_latest_unique_pcs give Error: ", str(e))
        return None


def print_detected_pcs(db: Session):
    detected_pcs = db.exec(select(models.RegisteredPcs)).all()
    for pc in detected_pcs:
        print(pc)
