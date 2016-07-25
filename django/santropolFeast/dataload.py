# -*- coding: utf-8 -*-
import aldjemy.core as ac
from sqlalchemy.orm import sessionmaker, aliased
from sqlalchemy import func, or_, and_

import datetime
import io
import sys

from meal.models import Component, Restricted_item, Ingredient
from meal.models import Component_ingredient, Incompatibility
from meal.models import Menu, Menu_component
from member.models import Member, Client, Contact, Address, Note, Referencing
from member.models import Route, Note, Option, Client_option, Restriction
from member.models import Client_avoid_ingredient, Client_avoid_component
from notification.models import Notification
from order.models import Order, Order_item


def print_all_cols(q):
    pass
    # print("\n---------------------------------------------------------\n", q)
    # for row in q:
    #     d = row.__dict__
    #     # filter out SQLAlchemy "internal" columns to get "result" dict
    #     fd = { k:v for (k,v) in d.items()
    #            if not str(k).startswith("_") }
    #     print("Row ", fd)


def print_rows(q, heading=""):
    pass
    # print("\n-----------------------------------------------------\n",
    #       # q, "\n",
    #       heading)
    # for row in q.all():
    #     print(row)


def insert_all():
    print("\nSTART dataload")
    engine = ac.get_engine()
    Session = sessionmaker(bind=engine)
    db = Session()

    # meal app
    Ingredient.objects.all().delete()
    Component.objects.all().delete()
    Component_ingredient.objects.all().delete()
    Restricted_item.objects.all().delete()
    Incompatibility.objects.all().delete()
    Menu.objects.all().delete()
    Menu_component.objects.all().delete()

    # member app
    Member.objects.all().delete()
    Address.objects.all().delete()
    Contact.objects.all().delete()
    Client.objects.all().delete()
    Referencing.objects.all().delete()
    Note.objects.all().delete()
    Option.objects.all().delete()
    Client_option.objects.all().delete()
    Restriction.objects.all().delete()
    Client_avoid_ingredient.objects.all().delete()
    Client_avoid_component.objects.all().delete()
    Route.objects.all().delete()

    # notification app
    Notification.objects.all().delete()

    # order app
    Order.objects.all().delete()
    Order_item.objects.all().delete()

    # -----------------------------------------------------------------------------
    ing_1 = Ingredient(
        name='Onion',
        ingredient_group='veggies and fruits')
    ing_1.save()
    ing_2 = Ingredient(
        name='Pepper',
        ingredient_group='spices')
    ing_2.save()
    ing_3 = Ingredient(
        name='Ground porc',
        ingredient_group='meat')
    ing_3.save()
    ing_4 = Ingredient(
        name='Ground beef',
        ingredient_group='meat')
    ing_4.save()
    ing_5 = Ingredient(
        name='Chicken thighs',
        ingredient_group='meat')
    ing_5.save()
    ing_6 = Ingredient(
        name='Turkey thighs',
        ingredient_group='meat')
    ing_6.save()
    ing_7 = Ingredient(
        name='Porc toulouse sausage',
        ingredient_group='meat')
    ing_7.save()
    ing_8 = Ingredient(
        name='Beef cubes',
        ingredient_group='meat')
    ing_8.save()
    ing_9 = Ingredient(
        name='Lamb cubes',
        ingredient_group='meat')
    ing_9.save()
    ing_10 = Ingredient(
        name='Ham',
        ingredient_group='meat')
    ing_10.save()
    ing_11 = Ingredient(
        name='Pork cubes',
        ingredient_group='meat')
    ing_11.save()
    ing_12 = Ingredient(
        name='Cheese : Feta',
        ingredient_group='dairy')
    ing_12.save()
    ing_13 = Ingredient(
        name='Cheese : Cheddar',
        ingredient_group='dairy')
    ing_13.save()
    ing_14 = Ingredient(
        name='Cheese : Parmesan',
        ingredient_group='dairy')
    ing_14.save()
    ing_15 = Ingredient(
        name='Cheese : Blue cheese',
        ingredient_group='dairy')
    ing_15.save()
    ing_16 = Ingredient(
        name='Cheese : Mozzarella',
        ingredient_group='dairy')
    ing_16.save()
    ing_17 = Ingredient(
        name='Cheese : Bocconcini',
        ingredient_group='dairy')
    ing_17.save()
    ing_18 = Ingredient(
        name='Cheese : Ricotta',
        ingredient_group='dairy')
    ing_18.save()
    ing_19 = Ingredient(
        name='Cheese : Cottage cheese',
        ingredient_group='dairy')
    ing_19.save()
    ing_20 = Ingredient(
        name='Milk',
        ingredient_group='dairy')
    ing_20.save()
    ing_21 = Ingredient(
        name='Lactose-free milk',
        ingredient_group='dairy')
    ing_21.save()
    ing_22 = Ingredient(
        name='Butter',
        ingredient_group='dairy')
    ing_22.save()
    ing_23 = Ingredient(
        name='soy sauce',
        ingredient_group='oils and sauces')
    ing_23.save()
    ing_24 = Ingredient(
        name='green peppers',
        ingredient_group='veggies and fruits')
    ing_24.save()
    ing_25 = Ingredient(
        name='sesame seeds',
        ingredient_group='dry and canned goods')
    ing_25.save()
    #
    print_all_cols(db.query(Ingredient.sa))
    print_rows(Ingredient.objects)

    # -----------------------------------------------------------------------------
    com_1 = Component(
        name='Coq au vin',
        component_group='main_dish')
    com_1.save()
    com_2 = Component(
        name='Meat pie',
        component_group='main_dish')
    com_2.save()
    com_3 = Component(
        name='Vegetable fried rice',
        component_group='main_dish')
    com_3.save()
    com_4 = Component(
        name='Sausage cassoulet',
        component_group='main_dish')
    com_4.save()
    com_5 = Component(
        name='Fish chowder',
        component_group='main_dish')
    com_5.save()
    com_6 = Component(
        name='Ginger pork',
        component_group='main_dish')
    com_6.save()
    com_7 = Component(
        name='Beef Meatloaf',
        component_group='main_dish')
    com_7.save()
    com_8 = Component(
        name='Day s Dessert',
        component_group='dessert')
    com_8.save()
    com_9 = Component(
        name='Day s Diabetic Dessert',
        component_group='diabetic dessert')
    com_9.save()
    com_10 = Component(
        name='Fruit Salad',
        component_group='fruit_salad')
    com_10.save()
    com_11 = Component(
        name='Green Salad',
        component_group='green_salad')
    com_11.save()
    com_12 = Component(
        name='Lemon Pudding',
        component_group='pudding')
    com_12.save()
    #
    print_all_cols(db.query(Component.sa))
    print_rows(Component.objects)

    # -----------------------------------------------------------------------------
    men_1 = Menu(
        date=datetime.date(2016, 7, 15))
    men_1.save()
    men_2 = Menu(
        date=datetime.date(2016, 7, 16))
    men_2.save()
    #
    print_all_cols(db.query(Menu.sa))
    print_rows(Menu.objects)

    # -----------------------------------------------------------------------------
    men_com_1 = Menu_component(
        menu=men_1, component=com_6)
    men_com_1.save()
    men_com_2 = Menu_component(
        menu=men_1, component=com_10)
    men_com_2.save()
    men_com_3 = Menu_component(
        menu=men_1, component=com_11)
    men_com_3.save()
    men_com_3 = Menu_component(
        menu=men_1, component=com_12)
    men_com_3.save()
    men_com_4 = Menu_component(
        menu=men_1, component=com_8)
    men_com_4.save()
    men_com_5 = Menu_component(
        menu=men_1, component=com_9)
    men_com_5.save()
    #
    print_all_cols(db.query(Menu_component.sa))
    print_rows(Menu_component.objects)

    # -----------------------------------------------------------------------------
    com_ing_1 = Component_ingredient(
        component=com_6, ingredient=ing_3)
    com_ing_1.save()
    com_ing_2 = Component_ingredient(
        component=com_6, ingredient=ing_23)
    com_ing_2.save()
    com_ing_3 = Component_ingredient(
        component=com_6, ingredient=ing_24)
    com_ing_3.save()
    com_ing_4 = Component_ingredient(
        component=com_6, ingredient=ing_25)
    com_ing_4.save()
    com_ing_5 = Component_ingredient(
        component=com_6, ingredient=ing_1)
    com_ing_5.save()
    #
    print_all_cols(db.query(Component_ingredient.sa))
    print_rows(Component_ingredient.objects)

    # -----------------------------------------------------------------------------
    ri_1 = Restricted_item(
        name='onion',
        restricted_item_group='vegetables',
        description='')
    ri_1.save()
    ri_2 = Restricted_item(
        name='pork',
        restricted_item_group='veggies and fruits',
        description='')
    ri_2.save()
    ri_3 = Restricted_item(
        name='soya',
        restricted_item_group='other',
        description='')
    ri_3.save()
    ri_4 = Restricted_item(
        name='soy sauce',
        restricted_item_group='other',
        description='gluten, salt')
    ri_4.save()
    ri_5 = Restricted_item(
        name='seeds',
        restricted_item_group='veggies and fruits',
        description='text')
    ri_5.save()
    ri_6 = Restricted_item(
        name='sesame',
        restricted_item_group='veggies and fruits',
        description='text')
    ri_6.save()
    ri_7 = Restricted_item(
        name='green veggies',
        restricted_item_group='veggies and fruits',
        description='text')
    ri_7.save()
    ri_8 = Restricted_item(
        name='brussel sprouts',
        restricted_item_group='veggies and fruits',
        description='text')
    ri_8.save()
    #
    print_all_cols(db.query(Restricted_item.sa))
    print_rows(Restricted_item.objects)

    # -----------------------------------------------------------------------------
    inc_1 = Incompatibility(
        restricted_item=ri_1, ingredient=ing_1)
    inc_1.save()
    inc_2 = Incompatibility(
        restricted_item=ri_2, ingredient=ing_3)
    inc_2.save()
    inc_3 = Incompatibility(
        restricted_item=ri_3, ingredient=ing_23)
    inc_3.save()
    inc_4 = Incompatibility(
        restricted_item=ri_4, ingredient=ing_23)
    inc_4.save()
    inc_5 = Incompatibility(
        restricted_item=ri_5, ingredient=ing_25)
    inc_5.save()
    inc_6 = Incompatibility(
        restricted_item=ri_6, ingredient=ing_25)
    inc_6.save()
    #
    print_all_cols(db.query(Incompatibility.sa))
    print_rows(Incompatibility.objects)
    # -----------------------------------------------------------------------------
    men_1 = Menu(
        date=datetime.date(2016, 5, 21))
    men_1.save()
    men_2 = Menu(
        date=datetime.date(2016, 5, 28))
    men_2.save()
    #
    print_all_cols(db.query(Menu.sa))
    print_rows(Menu.objects)
    # -----------------------------------------------------------------------------
    men_com_1 = Menu_component(
        component=com_6, menu=men_1)
    men_com_1.save()
    men_com_1 = Menu_component(
        component=com_7, menu=men_2)
    men_com_1.save()
    #
    print_all_cols(db.query(Menu_component.sa))
    print_rows(Menu_component.objects)

    # -----------------------------------------------------------------------------
    add_1 = Address(
        number=2444,
        street='Des Perdrix',
        apartment='407',
        floor=10,
        city='Montreal',
        postal_code='H1A2B3')
    add_1.save()
    add_2 = Address(
        number=1244,
        street='Des Hirondelles',
        apartment='4',
        city='Montreal',
        postal_code='H3D4G6')
    add_2.save()
    add_3 = Address(
        number=543,
        street='Des Éperviers',
        apartment='',
        city='Montreal',
        postal_code='H4E3WS')
    add_3.save()
    add_4 = Address(
        number=6543,
        street='Des Moineaux',
        apartment='1',
        city='Montreal',
        postal_code='H5R7H8')
    add_4.save()
    #
    print_all_cols(db.query(Address.sa))
    print_rows(Address.objects)

    # -----------------------------------------------------------------------------
    mem_1 = Member(
        firstname='John',
        lastname='Doe',
        address=add_1)
    mem_1.save()
    mem_2 = Member(
        firstname='Louise',
        lastname='Dallaire',
        address=add_2)
    mem_2.save()
    mem_3 = Member(
        firstname='Paul',
        lastname='Taylor',
        address=add_4)
    mem_3.save()
    mem_4 = Member(
        firstname='Peter',
        lastname='Murray',
        address=add_3)
    mem_4.save()
    mem_5 = Member(
        firstname='Dr. Lucie',
        lastname='Tremblay')
    mem_5.save()
    mem_6 = Member(
        firstname='Dr. Mary',
        lastname='Johnson')
    mem_6.save()
    #
    print_all_cols(db.query(Member.sa))
    print_rows(Member.objects)

    # -----------------------------------------------------------------------------
    con_1 = Contact(
        member=mem_1,
        type='Home phone',
        value='514-345-6789')
    con_1.save()
    con_2 = Contact(
        member=mem_2,
        type='Cell phone',
        value='438-234-4567')
    con_2.save()
    con_3 = Contact(
        member=mem_4,
        type='Home phone',
        value='514-654-1289')
    con_3.save()
    #
    print_all_cols(db.query(Contact.sa))
    print_rows(Contact.objects)

    # -----------------------------------------------------------------------------
    cli_1 = Client(
        member=mem_1,
        billing_member=mem_2,
        emergency_contact=mem_3,
        billing_payment_type='check',
        rate_type='Low income',
        emergency_contact_relationship='Nephew',
        status='A',
        language='en',
        alert='',
        delivery_type='O',
        gender='M',
        birthdate=datetime.date(1940, 2, 23))
    cli_1.save()
    cli_1.set_meal_defaults('main_dish', 4, 2, 'L')
    cli_1.set_meal_defaults('dessert', 4, 1, '')
    cli_1.set_meal_defaults('diabetic dessert', 4, 0, '')
    cli_1.set_meal_defaults('fruit_salad', 4, 0, '')
    cli_1.set_meal_defaults('green_salad', 4, 1, '')
    cli_1.set_meal_defaults('pudding', 4, 1, '')
    cli_1.set_meal_defaults('compote', 4, 0, '')
    cli_1.save()
    cli_2 = Client(
        member=mem_4,
        billing_member=mem_4,
        billing_payment_type='check',
        rate_type='Low income',
        emergency_contact_relationship='',
        status='A',
        language='en',
        alert='',
        delivery_type='O',
        gender='M',
        birthdate=datetime.date(1945, 12, 13))
    cli_2.save()
    cli_2.set_meal_defaults('main_dish', 4, 1, 'R')
    cli_2.set_meal_defaults('dessert', 4, 1, '')
    cli_2.set_meal_defaults('diabetic dessert', 4, 0, '')
    cli_2.set_meal_defaults('fruit_salad', 4, 0, '')
    cli_2.set_meal_defaults('green_salad', 4, 0, '')
    cli_2.set_meal_defaults('pudding', 4, 0, '')
    cli_2.set_meal_defaults('compote', 4, 0, '')
    cli_2.save()
    cli_3 = Client(
        member=mem_2,
        billing_member=mem_2,
        billing_payment_type='check',
        rate_type='Low income',
        emergency_contact_relationship='',
        status='A',
        language='en',
        alert='',
        delivery_type='O',
        gender='M',
        birthdate=datetime.date(1943, 12, 13))
    cli_3.save()
    cli_3.set_meal_defaults('main_dish', 4, 2, 'R')
    cli_3.set_meal_defaults('dessert', 4, 0, '')
    cli_3.set_meal_defaults('diabetic dessert', 4, 0, '')
    cli_3.set_meal_defaults('fruit_salad', 4, 0, '')
    cli_3.set_meal_defaults('green_salad', 4, 2, '')
    cli_3.set_meal_defaults('pudding', 4, 0, '')
    cli_3.set_meal_defaults('compote', 4, 0, '')
    cli_3.save()
    cli_4 = Client(
        member=mem_3,
        billing_member=mem_3,
        billing_payment_type='check',
        rate_type='Low income',
        emergency_contact_relationship='',
        status='A',
        language='en',
        alert='',
        delivery_type='O',
        gender='M',
        birthdate=datetime.date(1943, 12, 13))
    cli_4.save()
    cli_4.set_meal_defaults('main_dish', 4, 1, 'L')
    cli_4.set_meal_defaults('dessert', 4, 0, '')
    cli_4.set_meal_defaults('diabetic dessert', 4, 0, '')
    cli_4.set_meal_defaults('fruit_salad', 4, 0, '')
    cli_4.set_meal_defaults('green_salad', 4, 0, '')
    cli_4.set_meal_defaults('pudding', 4, 0, '')
    cli_4.set_meal_defaults('compote', 4, 1, '')
    cli_4.save()
    #
    print_all_cols(db.query(Client.sa))
    print_rows(Client.objects)

    # -----------------------------------------------------------------------------
    ref_1 = Referencing(
        referent=mem_5,
        client=cli_1,
        referral_reason='Can hardly walk.',
        work_information='CHUM Hôtel-Dieu',
        date=datetime.date(2015, 11, 2))
    ref_1.save()
    ref_2 = Referencing(
        referent=mem_6,
        client=cli_2,
        referral_reason='Had an operation.',
        work_information='CUSM',
        date=datetime.date(2014, 1, 12))
    ref_2.save()
    #
    print_all_cols(db.query(Referencing.sa))
    print_rows(Referencing.objects)

    # -----------------------------------------------------------------------------
    opt_1 = Option(
        name='Fruit Salad',
        option_group='side dish',
        description='')
    opt_1.save()
    opt_2 = Option(
        name='Green Salad',
        option_group='side dish',
        description='')
    opt_2.save()
    opt_3 = Option(
        name='Dessert',
        option_group='side dish',
        description='')
    opt_3.save()
    opt_4 = Option(
        name='Pudding',
        option_group='side dish',
        description='')
    opt_4.save()
    opt_5 = Option(
        name='Diabetic dessert',
        option_group='side dish',
        description='')
    opt_5.save()
    opt_6 = Option(
        name='Puree all',
        option_group='preparation',
        description='')
    opt_6.save()
    opt_7 = Option(
        name='Cut up meat',
        option_group='preparation',
        description='')
    opt_7.save()
    #
    print_all_cols(db.query(Referencing.sa))
    print_rows(Referencing.objects)

    # -----------------------------------------------------------------------------
    cli_opt_1 = Client_option(
        client=cli_1,
        option=opt_6)
    cli_opt_1.save()
    cli_opt_2 = Client_option(
        client=cli_1,
        option=opt_4)
    cli_opt_2.save()
    cli_opt_3 = Client_option(
        client=cli_2,
        option=opt_3)
    cli_opt_3.save()
    cli_opt_4 = Client_option(
        client=cli_3,
        option=opt_7)
    cli_opt_4.save()
    #
    print_all_cols(db.query(Client_option.sa))
    print_rows(Client_option.objects)

    # -----------------------------------------------------------------------------
    res_1 = Restriction(
        client=cli_1,
        restricted_item=ri_4)
    res_1.save()
    res_2 = Restriction(
        client=cli_1,
        restricted_item=ri_2)
    res_2.save()
    res_3 = Restriction(
        client=cli_1,
        restricted_item=ri_8)
    res_3.save()
    #
    print_all_cols(db.query(Restriction.sa))
    print_rows(Restriction.objects)

    # -----------------------------------------------------------------------------
    cai_1 = Client_avoid_ingredient(
        client=cli_4,
        ingredient=ing_1)
    cai_1.save()
    cai_2 = Client_avoid_ingredient(
        client=cli_4,
        ingredient=ing_10)
    cai_2.save()
    cai_3 = Client_avoid_ingredient(
        client=cli_4,
        ingredient=ing_3)
    cai_3.save()
    #
    print_all_cols(db.query(Client_avoid_ingredient.sa))
    print_rows(Client_avoid_ingredient.objects)

    # -----------------------------------------------------------------------------
    cac_1 = Client_avoid_component(
        client=cli_4,
        component=com_1)
    cac_1.save()
    cac_2 = Client_avoid_component(
        client=cli_4,
        component=com_7)
    cac_2.save()
    cac_3 = Client_avoid_component(
        client=cli_4,
        component=com_3)
    cac_3.save()
    #
    print_all_cols(db.query(Client_avoid_component.sa))
    print_rows(Client_avoid_component.objects)

    # -----------------------------------------------------------------------------
    ord_1 = Order(
        client=cli_1,
        creation_date=datetime.date(2016, 5, 20),
        delivery_date=datetime.date(2016, 5, 21),
        status='O')
    ord_1.save()
    ord_2 = Order(
        client=cli_2,
        creation_date=datetime.date(2016, 5, 20),
        delivery_date=datetime.date(2016, 5, 21),
        status='O')
    ord_2.save()
    ord_3 = Order(
        client=cli_3,
        creation_date=datetime.date(2016, 5, 20),
        delivery_date=datetime.date(2016, 5, 21),
        status='O')
    ord_3.save()
    ord_4 = Order(
        client=cli_4,
        creation_date=datetime.date(2016, 5, 20),
        delivery_date=datetime.date(2016, 5, 21),
        status='O')
    ord_4.save()
    #
    print_all_cols(db.query(Order.sa))
    print_rows(Order.objects)

    # -----------------------------------------------------------------------------
    oi_1 = Order_item(
        order=ord_1,
        component=com_6,
        price=7,
        billable_flag=True,
        size='R',
        order_item_type='B component',
        remark='Chat with him !')
    oi_1.save()
    oi_2 = Order_item(
        order=ord_1,
        component=com_12,
        price=7,
        billable_flag=True,
        size='L',
        order_item_type='B component',
        remark='')
    oi_2.save()
    oi_3 = Order_item(
        order=ord_2,
        component=com_6,
        price=7,
        billable_flag=True,
        size='L',
        order_item_type='B component',
        remark='')
    oi_3.save()
    oi_4 = Order_item(
        order=ord_2,
        component=com_6,
        price=7,
        billable_flag=True,
        size='L',
        order_item_type='B component',
        remark='')
    oi_4.save()
    oi_5 = Order_item(
        order=ord_2,
        component=com_8,
        price=7,
        billable_flag=True,
        size='L',
        order_item_type='B component',
        remark='')
    oi_5.save()
    oi_6 = Order_item(
        order=ord_2,
        component=com_8,
        price=7,
        billable_flag=True,
        size='L',
        order_item_type='B component',
        remark='')
    oi_6.save()
    oi_7 = Order_item(
        order=ord_1,
        component=com_11,
        price=7,
        billable_flag=True,
        size='L',
        order_item_type='B component',
        remark='')
    oi_7.save()
    oi_8 = Order_item(
        order=ord_3,
        component=com_6,
        price=7,
        billable_flag=True,
        size='L',
        order_item_type='B component',
        remark='')
    oi_8.save()
    oi_9 = Order_item(
        order=ord_3,
        component=com_10,
        price=7,
        billable_flag=True,
        size='L',
        order_item_type='B component',
        remark='')
    oi_9.save()
    oi_10 = Order_item(
        order=ord_4,
        component=com_6,
        price=7,
        billable_flag=True,
        size='L',
        order_item_type='B component',
        remark='')
    oi_10.save()
    oi_11 = Order_item(
        order=ord_4,
        component=com_9,
        price=7,
        billable_flag=True,
        size='L',
        order_item_type='B component',
        remark='')
    oi_11.save()
    #
    print_all_cols(db.query(Order_item.sa))
    print_rows(Order_item.objects)

    # =====================================================
    print("END dataload")
