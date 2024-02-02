# core

from utils import constants

COST = constants.AQSHA_COST

START_COMMAND = """✨ Salom! Men MuloqotAi, sizning shaxsiy 
yordamchingizman. Foydalanish uchun shunchaki savolingizni botga yozish kifoya.

Buyruqlar:
/start - Botni qayta ishga tushirish
/art - rasm generatsiya qilish
/premium - Premium obuna
/help - Foydalanish qo’llanmasi

@muloqotai - Ushbu kanalda siz bilmagan va yangi qo’shiladigan funksiyalar haqidagi ma’lumotlar berib boriladi. Kanal a'zolari birinchilardan bo'lib yangi funksiyalarni sinab ko'rishlari mumkin

🖼 <b>Rasm generatsiya qilish uchun</b> <b>/art</b> kommandasini yuboring! Batafsil ma'lumot uchun - /help
"""

ABILITY_COMMAND = """💡 Aqlli: Ko'plab mavzularni tushunish va javob berishga tayyorman. Umumiy bilimdan ma'lumotlarni qidirishga qadar, 
sizga aniqligi va maqbul javoblarni taklif etishim mumkin.

🧠 Dono: Men doimiy o'rganish va rivojlanishda, yangi ma'lumotlarga va foydalanuvchi bilan bo'lishuvlarga moslashishim mumkin. Aqlli muloqotlarni taklif etishim mumkin.

🌄 Rassom: Mening yana bir qobilyatlarimdan biri bu rasm generatsiya qila olishim. Men sizga xar qanday turdagi ajoyib rasmlarni generatsiya qilib olib bera olaman

⚙️ Avtotarjimon: Meni siz bilan o'zbek tilida yanada yahshiroq muloqot qila olishim uchun, avtotarjima funksiyasini ishlataman. Endi siz ingliz tilida qiynalib menga yozishingiz shart emas. Bu funksiya ixtiyoriy xoxlagan paytiz o'chirib qo'yishingiz mumkin."""

def getGreetingsText(firstName):
    return f"""Salom {firstName}, Men sizning virtual dunyodagi shaxsiy yordamchingizman, Sizga qanday yordam berishim mumkin?"""

HELP_COMMAND = """<b>Botni qanday ishlataman?</b>
Botda  chatgptni  ishlatish uchun botga shunchaki so'rov yuborish kifoya. 
Rasm generatsiyasi uchun esa ushbu komandani yuboring: /art prompt. Prompt o'rniga o'zingizni so'rovingizni yuboring. 

<b>Botning qo'shimcha xususiyatlari</b>:
🔹<b>Avtotarjima:</b> - bilasiz chatgpt o'zbek tilini  unchalik yahshi tushunmaydi shuning uchun botda avtotarjima xususiyati mavjud, agarda avtotarjimani yoqib qo'ysangiz sizning xar bir so'rovingiz  ingliz tilga  o'tqizilib chatgptga yuboriladi va  kelgan javob esa o'zbekchaga tarjima qilinadi. Bu bilan siz ingliz tilini bilmasdan turib chatgptni to'liqona ishlatishingiz mumkin bo'ladi.

Qachonki o'zbek tilida so'rov kiritsangiz avtotarjima o'zi avtomatik tarzda yonadi.

Botning rasmiy kanali - @muloqotai
"""


def buy_text(price):
    
    BUY_TEXT = f"""1/2
To'lov tafsilotlari:

<b>Mahsulot:</b> Premium obuna
<b>1 oylik obuna narxi:</b> {price} so'm
<b>Umumiy summa:</b> <b>{price} so'm</b>

Xaridni yakunlash uchun <b>{price}</b> so'm miqdorini quyidagi kartaga oʻtkazing:

<b>Karta raqami:</b> <code>5614 6814 0539 6510</code>
<b>Karta egasi</b>: TULKIN XUDAYBERGANOV

Ushbu kartaga to'lov qilganingizdan so'ng bizga to'lov skrinshotini yuboring 👇
Biz sizning to'lovingizni qo'lda tekshirib chiqamiz va sizga obuna taqdim etamiz.

Toʻlov jarayonida biror muammoga duch kelsangiz yoki savollaringiz boʻlsa, bizga murojat qiling - @texnosupportuzbot | @abdulvoris_101
"""
    return BUY_TEXT

PAYMENT_STEP1 = """1/2
Biz xozir sizning to'lovingizni o'zimiz qo'lda tekshirib chiqamiz,
uning uchun esa bizga yuborgan kartangizdagi ismingizni yozing 👇
"""

PAYMENT_STEP2 = """
Ajoyib! Sizning to'lovingiz yaqin soatlar ichida tekshirilib chiqib, 
sizga premium obuna taqdim etiladi. 
Yaqin soatlar ichida sizga premium obuna bo'yicha xabar keladi.
Bizni tanlaganiz uchun rahmat 🫡

Agarda biror savolingiz bo'lsa, bizga murojat qiling - @texnosupportuzbot | @abdulvoris_101
"""

# Plans

PLAN_TEXT = """
Xozirgi obuna quyidagilarni o'z ichiga oladi:
✅ Chatgptga har kuni 16 ta so'rov;
⭐️ AI bilan 5 ta rasm generatsiya qilish;
✅ Avtotarjimon funksiyasi;
✅ Birinchi 10ta so'rov uchun vaqt chegarasi yo'q;
⚠️ Keyingi so’rovlarda vaqt chegarasi mavjud;

Ko'proq kerakmi? 24.000 so'm evaziga bir oylik premium tarifga obuna bo'ling.

Premium obuna bilan siz:
✅ Chatgptga turboga har kuni 75 ta so'rov;
⭐️ AI bilan 20 ta rasm generatsiya qilish;
✅ Avtotarjimon funksiyasi;
✅ Xechqanday reklama yo'q;
✅ So’rovlar orasida pauza yo’q;
✅ Javoblar kreativroq.
"""

LIMIT_REACHED = """Afsuski sizning kunlik limitingiz tugadi. 
Yanada ko'proq so'rov uchun premium tarifga obuna bo'ling
16/16
/premium"""

LIMIT_GROUP_REACHED = """Afsuski guruhning kunlik limiti tugadi. 
So'rovlarni ko'paytirish uchun bizga donat qilib yordam berishingiz mumkin
150/150
/donate"""

PREMIUM_GAVE = """Tabriklaymiz sizga premium obuna taqdim etildi. Bizni tanlaganiz uchun rahmat 😊🎉"""

SUBSCRIPTION_END = """🚀 Obunani yangilash vaqti keldi!

Salom Qadrli Foydalanuvchi 👋,

Obunangiz muddati tugadi! Premium imtiyozlardan foydalanishda davom etish uchun “/premium” kommandasini kiriting.

Bizni tanlaganiz uchun tashakkur 🌟
"""
     
