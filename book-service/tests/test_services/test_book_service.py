import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from sqlalchemy import select
from book_service.services import books as book_service
from book_service.schemas.book import BookCreate, BookUpdate
from book_service.models.book import Book


@pytest.mark.anyio
async def test_create_book(db_session: AsyncSession):
    data = BookCreate(title="Dune", author="Frank Herbert", stock=10, price=29.99)
    book = await book_service.create_book(data, db_session)
    assert book.id is not None
    assert book.title == "Dune"
    assert book.author == "Frank Herbert"
    assert book.stock == 10
    assert float(book.price) == 29.99


@pytest.mark.anyio
async def test_create_book_persisted(db_session: AsyncSession):
    data = BookCreate(title="1984", author="George Orwell", stock=5, price=14.99)
    book = await book_service.create_book(data, db_session)
    result = await db_session.execute(select(Book).where(Book.id == book.id))
    db_book = result.scalar_one()
    assert db_book.title == "1984"
    assert db_book.author == "George Orwell"
    assert db_book.stock == 5
    assert float(db_book.price) == 14.99


@pytest.mark.anyio
async def test_get_all_books_empty(db_session: AsyncSession):
    books = await book_service.get_all_books(db_session)
    assert books == []


@pytest.mark.anyio
async def test_get_all_books_multiple(db_session: AsyncSession):
    await book_service.create_book(
        BookCreate(title="Book A", author="Author A", stock=1, price=9.99), db_session
    )
    await book_service.create_book(
        BookCreate(title="Book B", author="Author B", stock=2, price=19.99), db_session
    )
    books = await book_service.get_all_books(db_session)
    assert len(books) == 2


@pytest.mark.anyio
async def test_get_book_success(db_session: AsyncSession):
    book = await book_service.create_book(
        BookCreate(title="Dune", author="Frank Herbert", stock=10, price=29.99),
        db_session,
    )
    fetched = await book_service.get_book(book.id, db_session)
    assert fetched.id == book.id
    assert fetched.title == "Dune"
    assert fetched.author == "Frank Herbert"


@pytest.mark.anyio
async def test_get_book_not_found(db_session: AsyncSession):
    with pytest.raises(NoResultFound):
        await book_service.get_book(999, db_session)


@pytest.mark.anyio
async def test_update_book_full(db_session: AsyncSession):
    book = await book_service.create_book(
        BookCreate(title="Old Title", author="Old Author", stock=1, price=9.99),
        db_session,
    )
    updated = await book_service.update_book(
        book.id,
        BookUpdate(title="New Title", author="New Author", stock=99, price=49.99),
        db_session,
    )
    assert updated.title == "New Title"
    assert updated.author == "New Author"
    assert updated.stock == 99
    assert float(updated.price) == 49.99


@pytest.mark.anyio
async def test_update_book_partial_title(db_session: AsyncSession):
    book = await book_service.create_book(
        BookCreate(title="Old Title", author="Author", stock=5, price=9.99), db_session
    )
    updated = await book_service.update_book(
        book.id, BookUpdate(title="New Title"), db_session
    )
    assert updated.title == "New Title"
    assert updated.author == "Author"
    assert updated.stock == 5
    assert float(updated.price) == 9.99


@pytest.mark.anyio
async def test_update_book_partial_stock(db_session: AsyncSession):
    book = await book_service.create_book(
        BookCreate(title="Title", author="Author", stock=5, price=9.99), db_session
    )
    updated = await book_service.update_book(
        book.id, BookUpdate(stock=100), db_session
    )
    assert updated.title == "Title"
    assert updated.stock == 100


@pytest.mark.anyio
async def test_update_book_partial_price(db_session: AsyncSession):
    book = await book_service.create_book(
        BookCreate(title="Title", author="Author", stock=5, price=9.99), db_session
    )
    updated = await book_service.update_book(
        book.id, BookUpdate(price=99.99), db_session
    )
    assert updated.title == "Title"
    assert float(updated.price) == 99.99


@pytest.mark.anyio
async def test_update_book_not_found(db_session: AsyncSession):
    result = await book_service.update_book(999, BookUpdate(title="x"), db_session)
    assert result is None


@pytest.mark.anyio
async def test_update_book_no_fields(db_session: AsyncSession):
    book = await book_service.create_book(
        BookCreate(title="Title", author="Author", stock=5, price=9.99), db_session
    )
    result = await book_service.update_book(
        book.id,
        BookUpdate(),  # empty payload
        db_session,
    )
    assert result is None


@pytest.mark.anyio
async def test_delete_book_success(db_session: AsyncSession):
    book = await book_service.create_book(
        BookCreate(title="Title", author="Author", stock=5, price=9.99), db_session
    )
    result = await book_service.delete_book(book.id, db_session)
    assert result is True
    # verify deletion
    res = await db_session.execute(select(Book).where(Book.id == book.id))
    assert res.scalar_one_or_none() is None


@pytest.mark.anyio
async def test_delete_book_not_found(db_session: AsyncSession):
    with pytest.raises(NoResultFound):
        await book_service.delete_book(999, db_session)
