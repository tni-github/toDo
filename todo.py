import csv
import logging
from config import TOKEN
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
)


# Включим ведение журнала
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Определяем константы этапов разговора
MENU, HELP, SHOW, DELETE, ADD = range(5)


def start(update, _):
    '''
    Функция начала диалога.
    '''
    # Список кнопок для ответа
    reply_keyboard = [['/help', '/add', '/delete'],
                      ['/show', '/stop']]
    # Создаем простую клавиатуру для ответа
    markup_key = ReplyKeyboardMarkup(
        reply_keyboard, one_time_keyboard=False)
    # Начинаем разговор с предложения нажать кнопку
    update.message.reply_text(
        'Привет! Я Умный_Бот. Я помогу вам создать список дел.\n\n'
        'Выберите кнопку.',
        reply_markup=markup_key)
    return MENU


def menu(update, _):
    '''
    Функция обработки выбора кнопки на первом этапе.
    '''
    user = update.message.from_user
    logger.info("Пользователь %s нажал кнопку %s.",
                user.first_name, update.message.text)
    step = update.message.text
    if step == '/help':
        update.message.reply_text(
            'Открыть список команд? Выберите /Yes или /No.')
        return HELP
    if step == '/add':
        update.message.reply_text(
            'Введите задачу, которую хотите добавить. Иначе нажмите /No.')
        return ADD
    if step == '/delete':
        update.message.reply_text(
            'Если хотите удалить какую-то задачу, введите ее название, иначе нажмите /No.')
        return DELETE
    if step == '/show':
        update.message.reply_text(
            'Открыть список дел? Выберите /Yes или /No.')
        return SHOW
    if step == '/stop':
        return stop(update, _)


def help(update, _):
    '''
    Функция вызова помощи со списком команд.
    '''
    user = update.message.from_user
    logger.info("Пользователь %s подтвердил операцию вызова списка команд, нажал %s.",
                user.first_name, update.message.text)
    if update.message.text == '/Yes':
        update.message.reply_text(
            'Доступны следующие команды:'
            '/help - информация,'
            '/add - добавить задачу,'
            '/delete - удалить (пометить выполненным) задачу,'
            '/show - показать весь список задач,'
            '/stop - прекратить общение с ботом.')
    else:
        logger.info("Пользователь %s отклонил операцию вызова списка команд, нажал %s.",
                    user.first_name, update.message.text)
        return MENU
    return MENU


def add(update, _):
    '''
    Функция добавления задачи в список.
    '''
    user = update.message.from_user
    text = update.message.text
    if text == '/No':
        logger.info("Пользователь %s отклонил операцию добавления новой задачи, нажал %s.",
                    user.first_name, update.message.text)
        return MENU
    else:
        logger.info("Пользователь %s добавил задачу: %s.",
                    user.first_name, update.message.text)
        with open('list.csv', 'a', encoding='utf-8', newline='\n') as file:
            new_text = text + ',\n'
            file.write(new_text)
            update.message.reply_text(
                f'Задача "{text}" добавлена в список задач.')
    return MENU


def delete(update, _):
    ''''
    Функция удаления задачи из списка.
    '''
    user = update.message.from_user
    str = ''
    text = update.message.text
    if text == '/No':
        logger.info("Пользователь %s отклонил операцию удаления задачи, нажал %s.",
                    user.first_name, update.message.text)
        return MENU
    elif text and text != '/No':
        logger.info("Пользователь %s удаляет задачу, содержащую текст: %s.",
                    user.first_name, update.message.text)
        try:
            open('list.csv')
            with open('list.csv', 'r', encoding='utf-8', newline='\n') as file:
                file_reader = csv.reader(file)
                for row in file_reader:
                    if text.lower() in ''.join(row).lower():
                        continue
                    else:
                        row = ''.join(row)
                        str += row
                        str += ',\n'
            with open('new.csv', 'w', encoding='utf-8') as file_new:
                file_new.write(str)
            with open('list.csv', 'w', encoding='utf-8', newline='\n') as file:
                file.write(str)
            update.message.reply_text(f'Задачи, содержащие "{text}", удалены.')
        except FileNotFoundError:
            update.message.reply_text('Нет готового списка дел.')
    return MENU


def show(update, _):
    '''
    Функция отображения списка дел.
    '''
    user = update.message.from_user
    if update.message.text == '/Yes':
        logger.info("Пользователь %s подтвердил операцию отображения списка дел, нажал %s.",
                    user.first_name, update.message.text)
        str = ''
        filename = 'list.csv'
        try:
            open(filename)
            with open(filename, encoding='utf-8') as notes:
                file_reader = csv.reader(notes)
                for row in file_reader:
                    if len(row) > 0:
                        row = ''.join(row)
                        str += row
                        str += '\n'
                update.message.reply_text(str)
        except FileNotFoundError:
            update.message.reply_text('Нет готового списка дел.')
    else:
        logger.info("Пользователь %s отклонил операцию, нажал %s.",
                    user.first_name, update.message.text)
        return MENU
    return MENU


def stop(update, _):
    '''
    Функция остановки диалога.
    '''
    # определяем пользователя
    user = update.message.from_user
    # Пишем в журнал о том, что пользователь отменил разговор
    logger.info("Пользователь %s отменил разговор.", user.first_name)
    # Отвечаем на отказ поговорить
    update.message.reply_text(
        'Мое дело предложить - Ваше отказаться...\n'
        'Будет скучно - возвращайтесь (команда: /start)!',
        reply_markup=ReplyKeyboardRemove()
    )
    # Заканчиваем разговор.
    return ConversationHandler.END


if __name__ == '__main__':
    # Создаем Updater и передаем ему токен вашего бота.
    updater = Updater(TOKEN)
    # получаем диспетчера для регистрации обработчиков
    dispatcher = updater.dispatcher

    # Определяем обработчик разговоров `ConversationHandler`
    # с состояниями MENU, HELP, SHOW, DELETE, ADD
    conv_handler = ConversationHandler(  # здесь строится логика разговора
        # точка входа в разговор
        entry_points=[CommandHandler('start', start)],
        # этапы разговора, каждый со своим списком обработчиков сообщений
        states={
            MENU: [MessageHandler(Filters.regex('^(/help|/add|/edit|/find|/delete|/show|/save|/load)$'), menu)],
            HELP: [MessageHandler(Filters.text, help)],
            SHOW: [MessageHandler(Filters.text, show)],
            DELETE: [MessageHandler(Filters.text, delete)],
            ADD: [MessageHandler(Filters.text, add)],
        },
        # точка выхода из разговора
        fallbacks=[CommandHandler('stop', stop)],
    )

    # Добавляем обработчик разговоров `conv_handler`
    dispatcher.add_handler(conv_handler)

    # Запуск бота
    updater.start_polling()
    print('server started')
    updater.idle()
    print('server stoped')
