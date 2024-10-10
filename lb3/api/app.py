from aioodbc import Cursor
from fastapi import APIRouter
from pydantic import BaseModel

from lb3.dependencies import DbConnectionDep

router = APIRouter(prefix="/api")


class CreateGroupBody(BaseModel):
    name: str


@router.get("/groups")
async def list_groups(conn=DbConnectionDep, offset: int = 0, limit: int = 25):
    if limit > 100:
        limit = 100
    result = []

    cur: Cursor
    async with conn.cursor() as cur:
        await cur.execute("SELECT id, name FROM [group] ORDER BY id OFFSET ? ROWS FETCH NEXT ? ROWS ONLY;", offset, limit)
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


@router.patch("/groups/{group_id}")
async def edit_group(group_id: int, data: CreateGroupBody, conn=DbConnectionDep):
    async with conn.cursor() as cur:
        await cur.execute("UPDATE [group] SET name=? WHERE id=?;", data.name, group_id)

    return {
        "id": group_id,
        "name": data.name,
    }
