from aiogram.fsm.state import State, StatesGroup

class CategoryState(StatesGroup):
    addCategory = State()

    editCategorySelect = State()
    editCategoryName = State()

    startDelete = State()
    finishDelete = State()

class WordsState(StatesGroup):
    viewWords = State()
    kbWords = State()

class NewWordState(StatesGroup):
    selectCategory = State()
    insertWords = State()

class NewWordExcel(StatesGroup):
    selectCategory = State()
    inputExcel = State()

class UzWords(StatesGroup):
    selectCategory = State()
    betweenSelect = State()
    nextLevel = State()

class RuWords(StatesGroup):
    selectCategory = State()
    betweenSelect = State()
    nextLevel = State()

class EnWords(StatesGroup):
    selectCategory = State()
    betweenSelect = State()
    nextLevel = State()

class UzEnWords(StatesGroup):
    selectCategory = State()
    betweenSelect = State()
    nextLevel = State()

class Translate(StatesGroup):
    inputBodyRu = State()
    inputBodyUz = State()

class Quiz(StatesGroup):
    quizCategory = State()
    quizNext = State()
    quizStart = State()

class QuizUzRu(StatesGroup):
    quizCategory = State()
    quizNext = State()
    quizStart = State()

class QuizEnUz(StatesGroup):
    quizCategory = State()
    quizNext = State()
    quizStart = State()

class QuizUzEn(StatesGroup):
    quizCategory = State()
    quizNext = State()
    quizStart = State()

class Surah(StatesGroup):
    nextSurah = State()
    editSurah = State()