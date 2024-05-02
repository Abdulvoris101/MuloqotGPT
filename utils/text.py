# All texts
from typing import List

from aiogram import types

from apps.admin.schemes import StatisticsReadScheme
from apps.core.schemes import ChatScheme, ChatActivityViewScheme
from apps.subscription.models import Plan
from apps.subscription.schemes import ChatQuotaGetScheme

# CORE TEXTS

START_BOT_TEXT = """Botni boshlash uchun /start kommandasini yuboring!"""

WAIT_MESSAGE_TEXT = "⏳ Javob kelguncha botning rasmiy kanaliga obuna bo'lib qo'ying: @muloqotai"

GREETINGS_TEXT = """Salom! Men dunyodagi eng ilg'or Sun'iy intellektman

Men sizga ko'p vazifalarni hal qilishda yordam bera olaman. Masalan:
- ijtimoiy tarmoqlar uchun post, insho xabarini yozish
- rasm chizish
- uy vazifasini bajarish

🖼 Rasm chizish uchun so'rov boshiga ushbu so'zlarni qo'shishingiz kerak - generate yokida imagine

Men suhbat tarixni saqlab qolishim mumkin va suxbatni yangilash uchun /new kiriting

Menga o'zingiz qiziqayotgan savol yoki so'rovingizni yuboring!
"""

HELP_COMMAND = """<b>Botni qanday ishlataman?</b>
Botda  chatgptni  ishlatish uchun botga shunchaki so'rov yuborish kifoya. 
🖼 Rasm chizish uchun so'rov boshiga ushbu so'zlarni qo'shishingiz kerak - generate yokida imagine. 

<b>Bot bilan guruhda qanday yozishaman?</b>
Chatbot guruhga xabar yuborganda, bot xabari ostidagi “reply" tugmasini bosing va javobingizni kiriting yokida 
Xabaringizni boshida muloqotgpt ni nomi bilan boshlang

Misol uchun:
Muloqot  salom, menga ....
@muloqotgpt_bot salom, menga ....

<b>Botning qo'shimcha xususiyatlari</b>:
🔹<b>Avtotarjima:</b> - bilasiz chatgpt o'zbek tilini  unchalik yahshi tushunmaydi shuning uchun botda avtotarjima xususiyati mavjud, agarda avtotarjimani yoqib qo'ysangiz sizning xar bir so'rovingiz  ingliz tilga  o'tqizilib chatgptga yuboriladi va  kelgan javob esa o'zbekchaga tarjima qilinadi

Qachonki o'zbek tilida so'rov kiritsangiz avtotarjima o'zi avtomatik tarzda yonadi.

Bot bilan bo'lgan suxbatni tozalash uchun /new ushbu buyruqni yuboring!

Botning rasmiy guruhi - @muloqotaigr
Botning rasmiy kanali - @muloqotai
Biz bilan aloqa - @texnosupportuzbot
"""

PROFILE_TEXT = """⚡️ Obuna turi: {planTitle}
🤖 GPT modeli: {currentGptModel}

Limitlar:
• GPT-3.5 bu oygi so’rovlar:  {currentMonthGpt3Requests}/{availableGpt3Requests}
• GPT-4 bu oygi so’rovlar:  {currentMonthGpt4Requests}/{availableGpt4Requests}
• Rasm generatsiya: {currentMonthImageRequests}/{availableImageRequests}
• Qo'shimcha GPT-3.5 so'rovlar: {additionalGpt3Requests}
• Qo'shimcha GPT-4 so'rovlar: {additionalGpt4Requests}
• Qo'shimcha rasm so'rovlari: {additionalImageRequests}

{PREMIUM_TEXT}
"""

