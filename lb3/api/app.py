from datetime import date, timedelta

from aioodbc import Cursor
from fastapi import APIRouter
from pydantic import BaseModel

from ..dependencies import DbConnectionDep, GroupMustExistDep, SubjectMustExistDep, TeacherMustExistDep

router = APIRouter(prefix="/api")


class CreateGroupBody(BaseModel):
    name: str


class CreateSubjectBody(BaseModel):
    name: str
    short_name: str


class CreateTeacherBody(BaseModel):
    first_name: str
    last_name: str


@router.get("/groups")
async def list_groups(conn=DbConnectionDep, offset: int = 0, limit: int = 25):
    if limit > 100:
        limit = 100
    result = []

    cur: Cursor
    async with conn.cursor() as cur:
        await cur.execute(
            "SELECT id, name FROM [group] ORDER BY id OFFSET ? ROWS FETCH NEXT ? ROWS ONLY;", offset, limit
        )
        while (row := await cur.fetchone()) is not None:
            group_id, name = row
            result.append({
                "id": group_id,
                "name": name,
            })

    return result


@router.post("/groups")
async def create_group(data: CreateGroupBody, conn=DbConnectionDep):
    cur: Cursor
    async with conn.cursor() as cur:
        await cur.execute("INSERT INTO [group](name) OUTPUT inserted.id VALUES(?);", data.name)
        row = await cur.fetchone()

    return {
        "id": row[0],
        "name": data.name,
    }


@router.get("/groups/{group_id}", dependencies=[GroupMustExistDep])
async def get_group(group_id: int, conn=DbConnectionDep):
    async with conn.cursor() as cur:
        await cur.execute("SELECT name FROM [group] WHERE id=?;", group_id)
        name = (await cur.fetchone())[0]

    return {
        "id": group_id,
        "name": name,
    }


@router.patch("/groups/{group_id}", dependencies=[GroupMustExistDep])
async def edit_group(group_id: int, data: CreateGroupBody, conn=DbConnectionDep):
    async with conn.cursor() as cur:
        await cur.execute("UPDATE [group] SET name=? WHERE id=?;", data.name, group_id)

    return {
        "id": group_id,
        "name": data.name,
    }


# TODO: add learning hours per week/month calculation (as function?)
@router.get("/groups/{group_id}/schedule", dependencies=[GroupMustExistDep])
async def get_group_schedule_for_current_month(group_id: int, conn=DbConnectionDep):
    result = []

    cur: Cursor
    async with conn.cursor() as cur:
        await cur.execute(
            "SELECT schedule_item_id, teacher_id, teacher_first_name, teacher_last_name, subject_id, subject_name, "
            "subject_short_name, [date], [position], [type] FROM get_group_schedule_for_current_month(?);",
            (group_id,)
        )
        while (row := await cur.fetchone()) is not None:
            schedule_item_id, teacher_id, teacher_first_name, teacher_last_name, subject_id, subject_name, \
                subject_short_name, date_, position, type_ = row
            result.append({
                "id": schedule_item_id,
                "teacher": {
                    "id": teacher_id,
                    "first_name": teacher_first_name,
                    "last_name": teacher_last_name,
                },
                "subject": {
                    "id": subject_id,
                    "name": subject_name,
                    "short_name": subject_short_name,
                },
                "date": date_.isoformat(),
                "position": position,
                "type": type_,
            })

    return result


@router.get("/subjects")
async def list_subjects(conn=DbConnectionDep, offset: int = 0, limit: int = 25):
    if limit > 100:
        limit = 100
    result = []

    cur: Cursor
    async with conn.cursor() as cur:
        await cur.execute(
            "SELECT id, name, short_name FROM subject ORDER BY id OFFSET ? ROWS FETCH NEXT ? ROWS ONLY;", offset, limit
        )
        while (row := await cur.fetchone()) is not None:
            subject_id, name, short_name = row
            result.append({
                "id": subject_id,
                "name": name,
                "short_name": short_name,
            })

    return result


@router.post("/subjects")
async def create_subject(data: CreateSubjectBody, conn=DbConnectionDep):
    cur: Cursor
    async with conn.cursor() as cur:
        await cur.execute(
            "INSERT INTO subject(name, short_name) OUTPUT inserted.id VALUES(?, ?);", data.name, data.short_name
        )
        row = await cur.fetchone()

    return {
        "id": row[0],
        "name": data.name,
        "short_name": data.short_name,
    }


@router.get("/subjects/{subject_id}", dependencies=[SubjectMustExistDep])
async def get_subject(subject_id: int, conn=DbConnectionDep):
    async with conn.cursor() as cur:
        await cur.execute("SELECT name, short_name FROM subject WHERE id=?;", subject_id)
        name, short_name = await cur.fetchone()

    return {
        "id": subject_id,
        "name": name,
        "short_name": short_name,
    }


@router.patch("/subjects/{subject_id}", dependencies=[SubjectMustExistDep])
async def edit_subject(subject_id: int, data: CreateSubjectBody, conn=DbConnectionDep):
    async with conn.cursor() as cur:
        await cur.execute("UPDATE subject SET name=?, short_name=? WHERE id=?;", data.name, data.short_name, subject_id)

    return {
        "id": subject_id,
        "name": data.name,
        "short_name": data.short_name,
    }


@router.get("/teachers")
async def list_teachers(conn=DbConnectionDep, offset: int = 0, limit: int = 25):
    if limit > 100:
        limit = 100
    result = []

    cur: Cursor
    async with conn.cursor() as cur:
        await cur.execute(
            "SELECT id, first_name, last_name, info FROM teacher ORDER BY id OFFSET ? ROWS FETCH NEXT ? ROWS ONLY;",
            offset, limit
        )
        while (row := await cur.fetchone()) is not None:
            teacher_id, first_name, last_name, info = row
            result.append({
                "id": teacher_id,
                "first_name": first_name,
                "last_name": last_name,
                "info": info,
            })

    return result


@router.post("/teachers")
async def create_teacher(data: CreateTeacherBody, conn=DbConnectionDep):
    cur: Cursor
    async with conn.cursor() as cur:
        await cur.execute(
            "INSERT INTO teacher(first_name, last_name) OUTPUT inserted.id VALUES(?, ?);", data.first_name, data.last_name
        )
        row = await cur.fetchone()

    return {
        "id": row[0],
        "first_name": data.first_name,
        "last_name": data.last_name,
        "info": None,
    }


@router.get("/teachers/{teacher_id}", dependencies=[TeacherMustExistDep])
async def get_teacher(teacher_id: int, conn=DbConnectionDep):
    async with conn.cursor() as cur:
        await cur.execute("SELECT first_name, last_name, info FROM teacher WHERE id=?;", teacher_id)
        first_name, last_name, info = await cur.fetchone()

    return {
        "id": teacher_id,
        "first_name": first_name,
        "last_name": last_name,
        "info": info,
    }


@router.patch("/teachers/{teacher_id}", dependencies=[TeacherMustExistDep])
async def edit_teacher(teacher_id: int, data: CreateTeacherBody, conn=DbConnectionDep):
    async with conn.cursor() as cur:
        await cur.execute(
            "UPDATE teacher SET first_name=?, last_name=? WHERE id=?;", data.first_name, data.last_name, teacher_id
        )
        await cur.execute("SELECT info FROM teacher WHERE id=?;", teacher_id)
        row = await cur.fetchone()

    return {
        "id": teacher_id,
        "first_name": data.first_name,
        "last_name": data.last_name,
        "info": row[0],
    }
