# core
import os
COST = os.environ.get("AQSHA_COST")

START_COMMAND = """🤖 Salom! Men MuloqotAi, sizning shaxsiy 
yordamchingizman.
Avtotarjimon yoniq xolatda.
Batafsil ma'lumot uchun - /help
"""

HOW_TO_HELP_TEXT = """Sizga qanday yordam bera olaman?"""

HELP_COMMAND = """<b>Botni qanday ishlataman?</b>
Botda  chatgptni  ishlatish uchun botga shunchaki so'rov yuborish kifoya. 
Rasm generatsiyasi uchun esa shu komandani yuboring: /art prompt. Prompt o'rniga o'zingizni so'rovingizni yuboring. 

<b>Botning qo'shimcha xususiyatlari</b>:
🔹<b>Avtotarjima:</b> - bilasiz chatgpt o'zbek tilini tushunmaydi shuning uchun botda avtotarjima xususiyati mavjud, agarda avtotarjimani yoqib qo'ysangiz sizning xar bir so'rovingiz tarjimon orqali ingliz tilga  o'tqizilib chatgptga yuboriladi va  kelgan javob esa o'zbekchaga tarjima qilinadi. Bu bilan siz ingliz tilini bilmasdan turib chatgptni to'liqona ishlatishingiz mumkin bo'ladi.

🔹<b>Xazilkash AI:</b> muloqotai guruhlarda xam gaplasha oladi, qiziq tomoni u guruhlarda gaplashgan payti juda xam xazilkash tutadi. Siz bot bilan xuddi do'st kabi muloqot qila olasiz. Agarda siz  aniqroq javob olmoqchi bo'lsangiz uning o'ziga yozing

Botni guruhga qanday qo'shish bo'yicha batafsil ma'lumot - /groupinfo"""


GROUP_INFO_COMMAND = """Shaxsiy va guruh suhbatlaringizda yordam beradigan foydali yordamchi! Ushbu botning <b>guruhda</b> ishlash tartibi quyidagicha:

1️⃣ <b>Guruhga qo'shish</b>: MuloqotAIdan foydalanish uchun, uningni Telegram gruhingizga qo'shing. Bu uchun "@muloqataibot" ni qidiring va uningni gruhga taklif qiling.

2️⃣ <b>Admin huquqlarini berish</b>: MuloqotAItning samarali ishlashi uchun uningni admin sifatida qo'shish kerak. Uningga to'g'ri admin huquqlarini berishni unutmang, masalan, xabarlarni o'chirish (ixtiyoriy) va boshqa sozlamalarni boshqarish.

3️⃣ <b>Gruhda suhbatlashish</b>: Bot bilan suhbat qurish uchun unga reply tarzida so'rov yuboring. Guruh a'zolari savollarni so'rash, ma'lumot so'ralish, yordam so'ralish yoki qiziqarli suhbatlar olib borishlari mumkin.

➕ <b>Ochiq guruh:</b> @muloqataigr"""


ABILITY_COMMAND = """💡 Aqlli: Ko'plab mavzularni tushunish va javob berishga tayyorman. Umumiy bilimdan ma'lumotlarni qidirishga qadar, 
sizga aniqligi va maqbul javoblarni taklif etishim mumkin.

🧠 Dono: Men doimiy o'rganish va rivojlanishda, yangi ma'lumotlarga va foydalanuvchi bilan bo'lishuvlarga moslashishim mumkin. Aqlli muloqotlarni taklif etishim mumkin.

😄 Xushchaqchaq: Hayot kulguli tabassum bilan yaxshilanadi, va men sizning yuzingizga tabassum olib kelish uchun bu yerga keldim!

🌄 Rassom: Mening yana bir qobilyatlarimdan biri bu rasm generatsiya qila olishim. Men sizga xar qanday turdagi ajoyib rasmlarni generatsiya qilib olib bera olaman

⚙️ Avtotarjimon: Meni siz bilan o'zbek tilida yanada yahshiroq muloqot qila olishim uchun, avtotarjima funksiyasini ishlataman. Endi siz ingliz tilida qiynalib menga yozishingiz shart emas. Bu funksiya ixtiyoriy xoxlagan paytiz o'chirib qo'yishingiz mumkin."""


NEW_MEMBER_TEXT = """👋 Assalomu alaykum! Mening ismim MuloqotAI 
Men sizga yordam berish uchun yaratilgan aqlli chatbotman. 
Bot ishlashi uchun menga administrator huquqlarini bering
😊 Ko'proq foydam tegishi uchun /help kommandasini yuborib men bilan yaqinroq tanishib chiqing
"""

GREETINGS_TEXT = "Assalomu aleykum Men Muloqot AI man sizga qanday yordam bera olaman?"

AQSHA_TEXT = f"""'Aqsha' uchun joriy narxlarimiz quyidagicha:

1 aqsha - {COST} so'm
200 aqsha - {int(COST) * 200} so'm

Minimum 200 aqsha sotib olishingiz mumkin!

Chatga kerakli miqdordagi aqshani yozing, biz sizga to'lashingiz kerak bo'lgan summa miqdorni ko'rsatamiz."""


def buy_text(amount, price, transaction_id):
        
    BUY_TEXT = f"""
Buyurtmangiz tafsilotlari:

<b>Mahsulot:</b> "Aqsha"
<b>Miqdori:</b> {amount} aqsha
<b>Umumiy summa:</b> <b>{price} so'm</b>

Xaridni yakunlash uchun <b>{price}</b> so'm miqdorini quyidagi kartaga oʻtkazing:

<b>Karta raqami:</b> <code>5614 6814 0539 6512</code>
<b>Karta egasi</b>: TULKIN XUDAYBERGANOV

Agarda siz payme dan to'lasangiz to'lovni avtomotlashtirish uchun

To'lovni amalga oshirayotganda, <b>to'lov izohiga quyidagi matnini kiriting</b>:

<b>Izoh:</b> <code>{transaction_id}</code>

Izoh matni sizning to'lovingizni aniqlash va buyurtmangizni to'g'ri tekshirish uchun kerak.To'lov qilib bo'lganizdan keyin 
"✅ To'lovni tekshirish"  knopkasini bosing

Agarda siz paymedan boshqa bir ilovada pul o'tkazsangiz sizning to'lovingiz qo'lda tekshirilib chiqiladi.

Toʻlov jarayonida biror muammoga duch kelsangiz yoki savollaringiz boʻlsa, bizning @texnosupportuzbot botiga yozing.
"""

    return BUY_TEXT

FAILED_PAYMENT_STEP1 = """
Afsuski sizning to'lovingiz topilmadi. Lekin xavotirlanishga o'rin yo'q.

Biz xozirda sizning to'lovingizni o'zimiz qo'lda tekshirib chiqamiz,
uning uchun esa bizga yuborgan kartangizdagi ismingizni yozing 👇
"""

FAILED_PAYMENT_STEP2 = """
Ajoyib! Sizning to'lovingiz 24 soat ichida tekshirilib chiqib, 
sizning xisobingizga aqsha tushirib beramiz.

Balans - /balance

Agarda biror savolingiz bo'lsa, bizga murojat qiling - @texnosupportuzbot
"""

# Agarda biror savolingiz bo'lsa, bizga murojat qiling - @texnosupportuzbot
# 24 soat ichida
# sizning xisobingizga aqsha tushirib beramiz.