PREMIUM_TEXT = """Ko'proq kerakmi? 25.000 so'm evaziga bir oylik premium tarifga obuna bo'ling.
Premium obuna bilan siz:
✅ Chatgpt turboga oyiga 2250 ta so'rov;
⭐️ AI bilan oyiga 900 ta rasm generatsiya qilish;
✅ Avtotarjimon funksiyasi;
✅ Xechqanday reklama yo'q;
✅ Uzunroq javoblar;
✅ So’rovlar orasida pauza yo’q;
✅ Xabarlarni cheksiz tarjima qilish.
✅ Javoblar kreativroq.

Premium obunani ulash uchun /premium bo’limiga o’ting."""

SELECT_GPT_MODEL = "Ishlatmoqchi bo'lgan gpt modelni tanlang: "
UPDATED_MODEL = "Sizning gpt modelingiz o'zgartirildi!"
UNAVAILABLE_GPT_MODEL = "Siz gpt-4 dan foydalana olmaysiz, uning uchun premiumga obuna bo'lishingiz kerak /premium"
UNAVAILABLE_GROUP_TEXT = "Bu guruhda rasm generatsiya qilib bo'lmaydi, generatsiya uchun guruh - @muloqotaigen"

def getProfileText(plantTitle: str, chatActivityScheme: ChatActivityViewScheme,
                   chatQuotaScheme: ChatQuotaGetScheme, currentGptModel: str):
    data = {
        **chatActivityScheme.model_dump(),
        **chatActivityScheme.stats.model_dump(),
        **chatQuotaScheme.model_dump(),
        "currentGptModel": currentGptModel,
        "planTitle": plantTitle,
        "PREMIUM_TEXT": PREMIUM_TEXT if plantTitle == "Free plan" else ""
    }
    return PROFILE_TEXT.format_map(data)


# Referrals

CONGRATS_GAVE_REQUESTS = """Do'stingizni taklif etganingiz uchun sizga 10ta gpt so'rovlar taqdim etildi 🎉. 
Shaxsiy kabinet - /profile"""

REFERRAL_GUIDE = """Do'stingizni botga taklif qilib 10 dona gpt-3.5 turbo so'rovlarini qo'lga kiriting.

Sizning shaxsiy referral linkingiz - <code>https://t.me/{botUsername}?start={userId}</code>

* Ushbu linkni do'stingizga yuboring"""

# Premium plan texts

INVOICE_TEXT = """1/2
To'lov tafsilotlari:

<b>Mahsulot:</b> Premium obuna
<b>1 oylik obuna narxi:</b> {price} so'm
<b>Umumiy summa:</b> <b>{price} so'm</b>

Xaridni yakunlash uchun <b>{price}</b> so'm miqdorini quyidagi kartaga oʻtkazing:

<b>Karta raqami:</b> <code>5614 6814 0539 6510</code>
<b>Karta egasi</b>: TULKIN XUDAYBERGANOV

⚠️ Ushbu kartaga to'lov qilganingizdan so'ng bizga to'lov skrinshotini yuboring
Biz sizning to'lovingizni qo'lda tekshirib chiqamiz va sizga obuna taqdim etamiz.

Toʻlov jarayonida biror muammoga duch kelsangiz yoki savollaringiz boʻlsa, bizga murojat qiling - @texnosupportuzbot | @abdulvoris_101
"""


WAITING_PAYMENT_PHOTO_TEXT = """2/2
To'lovni tasdiqlash uchun bizga to'lov skrinshotini yuboring 👇
"""

COMPLETED_PAYMENT = """
Ajoyib! Sizning to'lovingiz yaqin soatlar ichida tekshirilib chiqib, 
sizga premium obuna taqdim etiladi. 
Yaqin soatlar ichida sizga premium obuna bo'yicha xabar keladi.
Bizni tanlaganiz uchun rahmat 🫡

Agarda biror savolingiz bo'lsa, bizga murojat qiling - @texnosupportuzbot | @abdulvoris_101
"""

PLANS_TEMPLATE = """{title}
----------------------------
{description}\n
- Obuna narxi: <b>{amountForMonth}</b> so'm """


