from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command

from config import DB_NAME
from keyboards.admin_inline_keyboards import make_products_kb, make_confirm_kb
from states.admin_states import CategoryStates
from states.admin_states import ProductStates

from utils.database import Database

product_router = Router()
db = Database(DB_NAME)

@product_router.message(Command('products'))
async def products_list_handler(message: Message):
    await message.answer(
        text='All products',
        reply_markup=make_product_kb()
    )

@product_router.message(Command('add_product'))
async def add_product_handler(message: Message, state=FSMContext):
    await state.set_state(ProductStates.addProductState)
    await message.answer(text="Please enter: Product name, price, image of the product")

@product_router.message(ProductStates.addProductState)
async def insert_category_handler(message: Message, state=FSMContext):
    if db.check_product_exists(message.text):
        if db.add_product(new_product=message.text):
            await state.clear()
            await message.answer(
                f'New product {message.text} added successfully'
            )
        else:
            await message.test(
                f'Something went wrong, please try again later\n'
                f'click /cancel for calcellation, thanks'
                )


@product_router.message(Command('edit_product'))
async def edit_product_handler(message:Message, state= FSMContext):
    await state.set_state(ProductStates.startAddProductState)
    await message.answer(
        text="Select which product you want to edit: ",
        reply_markup=make_products_kb()
    )


@product_router.callback_query(ProductStates.startEditProductState)
async def select_product_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ProductStates.finishEditProductState)
    await state.update_data(cat_name=callback.data)
    await callback.message.edit_text(f"Please, send new name for product: \"{callback.data}\":")


@product_router.message(CategoryStates.finishEditCategoryState)
async def rename_product_handler(message: Message, state=FSMContext):
    if db.check_product_exists(message.text):
        all_data = await state.get_data()
        if db.rename_product(old_name=all_data.get('prod_name'), new_name=message.text):
            await state.clear()
            await  message.answer(
                f'Product name, price and images are changed successfully'
            )
    await message.answer(
        f'this category {message.text} already exists'
    )

@product_router.message(Command('del_product'))
async def del_product_handler(message: Message, state: FSMContext):
    await state.set_state(ProductStates.startDeleteProductState)
    await message.answer(
        text='Select the name of the product you want to delete: ',
        reply_markup=make_products_kb()
    )

product_router.callback_query(ProductStates.startDeleteProductState)
async def select_product_del_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ProductStates.finishEditProductState)
    await state.update_data(prod_name=callback.data)
    all_data = await state.get_data()
    if db.delete_category(all_data.get('cat_name')):
        await callback.message.answer("Category successfully deleted!")
        await callback.message.delete()
        await state.clear()
    else:
        await callback.message.answer(
            f"Something went wrong!"
            f"Try again later or click /cancel for cancel process!"
        )


