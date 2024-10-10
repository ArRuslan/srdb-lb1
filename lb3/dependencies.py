from aioodbc import Connection, Cursor
from fastapi import Depends, HTTPException

from .db import DatabasePool


async def db_connection() -> Connection:
    async with DatabasePool.get_instance().acquire() as conn:
        yield conn


DbConnectionDep: Connection = Depends(db_connection)


async def group_must_exist(group_id: int, conn=DbConnectionDep) -> None:
    cur: Cursor
    async with conn.cursor() as cur:
        await cur.execute("SELECT COUNT(*) FROM [group] WHERE id=?;", group_id)
        row = await cur.fetchone()
        if not row[0]:
            raise HTTPException(404, "Group not found!")


async def subject_must_exist(subject_id: int, conn=DbConnectionDep) -> None:
    cur: Cursor
    async with conn.cursor() as cur:
        await cur.execute("SELECT COUNT(*) FROM subject WHERE id=?;", subject_id)
        row = await cur.fetchone()
        if not row[0]:
            raise HTTPException(404, "Subject not found!")


async def teacher_must_exist(teacher_id: int, conn=DbConnectionDep) -> None:
    cur: Cursor
    async with conn.cursor() as cur:
        await cur.execute("SELECT COUNT(*) FROM teacher WHERE id=?;", teacher_id)
        row = await cur.fetchone()
        if not row[0]:
            raise HTTPException(404, "Teacher not found!")


GroupMustExistDep = Depends(group_must_exist)
SubjectMustExistDep = Depends(subject_must_exist)
TeacherMustExistDep = Depends(teacher_must_exist)
