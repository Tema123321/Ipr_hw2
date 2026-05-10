import pytest
from sqlalchemy.exc import IntegrityError

from src.links import crud
from tests.conftest import TestingSessionLocal


@pytest.mark.asyncio
async def test_generate_short_id_default_length():
    short_id = crud.generate_short_id()

    assert isinstance(short_id, str)
    assert len(short_id) == 6


@pytest.mark.asyncio
async def test_generate_short_id_custom_length():
    short_id = crud.generate_short_id(10)

    assert len(short_id) == 10


@pytest.mark.asyncio
async def test_create_link_crud():
    async with TestingSessionLocal() as session:
        link = await crud.create_link(
            db=session,
            original_url="https://crud-test.com",
            custom_alias="crudalias"
        )

        assert link.original_url == "https://crud-test.com"
        assert link.short_id == "crudalias"


@pytest.mark.asyncio
async def test_create_link_duplicate_alias():
    async with TestingSessionLocal() as session:
        await crud.create_link(
            db=session,
            original_url="https://first.com",
            custom_alias="duplicate"
        )

        with pytest.raises(NotUniqueAliasError):
            await crud.create_link(
                db=session,
                original_url="https://second.com",
                custom_alias="duplicate"
            )


@pytest.mark.asyncio
async def test_get_link_by_short_id():
    async with TestingSessionLocal() as session:
        await crud.create_link(
            db=session,
            original_url="https://lookup.com",
            custom_alias="lookup"
        )

        link = await crud.get_link_by_short_id(session, "lookup")

        assert link is not None
        assert link.original_url == "https://lookup.com"


@pytest.mark.asyncio
async def test_increment_click_count():
    async with TestingSessionLocal() as session:
        link = await crud.create_link(
            db=session,
            original_url="https://clicks.com",
            custom_alias="clicks"
        )

        previous = link.click_count

        await crud.increment_click_count(session, link)

        updated = await crud.get_link_by_short_id(session, "clicks")

        assert updated.click_count == previous + 1


@pytest.mark.asyncio
async def test_update_link_crud():
    async with TestingSessionLocal() as session:
        link = await crud.create_link(
            db=session,
            original_url="https://before.com",
            custom_alias="before"
        )

        updated = await crud.update_link(
            db=session,
            link=link,
            new_url="https://after.com"
        )

        assert updated.original_url == "https://after.com"


@pytest.mark.asyncio
async def test_delete_link_crud():
    async with TestingSessionLocal() as session:
        link = await crud.create_link(
            db=session,
            original_url="https://deletecrud.com",
            custom_alias="deletecrud"
        )

        await crud.delete_link(session, link)

        deleted = await crud.get_link_by_short_id(session, "deletecrud")

        assert deleted is None


from src.links.exceptions import NotUniqueAliasError


@pytest.mark.asyncio
async def test_create_link_not_unique_alias_branch():
    async with TestingSessionLocal() as session:
        first = await crud.create_link(
            db=session,
            original_url="https://blabla.com",
            custom_alias="abc"
        )

        first.custom_alias = "abc"

        await session.commit()
        await session.refresh(first)

        with pytest.raises(NotUniqueAliasError):
            await crud.create_link(
                db=session,
                original_url="https://bla.com",
                custom_alias="abc"
            )

@pytest.mark.asyncio
async def test_search_links_crud():
    async with TestingSessionLocal() as session:
        link = await crud.create_link(
            db=session,
            original_url="https://google.com/search",
            custom_alias="searchcrud",
            user_id=1
        )

        results = await crud.search_links(
            db=session,
            original_url="google",
            user_id=1
        )

        assert len(results) == 1
        assert results[0].short_id == link.short_id