def getSubscriptionPlansText(plans: List[Plan]):
    plansText = ""

    for plan in plans:
        plansText += PLANS_TEMPLATE.format(
            title=plan.title,
            description=plan.description,
            amountForMonth="{:,.0f}".format(plan.amountForMonth).replace(",", ".")
        ) + "\n\n"
    return plansText


PREMIUM_GRANTED_TEXT = """Tabriklaymiz sizga premium obuna taqdim etildi. Bizni tanlaganiz uchun rahmat 😊🎉"""
SUBSCRIPTION_END = """🚀 Obunani yangilash vaqti keldi!

Salom Qadrli Foydalanuvchi 👋,

Obunangiz muddati tugadi! Premium imtiyozlardan foydalanishda davom etish uchun “/premium” kommandasini kiriting.

Bizni tanlaganiz uchun tashakkur 🌟
"""

PAYMENT_ON_REVIEW_TEXT = "Sizning premium obunaga so'rovingiz ko'rib chiqilmoqda"

# Limits


def getLimitReached(userUsedRequests, isPremium):
    freeText = """ruxsat etilgan maksimal bepul foydalanishga erishdingiz. ChatGPT-ni abadiy bepul taqdim etish biz uchun qimmat.
Yanada ko'proq so'rov uchun premium tarifga obuna bo'ling. /premium""" if not isPremium else ""
    return f"""Afsuski sizning kunlik limitingiz tugadi, {freeText}
{userUsedRequests}/{userUsedRequests}
"""


LIMIT_GROUP_REACHED = """Afsuski guruhning kunlik limiti tugadi. 
So'rovlarni ko'paytirish uchun bizga donat qilib yordam berishingiz mumkin

Har qanday to'lov o'tgandan so'ng biz zudlik bilan guruh uchun qo'shimcha chatgpt va rasm generatsiya so'rovlarini sotib olib sizlarga taqdim etamiz

/donate"""

DONATE = f"""
🌟 Bizga donat qilayotganiz uchun katta rahmat! 
Sizning donatingiz juda qadrlanadi va mazmunli o'zgarishlarga olib keladi.

Donat uchun karta informatsiyasi:

<b>Karta raqami:</b> <code>5614 6814 0539 6510</code>
<b>Karta egasi</b>: TULKIN XUDAYBERGANOV

Savol va takliflar uchun - @texnosupportuzbot
"""

# Admin

STATISTICS_TEXT = """Foydalanuvchilar - {usersCount}
Aktiv Foydalanuvchilar - {activeUsers}
Bugungi Aktiv Foydalanuvchilar - {activeUsersOfDay}
1 Kun ishlatgan foydalanuvchilar - {usersUsedOneDay}
1 hafta ishlatgan Foydalanuvchilar - {usersUsedOneWeek}
1 oy ishlatgan Foydalanuvchilar - {usersUsedOneMonth}
Premium Foydalanuvchilar - {premiumUsers}
Xabarlar - {allMessages}
User uchun o'rtacha xabar - {avgUsersMessagesCount}
Bugungi xabarlar - {todayMessages}

Eng oxirgi aktivlik - {lastUpdate}
Eng oxirgi aktivlik ko'rstgan user - {latestUserId}"""

REJECTED_TEXT = """Afsuski sizning premium obunaga bo'lgan so'rovingiz bekor qilindi.
Sababi: {reason}
Biror xatolik ketgan bo'lsa bizga murojat qiling: @texnosupportuzbot
"""

INLINE_BUTTONS_GUIDE = """Inline knopkalarni kiriting. 
Misol uchun\n`./Test-t.me//texnomasters\n./Test2-t.me//texnomasters`"""

SURE_TO_SUBSCRIBE = "Siz rostan ushbu foydalanuvchiga premium obuna taqdim etmoqchimisiz?"
SUCCESSFULLY_SUBSCRIBED = "Ushbu foydalanuvchi premium obunaga ega bo'ldi 🎉"

SELECT_MESSAGE_TYPE = "Xabar/Rasm/Video kiriting"

# FEEDBACK

