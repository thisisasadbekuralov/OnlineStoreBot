from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command

from config import DB_NAME
from keyboards.admin_inline_keyboards import make_products_kb, make_categories_kb
from states.admin_states import CategoryStates
from states.admin_states import ProductStates

from utils.database import Database

product_router = Router()
db = Database(DB_NAME)

@product_router.message(Command('products'))
async def products_list_handler(message: Message):
    await message.answer(
        text='All products',
        reply_markup=make_products_kb()
    )

@product_router.message(Command('add_product'))
async def add_product_handler(message: Message, state=FSMContext):
    await state.set_state(ProductStates.add_SelectCategoryProdState)
    await message.answer(
        text="Please select the category which you want to add a product to:",
        reply_markup=make_categories_kb()
    )

@product_router.callback_query(ProductStates.add_SelectCategoryProdState)
async def insert_category_handler(query: CallbackQuery, state=FSMContext):
    await state.update_data(product_category=query.data)
    await state.set_state(ProductStates.add_TitleProdState)
    await query.messege.text('Please enter the name of the product: ')
    await query.messege.delete



@product_router.message(ProductStates.add_TitleProdState)
async def add_title_product_handler(message: Message, state: FSMContext):
    if message.text:
        await state.update_data(product_title=message.text)
        await state.set_state(ProductStates.add_TextProdState)
        await message.text('Please enter the full description of the product')
    else:
        await message.answer("Please enter only text...")


@product_router.message(ProductStates.add_TextProdState)
async def add_text_product_handler(message: Message, state: FSMContext):
    if message.text:
        await state.update_data(product_text=message.text)
        await state.set_state(ProductStates.add_ImageProdState)
        await message.text('Please send the image of the product: ')
    else:
        await message.answer("Please send only photo")


@product_router.message(ProductStates.add_ImageProdState)
async def add_image_product_handler(message: Message, state: FSMContext):
    if message.photo:
        await state.update_data(product_photo=message.photo)
        await state.set_state(ProductStates.add_PriceProdState)
        await message.text('Please send the price of the product')
    else:
        await message.answer("Please send only text...")


@product_router.message(ProductStates.add_PriceProdState)
async def add_phone_product_handler(message: Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(product_price=int(message.text))
        await state.set_state(ProductStates.add_PhoneProdState)
        await message.text('Please send the image of the product')
    else:
        await message.answer("Please send only numbers...")

@product_router.message(ProductStates.add_PhoneProdState)
async def add_phone_product_handler(message: Message, state: FSMContext):
    if message.text or message.contact:
        phone = message.text if message.text else message.contact.phone_number
        all_data = await state.get_data()
        results = db.add_product(title=all_data.get('product_title'),
                                 text=all_data.get('product_title'),
                                 image=all_data.get('product_image'),
                                 price=all_data.get('product_price'),
                                 phone=phone,
                                 cat_id=all_data.get('product_category'),
                                 u_id=message.from_user.id)

    else:
        message.text('please send your contact info')


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