REQUEST_FEEDBACK_MESSAGE = """Bot bilan bo'lgan tajribangizni yozib qoldiring, bu bilan siz botni rivoji uchun xissa qo'shgan bo'lasiz! 
Sizning fikr-mulohazalaringiz xizmatimizni yaxshilashga yordam beradi. Biz sizning har bir fikringizni qadrlaymiz! ✨"""

FEEDBACK_GUIDE_MESSAGE = """Ushbu savollarga javob berib bizga yordam bering
1. Bot siz uchun qanchalik foydali 0-10 gacha baxolang
2. Botda yana qanday jihatlarni ko'rishni xoxlar edingiz? 
3. Bot bilan suxbatlashayotganda sizda qandaydir xatolik ro'y berdimi? Bo'lgan bo'lsa qanday xatolik?
4. Botni qayerdan eshitib kirdingiz?

Ushbu savollarga qisqagina javob yo'llab bizga yordam bering 😊
"""


# Event template texts

NEW_CHAT_MEMBER_TEMPLATE = """👋 Assalomu alaykum! {firstName}, 
Sizni yana bir bor ko'rib turganimdan xursandman. Bugun sizga qanday yordam bera olaman? 
Men bilan qiziqarli suxbat qurishga tayyormisiz?"
"""

USER_REGISTERED_EVENT_TEMPLATE = """#new\nid: {id}\ntelegramId: {chatId}
\nusername: @{username}\nname: {chatName}"""

SUBSCRIPTION_SEND_EVENT_TEXT = """#payment check-in\nchatId: {userId},\nplan title: {planTitle}\nplan id: <code>{planId}</code>\nprice: {price}"""

FEEDBACK_MESSAGE_EVENT_TEMPLATE = """#chat-id: {id}
#username: @{username}
#xabar: \n\n{text}
"""

IMAGE_RESPONSE_TEMPLATE = "\n🌄 {caption}\n\n@muloqotgpt_bot"

# COMMON
CANCELED_TEXT = "Bekor qilindi!"
THANK_YOU_TEXT = "Izoh uchun rahmat!"

CONTEXT_CHAT_CLEARED_TEXT = """Sizning suxbat tarixingiz yangilandi!"""


# FORBIDDEN

NOT_SUBSCRIBED = "Bu xizmatdan foydalanish uchun premiumga obuna bo'lishingiz kerak. /premium buyrug'i yordamida obuna bo'ling"
LIMIT_TRANSLATION_REACHED = """Afsuski sizning tarjima uchun limitingiz tugadi. Yanada ko'proq tarjima uchun 
premiumga obuna bo'ling - /premium """
NOT_PERMITTED_IMAGE_GENERATION = """Bu guruhda rasm generatsiya qilib bo'lmaydi!"""

# ERRORS

NOT_AVAILABLE_GROUP = """Bu guruhda rasm generatsiya qilib bo'lmaydi!"""
IMAGE_GEN_NOT_AVAILABLE = """Rasm generatsiyasi jarayonida xatolik yuz berdi. Iltimos, keyinroq urinib ko'ring."""
CHATGPT_SERVER_ERROR = "Chatgptda uzilish, Iltimos birozdan so'ng yana qayta urinib ko'ring"
SERVER_ERROR_TRY_AGAIN = "Serverda xatolik. Iltimoz birozdan so'ng qayta urinib ko'ring"
GPT_ERROR_TEMPLATE = "#error\nChat-id: {chatId}\nMessage: {message}\nApi-token: {apiToken}"
TRY_AGAIN = "Iltimos qayta urinib ko'ring"
SENT_USER_REPORT_TEXT = """Message sent to {receivedUsersCount} users
Bot was blocked by {blockedUsersCount} users"""
ENTER_AGAIN = "Iltimos boshqatan so'rov yuboring"
TOKEN_REACHED = "Savolni qisqartiribroq yozing"
ALREADY_SUBSCRIBED = "Siz allaqachon ushbu obunaga egasiz!"
NOT_FOUND_USER = "Foydalanuvchi topilmadi"